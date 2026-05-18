# Changelog

All notable changes to OverBabel will be documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Phase 0: project scaffolding, CI, linting, type-check, license, docs skeleton.
- Phase 1: transparent click-through overlay on primary monitor (PyQt6).
- System tray with overlay toggle / quit, balloon notification on startup.
- Global hotkey `Ctrl+Alt+T` to toggle overlay (configurable via config.toml).
- `--debug-boxes` CLI flag to render mock-style red-bordered translation samples.
- Offscreen smoke tests for overlay / tray / hotkey manager.
