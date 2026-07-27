from morphology_toolkit.core.model import ProcessingMode
from morphology_toolkit.importers import DirectoryImporter, UrdfImporter, detect_format


def test_detect_and_parse_urdf(fixture_models):
    arm, _, _ = fixture_models
    assert detect_format(arm) == "urdf"
    model = UrdfImporter().execute(arm)
    assert model.root_links == ["base"]
    assert set(model.links) == {"base", "tip"}
    assert model.joints["axis"].limit["upper"] == 1


def test_directory_requires_assisted_confirmation(fixture_models):
    arm, tool, _ = fixture_models
    analysis = DirectoryImporter().analyze(arm.parent)
    assert len(analysis.entry_candidates) == 3
    try:
        DirectoryImporter().execute(arm.parent, ProcessingMode.ASSISTED)
    except ValueError as exc:
        assert "confirmation" in str(exc).lower()
    else:
        raise AssertionError("assisted mode silently selected an ambiguous entry")


def test_manual_directory_selection(fixture_models):
    arm, _, _ = fixture_models
    model = DirectoryImporter().execute(arm.parent, ProcessingMode.MANUAL, {"entry": arm})
    assert model.robot_id == "arm"

