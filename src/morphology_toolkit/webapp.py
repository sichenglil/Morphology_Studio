from __future__ import annotations

import hashlib
import json
import logging
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote

from morphology_toolkit.assembly import assemble_models
from morphology_toolkit.core.model import (
    AssemblyConnection,
    ProcessingMode,
    RobotModel,
    Transform,
)
from morphology_toolkit.exporters.mjcf_exporter import MjcfExporter
from morphology_toolkit.exporters.portable_package_exporter import PortablePackageExporter
from morphology_toolkit.exporters.urdf_exporter import UrdfExporter
from morphology_toolkit.importers import (
    DirectoryImporter,
    UrdfImporter,
    XacroImporter,
    detect_format,
)
from morphology_toolkit.morphology import generate_morphology
from morphology_toolkit.resources import ResourceResolver, load_package_map
from morphology_toolkit.validation import validate_model

LOGGER = logging.getLogger(__name__)


@dataclass
class EditorSession:
    model: RobotModel | None = None
    source: Path | None = None
    package_map: dict[str, Path] = field(default_factory=dict)
    resources: dict[str, Path] = field(default_factory=dict)
    joint_values: dict[str, float] = field(default_factory=dict)
    changes: list[dict[str, Any]] = field(default_factory=list)

    def clear(self) -> None:
        self.model = None
        self.source = None
        self.package_map.clear()
        self.resources.clear()
        self.joint_values.clear()
        self.changes.clear()


def _pick_path(kind: str) -> str:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        value = filedialog.askdirectory() if kind == "directory" else filedialog.askopenfilename()
        return value or ""
    finally:
        root.destroy()


def _load_model(
    source: Path,
    entry: str | None,
    arguments: dict[str, str],
    package_map: dict[str, Path],
) -> RobotModel:
    fmt = detect_format(source)
    if fmt in {"directory", "ros_package"}:
        return DirectoryImporter().execute(
            source,
            ProcessingMode.ASSISTED,
            {"entry": entry, "arguments": arguments, "package_map": package_map},
        )
    if fmt == "urdf":
        return UrdfImporter().execute(source, ProcessingMode.ASSISTED)
    if fmt == "xacro":
        return XacroImporter().execute(
            source,
            ProcessingMode.ASSISTED,
            {"arguments": arguments, "package_map": package_map},
        )
    raise ValueError(f"Unsupported model format: {fmt}")


def _resource_url(session: EditorSession, path: Path) -> str:
    resolved = path.resolve(strict=True)
    token = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:24]
    session.resources[token] = resolved
    return f"/api/resources/{token}?name={quote(resolved.name)}"


def _scene_manifest(session: EditorSession) -> dict[str, Any]:
    model = session.model
    if model is None:
        return {"robotId": None, "rootLinks": [], "links": [], "joints": [], "resources": []}
    base = session.source.parent if session.source and session.source.is_file() else session.source
    resolver = ResourceResolver(base or Path.cwd(), package_map=session.package_map)
    resource_urls: dict[str, str] = {}
    for item in model.resources:
        resolved = item.resolved_path or resolver.resolve(item.uri)
        if resolved and resolved.is_file():
            resource_urls[item.uri] = _resource_url(session, resolved)

    links = []
    child_joint = {joint.child: joint for joint in model.joints.values()}
    for link in model.links.values():
        visuals = []
        render_geometry = link.collisions if link.collisions else link.visuals
        for visual in render_geometry:
            geometry = visual.geometry
            visuals.append(
                {
                    "kind": geometry.kind,
                    "size": list(geometry.size or []),
                    "scale": list(geometry.scale),
                    "resource": (
                        resource_urls.get(geometry.resource.uri) if geometry.resource else None
                    ),
                    "origin": {
                        "xyz": list(visual.origin.xyz),
                        "rpy": list(visual.origin.rpy),
                    },
                    "material": getattr(visual, "material", None),
                }
            )
        parent = child_joint.get(link.name)
        links.append(
            {
                "id": link.name,
                "name": link.name,
                "parentJoint": parent.name if parent else None,
                "visuals": visuals,
                "collisions": len(link.collisions),
                "renderSource": "collision" if link.collisions else "visual",
                "inertial": model.to_dict()["links"][link.name]["inertial"],
            }
        )
    joints = []
    for joint in model.joints.values():
        joints.append(
            {
                "id": joint.name,
                "name": joint.name,
                "type": joint.joint_type,
                "parent": joint.parent,
                "child": joint.child,
                "origin": {"xyz": list(joint.origin.xyz), "rpy": list(joint.origin.rpy)},
                "axis": list(joint.axis or (1.0, 0.0, 0.0)),
                "limit": joint.limit,
                "value": session.joint_values.get(joint.name, 0.0),
            }
        )
    return {
        "robotId": model.robot_id,
        "displayName": model.display_name,
        "rootLinks": model.root_links,
        "links": links,
        "joints": joints,
        "resources": list(resource_urls.values()),
        "sourceFormat": model.source_format,
    }


