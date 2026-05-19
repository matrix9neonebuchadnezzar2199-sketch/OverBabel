"""Load and save `OverBabelConfig` as TOML under the user config directory."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from overbabel_core.config.paths import get_config_path
from overbabel_core.config.schema import OverBabelConfig


def _migrate_config_data(data: dict[str, Any]) -> dict[str, Any]:
    """Map legacy `work_mode` / `audio_region` to `text_scope` + `audio.enabled`."""
    if "text_scope" not in data:
        legacy = data.pop("work_mode", None)
        if legacy == "audio_region":
            data["text_scope"] = "text_region"
            audio = data.setdefault("audio", {})
            if isinstance(audio, dict):
                audio["enabled"] = True
        elif legacy in ("text_full", "text_region"):
            data["text_scope"] = legacy
    return data


def load_config() -> OverBabelConfig:
    """Return configuration from disk, or defaults if the file is missing."""
    path = get_config_path()
    if not path.exists():
        return OverBabelConfig()
    text = path.read_text(encoding="utf-8")
    data: dict[str, Any] = _migrate_config_data(tomllib.loads(text))
    return OverBabelConfig.model_validate(data)


def save_config(config: OverBabelConfig) -> None:
    """Persist configuration to TOML, creating parent directories as needed."""
    path: Path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = config.model_dump(mode="python", exclude_none=True)
    with path.open("wb") as handle:
        tomli_w.dump(payload, handle)
