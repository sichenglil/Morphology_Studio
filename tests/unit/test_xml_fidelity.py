from pathlib import Path
from xml.etree import ElementTree as ET

from morphology_toolkit.assembly import assemble_models
from morphology_toolkit.exporters.urdf_exporter import UrdfExporter
from morphology_toolkit.importers import UrdfImporter


def test_unknown_extensions_round_trip_and_rewrite(tmp_path: Path):
    source = tmp_path / "extended.urdf"
    source.write_text('''<robot name="extended"><link name="base"/><gazebo reference="base"><plugin name="p" filename="plugin"><frame>base</frame></plugin></gazebo><ros2_control name="system" type="system"><joint name="drive"/></ros2_control><transmission name="t"><joint name="drive"/></transmission></robot>''', encoding="utf-8")
    model = UrdfImporter().execute(source)
    assert len(model.extension_elements) == 3
    combined = assemble_models({"model": model}, [], {"model": "p_"}).model
    output = UrdfExporter().export(combined, tmp_path / "roundtrip.urdf")
    root = ET.parse(output).getroot()
    assert root.find("gazebo").get("reference") == "p_base"
    assert root.find("gazebo/plugin/frame").text == "p_base"
    assert root.find("ros2_control") is not None
    assert root.find("transmission") is not None
