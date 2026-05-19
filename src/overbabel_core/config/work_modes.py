"""Preset capture / audio settings from welcome-menu choices."""

from __future__ import annotations

from overbabel_core.config.schema import OverBabelConfig, TextScopeId


def apply_work_preferences(
    config: OverBabelConfig,
    text_scope: TextScopeId,
    *,
    audio: bool,
) -> None:
    """①/② は排他、音声は任意で追加。"""
    config.text_scope = text_scope
    config.audio.enabled = audio
    cap = config.capture
    cap.enabled = True
    if text_scope == "text_full":
        cap.subtitle_band_only = False
        cap.fps_cap = 18
        cap.min_roi_area = 2500
        cap.max_rois_per_frame = 10
        cap.region.enabled = False
    else:
        cap.subtitle_band_only = False
        cap.fps_cap = 12
        cap.min_roi_area = 1200
        cap.max_rois_per_frame = 8
        cap.region.enabled = True
