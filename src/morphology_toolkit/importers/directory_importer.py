from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from morphology_toolkit.core.model import ProcessingMode, RobotModel

from .base import Candidate, ImportAnalysis, Importer
from .registry import detect_format


class DirectoryImporter(Importer):
    ENTRY_FORMATS = {"urdf", "xacro", "mjcf", "step", "srdf"}

    def analyze(self, path: Path) -> ImportAnalysis:
        path = Path(path).resolve()
        if not path.is_dir():
            raise NotADirectoryError(path)
        analysis = ImportAnalysis(input_path=path)
        package_names = {p.parent: self._package_name(p) for p in path.rglob("package.xml")}
        for candidate_path in sorted(p for p in path.rglob("*") if p.is_file()):
            fmt = detect_format(candidate_path)
            if fmt not in self.ENTRY_FORMATS:
                continue
            if fmt == "srdf":
                analysis.format_candidates.append(Candidate(candidate_path, fmt, 1.0, "Semantic Robot Description detected; excluded as a geometry entry"))
                continue
            name = candidate_path.name.lower()
            score = 0.45
            reasons = [f"content detected as {fmt}"]
            if ".urdf." in name or name.endswith(".urdf"):
                score += 0.2
                reasons.append("entry-like filename")
            if any(part in {"urdf", "robots"} for part in candidate_path.parts):
                score += 0.15
                reasons.append("located in model entry directory")
            if any(candidate_path.is_relative_to(pkg) for pkg in package_names):
                score += 0.1
                reasons.append("inside ROS package")
            analysis.entry_candidates.append(Candidate(candidate_path, fmt, min(score, 0.95), "; ".join(reasons), score < 0.8))
        analysis.entry_candidates.sort(key=lambda item: (-item.score, item.path.as_posix()))
        if not analysis.entry_candidates:
            analysis.diagnostics.append("No URDF, Xacro, MJCF or STEP entry candidates found")
        return analysis

    def execute(self, path: Path, mode: ProcessingMode = ProcessingMode.ASSISTED, selection: Optional[Dict[str, Any]] = None) -> RobotModel:
        analysis = self.analyze(path)
        selection = selection or {}
        selected = selection.get("entry")
        if selected:
            entry = Path(selected)
        elif mode == ProcessingMode.AUTO and analysis.entry_candidates and analysis.entry_candidates[0].score >= 0.8 and (len(analysis.entry_candidates) == 1 or analysis.entry_candidates[0].score > analysis.entry_candidates[1].score):
            entry = analysis.entry_candidates[0].path
        else:
            raise ValueError("Entry confirmation required; pass selection={'entry': <path>}")
        from .urdf_importer import UrdfImporter
        from .xacro_importer import XacroImporter
        fmt = detect_format(entry)
        if fmt == "urdf":
            return UrdfImporter().execute(entry, mode, selection)
        if fmt == "xacro":
            return XacroImporter().execute(entry, mode, selection)
        raise ValueError(f"Execution for directory candidate format {fmt!r} is not available")

    @staticmethod
    def _package_name(path: Path) -> str:
        try:
            import xml.etree.ElementTree as ET
            return ET.parse(path).getroot().findtext("name", default=path.parent.name)
        except ET.ParseError:
            return path.parent.name
