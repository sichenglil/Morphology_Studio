from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch an isolated local step2urdf checkout")
    parser.add_argument("--path", type=Path, default=Path("external/step2urdf"))
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    root = args.path.resolve()
    if not (root / "package.json").exists():
        raise SystemExit(
            f"step2urdf is not installed at {root}. Clone the MIT project there first; see docs/step_workflow.md"
        )
    if args.install:
        subprocess.run(["pnpm", "install"], cwd=root, check=True)
    return subprocess.run(["pnpm", "dev"], cwd=root, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
