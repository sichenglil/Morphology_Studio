from pathlib import Path

import pytest

from morphology_toolkit.exporters import usd_exporter


def test_usd_does_not_fake_output_without_isaac(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(usd_exporter, "_discover_isaac_python", lambda: None)
    output = tmp_path / "robot.usd"
    with pytest.raises(RuntimeError, match="Isaac Sim Python was not found"):
        usd_exporter.launch_usd_conversion(tmp_path / "robot.urdf", output)
    assert not output.exists()
