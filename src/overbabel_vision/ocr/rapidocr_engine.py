from __future__ import annotations

import numpy as np

from overbabel_core.roi import RegionOfInterest
from overbabel_core.utils import get_logger
from overbabel_vision.ocr.base import OcrEngine, OcrResult

_log = get_logger("vision.ocr")


class RapidOcrEngine(OcrEngine):
    def __init__(self) -> None:
        from rapidocr_onnxruntime import RapidOCR

        self._engine = RapidOCR()
        _log.info("ocr.rapidocr.ready")

    def detect(self, image: np.ndarray, rois: list[RegionOfInterest]) -> list[OcrResult]:
        if not rois:
            return []
        out: list[OcrResult] = []
        for roi in rois:
            crop = image[roi.y : roi.y + roi.h, roi.x : roi.x + roi.w]
            if crop.size == 0:
                continue
            result, _ = self._engine(crop)
            if not result:
                continue
            texts = [line[1] for line in result if len(line) > 1]
            confs = [float(line[2]) for line in result if len(line) > 2]
            text = " ".join(texts).strip()
            if not text:
                continue
            conf = sum(confs) / len(confs) if confs else 0.0
            out.append(OcrResult(bbox=roi, text=text, confidence=conf))
        return out


class StubOcrEngine(OcrEngine):
    """CI / no-model fallback."""

    def detect(self, image: np.ndarray, rois: list[RegionOfInterest]) -> list[OcrResult]:
        return [OcrResult(bbox=r, text="Hello world", confidence=1.0) for r in rois[:3]]


def create_ocr_engine(engine: str) -> OcrEngine:
    if engine == "stub":
        return StubOcrEngine()
    try:
        return RapidOcrEngine()
    except Exception as exc:
        _log.warning("ocr.fallback_stub", error=str(exc))
        return StubOcrEngine()
