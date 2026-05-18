"""Pydantic configuration schema (expanded in Phase 4)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ProfileId = Literal["A", "B", "C", "D"]


class OverlaySettings(BaseModel):
    """On-screen overlay appearance and behavior."""

    click_through: bool = True
    font_size: int = Field(default=14, ge=8, le=48)
    background_opacity: float = Field(default=0.55, ge=0.0, le=1.0)
    text_color: str = "#ffffff"


class OverBabelConfig(BaseModel):
    """Top-level application configuration (Phase 0 minimal subset)."""

    schema_version: int = Field(default=1, ge=1)
    active_profile: ProfileId = "A"
    source_language: str = "en"
    target_language: str = "ja"
    overlay: OverlaySettings = Field(default_factory=OverlaySettings)
