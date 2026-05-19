"""Single source of truth for welcome-menu choices -> runtime behavior."""

from __future__ import annotations

from overbabel_core.config.region_util import (
    active_capture_region,
    needs_region_pick,
)
from overbabel_core.config.schema import OverBabelConfig, TextScopeId
from overbabel_core.config.work_modes import apply_work_preferences

__all__ = [
    "apply_user_choices",
    "active_capture_region",
    "needs_region_pick",
    "should_show_region_picker",
    "should_use_grpc_audio",
    "should_use_grpc_vision",
    "should_show_raw_roi_boxes",
]


def apply_user_choices(
    config: OverBabelConfig,
    *,
    text_scope: TextScopeId,
    audio: bool,
    quiet_mode: bool,
) -> None:
    """Apply welcome / mode-change UI selections to config."""
    config.performance.quiet_mode = quiet_mode
    apply_work_preferences(config, text_scope, audio=audio)


def should_show_region_picker(config: OverBabelConfig, *, after_welcome: bool) -> bool:
    """②: always pick after welcome; otherwise pick only if region not confirmed."""
    if config.text_scope != "text_region":
        return False
    if after_welcome:
        return True
    return needs_region_pick(config)


def should_use_grpc_vision(*, cli_use_grpc: bool) -> bool:
    """Vision gRPC is opt-in from CLI; audio must not enable it."""
    return cli_use_grpc


def should_use_grpc_audio(config: OverBabelConfig) -> bool:
    return config.audio.enabled


def should_show_raw_roi_boxes(config: OverBabelConfig, *, debug_raw_rois: bool) -> bool:
    """Mode ② never shows raw diff boxes (full-screen flicker)."""
    if debug_raw_rois:
        return True
    if config.text_scope == "text_region":
        return False
    return config.preview.show_roi_boxes or config.overlay.show_roi_boxes
