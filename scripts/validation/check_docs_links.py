"""Validate local Markdown links without requiring network access."""

from __future__ import annotations

import re
import sys
from pathlib import Path

LINK = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    files = [root / "README.md", root / "README.zh-CN.md", *sorted((root / "docs").rglob("*.md"))]
    for document in files:
        if not document.exists():
            errors.append(f"missing document: {document.relative_to(root)}")
            continue
        for target in LINK.findall(document.read_text(encoding="utf-8")):
            target = target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            candidate = (document.parent / target).resolve()
            if not candidate.exists():
                errors.append(f"{document.relative_to(root)} -> {target}")
    return errors


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[2]
    failures = check(project)
    if failures:
        print("\n".join(failures))
        sys.exit(1)
    print("DOC_LINKS_PASS")
