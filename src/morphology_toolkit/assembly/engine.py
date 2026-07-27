from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
from xml.etree import ElementTree as ET

from morphology_toolkit.core.model import (
    AssemblyConnection,
    Diagnostic,
    JointModel,
    ProcessingMode,
    RobotModel,
)


@dataclass
class AssemblyAnalysis:
    diagnostics: List[Diagnostic] = field(default_factory=list)
    conflicts: Dict[str, List[str]] = field(default_factory=dict)
    requires_confirmation: bool = False


@dataclass
class AssemblyResult:
    model: RobotModel
    source_map: Dict[str, Dict[str, str]]
    diagnostics: List[Diagnostic]


def _prefixed(model: RobotModel, prefix: str) -> tuple:
    result = copy.deepcopy(model)
    link_map = {name: f"{prefix}{name}" for name in result.links}
    joint_map = {name: f"{prefix}{name}" for name in result.joints}
    material_map = {name: f"{prefix}{name}" for name in result.materials}
    result.links = {link_map[name]: link for name, link in result.links.items()}
    for name, link in result.links.items():
        link.name = name
        for visual in link.visuals:
            if visual.material in material_map:
                visual.material = material_map[visual.material]
    result.joints = {joint_map[name]: joint for name, joint in result.joints.items()}
    for name, joint in result.joints.items():
        joint.name = name
        joint.parent = link_map.get(joint.parent, joint.parent)
        joint.child = link_map.get(joint.child, joint.child)
        if joint.mimic:
            joint.mimic = joint_map.get(joint.mimic, joint.mimic)
    result.materials = {material_map[name]: material for name, material in result.materials.items()}
    for name, material in result.materials.items():
        material.name = name
    result.transmissions = {f"{prefix}{name}": transmission for name, transmission in result.transmissions.items()}
    for name, transmission in result.transmissions.items():
        transmission.name = name
        transmission.joints = [joint_map.get(joint, joint) for joint in transmission.joints]
    result.sensors = {f"{prefix}{name}": sensor for name, sensor in result.sensors.items()}
    for name, sensor in result.sensors.items():
        sensor.name = name
        sensor.frame = link_map.get(sensor.frame, sensor.frame) if sensor.frame else None
    result.actuators = {f"{prefix}{name}": actuator for name, actuator in result.actuators.items()}
    for name, actuator in result.actuators.items():
        actuator.name = name
        actuator.joint = joint_map.get(actuator.joint, actuator.joint) if actuator.joint else None
    replacements = {**link_map, **joint_map, **material_map}
    rewritten_extensions = []
    for raw in result.extension_elements:
        element = ET.fromstring(raw)
        for node in element.iter():
            for key, value in list(node.attrib.items()):
                if value in replacements: node.set(key, replacements[value])
            if node.text and node.text.strip() in replacements:
                node.text = node.text.replace(node.text.strip(), replacements[node.text.strip()])
        rewritten_extensions.append(ET.tostring(element, encoding="unicode"))
    result.extension_elements = rewritten_extensions
    return result, link_map, joint_map


def analyze_assembly(models: Dict[str, RobotModel], connections: List[AssemblyConnection], prefixes: Dict[str, str]) -> AssemblyAnalysis:
    analysis = AssemblyAnalysis()
    if len(models) != len(set(models)):
        analysis.diagnostics.append(Diagnostic("ERROR", "duplicate_model", "Model IDs must be unique"))
    seen_links: Dict[str, str] = {}
    for model_id, model in models.items():
        prefix = prefixes.get(model_id, "")
        for name in model.links:
            target = f"{prefix}{name}"
            if target in seen_links:
                analysis.conflicts.setdefault("links", []).append(target)
            seen_links[target] = model_id
    for connection in connections:
        for model_id, link, role in ((connection.parent_model, connection.parent_link, "parent"), (connection.child_model, connection.child_link, "child")):
            if model_id not in models:
                analysis.diagnostics.append(Diagnostic("ERROR", "unknown_model", f"Unknown {role} model {model_id!r}", connection.name))
            elif link not in models[model_id].links:
                analysis.diagnostics.append(Diagnostic("ERROR", "unknown_link", f"Unknown {role} link {link!r} in {model_id!r}", connection.name))
        if connection.joint_type != "fixed":
            analysis.diagnostics.append(Diagnostic("ERROR", "unsupported_connection", "Version 0.1 executes fixed assembly joints only", connection.name))
    analysis.requires_confirmation = bool(analysis.conflicts or any(item.severity == "ERROR" for item in analysis.diagnostics))
    return analysis


def assemble_models(models: Dict[str, RobotModel], connections: List[AssemblyConnection], prefixes: Dict[str, str], name: str = "combined_robot", mode: ProcessingMode = ProcessingMode.ASSISTED) -> AssemblyResult:
    analysis = analyze_assembly(models, connections, prefixes)
    if any(item.severity == "ERROR" for item in analysis.diagnostics):
        raise ValueError("Assembly analysis failed: " + "; ".join(item.message for item in analysis.diagnostics))
    if analysis.conflicts:
        raise ValueError(f"Namespace conflicts remain: {analysis.conflicts}")
    combined = RobotModel(name, name, "assembly", Path("assembly.yaml"))
    source_map: Dict[str, Dict[str, str]] = {}
    link_maps: Dict[str, Dict[str, str]] = {}
    for model_id, model in models.items():
        transformed, link_map, joint_map = _prefixed(model, prefixes.get(model_id, ""))
        link_maps[model_id] = link_map
        source_map[model_id] = {**link_map, **joint_map}
        for collection in ("links", "joints", "materials", "sensors", "actuators", "transmissions"):
            target, values = getattr(combined, collection), getattr(transformed, collection)
            overlap = set(target) & set(values)
            if overlap:
                raise ValueError(f"Conflicting {collection}: {sorted(overlap)}")
            target.update(values)
        combined.resources.extend(transformed.resources)
        combined.extension_elements.extend(transformed.extension_elements)
    for connection in connections:
        if connection.name in combined.joints:
            raise ValueError(f"Connection joint conflicts with existing joint: {connection.name}")
        combined.joints[connection.name] = JointModel(
            connection.name,
            connection.joint_type,
            link_maps[connection.parent_model][connection.parent_link],
            link_maps[connection.child_model][connection.child_link],
            connection.origin,
        )
    if len(combined.root_links) != 1:
        raise ValueError(f"Assembly must produce exactly one root link, got {combined.root_links}")
    if _has_cycle(combined):
        raise ValueError("Assembly creates a kinematic cycle")
    combined.metadata["source_map"] = source_map
    combined.metadata["processing_mode"] = mode.value
    return AssemblyResult(combined, source_map, analysis.diagnostics)


def _has_cycle(model: RobotModel) -> bool:
    graph = model.children()
    visiting, visited = set(), set()
    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph.get(node, [])):
            return True
        visiting.remove(node)
        visited.add(node)
        return False
    return any(visit(node) for node in graph)
