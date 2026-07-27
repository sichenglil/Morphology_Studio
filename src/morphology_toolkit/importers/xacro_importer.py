from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Optional

from morphology_toolkit.core.model import ProcessingMode, RobotModel
from morphology_toolkit.resources.package_resolver import PackageResolver

from .base import Candidate, ImportAnalysis, Importer
from .urdf_importer import UrdfImporter

ARG_RE = re.compile(r"<xacro:arg\s+name=[\"']([^\"']+)[\"'](?:\s+default=[\"']([^\"']*)[\"'])?")


@dataclass
class XacroExpansion:
    xml: str = ""
    method: str = ""
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    package_resolutions: dict = field(default_factory=dict)


class XacroImporter(Importer):
    def analyze(self, path: Path) -> ImportAnalysis:
        path = Path(path).resolve()
        text = path.read_text(encoding="utf-8")
        analysis = ImportAnalysis(input_path=path)
        analysis.format_candidates.append(Candidate(path, "xacro", 1.0, "Xacro namespace or macro elements detected"))
        analysis.parameter_candidates = {name: default or None for name, default in ARG_RE.findall(text)}
        if "<xacro:macro" in text and "<robot" in text and not re.search(r"<xacro:[\w.-]+\s", text.replace("<xacro:macro", "")):
            analysis.diagnostics.append("File appears to define macros only; a wrapper entry may be required")
        return analysis

    def execute(self, path: Path, mode: ProcessingMode = ProcessingMode.ASSISTED, selection: Optional[Dict[str, Any]] = None) -> RobotModel:
        path = Path(path).resolve()
        selection = selection or {}
        arguments = dict(selection.get("arguments", {}))
        analysis = self.analyze(path)
        missing = [name for name, default in analysis.parameter_candidates.items() if default is None and name not in arguments]
        if missing:
            raise ValueError(f"Xacro parameters require values: {', '.join(missing)}")
        package_paths = [Path(p).resolve() for p in selection.get("package_paths", [])]
        package_paths.extend(self._discover_package_roots(path))
        resolver = PackageResolver(selection.get("package_map", {}), package_paths, mode)
        expansion = self.expand(path, arguments, resolver)
        if expansion.returncode:
            raise RuntimeError(f"Xacro failed ({expansion.returncode}) via {expansion.method}:\n{expansion.stderr.strip()}")
        xml = expansion.xml
        leftovers = [token for token in ("$(find ", "${", "<xacro:") if token in xml]
        if leftovers:
            raise RuntimeError(f"Expanded Xacro contains unresolved tokens: {leftovers}")
        with tempfile.TemporaryDirectory(prefix="morphology-xacro-") as tmp:
            generated = Path(tmp) / "expanded.urdf"
            generated.write_text(xml, encoding="utf-8")
            model = UrdfImporter().execute(generated, mode, selection)
        model.source_format = "xacro"
        model.source_path = path
        model.metadata["xacro_arguments"] = arguments
        model.metadata["xacro_method"] = expansion.method
        model.metadata["package_resolutions"] = expansion.package_resolutions
        return model

    def expand(self, path: Path, arguments: Dict[str, str], resolver: PackageResolver) -> XacroExpansion:
        try:
            import xacro
            import xacro.substitution_args as substitution_args
        except ImportError:
            xacro = None
        if xacro is not None:
            stdout, stderr = StringIO(), StringIO()
            original_find = substitution_args._eval_find
            def scoped_find(package_name):
                return str(resolver.require(package_name))
            substitution_args._eval_find = scoped_find
            try:
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    document = xacro.process_file(str(Path(path).resolve()), mappings=arguments)
                xml = document.toprettyxml(indent="  ")
                for package_name, trace in resolver._traces.items():
                    if trace.selected:
                        for spelling in {str(trace.selected), trace.selected.as_posix()}:
                            xml = xml.replace(spelling, f"package://{package_name}")
                resolutions = {name: trace.selected.as_posix() if trace.selected else None for name, trace in resolver._traces.items()}
                return XacroExpansion(xml, "python_api", 0, stdout.getvalue(), stderr.getvalue(), resolutions)
            except Exception as exc:
                return XacroExpansion("", "python_api", 1, stdout.getvalue(), stderr.getvalue() + str(exc), {name: trace.selected.as_posix() if trace.selected else None for name, trace in resolver._traces.items()})
            finally:
                substitution_args._eval_find = original_find
        executable = shutil.which("xacro")
        if executable:
            command = [executable, str(Path(path).resolve()), *(f"{key}:={value}" for key, value in sorted(arguments.items()))]
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            return XacroExpansion(completed.stdout if completed.returncode == 0 else "", "executable", completed.returncode, completed.stdout, completed.stderr)
        return XacroExpansion("", "unavailable", 127, "", "Xacro is unavailable. Install it with 'python -m pip install xacro'.")

    @staticmethod
    def expand_to(path: Path, output: Path, arguments: Dict[str, str], package_paths: Optional[list] = None) -> Path:
        importer = XacroImporter()
        result = importer.expand(Path(path), arguments, PackageResolver(roots=package_paths or []))
        if result.returncode:
            raise RuntimeError(result.stderr.strip())
        if any(token in result.xml for token in ("$(find ", "${", "<xacro:")):
            raise RuntimeError("Xacro output contains unresolved expressions")
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result.xml, encoding="utf-8")
        return output

    @staticmethod
    def _command(path: Path, arguments: Dict[str, str]) -> Optional[list]:
        args = [f"{key}:={value}" for key, value in sorted(arguments.items())]
        executable = shutil.which("xacro")
        if executable:
            return [executable, str(path), *args]
        return None

    @staticmethod
    def _discover_package_roots(path: Path) -> list:
        roots = []
        for parent in [path.parent, *path.parents]:
            if (parent / "package.xml").exists():
                roots.append(parent.parent)
                break
        return roots
