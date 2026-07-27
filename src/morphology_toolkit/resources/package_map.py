from __future__ import annotations

from pathlib import Path
from typing import Dict

import yaml


def load_package_map(path: Path, project_root: Path = None) -> Dict[str, Path]:
    path = Path(path).resolve()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    packages = data.get("packages", {})
    root = Path(project_root).resolve() if project_root else path.parents[1]
    result = {}
    for name, value in packages.items():
        raw = value.get("path") if isinstance(value, dict) else value
        candidate = Path(raw)
        candidate = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
        if name in result:
            raise ValueError(f"Duplicate explicit package mapping: {name}")
        if not candidate.is_dir():
            raise FileNotFoundError(f"Mapped package directory does not exist: {candidate}")
        result[name] = candidate
    return result

