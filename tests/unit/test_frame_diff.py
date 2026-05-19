"""Frame diff unit tests (no dxcam)."""

from __future__ import annotations

import numpy as np

from overbabel_vision.diff.frame_diff import FrameDiffer, diff_rois


def test_diff_rois_detects_change() -> None:
    prev = np.zeros((100, 100), dtype=np.uint8)
    curr = prev.copy()
    curr[10:40, 10:40] = 255
    rois = diff_rois(prev, curr, threshold=10.0, min_area=50)
    assert len(rois) >= 1
    assert rois[0].area >= 50


def test_frame_differ_first_frame_empty() -> None:
    differ = FrameDiffer(min_area=10)
    frame = np.zeros((50, 50, 3), dtype=np.uint8)
    assert differ.update(frame) == []
