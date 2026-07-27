from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from morphology_toolkit.assembly import assemble_models
from morphology_toolkit.core.model import AssemblyConnection, ProcessingMode, Transform
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
from morphology_toolkit.reports import audit_repository
from morphology_toolkit.resources import PackageResolver, ResourceResolver, load_package_map
from morphology_toolkit.validation import validate_model
from morphology_toolkit.workspace import Workspace


def _mode(value: str) -> ProcessingMode:
    return ProcessingMode(value)


def _load(path: Path, mode: ProcessingMode, entry: str = None, arguments=None, package_map=None, package_roots=None):
    fmt = detect_format(path)
    if fmt in {"directory", "ros_package"}:
        selection = {"entry": entry, "arguments": arguments or {}, "package_map": package_map or {}, "package_paths": package_roots or []}
        return DirectoryImporter().execute(path, mode, selection)
    if fmt == "urdf":
        return UrdfImporter().execute(path, mode)
    if fmt == "xacro":
        return XacroImporter().execute(path, mode, {"arguments": arguments or {}, "package_map": package_map or {}, "package_paths": package_roots or []})
    raise ValueError(f"Unsupported input format: {fmt}")


def _analysis(path: Path):
    fmt = detect_format(path)
    if fmt in {"directory", "ros_package"}: return DirectoryImporter().analyze(path)
    if fmt == "urdf": return UrdfImporter().analyze(path)
    if fmt == "xacro": return XacroImporter().analyze(path)
    raise ValueError(f"No analyzer for {fmt}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="morphology-tool")
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit"); audit.add_argument("--root", type=Path, default=Path.cwd())
    workspace = sub.add_parser("workspace"); ws = workspace.add_subparsers(dest="action", required=True)
    for action in ("create", "open"):
        item = ws.add_parser(action); item.add_argument("--path", type=Path, required=True); item.add_argument("--mode", type=_mode, default=ProcessingMode.ASSISTED)
    imp = sub.add_parser("import"); imp.add_argument("--path", type=Path, required=True); imp.add_argument("--mode", type=_mode, default=ProcessingMode.ASSISTED); imp.add_argument("--entry"); imp.add_argument("--workspace", type=Path); imp.add_argument("--package-map", type=Path); imp.add_argument("--package-root", type=Path, action="append", default=[])
    package_map_parser = sub.add_parser("inspect-package-map"); package_map_parser.add_argument("--package-map", type=Path, required=True); package_map_parser.add_argument("--package", action="append", default=[])
    inspect = sub.add_parser("inspect"); inspect.add_argument("--path", type=Path, required=True); inspect.add_argument("--mode", type=_mode, default=ProcessingMode.ASSISTED)
    validate = sub.add_parser("validate"); validate.add_argument("--input", type=Path, required=True); validate.add_argument("--output", type=Path, default=Path("build/reports")); validate.add_argument("--package-map", type=Path)
    morphology = sub.add_parser("morphology"); morphology.add_argument("--input", type=Path, required=True); morphology.add_argument("--output", type=Path, default=Path("build/morphology/morphology.json"))
    assemble = sub.add_parser("assemble"); assemble.add_argument("--config", type=Path, required=True); assemble.add_argument("--mode", type=_mode, default=ProcessingMode.ASSISTED); assemble.add_argument("--output", type=Path); assemble.add_argument("--report-json", type=Path); assemble.add_argument("--report-md", type=Path)
    package = sub.add_parser("package"); package.add_argument("--input", type=Path, required=True); package.add_argument("--output", type=Path, required=True); package.add_argument("--resource-root", type=Path); package.add_argument("--package-map", type=Path)
    convert = sub.add_parser("convert"); convert.add_argument("--input", type=Path, required=True); convert.add_argument("--format", choices=("urdf", "mjcf", "usd"), required=True); convert.add_argument("--output", type=Path, required=True); convert.add_argument("--mode", type=_mode, default=ProcessingMode.ASSISTED); convert.add_argument("--isaac-python", type=Path)
    sub.add_parser("web").add_argument("--port", type=int, default=8000)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "audit":
            print(json.dumps(audit_repository(args.root), indent=2)); return 0
        if args.command == "workspace":
            workspace = Workspace.create(args.path, args.mode) if args.action == "create" else Workspace.open(args.path)
            print(workspace.root); return 0
        if args.command == "inspect-package-map":
            mapping = load_package_map(args.package_map, Path.cwd()); resolver = PackageResolver(mapping)
            names = args.package or sorted(mapping); payload = {}
            for name in names:
                resolved = resolver.resolve(name); trace = resolver.explain(name)
                payload[name] = {"resolved": resolved.as_posix() if resolved else None, "source": trace.candidates[0].source if trace.candidates else None, "error": trace.error}
            print(json.dumps(payload, indent=2)); return 0
        if args.command == "import":
            analysis = _analysis(args.path)
            package_map = load_package_map(args.package_map, Path.cwd()) if args.package_map else {}
            payload = {"detected_format": detect_format(args.path), "entries": [{"path": str(item.path), "format": item.detected_format, "score": item.score, "confidence": item.confidence, "reason": item.reason, "requires_confirmation": item.requires_confirmation} for item in analysis.entry_candidates], "parameters": analysis.parameter_candidates, "diagnostics": analysis.diagnostics}
            if args.entry or detect_format(args.path) not in {"directory", "ros_package"}:
                model = _load(args.path, args.mode, args.entry, package_map=package_map, package_roots=args.package_root); payload["model"] = {"robot_id": model.robot_id, "links": len(model.links), "joints": len(model.joints), "roots": model.root_links}
            if args.workspace:
                ws = Workspace.open(args.workspace); ws.imported_models.append({"source": args.path.as_posix(), "entry": args.entry, "mode": args.mode.value, "package_map": args.package_map.as_posix() if args.package_map else None, "package_roots": [p.as_posix() for p in args.package_root]}); ws.save(); ws.log("model_import", payload)
            print(json.dumps(payload, indent=2)); return 0
        if args.command == "inspect":
            model = _load(args.path, args.mode); print(json.dumps(model.to_dict(), indent=2)); return 0
        if args.command == "validate":
            model = UrdfImporter().execute(args.input); package_map = load_package_map(args.package_map, Path.cwd()) if args.package_map else {}; resolver = ResourceResolver(args.input.parent, package_map=package_map)
            report = validate_model(model, resolver); report.write(args.output / "validation.json", args.output / "validation.md")
            print(json.dumps({"errors": report.errors, "warnings": report.warnings, "export_ready": report.export_ready})); return 0 if report.export_ready else 2
        if args.command == "morphology":
            data = generate_morphology(UrdfImporter().execute(args.input)); args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(data, indent=2), encoding="utf-8"); print(args.output); return 0
        if args.command == "assemble":
            config = yaml.safe_load(args.config.read_text(encoding="utf-8")); models = {}; prefixes = {}
            for spec in config["models"]:
                models[spec["id"]] = _load((args.config.parent / spec["source"]).resolve() if not Path(spec["source"]).is_absolute() else Path(spec["source"]), args.mode, spec.get("entry"), spec.get("arguments")); prefixes[spec["id"]] = spec.get("prefix", "")
            connections = [AssemblyConnection(item["name"], item.get("type", "fixed"), item["parent"]["model"], item["parent"]["link"], item["child"]["model"], item["child"]["link"], Transform(tuple(item.get("origin", {}).get("xyz", (0,0,0))), tuple(item.get("origin", {}).get("rpy", (0,0,0))))) for item in config["connections"]]
            result = assemble_models(models, connections, prefixes, config["assembly"]["name"], args.mode); output = args.output or Path("build/urdf") / f"{result.model.robot_id}.urdf"; UrdfExporter().export(result.model, output)
            report = {"assembly": result.model.robot_id, "models": list(models), "connections": [item.name for item in connections], "roots": result.model.root_links, "links": len(result.model.links), "joints": len(result.model.joints), "source_map": result.source_map, "notes": config.get("notes", [])}
            if args.report_json: args.report_json.parent.mkdir(parents=True, exist_ok=True); args.report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
            if args.report_md: args.report_md.parent.mkdir(parents=True, exist_ok=True); args.report_md.write_text("# Assembly report\n\n" + "\n".join(f"- {key}: `{value}`" for key, value in report.items() if key != "source_map") + "\n", encoding="utf-8")
            print(output); return 0
        if args.command == "package":
            model = UrdfImporter().execute(args.input); root = args.resource_root or args.input.parent; package_map = load_package_map(args.package_map, Path.cwd()) if args.package_map else {}; print(PortablePackageExporter().export(model, args.output, ResourceResolver(root, package_map=package_map))); return 0
        if args.command == "convert":
            if args.format == "usd":
                from morphology_toolkit.exporters.usd_exporter import launch_usd_conversion
                print(launch_usd_conversion(args.input, args.output, args.isaac_python)); return 0
            model = _load(args.input, args.mode)
            output = UrdfExporter().export(model, args.output) if args.format == "urdf" else MjcfExporter().export(model, args.output)
            print(output); return 0
        if args.command == "web":
            from morphology_toolkit.webapp import run
            run(args.port); return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
