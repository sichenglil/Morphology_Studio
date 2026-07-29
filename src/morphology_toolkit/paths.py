"""Stable resource paths for source and PyInstaller onedir execution."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def executable_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def bundled_root() -> Path:
    bundle = getattr(sys, "_MEIPASS", None)
    return Path(bundle).resolve() if bundle else executable_root()


def resource_root() -> Path:
    override = os.environ.get("MORPHOLOGY_RESOURCE_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    external = executable_root()
    if (external / "assets").is_dir() and (external / "config").is_dir():
        return external
    return bundled_root()


def assets_dir() -> Path:
    return resource_root() / "assets"


def config_dir() -> Path:
    return resource_root() / "config"


def logs_dir() -> Path:
    override = os.environ.get("MORPHOLOGY_LOG_DIR")
    return Path(override).expanduser().resolve() if override else executable_root() / "logs"
