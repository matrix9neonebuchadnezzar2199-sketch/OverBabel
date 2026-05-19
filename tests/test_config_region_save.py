from overbabel_core.config.loader import load_config, save_config
from overbabel_core.config.schema import OverBabelConfig
from overbabel_core.config.region_util import write_region_to_settings
from overbabel_core.roi import RegionOfInterest


def test_region_roundtrip_in_toml(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "overbabel_core.config.loader.get_config_path",
        lambda: tmp_path / "config.toml",
    )
    cfg = OverBabelConfig(text_scope="text_region")
    write_region_to_settings(cfg.capture.region, RegionOfInterest(120, 340, 640, 280))
    save_config(cfg)
    loaded = load_config()
    assert loaded.capture.region.w == 640
    assert loaded.capture.region.h == 280
    assert loaded.capture.region.x == 120
    assert loaded.capture.region.confirmed is True
