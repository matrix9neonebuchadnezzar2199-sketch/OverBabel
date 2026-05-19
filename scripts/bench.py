#!/usr/bin/env python3
"""Benchmark capture + diff for ~60 seconds."""

from __future__ import annotations

import argparse
import os
import sys
import time

def main() -> int:
    parser = argparse.ArgumentParser(description="OverBabel vision bench")
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args()

    os.environ.setdefault("OVERBABEL_OCR_ENGINE", "stub")
    os.environ.setdefault("OVERBABEL_TRANSLATE_ENGINE", "stub")

    try:
        from overbabel_vision.capture.dxcam_capture import create_capture
        from overbabel_vision.pipeline import VisionPipeline
    except ImportError as exc:
        print("vision dependencies missing:", exc, file=sys.stderr)
        return 1

    roi_total = 0
    frames = 0
    t_end = time.time() + args.seconds

    try:
        cap = create_capture(fps_cap=args.fps)
    except Exception as exc:  # noqa: BLE001
        print("capture unavailable (expected in CI):", exc)
        return 0

    pipeline = VisionPipeline(
        cap,
        on_rois=lambda rois, _f: None,
    )

    print(f"bench start seconds={args.seconds} fps_cap={args.fps}")
    while time.time() < t_end:
        pipeline.tick()
        frames += 1
        roi_total = pipeline.roi_count
        time.sleep(1.0 / max(args.fps, 1))

    pipeline.close()
    print(
        f"frames={frames} rois_total={roi_total} "
        f"avg_fps={frames / max(args.seconds, 1):.2f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
