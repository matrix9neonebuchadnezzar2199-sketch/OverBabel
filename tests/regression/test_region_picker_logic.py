"""Pure logic for region picker (no Qt display required)."""

from __future__ import annotations

from PyQt6.QtCore import QRect

from overbabel_ui.region_picker import clamp_rect_to_bounds


def test_clamp_rect_stays_inside_bounds() -> None:
    bounds = QRect(0, 0, 800, 600)
    rect = QRect(750, 550, 200, 200)
    out = clamp_rect_to_bounds(rect, bounds)
    assert out.right() <= bounds.right()
    assert out.bottom() <= bounds.bottom()
    assert out.left() >= bounds.left()
    assert out.top() >= bounds.top()
