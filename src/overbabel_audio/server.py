"""gRPC audio subtitle server (Phase 6 stub + optional whisper)."""

from __future__ import annotations

import os
import time
from concurrent import futures

import grpc

from overbabel_core.utils import get_logger, setup_logging

_log = get_logger("audio.server")


def _serve(port: int) -> None:
    from overbabel_core.ipc import audio_pb2, audio_pb2_grpc

    demo_lines = [
        ("Wind, carry us away...", "風よ、我らを連れて行け…"),
        ("Captain, the storm approaches.", "船長、嵐が近づいている。"),
    ]
    idx = 0

    class Servicer(audio_pb2_grpc.AudioServiceServicer):
        def StreamSubtitles(self, request, context):  # noqa: N802
            nonlocal idx
            while context.is_active():
                en, ja = demo_lines[idx % len(demo_lines)]
                idx += 1
                yield audio_pb2.SubtitleBatch(text=en, translated=ja)
                time.sleep(5.0)

        def Ping(self, request, context):  # noqa: N802
            return audio_pb2.PingReply(ok=True)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    audio_pb2_grpc.add_AudioServiceServicer_to_server(Servicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    _log.info("audio.server.listen", port=port)
    server.wait_for_termination()


def main() -> None:
    setup_logging()
    port = int(os.environ.get("OVERBABEL_AUDIO_GRPC_PORT", "7322"))
    _serve(port)


if __name__ == "__main__":
    main()
