from pathlib import Path

import pytest

ROBOT = """<?xml version="1.0"?>
<robot name="arm">
  <link name="base"><inertial><mass value="1"/><inertia ixx="1" ixy="0" ixz="0" iyy="1" iyz="0" izz="1"/></inertial><visual><geometry><box size="1 1 1"/></geometry></visual><collision><geometry><box size="1 1 1"/></geometry></collision></link>
  <link name="tip"><inertial><mass value="0.5"/><inertia ixx=".1" ixy="0" ixz="0" iyy=".1" iyz="0" izz=".1"/></inertial><visual><geometry><box size=".1 .1 .2"/></geometry></visual><collision><geometry><box size=".1 .1 .2"/></geometry></collision></link>
  <joint name="axis" type="revolute"><parent link="base"/><child link="tip"/><axis xyz="0 0 1"/><limit lower="-1" upper="1" effort="2" velocity="3"/></joint>
</robot>"""

TOOL = """<robot name="tool"><link name="mount"><inertial><mass value=".1"/><inertia ixx=".01" ixy="0" ixz="0" iyy=".01" iyz="0" izz=".01"/></inertial><visual><geometry><box size=".1 .1 .1"/></geometry></visual><collision><geometry><box size=".1 .1 .1"/></geometry></collision></link></robot>"""


@pytest.fixture
def fixture_models(tmp_path: Path):
    arm = tmp_path / "arm.urdf"
    arm.write_text(ROBOT, encoding="utf-8")
    tool = tmp_path / "tool.urdf"
    tool.write_text(TOOL, encoding="utf-8")
    camera = tmp_path / "camera.urdf"
    camera.write_text(
        TOOL.replace('name="tool"', 'name="camera"').replace('name="mount"', 'name="camera_frame"'),
        encoding="utf-8",
    )
    return arm, tool, camera
