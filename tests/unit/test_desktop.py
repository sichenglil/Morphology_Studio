import logging
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from morphology_toolkit.desktop import available_port, create_server
from morphology_toolkit.logging_config import configure_logging
from morphology_toolkit.webapp import create_app


def test_desktop_port_and_routes():
    assert available_port() > 0
    app = create_app()
    paths = {route.path for route in app.routes}
    assert {
        "/",
        "/api/health",
        "/api/status",
        "/api/models/analyze",
        "/api/models/load",
        "/api/models/tree",
        "/api/scene",
        "/api/validation",
        "/api/resources/{token}",
    } <= paths


def test_desktop_server_has_console_independent_uvicorn_config():
    server = create_server(available_port())
    assert server.config.log_config is None
    assert server.config.access_log is False
    assert server.config.use_colors is False


def test_logging_survives_missing_standard_streams(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", None)
    path = configure_logging()
    logging.getLogger("test").warning("windowed mode works")
    assert path == tmp_path / "MorphologyStudio" / "logs" / "morphology-studio.log"
    assert "windowed mode works" in path.read_text(encoding="utf-8")


def _write_test_model(root: Path) -> Path:
    (root / "mesh.stl").write_text("solid mesh\nendsolid mesh\n", encoding="utf-8")
    model = root / "robot.urdf"
    model.write_text(
        '<robot name="test"><link name="base"><visual><geometry>'
        '<mesh filename="mesh.stl"/></geometry></visual></link></robot>',
        encoding="utf-8",
    )
    return model


def test_scene_and_registered_resource_api(tmp_path):
    client = TestClient(create_app())
    model = _write_test_model(tmp_path)
    response = client.post("/api/models/load", json={"path": str(model)})
    assert response.status_code == 200
    scene = response.json()
    assert scene["robotId"] == "test"
    assert scene["links"][0]["visuals"][0]["resource"].startswith("/api/resources/")
    resource = client.get(scene["links"][0]["visuals"][0]["resource"])
    assert resource.status_code == 200


def test_resource_api_rejects_unregistered_and_path_inputs():
    client = TestClient(create_app())
    assert client.get("/api/resources/notregistered").status_code == 404
    assert client.get("/api/resources/..%2Fsecret.txt").status_code == 404
    assert client.get("/api/resources/C%3A%5CWindows%5Cwin.ini").status_code == 404


def test_generic_ui_assembly_and_export(tmp_path):
    parent = tmp_path / "parent.urdf"
    child = tmp_path / "child.urdf"
    parent.write_text('<robot name="parent"><link name="mount"/></robot>', encoding="utf-8")
    child.write_text('<robot name="child"><link name="root"/></robot>', encoding="utf-8")
    client = TestClient(create_app())
    assert client.post("/api/models/load", json={"path": str(parent)}).status_code == 200
    response = client.post(
        "/api/assembly",
        json={
            "child_path": str(child),
            "parent_link": "mount",
            "child_link": "root",
            "name": "tool_mount",
            "transform": [0, 0, 0.1, 0, 0, 0],
        },
    )
    assert response.status_code == 200
    scene = response.json()
    assert len(scene["rootLinks"]) == 1
    assert any(joint["name"] == "tool_mount" for joint in scene["joints"])
    output = tmp_path / "assembled.urdf"
    exported = client.post("/api/export", json={"format": "urdf", "output": str(output)})
    assert exported.status_code == 200
    assert output.is_file()


def test_transform_commit_revision_undo_and_urdf_writeback(tmp_path):
    model = tmp_path / "editable.urdf"
    model.write_text(
        '<robot name="editable"><link name="base"/><link name="tool">'
        '<visual><origin xyz="0 0 0"/><geometry><box size="1 1 1"/></geometry></visual>'
        '</link><joint name="mount" type="fixed"><parent link="base"/><child link="tool"/>'
        '<origin xyz="0 0 1"/></joint></robot>', encoding="utf-8"
    )
    client = TestClient(create_app())
    scene = client.post("/api/models/load", json={"path": str(model)}).json()
    response = client.post("/api/workspaces/current/transforms/commit", json={
        "targetType": "link", "entityId": "tool", "expectedRevision": scene["revision"],
        "transform": {"xyz": [0.2, 0.3, 1.4], "rpy": [0, 0, 0.5]},
    })
    assert response.status_code == 200
    assert response.json()["scene"]["joints"][0]["origin"]["xyz"] == [0.2, 0.3, 1.4]
    stale = client.post("/api/workspaces/current/transforms/commit", json={
        "targetType": "link", "entityId": "tool", "expectedRevision": 0,
        "transform": {"xyz": [0, 0, 0], "rpy": [0, 0, 0]},
    })
    assert stale.status_code == 409
    assert client.post("/api/workspaces/current/history/undo").json()["joints"][0]["origin"]["xyz"] == [0.0, 0.0, 1.0]
    assert client.post("/api/workspaces/current/history/redo").json()["joints"][0]["origin"]["xyz"] == [0.2, 0.3, 1.4]
    output = tmp_path / "written.urdf"
    assert client.post("/api/export", json={"format": "urdf", "output": str(output)}).status_code == 200
    assert 'xyz="0.2 0.3 1.4"' in output.read_text(encoding="utf-8")


def test_transform_rejects_non_finite_and_saves_workspace(tmp_path):
    model = tmp_path / "root.urdf"
    model.write_text('<robot name="root"><link name="base"/></robot>', encoding="utf-8")
    client = TestClient(create_app())
    client.post("/api/models/load", json={"path": str(model)})
    invalid = client.post("/api/workspaces/current/transforms/commit", json={
        "targetType": "model_instance", "entityId": "root", "expectedRevision": 0,
        "transform": {"xyz": ["NaN", 0, 0], "rpy": [0, 0, 0]},
    })
    assert invalid.status_code == 422
    workspace = tmp_path / "workspace.yaml"
    saved = client.post("/api/workspaces/current/save", json={"path": str(workspace), "settings": {"space": "local"}})
    assert saved.status_code == 200
    assert "transform_edits:" in workspace.read_text(encoding="utf-8")
    reopened = client.post("/api/workspaces/open", json={"path": str(workspace)})
    assert reopened.status_code == 200
    assert reopened.json()["robotId"] == "root"


def test_new_workspace_clears_scene_with_complete_manifest(tmp_path):
    model = tmp_path / "clear.urdf"
    model.write_text('<robot name="clear"><link name="base"/></robot>', encoding="utf-8")
    client = TestClient(create_app())
    assert client.post("/api/models/load", json={"path": str(model)}).json()["robotId"] == "clear"
    scene = client.post("/api/workspaces/current/new", json={}).json()
    assert scene["robotId"] is None
    assert scene["rootTransform"] == {"xyz": [0.0, 0.0, 0.0], "rpy": [0.0, 0.0, 0.0]}
    assert scene["history"] == {"canUndo": False, "canRedo": False}


def test_batch_joint_commit_revision_limits_and_single_history(tmp_path):
    model = tmp_path / "joints.urdf"
    model.write_text(
        '<robot name="joints"><link name="base"/><link name="one"/><link name="two"/>'
        '<joint name="a" type="revolute"><parent link="base"/><child link="one"/>'
        '<limit lower="-1" upper="1" effort="1" velocity="1"/></joint>'
        '<joint name="b" type="prismatic"><parent link="one"/><child link="two"/>'
        '<limit lower="0" upper="0.5" effort="1" velocity="1"/></joint></robot>', encoding="utf-8"
    )
    app = create_app()
    client = TestClient(app)
    client.post("/api/models/load", json={"path": str(model)})
    response = client.post("/api/workspaces/current/joint-states/commit", json={
        "values": {"a": 0.4, "b": 0.2}, "expectedRevision": 0,
    })
    assert response.status_code == 200
    assert response.json() == {"values": {"a": 0.4, "b": 0.2}, "revision": 1, "saved": False, "validation": "lightweight"}
    session = app.state.editor_session
    assert session.joint_values == {"a": 0.4, "b": 0.2}
    assert len(session.changes) == 1
    undone = client.post("/api/workspaces/current/history/undo")
    assert undone.status_code == 200
    assert {item["id"]: item["value"] for item in undone.json()["joints"]} == {"a": 0.0, "b": 0.0}
    redone = client.post("/api/workspaces/current/history/redo")
    assert redone.status_code == 200
    assert {item["id"]: item["value"] for item in redone.json()["joints"]} == {"a": 0.4, "b": 0.2}
    workspace = tmp_path / "joint-workspace.yaml"
    assert client.post("/api/workspaces/current/save", json={"path": str(workspace)}).status_code == 200
    assert client.post("/api/workspaces/open", json={"path": str(workspace)}).json()["joints"][0]["value"] == 0.4
    assert client.post("/api/workspaces/current/joint-states/commit", json={"values": {"a": 0.5}, "expectedRevision": 0}).status_code == 409
    assert client.post("/api/workspaces/current/joint-states/commit", json={"values": {"b": 2}, "expectedRevision": 3}).status_code == 422
