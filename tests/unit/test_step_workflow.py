from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from morphology_toolkit.core.model import JointModel, LinkModel, RobotModel
from morphology_toolkit.exporters.urdf_exporter import UrdfExporter
from morphology_toolkit.importers import detect_format
from morphology_toolkit.step import (
    GeometryTolerance,
    Step2UrdfAdapter,
    Step2UrdfPackageImporter,
    classify_arc,
    classify_cylinder,
    classify_line,
    distribute_mass,
    normalize_axis,
    sanitize_name,
    stable_part_id,
    validate_inertia,
)
from morphology_toolkit.step.geometry import step_length_to_m
from morphology_toolkit.validation import validate_model
from morphology_toolkit.workspace import Workspace


def test_step_extension_magic_and_invalid_input(tmp_path: Path):
    step = tmp_path / "assembly.step"
    step.write_text("ISO-10303-21;\nHEADER;\nENDSEC;\nEND-ISO-10303-21;", encoding="ascii")
    assert detect_format(step) == "step"
    stp = tmp_path / "part.stp"
    stp.write_text("invalid", encoding="ascii")
    assert detect_format(stp) == "step"
    assert not Step2UrdfPackageImporter.is_package(stp)


def test_optional_adapter_discovery(tmp_path: Path, monkeypatch):
    root = tmp_path / "adapter"
    (root / "node_modules").mkdir(parents=True)
    (root / "package.json").write_text('{"scripts":{"dev":"vite"}}', encoding="utf-8")
    fake_pnpm = tmp_path / "pnpm.cmd"
    fake_pnpm.write_text("", encoding="utf-8")
    monkeypatch.setattr("morphology_toolkit.step.adapter.shutil.which", lambda _: str(fake_pnpm))
    status = Step2UrdfAdapter(root).status()
    assert status.available and status.installed and status.root == root.resolve()


def test_step_units_names_and_stable_duplicate_ids():
    assert step_length_to_m(1000, "mm") == pytest.approx(1.0)
    assert step_length_to_m(2, "in") == pytest.approx(0.0508)
    assert sanitize_name(" 12 / wrist & hand ") == "_12_wrist_hand"
    assert stable_part_id(["assembly", "bolt"], 0) == stable_part_id(["assembly", "bolt"], 0)
    assert stable_part_id(["assembly", "bolt"], 0) != stable_part_id(["assembly", "bolt"], 1)


def test_geometry_feature_classification_and_degenerate_handling():
    line = classify_line((0, 0, 0), (0, 0, 2), GeometryTolerance(1e-9))
    assert line and line.direction == pytest.approx((0, 0, 1))
    assert classify_line((0, 0, 0), (0, 0, 1e-10)) is None
    assert classify_arc((1, 2, 3), (0, 2, 0), 0.1, 1.2).direction == pytest.approx((0, 1, 0))
    assert classify_cylinder((0, 0, 0), (1, 0, 0), 0.2, 1).kind == "revolute"
    with pytest.raises(ValueError, match="degenerate"):
        normalize_axis((0, 0, 0))


def test_mass_distribution_and_inertia_validation():
    assert distribute_mass(12, [1, 2, 3]) == pytest.approx([2, 4, 6])
    validate_inertia(1, (1, 0, 0, 1, 0, 1))
    with pytest.raises(ValueError):
        distribute_mass(1, [0, 0])
    with pytest.raises(ValueError):
        validate_inertia(1, (-1, 0, 0, 1, 0, 1))


def _joint_model(joint_type: str) -> RobotModel:
    model = RobotModel("robot", "robot & test", "step2urdf", Path("input.step"))
    model.links = {"base": LinkModel("base"), "child": LinkModel("child")}
    model.joints["axis"] = JointModel(
        "axis",
        joint_type,
        "base",
        "child",
        axis=(0, 0, 1) if joint_type != "fixed" else None,
        limit={"lower": -1, "upper": 1, "effort": 2, "velocity": 3}
        if joint_type in {"revolute", "prismatic"}
        else {},
        dynamics={"damping": 0.1, "friction": 0.2},
    )
    return model


@pytest.mark.parametrize("joint_type", ["fixed", "revolute", "prismatic"])
def test_joint_urdf_generation_and_xml_escaping(tmp_path: Path, joint_type: str):
    output = UrdfExporter().export(_joint_model(joint_type), tmp_path / f"{joint_type}.urdf")
    text = output.read_text(encoding="utf-8")
    assert 'name="robot &amp; test"' in text
    root = ET.parse(output).getroot()
    joint = root.find("joint")
    assert joint is not None and joint.get("type") == joint_type
    assert joint.find("dynamics").get("damping") == "0.1"
    assert (joint.find("limit") is not None) == (joint_type in {"revolute", "prismatic"})


def test_invalid_joint_dynamics_and_cycle_are_reported():
    model = _joint_model("revolute")
    model.joints["axis"].dynamics["damping"] = float("nan")
    model.joints["cycle"] = JointModel("cycle", "fixed", "child", "base")
    codes = {item.code for item in validate_model(model).diagnostics}
    assert {"invalid_dynamics", "cycle"} <= codes


def test_step2urdf_zip_round_trip_and_relative_mesh(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    package = tmp_path / "converted.zip"
    urdf = (
        '<robot name="converted"><link name="base"><visual><geometry>'
        '<mesh filename="meshes/base.stl"/></geometry></visual></link></robot>'
    )
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("robot.urdf", urdf)
        archive.writestr("meshes/base.stl", "solid base\nendsolid base\n")
    assert detect_format(package) == "step2urdf_package"
    model = Step2UrdfPackageImporter().execute(package)
    assert model.robot_id == "converted"
    assert model.source_format == "step2urdf"
    assert model.resources[0].uri == "meshes/base.stl"
    assert (model.source_path.parent / model.resources[0].uri).is_file()


def test_step2urdf_zip_rejects_path_traversal(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    package = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("robot.urdf", '<robot name="safe"><link name="base"/></robot>')
        archive.writestr("../outside.txt", "unsafe")
    with pytest.raises(ValueError, match="Unsafe path"):
        Step2UrdfPackageImporter().execute(package)


def test_workspace_schema_version_round_trip_and_backward_compatibility(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "workspace")
    workspace.settings["ui"] = {"panel": "joint"}
    workspace.save()
    assert Workspace.open(workspace.root).schema_version == 1
    old = workspace.root / "workspace.yaml"
    old.write_text("mode: assisted\nsettings: {}\n", encoding="utf-8")
    assert Workspace.open(workspace.root).schema_version == 1
