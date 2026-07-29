"""Read and validate the packaged robot preview registry."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

from morphology_toolkit.paths import resource_root

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class RobotModelEntry:
    id: str
    name: str
    urdf: str
    preview_gif: str
    preview_png: str
    enabled: bool = True
    primary: bool = False

    def urdf_path(self, root: Path) -> Path:
        return root / Path(self.urdf)

    def gif_path(self, root: Path) -> Path:
        return root / Path(self.preview_gif)

    def png_path(self, root: Path) -> Path:
        return root / Path(self.preview_png)

    def public_dict(self, root: Path) -> dict:
        value = asdict(self)
        value.update(
            {
                "available": self.urdf_path(root).is_file(),
                "preview_available": self.gif_path(root).is_file(),
                "preview_url": "/app-assets/"
                + Path(self.preview_gif).relative_to("assets").as_posix(),
                "preview_png_url": "/app-assets/"
                + Path(self.preview_png).relative_to("assets").as_posix(),
            }
        )
        return value


def load_registry(root: Path | None = None) -> list[RobotModelEntry]:
    base = root or resource_root()
    path = base / "config" / "robot_models.json"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        LOGGER.exception("Unable to read robot model registry: %s", path)
        return []
    entries: list[RobotModelEntry] = []
    for item in document.get("models", []):
        try:
            entry = RobotModelEntry(**item)
            if entry.enabled and entry.urdf_path(base).is_file():
                entries.append(entry)
        except (TypeError, ValueError, OSError):
            LOGGER.exception("Invalid robot model registry entry")
    return sorted(entries, key=lambda item: (not item.primary, item.name))
