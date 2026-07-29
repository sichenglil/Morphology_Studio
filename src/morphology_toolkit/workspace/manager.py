from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml

from morphology_toolkit.core.model import ProcessingMode


@dataclass
class Workspace:
    root: Path
    mode: ProcessingMode = ProcessingMode.ASSISTED
    imported_models: List[Dict[str, Any]] = field(default_factory=list)
    assemblies: List[Dict[str, Any]] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, root: Path, mode: ProcessingMode = ProcessingMode.ASSISTED) -> "Workspace":
        root = Path(root).resolve()
        for folder in (
            "imported_models",
            "assemblies",
            "semantic_annotations",
            "generated",
            "reports",
            "cache",
            "logs",
        ):
            (root / folder).mkdir(parents=True, exist_ok=True)
        workspace = cls(root, mode)
        workspace.save()
        workspace.log("workspace_created", {"mode": mode.value})
        return workspace

    @classmethod
    def open(cls, root: Path) -> "Workspace":
        root = Path(root).resolve()
        data = yaml.safe_load((root / "workspace.yaml").read_text(encoding="utf-8")) or {}
        return cls(
            root,
            ProcessingMode(data.get("mode", "assisted")),
            data.get("imported_models", []),
            data.get("assemblies", []),
            data.get("settings", {}),
        )

    def save(self) -> None:
        payload = {
            "mode": self.mode.value,
            "imported_models": self.imported_models,
            "assemblies": self.assemblies,
            "settings": self.settings,
        }
        (self.root / "workspace.yaml").write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )

    def log(self, event: str, data: Dict[str, Any]) -> None:
        entry = {
            "time": datetime.now(timezone.utc).isoformat(),
            "mode": self.mode.value,
            "event": event,
            **data,
        }
        json_path = self.root / "logs" / "session.json"
        entries = json.loads(json_path.read_text(encoding="utf-8")) if json_path.exists() else []
        entries.append(entry)
        json_path.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = ["# Workspace session log", ""] + [
            f"- `{item['time']}` **{item['event']}** — mode `{item['mode']}`" for item in entries
        ]
        (self.root / "logs" / "session.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
