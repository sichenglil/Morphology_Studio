import hashlib
import json
import shutil
from pathlib import Path

from morphology_toolkit.exporters.portable_package_exporter import PortablePackageExporter
from morphology_toolkit.importers import UrdfImporter
from morphology_toolkit.resources import ResourceResolver
from morphology_toolkit.validation import validate_model


def test_package_survives_source_removal(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    mesh = source / "shape.stl"
    mesh.write_text("solid s\nendsolid s\n", encoding="ascii")
    urdf = source / "robot.urdf"
    urdf.write_text(
        '<robot name="p"><link name="base"><visual><geometry><mesh filename="shape.stl"/></geometry></visual><collision><geometry><mesh filename="shape.stl"/></geometry></collision></link></robot>',
        encoding="utf-8",
    )
    output = tmp_path / "portable"
    PortablePackageExporter().export(UrdfImporter().execute(urdf), output, ResourceResolver(source))
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["resources"][0]["sha256"] == hashlib.sha256(mesh.read_bytes()).hexdigest()
    shutil.rmtree(source)
    packaged = UrdfImporter().execute(output / "robot.urdf")
    assert validate_model(packaged, ResourceResolver(output)).errors == 0


def test_extension_resource_is_packaged(tmp_path: Path):
    package = tmp_path / "package"
    package.mkdir()
    config = package / "config.yaml"
    config.write_text("value: 1", encoding="utf-8")
    urdf = tmp_path / "robot.urdf"
    urdf.write_text(
        '<robot name="p"><link name="base"/><gazebo><plugin name="p" filename="plugin"><parameters>package://demo/config.yaml</parameters></plugin></gazebo></robot>',
        encoding="utf-8",
    )
    model = UrdfImporter().execute(urdf)
    output = tmp_path / "portable"
    PortablePackageExporter().export(
        model, output, ResourceResolver(tmp_path, package_map={"demo": package})
    )
    packaged_text = (output / "robot.urdf").read_text(encoding="utf-8")
    assert "package://" not in packaged_text
    assert "resources/" in packaged_text
