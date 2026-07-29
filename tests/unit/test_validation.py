from morphology_toolkit.core.model import JointModel
from morphology_toolkit.importers import UrdfImporter
from morphology_toolkit.validation import validate_model


def test_valid_fixture_is_export_ready(fixture_models):
    model = UrdfImporter().execute(fixture_models[0])
    report = validate_model(model)
    assert report.errors == 0


def test_cycle_and_bad_reference_are_errors(fixture_models):
    model = UrdfImporter().execute(fixture_models[0])
    model.joints["cycle"] = JointModel("cycle", "fixed", "tip", "base")
    report = validate_model(model)
    assert report.errors > 0


def test_invalid_inertia_is_error(fixture_models):
    model = UrdfImporter().execute(fixture_models[0])
    model.links["base"].inertial.matrix = (-1, 0, 0, 1, 0, 1)
    assert any(item.code == "non_positive_inertia" for item in validate_model(model).diagnostics)
