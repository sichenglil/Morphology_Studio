from __future__ import annotations

import json
import subprocess
from pathlib import Path


def launch_usd_conversion(input_path: Path, output: Path, isaac_python: Path = None) -> Path:
    runner = Path(__file__).resolve().parents[3] / "scripts" / "isaac_urdf_to_usd.py"
    python = Path(isaac_python) if isaac_python else _discover_isaac_python()
    if python is None:
        raise RuntimeError(
            "Isaac Sim Python was not found. Pass --isaac-python pointing to python.bat/python.sh."
        )
    command = [
        str(python),
        str(runner),
        "--input",
        str(Path(input_path).resolve()),
        "--output",
        str(Path(output).resolve()),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    log = Path(output).with_suffix(".import.json")
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(
        json.dumps(
            {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    if result.returncode:
        raise RuntimeError(f"Isaac import failed; see {log}")
    return Path(output)


def _discover_isaac_python():
    for root in (Path.home() / "AppData/Local/ov/pkg", Path("C:/isaacsim"), Path("C:/IsaacSim")):
        if root.exists():
            for name in ("python.bat", "python.sh"):
                candidates = list(root.rglob(name))
                if candidates:
                    return candidates[0]
    return None
