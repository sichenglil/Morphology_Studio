"""Validate the bilingual README layout and required feature coverage."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULES = [
    "Model Import",
    "Model Tree & Viewport",
    "Joint Control",
    "Transform Editing",
    "Assembly",
    "Validation",
    "Export & Packaging",
    "Workspaces",
    "Desktop Application",
]
SECTION_ANCHORS = (
    "overview",
    "features",
    "formats",
    "requirements",
    "quick-start",
    "five-minute-workflow",
    "architecture",
    "repository-structure",
    "roadmap",
)


def check() -> list[str]:
    errors: list[str] = []
    english = (ROOT / "README.md").read_text(encoding="utf-8-sig")
    chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8-sig")
    for name, text in (("README.md", english), ("README.zh-CN.md", chinese)):
        if not text.startswith('<div align="center">'):
            errors.append(f"{name}: centered hero missing")
        if '<h2 align="center">' in text or re.search(r"<h[1-6][^>]*>", text):
            errors.append(f"{name}: section headings must use standard Markdown")
        if "<table" in text:
            errors.append(f"{name}: tables must use native Markdown syntax")
        if re.search(r"[A-Za-z]:\\", text):
            errors.append(f"{name}: local absolute path")
        if re.search(r"\b(TODO|TBD)\b|根据实际", text, re.I):
            errors.append(f"{name}: placeholder text")
    for module in MODULES:
        if module not in english:
            errors.append(f"README.md: missing module {module}")
    for anchor in SECTION_ANCHORS:
        if f'<a id="{anchor}"></a>' not in english:
            errors.append(f"README.md: missing section anchor {anchor}")
    return errors


if __name__ == "__main__":
    failures = check()
    if failures:
        print("\n".join(failures))
        sys.exit(1)
    print("README_FORMAT_PASS")
