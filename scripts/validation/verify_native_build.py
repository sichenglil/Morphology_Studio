"""Run the packaged application's non-GUI installation verification mode."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "build" / "native-dist"


def main() -> int:
    if sys.platform == "win32":
        executable = DIST / "MorphologyStudio.exe"
    elif sys.platform == "darwin":
        executable = DIST / "MorphologyStudio.app" / "Contents" / "MacOS" / "MorphologyStudio"
    else:
        executable = DIST / "MorphologyStudio" / "MorphologyStudio"
    if not executable.is_file():
        raise FileNotFoundError(executable)
    env = os.environ.copy()
    env["MORPHOLOGY_VERIFY_INSTALLATION"] = "1"
    completed = subprocess.run(
        [str(executable)], env=env, cwd=Path.home(), text=True, capture_output=True, timeout=90
    )
    if completed.returncode:
        raise RuntimeError(
            f"Packaged verification failed ({completed.returncode}): {completed.stderr}"
        )
    if "INSTALLATION_OK" not in completed.stdout:
        raise RuntimeError(f"Packaged verification marker missing: {completed.stdout!r}")
    print("NATIVE_VERIFY_OK", platform.system(), platform.machine(), executable)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
