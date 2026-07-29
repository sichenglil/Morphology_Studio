"""Normalize PyInstaller output into the supported portable release layout."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dist" / "MorphologyStudio"
RELEASE = ROOT / "release" / "MorphologyStudio"

README = """Morphology Studio 0.1.0

双击 MorphologyStudio.exe 启动。
不要单独移动 EXE；assets、config 和 _internal 必须一起复制。
机器人模型位于 assets\\robot_models\\ur5e_hx5_right。
预览动画位于 assets\\previews\\ur5e_hx5_right。
日志位于 logs\\MorphologyStudio.log。
若 GIF 无法显示，请恢复完整发布目录；程序会依次尝试 PNG 和占位图。
Windows 需要 Microsoft Edge WebView2 Runtime。
"""


def main() -> int:
    if not (SOURCE / "MorphologyStudio.exe").is_file():
        raise FileNotFoundError(SOURCE / "MorphologyStudio.exe")
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    shutil.copytree(SOURCE, RELEASE)
    internal = RELEASE / "_internal"
    for name in ("assets", "config"):
        bundled, external = internal / name, RELEASE / name
        if bundled.exists():
            shutil.move(str(bundled), str(external))
    (RELEASE / "logs").mkdir(exist_ok=True)
    (RELEASE / "README_RUN.txt").write_text(README, encoding="utf-8")
    (RELEASE / "VERSION").write_text("0.1.0\n", encoding="ascii")
    print(RELEASE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
