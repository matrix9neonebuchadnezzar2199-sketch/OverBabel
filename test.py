#!/usr/bin/env python3
"""OverBabel 動作チェック（回帰テストランナー）。

コードを直すたびに実行してください:

    python test.py

区間だけ:
    python test.py --only user-flow
    python test.py --only pipeline

フル pytest（遅い・GUI 含む）:
    python test.py --full
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence

# (表示名, pytest パス)
SECTIONS: list[tuple[str, str]] = [
    ("user-flow", "tests/regression/test_operational_checklist.py::TestUserSelectionFlow"),
    ("policy", "tests/regression/test_operational_checklist.py::TestRuntimePolicyGuards"),
    ("pipeline", "tests/regression/test_operational_checklist.py::TestCaptureRegionPipeline"),
    ("overlay", "tests/regression/test_operational_checklist.py::TestOverlayCoordinates"),
    ("stabilizer", "tests/regression/test_operational_checklist.py::TestLabelStabilizer"),
    ("quiet", "tests/regression/test_operational_checklist.py::TestQuietModeTuning"),
    ("regression-file", "tests/regression/test_operational_checklist.py"),
    ("user-flow-unit", "tests/test_user_flow.py"),
    ("work-modes", "tests/test_work_modes.py"),
    ("region-save", "tests/test_config_region_save.py"),
    ("pipeline-crop", "tests/test_pipeline_region_crop.py"),
    ("roi-filter", "tests/test_roi_filter.py"),
    ("label-hold", "tests/test_label_stabilizer.py"),
    ("unit", "tests/unit"),
]

FULL_MARKERS = "not integration and not gpu and not slow"


def _run_pytest(targets: Sequence[str], *, verbose: bool) -> int:
    cmd = [sys.executable, "-m", "pytest", *targets]
    if verbose:
        cmd.append("-v")
    else:
        cmd.extend(["-q", "--tb=short"])
    cmd.extend(["-m", FULL_MARKERS, "--strict-markers"])
    print("$", " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OverBabel operational regression check")
    parser.add_argument(
        "--only",
        choices=[name for name, _ in SECTIONS],
        help="Run a single section (see test.py header for names).",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose pytest output.")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run all tests under tests/ (excluding integration/gpu/slow).",
    )
    args = parser.parse_args(argv)

    if args.full:
        print("=== OverBabel FULL test suite ===", flush=True)
        return _run_pytest(["tests"], verbose=args.verbose)

    if args.only:
        mapping = dict(SECTIONS)
        target = mapping.get(args.only)
        if target is None:
            print(f"Unknown section: {args.only}", file=sys.stderr)
            return 2
        print(f"=== OverBabel check: {args.only} ===", flush=True)
        code = _run_pytest([target], verbose=args.verbose)
        print("=== PASS ===" if code == 0 else "=== FAIL ===", flush=True)
        return code

    print("=== OverBabel operational regression ===", flush=True)
    failed: list[str] = []
    for name, target in SECTIONS:
        print(f"\n--- [{name}] ---", flush=True)
        code = _run_pytest([target], verbose=args.verbose)
        if code != 0:
            failed.append(name)

    print("\n=== Summary ===", flush=True)
    if failed:
        print("FAILED sections:", ", ".join(failed), flush=True)
        return 1
    print("All sections passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
