from __future__ import annotations

import hashlib
import os
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Optional

from morphology_toolkit.core.model import ProcessingMode, RobotModel
from morphology_toolkit.importers.base import Candidate, ImportAnalysis, Importer
from morphology_toolkit.importers.urdf_importer import UrdfImporter


class Step2UrdfPackageImporter(Importer):
    """Safely import the ZIP package exported by the interactive step2urdf adapter."""

    MAX_MEMBERS = 20_000
    MAX_UNCOMPRESSED_BYTES = 2 * 1024**3

    @staticmethod
    def is_package(path: Path) -> bool:
        if path.suffix.lower() != ".zip" or not zipfile.is_zipfile(path):
            return False
        with zipfile.ZipFile(path) as archive:
            return any(
                PurePosixPath(name).name.lower().endswith(".urdf") for name in archive.namelist()
            )

    def analyze(self, path: Path) -> ImportAnalysis:
        path = Path(path).resolve()
        analysis = ImportAnalysis(input_path=path)
        if not self.is_package(path):
            analysis.diagnostics.append("ZIP is not a step2urdf URDF export package")
            return analysis
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                member = PurePosixPath(name)
                if member.suffix.lower() == ".urdf":
                    analysis.entry_candidates.append(
                        Candidate(
                            Path(member.as_posix()), "urdf", 0.95, "URDF found in adapter export"
                        )
                    )
        return analysis

    def execute(
        self,
        path: Path,
        mode: ProcessingMode = ProcessingMode.ASSISTED,
        selection: Optional[Dict[str, Any]] = None,
    ) -> RobotModel:
        path = Path(path).resolve()
        analysis = self.analyze(path)
        if not analysis.entry_candidates:
            raise ValueError("No URDF entry found in step2urdf export package")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        cache_root = (
            Path(os.environ.get("LOCALAPPDATA", Path.home())) / "MorphologyStudio" / "step_imports"
        )
        target = cache_root / digest
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) > self.MAX_MEMBERS:
                raise ValueError("STEP export package contains too many files")
            if sum(info.file_size for info in infos) > self.MAX_UNCOMPRESSED_BYTES:
                raise ValueError("STEP export package is too large after extraction")
            for info in infos:
                member = PurePosixPath(info.filename)
                if member.is_absolute() or ".." in member.parts:
                    raise ValueError(f"Unsafe path in STEP export package: {info.filename}")
                destination = (target / Path(*member.parts)).resolve()
                if not destination.is_relative_to(target.resolve()):
                    raise ValueError(f"Unsafe path in STEP export package: {info.filename}")
            for info in infos:
                member = PurePosixPath(info.filename)
                destination = (target / Path(*member.parts)).resolve()
                if info.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info) as source, destination.open("wb") as output:
                        output.write(source.read())
        requested = (selection or {}).get("entry")
        entry = (target / Path(requested)).resolve() if requested else next(target.rglob("*.urdf"))
        if not entry.is_relative_to(target.resolve()) or not entry.is_file():
            raise ValueError("Selected URDF entry is outside the extracted STEP package")
        model = UrdfImporter().execute(entry, mode)
        model.source_format = "step2urdf"
        model.metadata["step_source_package"] = path.name
        return model
