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


def test_srdf_is_visible_but_not_geometry_candidate(tmp_path):
    srdf = tmp_path / "robot.srdf"
    srdf.write_text('<robot name="semantic"><group name="arm"><joint name="axis"/></group><disable_collisions link1="a" link2="b" reason="Adjacent"/></robot>', encoding="utf-8")
    assert detect_format(srdf) == "srdf"
    analysis = DirectoryImporter().analyze(tmp_path)
    assert not analysis.entry_candidates
    assert analysis.format_candidates[0].detected_format == "srdf"
    try:
        UrdfImporter().execute(srdf)
    except ValueError as exc:
        assert "SRDF" in str(exc)
    else:
        raise AssertionError("SRDF was accepted as URDF")


def test_real_srdf_is_excluded():
    from pathlib import Path
    path = Path("models/robotis_hand/robotis_hand_moveit_config/config/hx5_d20_right/hx5_d20_right.srdf")
    assert detect_format(path) == "srdf"
