"""HotkeyManager は pynput が無い環境でも import / start / stop が落ちないこと。"""

from __future__ import annotations

from overbabel_ui.hotkey.manager import HotkeyManager


def test_hotkey_manager_lifecycle_safe() -> None:
    called: list[str] = []
    mgr = HotkeyManager({"<ctrl>+<alt>+t": lambda: called.append("hit")})
    # pynput が無くても例外を投げないこと
    mgr.start()
    mgr.stop()
