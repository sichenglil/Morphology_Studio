from __future__ import annotations

import os
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
        asset = ET.SubElement(mujoco, "asset")
        mesh_names = {}
        for index, resource in enumerate(model.resources):
            if resource.kind != "mesh" or resource.uri in mesh_names: continue
            name = f"mesh_{index}"
            uri = resource.uri.replace("\\", "/")
            if not uri.startswith(("package://", "file://", "http://", "https://")):
                source = (model.source_path.parent / uri).resolve()
                uri = os.path.relpath(source, Path(output).resolve().parent).replace("\\", "/")
            ET.SubElement(asset, "mesh", name=name, file=uri)
            mesh_names[resource.uri] = name
        world = ET.SubElement(mujoco, "worldbody")
        by_parent = {}
        for joint in model.joints.values(): by_parent.setdefault(joint.parent, []).append(joint)
        def add_body(parent, link_name, incoming=None):
            body = ET.SubElement(parent, "body", name=link_name)
            if incoming:
                body.set("pos", " ".join(map(str, incoming.origin.xyz)))
                body.set("euler", " ".join(map(str, incoming.origin.rpy)))
                if incoming.joint_type != "fixed":
                    kind = "hinge" if incoming.joint_type in {"revolute", "continuous"} else "slide"
                    attrs = {"name": incoming.name, "type": kind, "axis": " ".join(map(str, incoming.axis or (1, 0, 0)))}
                    if incoming.joint_type != "continuous" and "lower" in incoming.limit and "upper" in incoming.limit:
                        attrs.update(limited="true", range=f"{incoming.limit['lower']} {incoming.limit['upper']}")
                    ET.SubElement(body, "joint", **attrs)
            link = model.links[link_name]
            if link.inertial:
                ixx, ixy, ixz, iyy, iyz, izz = link.inertial.matrix
                ET.SubElement(body, "inertial", mass=str(link.inertial.mass), pos=" ".join(map(str, link.inertial.origin.xyz)), fullinertia=" ".join(map(str, (ixx, iyy, izz, ixy, ixz, iyz))))
            for visual in link.visuals:
                geometry = visual.geometry
                attrs = {"group": "1", "pos": " ".join(map(str, visual.origin.xyz)), "euler": " ".join(map(str, visual.origin.rpy))}
                if geometry.kind == "mesh" and geometry.resource:
                    attrs.update(type="mesh", mesh=mesh_names[geometry.resource.uri])
                elif geometry.kind == "box":
                    attrs.update(type="box", size=" ".join(str(value / 2) for value in geometry.size or (1, 1, 1)))
                elif geometry.kind == "sphere": attrs.update(type="sphere", size=str((geometry.size or (1,))[0]))
                elif geometry.kind in {"cylinder", "capsule"}:
                    size = geometry.size or (1, 1); attrs.update(type=geometry.kind, size=f"{size[0]} {size[1] / 2}")
                else: continue
                ET.SubElement(body, "geom", **attrs)
            for joint in by_parent.get(link_name, []): add_body(body, joint.child, joint)
        add_body(world, model.root_links[0])
        ET.SubElement(mujoco, "actuator")
        ET.indent(mujoco, space="  ")
        output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(mujoco).write(output, encoding="utf-8", xml_declaration=True)
        return output
