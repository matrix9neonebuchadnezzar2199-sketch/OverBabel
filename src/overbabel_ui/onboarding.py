"""First-run onboarding dialog (Phase 7)."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
)

from overbabel_core.config.schema import OverBabelConfig


class OnboardingDialog(QDialog):
    def __init__(self, config: OverBabelConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("OverBabel Setup")
        self._config = config
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Welcome to OverBabel. Choose languages and profile."))
        form = QFormLayout()
        self._profile = QComboBox()
        self._profile.addItems(["A", "B", "C", "D"])
        self._profile.setCurrentText(config.active_profile)
        self._src = QComboBox()
        self._src.addItems(["en", "ja"])
        self._src.setCurrentText(config.source_language)
        self._tgt = QComboBox()
        self._tgt.addItems(["ja", "en"])
        self._tgt.setCurrentText(config.target_language)
        form.addRow("Profile", self._profile)
        form.addRow("Source language", self._src)
        form.addRow("Target language", self._tgt)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def apply(self, config: OverBabelConfig) -> None:
        config.active_profile = self._profile.currentText()  # type: ignore[assignment]
        config.source_language = self._src.currentText()
        config.target_language = self._tgt.currentText()
        config.onboarding.completed = True
