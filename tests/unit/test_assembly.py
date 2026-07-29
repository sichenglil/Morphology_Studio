from morphology_toolkit.assembly import assemble_models
from morphology_toolkit.core.model import AssemblyConnection, Transform
from morphology_toolkit.importers import UrdfImporter


def test_two_model_fixed_assembly_and_prefix_rewrite(fixture_models):
    arm, tool, _ = fixture_models
    models = {"a": UrdfImporter().execute(arm), "b": UrdfImporter().execute(tool)}
    connection = AssemblyConnection(
        "mount_joint", "fixed", "a", "tip", "b", "mount", Transform((0, 0, 0.1))
    )
    result = assemble_models(models, [connection], {"a": "a_", "b": "b_"})
    assert result.model.root_links == ["a_base"]
    assert result.model.joints["a_axis"].parent == "a_base"
    assert result.model.joints["mount_joint"].child == "b_mount"


def test_three_model_chain(fixture_models):
    arm, tool, camera = fixture_models
    importer = UrdfImporter()
    models = {
        "arm": importer.execute(arm),
        "tool": importer.execute(tool),
        "camera": importer.execute(camera),
    }
    connections = [
        AssemblyConnection("arm_tool", "fixed", "arm", "tip", "tool", "mount"),
        AssemblyConnection("tool_camera", "fixed", "tool", "mount", "camera", "camera_frame"),
    ]
    result = assemble_models(models, connections, {key: key + "_" for key in models})
    assert len(result.model.links) == 4
    assert len(result.model.joints) == 3
    assert result.model.root_links == ["arm_base"]
