from overbabel_core.roi import RegionOfInterest
from overbabel_ui.overlay.label_stabilizer import LabelStabilizer
from overbabel_vision.pipeline import OverlayLabel


def _label(text: str, x: int = 100, y: int = 800) -> OverlayLabel:
    return OverlayLabel(tag="OCR", text=text, roi=RegionOfInterest(x, y, 200, 40))


def test_stabilizer_requires_min_hits() -> None:
    stab = LabelStabilizer(hold_seconds=5.0, min_hits=2, max_visible=4)
    stab.push([_label("hello")])
    assert stab.snapshot() == []
    stab.push([_label("hello")])
    out = stab.snapshot()
    assert len(out) == 1
    assert out[0].text == "hello"
