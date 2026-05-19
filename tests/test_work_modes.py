from overbabel_core.config.region_util import needs_region_pick, write_region_to_settings
from overbabel_core.config.schema import OverBabelConfig
from overbabel_core.config.work_modes import apply_work_mode
from overbabel_core.roi import RegionOfInterest
from overbabel_vision.roi_filter import clip_rois_to_capture_region


def test_apply_text_full_disables_region() -> None:
    cfg = OverBabelConfig()
    apply_work_mode(cfg, "text_full")
    assert cfg.capture.region.enabled is False
    assert cfg.capture.subtitle_band_only is False


def test_needs_region_pick_when_empty() -> None:
    cfg = OverBabelConfig(work_mode="text_region")
    assert needs_region_pick(cfg) is True
    write_region_to_settings(cfg.capture.region, RegionOfInterest(10, 10, 200, 100))
    assert needs_region_pick(cfg) is False


def test_clip_rois_to_region() -> None:
    region = RegionOfInterest(100, 100, 300, 200)
    rois = [RegionOfInterest(50, 50, 80, 40), RegionOfInterest(150, 120, 100, 40)]
    out = clip_rois_to_capture_region(rois, region)
    assert len(out) == 1
    assert out[0].x >= 100
