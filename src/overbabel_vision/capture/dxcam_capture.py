"""DXGI capture via dxcam (Windows)."""

from __future__ import annotations

import numpy as np

from overbabel_core.utils import get_logger
from overbabel_vision.capture.base import ScreenCapture

_log = get_logger("vision.capture")


class DxcamCapture(ScreenCapture):
    def __init__(self, *, monitor_index: int = 0, fps_cap: int = 30) -> None:
        import dxcam

        self._camera = dxcam.create(output_idx=monitor_index)
        self._camera.start(target_fps=min(fps_cap, 60))
        _log.info("capture.dxcam.start", monitor=monitor_index, fps=fps_cap)

    def grab(self) -> np.ndarray | None:
        frame = self._camera.get_latest_frame()
        if frame is None:
            return None
        # dxcam returns RGB; OpenCV expects BGR
        return frame[:, :, ::-1].copy()

    def close(self) -> None:
        self._camera.stop()
        _log.info("capture.dxcam.stop")


def create_capture(*, monitor_index: int = 0, fps_cap: int = 30) -> ScreenCapture:
    """Instantiate dxcam or raise ImportError."""
    return DxcamCapture(monitor_index=monitor_index, fps_cap=fps_cap)
