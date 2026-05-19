"""Operational regression checklist — user selection, region, vision, overlay.

Run all sections:
    python test.py

Or only this file:
    python -m pytest tests/regression/test_operational_checklist.py -v
"""

from __future__ import annotations

import numpy as np
import pytest
from PyQt6.QtCore import QRect

from overbabel_core.config.loader import _migrate_config_data
from overbabel_core.config.region_util import (
    active_capture_region,
    clear_capture_region,
    needs_region_pick,
    write_region_to_settings,
)
from overbabel_core.config.schema import OverBabelConfig
from overbabel_core.config.screen_coords import global_rect_to_capture_region, widget_rect_to_capture_region
from overbabel_core.config.user_flow import (
    apply_user_choices,
    should_show_raw_roi_boxes,
    should_show_region_picker,
    should_use_grpc_audio,
    should_use_grpc_vision,
)
from overbabel_core.config.work_modes import apply_work_preferences
from overbabel_core.roi import RegionOfInterest
from overbabel_ui.overlay.label_stabilizer import LabelStabilizer
from overbabel_vision.pipeline import VisionPipeline
from overbabel_vision.roi_filter import clip_rois_to_capture_region


class TestUserSelectionFlow:
    """Welcome / mode ①② + audio checkbox -> config."""

    def test_mode_full_clears_region(self) -> None:
        cfg = OverBabelConfig(text_scope="text_region")
        write_region_to_settings(cfg.capture.region, RegionOfInterest(1, 2, 200, 100))
        apply_user_choices(cfg, text_scope="text_full", audio=False, quiet_mode=False)
        assert cfg.text_scope == "text_full"
        assert active_capture_region(cfg) is None

    def test_mode_region_clears_until_picker(self) -> None:
        cfg = OverBabelConfig()
        write_region_to_settings(cfg.capture.region, RegionOfInterest(10, 20, 300, 200))
        apply_user_choices(cfg, text_scope="text_region", audio=True, quiet_mode=True)
        assert cfg.text_scope == "text_region"
        assert cfg.audio.enabled is True
        assert cfg.performance.quiet_mode is True
        assert active_capture_region(cfg) is None
        assert needs_region_pick(cfg) is True

    def test_welcome_always_picks_for_mode_region(self) -> None:
        cfg = OverBabelConfig(text_scope="text_region")
        write_region_to_settings(cfg.capture.region, RegionOfInterest(0, 0, 400, 300))
        assert should_show_region_picker(cfg, after_welcome=True) is True

    def test_skip_picker_when_region_confirmed_and_no_welcome(self) -> None:
        cfg = OverBabelConfig(text_scope="text_region")
        write_region_to_settings(cfg.capture.region, RegionOfInterest(10, 20, 400, 300))
        assert should_show_region_picker(cfg, after_welcome=False) is False
        assert active_capture_region(cfg) is not None

    def test_unconfirmed_region_not_active_even_with_size(self) -> None:
        cfg = OverBabelConfig(text_scope="text_region")
        reg = cfg.capture.region
        reg.enabled = True
        reg.confirmed = False
        reg.x, reg.y, reg.w, reg.h = 10, 20, 400, 300
        assert active_capture_region(cfg) is None

    def test_legacy_audio_region_migration(self) -> None:
        data = _migrate_config_data({"work_mode": "audio_region", "audio": {"enabled": False}})
        assert data["text_scope"] == "text_region"
        assert data["audio"]["enabled"] is True


