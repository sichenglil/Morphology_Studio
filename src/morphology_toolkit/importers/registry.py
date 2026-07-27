from __future__ import annotations

from pathlib import Path
from typing import Dict, Type
from xml.etree import ElementTree as ET

from .base import Importer


def detect_format(path: Path) -> str:
    path = Path(path)
    if path.is_dir():
        if (path / "package.xml").exists():
            return "ros_package"
        return "directory"
    head = path.read_bytes()[:4096]
    text = head.decode("utf-8", errors="ignore")
    upper = text.upper()
    if "ISO-10303-21" in upper or path.suffix.lower() in {".step", ".stp"}:
        return "step"
    if "xmlns:xacro" in text or "<xacro:" in text:
        return "xacro"
    try:
        root = ET.fromstring(text if len(head) < 4096 else path.read_text(encoding="utf-8"))
        tag = root.tag.rsplit("}", 1)[-1]
        if tag == "robot":
            return "urdf"
        if tag == "mujoco":
            return "mjcf"
    except (ET.ParseError, UnicodeDecodeError):
        pass
    if path.suffix.lower() in {".stl", ".obj", ".dae", ".ply", ".glb", ".gltf"}:
        return "mesh"
    return "unknown"


class ImporterRegistry:
    def __init__(self) -> None:
        self._importers: Dict[str, Type[Importer]] = {}

    def register(self, format_name: str, importer: Type[Importer]) -> None:
        self._importers[format_name] = importer

    def create(self, format_name: str) -> Importer:
        if format_name not in self._importers:
            raise ValueError(f"No importer registered for {format_name!r}")
        return self._importers[format_name]()

