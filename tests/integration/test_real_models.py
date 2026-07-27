from pathlib import Path

import yaml

from morphology_toolkit.assembly import assemble_models
from morphology_toolkit.core.model import AssemblyConnection
from morphology_toolkit.importers import UrdfImporter, XacroImporter
from morphology_toolkit.resources import PackageResolver, ResourceResolver, load_package_map
from morphology_toolkit.validation import validate_model

ROOT = Path.cwd()
PACKAGE_MAP = load_package_map(ROOT / "configs/package_maps/local_models.yaml", ROOT)


def expand_config(config_path: Path, output: Path):
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    result = XacroImporter().expand(ROOT / config["source"], {key: str(value) for key, value in config["arguments"].items()}, PackageResolver(PACKAGE_MAP))
    assert result.returncode == 0, result.stderr
    assert not any(token in result.xml for token in ("$(find ", "${", "<xacro:"))
    output.write_text(result.xml, encoding="utf-8")
    model = UrdfImporter().execute(output)
    assert validate_model(model, ResourceResolver(output.parent, package_map=PACKAGE_MAP)).errors == 0
    return model


def test_real_models_expand_and_generic_assembly(tmp_path: Path):
    arm = expand_config(ROOT / "configs/examples/ur5e_local.yaml", tmp_path / "arm.urdf")
    hand = expand_config(ROOT / "configs/examples/hx5_d20_rev2_right.yaml", tmp_path / "hand.urdf")
    result = assemble_models({"arm": arm, "hand": hand}, [AssemblyConnection("test_mount", "fixed", "arm", "tool0", "hand", "world")], {"arm": "a_", "hand": "h_"})
    assert result.model.root_links == ["a_world"]
    assert len(result.model.links) == 40
    assert len(result.model.joints) == 39
