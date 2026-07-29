from morphology_toolkit.services.model_registry import load_registry


def test_registry_contains_only_combined_robot():
    entries = load_registry()
    assert [entry.id for entry in entries] == ["ur5e_hx5_right"]
    assert entries[0].primary
    assert (
        entries[0]
        .urdf_path(
            __import__("morphology_toolkit.paths", fromlist=["resource_root"]).resource_root()
        )
        .is_file()
    )
