"""Shared region-of-interest types for vision / overlay."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegionOfInterest:
    """Screen-space bounding box in physical pixels."""

    x: int
    y: int
    w: int
    h: int

    @property
    def area(self) -> int:
        return self.w * self.h

    def intersects(self, other: RegionOfInterest) -> bool:
        return (
            self.x < other.x + other.w
            and self.x + self.w > other.x
            and self.y < other.y + other.h
            and self.y + self.h > other.y
        )

    def clip(self, other: RegionOfInterest) -> RegionOfInterest | None:
        """Intersection with *other*, or None if disjoint."""
        if not self.intersects(other):
            return None
        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.x + self.w, other.x + other.w)
        y2 = min(self.y + self.h, other.y + other.h)
        return RegionOfInterest(x1, y1, x2 - x1, y2 - y1)
