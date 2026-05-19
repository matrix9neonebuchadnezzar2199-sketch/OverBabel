"""QThread wrapper for vision pipeline."""

from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from overbabel_core.roi import RegionOfInterest
from overbabel_vision.pipeline import OverlayLabel, VisionPipeline


class VisionWorker(QThread):
    rois_updated = pyqtSignal(list)
    labels_updated = pyqtSignal(list)

    def __init__(self, pipeline: VisionPipeline, *, fps_cap: int = 30) -> None:
        super().__init__()
        self._pipeline = pipeline
        self._fps_cap = fps_cap
        self._running = True

    def run(self) -> None:
        if self._pipeline.has_ocr_pipeline:
            self._pipeline._on_labels = self._emit_labels
        else:
            self._pipeline._on_rois = self._emit_rois
        self._pipeline.run_loop(fps_cap=self._fps_cap, until=lambda: not self._running)

    def stop(self) -> None:
        self._running = False
        self._pipeline.stop()

    def _emit_rois(self, rois: list[RegionOfInterest], _frame) -> None:
        self.rois_updated.emit(rois)

    def _emit_labels(self, labels: list[OverlayLabel]) -> None:
        self.labels_updated.emit(labels)
