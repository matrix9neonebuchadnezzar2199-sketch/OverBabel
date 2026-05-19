"""Build DebugSample list from ROIs or overlay labels."""

from __future__ import annotations

from PyQt6.QtCore import QRect

from overbabel_core.roi import RegionOfInterest
from overbabel_ui.overlay.debug_layer import DebugSample
from overbabel_vision.pipeline import OverlayLabel


def rois_to_samples(rois: list[RegionOfInterest]) -> list[DebugSample]:
    return [DebugSample(tag="ROI", text="", rect=QRect(r.x, r.y, r.w, r.h)) for r in rois]


def labels_to_samples(labels: list[OverlayLabel]) -> list[DebugSample]:
    return [
        DebugSample(
            tag=label.tag,
            text=label.text,
            rect=QRect(label.roi.x, label.roi.y, label.roi.w, label.roi.h),
            accent=label.accent,
        )
        for label in labels
    ]
