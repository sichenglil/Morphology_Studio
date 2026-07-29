from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class GeometryTolerance:
    linear_m: float = 1e-6
    angular_rad: float = 1e-6


@dataclass(frozen=True)
class LineFeature:
    origin_m: tuple[float, float, float]
    direction: tuple[float, float, float]
    length_m: float


@dataclass(frozen=True)
class AxisCandidate:
    kind: str
    origin_m: tuple[float, float, float]
    direction: tuple[float, float, float]
    confidence: float


def step_length_to_m(value: float, unit: str = "mm") -> float:
    factors = {"m": 1.0, "cm": 1e-2, "mm": 1e-3, "um": 1e-6, "in": 0.0254}
    try:
        return float(value) * factors[unit.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported STEP length unit: {unit}") from exc


def normalize_axis(values: Sequence[float], tolerance: float = 1e-12) -> tuple[float, float, float]:
    if len(values) != 3 or not all(math.isfinite(float(value)) for value in values):
        raise ValueError("Joint axis must contain three finite values")
    norm = math.sqrt(sum(float(value) ** 2 for value in values))
    if norm <= tolerance:
        raise ValueError("Joint axis is degenerate")
    return tuple(float(value) / norm for value in values)  # type: ignore[return-value]


def sanitize_name(value: str, fallback: str = "part") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_") or fallback
    return f"_{cleaned}" if cleaned[0].isdigit() else cleaned


def stable_part_id(path: Iterable[str], occurrence: int = 0) -> str:
    key = "/".join(path) + f"#{occurrence}"
    return f"part_{hashlib.sha256(key.encode('utf-8')).hexdigest()[:12]}"


def classify_line(
    start: Sequence[float], end: Sequence[float], tolerance: GeometryTolerance | None = None
) -> LineFeature | None:
    tolerance = tolerance or GeometryTolerance()
    if len(start) != 3 or len(end) != 3:
        raise ValueError("Line endpoints must be 3D")
    delta = tuple(float(b) - float(a) for a, b in zip(start, end))
    length = math.sqrt(sum(value * value for value in delta))
    if not math.isfinite(length) or length <= tolerance.linear_m:
        return None
    return LineFeature(tuple(map(float, start)), normalize_axis(delta), length)  # type: ignore[arg-type]


def classify_arc(
    center: Sequence[float], axis: Sequence[float], radius_m: float, sweep_rad: float
) -> AxisCandidate | None:
    if radius_m <= 0 or abs(sweep_rad) <= 1e-8 or not math.isfinite(radius_m + sweep_rad):
        return None
    return AxisCandidate("revolute", tuple(map(float, center)), normalize_axis(axis), 0.9)  # type: ignore[arg-type]


def classify_cylinder(
    center: Sequence[float], axis: Sequence[float], radius_m: float, height_m: float
) -> AxisCandidate | None:
    if radius_m <= 0 or height_m <= 0 or not math.isfinite(radius_m + height_m):
        return None
    return AxisCandidate("revolute", tuple(map(float, center)), normalize_axis(axis), 0.95)  # type: ignore[arg-type]


def distribute_mass(total_mass: float, volumes: Sequence[float]) -> list[float]:
    if not math.isfinite(total_mass) or total_mass <= 0:
        raise ValueError("Total mass must be finite and positive")
    if not volumes or any(not math.isfinite(value) or value < 0 for value in volumes):
        raise ValueError("Volumes must be finite and non-negative")
    total_volume = sum(volumes)
    if total_volume <= 0:
        raise ValueError("At least one part must have positive volume")
    return [total_mass * value / total_volume for value in volumes]


def validate_inertia(mass: float, matrix: Sequence[float]) -> None:
    if not math.isfinite(mass) or mass <= 0:
        raise ValueError("Mass must be finite and positive")
    if len(matrix) != 6 or not all(math.isfinite(value) for value in matrix):
        raise ValueError("Inertia must contain six finite values")
    ixx, ixy, ixz, iyy, iyz, izz = matrix
    if min(ixx, iyy, izz) <= 0:
        raise ValueError("Inertia diagonal must be positive")
    if ixx * iyy <= ixy * ixy or ixx * izz <= ixz * ixz or iyy * izz <= iyz * iyz:
        raise ValueError("Inertia matrix must be positive definite")
