from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from morphology_toolkit.importers import DirectoryImporter


def _version(command):
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=10).stdout.strip() or subprocess.run(command, capture_output=True, text=True, timeout=10).stderr.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        return None


def audit_repository(root: Path) -> Dict[str, Any]:
    root = Path(root).resolve()
    models = root / "models"
    report = {
        "platform": platform.platform(),
        "python": sys.version,
        "node": _version(["node", "--version"]),
        "pnpm": _version(["pnpm", "--version"]),
        "git": _version(["git", "--version"]),
        "xacro": shutil.which("xacro"),
        "ros_distro": os.environ.get("ROS_DISTRO"),
        "isaac_sim_candidates": [],
        "isaac_lab_candidates": [],
        "model_candidates": [],
    }
    if models.exists():
        analysis = DirectoryImporter().analyze(models)
        report["model_candidates"] = [{"path": item.path.relative_to(root).as_posix(), "format": item.detected_format, "score": item.score, "confidence": item.confidence, "reason": item.reason} for item in analysis.entry_candidates]
    for candidate in (Path.home() / "AppData/Local/ov/pkg", Path("C:/isaacsim"), Path("C:/IsaacSim")):
        if candidate.exists(): report["isaac_sim_candidates"].append(candidate.as_posix())
    destination = root / "build" / "reports"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "environment_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    inventory = {"candidates": report["model_candidates"], "count": len(report["model_candidates"])}
    (destination / "model_inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    docs = root / "docs"; docs.mkdir(exist_ok=True)
    lines = ["# Model and environment audit", "", f"- Platform: `{report['platform']}`", f"- Python: `{platform.python_version()}`", f"- ROS distro: `{report['ros_distro'] or 'not active'}`", f"- Xacro executable: `{report['xacro'] or 'not found'}`", f"- Entry candidates: {len(report['model_candidates'])}", "", "## Candidate entries", ""]
    lines.extend(f"- `{item['path']}` — {item['format']}, {item['confidence']} ({item['score']:.2f})" for item in report["model_candidates"])
    (docs / "model_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report

