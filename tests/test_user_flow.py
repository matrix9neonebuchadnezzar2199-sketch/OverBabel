from overbabel_core.config.schema import OverBabelConfig
from overbabel_core.config.user_flow import should_show_region_picker


def test_should_pick_after_welcome_for_region_mode() -> None:
    cfg = OverBabelConfig(text_scope="text_region")
    cfg.capture.region.confirmed = True
    cfg.capture.region.w = 200
    cfg.capture.region.h = 100
    assert should_show_region_picker(cfg, after_welcome=True) is True


def test_should_not_pick_after_welcome_for_full_mode() -> None:
    cfg = OverBabelConfig(text_scope="text_full")
    assert should_show_region_picker(cfg, after_welcome=True) is False
