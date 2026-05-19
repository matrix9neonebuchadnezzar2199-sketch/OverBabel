"""Numpy/OpenCV frame differencing and connected-component ROI extraction."""

from __future__ import annotations

import cv2
import numpy as np

from overbabel_core.roi import RegionOfInterest


def diff_rois(
    prev_gray: np.ndarray,
    curr_gray: np.ndarray,
    *,
    threshold: float = 25.0,
    min_area: int = 400,
) -> list[RegionOfInterest]:
    """Return ROIs where ``curr`` differs from ``prev`` (both HxW uint8)."""
    if prev_gray.shape != curr_gray.shape:
        return []
    delta = cv2.absdiff(prev_gray, curr_gray)
    _, mask = cv2.threshold(delta, threshold, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rois: list[RegionOfInterest] = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h < min_area:
            continue
        rois.append(RegionOfInterest(x=x, y=y, w=w, h=h))
    return rois


class FrameDiffer:
    """Stateful differ comparing consecutive grayscale frames."""

    def __init__(self, *, threshold: float = 25.0, min_area: int = 400) -> None:
        self._threshold = threshold
        self._min_area = min_area
        self._prev: np.ndarray | None = None

    def reset(self) -> None:
        self._prev = None

    def update(self, frame_bgr: np.ndarray) -> list[RegionOfInterest]:
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        if self._prev is None:
            self._prev = gray
            return []
        rois = diff_rois(
            self._prev,
            gray,
            threshold=self._threshold,
            min_area=self._min_area,
        )
        self._prev = gray
        return rois
