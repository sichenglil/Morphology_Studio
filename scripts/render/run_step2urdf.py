from __future__ import annotations

import argparse
from pathlib import Path

from morphology_toolkit.step import Step2UrdfAdapter


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch an isolated local step2urdf checkout")
    parser.add_argument("--path", type=Path, default=Path("external/step2urdf"))
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    root = args.path.resolve()
    adapter = Step2UrdfAdapter(root)
    if args.install:
        import subprocess

        if not (root / "package.json").is_file():
            raise SystemExit(f"step2urdf package.json not found at {root}")
        subprocess.run(["pnpm", "install"], cwd=root, check=True)
    status = adapter.launch()
    print(status.url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
