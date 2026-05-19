"""Application lifecycle for OverBabel UI."""

from __future__ import annotations

import os
import signal
import sys
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication

from overbabel_core.config.loader import load_config, save_config
from overbabel_core.utils import get_logger, setup_logging
from overbabel_ui.audio_client import AudioGrpcClient
from overbabel_ui.hotkey.manager import HotkeyManager
from overbabel_ui.ipc_client.vision_client import VisionGrpcClient
from overbabel_ui.onboarding import OnboardingDialog
from overbabel_ui.overlay.window import OverlayWindow
from overbabel_ui.process_manager import ManagedProcess
from overbabel_ui.settings.window import SettingsWindow
from overbabel_ui.tray.tray import OverBabelTray
from overbabel_ui.vision_worker import VisionWorker

if TYPE_CHECKING:
    from overbabel_core.config.schema import OverBabelConfig


class OverBabelApp(QObject):
    overlay_toggle_requested = pyqtSignal()

    def __init__(
        self,
        *,
        debug_boxes: bool = False,
        live_capture: bool = True,
        use_grpc: bool = False,
    ) -> None:
        super().__init__()
        self._log = get_logger("ui.app")
        self._debug_boxes = debug_boxes
        self._live_capture = live_capture
        self._use_grpc = use_grpc
        self._config: OverBabelConfig = load_config()

        if not self._config.onboarding.completed:
            dlg = OnboardingDialog(self._config)
            if dlg.exec():
                dlg.apply(self._config)
                save_config(self._config)
        else:
            save_config(self._config)

        self._qapp = QApplication.instance() or QApplication(sys.argv)
        assert isinstance(self._qapp, QApplication)
        self._qapp.setQuitOnLastWindowClosed(False)
        self._qapp.setApplicationName("OverBabel")

        live = live_capture and (self._config.capture.enabled or debug_boxes)
        self._overlay = OverlayWindow(
            debug_boxes=debug_boxes and not live,
            live_mode=live,
        )
        self._tray = OverBabelTray(parent=self)
        self._tray.set_settings_enabled(True)
        self._hotkeys = HotkeyManager(
            bindings={
                self._config.hotkey.toggle_overlay: self.request_toggle_overlay,
            }
        )

        self._vision_worker: VisionWorker | None = None
        self._vision_grpc: VisionGrpcClient | None = None
        self._audio_grpc: AudioGrpcClient | None = None
        self._vision_proc = ManagedProcess("vision")
        self._audio_proc = ManagedProcess("audio")
        self._settings: SettingsWindow | None = None

        self.overlay_toggle_requested.connect(self._on_toggle_overlay)
        self._tray.toggle_overlay_requested.connect(self.request_toggle_overlay)
        self._tray.settings_requested.connect(self._open_settings)
        self._tray.quit_requested.connect(self.quit)

        signal.signal(signal.SIGINT, lambda *_: self.quit())
        self._sigint_timer = QTimer(self)
        self._sigint_timer.start(100)
        self._sigint_timer.timeout.connect(lambda: None)

        if live and not use_grpc:
            self._start_inline_vision()
        elif live and use_grpc:
            self._start_grpc_vision()

        if use_grpc and self._config.audio.enabled:
            self._start_grpc_audio()

    def _start_inline_vision(self) -> None:
        from overbabel_vision.capture.dxcam_capture import create_capture
        from overbabel_vision.ocr.rapidocr_engine import create_ocr_engine
        from overbabel_vision.pipeline import VisionPipeline
        from overbabel_vision.processor import VisionProcessor
        from overbabel_vision.translate.opus_mt import create_translator

        try:
            cap = create_capture(
                monitor_index=self._config.capture.monitor_index,
                fps_cap=self._config.capture.fps_cap,
            )
        except Exception as exc:
            self._log.warning("vision.capture_unavailable", error=str(exc))
            return

        ocr = create_ocr_engine(os.environ.get("OVERBABEL_OCR_ENGINE", self._config.ocr.engine))
        translator = create_translator(
            self._config.translate.engine,
            self._config.translate.model_id,
        )
        processor = VisionProcessor(
            ocr,
            translator,
            src=self._config.source_language,
            tgt=self._config.target_language,
            cache_size=self._config.performance.cache_size,
        )

        pipeline = VisionPipeline(
            cap,
            diff_threshold=self._config.capture.diff_threshold,
            min_roi_area=self._config.capture.min_roi_area,
            process_rois=processor.process,
        )
        self._vision_worker = VisionWorker(
            pipeline,
            fps_cap=self._config.capture.fps_cap,
        )
        self._vision_worker.labels_updated.connect(self._overlay.set_labels)
        if self._config.preview.show_roi_boxes:
            self._vision_worker.rois_updated.connect(self._overlay.set_rois)

    def _start_grpc_vision(self) -> None:
        self._vision_proc.start("overbabel_vision.server")
        self._vision_grpc = VisionGrpcClient(port=self._config.grpc.vision_port)
        self._vision_grpc.labels_updated.connect(self._overlay.set_labels)

    def _start_grpc_audio(self) -> None:
        self._audio_proc.start("overbabel_audio.server")
        self._audio_grpc = AudioGrpcClient(port=self._config.grpc.audio_port)
        self._audio_grpc.subtitle_updated.connect(self._on_audio_subtitle)

    @pyqtSlot(str)
    def _on_audio_subtitle(self, text: str) -> None:
        from overbabel_core.roi import RegionOfInterest
        from overbabel_vision.pipeline import OverlayLabel

        w, h = self._overlay.width(), self._overlay.height()
        label = OverlayLabel(
            tag="AUDIO",
            text=text,
            roi=RegionOfInterest(x=int(w * 0.2), y=int(h * 0.9), w=int(w * 0.6), h=48),
            accent=True,
        )
        self._overlay.set_labels([label])

    def run(self) -> int:
        self._log.info("app.start", grpc=self._use_grpc, live=self._live_capture)
        self._overlay.show()
        self._tray.show()
        self._hotkeys.start()
        if self._vision_worker is not None:
            self._vision_worker.start()
        if self._vision_grpc is not None:
            self._vision_grpc.start()
        if self._audio_grpc is not None:
            self._audio_grpc.start()
        self._tray.show_message("OverBabel", "Running. Ctrl+Alt+T toggles overlay.")
        try:
            return self._qapp.exec()
        finally:
            self._stop_workers()
            self._log.info("app.exit")

    def _stop_workers(self) -> None:
        self._hotkeys.stop()
        if self._vision_worker is not None:
            self._vision_worker.stop()
            self._vision_worker.wait(3000)
        if self._vision_grpc is not None:
            self._vision_grpc.stop()
            self._vision_grpc.wait(3000)
        if self._audio_grpc is not None:
            self._audio_grpc.stop()
            self._audio_grpc.wait(3000)
        self._vision_proc.stop()
        self._audio_proc.stop()

    @pyqtSlot()
    def request_toggle_overlay(self) -> None:
        self.overlay_toggle_requested.emit()

    @pyqtSlot()
    def quit(self) -> None:
        self._log.info("app.quit_requested")
        self._stop_workers()
        self._tray.hide()
        self._overlay.close()
        if self._settings is not None:
            self._settings.close()
        self._qapp.quit()

    @pyqtSlot()
    def _on_toggle_overlay(self) -> None:
        if self._overlay.isVisible():
            self._overlay.hide()
            self._tray.set_overlay_state(False)
        else:
            self._overlay.show()
            self._tray.set_overlay_state(True)

    @pyqtSlot()
    def _open_settings(self) -> None:
        self._settings = SettingsWindow()
        self._settings.config_saved.connect(self._on_config_saved)
        self._settings.show()

    @pyqtSlot(object)
    def _on_config_saved(self, config: object) -> None:
        self._config = config  # type: ignore[assignment]
        self._log.info("config.saved")


def run_app(
    *,
    debug_boxes: bool = False,
    live_capture: bool = True,
    use_grpc: bool = False,
) -> int:
    setup_logging()
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = OverBabelApp(
        debug_boxes=debug_boxes,
        live_capture=live_capture,
        use_grpc=use_grpc,
    )
    return app.run()
