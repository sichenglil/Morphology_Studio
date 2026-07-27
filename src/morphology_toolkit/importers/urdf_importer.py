from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from xml.etree import ElementTree as ET

from morphology_toolkit.core.model import (
    CollisionModel,
    GeometryModel,
    InertialModel,
    JointModel,
    LinkModel,
    MaterialModel,
    ProcessingMode,
    ResourceReference,
    RobotModel,
    Transform,
    VisualModel,
)

from .base import Candidate, ImportAnalysis, Importer


def _numbers(text: Optional[str], count: int, default: Tuple[float, ...]) -> Tuple[float, ...]:
    if not text:
        return default
    values = tuple(float(item) for item in text.split())
    if len(values) != count:
        raise ValueError(f"Expected {count} numeric values, got {text!r}")
    return values


def _transform(element: Optional[ET.Element]) -> Transform:
    if element is None:
        return Transform()
    return Transform(_numbers(element.get("xyz"), 3, (0.0, 0.0, 0.0)), _numbers(element.get("rpy"), 3, (0.0, 0.0, 0.0)))


class UrdfImporter(Importer):
    def analyze(self, path: Path) -> ImportAnalysis:
        path = Path(path).resolve()
        analysis = ImportAnalysis(input_path=path)
        try:
            model = self.execute(path, ProcessingMode.MANUAL)
            analysis.format_candidates.append(Candidate(path, "urdf", 1.0, "XML root is <robot>"))
            analysis.root_candidates = model.root_links
            leaves = sorted(name for name, children in model.children().items() if not children)
            for index, name in enumerate(leaves):
                score = max(0.45, 0.9 - index * 0.03)
                analysis.interface_candidates.append({"link": name, "score": score, "confidence": "high" if score >= 0.8 else "medium", "reason": "kinematic leaf link", "requires_confirmation": score < 0.8})
            analysis.resource_candidates = [item.uri for item in model.resources]
        except Exception as exc:
            analysis.diagnostics.append(str(exc))
        return analysis

    def execute(self, path: Path, mode: ProcessingMode = ProcessingMode.ASSISTED, selection: Optional[Dict[str, Any]] = None) -> RobotModel:
        del mode, selection
        path = Path(path).resolve()
        from .registry import detect_format
        if detect_format(path) == "srdf":
            raise ValueError(f"SRDF is semantic metadata, not a URDF geometry model: {path}")
        root = ET.parse(path).getroot()
        if root.tag.rsplit("}", 1)[-1] != "robot":
            raise ValueError(f"Expected URDF <robot> root: {path}")
        robot_id = root.get("name") or path.stem
        model = RobotModel(robot_id, robot_id, "urdf", path)
        for material in root.findall("material"):
            name = material.get("name")
            if name:
                color = material.find("color")
                rgba = _numbers(color.get("rgba") if color is not None else None, 4, (0.0, 0.0, 0.0, 1.0)) if color is not None else None
                model.materials[name] = MaterialModel(name, rgba)
        for link in root.findall("link"):
            name = link.get("name")
            if not name or name in model.links:
                raise ValueError(f"Missing or duplicate link name: {name!r}")
            item = LinkModel(name)
            for tag, target in (("visual", item.visuals), ("collision", item.collisions)):
                for node in link.findall(tag):
                    geometry = self._geometry(node.find("geometry"), model)
                    if geometry:
                        if tag == "visual":
                            material_node = node.find("material")
                            target.append(VisualModel(geometry, _transform(node.find("origin")), material_node.get("name") if material_node is not None else None))
                        else:
                            target.append(CollisionModel(geometry, _transform(node.find("origin"))))
            inertial = link.find("inertial")
            if inertial is not None:
                mass = inertial.find("mass")
                inertia = inertial.find("inertia")
                if mass is not None and inertia is not None:
                    keys = ("ixx", "ixy", "ixz", "iyy", "iyz", "izz")
                    item.inertial = InertialModel(float(mass.get("value", "nan")), tuple(float(inertia.get(key, "nan")) for key in keys), _transform(inertial.find("origin")))
            model.links[name] = item
        for joint in root.findall("joint"):
            name = joint.get("name")
            parent, child = joint.find("parent"), joint.find("child")
            if not name or name in model.joints or parent is None or child is None:
                raise ValueError(f"Invalid or duplicate joint: {name!r}")
            axis = joint.find("axis")
            limit = joint.find("limit")
            mimic = joint.find("mimic")
            model.joints[name] = JointModel(
                name=name,
                joint_type=joint.get("type", ""),
                parent=parent.get("link", ""),
                child=child.get("link", ""),
                origin=_transform(joint.find("origin")),
                axis=_numbers(axis.get("xyz") if axis is not None else None, 3, (1.0, 0.0, 0.0)) if axis is not None else None,
                limit={key: float(value) for key, value in (limit.attrib.items() if limit is not None else []) if key in {"lower", "upper", "effort", "velocity"}},
                mimic=mimic.get("joint") if mimic is not None else None,
            )
        return model

    @staticmethod
    def _geometry(node: Optional[ET.Element], model: RobotModel) -> Optional[GeometryModel]:
        if node is None or not list(node):
            return None
        shape = list(node)[0]
        kind = shape.tag.rsplit("}", 1)[-1]
        if kind == "mesh":
            uri = shape.get("filename", "")
            resource = ResourceReference(uri)
            model.resources.append(resource)
            return GeometryModel(kind, resource, scale=_numbers(shape.get("scale"), 3, (1.0, 1.0, 1.0)))
        if kind == "box":
            return GeometryModel(kind, size=_numbers(shape.get("size"), 3, (1.0, 1.0, 1.0)))
        if kind in {"sphere", "cylinder", "capsule"}:
            values = tuple(float(shape.get(key)) for key in ("radius", "length") if shape.get(key) is not None)
            return GeometryModel(kind, size=values)
        return GeometryModel(kind)
