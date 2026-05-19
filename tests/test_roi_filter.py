from overbabel_core.roi import RegionOfInterest
from overbabel_vision.roi_filter import filter_translation_candidates


def test_subtitle_band_keeps_bottom_wide_regions() -> None:
    rois = [
        RegionOfInterest(50, 50, 40, 40),  # tiny top chrome
        RegionOfInterest(120, 900, 400, 36),  # bottom subtitle line
    ]
    out = filter_translation_candidates(rois, 1920, 1080, subtitle_band=True)
    assert len(out) == 1
    assert out[0].y == 900
