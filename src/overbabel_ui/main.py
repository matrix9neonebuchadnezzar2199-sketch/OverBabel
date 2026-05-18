"""PyQt6 entry point (Phase 0 placeholder; overlay in Phase 1)."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    """CLI entry for the `overbabel` console script."""
    parser = argparse.ArgumentParser(prog="overbabel", description="OverBabel UI")
    parser.parse_args(argv if argv is not None else sys.argv[1:])
    print("OverBabel: Phase 0 bootstrap. Install Phase 1 for the transparent overlay.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
