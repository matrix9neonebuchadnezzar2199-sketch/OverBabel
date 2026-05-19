from __future__ import annotations

from overbabel_core.utils import get_logger
from overbabel_vision.translate.base import Translator

_log = get_logger("vision.translate")

# Minimal en->ja map for stub / demo when models unavailable
_DEMO_MAP = {
    "hello world": "こんにちは世界",
    "hello": "こんにちは",
    "world": "世界",
    "start game": "ゲーム開始",
    "game start": "ゲーム開始",
}


class OpusMtTranslator(Translator):
    def __init__(self, model_id: str = "Helsinki-NLP/opus-mt-en-ja") -> None:
        self._model_id = model_id
        self._translator = None
        try:
            import ctranslate2  # noqa: F401

            # Lightweight path: use transformers pipeline fallback if CT2 model not cached
            from transformers import (
                pipeline,
            )

            self._pipe = pipeline("translation", model=model_id)
            _log.info("translate.opus_mt.ready", model=model_id)
        except Exception as exc:
            _log.warning("translate.opus_mt.pipeline_unavailable", error=str(exc))
            self._pipe = None

    def translate(self, texts: list[str], src: str, tgt: str) -> list[str]:
        if not texts:
            return []
        if self._pipe is not None:
            out: list[str] = []
            for t in texts:
                r = self._pipe(t, max_length=256)
                out.append(r[0]["translation_text"] if r else t)
            return out
        return [_DEMO_MAP.get(t.lower().strip(), f"[{tgt}] {t}") for t in texts]


class StubTranslator(Translator):
    def translate(self, texts: list[str], src: str, tgt: str) -> list[str]:
        return [_DEMO_MAP.get(t.lower().strip(), f"({tgt}) {t}") for t in texts]


def create_translator(engine: str, model_id: str) -> Translator:
    if engine == "stub":
        return StubTranslator()
    if engine == "opus_mt":
        return OpusMtTranslator(model_id=model_id)
    return StubTranslator()
