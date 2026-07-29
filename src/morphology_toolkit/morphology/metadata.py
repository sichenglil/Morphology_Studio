from __future__ import annotations

from typing import Any, Dict

from morphology_toolkit.core.model import RobotModel


def generate_morphology(model: RobotModel) -> Dict[str, Any]:
    children = model.children()
    leaves = sorted(name for name, values in children.items() if not values)
    movable = [
        joint
        for joint in model.joints.values()
        if joint.joint_type not in {"fixed", "floating", "planar"}
    ]
    return {
        "robot_id": model.robot_id,
        "root_links": model.root_links,
        "links": sorted(model.links),
        "joints": sorted(model.joints),
        "kinematic_graph": {key: sorted(value) for key, value in children.items()},
        "end_effectors": [
            {"link": name, "source": "kinematic_leaf", "confirmed": False} for name in leaves
        ],
        "sensors": sorted(model.sensors),
        "actuators": sorted(model.actuators),
        "joint_limits_normalized": [
            {
                "joint": joint.name,
                "lower": joint.limit.get("lower"),
                "upper": joint.limit.get("upper"),
            }
            for joint in movable
        ],
        "semantic_groups": model.semantic_tags.tags,
        "contact_candidates": leaves,
    }
