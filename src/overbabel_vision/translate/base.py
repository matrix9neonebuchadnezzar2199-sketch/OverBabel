from __future__ import annotations

from abc import ABC, abstractmethod


class Translator(ABC):
    @abstractmethod
    def translate(self, texts: list[str], src: str, tgt: str) -> list[str]:
        pass
