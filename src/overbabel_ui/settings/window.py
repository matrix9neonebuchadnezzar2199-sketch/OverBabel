"""Settings shell: sidebar + 11 pages (Phase 4)."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from overbabel_core.config.loader import load_config, save_config
from overbabel_core.config.schema import OverBabelConfig
from overbabel_ui.settings.pages import build_pages


class SettingsWindow(QMainWindow):
    config_saved = pyqtSignal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("OverBabel Settings")
        self.resize(900, 620)
        self._config: OverBabelConfig = load_config()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        self._nav = QListWidget()
        self._stack = QStackedWidget()
        self._page_widgets, self._page_binders = build_pages(self._config)
        for title, widget in self._page_widgets:
            self._nav.addItem(QListWidgetItem(title))
            self._stack.addWidget(widget)

        self._nav.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._nav.setCurrentRow(0)

        layout.addWidget(self._nav, 1)
        layout.addWidget(self._stack, 4)

        footer = QVBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._on_save)
        footer.addWidget(save_btn)
        layout.addLayout(footer)

    def _on_save(self) -> None:
        for binder in self._page_binders:
            binder(self._config)
        save_config(self._config)
        self.config_saved.emit(self._config)
        self.close()
