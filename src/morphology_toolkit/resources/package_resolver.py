from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from xml.etree import ElementTree as ET

from morphology_toolkit.core.model import ProcessingMode


@dataclass
class ResolutionCandidate:
    package: str
    path: Path
    source: str
    priority: int


@dataclass
class ResolutionTrace:
    package: str
    searched: List[str] = field(default_factory=list)
    candidates: List[ResolutionCandidate] = field(default_factory=list)
    selected: Optional[Path] = None
    error: Optional[str] = None


class PackageResolver:
    def __init__(
        self,
        explicit_map: Dict[str, Path] = None,
        roots: Iterable[Path] = (),
        mode: ProcessingMode = ProcessingMode.ASSISTED,
    ):
        self.explicit_map = {
            name: Path(path).resolve() for name, path in (explicit_map or {}).items()
        }
        self.roots = [Path(path).resolve() for path in roots]
        self.mode = mode
        self._traces: Dict[str, ResolutionTrace] = {}

    @staticmethod
    def package_name(directory: Path) -> Optional[str]:
        manifest = Path(directory) / "package.xml"
        if not manifest.exists():
            return None
        try:
            return ET.parse(manifest).getroot().findtext("name")
        except ET.ParseError:
            return None

    def discover(self, roots: Iterable[Path] = None) -> Dict[str, List[Path]]:
        found: Dict[str, List[Path]] = {}
        for root in roots or self.roots:
            root = Path(root).resolve()
            manifests = (
                [root / "package.xml"]
                if (root / "package.xml").exists()
                else root.rglob("package.xml")
                if root.exists()
                else []
            )
            for manifest in manifests:
                name = self.package_name(manifest.parent)
                if name:
                    found.setdefault(name, []).append(manifest.parent.resolve())
        return found

    def resolve(self, package_name: str) -> Optional[Path]:
        trace = ResolutionTrace(package_name)
        if package_name in self.explicit_map:
            path = self.explicit_map[package_name]
            trace.searched.append("explicit package map")
            trace.candidates.append(ResolutionCandidate(package_name, path, "explicit_map", 1))
            trace.selected = path
            self._traces[package_name] = trace
            return path
        discovered = self.discover()
        trace.searched.extend(path.as_posix() for path in self.roots)
        paths = list(dict.fromkeys(discovered.get(package_name, [])))
        trace.candidates.extend(
            ResolutionCandidate(package_name, path, "package_root", 2) for path in paths
        )
        if len(paths) == 1:
            trace.selected = paths[0]
        elif len(paths) > 1:
            trace.error = f"Ambiguous package {package_name!r}: {paths}"
            if self.mode == ProcessingMode.MANUAL:
                trace.selected = paths[0]
        else:
            trace.error = f"Package {package_name!r} not found"
        self._traces[package_name] = trace
        return trace.selected

    def require(self, package_name: str) -> Path:
        result = self.resolve(package_name)
        if result is None:
            raise LookupError(self.explain(package_name).error)
        return result

    def explain(self, package_name: str) -> ResolutionTrace:
        if package_name not in self._traces:
            self.resolve(package_name)
        return self._traces[package_name]
