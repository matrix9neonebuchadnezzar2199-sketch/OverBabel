"""Map between Qt logical screen coords and capture (physical) pixels."""

from __future__ import annotations

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QGuiApplication, QScreen

from overbabel_core.roi import RegionOfInterest


def primary_screen() -> QScreen | None:
    return QGuiApplication.primaryScreen()


def device_pixel_ratio(screen: QScreen | None = None) -> float:
    scr = screen or primary_screen()
    return float(scr.devicePixelRatio()) if scr is not None else 1.0


def picker_rect_to_capture_region(rect: QRect, screen: QScreen | None = None) -> RegionOfInterest:
    """Convert a widget-local picker rect to dxcam / OpenCV pixel coordinates."""
    scr = screen or primary_screen()
    if scr is None:
        return RegionOfInterest(rect.x(), rect.y(), rect.width(), rect.height())
    dpr = device_pixel_ratio(scr)
    geo = scr.geometry()
    top_left = rect.topLeft()
    # rect is already in dialog/client coords; caller passes global-mapped rect
    x = int((top_left.x()) * dpr)
    y = int((top_left.y()) * dpr)
    return RegionOfInterest(x, y, int(rect.width() * dpr), int(rect.height() * dpr))


def global_rect_to_capture_region(rect: QRect, screen: QScreen | None = None) -> RegionOfInterest:
    """Map a screen-global QRect (logical) to physical capture pixels."""
    scr = screen or primary_screen()
    if scr is None:
        return RegionOfInterest(rect.x(), rect.y(), rect.width(), rect.height())
    dpr = device_pixel_ratio(scr)
    geo = scr.geometry()
    x = int((rect.x() - geo.x()) * dpr)
    y = int((rect.y() - geo.y()) * dpr)
    return RegionOfInterest(x, y, int(rect.width() * dpr), int(rect.height() * dpr))
