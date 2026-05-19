from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from overbabel_core.roi import RegionOfInterest


@dataclass(frozen=True)
class OcrResult:
    bbox: RegionOfInterest
    text: str
    confidence: float


class OcrEngine(ABC):
    @abstractmethod
    def detect(self, image: np.ndarray, rois: list[RegionOfInterest]) -> list[OcrResult]:
        """Run OCR on full image, optionally limited to ROIs."""
