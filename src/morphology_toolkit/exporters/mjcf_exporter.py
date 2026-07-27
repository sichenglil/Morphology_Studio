from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from morphology_toolkit.core.model import RobotModel


class MjcfExporter:
    """Deterministic model-level MJCF exporter for basic URDF kinematics."""

    def export(self, model: RobotModel, output: Path) -> Path:
        if len(model.root_links) != 1:
            raise ValueError("MJCF export requires exactly one root")
        mujoco = ET.Element("mujoco", model=model.display_name)
        ET.SubElement(mujoco, "compiler", angle="radian", coordinate="local")
        world = ET.SubElement(mujoco, "worldbody")
        by_parent = {}
        for joint in model.joints.values(): by_parent.setdefault(joint.parent, []).append(joint)
        def add_body(parent, link_name, incoming=None):
            body = ET.SubElement(parent, "body", name=link_name)
            if incoming:
                body.set("pos", " ".join(map(str, incoming.origin.xyz)))
                if incoming.joint_type != "fixed":
                    kind = "hinge" if incoming.joint_type in {"revolute", "continuous"} else "slide"
                    attrs = {"name": incoming.name, "type": kind, "axis": " ".join(map(str, incoming.axis or (1, 0, 0)))}
                    if incoming.joint_type != "continuous" and "lower" in incoming.limit and "upper" in incoming.limit:
                        attrs.update(limited="true", range=f"{incoming.limit['lower']} {incoming.limit['upper']}")
                    ET.SubElement(body, "joint", **attrs)
            link = model.links[link_name]
            if link.inertial:
                ET.SubElement(body, "inertial", mass=str(link.inertial.mass), pos=" ".join(map(str, link.inertial.origin.xyz)), fullinertia=" ".join(map(str, link.inertial.matrix)))
            for joint in by_parent.get(link_name, []): add_body(body, joint.child, joint)
        add_body(world, model.root_links[0])
        ET.SubElement(mujoco, "actuator")
        ET.indent(mujoco, space="  ")
        output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(mujoco).write(output, encoding="utf-8", xml_declaration=True)
        return output

