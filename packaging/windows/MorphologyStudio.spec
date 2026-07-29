# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

root = Path(SPECPATH).parents[1]
datas = [(str(root / "src" / "morphology_toolkit" / "static" / "frontend"), "morphology_toolkit/static/frontend")]
binaries = []
hiddenimports = ["morphology_toolkit.webapp", "webview.platforms.edgechromium"]
for package in ("xacro", "fastapi", "uvicorn", "webview"):
    package_datas, package_binaries, package_hidden = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hidden

a = Analysis(
    [str(root / "desktop_entry.py")],
    pathex=[str(root / "src")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="MorphologyStudio", console=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True, name="MorphologyStudio")
