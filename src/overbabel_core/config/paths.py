"""Filesystem paths for config and model storage."""

from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_data_dir

_APP_NAME = "OverBabel"


def get_config_dir() -> Path:
    """Return the directory used for `config.toml` and related files."""
    override = os.environ.get("OVERBABEL_CONFIG_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(user_data_dir(_APP_NAME, appauthor=False))


def get_config_path() -> Path:
    """Return the full path to the primary TOML config file."""
    return get_config_dir() / "config.toml"


def get_model_dir() -> Path:
    """Return the root directory for downloaded models."""
    override = os.environ.get("OVERBABEL_MODEL_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return get_config_dir() / "models"
