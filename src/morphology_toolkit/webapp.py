from __future__ import annotations

import hashlib
import json
import logging
import math
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
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
from morphology_toolkit.paths import assets_dir, resource_root
from morphology_toolkit.resources import ResourceResolver, load_package_map
from morphology_toolkit.services.model_registry import load_registry
from morphology_toolkit.step import Step2UrdfAdapter, Step2UrdfPackageImporter
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
    transform_history: list[dict[str, Any]] = field(default_factory=list)
    history_cursor: int = 0
    revision: int = 0
    root_transform: Transform = field(default_factory=Transform)
    assembly_joints: set[str] = field(default_factory=set)

    def clear(self) -> None:
        self.model = None
        self.source = None
        self.package_map.clear()
        self.resources.clear()
        self.joint_values.clear()
        self.changes.clear()
        self.transform_history.clear()
        self.history_cursor = 0
        self.revision = 0
        self.root_transform = Transform()
        self.assembly_joints.clear()


def _transform_dict(value: Transform, scale: tuple[float, float, float] | None = None):
    result: dict[str, Any] = {"xyz": list(value.xyz), "rpy": list(value.rpy)}
    if scale is not None:
        result["scale"] = list(scale)
    return result


def _parse_transform(payload: dict[str, Any], allow_scale: bool = False):
    try:
        xyz = tuple(float(item) for item in payload["xyz"])
        rpy = tuple(float(item) for item in payload["rpy"])
        scale = tuple(float(item) for item in payload.get("scale", (1, 1, 1)))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("transform requires numeric xyz and rpy arrays") from exc
    if len(xyz) != 3 or len(rpy) != 3 or len(scale) != 3:
        raise ValueError("xyz, rpy and scale must contain three numbers")
    values = (*xyz, *rpy, *(scale if allow_scale else ()))
    if not all(math.isfinite(item) for item in values):
        raise ValueError("transform values must be finite")
    if allow_scale and any(item <= 0 for item in scale):
        raise ValueError("scale values must be greater than zero")
    return Transform(xyz, rpy), scale


def _resolve_transform_target(session: EditorSession, target_type: str, entity_id: str):
    model = session.model
    if model is None:
        raise KeyError("No model is loaded")
    if target_type == "model_instance":
        return session, "root_transform", None
    if target_type in {"joint", "assembly_connection"}:
        joint = model.joints[entity_id]
        if target_type == "assembly_connection" and entity_id not in session.assembly_joints:
            raise KeyError("Assembly connection not found")
        return joint, "origin", None
    if target_type == "link":
        matches = [joint for joint in model.joints.values() if joint.child == entity_id]
        if not matches:
            raise ValueError("Root links use the model_instance transform")
        return matches[0], "origin", None
    if target_type in {"visual", "collision"}:
        parts = entity_id.rsplit(":", 2)
        if len(parts) != 3 or parts[1] != target_type:
            raise KeyError("Invalid geometry entity id")
        link = model.links[parts[0]]
        items = link.visuals if target_type == "visual" else link.collisions
        return items[int(parts[2])], "origin", "geometry"
    raise KeyError("Unsupported transform target")


def _target_state(session: EditorSession, target_type: str, entity_id: str):
    owner, attribute, geometry = _resolve_transform_target(session, target_type, entity_id)
    scale = owner.geometry.scale if geometry else None
    return _transform_dict(getattr(owner, attribute), scale)


def _apply_target_state(session: EditorSession, target_type: str, entity_id: str, state):
    owner, attribute, geometry = _resolve_transform_target(session, target_type, entity_id)
    transform, scale = _parse_transform(state, geometry is not None)
    setattr(owner, attribute, transform)
    if geometry:
        owner.geometry.scale = scale


