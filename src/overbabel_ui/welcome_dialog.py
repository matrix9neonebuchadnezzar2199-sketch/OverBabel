"""Startup welcome menu: text scope (①/②) + optional audio."""

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

from overbabel_core.config.schema import OverBabelConfig, TextScopeId
from overbabel_core.config.user_flow import apply_user_choices


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
                "<p>テキスト翻訳の範囲を選び、必要なら音声翻訳も追加できます。"
                "あとからトレイ「モードを変更…」でも切り替えられます。</p>"
            )
        )

        layout.addWidget(QLabel("<b>テキストライブ翻訳（どちらか一方）</b>"))

        self._group = QButtonGroup(self)
        self._opt_full = QRadioButton("① 画面に表示されるテキスト全体")
        self._opt_region = QRadioButton("② 指定した範囲のみ（ドラッグで囲む）")

        for i, (btn, hint, load) in enumerate(
            (
                (
                    self._opt_full,
                    "動画・ブラウザ全体向け。画面上の文字を広く拾います。",
                    "負荷: 大",
                ),
                (
                    self._opt_region,
                    "「開始」の直後、必ず画面でドラッグして範囲を囲みます。",
                    "負荷: 小",
                ),
            )
        ):
            self._group.addButton(btn, i)
            block = QVBoxLayout()
            block.addWidget(btn)
            block.addWidget(QLabel(f"<small>{hint}</small>"))
            block.addWidget(QLabel(f"<small><b>{load}</b></small>"))
            layout.addLayout(block)

        if config.text_scope == "text_full":
            self._opt_full.setChecked(True)
        else:
            self._opt_region.setChecked(True)

        self._audio = QCheckBox("＋ 音声認識＋翻訳も実行する")
        self._audio.setChecked(config.audio.enabled)
        layout.addWidget(self._audio)
        layout.addWidget(
            QLabel(
                "<small>音声の訳は、②のときは指定範囲の下、①のときは画面下部に表示します。"
                "（実験的・負荷: 中）</small>"
            )
        )

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

        self._quiet = QCheckBox("静音・省電力（CPU 負荷を抑える）")
        self._quiet.setChecked(config.performance.quiet_mode)
        layout.addWidget(self._quiet)

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

    def selected_text_scope(self) -> TextScopeId:
        return "text_full" if self._opt_full.isChecked() else "text_region"

    def apply(self, config: OverBabelConfig) -> None:
        apply_user_choices(
            config,
            text_scope=self.selected_text_scope(),
            audio=self._audio.isChecked(),
            quiet_mode=self._quiet.isChecked(),
        )
        config.source_language = self._src.currentText()
        config.target_language = self._tgt.currentText()
        config.welcome.show_on_startup = not self._hide_next.isChecked()
        config.onboarding.completed = True
