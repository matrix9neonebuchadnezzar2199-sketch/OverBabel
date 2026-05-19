"""Preset capture / audio settings from welcome-menu choices."""

from __future__ import annotations

from overbabel_core.config.region_util import clear_capture_region, region_from_settings
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
        clear_capture_region(cap.region)
    else:
        cap.subtitle_band_only = False
        cap.fps_cap = 12
        cap.min_roi_area = 1200
        cap.max_rois_per_frame = 8
        # ②は毎回ピッカーで確定するまで古い範囲を使わない
        if region_from_settings(cap.region) is None:
            clear_capture_region(cap.region)
        else:
            cap.region.enabled = True
            cap.region.confirmed = False
    _apply_quiet_tuning(config)


def _apply_quiet_tuning(config: OverBabelConfig) -> None:
    if not config.performance.quiet_mode:
        return
    cap = config.capture
    if config.text_scope == "text_full":
        cap.fps_cap = min(cap.fps_cap, 10)
        cap.max_rois_per_frame = min(cap.max_rois_per_frame, 6)
    else:
        cap.fps_cap = min(cap.fps_cap, 6)
        cap.max_rois_per_frame = min(cap.max_rois_per_frame, 4)
