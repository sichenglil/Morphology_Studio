from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from morphology_toolkit.core.model import GeometryModel, RobotModel, Transform


def _origin(parent: ET.Element, transform: Transform) -> None:
    ET.SubElement(
        parent,
        "origin",
        xyz=" ".join(map(str, transform.xyz)),
        rpy=" ".join(map(str, transform.rpy)),
    )


def _geometry(parent: ET.Element, geometry: GeometryModel) -> None:
    node = ET.SubElement(parent, "geometry")
    if geometry.kind == "mesh" and geometry.resource:
        ET.SubElement(
            node,
            "mesh",
            filename=geometry.resource.uri.replace("\\", "/"),
            scale=" ".join(map(str, geometry.scale)),
        )
    elif geometry.kind == "box":
        ET.SubElement(node, "box", size=" ".join(map(str, geometry.size or (1, 1, 1))))
    elif geometry.kind == "sphere":
        ET.SubElement(node, "sphere", radius=str((geometry.size or (1,))[0]))
    elif geometry.kind in {"cylinder", "capsule"}:
        values = geometry.size or (1, 1)
        ET.SubElement(node, geometry.kind, radius=str(values[0]), length=str(values[1]))


class UrdfExporter:
    def export(self, model: RobotModel, output: Path) -> Path:
        robot = ET.Element("robot", name=model.display_name)
        for material in model.materials.values():
            node = ET.SubElement(robot, "material", name=material.name)
            if material.rgba:
                ET.SubElement(node, "color", rgba=" ".join(map(str, material.rgba)))
        for link in model.links.values():
            node = ET.SubElement(robot, "link", name=link.name)
            for visual in link.visuals:
                child = ET.SubElement(node, "visual")
                _origin(child, visual.origin)
                _geometry(child, visual.geometry)
                if visual.material:
                    ET.SubElement(child, "material", name=visual.material)
            for collision in link.collisions:
                child = ET.SubElement(node, "collision")
                _origin(child, collision.origin)
                _geometry(child, collision.geometry)
            if link.inertial:
                child = ET.SubElement(node, "inertial")
                _origin(child, link.inertial.origin)
                ET.SubElement(child, "mass", value=str(link.inertial.mass))
                keys = ("ixx", "ixy", "ixz", "iyy", "iyz", "izz")
                ET.SubElement(child, "inertia", **dict(zip(keys, map(str, link.inertial.matrix))))
        for joint in model.joints.values():
            node = ET.SubElement(robot, "joint", name=joint.name, type=joint.joint_type)
            ET.SubElement(node, "parent", link=joint.parent)
            ET.SubElement(node, "child", link=joint.child)
            _origin(node, joint.origin)
            if joint.axis is not None:
                ET.SubElement(node, "axis", xyz=" ".join(map(str, joint.axis)))
            if joint.limit:
                ET.SubElement(
                    node, "limit", **{key: str(value) for key, value in joint.limit.items()}
                )
            if joint.dynamics:
                ET.SubElement(
                    node, "dynamics", **{key: str(value) for key, value in joint.dynamics.items()}
                )
            if joint.mimic:
                ET.SubElement(node, "mimic", joint=joint.mimic)
        for raw in model.extension_elements:
            robot.append(ET.fromstring(raw))
        ET.indent(robot, space="  ")
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(robot).write(output, encoding="utf-8", xml_declaration=True)
        return output
