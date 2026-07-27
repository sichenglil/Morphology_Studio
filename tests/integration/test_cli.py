import json

from morphology_toolkit.cli import main


def test_cli_import_and_workspace(fixture_models, tmp_path, capsys):
    arm, _, _ = fixture_models
    workspace = tmp_path / "workspace"
    assert main(["workspace", "create", "--path", str(workspace)]) == 0
    assert (workspace / "workspace.yaml").exists()
    assert main(["import", "--path", str(arm), "--workspace", str(workspace)]) == 0
    output = capsys.readouterr().out
    assert '"robot_id": "arm"' in output
    assert (workspace / "logs" / "session.json").exists()

