import re
import runpy
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = re.search(
    r'^version\s*=\s*"([^"]+)"',
    (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
    re.MULTILINE,
).group(1)
VERSION_DIR = ROOT / "release" / f"v{VERSION}"


def test_python_packagers_use_versioned_release_directory():
    native = runpy.run_path(ROOT / "scripts" / "build" / "build_native.py")
    prepared = runpy.run_path(ROOT / "scripts" / "build" / "prepare_release.py")
    smoke = runpy.run_path(ROOT / "scripts" / "validation" / "smoke_release.py")

    assert native["RELEASE"] == VERSION_DIR
    assert prepared["RELEASE"] == VERSION_DIR / "MorphologyStudio"
    assert smoke["EXE"] == VERSION_DIR / "MorphologyStudio" / "MorphologyStudio.exe"
    assert prepared["README"].startswith(f"Morphology Studio {VERSION}\n")


def test_onefile_and_ci_publish_from_versioned_directory():
    onefile = (ROOT / "scripts" / "build_onefile.ps1").read_text(encoding="utf-8")
    tester = (ROOT / "scripts" / "test_onefile.ps1").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "build-release.yml").read_text(encoding="utf-8")

    assert '"release/v$version"' in onefile
    assert "release/v$version/MorphologyStudio-$version-windows-x64.exe" in tester
    assert "release/v*/MorphologyStudio-*" in workflow


def test_checksum_manifest_does_not_hash_itself(tmp_path):
    artifact = tmp_path / "package.zip"
    manifest = tmp_path / "SHA256SUMS.txt"
    artifact.write_bytes(b"release")
    manifest.write_text("stale manifest\n", encoding="ascii")

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build" / "generate_checksums.py"),
            tmp_path,
            manifest,
        ],
        check=True,
    )

    contents = manifest.read_text(encoding="ascii")
    assert "package.zip" in contents
    assert "SHA256SUMS.txt" not in contents
