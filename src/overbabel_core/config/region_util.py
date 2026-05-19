"""Helpers for persisted capture rectangles."""

from __future__ import annotations

from overbabel_core.config.schema import CaptureRegionSettings, OverBabelConfig
from overbabel_core.roi import RegionOfInterest

_MIN_W = 80
_MIN_H = 48


def region_from_settings(settings: CaptureRegionSettings) -> RegionOfInterest | None:
    if settings.w < _MIN_W or settings.h < _MIN_H:
        return None
    return RegionOfInterest(settings.x, settings.y, settings.w, settings.h)


def write_region_to_settings(settings: CaptureRegionSettings, region: RegionOfInterest) -> None:
    settings.enabled = True
    settings.confirmed = True
    settings.x = region.x
    settings.y = region.y
    settings.w = region.w
    settings.h = region.h


def clear_capture_region(settings: CaptureRegionSettings) -> None:
    settings.enabled = False
    settings.confirmed = False
    settings.x = 0
    settings.y = 0
    settings.w = 0
    settings.h = 0


def needs_region_pick(config: OverBabelConfig) -> bool:
    if config.text_scope != "text_region":
        return False
    reg = config.capture.region
    if not reg.confirmed:
        return True
    return region_from_settings(reg) is None


def active_capture_region(config: OverBabelConfig) -> RegionOfInterest | None:
    if config.text_scope != "text_region":
        return None
    return region_from_settings(config.capture.region)
