"""Hold translation labels on screen to avoid flicker from per-frame diff noise."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from overbabel_vision.pipeline import OverlayLabel


@dataclass
class _Track:
    label: OverlayLabel
    last_seen: float
    hits: int = 1


@dataclass
class LabelStabilizer:
    """Merge rapid vision updates into a steady overlay list."""

    hold_seconds: float = 1.5
    min_hits: int = 2
    max_visible: int = 6
    _tracks: dict[str, _Track] = field(default_factory=dict)

    def push(self, labels: list[OverlayLabel]) -> None:
        now = time.monotonic()
        for lb in labels:
            key = self._key(lb)
            if key in self._tracks:
                tr = self._tracks[key]
                tr.last_seen = now
                tr.hits += 1
                tr.label = lb
            else:
                self._tracks[key] = _Track(label=lb, last_seen=now, hits=1)
        expired = [k for k, tr in self._tracks.items() if now - tr.last_seen > self.hold_seconds]
        for k in expired:
            del self._tracks[k]

    def snapshot(self) -> list[OverlayLabel]:
        visible = [
            tr.label
            for tr in self._tracks.values()
            if tr.hits >= self.min_hits or (tr.hits >= 1 and len(tr.label.text) >= 6)
        ]
        visible.sort(key=lambda lb: lb.roi.y)
        return visible[: self.max_visible]

    @staticmethod
    def _key(lb: OverlayLabel) -> str:
        r = lb.roi
        gx = r.x // 64
        gy = r.y // 48
        text_key = lb.text.strip()[:48]
        return f"{gx}:{gy}:{text_key}"
