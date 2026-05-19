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
    _fix_grpc_imports(out_dir)
    return 0


def _fix_grpc_imports(out_dir: Path) -> None:
    """Rewrite protoc's bare imports to package-relative imports."""
    for path in out_dir.glob("*_pb2_grpc.py"):
        text = path.read_text(encoding="utf-8")
        text = text.replace("import audio_pb2", "from overbabel_core.ipc import audio_pb2")
        text = text.replace("import vision_pb2", "from overbabel_core.ipc import vision_pb2")
        path.write_text(text, encoding="utf-8")
    for path in out_dir.glob("*_pb2.py"):
        text = path.read_text(encoding="utf-8")
        if "from overbabel_core.ipc" not in text:
            pass  # pb2 files have no cross-imports in our protos
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
