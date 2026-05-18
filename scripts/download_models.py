#!/usr/bin/env python3
"""Download Hugging Face models into the user model directory (Phase 7 wiring)."""

from __future__ import annotations

from overbabel_core.config.paths import get_model_dir


def main() -> None:
    print("Model download helper: implement in Phase 3+ using huggingface_hub.")
    print("Default model root:", get_model_dir())


if __name__ == "__main__":
    main()
