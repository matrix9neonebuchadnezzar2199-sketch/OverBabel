from __future__ import annotations

import numpy as np

from overbabel_core.roi import RegionOfInterest
from overbabel_vision.ocr.rapidocr_engine import StubOcrEngine
from overbabel_vision.processor import VisionProcessor
from overbabel_vision.translate.opus_mt import StubTranslator


def test_processor_stub_pipeline() -> None:
    proc = VisionProcessor(StubOcrEngine(), StubTranslator(), src="en", tgt="ja")
    frame = np.zeros((200, 200, 3), dtype=np.uint8)
    rois = [RegionOfInterest(x=10, y=10, w=80, h=40)]
    labels = proc.process(frame, rois, subtitle_band=False)
    assert labels
    assert labels[0].text
