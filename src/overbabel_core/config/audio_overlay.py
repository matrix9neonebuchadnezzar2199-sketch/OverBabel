"""AUDIO subtitle strip placement within capture region or fullscreen."""

from __future__ import annotations

from typing import Literal

from PyQt6.QtCore import QRect

from overbabel_core.roi import RegionOfInterest

AudioSubtitleBandId = Literal["top", "center", "bottom"]

DEFAULT_BAND_HEIGHT = 48


def audio_subtitle_roi_in_region(
    region: RegionOfInterest,
    band: AudioSubtitleBandId,
    *,
    band_height: int = DEFAULT_BAND_HEIGHT,
) -> RegionOfInterest:
    """Place a horizontal strip inside *region* at top, center, or bottom."""
    h = min(max(band_height, 1), region.h)
    if band == "top":
        y_off = 0
    elif band == "center":
        y_off = max((region.h - h) // 2, 0)
    else:
        y_off = max(region.h - h, 0)
    return RegionOfInterest(region.x, region.y + y_off, region.w, h)


def audio_subtitle_widget_rect(
    width: int,
    height: int,
    band: AudioSubtitleBandId,
    *,
    band_height: int = DEFAULT_BAND_HEIGHT,
    band_width_ratio: float = 0.6,
) -> QRect:
    """Logical overlay coords for fullscreen (no capture region)."""
    w_band = max(1, int(width * band_width_ratio))
    x = int(width * (1.0 - band_width_ratio) / 2.0)
    h = min(max(band_height, 1), max(height, 1))
    if band == "top":
        y = int(height * 0.04)
    elif band == "center":
        y = max((height - h) // 2, 0)
    else:
        y = max(int(height * 0.9) - h, 0)
    return QRect(x, y, w_band, h)
