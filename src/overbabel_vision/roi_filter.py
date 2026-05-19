"""Heuristics to drop noisy diff boxes (video motion, browser chrome)."""

from __future__ import annotations

from overbabel_core.roi import RegionOfInterest


def filter_translation_candidates(
    rois: list[RegionOfInterest],
    frame_width: int,
    frame_height: int,
    *,
    subtitle_band: bool = True,
) -> list[RegionOfInterest]:
    """Keep regions that look like subtitles or readable text blocks."""
    if not rois:
        return []
    out: list[RegionOfInterest] = []
    for r in rois:
        if r.w < 60 or r.h < 14:
            continue
        aspect = r.w / max(r.h, 1)
        bottom = r.y + r.h >= int(frame_height * 0.52)
        wide_line = aspect >= 2.0 and r.w >= 100 and r.h <= 120
        text_block = 18 <= r.h <= 200 and r.w >= 80
        if subtitle_band:
            if bottom and (wide_line or text_block):
                out.append(r)
        elif wide_line or text_block:
            out.append(r)
    out.sort(key=lambda x: x.area, reverse=True)
    return out
