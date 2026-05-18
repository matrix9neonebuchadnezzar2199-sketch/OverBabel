"""Global hotkey manager using pynput.

pynput はバックグラウンドスレッドでイベントを発火するため、Qt スレッドに
直接触らないこと。コールバックは Qt 側のシグナルへ橋渡しすることを前提とする。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from overbabel_core.utils import get_logger

try:
    from pynput import keyboard as kb
except Exception:  # pragma: no cover - pynput is optional at install time
    kb = None


HotkeyCallback = Callable[[], None]


class HotkeyManager:
    """Global hotkey listener wrapper.

    bindings = {"<ctrl>+<alt>+t": callback, ...}
    pynput の GlobalHotKeys 形式 (`<ctrl>+<alt>+t`) をそのまま受ける。
    """

    def __init__(self, bindings: dict[str, HotkeyCallback]) -> None:
        self._log = get_logger("ui.hotkey")
        self._bindings = bindings
        self._listener: Any = None

    def start(self) -> None:
        if kb is None:
            self._log.warning("hotkey.pynput_unavailable")
            return
        if self._listener is not None:
            return
        try:
            self._listener = kb.GlobalHotKeys(self._bindings)
            self._listener.start()
            self._log.info("hotkey.start", count=len(self._bindings))
        except Exception as exc:
            self._log.warning("hotkey.start_failed", error=str(exc))
            self._listener = None

    def stop(self) -> None:
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception as exc:
                self._log.warning("hotkey.stop_failed", error=str(exc))
            finally:
                self._listener = None
                self._log.info("hotkey.stop")
