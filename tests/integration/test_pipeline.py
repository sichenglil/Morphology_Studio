from pathlib import Path

from morphology_toolkit.assembly import assemble_models
from morphology_toolkit.core.model import AssemblyConnection
from morphology_toolkit.exporters.mjcf_exporter import MjcfExporter
from morphology_toolkit.exporters.urdf_exporter import UrdfExporter
from morphology_toolkit.importers import UrdfImporter, detect_format
from morphology_toolkit.morphology import generate_morphology
from morphology_toolkit.validation import validate_model


def test_generic_assemble_export_reimport_validate(fixture_models, tmp_path: Path):
    arm, tool, _ = fixture_models
    importer = UrdfImporter()
    result = assemble_models(
        {"one": importer.execute(arm), "two": importer.execute(tool)},
        [AssemblyConnection("connection", "fixed", "one", "tip", "two", "mount")],
        {"one": "one_", "two": "two_"},
    )
    urdf = UrdfExporter().export(result.model, tmp_path / "combined.urdf")
    reloaded = importer.execute(urdf)
    assert validate_model(reloaded).errors == 0
    mjcf = MjcfExporter().export(reloaded, tmp_path / "combined.xml")
    assert detect_format(mjcf) == "mjcf"
    import xml.etree.ElementTree as ET

    root = ET.parse(mjcf).getroot()
    assert len(root.findall(".//body")) == len(reloaded.links)
    assert root.find(".//joint").get("range") == "-1.0 1.0"
    morphology = generate_morphology(reloaded)
    assert morphology["root_links"] == ["one_base"]
    assert {item["link"] for item in morphology["end_effectors"]} == {"two_mount"}
