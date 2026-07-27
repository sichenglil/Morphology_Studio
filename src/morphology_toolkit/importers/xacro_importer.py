from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from morphology_toolkit.core.model import ProcessingMode, RobotModel

from .base import Candidate, ImportAnalysis, Importer
from .urdf_importer import UrdfImporter

ARG_RE = re.compile(r"<xacro:arg\s+name=[\"']([^\"']+)[\"'](?:\s+default=[\"']([^\"']*)[\"'])?")


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
        env = os.environ.copy()
        existing = env.get("AMENT_PREFIX_PATH", "")
        env["AMENT_PREFIX_PATH"] = os.pathsep.join([*(str(p) for p in package_paths), existing])
        command = self._command(path, arguments)
        if command is None:
            raise RuntimeError("Xacro is unavailable. Activate ROS 2 Jazzy or install the Python package with 'python -m pip install xacro'.")
        completed = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
        if completed.returncode:
            raise RuntimeError(f"Xacro failed ({completed.returncode}):\n{completed.stderr.strip()}")
        xml = completed.stdout
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
        return model

    @staticmethod
    def expand_to(path: Path, output: Path, arguments: Dict[str, str], package_paths: Optional[list] = None) -> Path:
        importer = XacroImporter()
        model_selection = {"arguments": arguments, "package_paths": package_paths or []}
        command = importer._command(Path(path).resolve(), arguments)
        if command is None:
            raise RuntimeError("Xacro is unavailable. Activate ROS 2 or install 'xacro'.")
        env = os.environ.copy()
        roots = [str(Path(p).resolve()) for p in package_paths or []]
        env["AMENT_PREFIX_PATH"] = os.pathsep.join([*roots, env.get("AMENT_PREFIX_PATH", "")])
        result = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
        if result.returncode:
            raise RuntimeError(result.stderr.strip())
        if any(token in result.stdout for token in ("$(find ", "${", "<xacro:")):
            raise RuntimeError("Xacro output contains unresolved expressions")
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result.stdout, encoding="utf-8")
        return output

    @staticmethod
    def _command(path: Path, arguments: Dict[str, str]) -> Optional[list]:
        args = [f"{key}:={value}" for key, value in sorted(arguments.items())]
        executable = shutil.which("xacro")
        if executable:
            return [executable, str(path), *args]
        try:
            __import__("xacro")
            return [sys.executable, "-m", "xacro", str(path), *args]
        except ImportError:
            return None

    @staticmethod
    def _discover_package_roots(path: Path) -> list:
        roots = []
        for parent in [path.parent, *path.parents]:
            if (parent / "package.xml").exists():
                roots.append(parent.parent)
                break
        return roots

