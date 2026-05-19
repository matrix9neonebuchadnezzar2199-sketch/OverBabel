"""Audio gRPC client for subtitle strip."""

from __future__ import annotations

import grpc
from PyQt6.QtCore import QThread, pyqtSignal


class AudioGrpcClient(QThread):
    subtitle_updated = pyqtSignal(str)

    def __init__(self, host: str = "localhost", port: int = 7322) -> None:
        super().__init__()
        self._target = f"{host}:{port}"
        self._running = True

    def run(self) -> None:
        from overbabel_core.ipc import audio_pb2, audio_pb2_grpc

        channel = grpc.insecure_channel(self._target)
        stub = audio_pb2_grpc.AudioServiceStub(channel)
        try:
            for batch in stub.StreamSubtitles(audio_pb2.StreamRequest()):
                if not self._running:
                    break
                self.subtitle_updated.emit(batch.translated)
        except grpc.RpcError:
            pass
        finally:
            channel.close()

    def stop(self) -> None:
        self._running = False
