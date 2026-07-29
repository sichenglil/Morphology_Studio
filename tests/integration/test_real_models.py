from pathlib import Path

from morphology_toolkit.importers import UrdfImporter
from morphology_toolkit.resources import ResourceResolver
from morphology_toolkit.validation import validate_model

ROOT = Path.cwd()


def test_packaged_combined_robot_is_valid():
    source = ROOT / "assets/robot_models/ur5e_hx5_right/robot.urdf"
    model = UrdfImporter().execute(source)
    report = validate_model(model, ResourceResolver(source.parent))
    assert report.errors == 0
    assert model.robot_id == "ur5e_hx5_right"
    assert len(model.links) == 40
    assert len(model.joints) == 39
