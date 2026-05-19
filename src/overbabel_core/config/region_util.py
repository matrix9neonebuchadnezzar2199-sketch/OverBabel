"""Helpers for persisted capture rectangles."""

from __future__ import annotations

from overbabel_core.config.schema import CaptureRegionSettings, OverBabelConfig
from overbabel_core.roi import RegionOfInterest


def region_from_settings(settings: CaptureRegionSettings) -> RegionOfInterest | None:
    if not settings.enabled or settings.w < 80 or settings.h < 48:
        return None
    return RegionOfInterest(settings.x, settings.y, settings.w, settings.h)


def write_region_to_settings(settings: CaptureRegionSettings, region: RegionOfInterest) -> None:
    settings.enabled = True
    settings.x = region.x
    settings.y = region.y
    settings.w = region.w
    settings.h = region.h


def needs_region_pick(config: OverBabelConfig) -> bool:
    return config.work_mode in ("text_region", "audio_region") and region_from_settings(
        config.capture.region
    ) is None


def active_capture_region(config: OverBabelConfig) -> RegionOfInterest | None:
    if config.work_mode == "text_full":
        return None
    return region_from_settings(config.capture.region)
