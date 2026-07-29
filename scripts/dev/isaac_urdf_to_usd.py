"""Run inside Isaac Sim's Python environment to import URDF with the official extension."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from isaacsim import SimulationApp

    app = SimulationApp({"headless": True})
    try:
        import omni.kit.commands
        from isaacsim.asset.importer.urdf import _urdf

        config = _urdf.ImportConfig()
        config.fix_base = False
        config.merge_fixed_joints = False
        config.make_default_prim = True
        args.output.parent.mkdir(parents=True, exist_ok=True)
        success, result = omni.kit.commands.execute(
            "URDFParseAndImportFile",
            urdf_path=str(args.input.resolve()),
            import_config=config,
            dest_path=str(args.output.resolve()),
        )
        if not success:
            raise RuntimeError(f"Official URDF importer failed: {result}")
        if not args.output.exists():
            raise RuntimeError("Importer returned success but output USD does not exist")
    finally:
        app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
