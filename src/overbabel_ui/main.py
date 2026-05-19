"""OverBabel UI entry point."""

from __future__ import annotations

import argparse
import sys

from overbabel_core import __version__


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="overbabel", description="OverBabel overlay")
    p.add_argument(
        "--debug-boxes",
        action="store_true",
        help="Show mock debug samples (no capture).",
    )
    p.add_argument(
        "--no-capture",
        action="store_true",
        help="Disable live capture pipeline.",
    )
    p.add_argument(
        "--use-grpc",
        action="store_true",
        help="Use vision/audio gRPC child processes.",
    )
    p.add_argument("--version", action="store_true", help="Print version and exit.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    if args.version:
        print(f"OverBabel {__version__}")
        return 0

    from overbabel_ui.app import run_app

    return run_app(
        debug_boxes=args.debug_boxes,
        live_capture=not args.no_capture,
        use_grpc=args.use_grpc,
    )


if __name__ == "__main__":
    sys.exit(main())
