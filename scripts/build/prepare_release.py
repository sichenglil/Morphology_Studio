"""Normalize PyInstaller output into the supported portable release layout."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "dist" / "MorphologyStudio"
VERSION = re.search(
    r'^version\s*=\s*"([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.MULTILINE
).group(1)
RELEASE = ROOT / "release" / f"v{VERSION}" / "MorphologyStudio"

README = f"""Morphology Studio {VERSION}

双击 MorphologyStudio.exe 启动。
请勿单独移动 EXE；_internal、assets 和 config 必须与 EXE 一起复制。
EXE 已内置 OpenCascade WebAssembly，可直接选择 STEP/STP，无需安装 step2urdf、Node.js 或 pnpm。
首次解析 STEP 会加载约 50 MB 的本地 WASM，属于正常现象，不需要联网。
生成的 STEP 网格缓存位于 %LOCALAPPDATA%\\MorphologyStudio\\step_imports。
日志位于 logs\\MorphologyStudio.log。
第三方许可证位于 _internal\\licenses。
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
    (RELEASE / "VERSION").write_text(f"{VERSION}\n", encoding="ascii")
    print(RELEASE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
