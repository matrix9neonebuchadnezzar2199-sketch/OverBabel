"""System tray for OverBabel.

Phase 1 では「オーバーレイ ON/OFF」「設定 (未実装)」「終了」の 3 項目。
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon


class OverBabelTray(QObject):
    toggle_overlay_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._tray = QSystemTrayIcon(self._default_icon(), parent)
        self._tray.setToolTip("OverBabel")

        self._menu = QMenu()

        self._act_toggle = QAction("オーバーレイを非表示", self._menu)
        self._act_toggle.triggered.connect(self.toggle_overlay_requested.emit)
        self._menu.addAction(self._act_toggle)

        self._act_settings = QAction("設定…", self._menu)
        self._act_settings.triggered.connect(self.settings_requested.emit)
        self._menu.addAction(self._act_settings)

        self._menu.addSeparator()

        self._act_quit = QAction("終了", self._menu)
        self._act_quit.triggered.connect(self.quit_requested.emit)
        self._menu.addAction(self._act_quit)

        self._tray.setContextMenu(self._menu)
        self._tray.activated.connect(self._on_activated)

    # --- public ---------------------------------------------------------

    def show(self) -> None:
        self._tray.show()

    def hide(self) -> None:
        self._tray.hide()

    def show_message(self, title: str, body: str) -> None:
        if self._tray.supportsMessages():
            self._tray.showMessage(title, body, self._default_icon(), 3000)

    def set_overlay_state(self, visible: bool) -> None:
        self._act_toggle.setText("オーバーレイを非表示" if visible else "オーバーレイを表示")

    def set_settings_enabled(self, enabled: bool) -> None:
        self._act_settings.setEnabled(enabled)

    # --- internal -------------------------------------------------------

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        # 左クリック / ダブルクリックでトグル
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.toggle_overlay_requested.emit()

    def _default_icon(self) -> QIcon:
        app = QApplication.instance()
        if isinstance(app, QApplication):
            style = app.style()
            if style is not None:
                return style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        return QIcon()
