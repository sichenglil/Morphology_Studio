"""Validate the single packaged URDF model and its previews."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    config = json.loads((ROOT / "config" / "robot_models.json").read_text(encoding="utf-8"))
    errors, results = [], []
    if len(config.get("models", [])) != 1:
        errors.append("robot_models.json must contain exactly one model")
    for model in config.get("models", []):
        urdf = ROOT / model["urdf"]
        gif = ROOT / model["preview_gif"]
        png = ROOT / model["preview_png"]
        missing, absolute, package = [], [], []
        root = ET.parse(urdf).getroot()
        refs = [node.get("filename", "") for node in root.findall(".//mesh")]
        for reference in refs:
            normalized = reference.replace("\\", "/")
            if normalized.startswith("package://"):
                package.append(reference)
            elif normalized.startswith("file://") or Path(normalized).is_absolute():
                absolute.append(reference)
            elif not (urdf.parent / normalized).is_file():
                missing.append(reference)
        try:
            with Image.open(gif) as image:
                if image.size != (960, 540) or getattr(image, "n_frames", 1) < 40:
                    errors.append(f"Invalid GIF dimensions or frames: {gif}")
                frames = getattr(image, "n_frames", 1)
        except Exception as exc:
            errors.append(f"Invalid GIF {gif}: {exc}")
            frames = 0
        if not png.is_file():
            errors.append(f"Missing PNG: {png}")
        if missing or absolute or package:
            errors.append(
                f"Invalid mesh references: missing={missing}, absolute={absolute}, package={package}"
            )
        results.append(
            {
                "urdf": model["urdf"],
                "robot": root.get("name"),
                "links": len(root.findall("link")),
                "joints": len(root.findall("joint")),
                "mesh_references": len(refs),
                "missing": missing,
                "gif_frames": frames,
            }
        )
    print(json.dumps({"models": results, "errors": errors}, indent=2, ensure_ascii=False))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
