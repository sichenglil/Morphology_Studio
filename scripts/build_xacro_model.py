from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from morphology_toolkit.core.model import ProcessingMode
from morphology_toolkit.importers import UrdfImporter, XacroImporter
from morphology_toolkit.morphology import generate_morphology
from morphology_toolkit.resources import PackageResolver, ResourceResolver, load_package_map
from morphology_toolkit.validation import validate_model


def main() -> int:
    parser = argparse.ArgumentParser(description="Build any configured Xacro model without requiring ROS")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--validation-json", type=Path, required=True)
    parser.add_argument("--validation-md", type=Path, required=True)
    parser.add_argument("--morphology", type=Path)
    args = parser.parse_args()
    project = Path.cwd().resolve()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    source = (project / config["source"]).resolve()
    package_map = load_package_map(project / config["package_map"], project)
    resolver = PackageResolver(package_map, mode=ProcessingMode(config.get("mode", "assisted")))
    expansion = XacroImporter().expand(source, {key: str(value).lower() if isinstance(value, bool) else str(value) for key, value in config.get("arguments", {}).items()}, resolver)
    trace = {"source": source.relative_to(project).as_posix(), "method": expansion.method, "returncode": expansion.returncode, "stderr": expansion.stderr, "packages": expansion.package_resolutions, "arguments": config.get("arguments", {})}
    args.trace.parent.mkdir(parents=True, exist_ok=True)
    args.trace.write_text(json.dumps(trace, indent=2), encoding="utf-8")
    if expansion.returncode:
        raise SystemExit(f"Xacro failed: {expansion.stderr}")
    forbidden = [token for token in ("$(find ", "${", "<xacro:") if token in expansion.xml]
    if forbidden: raise SystemExit(f"Generated XML contains unresolved tokens: {forbidden}")
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(expansion.xml, encoding="utf-8")
    model = UrdfImporter().execute(args.output)
    resources = ResourceResolver(args.output.parent, package_map=package_map)
    report = validate_model(model, resources); report.write(args.validation_json, args.validation_md)
    if args.morphology:
        args.morphology.parent.mkdir(parents=True, exist_ok=True)
        args.morphology.write_text(json.dumps(generate_morphology(model), indent=2), encoding="utf-8")
    print(json.dumps({"output": args.output.as_posix(), "links": len(model.links), "joints": len(model.joints), "roots": model.root_links, "errors": report.errors, "warnings": report.warnings}))
    return 0 if report.export_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
