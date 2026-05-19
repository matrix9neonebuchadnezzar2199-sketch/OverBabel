"""Smoke tests for Phase 0 scaffolding."""

from __future__ import annotations

import overbabel_core
from overbabel_core.config import (
    OverBabelConfig,
    get_config_dir,
    get_config_path,
    get_model_dir,
)


def test_package_version() -> None:
    assert overbabel_core.__version__ == "0.8.0"


def test_config_paths_are_absolute() -> None:
    assert get_config_dir().is_absolute()
    assert get_config_path().is_absolute()
    assert get_model_dir().is_absolute()
    assert get_config_path().name == "config.toml"


def test_default_config_roundtrip_dict() -> None:
    cfg = OverBabelConfig()
    data = cfg.model_dump()
    restored = OverBabelConfig.model_validate(data)
    assert restored == cfg
