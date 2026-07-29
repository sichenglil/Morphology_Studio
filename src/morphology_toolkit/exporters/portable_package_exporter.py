from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from morphology_toolkit.core.model import RobotModel
from morphology_toolkit.resources import ResourceResolver
from morphology_toolkit.validation import validate_model

from .urdf_exporter import UrdfExporter


class PortablePackageExporter:
    def export(self, model: RobotModel, output: Path, resolver: ResourceResolver) -> Path:
        output = Path(output).resolve()
        output.mkdir(parents=True, exist_ok=True)
        (output / "meshes").mkdir(exist_ok=True)
        (output / "textures").mkdir(exist_ok=True)
        (output / "resources").mkdir(exist_ok=True)
        portable = copy.deepcopy(model)
        manifest = []
        uri_map = {}
        for resource in portable.resources:
            source = resolver.resolve(resource.uri)
            if source is None or not source.exists():
                raise FileNotFoundError(f"Cannot package unresolved resource: {resource.uri}")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            suffix = source.suffix.lower()
            folder = (
                "meshes"
                if suffix in {".stl", ".obj", ".dae", ".ply", ".glb", ".gltf"}
                else "textures"
                if suffix in {".png", ".jpg", ".jpeg", ".tga", ".bmp"}
                else "resources"
            )
            target = output / folder / f"{digest[:12]}_{source.name}"
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copy2(source, target)
            old_uri = resource.uri
            resource.uri = target.relative_to(output).as_posix()
            uri_map[old_uri] = resource.uri
            resource.resolved_path = target
            manifest.append(
                {
                    "source_uri": source.as_posix(),
                    "portable_uri": resource.uri,
                    "sha256": digest,
                    "bytes": source.stat().st_size,
                }
            )
        portable.extension_elements = [
            replace_many(raw, uri_map) for raw in portable.extension_elements
        ]
        UrdfExporter().export(portable, output / "robot.urdf")
        (output / "manifest.json").write_text(
            json.dumps({"resources": manifest}, indent=2), encoding="utf-8"
        )
        report = validate_model(portable, ResourceResolver(output))
        report.write(output / "validation.json", output / "validation.md")
        return output

    def export_zip(self, model: RobotModel, output: Path, resolver: ResourceResolver) -> Path:
        output = Path(output).resolve()
        if output.suffix.lower() != ".zip":
            output = output.with_suffix(".zip")
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="morphology-package-") as temporary:
            package_root = Path(temporary) / model.robot_id
            self.export(model, package_root, resolver)
            archive = shutil.make_archive(
                str(output.with_suffix("")), "zip", package_root.parent, package_root.name
            )
        return Path(archive)


def replace_many(text: str, replacements: dict) -> str:
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text
