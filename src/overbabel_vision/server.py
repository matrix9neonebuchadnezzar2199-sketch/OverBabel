"""gRPC vision server (Phase 5)."""

from __future__ import annotations

import os
import sys
import time
from concurrent import futures

import grpc

from overbabel_core.config.loader import load_config
from overbabel_core.utils import get_logger, setup_logging
from overbabel_vision.capture.dxcam_capture import create_capture
from overbabel_vision.ocr.rapidocr_engine import create_ocr_engine
from overbabel_vision.pipeline import OverlayLabel, VisionPipeline
from overbabel_vision.processor import VisionProcessor
from overbabel_vision.translate.opus_mt import create_translator

_log = get_logger("vision.server")


def _serve(port: int) -> None:
    from overbabel_core.ipc import vision_pb2, vision_pb2_grpc

    cfg = load_config()
    ocr = create_ocr_engine(os.environ.get("OVERBABEL_OCR_ENGINE", cfg.ocr.engine))
    translator = create_translator(cfg.translate.engine, cfg.translate.model_id)
    processor = VisionProcessor(
        ocr,
        translator,
        src=cfg.source_language,
        tgt=cfg.target_language,
        cache_size=cfg.performance.cache_size,
    )

    try:
        capture = create_capture(
            monitor_index=cfg.capture.monitor_index,
            fps_cap=cfg.capture.fps_cap,
        )
    except Exception as exc:
        _log.error("server.capture_failed", error=str(exc))
        sys.exit(1)

    latest: list[OverlayLabel] = []

    def on_labels(labels: list[OverlayLabel]) -> None:
        latest.clear()
        latest.extend(labels)

    pipeline = VisionPipeline(
        capture,
        diff_threshold=cfg.capture.diff_threshold,
        min_roi_area=cfg.capture.min_roi_area,
        process_rois=processor.process,
        on_labels=on_labels,
    )

    class Servicer(vision_pb2_grpc.VisionServiceServicer):
        def StreamTranslations(self, request, context):  # noqa: N802
            frame_id = 0
            interval = 1.0 / max(cfg.capture.fps_cap, 1)
            while context.is_active():
                pipeline.tick()
                frame_id += 1
                items = [
                    vision_pb2.TranslationItem(
                        x=lb.roi.x,
                        y=lb.roi.y,
                        w=lb.roi.w,
                        h=lb.roi.h,
                        tag=lb.tag,
                        text=lb.text,
                        accent=lb.accent,
                    )
                    for lb in latest
                ]
                yield vision_pb2.TranslationBatch(items=items, frame_id=frame_id)
                time.sleep(interval)

        def ReloadEngine(self, request, context):  # noqa: N802
            return vision_pb2.ReloadEngineReply(ok=True, message="reload accepted")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    vision_pb2_grpc.add_VisionServiceServicer_to_server(Servicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    _log.info("server.listen", port=port)
    try:
        server.wait_for_termination()
    finally:
        pipeline.close()


def main() -> None:
    setup_logging()
    port = int(os.environ.get("OVERBABEL_VISION_GRPC_PORT", "7321"))
    _serve(port)


if __name__ == "__main__":
    main()
