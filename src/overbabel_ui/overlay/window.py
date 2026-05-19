"""Fullscreen transparent click-through overlay (primary monitor).

Phase 1 はダミー描画のみ。Phase 3 以降で OCR / 翻訳の結果を描画する。
"""

from __future__ import annotations

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QGuiApplication, QPainter, QPaintEvent, QPen
from PyQt6.QtWidgets import QWidget

from overbabel_core.config.screen_coords import device_pixel_ratio
from overbabel_core.roi import RegionOfInterest
from overbabel_core.utils import get_logger
from overbabel_ui.overlay.debug_layer import DebugSample, draw_debug_layer
from overbabel_ui.overlay.render import labels_to_samples, rois_to_samples


class OverlayWindow(QWidget):
    """Frameless / translucent / topmost / click-through window.

    プライマリモニタの全画面を覆う。マウスとキーは下のアプリへ素通しする。
    """

    def __init__(self, *, debug_boxes: bool = False, live_mode: bool = False) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool  # タスクバーに出さない
            | Qt.WindowType.NoDropShadowWindowHint,
        )
        self._log = get_logger("ui.overlay")
        self._debug_boxes = debug_boxes
        self._live_mode = live_mode
        self._samples: list[DebugSample] = []
        self._region_hint: RegionOfInterest | None = None
        screen = QGuiApplication.primaryScreen()
        self._dpr = device_pixel_ratio(screen)

        # 透明 + クリックスルー
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        # 一部 Windows で透過を安定させるため
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setWindowOpacity(1.0)
        self.setWindowTitle("OverBabel Overlay")

        self._apply_primary_geometry()

    # --- geometry -------------------------------------------------------

    def _apply_primary_geometry(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            self._log.warning("overlay.no_primary_screen")
            return
        geo: QRect = screen.geometry()
        self.setGeometry(geo)
        self._log.info(
            "overlay.geometry",
            x=geo.x(),
            y=geo.y(),
            w=geo.width(),
            h=geo.height(),
            scale=screen.devicePixelRatio(),
        )

    # --- painting -------------------------------------------------------

    def paintEvent(self, _event: QPaintEvent | None) -> None:  # noqa: N802 (Qt API)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        # ベースは完全透明 (何も塗らない)
        if self._region_hint is not None:
            painter.setPen(QPen(Qt.GlobalColor.cyan, 2, Qt.PenStyle.DashLine))
            painter.drawRect(self._phys_to_widget_rect(self._region_hint))
        if self._debug_boxes or self._live_mode:
            samples = self._samples if self._live_mode else self._build_debug_samples()
            if samples:
                draw_debug_layer(painter, samples)

    def set_capture_region_hint(self, region: RegionOfInterest | None) -> None:
        self._region_hint = region
        self.update()

    def _phys_to_widget_rect(self, roi: RegionOfInterest) -> QRect:
        dpr = self._dpr if self._dpr > 0 else 1.0
        return QRect(
            int(roi.x / dpr),
            int(roi.y / dpr),
            max(1, int(roi.w / dpr)),
            max(1, int(roi.h / dpr)),
        )

    def _samples_to_widget(self, samples: list[DebugSample]) -> list[DebugSample]:
        out: list[DebugSample] = []
        for s in samples:
            r = s.rect
            phys = RegionOfInterest(r.x(), r.y(), r.width(), r.height())
            wr = self._phys_to_widget_rect(phys)
            out.append(DebugSample(tag=s.tag, text=s.text, rect=wr, accent=s.accent))
        return out

    def set_rois(self, rois: list[object]) -> None:
        from overbabel_core.roi import RegionOfInterest as R

        typed = [r for r in rois if isinstance(r, R)]
        self._samples = self._samples_to_widget(rois_to_samples(typed))
        self.update()

    def set_labels(self, labels: list[object]) -> None:
        samples = labels_to_samples(labels)  # type: ignore[arg-type]
        samples = self._samples_to_widget(samples)
        if samples == self._samples:
            return
        self._samples = samples
        self.update()

    def _build_debug_samples(self) -> list[DebugSample]:
        """モック画面と同じ位置関係でダミーラベルを返す。"""
        w = self.width()
        h = self.height()
        return [
            DebugSample(
                tag="UI",
                text="ゲーム開始",
                rect=QRect(int(w * 0.85), int(h * 0.04), 140, 38),
            ),
            DebugSample(
                tag="DIALOG",
                text="「船長、嵐の接近が予想より早いです。\n針路を南の島々へ変更すべきです」",
                rect=QRect(int(w * 0.06), int(h * 0.22), int(w * 0.36), 120),
            ),
            DebugSample(
                tag="SUBTITLE",
                text="— では選択の余地はない。直ちに出航せよ。",
                rect=QRect(int(w * 0.08), int(h * 0.85), int(w * 0.84), 60),
            ),
            DebugSample(
                tag="🎙 AUDIO",
                text="(BGMの歌詞)風よ、我らを連れて行け…",
                rect=QRect(int(w * 0.30), int(h * 0.94), int(w * 0.40), 36),
                accent=True,
            ),
        ]
