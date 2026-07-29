"""Optional STEP-to-URDF adapter integration and geometry helpers."""

from .adapter import Step2UrdfAdapter, StepAdapterStatus
from .geometry import (
    AxisCandidate,
    GeometryTolerance,
    LineFeature,
    classify_arc,
    classify_cylinder,
    classify_line,
    distribute_mass,
    normalize_axis,
    sanitize_name,
    stable_part_id,
    validate_inertia,
)
from .package_importer import Step2UrdfPackageImporter

__all__ = [
    "AxisCandidate",
    "GeometryTolerance",
    "LineFeature",
    "Step2UrdfAdapter",
    "Step2UrdfPackageImporter",
    "StepAdapterStatus",
    "classify_arc",
    "classify_cylinder",
    "classify_line",
    "distribute_mass",
    "normalize_axis",
    "sanitize_name",
    "stable_part_id",
    "validate_inertia",
]
