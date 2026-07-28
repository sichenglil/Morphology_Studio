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
