from __future__ import annotations

import json
from pathlib import Path


def convert_mesh(source: Path, output: Path, scale: float = 1.0, repair_normals: bool = False, simplify_faces: int = 0) -> Path:
    try:
        import trimesh
    except ImportError as exc:
        raise RuntimeError("Mesh conversion requires 'pip install morphology-toolkit[mesh]'") from exc
    source, output = Path(source).resolve(), Path(output).resolve()
    if source == output:
        raise ValueError("Source meshes are read-only; choose a different output path")
    mesh = trimesh.load(source, force="scene")
    if scale != 1.0: mesh.apply_scale(scale)
    if repair_normals:
        for geometry in mesh.geometry.values(): geometry.fix_normals()
    if simplify_faces:
        for key, geometry in list(mesh.geometry.items()):
            if len(geometry.faces) > simplify_faces: mesh.geometry[key] = geometry.simplify_quadric_decimation(face_count=simplify_faces)
    output.parent.mkdir(parents=True, exist_ok=True); mesh.export(output)
    report = {"source": source.as_posix(), "output": output.as_posix(), "scale": scale, "repair_normals": repair_normals, "simplify_faces": simplify_faces}
    output.with_suffix(output.suffix + ".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return output

