"""Build and package Morphology Studio on the current native operating system."""

from __future__ import annotations

import hashlib
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "build" / "native-dist"
WORK = ROOT / "build" / "native-work"
VERSION = re.search(
    r'^version\s*=\s*"([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.MULTILINE
).group(1)
RELEASE = ROOT / "release" / f"v{VERSION}"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def architecture() -> str:
    machine = platform.machine().lower()
    if machine in {"arm64", "aarch64"}:
        return "arm64"
    return "x86_64" if sys.platform.startswith("linux") else "x64"


def add_tree_to_zip(archive: zipfile.ZipFile, source: Path, prefix: str) -> None:
    for path in source.rglob("*"):
        if path.is_file():
            archive.write(path, Path(prefix) / path.relative_to(source))


def main() -> int:
    RELEASE.mkdir(parents=True, exist_ok=True)
    system = (
        "windows" if sys.platform == "win32" else "macos" if sys.platform == "darwin" else "linux"
    )
    arch = architecture()
    if sys.platform == "win32":
        spec = ROOT / "scripts" / "build" / "packaging" / "MorphologyStudio.onefile.spec"
    else:
        spec = ROOT / "scripts" / "build" / "packaging" / "MorphologyStudio.spec"
    run(
        sys.executable,
        "-m",
        "PyInstaller",
        str(spec),
        "--noconfirm",
        "--clean",
        "--distpath",
        str(DIST),
        "--workpath",
        str(WORK),
    )
    stem = f"MorphologyStudio-{VERSION}-{system}-{arch}"
    if sys.platform == "win32":
        artifact = RELEASE / f"{stem}.exe"
        shutil.copy2(DIST / "MorphologyStudio.exe", artifact)
    elif sys.platform == "darwin":
        app = DIST / "MorphologyStudio.app"
        artifact = RELEASE / f"{stem}-unsigned.zip"
        with zipfile.ZipFile(artifact, "w", zipfile.ZIP_DEFLATED) as archive:
            add_tree_to_zip(archive, app, app.name)
    else:
        directory = DIST / "MorphologyStudio"
        executable = directory / "MorphologyStudio"
        executable.chmod(executable.stat().st_mode | 0o111)
        artifact = RELEASE / f"{stem}.tar.gz"
        with tarfile.open(artifact, "w:gz") as archive:
            archive.add(directory, arcname="MorphologyStudio")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    checksum = artifact.with_name(f"{artifact.name}.sha256")
    checksum.write_text(f"{digest}  {artifact.name}\n", encoding="ascii")
    print(f"NATIVE_BUILD_OK {artifact} {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
