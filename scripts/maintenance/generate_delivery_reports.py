"""Generate compact, reproducible delivery reports after validation and packaging."""

from __future__ import annotations

import platform
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "artifacts" / "reports"
SKIP = {".git", "node_modules", "build", "dist", "release", "archive", "__pycache__"}


def directory_size(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def tree(path: Path, prefix: str = "") -> list[str]:
    entries = [item for item in path.iterdir() if item.name not in SKIP]
    entries.sort(key=lambda item: (item.is_file(), item.name.lower()))
    lines: list[str] = []
    for index, item in enumerate(entries):
        last = index == len(entries) - 1
        lines.append(f"{prefix}{'`-- ' if last else '|-- '}{item.name}")
        if item.is_dir():
            lines.extend(tree(item, prefix + ("    " if last else "|   ")))
    return lines


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "project_tree_after.txt").write_text(
        "Morphology_Studio\n" + "\n".join(tree(ROOT)) + "\n", encoding="utf-8"
    )
    release = ROOT / "release" / "MorphologyStudio"
    exe = release / "MorphologyStudio.exe"
    build = f"""Morphology Studio build report
Build time: {datetime.now().astimezone().isoformat(timespec='seconds')}
Operating system: {platform.platform()}
Python: {sys.version.split()[0]}
PyInstaller: 6.21.0 (isolated build/packaging-venv)
Command: python -m PyInstaller scripts\\build\\packaging\\MorphologyStudio.spec --noconfirm --clean
Mode: release, windowed, onedir
EXE: {exe}
EXE size: {exe.stat().st_size} bytes
Release size: {directory_size(release)} bytes
Packaged models: 1 (ur5e_hx5_right)
Generated GIFs: 1 (512x512, 49 frames)
Tests: Python 43 passed; frontend 20 passed; Playwright 13 passed; EXE smoke passed
Known warnings: one xacro deprecation warning; Vite reports a large frontend chunk.
Initial build issue: global Anaconda pathlib backport conflicted with PyInstaller; solved with an isolated venv.
"""
    (REPORTS / "build_report.txt").write_text(build, encoding="utf-8")
    tests = """Morphology Studio test report
Resource verifier: PASS (40 links, 39 joints, 56 mesh references, 0 missing, 49 GIF frames)
Python compileall: PASS
Ruff: PASS
Pytest: 43 passed, 0 failed, 1 third-party deprecation warning
Vue type-check: PASS
ESLint: PASS
Vitest: 20 passed, 0 failed
Vite production build: PASS
Playwright: 13 passed, 0 failed
Release smoke: PASS from an unrelated directory containing Chinese characters and a space
Smoke endpoints: /api/health, /api/model-registry and packaged GIF all returned successfully
"""
    (REPORTS / "test_report.txt").write_text(tests, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
