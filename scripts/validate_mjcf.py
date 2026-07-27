from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.etree import ElementTree as ET


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    root = ET.parse(args.input).getroot()
    bodies = root.findall(".//body"); joints = root.findall(".//joint"); meshes = root.findall("./asset/mesh")
    missing = []
    for mesh in meshes:
        uri = mesh.get("file", "")
        if uri.startswith("package://") or not (args.input.parent / uri).resolve().exists(): missing.append(uri)
    result = {"xml_valid": root.tag == "mujoco", "bodies": len(bodies), "joints": len(joints), "meshes": len(meshes), "missing_meshes": missing, "root_bodies": len(root.findall("./worldbody/body")), "mujoco_runtime": "MUJOCO_RUNTIME_NOT_INSTALLED"}
    try:
        import mujoco
        mujoco.MjModel.from_xml_path(str(args.input.resolve())); result["mujoco_runtime"] = "PASS"
    except ImportError: pass
    except Exception as exc: result["mujoco_runtime"] = f"FAIL: {exc}"
    args.json.parent.mkdir(parents=True, exist_ok=True); args.json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    args.markdown.write_text("# MJCF conversion validation\n\n" + "\n".join(f"- {key}: `{value}`" for key, value in result.items()) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0 if result["xml_valid"] and result["root_bodies"] == 1 and not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
