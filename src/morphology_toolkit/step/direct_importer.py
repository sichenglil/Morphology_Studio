"""Build an editable robot model from browser-tessellated STEP solids."""

from __future__ import annotations

import base64
import hashlib
import os
import re
import struct
from pathlib import Path
from typing import Any

from morphology_toolkit.core.model import (
    CollisionModel,
    GeometryModel,
    JointModel,
    LinkModel,
    ResourceReference,
    RobotModel,
    VisualModel,
)
from morphology_toolkit.exporters.urdf_exporter import UrdfExporter

MAX_PARTS = 512
MAX_TOTAL_BYTES = 250 * 1024 * 1024
_SAFE_NAME = re.compile(r"[^A-Za-z0-9_]+")


def safe_name(value: str, fallback: str) -> str:
    name = _SAFE_NAME.sub("_", value.strip()).strip("_") or fallback
    if name[0].isdigit():
        name = f"part_{name}"
    return name[:96]


def step_cache_root() -> Path:
    override = os.environ.get("MORPHOLOGY_STEP_CACHE")
    if override:
        return Path(override).expanduser().resolve()
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / "MorphologyStudio" / "step_imports"
    return Path.cwd() / "artifacts" / "step_imports"


def _decode_stl(value: Any) -> bytes:
    if not isinstance(value, str) or not value:
        raise ValueError("Each STEP part requires a base64 STL payload")
    try:
        data = base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid base64 STL payload") from exc
    if len(data) < 84:
        raise ValueError("Binary STL payload is truncated")
    triangle_count = struct.unpack_from("<I", data, 80)[0]
    if 84 + triangle_count * 50 != len(data):
        raise ValueError("Binary STL triangle count does not match its size")
    return data


def import_step_payload(payload: dict[str, Any]) -> RobotModel:
    parts = payload.get("parts")
    if not isinstance(parts, list) or not 1 <= len(parts) <= MAX_PARTS:
        raise ValueError(f"STEP import requires between 1 and {MAX_PARTS} solids")

    decoded: list[tuple[dict[str, Any], bytes]] = []
    total = 0
    for raw in parts:
        if not isinstance(raw, dict):
            raise ValueError("Invalid STEP solid entry")
        data = _decode_stl(raw.get("stl"))
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise ValueError("STEP tessellation exceeds the 250 MiB import limit")
        decoded.append((raw, data))

    source_name = Path(str(payload.get("source_path") or "model.step")).stem
    robot_name = safe_name(str(payload.get("name") or source_name), "step_robot")
    digest = hashlib.sha256(robot_name.encode("utf-8"))
    for _, data in decoded:
        digest.update(data)
    output = step_cache_root() / digest.hexdigest()[:20]
    mesh_dir = output / "meshes"
    mesh_dir.mkdir(parents=True, exist_ok=True)

    model = RobotModel(robot_name, robot_name, "step", output)
    used: set[str] = set()
    names: list[str] = []
    for index, (raw, data) in enumerate(decoded):
        base = safe_name(str(raw.get("name") or ""), f"link_{index}")
        name = base
        suffix = 2
        while name in used:
            name = f"{base}_{suffix}"
            suffix += 1
        used.add(name)
        names.append(name)
        mesh = mesh_dir / f"{name}.stl"
        if not mesh.exists() or mesh.read_bytes() != data:
            mesh.write_bytes(data)
        resource = ResourceReference(f"meshes/{mesh.name}", resolved_path=mesh)
        geometry = GeometryModel("mesh", resource=resource, scale=(0.001, 0.001, 0.001))
        model.links[name] = LinkModel(
            name,
            visuals=[VisualModel(geometry)],
            collisions=[CollisionModel(geometry)],
        )
        model.resources.append(resource)

    for index, (raw, _) in enumerate(decoded):
        parent_index = raw.get("parent")
        if parent_index is None or parent_index == "":
            continue
        try:
            parent_index = int(parent_index)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid parent for {names[index]}") from exc
        if parent_index < 0 or parent_index >= index:
            raise ValueError(f"Parent of {names[index]} must be an earlier solid")
        joint_type = str(raw.get("joint_type") or "fixed")
        if joint_type not in {"fixed", "revolute", "continuous", "prismatic"}:
            raise ValueError(f"Unsupported joint type: {joint_type}")
        axis_values = raw.get("axis") or [0, 0, 1]
        if not isinstance(axis_values, list) or len(axis_values) != 3:
            raise ValueError(f"Joint axis for {names[index]} must have three values")
        axis = tuple(float(value) for value in axis_values)
        if sum(value * value for value in axis) < 1e-12:
            raise ValueError(f"Joint axis for {names[index]} cannot be zero")
        limit: dict[str, float] = {}
        if joint_type == "revolute":
            limit = {"lower": -3.1416, "upper": 3.1416, "effort": 100.0, "velocity": 1.0}
        elif joint_type == "prismatic":
            limit = {"lower": -0.1, "upper": 0.1, "effort": 100.0, "velocity": 0.1}
        joint_name = safe_name(
            str(raw.get("joint_name") or ""), f"{names[parent_index]}_to_{names[index]}"
        )
        model.joints[joint_name] = JointModel(
            joint_name,
            joint_type,
            names[parent_index],
            names[index],
            axis=None if joint_type == "fixed" else axis,
            limit=limit,
        )

    model.metadata.update(
        {
            "step_source": str(payload.get("source_path") or ""),
            "tessellator": "opencascade.js",
            "unit_scale": 0.001,
        }
    )
    model.source_path = UrdfExporter().export(model, output / "robot.urdf")
    return model
