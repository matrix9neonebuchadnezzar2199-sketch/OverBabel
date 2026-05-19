"""AUDIO subtitle band placement."""

from __future__ import annotations

from overbabel_core.config.audio_overlay import (
    audio_subtitle_roi_in_region,
    audio_subtitle_widget_rect,
)
from overbabel_core.roi import RegionOfInterest


def test_audio_band_top_center_bottom_in_region() -> None:
    region = RegionOfInterest(100, 200, 800, 600)
    top = audio_subtitle_roi_in_region(region, "top", band_height=48)
    assert top.x == 100 and top.w == 800 and top.h == 48
    assert top.y == 200

    center = audio_subtitle_roi_in_region(region, "center", band_height=48)
    assert center.y == 200 + (600 - 48) // 2

    bottom = audio_subtitle_roi_in_region(region, "bottom", band_height=48)
    assert bottom.y == 200 + 600 - 48


def test_audio_band_clamps_to_small_region() -> None:
    region = RegionOfInterest(0, 0, 100, 30)
    roi = audio_subtitle_roi_in_region(region, "bottom", band_height=48)
    assert roi.h == 30
    assert roi.y == 0


def test_audio_band_fullscreen_rect_ordering() -> None:
    top = audio_subtitle_widget_rect(1920, 1080, "top")
    center = audio_subtitle_widget_rect(1920, 1080, "center")
    bottom = audio_subtitle_widget_rect(1920, 1080, "bottom")
    assert top.y() < center.y() < bottom.y()
