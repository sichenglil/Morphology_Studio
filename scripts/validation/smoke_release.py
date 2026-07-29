"""Start the packaged EXE from an unrelated directory and probe bundled resources."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
EXE = ROOT / "release" / "MorphologyStudio" / "MorphologyStudio.exe"
WORKING_DIRECTORY = ROOT / "artifacts" / "temporary" / "中文 启动目录"
PORT = 48765


def fetch(path: str) -> bytes:
    with urlopen(f"http://127.0.0.1:{PORT}{path}", timeout=2) as response:  # noqa: S310
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {path}")
        return response.read()


def main() -> int:
    WORKING_DIRECTORY.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["MORPHOLOGY_PORT"] = str(PORT)
    process = subprocess.Popen([EXE], cwd=WORKING_DIRECTORY, env=environment)  # noqa: S603
    try:
        for _ in range(60):
            try:
                health = json.loads(fetch("/api/health"))
                break
            except OSError:
                time.sleep(0.25)
        else:
            raise RuntimeError("EXE API did not become healthy")
        registry = json.loads(fetch("/api/model-registry"))
        gif = fetch("/app-assets/previews/ur5e_hx5_right/robot.gif")
        model = registry["models"][0]
        print(json.dumps({
            "health": health,
            "model_count": len(registry["models"]),
            "model_id": model["id"],
            "available": model["available"],
            "gif_bytes": len(gif),
            "working_directory": str(WORKING_DIRECTORY),
        }, ensure_ascii=False, indent=2))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
