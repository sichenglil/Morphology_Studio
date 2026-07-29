from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

from morphology_toolkit.core.model import Diagnostic, RobotModel
from morphology_toolkit.resources import ResourceResolver


@dataclass
class ValidationReport:
    diagnostics: List[Diagnostic] = field(default_factory=list)

    @property
    def errors(self) -> int:
        return sum(item.severity == "ERROR" for item in self.diagnostics)

    @property
    def warnings(self) -> int:
        return sum(item.severity == "WARNING" for item in self.diagnostics)

    @property
    def export_ready(self) -> bool:
        return self.errors == 0

    def write(self, json_path: Path, markdown_path: Path) -> None:
        payload = {
            "summary": {
                "errors": self.errors,
                "warnings": self.warnings,
                "export_ready": self.export_ready,
            },
            "diagnostics": [asdict(item) for item in self.diagnostics],
        }
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = [
            "# Model validation",
            "",
            f"- Export ready: **{self.export_ready}**",
            f"- Errors: {self.errors}",
            f"- Warnings: {self.warnings}",
            "",
            "## Diagnostics",
            "",
        ]
        lines.extend(
            f"- **{item.severity}** `{item.code}`: {item.message}"
            + (f" (`{item.subject}`)" if item.subject else "")
            for item in self.diagnostics
        )
        markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_model(
    model: RobotModel, resolver: Optional[ResourceResolver] = None
) -> ValidationReport:
    report = ValidationReport()
    roots = model.root_links
    if len(roots) != 1:
        report.diagnostics.append(
            Diagnostic(
                "ERROR", "root_count", f"Expected one root link, found {len(roots)}: {roots}"
            )
        )
    graph = model.children()
    visited, visiting = set(), set()

    def visit(node: str) -> None:
        if node in visiting:
            report.diagnostics.append(
                Diagnostic("ERROR", "cycle", "Kinematic cycle detected", node)
            )
            return
        if node in visited:
            return
        visiting.add(node)
        for child in graph.get(node, []):
            visit(child)
        visiting.remove(node)
        visited.add(node)

    for root in roots:
        visit(root)
    reachable = set(visited)
    for name in sorted(set(model.links) - visited):
        visit(name)
    for name in sorted(set(model.links) - reachable):
        report.diagnostics.append(
            Diagnostic("ERROR", "orphan_link", "Link is disconnected from the kinematic root", name)
        )
    valid_types = {"fixed", "revolute", "continuous", "prismatic", "floating", "planar"}
    for joint in model.joints.values():
        if joint.parent not in model.links or joint.child not in model.links:
            report.diagnostics.append(
                Diagnostic(
                    "ERROR", "invalid_reference", "Joint parent or child does not exist", joint.name
                )
            )
        if joint.joint_type not in valid_types:
            report.diagnostics.append(
                Diagnostic(
                    "ERROR",
                    "joint_type",
                    f"Unsupported joint type {joint.joint_type!r}",
                    joint.name,
                )
            )
        if joint.joint_type in {"revolute", "prismatic"}:
            if joint.axis is None:
                report.diagnostics.append(
                    Diagnostic("ERROR", "missing_axis", "Movable joint has no axis", joint.name)
                )
            for key in ("lower", "upper", "effort", "velocity"):
                if key not in joint.limit:
                    report.diagnostics.append(
                        Diagnostic(
                            "WARNING", "missing_limit", f"Joint limit lacks {key}", joint.name
                        )
                    )
            if (
                "lower" in joint.limit
                and "upper" in joint.limit
                and joint.limit["lower"] > joint.limit["upper"]
            ):
                report.diagnostics.append(
                    Diagnostic(
                        "ERROR", "invalid_limit", "Lower joint limit exceeds upper", joint.name
                    )
                )
        if joint.joint_type == "continuous" and any(
            key in joint.limit for key in ("lower", "upper")
        ):
            report.diagnostics.append(
                Diagnostic(
                    "WARNING",
                    "continuous_limit",
                    "Continuous joint has position limits",
                    joint.name,
                )
            )
        if any(not math.isfinite(value) or value < 0 for value in joint.dynamics.values()):
            report.diagnostics.append(
                Diagnostic(
                    "ERROR",
                    "invalid_dynamics",
                    "Joint damping and friction must be finite and non-negative",
                    joint.name,
                )
            )
        if joint.mimic and joint.mimic not in model.joints:
            report.diagnostics.append(
                Diagnostic("ERROR", "missing_mimic", "Mimic target does not exist", joint.name)
            )
    for link in model.links.values():
        inertia = link.inertial
        if inertia is None:
            report.diagnostics.append(
                Diagnostic("WARNING", "missing_inertial", "Link has no inertial data", link.name)
            )
            continue
        if not math.isfinite(inertia.mass) or inertia.mass <= 0:
            report.diagnostics.append(
                Diagnostic("ERROR", "invalid_mass", "Mass must be finite and positive", link.name)
            )
        ixx, ixy, ixz, iyy, iyz, izz = inertia.matrix
        if not all(math.isfinite(value) for value in inertia.matrix):
            report.diagnostics.append(
                Diagnostic(
                    "ERROR", "invalid_inertia", "Inertia contains non-finite values", link.name
                )
            )
        elif (
            min(ixx, iyy, izz) <= 0
            or ixx * iyy <= ixy * ixy
            or ixx * izz <= ixz * ixz
            or iyy * izz <= iyz * iyz
        ):
            report.diagnostics.append(
                Diagnostic(
                    "ERROR",
                    "non_positive_inertia",
                    "Inertia matrix is not positive definite by principal minors",
                    link.name,
                )
            )
        if not link.visuals:
            report.diagnostics.append(
                Diagnostic("INFO", "missing_visual", "Link has no visual geometry", link.name)
            )
        if not link.collisions:
            report.diagnostics.append(
                Diagnostic(
                    "WARNING", "missing_collision", "Link has no collision geometry", link.name
                )
            )
    for resource in model.resources:
        uri = resource.uri
        if Path(uri).is_absolute() or (len(uri) > 2 and uri[1:3] in {":/", ":\\"}):
            report.diagnostics.append(
                Diagnostic("ERROR", "absolute_resource", "Resource path is not portable", uri)
            )
        resolved = resolver.resolve(uri) if resolver else None
        if resolver and (resolved is None or not resolved.exists()):
            report.diagnostics.append(
                Diagnostic("ERROR", "missing_resource", "Resource could not be resolved", uri)
            )
    report.diagnostics.append(
        Diagnostic(
            "INFO",
            "compatibility",
            "URDF structural checks completed; target converters perform additional compatibility checks",
        )
    )
    return report
