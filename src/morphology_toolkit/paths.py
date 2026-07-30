"""Stable read-only bundle and writable user paths for desktop execution."""

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


def get_bundle_root() -> Path:
    """Return the read-only source, onedir, or onefile extraction root."""
    return bundled_root()


def get_resource_path(*parts: str) -> Path:
    """Resolve a resource without depending on the process working directory."""
    return resource_root().joinpath(*parts)


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
    if override:
        return Path(override).expanduser().resolve()
    return get_user_data_dir() / "logs"


def get_user_data_dir() -> Path:
    override = os.environ.get("MORPHOLOGY_USER_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local).resolve() / "MorphologyStudio"
    return Path.home() / "AppData" / "Local" / "MorphologyStudio"


def get_cache_dir() -> Path:
    return get_user_data_dir() / "cache"


def get_log_dir() -> Path:
    return logs_dir()
