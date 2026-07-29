from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import unquote, urlparse


@dataclass
class ResourceResolver:
    source_root: Path
    search_paths: List[Path] = field(default_factory=list)
    package_map: Dict[str, Path] = field(default_factory=dict)

    def resolve(self, uri: str) -> Optional[Path]:
        normalized = uri.replace("\\", "/")
        if normalized.startswith("package://"):
            remainder = normalized[len("package://") :]
            package, _, relative = remainder.partition("/")
            roots = []
            if package in self.package_map:
                roots.append(self.package_map[package])
            for search in self.search_paths:
                roots.extend([search / package, search])
            return self._first(roots, relative)
        if normalized.startswith("file://"):
            return Path(unquote(urlparse(normalized).path)).resolve()
        if normalized.startswith(("http://", "https://")):
            return None
        path = Path(normalized)
        if path.is_absolute():
            return path
        return self._first([self.source_root, *self.search_paths], normalized)

    @staticmethod
    def _first(roots: List[Path], relative: str) -> Optional[Path]:
        for root in roots:
            candidate = (Path(root) / relative).resolve()
            if candidate.exists():
                return candidate
        return None

    @staticmethod
    def portable_uri(path: Path, output_root: Path) -> str:
        return path.resolve().relative_to(output_root.resolve()).as_posix()
