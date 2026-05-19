"""Eleven settings pages as simple forms."""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QWidget,
)

from overbabel_core.config.schema import OverBabelConfig

Binder = Callable[[OverBabelConfig], None]


def _page(title: str, form: QFormLayout) -> QWidget:
    w = QWidget()
    lay = QFormLayout(w)
    lay.addRow(QLabel(f"<h3>{title}</h3>"))
    while form.rowCount():
        label = form.itemAt(0, QFormLayout.ItemRole.LabelRole)
        field = form.itemAt(0, QFormLayout.ItemRole.FieldRole)
        if label and field:
            lay.addRow(label.widget(), field.widget())
            form.removeRow(0)
    return w


def build_pages(cfg: OverBabelConfig) -> tuple[list[tuple[str, QWidget]], list[Binder]]:
    pages: list[tuple[str, QWidget]] = []
    binders: list[Binder] = []

    # 1 Profile
    prof = QComboBox()
    prof.addItems(["A", "B", "C", "D"])
    prof.setCurrentText(cfg.active_profile)
    f = QFormLayout()
    f.addRow("Active profile", prof)
    pages.append(("プロファイル", _wrap(f)))

    def bind_prof(c: OverBabelConfig) -> None:
        c.active_profile = prof.currentText()  # type: ignore[assignment]

    binders.append(bind_prof)

    # 2 Language
    src = QComboBox()
    src.addItems(["en", "ja", "de", "zh"])
    src.setCurrentText(cfg.source_language)
    tgt = QComboBox()
    tgt.addItems(["ja", "en", "de", "zh"])
    tgt.setCurrentText(cfg.target_language)
    f2 = QFormLayout()
    f2.addRow("Source", src)
    f2.addRow("Target", tgt)
    pages.append(("言語", _wrap(f2)))

    def bind_lang(c: OverBabelConfig) -> None:
        c.source_language = src.currentText()
        c.target_language = tgt.currentText()

    binders.append(bind_lang)

    # 3 Capture
    cap_on = QCheckBox()
    cap_on.setChecked(cfg.capture.enabled)
    fps = QSpinBox()
    fps.setRange(1, 60)
    fps.setValue(cfg.capture.fps_cap)
    f3 = QFormLayout()
    f3.addRow("Enable capture", cap_on)
    f3.addRow("FPS cap", fps)
    pages.append(("キャプチャ", _wrap(f3)))

    def bind_cap(c: OverBabelConfig) -> None:
        c.capture.enabled = cap_on.isChecked()
        c.capture.fps_cap = fps.value()

    binders.append(bind_cap)

    # 4 Audio
    aud = QCheckBox()
    aud.setChecked(cfg.audio.enabled)
    aud_band = QComboBox()
    aud_band.addItem("上", "top")
    aud_band.addItem("中央", "center")
    aud_band.addItem("下", "bottom")
    idx = aud_band.findData(cfg.audio.subtitle_band)
    aud_band.setCurrentIndex(idx if idx >= 0 else 2)
    f_aud = QFormLayout()
    f_aud.addRow("音声パイプライン", aud)
    f_aud.addRow("字幕の表示位置", aud_band)
    pages.append(("音声", _wrap(f_aud)))

    def bind_aud(c: OverBabelConfig) -> None:
        c.audio.enabled = aud.isChecked()
        c.audio.subtitle_band = aud_band.currentData()  # type: ignore[assignment]

    binders.append(bind_aud)

    # 5 OCR
    ocr = QComboBox()
    ocr.addItems(["rapidocr", "stub", "winocr", "tesseract"])
    ocr.setCurrentText(cfg.ocr.engine)
    pages.append(("OCR", _wrap_single("Engine", ocr)))

    def bind_ocr(c: OverBabelConfig) -> None:
        c.ocr.engine = ocr.currentText()  # type: ignore[assignment]

    binders.append(bind_ocr)

    # 6 Translate
    tr = QComboBox()
    tr.addItems(["opus_mt", "stub", "nllb", "llm_gguf"])
    tr.setCurrentText(cfg.translate.engine)
    pages.append(("翻訳", _wrap_single("Engine", tr)))

    def bind_tr(c: OverBabelConfig) -> None:
        c.translate.engine = tr.currentText()  # type: ignore[assignment]

    binders.append(bind_tr)

    # 7 Models
    pages.append(("モデル", QLabel("Models download via scripts/download_models.py (Phase 7)")))

    binders.append(lambda c: None)

    # 8 Overlay
    ct = QCheckBox()
    ct.setChecked(cfg.overlay.click_through)
    pages.append(("オーバーレイ", _wrap_single("Click-through", ct)))

    def bind_ov(c: OverBabelConfig) -> None:
        c.overlay.click_through = ct.isChecked()

    binders.append(bind_ov)

    # 9 Preview
    roi_dbg = QCheckBox()
    roi_dbg.setChecked(cfg.preview.show_roi_boxes)
    pages.append(("プレビュー", _wrap_single("Show ROI boxes", roi_dbg)))

    def bind_pr(c: OverBabelConfig) -> None:
        c.preview.show_roi_boxes = roi_dbg.isChecked()

    binders.append(bind_pr)

    # 10 Performance
    quiet = QCheckBox()
    quiet.setChecked(cfg.performance.quiet_mode)
    idle = QSpinBox()
    idle.setRange(1, 15)
    idle.setValue(cfg.performance.idle_fps_cap)
    cache = QSpinBox()
    cache.setRange(128, 100000)
    cache.setValue(cfg.performance.cache_size)
    pf = QFormLayout()
    pf.addRow("静音・省電力", quiet)
    pf.addRow("静止時 FPS 上限", idle)
    pf.addRow("Cache size", cache)
    pages.append(("パフォーマンス", _page("パフォーマンス", pf)))

    def bind_perf(c: OverBabelConfig) -> None:
        c.performance.quiet_mode = quiet.isChecked()
        c.performance.idle_fps_cap = idle.value()
        c.performance.cache_size = cache.value()

    binders.append(bind_perf)

    # 11 Hotkeys
    pages.append(("ホットキー", QLabel(f"Toggle: {cfg.hotkey.toggle_overlay}")))

    binders.append(lambda c: None)

    return pages, binders


def _wrap(form: QFormLayout) -> QWidget:
    w = QWidget()
    w.setLayout(form)
    return w


def _wrap_single(label: str, widget: QWidget) -> QWidget:
    f = QFormLayout()
    f.addRow(label, widget)
    return _wrap(f)
