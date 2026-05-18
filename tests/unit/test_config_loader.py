"""Config loader round-trip."""

from __future__ import annotations

from pathlib import Path

import pytest

from overbabel_core.config.loader import load_config, save_config
from overbabel_core.config.schema import HotkeySettings, OverBabelConfig


def test_save_and_load_config_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OVERBABEL_CONFIG_DIR", str(tmp_path))
    original = OverBabelConfig(
        source_language="de",
        hotkey=HotkeySettings(toggle_overlay="<ctrl>+<alt>+x"),
    )
    save_config(original)
    loaded = load_config()
    assert loaded.source_language == "de"
    assert loaded.hotkey.toggle_overlay == "<ctrl>+<alt>+x"
    assert (tmp_path / "config.toml").is_file()
