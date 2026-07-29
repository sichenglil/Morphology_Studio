"""Fail on common repository hygiene and accidental disclosure problems."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "README.zh-CN.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "THIRD_PARTY_NOTICES.md",
    "mkdocs.yml",
]
ROOT_ALLOWLIST = {
    ".github",
    ".reuse",
    "LICENSES",
    "configs",
    "docs",
    "examples",
    "packaging",
    "scripts",
    "src",
    "tests",
    "web",
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "CHANGELOG.md",
    "CITATION.cff",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "LICENSE",
    "README.md",
    "README.zh-CN.md",
    "SECURITY.md",
    "SUPPORT.md",
    "THIRD_PARTY_NOTICES.md",
    "desktop_entry.py",
    "mkdocs.yml",
    "pnpm-workspace.yaml",
    "pyproject.toml",
}
SENSITIVE = re.compile(
    r"(^|/)(\.env($|\.)|id_rsa$|id_ed25519$|credentials|secrets|token|service-account)|\.(pem|key|pfx|p12)$",
    re.I,
)
ABSOLUTE = re.compile(r"(?:^|[\s'\"`(])([A-Za-z]:[\\/])")


def tracked() -> list[str]:
    return subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()


def main() -> int:
    errors = [f"missing: {name}" for name in REQUIRED if not (ROOT / name).exists()]
    names = tracked()
    tracked_root = {
        name.replace("\\", "/").split("/", 1)[0] for name in names if (ROOT / name).exists()
    }
    errors.extend(
        f"root item not allowlisted: {name}" for name in sorted(tracked_root - ROOT_ALLOWLIST)
    )
    for name in names:
        portable = name.replace("\\", "/")
        path = ROOT / name
        if not path.exists():
            continue
        if SENSITIVE.search(portable):
            errors.append(f"sensitive filename: {portable}")
        if portable.startswith(
            ("models/", "workspace/", "generated/", "build/", "dist/", "web/frontend/node_modules/")
        ):
            errors.append(f"generated or user data tracked: {portable}")
        if path.is_file() and path.stat().st_size > 5 * 1024 * 1024:
            errors.append(f"large file: {portable}")
        if path.suffix.lower() in {".py", ".ts", ".vue", ".md", ".yaml", ".yml", ".json"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            absolute_allowlist = {
                "scripts/check_repository_health.py",
                "docs/audits/project_structure_audit.md",
                "src/morphology_toolkit/exporters/usd_exporter.py",
                "src/morphology_toolkit/reports/audit.py",
                "web/frontend/src/components/dialogs/ExportDialog.vue",
            }
            if ABSOLUTE.search(text) and portable not in absolute_allowlist:
                errors.append(f"local absolute path: {portable}")
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for item in ("build/", "dist/", "workspace/", "node_modules/"):
        if item not in ignore:
            errors.append(f"missing ignore rule: {item}")
    if errors:
        print("\n".join(sorted(set(errors))))
        return 1
    print("REPOSITORY_HEALTH_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
