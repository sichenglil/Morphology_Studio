# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

root = Path(SPECPATH).parents[2]
mode = os.environ.get("MORPHOLOGY_BUILD_MODE", "release").lower()
datas = [
    (str(root / "src" / "morphology_toolkit" / "static" / "frontend"), "morphology_toolkit/static/frontend"),
    (str(root / "assets" / "robot_models" / "ur5e_hx5_right"), "assets/robot_models/ur5e_hx5_right"),
    (str(root / "assets" / "previews" / "ur5e_hx5_right"), "assets/previews/ur5e_hx5_right"),
    (str(root / "assets" / "placeholders"), "assets/placeholders"),
    (str(root / "config"), "config"),
    (str(root / "project" / "THIRD_PARTY_NOTICES.md"), "licenses"),
    (str(root / "LICENSES" / "LGPL-2.1-only.txt"), "licenses"),
    (str(root / "LICENSES" / "MIT.txt"), "licenses"),
]
binaries = []
hiddenimports = ["morphology_toolkit.webapp", "webview.platforms.edgechromium"]
for package in ("xacro", "fastapi", "uvicorn", "webview"):
    package_datas, package_binaries, package_hidden = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hidden

a = Analysis(
    [str(root / "project" / "desktop_entry.py")], pathex=[str(root / "src")], binaries=binaries,
    datas=datas, hiddenimports=hiddenimports,
    excludes=["PIL", "numpy", "trimesh", "collada", "pytest", "ruff", "IPython", "notebook"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="MorphologyStudio", console=mode == "debug")
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="MorphologyStudio")
