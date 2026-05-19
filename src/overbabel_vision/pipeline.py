"""Vision pipeline: capture -> diff -> (optional) OCR -> translate."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from overbabel_core.roi import RegionOfInterest
from overbabel_core.utils import get_logger
from overbabel_vision.capture.base import ScreenCapture
from overbabel_vision.diff.frame_diff import FrameDiffer

_log = get_logger("vision.pipeline")


@dataclass(frozen=True)
class OverlayLabel:
    """One translated region for the UI overlay."""

    tag: str
    text: str
    roi: RegionOfInterest
    accent: bool = False


class VisionPipeline:
    """Runs capture loop steps; OCR/translate hooks optional (Phase 3+)."""

    def __init__(
        self,
        capture: ScreenCapture,
        *,
        diff_threshold: float = 25.0,
        min_roi_area: int = 400,
        max_rois_per_frame: int = 12,
        on_rois: Callable[[list[RegionOfInterest], np.ndarray], None] | None = None,
        on_labels: Callable[[list[OverlayLabel]], None] | None = None,
        process_rois: Callable[[np.ndarray, list[RegionOfInterest]], list[OverlayLabel]] | None = None,
    ) -> None:
        self._capture = capture
        self._differ = FrameDiffer(threshold=diff_threshold, min_area=min_roi_area)
        self._max_rois = max_rois_per_frame
        self._on_rois = on_rois
        self._on_labels = on_labels
        self._process_rois = process_rois
        self._running = False
        self._frame_count = 0
        self._roi_count = 0

    @property
    def frame_count(self) -> int:
        return self._frame_count

    @property
    def roi_count(self) -> int:
        return self._roi_count

    @property
    def has_ocr_pipeline(self) -> bool:
        return self._process_rois is not None

    def tick(self) -> None:
        """Process one frame (call from worker thread)."""
        frame = self._capture.grab()
        if frame is None:
            return
        self._frame_count += 1
        rois = self._differ.update(frame)
        if len(rois) > self._max_rois:
            rois = sorted(rois, key=lambda r: r.area, reverse=True)[: self._max_rois]
        if rois:
            self._roi_count += len(rois)
            # Raw ROI debug callback only when OCR pipeline is off (see app wiring).
            if self._on_rois is not None and self._process_rois is None:
                self._on_rois(rois, frame)
            if self._process_rois is not None and self._on_labels is not None:
                labels = self._process_rois(frame, rois)
                if labels:
                    self._on_labels(labels)

    def run_loop(self, *, fps_cap: int = 30, until: Callable[[], bool] | None = None) -> None:
        """Blocking loop for bench script."""
        self._running = True
        interval = 1.0 / max(fps_cap, 1)
        try:
            while self._running:
                if until is not None and until():
                    break
                t0 = time.perf_counter()
                self.tick()
                elapsed = time.perf_counter() - t0
                sleep = interval - elapsed
                if sleep > 0:
                    time.sleep(sleep)
        finally:
            self.close()

    def stop(self) -> None:
        self._running = False

    def close(self) -> None:
        self._capture.close()
