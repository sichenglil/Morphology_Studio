from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ProcessingMode(str, Enum):
    AUTO = "auto"
    ASSISTED = "assisted"
    MANUAL = "manual"


@dataclass
class Transform:
    xyz: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rpy: Tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class ResourceReference:
    uri: str
    kind: str = "mesh"
    resolved_path: Optional[Path] = None


@dataclass
class GeometryModel:
    kind: str
    resource: Optional[ResourceReference] = None
    size: Optional[Tuple[float, ...]] = None
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)


@dataclass
class VisualModel:
    geometry: GeometryModel
    origin: Transform = field(default_factory=Transform)
    material: Optional[str] = None


@dataclass
class CollisionModel:
    geometry: GeometryModel
    origin: Transform = field(default_factory=Transform)


@dataclass
class InertialModel:
    mass: float
    matrix: Tuple[float, float, float, float, float, float]
    origin: Transform = field(default_factory=Transform)


@dataclass
class LinkModel:
    name: str
    visuals: List[VisualModel] = field(default_factory=list)
    collisions: List[CollisionModel] = field(default_factory=list)
    inertial: Optional[InertialModel] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JointModel:
    name: str
    joint_type: str
    parent: str
    child: str
    origin: Transform = field(default_factory=Transform)
    axis: Optional[Tuple[float, float, float]] = None
    limit: Dict[str, float] = field(default_factory=dict)
    mimic: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dynamics: Dict[str, float] = field(default_factory=dict)


@dataclass
class MaterialModel:
    name: str
    rgba: Optional[Tuple[float, float, float, float]] = None
    texture: Optional[ResourceReference] = None


@dataclass
class SensorModel:
    name: str
    frame: Optional[str] = None
    sensor_type: str = "generic"


@dataclass
class ActuatorModel:
    name: str
    joint: Optional[str] = None


@dataclass
class TransmissionModel:
    name: str
    joints: List[str] = field(default_factory=list)


@dataclass
class SemanticMetadata:
    tags: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class Diagnostic:
    severity: str
    code: str
    message: str
    subject: Optional[str] = None


@dataclass
class RobotModel:
    robot_id: str
    display_name: str
    source_format: str
    source_path: Path
    links: Dict[str, LinkModel] = field(default_factory=dict)
    joints: Dict[str, JointModel] = field(default_factory=dict)
    materials: Dict[str, MaterialModel] = field(default_factory=dict)
    sensors: Dict[str, SensorModel] = field(default_factory=dict)
    actuators: Dict[str, ActuatorModel] = field(default_factory=dict)
    transmissions: Dict[str, TransmissionModel] = field(default_factory=dict)
    resources: List[ResourceReference] = field(default_factory=list)
    semantic_tags: SemanticMetadata = field(default_factory=SemanticMetadata)
    metadata: Dict[str, Any] = field(default_factory=dict)
    diagnostics: List[Diagnostic] = field(default_factory=list)
    extension_elements: List[str] = field(default_factory=list)

    @property
    def root_links(self) -> List[str]:
        children = {joint.child for joint in self.joints.values()}
        return sorted(set(self.links) - children)

    def children(self) -> Dict[str, List[str]]:
        result = {name: [] for name in self.links}
        for joint in self.joints.values():
            if joint.parent in result:
                result[joint.parent].append(joint.child)
        return result

    def to_dict(self) -> Dict[str, Any]:
        def convert(value: Any) -> Any:
            if isinstance(value, Path):
                return value.as_posix()
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            if isinstance(value, (list, tuple)):
                return [convert(v) for v in value]
            return value

        return convert(asdict(self))


@dataclass
class AssemblyConnection:
    name: str
    joint_type: str
    parent_model: str
    parent_link: str
    child_model: str
    child_link: str
    origin: Transform = field(default_factory=Transform)
