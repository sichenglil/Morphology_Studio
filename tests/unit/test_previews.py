from PIL import Image

from morphology_toolkit.paths import assets_dir


def test_combined_robot_preview_is_an_animated_software_recording():
    preview = assets_dir() / "previews" / "ur5e_hx5_right" / "robot.gif"
    with Image.open(preview) as image:
        assert image.size == (960, 540)
        assert image.n_frames >= 40
        assert image.info.get("loop") == 0
