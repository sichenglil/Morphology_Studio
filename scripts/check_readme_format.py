"""Validate the bilingual README layout and required feature coverage."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
    "gallery",
    "architecture",
    "repository-structure",
    "roadmap",
)
CONTENTS_ANCHORS = (
    "overview",
    "features",
    "formats",
    "requirements",
    "quick-start",
    "gallery",
    "architecture",
    "roadmap",
)


def check() -> list[str]:
    errors: list[str] = []
    english = (ROOT / "README.md").read_text(encoding="utf-8")
    chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    for name, text in (("README.md", english), ("README.zh-CN.md", chinese)):
        if not text.startswith('<div align="center">'):
            errors.append(f"{name}: centered hero missing")
        if text.count('<h2 align="center">') < 9:
            errors.append(f"{name}: centered section headings missing")
        if '<table align="center">' not in text or '<th align="center">' not in text:
            errors.append(f"{name}: centered table markup missing")
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
    for anchor in CONTENTS_ANCHORS:
        if f'href="#{anchor}"' not in english:
            errors.append(f"README.md: missing contents link {anchor}")
    return errors


if __name__ == "__main__":
    failures = check()
    if failures:
        print("\n".join(failures))
        sys.exit(1)
    print("README_FORMAT_PASS")