def _pick_path(kind: str) -> str:
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        value = (
            filedialog.askdirectory()
            if kind == "directory"
            else filedialog.asksaveasfilename(defaultextension=".yaml")
            if kind == "save"
            else filedialog.askopenfilename()
        )
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
    if fmt == "step2urdf_package":
        return Step2UrdfPackageImporter().execute(source, ProcessingMode.ASSISTED)
    if fmt == "step":
        raise ValueError(
            "STEP requires the interactive step2urdf adapter. Launch it, define links and joints, "
            "export the URDF ZIP, then import that ZIP."
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
        return {
            "robotId": None,
            "rootLinks": [],
            "links": [],
            "joints": [],
            "resources": [],
            "revision": session.revision,
            "rootTransform": _transform_dict(session.root_transform),
            "assemblyJoints": [],
            "history": {"canUndo": False, "canRedo": False},
        }
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
        render_geometry = link.visuals if link.visuals else link.collisions
        render_kind = "visual" if link.visuals else "collision"
        for index, visual in enumerate(render_geometry):
            geometry = visual.geometry
            visuals.append(
                {
                    "id": f"{link.name}:{render_kind}:{index}",
                    "entityType": render_kind,
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
        "revision": session.revision,
        "rootTransform": _transform_dict(session.root_transform),
        "assemblyJoints": sorted(session.assembly_joints),
        "history": {
            "canUndo": session.history_cursor > 0,
            "canRedo": session.history_cursor < len(session.transform_history),
        },
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
    packaged_assets = assets_dir()
    if packaged_assets.is_dir():
        app.mount("/app-assets", StaticFiles(directory=packaged_assets), name="app-assets")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "app": "Morphology Studio"}

    @app.get("/api/model-registry")
    def model_registry():
        root = resource_root()
        return {"models": [entry.public_dict(root) for entry in load_registry(root)]}

    @app.post("/api/model-registry/{model_id}/load")
    def load_packaged_model(model_id: str):
        root = resource_root()
        entry = next((item for item in load_registry(root) if item.id == model_id), None)
        if entry is None:
            raise HTTPException(404, "Packaged model not found")
        source = entry.urdf_path(root).resolve()
        try:
            model = _load_model(source, None, {}, {})
        except Exception as exc:
            LOGGER.exception("Packaged model import failed: %s", model_id)
            raise HTTPException(400, str(exc)) from exc
        session.clear()
        session.model, session.source = model, source
        LOGGER.info("Loaded packaged model %s from %s", model.robot_id, source)
        return _scene_manifest(session)

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
            "step2urdf": Step2UrdfAdapter().status().public_dict(),
        }

    @app.get("/api/step-adapter/status")
    def step_adapter_status():
        return Step2UrdfAdapter().status().public_dict()

    @app.post("/api/step-adapter/launch")
    def launch_step_adapter(request: Optional[dict[str, Any]] = None):
        root = Path(request["path"]) if request and request.get("path") else None
        try:
            return Step2UrdfAdapter(root).launch().public_dict()
        except Exception as exc:
            LOGGER.exception("Unable to launch step2urdf adapter")
            raise HTTPException(409, str(exc)) from exc

    @app.get("/api/pick")
    def pick(kind: str = "file"):
        if kind not in {"file", "directory", "save"}:
            raise HTTPException(400, "kind must be file, directory or save")
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
            "stepAdapter": Step2UrdfAdapter().status().public_dict()
            if detect_format(target) == "step"
            else None,
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
        session.source = model.source_path
        session.package_map = package_map
        LOGGER.info("Loaded model %s from %s", model.robot_id, source)
        return _scene_manifest(session)

    @app.get("/api/scene")
    def scene():
        return _scene_manifest(session)

    @app.get("/api/workspaces/current/transform-state")
    def transform_state():
        manifest = _scene_manifest(session)
        return {
            "revision": session.revision,
            "rootTransform": manifest.get("rootTransform"),
            "history": manifest.get("history"),
        }

    @app.post("/api/workspaces/current/transforms/commit")
    def commit_transform(request: dict[str, Any] = required_body):
        target_type, entity_id = request.get("targetType"), request.get("entityId")
        if request.get("expectedRevision") != session.revision:
            raise HTTPException(409, f"Workspace revision changed to {session.revision}")
        if not isinstance(target_type, str) or not isinstance(entity_id, str):
            raise HTTPException(422, "targetType and entityId are required")
        try:
            before = _target_state(session, target_type, entity_id)
            _apply_target_state(session, target_type, entity_id, request.get("transform", {}))
            after = _target_state(session, target_type, entity_id)
        except KeyError as exc:
            raise HTTPException(404, str(exc)) from exc
        except (ValueError, IndexError) as exc:
            raise HTTPException(422, str(exc)) from exc
        session.transform_history[session.history_cursor :] = []
        session.transform_history.append(
            {"targetType": target_type, "entityId": entity_id, "before": before, "after": after}
        )
        session.history_cursor += 1
        session.revision += 1
        return {"scene": _scene_manifest(session), "transform": after}

    def move_history(direction: int):
        if direction < 0:
            if session.history_cursor == 0:
                raise HTTPException(409, "Nothing to undo")
            session.history_cursor -= 1
            edit = session.transform_history[session.history_cursor]
            state = edit["before"]
        else:
            if session.history_cursor >= len(session.transform_history):
                raise HTTPException(409, "Nothing to redo")
            edit = session.transform_history[session.history_cursor]
            session.history_cursor += 1
            state = edit["after"]
        if edit.get("action") == "joint_state_batch":
            session.joint_values.update(state)
        else:
            _apply_target_state(session, edit["targetType"], edit["entityId"], state)
        session.revision += 1
        return _scene_manifest(session)

    @app.post("/api/workspaces/current/history/undo")
    def undo_transform():
        return move_history(-1)

    @app.post("/api/workspaces/current/history/redo")
    def redo_transform():
        return move_history(1)

    @app.post("/api/workspaces/current/save")
    def save_workspace(request: dict[str, Any] = required_body):
        import yaml

        value = request.get("path")
        if not isinstance(value, str) or not value:
            raise HTTPException(422, "path is required")
        destination = Path(value).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "version": 1,
            "source": session.source.as_posix() if session.source else None,
            "revision": session.revision,
            "root_transform": _transform_dict(session.root_transform),
            "joint_values": dict(session.joint_values),
            "transform_edits": session.transform_history[: session.history_cursor],
            "settings": request.get("settings", {}),
        }
        destination.write_text(
            yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        return {"ok": True, "path": destination.as_posix()}

    @app.post("/api/workspaces/current/new")
    def new_workspace():
        session.clear()
        return _scene_manifest(session)

    @app.post("/api/workspaces/open")
    def open_workspace(request: dict[str, Any] = required_body):
        import yaml

        value = request.get("path")
        if not isinstance(value, str) or not value:
            raise HTTPException(422, "path is required")
        workspace = Path(value).expanduser().resolve()
        try:
            document = yaml.safe_load(workspace.read_text(encoding="utf-8")) or {}
            source = Path(document["source"]).expanduser().resolve()
            model = _load_model(source, None, {}, {})
            session.clear()
            session.model, session.source = model, source
            root, _ = _parse_transform(document.get("root_transform", {}))
            session.root_transform = root
            for name, value in document.get("joint_values", {}).items():
                if name in model.joints and math.isfinite(float(value)):
                    session.joint_values[name] = float(value)
            for edit in document.get("transform_edits", []):
                if edit.get("action") == "joint_state_batch":
                    session.joint_values.update(edit["after"])
                else:
                    _apply_target_state(
                        session, edit["targetType"], edit["entityId"], edit["after"]
                    )
                session.transform_history.append(edit)
            session.history_cursor = len(session.transform_history)
            session.revision = int(document.get("revision", session.history_cursor))
        except Exception as exc:
            LOGGER.exception("Workspace load failed")
            raise HTTPException(400, str(exc)) from exc
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

    @app.post("/api/workspaces/current/joint-states/commit")
    def commit_joint_states(request: dict[str, Any] = required_body):
        if session.model is None:
            raise HTTPException(409, "No model is loaded")
        if request.get("expectedRevision") != session.revision:
            raise HTTPException(409, f"Workspace revision changed to {session.revision}")
        values = request.get("values")
        if not isinstance(values, dict) or not values:
            raise HTTPException(422, "values must be a non-empty object")
        normalized: dict[str, float] = {}
        for name, raw in values.items():
            joint = session.model.joints.get(name)
            if joint is None:
                raise HTTPException(404, f"Joint not found: {name}")
            if joint.joint_type == "fixed":
                raise HTTPException(422, f"Fixed joint cannot move: {name}")
            try:
                value = float(raw)
            except (TypeError, ValueError) as exc:
                raise HTTPException(422, f"Joint value must be numeric: {name}") from exc
            if not math.isfinite(value):
                raise HTTPException(422, f"Joint value must be finite: {name}")
            lower = float(joint.limit.get("lower", -math.inf))
            upper = float(joint.limit.get("upper", math.inf))
            if not lower <= value <= upper:
                raise HTTPException(422, f"Joint {name} must be between {lower} and {upper}")
            normalized[name] = value
        before = {name: session.joint_values.get(name, 0.0) for name in normalized}
        session.joint_values.update(normalized)
        session.changes.append(
            {"action": "joint_state_batch", "before": before, "after": normalized}
        )
        session.transform_history[session.history_cursor :] = []
        session.transform_history.append(
            {"action": "joint_state_batch", "before": before, "after": normalized}
        )
        session.history_cursor += 1
        session.revision += 1
        LOGGER.info("Committed %d joint state(s)", len(normalized))
        return {
            "values": normalized,
            "revision": session.revision,
            "saved": False,
            "validation": "lightweight",
        }

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
        session.assembly_joints.add(request["name"])
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
                output.write_text(
                    json.dumps(generate_morphology(session.model), indent=2), encoding="utf-8"
                )
                result = output
            elif export_format in {"package", "package_zip"}:
                base = session.source.parent if session.source.is_file() else session.source
                exporter = PortablePackageExporter()
                resolver = ResourceResolver(base, package_map=session.package_map)
                result = (
                    exporter.export_zip(session.model, output, resolver)
                    if export_format == "package_zip"
                    else exporter.export(session.model, output, resolver)
                )
            else:
                raise ValueError("format must be urdf, mjcf, morphology, package, or package_zip")
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
