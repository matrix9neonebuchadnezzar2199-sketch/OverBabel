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
