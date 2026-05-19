"""Startup welcome menu: pick translation workload / mode."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
)

from overbabel_core.config.schema import OverBabelConfig, WorkModeId
from overbabel_core.config.work_modes import apply_work_mode


class WelcomeDialog(QDialog):
    def __init__(self, config: OverBabelConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("OverBabel — ようこそ")
        self.setMinimumWidth(520)
        self._config = config

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "<h2>OverBabel へようこそ</h2>"
                "<p>使い方に合わせてモードを選んでください。"
                "あとからトレイメニュー「モードを変更…」でも切り替えできます。</p>"
            )
        )

        self._group = QButtonGroup(self)
        self._opt_full = QRadioButton("① テキストライブ翻訳（画面全体）")
        self._opt_region = QRadioButton("② テキストライブ翻訳（指定した範囲のみ）")
        self._opt_audio = QRadioButton("③ 音声認識＋翻訳（指定した範囲に表示）")

        for i, (btn, hint, load) in enumerate(
            (
                (
                    self._opt_full,
                    "画面上のテキストを広く拾います。動画・ブラウザ全体向け。",
                    "負荷: 大",
                ),
                (
                    self._opt_region,
                    "ドラッグで囲んだ矩形の中だけ OCR します。字幕ウィンドウ向け。",
                    "負荷: 小",
                ),
                (
                    self._opt_audio,
                    "音声を認識して訳を、選んだ範囲の下に表示します（実験的）。",
                    "負荷: 中",
                ),
            )
        ):
            self._group.addButton(btn, i)
            block = QVBoxLayout()
            block.addWidget(btn)
            block.addWidget(QLabel(f"<small>{hint}</small>"))
            block.addWidget(QLabel(f"<small><b>{load}</b></small>"))
            layout.addLayout(block)

        mode = config.work_mode
        if mode == "text_full":
            self._opt_full.setChecked(True)
        elif mode == "audio_region":
            self._opt_audio.setChecked(True)
        else:
            self._opt_region.setChecked(True)

        form = QFormLayout()
        self._src = QComboBox()
        self._src.addItems(["en", "ja"])
        self._src.setCurrentText(config.source_language)
        self._tgt = QComboBox()
        self._tgt.addItems(["ja", "en"])
        self._tgt.setCurrentText(config.target_language)
        form.addRow("原文", self._src)
        form.addRow("訳文", self._tgt)
        layout.addLayout(form)

        self._hide_next = QCheckBox("次回からこのメニューを表示しない")
        self._hide_next.setChecked(not config.welcome.show_on_startup)
        layout.addWidget(self._hide_next)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("開始")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_mode(self) -> WorkModeId:
        if self._opt_full.isChecked():
            return "text_full"
        if self._opt_audio.isChecked():
            return "audio_region"
        return "text_region"

    def apply(self, config: OverBabelConfig) -> None:
        apply_work_mode(config, self.selected_mode())
        config.source_language = self._src.currentText()
        config.target_language = self._tgt.currentText()
        config.welcome.show_on_startup = not self._hide_next.isChecked()
        config.onboarding.completed = True
