"""Translation LRU cache keyed by xxhash."""

from __future__ import annotations

import xxhash
from cachetools import LRUCache


class TranslationCache:
    def __init__(self, maxsize: int = 2048) -> None:
        self._cache: LRUCache[str, str] = LRUCache(maxsize=maxsize)

    @staticmethod
    def _key(text: str, src: str, tgt: str) -> str:
        payload = f"{src}|{tgt}|{text}"
        return xxhash.xxh64(payload.encode("utf-8")).hexdigest()

    def get(self, text: str, src: str, tgt: str) -> str | None:
        return self._cache.get(self._key(text, src, tgt))

    def put(self, text: str, src: str, tgt: str, translated: str) -> None:
        self._cache[self._key(text, src, tgt)] = translated

    def translate_many(
        self,
        texts: list[str],
        src: str,
        tgt: str,
        fn,
    ) -> list[str]:
        """Return translations, calling ``fn(missing)`` for cache misses."""
        results: list[str | None] = [None] * len(texts)
        missing_idx: list[int] = []
        for i, t in enumerate(texts):
            hit = self.get(t, src, tgt)
            if hit is not None:
                results[i] = hit
            else:
                missing_idx.append(i)
        if missing_idx:
            unique = list(dict.fromkeys(texts[i] for i in missing_idx))
            fresh = fn(unique)
            mapping = dict(zip(unique, fresh, strict=True))
            for i in missing_idx:
                tr = mapping[texts[i]]
                results[i] = tr
                self.put(texts[i], src, tgt, tr)
        return [r if r is not None else "" for r in results]
