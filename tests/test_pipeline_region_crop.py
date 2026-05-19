import numpy as np

from overbabel_core.roi import RegionOfInterest
from overbabel_vision.pipeline import VisionPipeline


class _FakeCap:
    def __init__(self, frame: np.ndarray) -> None:
        self._frame = frame
        self._n = 0

    def grab(self) -> np.ndarray | None:
        self._n += 1
        return self._frame

    def close(self) -> None:
        pass


def test_pipeline_only_diffs_inside_capture_region() -> None:
    h, w = 200, 300
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[50:70, 40:80] = 255  # inside capture region
    frame[150:170, 220:260] = 255  # outside capture region

    cap = _FakeCap(frame)
    region = RegionOfInterest(10, 10, 120, 100)
    pipe = VisionPipeline(cap, min_roi_area=50, capture_region=region)

    assert pipe.tick() is False
    frame2 = frame.copy()
    frame2[150:170, 220:260] = 0  # change outside region only
    cap._frame = frame2
    assert pipe.tick() is False

    frame3 = frame2.copy()
    frame3[55:65, 50:60] = 0  # change inside region
    cap._frame = frame3
    assert pipe.tick() is True
