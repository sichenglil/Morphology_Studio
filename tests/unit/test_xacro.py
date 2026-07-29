from morphology_toolkit.importers import UrdfImporter, XacroImporter, detect_format
from morphology_toolkit.resources import PackageResolver


def test_xacro_parameter_detection(tmp_path):
    source = tmp_path / "model.xacro"
    source.write_text(
        '<robot xmlns:xacro="http://www.ros.org/wiki/xacro"><xacro:arg name="size"/><xacro:arg name="prefix" default=""/></robot>',
        encoding="utf-8",
    )
    assert detect_format(source) == "xacro"
    analysis = XacroImporter().analyze(source)
    assert analysis.parameter_candidates == {"size": None, "prefix": None}


def test_python_api_xacro_with_package_find_and_space_path(tmp_path):
    root = tmp_path / "root with spaces"
    package = root / "sample_description"
    package.mkdir(parents=True)
    (package / "package.xml").write_text(
        "<package><name>sample_description</name></package>", encoding="utf-8"
    )
    (package / "part.xacro").write_text(
        '<robot xmlns:xacro="http://www.ros.org/wiki/xacro"><xacro:macro name="part" params="prefix"><link name="${prefix}base"/></xacro:macro></robot>',
        encoding="utf-8",
    )
    entry = root / "entry.xacro"
    entry.write_text(
        '<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="sample"><xacro:arg name="prefix" default=""/><xacro:include filename="$(find sample_description)/part.xacro"/><xacro:part prefix="$(arg prefix)"/></robot>',
        encoding="utf-8",
    )
    resolver = PackageResolver({"sample_description": package})
    result = XacroImporter().expand(entry, {"prefix": "p_"}, resolver)
    assert result.returncode == 0, result.stderr
    assert result.method == "python_api"
    assert str(package) not in result.xml
    assert "package://sample_description/part.xacro" not in result.xml
    generated = tmp_path / "generated.urdf"
    generated.write_text(result.xml, encoding="utf-8")
    assert "p_base" in UrdfImporter().execute(generated).links


def test_missing_package_is_structured_failure(tmp_path):
    entry = tmp_path / "bad.xacro"
    entry.write_text(
        '<robot xmlns:xacro="http://www.ros.org/wiki/xacro"><xacro:include filename="$(find absent)/part.xacro"/></robot>',
        encoding="utf-8",
    )
    result = XacroImporter().expand(entry, {}, PackageResolver())
    assert result.returncode != 0
    assert result.method == "python_api"
    assert "not found" in result.stderr
