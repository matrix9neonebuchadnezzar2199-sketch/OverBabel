"""Configuration schema and paths for OverBabel."""

from overbabel_core.config.paths import get_config_dir, get_config_path, get_model_dir
from overbabel_core.config.schema import OverBabelConfig

__all__ = [
    "OverBabelConfig",
    "get_config_dir",
    "get_config_path",
    "get_model_dir",
]
