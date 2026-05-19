"""Vision gRPC client streaming translations to overlay."""

from __future__ import annotations

import grpc
from PyQt6.QtCore import QThread, pyqtSignal

from overbabel_core.roi import RegionOfInterest
from overbabel_vision.pipeline import OverlayLabel


class VisionGrpcClient(QThread):
    labels_updated = pyqtSignal(list)

    def __init__(self, host: str = "localhost", port: int = 7321) -> None:
        super().__init__()
        self._target = f"{host}:{port}"
        self._running = True

    def run(self) -> None:
        from overbabel_core.ipc import vision_pb2, vision_pb2_grpc

        channel = grpc.insecure_channel(self._target)
        stub = vision_pb2_grpc.VisionServiceStub(channel)
        request = vision_pb2.StreamRequest(enable_ocr=True)
        try:
            for batch in stub.StreamTranslations(request):
                if not self._running:
                    break
                labels = [
                    OverlayLabel(
                        tag=item.tag or "OCR",
                        text=item.text,
                        roi=RegionOfInterest(
                            x=item.x,
                            y=item.y,
                            w=item.w,
                            h=item.h,
                        ),
                        accent=item.accent,
                    )
                    for item in batch.items
                ]
                if labels:
                    self.labels_updated.emit(labels)
        except grpc.RpcError:
            pass
        finally:
            channel.close()

    def stop(self) -> None:
        self._running = False