class TestRuntimePolicyGuards:
    """Regressions that caused full-screen flicker or missing OCR."""

    def test_audio_does_not_enable_vision_grpc(self) -> None:
        assert should_use_grpc_vision(cli_use_grpc=False) is False
        assert should_use_grpc_vision(cli_use_grpc=True) is True

    def test_audio_grpc_only_when_enabled(self) -> None:
        cfg = OverBabelConfig()
        assert should_use_grpc_audio(cfg) is False
        cfg.audio.enabled = True
        assert should_use_grpc_audio(cfg) is True

    def test_mode_region_never_raw_roi_boxes(self) -> None:
        cfg = OverBabelConfig(text_scope="text_region")
        cfg.preview.show_roi_boxes = True
        cfg.overlay.show_roi_boxes = True
        assert should_show_raw_roi_boxes(cfg, debug_raw_rois=False) is False

    def test_mode_full_respects_roi_debug_flag(self) -> None:
        cfg = OverBabelConfig(text_scope="text_full")
        cfg.preview.show_roi_boxes = True
        assert should_show_raw_roi_boxes(cfg, debug_raw_rois=False) is True


class TestCaptureRegionPipeline:
    """Diff / OCR must stay inside user rectangle."""

    def test_clip_rois_discards_outside(self) -> None:
        zone = RegionOfInterest(100, 100, 200, 150)
        rois = [
            RegionOfInterest(10, 10, 50, 40),
            RegionOfInterest(120, 110, 80, 30),
        ]
        out = clip_rois_to_capture_region(rois, zone)
        assert len(out) == 1
        assert out[0].x >= 100

    def test_pipeline_ignores_changes_outside_crop(self) -> None:
        h, w = 240, 320
        base = np.zeros((h, w, 3), dtype=np.uint8)
        base[50:70, 40:80] = 255  # inside capture region
        base[180:210, 250:300] = 255  # outside capture region

        class _Cap:
            def __init__(self) -> None:
                self.frame = base.copy()

            def grab(self) -> np.ndarray:
                return self.frame

            def close(self) -> None:
                pass

        cap = _Cap()
        region = RegionOfInterest(10, 10, 120, 100)
        pipe = VisionPipeline(cap, min_roi_area=40, capture_region=region)  # type: ignore[arg-type]
        assert pipe.tick() is False
        cap.frame = base.copy()
        cap.frame[180:210, 250:300] = 0  # change only outside region
        assert pipe.tick() is False
        cap.frame[55:65, 50:60] = 0  # change inside region
        assert pipe.tick() is True


class TestOverlayCoordinates:
    def test_global_rect_scales_by_dpr(self) -> None:
        class _Screen:
            devicePixelRatio = lambda self: 2.0  # noqa: N805
            def geometry(self) -> QRect:
                return QRect(0, 0, 1920, 1080)

        rect = QRect(100, 200, 80, 60)
        roi = global_rect_to_capture_region(rect, _Screen())  # type: ignore[arg-type]
        assert roi.x == 200
        assert roi.y == 400
        assert roi.w == 160
        assert roi.h == 120

    def test_widget_rect_scales_by_dpr(self) -> None:
        roi = widget_rect_to_capture_region(QRect(50, 90, 100, 40), dpr=1.5)
        assert roi.x == 75
        assert roi.w == 150


class TestLabelStabilizer:
    def test_requires_min_hits_or_long_text(self) -> None:
        from overbabel_vision.pipeline import OverlayLabel

        stab = LabelStabilizer(hold_seconds=5.0, min_hits=2, max_visible=4)
        lb = OverlayLabel(
            tag="OCR",
            text="short",
            roi=RegionOfInterest(10, 10, 100, 40),
        )
        stab.push([lb])
        assert stab.snapshot() == []
        stab.push([lb])
        assert len(stab.snapshot()) == 1


class TestQuietModeTuning:
    def test_region_mode_lowers_fps_when_quiet(self) -> None:
        cfg = OverBabelConfig()
        apply_user_choices(cfg, text_scope="text_region", audio=False, quiet_mode=True)
        assert cfg.capture.fps_cap <= 6
        assert cfg.capture.max_rois_per_frame <= 4

    def test_clear_region_resets_all_fields(self) -> None:
        reg = OverBabelConfig().capture.region
        write_region_to_settings(reg, RegionOfInterest(1, 2, 300, 200))
        clear_capture_region(reg)
        assert reg.confirmed is False
        assert reg.w == 0
