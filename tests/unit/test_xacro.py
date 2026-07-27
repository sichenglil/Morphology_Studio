from morphology_toolkit.importers import XacroImporter, detect_format


def test_xacro_parameter_detection(tmp_path):
    source = tmp_path / "model.xacro"
    source.write_text('<robot xmlns:xacro="http://www.ros.org/wiki/xacro"><xacro:arg name="size"/><xacro:arg name="prefix" default=""/></robot>', encoding="utf-8")
    assert detect_format(source) == "xacro"
    analysis = XacroImporter().analyze(source)
    assert analysis.parameter_candidates == {"size": None, "prefix": None}

