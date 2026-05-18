#!/usr/bin/env python3
"""Generate Python gRPC stubs from proto/ (requires grpcio-tools)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    proto_dir = root / "proto"
    out_dir = root / "src" / "overbabel_core" / "ipc"
    out_dir.mkdir(parents=True, exist_ok=True)

    protos = sorted(proto_dir.glob("*.proto"))
    if not protos:
        print("No .proto files found.", file=sys.stderr)
        return 1

    cmd = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"-I{proto_dir}",
        f"--python_out={out_dir}",
        f"--grpc_python_out={out_dir}",
        *[str(p) for p in protos],
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
