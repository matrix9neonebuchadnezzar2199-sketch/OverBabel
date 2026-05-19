"""Preset capture / audio settings per user-facing work mode."""

from __future__ import annotations

from overbabel_core.config.schema import OverBabelConfig, WorkModeId


def apply_work_mode(config: OverBabelConfig, mode: WorkModeId) -> None:
    """Map welcome-menu choice to concrete pipeline settings."""
    config.work_mode = mode
    cap = config.capture
    if mode == "text_full":
        cap.enabled = True
        cap.subtitle_band_only = False
        cap.fps_cap = 18
        cap.min_roi_area = 3500
        cap.max_rois_per_frame = 10
        cap.region.enabled = False
        config.audio.enabled = False
    elif mode == "text_region":
        cap.enabled = True
        cap.subtitle_band_only = False
        cap.fps_cap = 12
        cap.min_roi_area = 5000
        cap.max_rois_per_frame = 6
        cap.region.enabled = True
        config.audio.enabled = False
    else:  # audio_region
        cap.enabled = False
        cap.region.enabled = True
        config.audio.enabled = True
        config.grpc.vision_enabled = False
