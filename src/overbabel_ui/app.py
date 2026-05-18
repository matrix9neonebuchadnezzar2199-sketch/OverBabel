"""Application lifecycle for OverBabel UI.

QApplication をシングルトンとして保持し、Overlay / Tray / Hotkey を束ねる。
Phase 1 では overlay にダミー描画のみを表示する。
"""

from __future__ import annotations

import signal
import sys
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication

from overbabel_core.config.loader import load_config, save_config
from overbabel_core.utils import get_logger, setup_logging
from overbabel_ui.hotkey.manager import HotkeyManager
from overbabel_ui.overlay.window import OverlayWindow
from overbabel_ui.tray.tray import OverBabelTray

if TYPE_CHECKING:
    from overbabel_core.config.schema import OverBabelConfig


class OverBabelApp(QObject):
    """Phase 1 application controller.

    - QApplication を生成
    - OverlayWindow をプライマリモニタ全画面で表示
    - QSystemTrayIcon を常駐
    - グローバルホットキーで overlay の表示/非表示を切替
    """

    overlay_toggle_requested = pyqtSignal()

    def __init__(self, *, debug_boxes: bool = False) -> None:
        super().__init__()
        self._log = get_logger("ui.app")
        self._debug_boxes = debug_boxes
        self._config: OverBabelConfig = load_config()
        save_config(self._config)  # ensure file exists

        self._qapp = QApplication.instance() or QApplication(sys.argv)
        assert isinstance(self._qapp, QApplication)
        self._qapp.setQuitOnLastWindowClosed(False)  # trayがあるので閉じても終了しない
        self._qapp.setApplicationName("OverBabel")

        self._overlay = OverlayWindow(debug_boxes=self._debug_boxes)
        self._tray = OverBabelTray(parent=self)
        self._hotkeys = HotkeyManager(
            bindings={
                self._config.hotkey.toggle_overlay: self.request_toggle_overlay,
            }
        )

        # 接続
        self.overlay_toggle_requested.connect(self._on_toggle_overlay)
        self._tray.toggle_overlay_requested.connect(self.request_toggle_overlay)
        self._tray.quit_requested.connect(self.quit)

        # Ctrl+C 対応 (PyQt はデフォルトで SIGINT を握り潰す)
        signal.signal(signal.SIGINT, lambda *_: self.quit())
        # SIGINT を Python に届けるため、ダミータイマで毎100msイベントループを起こす
        self._sigint_timer = QTimer(self)
        self._sigint_timer.start(100)
        self._sigint_timer.timeout.connect(lambda: None)

    # --- public ---------------------------------------------------------

    def run(self) -> int:
        self._log.info(
            "app.start",
            debug_boxes=self._debug_boxes,
            toggle_hotkey=self._config.hotkey.toggle_overlay,
        )
        self._overlay.show()
        self._tray.show()
        self._hotkeys.start()
        self._tray.show_message(
            "OverBabel",
            "Overlay is running. Press Ctrl+Alt+T to toggle.",
        )
        try:
            return self._qapp.exec()
        finally:
            self._hotkeys.stop()
            self._log.info("app.exit")

    @pyqtSlot()
    def request_toggle_overlay(self) -> None:
        """スレッド安全にトグルを依頼する。pynput スレッドからも呼べる。"""
        self.overlay_toggle_requested.emit()

    @pyqtSlot()
    def quit(self) -> None:
        self._log.info("app.quit_requested")
        self._hotkeys.stop()
        self._tray.hide()
        self._overlay.close()
        self._qapp.quit()

    # --- internal -------------------------------------------------------

    @pyqtSlot()
    def _on_toggle_overlay(self) -> None:
        visible = self._overlay.isVisible()
        if visible:
            self._overlay.hide()
            self._tray.set_overlay_state(False)
            self._log.info("overlay.hidden")
        else:
            self._overlay.show()
            self._tray.set_overlay_state(True)
            self._log.info("overlay.shown")


def run_app(*, debug_boxes: bool = False) -> int:
    setup_logging()
    # Windows DPI: Qt 6 はデフォルトで PerMonitorV2 だが念のため属性指定
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = OverBabelApp(debug_boxes=debug_boxes)
    return app.run()
