"""OCR + translate ROI processing."""

from __future__ import annotations

import numpy as np

from overbabel_core.roi import RegionOfInterest
from overbabel_vision.cache import TranslationCache
from overbabel_vision.ocr.base import OcrEngine
from overbabel_vision.pipeline import OverlayLabel
from overbabel_vision.translate.base import Translator


class VisionProcessor:
    def __init__(
        self,
        ocr: OcrEngine,
        translator: Translator,
        *,
        src: str = "en",
        tgt: str = "ja",
        cache_size: int = 2048,
    ) -> None:
        self._ocr = ocr
        self._translator = translator
        self._src = src
        self._tgt = tgt
        self._cache = TranslationCache(maxsize=cache_size)

    def process(
        self,
        frame: np.ndarray,
        rois: list[RegionOfInterest],
        *,
        max_rois: int = 12,
    ) -> list[OverlayLabel]:
        if not rois:
            return []
        rois = sorted(rois, key=lambda r: r.area, reverse=True)[:max_rois]
        ocr_results = self._ocr.detect(frame, rois)
        if not ocr_results:
            return []
        texts = [r.text for r in ocr_results]

        def _translate(batch: list[str]) -> list[str]:
            return self._translator.translate(batch, self._src, self._tgt)

        translated = self._cache.translate_many(texts, self._src, self._tgt, _translate)
        labels: list[OverlayLabel] = []
        for ocr_r, tr in zip(ocr_results, translated, strict=True):
            labels.append(
                OverlayLabel(
                    tag="OCR",
                    text=tr,
                    roi=ocr_r.bbox,
                )
            )
        return labels
