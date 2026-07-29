"""Generate cached 360-degree GIF and PNG previews from packaged URDF meshes."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from morphology_toolkit.services.model_registry import RobotModelEntry, load_registry  # noqa: E402


def _numbers(value: str | None, default=(0.0, 0.0, 0.0)) -> tuple[float, ...]:
    return tuple(float(item) for item in value.split()) if value else default


def _transform(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, 0.0)):
    import numpy as np

    roll, pitch, yaw = rpy
    cr, sr, cp, sp, cy, sy = (
        math.cos(roll),
        math.sin(roll),
        math.cos(pitch),
        math.sin(pitch),
        math.cos(yaw),
        math.sin(yaw),
    )
    matrix = np.eye(4)
    matrix[:3, :3] = (
        (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
        (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
        (-sp, cp * sr, cp * cr),
    )
    matrix[:3, 3] = xyz
    return matrix


def _geometry(node: ET.Element, directory: Path):
    import trimesh

    mesh_node = node.find("mesh")
    if mesh_node is not None:
        reference = mesh_node.get("filename", "").replace("\\", "/")
        path = (directory / reference).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        loaded = trimesh.load(path, force="scene", process=False)
        # Scene graph transforms carry Collada unit conversion (often mm -> m).
        # Concatenating raw geometry drops that transform and distorts the robot.
        mesh = loaded.to_geometry()
        mesh.vertices *= _numbers(mesh_node.get("scale"), (1.0, 1.0, 1.0))
        return mesh
    box = node.find("box")
    if box is not None:
        return trimesh.creation.box(extents=_numbers(box.get("size"), (1.0, 1.0, 1.0)))
    cylinder = node.find("cylinder")
    if cylinder is not None:
        return trimesh.creation.cylinder(
            radius=float(cylinder.get("radius", ".5")), height=float(cylinder.get("length", "1"))
        )
    sphere = node.find("sphere")
    if sphere is not None:
        return trimesh.creation.icosphere(radius=float(sphere.get("radius", ".5")))
    raise ValueError("Unsupported or empty geometry")


def _robot_mesh(urdf: Path):
    import numpy as np
    import trimesh

    root = ET.parse(urdf).getroot()
    parents = {}
    for joint in root.findall("joint"):
        parent, child, origin = joint.find("parent"), joint.find("child"), joint.find("origin")
        if parent is not None and child is not None:
            parents[child.get("link", "")] = (
                parent.get("link", ""),
                _transform(
                    _numbers(origin.get("xyz")) if origin is not None else (0, 0, 0),
                    _numbers(origin.get("rpy")) if origin is not None else (0, 0, 0),
                ),
            )
    cache = {}

    def world(link: str):
        if link not in cache:
            cache[link] = (
                np.eye(4) if link not in parents else world(parents[link][0]) @ parents[link][1]
            )
        return cache[link]

    meshes, warnings = [], []
    for link in root.findall("link"):
        for visual in link.findall("visual"):
            geometry, origin = visual.find("geometry"), visual.find("origin")
            if geometry is None:
                continue
            try:
                mesh = _geometry(geometry, urdf.parent)
                local = _transform(
                    _numbers(origin.get("xyz")) if origin is not None else (0, 0, 0),
                    _numbers(origin.get("rpy")) if origin is not None else (0, 0, 0),
                )
                mesh.apply_transform(world(link.get("name", "")) @ local)
                meshes.append(mesh)
            except Exception as exc:
                warnings.append(f"{link.get('name', '')}: {exc}")
    if not meshes:
        raise RuntimeError("No renderable visual geometry")
    return trimesh.util.concatenate(meshes), warnings


def _digest(entry: RobotModelEntry, size: int, frames: int, fps: int) -> str:
    digest = hashlib.sha256(f"{size}:{frames}:{fps}:v2".encode())
    directory = entry.urdf_path(ROOT).parent
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        digest.update(path.relative_to(directory).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _render(mesh, size: int, frames: int):
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter

    vertices, faces = np.asarray(mesh.vertices, float), np.asarray(mesh.faces, int)
    # Keep complete faces. Random face subsampling makes watertight meshes look
    # like wireframes and is unsuitable for an application preview.
    center = (vertices.min(0) + vertices.max(0)) / 2
    vertices -= center
    radius = max(float(np.linalg.norm(vertices, axis=1).max()), 1e-6)
    elevation = math.radians(18)
    tilt = np.array(
        (
            (1, 0, 0),
            (0, math.cos(elevation), -math.sin(elevation)),
            (0, math.sin(elevation), math.cos(elevation)),
        )
    )
    images = []
    for index in range(frames):
        angle = 2 * math.pi * index / frames
        turn = np.array(
            (
                (math.cos(angle), -math.sin(angle), 0),
                (math.sin(angle), math.cos(angle), 0),
                (0, 0, 1),
            )
        )
        view = vertices @ (tilt @ turn).T
        projected = view[:, :2] * (size * 0.39 / radius)
        projected[:, 0] += size / 2
        projected[:, 1] = size / 2 - projected[:, 1]
        triangles, depths = projected[faces], view[faces, 2].mean(1)
        normals = np.cross(
            view[faces[:, 1]] - view[faces[:, 0]], view[faces[:, 2]] - view[faces[:, 0]]
        )
        lighting = 0.28 + 0.72 * np.abs(normals[:, 2]) / np.maximum(
            np.linalg.norm(normals, axis=1), 1e-9
        )
        image = Image.new("RGB", (size, size), "#f4f6f8")
        shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse(
            (size * 0.22, size * 0.76, size * 0.78, size * 0.88), fill=(35, 45, 55, 55)
        )
        image = Image.alpha_composite(
            image.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(size / 40))
        )
        draw = ImageDraw.Draw(image)
        for face_index in np.argsort(depths):
            shade = float(lighting[face_index])
            color = (int(45 + 70 * shade), int(93 + 92 * shade), int(125 + 105 * shade), 255)
            draw.polygon([tuple(point) for point in triangles[face_index]], fill=color)
        images.append(image.convert("RGB"))
    return images


def generate(entry: RobotModelEntry, force: bool, size: int, frames: int, fps: int) -> dict:
    # The registry GIF is the real in-application operation recording. Keep
    # this mesh-only turntable under a separate development filename.
    gif_path = entry.gif_path(ROOT).with_name("robot_turntable.gif")
    png_path = entry.png_path(ROOT)
    metadata = gif_path.with_suffix(".cache.json")
    digest = _digest(entry, size, frames, fps)
    if not force and gif_path.is_file() and png_path.is_file() and metadata.is_file():
        if json.loads(metadata.read_text(encoding="utf-8")).get("digest") == digest:
            return {
                "urdf": entry.urdf,
                "status": "cached",
                "gif": str(gif_path),
                "png": str(png_path),
            }
    mesh, warnings = _robot_mesh(entry.urdf_path(ROOT))
    images = _render(mesh, size, frames)
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(png_path, optimize=True)
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=round(1000 / fps),
        loop=0,
        optimize=True,
        disposal=2,
    )
    metadata.write_text(
        json.dumps({"digest": digest, "size": size, "frames": frames, "fps": fps}, indent=2),
        encoding="utf-8",
    )
    return {
        "urdf": entry.urdf,
        "status": "generated",
        "gif": str(gif_path),
        "png": str(png_path),
        "warnings": warnings,
    }


def _placeholder(size: int) -> None:
    from PIL import Image, ImageDraw

    path = ROOT / "assets" / "placeholders" / "model-preview.png"
    image = Image.new("RGB", (size, size), "#f4f6f8")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((80, 160, size - 80, size - 160), radius=24, outline="#9aaeba", width=5)
    draw.text((size / 2, size / 2), "Preview unavailable", fill="#526774", anchor="mm")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--urdf")
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--frames", type=int, default=60)
    parser.add_argument("--fps", type=int, default=20)
    args = parser.parse_args()
    _placeholder(args.size)
    entries = load_registry(ROOT)
    if args.urdf:
        entries = [
            item
            for item in entries
            if Path(item.urdf).name == Path(args.urdf).name or item.urdf == args.urdf
        ]
    if not entries:
        print("No matching valid URDF in config", file=sys.stderr)
        return 2
    failed = False
    for entry in entries:
        try:
            print(
                json.dumps(
                    generate(entry, args.force, args.size, args.frames, args.fps),
                    ensure_ascii=False,
                )
            )
        except Exception as exc:
            failed = True
            print(
                json.dumps(
                    {"urdf": entry.urdf, "status": "failed", "error": str(exc)}, ensure_ascii=False
                )
            )
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