def create_app():
    try:
        from fastapi import Body, FastAPI, HTTPException
        from fastapi.responses import FileResponse, HTMLResponse
        from fastapi.staticfiles import StaticFiles
    except ImportError as exc:
        raise RuntimeError("Desktop UI requires morphology-toolkit[desktop]") from exc

    # Some Windows registry configurations report JavaScript as text/plain,
    # which modern WebView2/Chromium correctly refuses for ES modules.
    mimetypes.add_type("text/javascript", ".js", strict=True)
    mimetypes.add_type("text/css", ".css", strict=True)
    app = FastAPI(title="Morphology Studio", docs_url="/api/docs")
    required_body = Body(...)
    session = EditorSession()
    app.state.editor_session = session
    static_root = Path(__file__).with_name("static")
    frontend_root = static_root / "frontend"
    if frontend_root.exists():
        app.mount("/assets", StaticFiles(directory=frontend_root / "assets"), name="assets")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "app": "Morphology Studio"}

    @app.get("/api/status")
    def status():
        try:
            import xacro

            xacro_status = Path(xacro.__file__).name
        except ImportError:
            xacro_status = "NOT_AVAILABLE_LOCAL"
        return {
            "app": "Morphology Studio",
            "mode": "assisted",
            "xacro": xacro_status,
            "ros": "NOT_AVAILABLE_LOCAL",
            "isaac": "NOT_AVAILABLE_LOCAL",
        }

    @app.get("/api/pick")
    def pick(kind: str = "file"):
        if kind not in {"file", "directory"}:
            raise HTTPException(400, "kind must be file or directory")
        return {"path": _pick_path(kind)}

    @app.get("/api/models/analyze")
    def analyze(path: str):
        target = Path(path)
        if not target.exists():
            raise HTTPException(404, "Path not found")
        analysis = DirectoryImporter().analyze(target) if target.is_dir() else None
        return {
            "format": detect_format(target),
            "entries": []
            if analysis is None
            else [
                {
                    "path": str(item.path),
                    "format": item.detected_format,
                    "score": item.score,
                    "confidence": item.confidence,
                    "reason": item.reason,
                    "requiresConfirmation": item.requires_confirmation,
                }
                for item in analysis.entry_candidates
            ],
        }

    @app.post("/api/models/load")
    def load_model(request: dict[str, Any] = required_body):
        if not isinstance(request.get("path"), str) or not request["path"].strip():
            raise HTTPException(422, "path is required")
        source = Path(request["path"]).expanduser().resolve()
        if not source.exists():
            raise HTTPException(404, "Model path not found")
        package_map = (
            load_package_map(Path(request["package_map_path"]), Path.cwd())
            if request.get("package_map_path")
            else {}
        )
        try:
            model = _load_model(
                source,
                request.get("entry"),
                request.get("arguments", {}),
                package_map,
            )
        except Exception as exc:
            LOGGER.exception("Model import failed")
            raise HTTPException(400, str(exc)) from exc
        session.clear()
        session.model = model
        session.source = source
        session.package_map = package_map
        LOGGER.info("Loaded model %s from %s", model.robot_id, source)
        return _scene_manifest(session)

    @app.get("/api/scene")
    def scene():
        return _scene_manifest(session)

    @app.get("/api/models/tree")
    def model_tree():
        manifest = _scene_manifest(session)
        return {
            "robotId": manifest["robotId"],
            "roots": manifest["rootLinks"],
            "links": manifest["links"],
            "joints": manifest["joints"],
        }

    @app.patch("/api/joints/{joint_name}")
    def update_joint(joint_name: str, request: dict[str, Any] = required_body):
        if session.model is None or joint_name not in session.model.joints:
            raise HTTPException(404, "Joint not found")
        joint = session.model.joints[joint_name]
        lower = float(joint.limit.get("lower", -3.141592653589793))
        upper = float(joint.limit.get("upper", 3.141592653589793))
        try:
            value = float(request["value"])
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(422, "value must be a number") from exc
        if not lower <= value <= upper:
            raise HTTPException(422, f"Joint value must be between {lower} and {upper}")
        previous = session.joint_values.get(joint_name, 0.0)
        session.joint_values[joint_name] = value
        session.changes.append(
            {"action": "joint_value", "joint": joint_name, "before": previous, "after": value}
        )
        LOGGER.info("Joint %s changed from %s to %s", joint_name, previous, value)
        return {"joint": joint_name, "value": value, "undoDepth": len(session.changes)}

    @app.post("/api/validation")
    def validation():
        if session.model is None or session.source is None:
            raise HTTPException(409, "No model is loaded")
        base = session.source.parent if session.source.is_file() else session.source
        report = validate_model(
            session.model,
            ResourceResolver(base, package_map=session.package_map),
        )
        return {
            "errors": report.errors,
            "warnings": report.warnings,
            "exportReady": report.export_ready,
            "diagnostics": [vars(item) for item in report.diagnostics],
        }

    @app.post("/api/assembly")
    def assemble(request: dict[str, Any] = required_body):
        if session.model is None or session.source is None:
            raise HTTPException(409, "Load the parent model first")
        required = ("child_path", "parent_link", "child_link", "name")
        if any(not isinstance(request.get(key), str) or not request[key] for key in required):
            raise HTTPException(422, f"Required fields: {', '.join(required)}")
        child_source = Path(request["child_path"]).expanduser().resolve()
        if not child_source.is_file():
            raise HTTPException(404, "Child model path not found")
        try:
            child = _load_model(child_source, None, {}, {})
            parent_base = session.source.parent if session.source.is_file() else session.source
            child_base = child_source.parent
            for model, base in ((session.model, parent_base), (child, child_base)):
                resolver = ResourceResolver(base, package_map=session.package_map)
                for item in model.resources:
                    item.resolved_path = item.resolved_path or resolver.resolve(item.uri)
            values = request.get("transform", [0.0] * 6)
            if not isinstance(values, list) or len(values) != 6:
                raise ValueError("transform must contain XYZ and RPY")
            connection = AssemblyConnection(
                request["name"],
                "fixed",
                "parent",
                request["parent_link"],
                "child",
                request["child_link"],
                Transform(tuple(map(float, values[:3])), tuple(map(float, values[3:]))),
            )
            child_prefix = f"{child.robot_id}_"
            result = assemble_models(
                {"parent": session.model, "child": child},
                [connection],
                {"parent": "", "child": child_prefix},
                request.get("assembly_name", "assembly"),
                ProcessingMode.ASSISTED,
            )
        except Exception as exc:
            LOGGER.exception("Assembly failed")
            raise HTTPException(400, str(exc)) from exc
        session.model = result.model
        session.changes.append({"action": "assembly", "connection": request["name"]})
        LOGGER.info("Assembled child model %s", child.robot_id)
        return _scene_manifest(session)

    @app.post("/api/export")
    def export_model(request: dict[str, Any] = required_body):
        if session.model is None or session.source is None:
            raise HTTPException(409, "No model is loaded")
        output_value = request.get("output")
        export_format = request.get("format")
        if not isinstance(output_value, str) or not output_value:
            raise HTTPException(422, "output is required")
        output = Path(output_value).expanduser().resolve()
        try:
            if export_format == "urdf":
                result = UrdfExporter().export(session.model, output)
            elif export_format == "mjcf":
                result = MjcfExporter().export(session.model, output)
            elif export_format == "morphology":
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(generate_morphology(session.model), indent=2), encoding="utf-8")
                result = output
            elif export_format == "package":
                base = session.source.parent if session.source.is_file() else session.source
                result = PortablePackageExporter().export(
                    session.model,
                    output,
                    ResourceResolver(base, package_map=session.package_map),
                )
            else:
                raise ValueError("format must be urdf, mjcf, morphology, or package")
        except Exception as exc:
            LOGGER.exception("Export failed")
            raise HTTPException(400, str(exc)) from exc
        session.changes.append({"action": "export", "format": export_format})
        return {"ok": True, "output": Path(result).as_posix()}

    @app.get("/api/resources/{token}")
    def resource(token: str):
        if not token.isalnum() or token not in session.resources:
            raise HTTPException(404, "Resource is not registered in the active workspace")
        path = session.resources[token]
        if not path.is_file():
            raise HTTPException(404, "Resource no longer exists")
        return FileResponse(path)

    @app.get("/", response_class=HTMLResponse)
    def home():
        index = frontend_root / "index.html"
        if not index.exists():
            index = static_root / "index.html"
        return index.read_text(encoding="utf-8")

    @app.get("/{route:path}", response_class=HTMLResponse)
    def spa(route: str):
        if route.startswith("api/"):
            raise HTTPException(404, "API route not found")
        index = frontend_root / "index.html"
        if not index.exists():
            raise HTTPException(404, "Frontend build is not installed")
        return index.read_text(encoding="utf-8")

    return app


def run(port: int = 8000):
    import uvicorn

    config = uvicorn.Config(
        app=create_app(),
        host="127.0.0.1",
        port=port,
        log_config=None,
        access_log=False,
        use_colors=False,
    )
    uvicorn.Server(config).run()
