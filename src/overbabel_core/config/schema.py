"""Pydantic configuration schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ProfileId = Literal["A", "B", "C", "D"]
OcrEngineId = Literal["rapidocr", "winocr", "tesseract", "stub"]
TranslateEngineId = Literal["opus_mt", "nllb", "llm_gguf", "stub"]
TextScopeId = Literal["text_full", "text_region"]


class CaptureRegionSettings(BaseModel):
    """Monitor-local rectangle (pixels) for region-limited modes."""

    enabled: bool = False
    x: int = Field(default=0, ge=0)
    y: int = Field(default=0, ge=0)
    w: int = Field(default=0, ge=0)
    h: int = Field(default=0, ge=0)


class CaptureSettings(BaseModel):
    enabled: bool = True
    fps_cap: int = Field(default=30, ge=1, le=60)
    diff_threshold: float = Field(default=30.0, ge=1.0, le=255.0)
    min_roi_area: int = Field(default=6000, ge=16)
    max_rois_per_frame: int = Field(default=8, ge=1, le=64)
    subtitle_band_only: bool = True
    monitor_index: int = Field(default=0, ge=0)
    region: CaptureRegionSettings = Field(default_factory=CaptureRegionSettings)


class AudioSettings(BaseModel):
    enabled: bool = False
    device_id: str | None = None
    sample_rate: int = Field(default=16000, ge=8000)
    vad_aggressiveness: float = Field(default=0.5, ge=0.0, le=1.0)


class OcrSettings(BaseModel):
    engine: OcrEngineId = "rapidocr"
    language_packs: list[str] = Field(default_factory=lambda: ["en", "ja"])


class TranslateSettings(BaseModel):
    engine: TranslateEngineId = "opus_mt"
    model_id: str = "Helsinki-NLP/opus-mt-en-ja"
    quantization: str = "int8"


class ModelSettings(BaseModel):
    auto_update: bool = False


class OverlaySettings(BaseModel):
    click_through: bool = True
    font_size: int = Field(default=14, ge=8, le=48)
    background_opacity: float = Field(default=0.55, ge=0.0, le=1.0)
    text_color: str = "#ffffff"
    show_roi_boxes: bool = False


class PreviewSettings(BaseModel):
    show_roi_boxes: bool = False
    log_fps: bool = False


class PerformanceSettings(BaseModel):
    ocr_workers: int = Field(default=2, ge=1, le=8)
    translate_workers: int = Field(default=2, ge=1, le=8)
    cache_size: int = Field(default=2048, ge=128)
    quiet_mode: bool = True
    idle_fps_cap: int = Field(default=4, ge=1, le=15)


class HotkeySettings(BaseModel):
    toggle_overlay: str = "<ctrl>+<alt>+t"
    open_settings: str = "<ctrl>+<alt>+o"


class GrpcSettings(BaseModel):
    vision_enabled: bool = False
    vision_port: int = Field(default=7321, ge=1024, le=65535)
    audio_port: int = Field(default=7322, ge=1024, le=65535)


class OnboardingSettings(BaseModel):
    completed: bool = False


class WelcomeSettings(BaseModel):
    show_on_startup: bool = True


class OverBabelConfig(BaseModel):
    schema_version: int = Field(default=3, ge=1)
    text_scope: TextScopeId = "text_region"
    active_profile: ProfileId = "A"
    source_language: str = "en"
    target_language: str = "ja"
    ui_language: str = "ja"
    capture: CaptureSettings = Field(default_factory=CaptureSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    ocr: OcrSettings = Field(default_factory=OcrSettings)
    translate: TranslateSettings = Field(default_factory=TranslateSettings)
    models: ModelSettings = Field(default_factory=ModelSettings)
    overlay: OverlaySettings = Field(default_factory=OverlaySettings)
    preview: PreviewSettings = Field(default_factory=PreviewSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)
    hotkey: HotkeySettings = Field(default_factory=HotkeySettings)
    grpc: GrpcSettings = Field(default_factory=GrpcSettings)
    onboarding: OnboardingSettings = Field(default_factory=OnboardingSettings)
    welcome: WelcomeSettings = Field(default_factory=WelcomeSettings)
