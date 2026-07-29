from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TextIO


def log_directory() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    root = Path(base) / "MorphologyStudio" if base else Path.home() / ".morphology_studio"
    return root / "logs"


def configure_logging(stream: TextIO | None = None) -> Path:
    directory = log_directory()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "morphology-studio.log"
    handlers: list[logging.Handler] = [
        RotatingFileHandler(
            path,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
    ]
    candidate = sys.stderr if stream is None else stream
    if candidate is not None and callable(getattr(candidate, "write", None)):
        handlers.append(logging.StreamHandler(candidate))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )
    return path
