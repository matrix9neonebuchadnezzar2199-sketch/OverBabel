from __future__ import annotations

from overbabel_vision.cache import TranslationCache


def test_cache_hit() -> None:
    cache = TranslationCache(maxsize=10)
    calls: list[str] = []

    def fn(batch: list[str]) -> list[str]:
        calls.extend(batch)
        return [f"#{t}" for t in batch]

    out = cache.translate_many(["a", "b", "a"], "en", "ja", fn)
    assert out == ["#a", "#b", "#a"]
    assert calls == ["a", "b"]
