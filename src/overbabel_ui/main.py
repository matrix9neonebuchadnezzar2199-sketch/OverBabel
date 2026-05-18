"""OverBabel UI entry point (Phase 1).

Usage:
    python -m overbabel_ui.main                 # 透明オーバーレイ起動
    python -m overbabel_ui.main --debug-boxes   # 赤枠+ダミー翻訳テキストを表示
    python -m overbabel_ui.main --version
"""

from __future__ import annotations

import argparse
import sys

from overbabel_core import __version__


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="overbabel", description="OverBabel — realtime translation overlay")
    p.add_argument(
        "--debug-boxes",
        action="store_true",
        help="モックと同じ赤枠+ダミーラベルを描画する (Phase 1 動作確認用)。",
    )
    p.add_argument("--version", action="store_true", help="バージョンを表示して終了。")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    if args.version:
        print(f"OverBabel {__version__}")
        return 0

    # Qt 関連は引数解析後に import (--version 用の起動を軽くする)
    from overbabel_ui.app import run_app

    return run_app(debug_boxes=args.debug_boxes)


if __name__ == "__main__":
    sys.exit(main())
