from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path

from morphology_toolkit.core.model import RobotModel
from morphology_toolkit.resources import ResourceResolver
from morphology_toolkit.validation import validate_model

from .urdf_exporter import UrdfExporter


class PortablePackageExporter:
    def export(self, model: RobotModel, output: Path, resolver: ResourceResolver) -> Path:
        output = Path(output).resolve()
        output.mkdir(parents=True, exist_ok=True)
        portable = copy.deepcopy(model)
        manifest = []
        for resource in portable.resources:
            source = resolver.resolve(resource.uri)
            if source is None or not source.exists():
                raise FileNotFoundError(f"Cannot package unresolved resource: {resource.uri}")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            target = output / "meshes" / f"{digest[:12]}_{source.name}"
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copy2(source, target)
            resource.uri = target.relative_to(output).as_posix()
            resource.resolved_path = target
            manifest.append({"source_uri": source.as_posix(), "portable_uri": resource.uri, "sha256": digest, "bytes": source.stat().st_size})
        UrdfExporter().export(portable, output / "robot.urdf")
        (output / "manifest.json").write_text(json.dumps({"resources": manifest}, indent=2), encoding="utf-8")
        report = validate_model(portable, ResourceResolver(output))
        report.write(output / "validation.json", output / "validation.md")
        return output

