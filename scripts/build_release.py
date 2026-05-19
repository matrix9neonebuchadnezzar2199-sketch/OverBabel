#!/usr/bin/env python3
"""Build PyInstaller onedir distribution."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    spec = root / "overbabel.spec"
    cmd = [sys.executable, "-m", "PyInstaller", str(spec), "--noconfirm"]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=root)
    print("Output: dist/overbabel/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
