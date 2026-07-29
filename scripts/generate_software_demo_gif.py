"""Record real Morphology Studio joint operation and encode it as the preview GIF."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ROOT / "artifacts" / "temporary" / "software-demo-frames"
OUTPUT = ROOT / "assets" / "previews" / "ur5e_hx5_right" / "robot.gif"


def capture() -> None:
    environment = os.environ.copy()
    environment["CAPTURE_SOFTWARE_DEMO"] = "1"
    subprocess.run(  # noqa: S603
        [
            "pnpm.cmd",
            "exec",
            "playwright",
            "test",
            "tests/e2e/software_demo_capture.spec.ts",
        ],
        cwd=ROOT / "web" / "frontend",
        env=environment,
        check=True,
    )


def encode() -> None:
    paths = sorted(FRAMES.glob("*.png"))
    if len(paths) < 2:
        raise RuntimeError(f"Not enough captured frames in {FRAMES}")
    images: list[Image.Image] = []
    for path in paths:
        with Image.open(path) as source:
            frame = source.convert("RGB").resize((960, 540), Image.Resampling.LANCZOS)
            images.append(frame.quantize(colors=192, method=Image.Quantize.MEDIANCUT))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        OUTPUT,
        save_all=True,
        append_images=images[1:],
        duration=80,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Generated {OUTPUT} from {len(images)} real application frames")


def main() -> int:
    capture()
    encode()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
