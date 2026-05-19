"""Application lifecycle for OverBabel UI."""

from __future__ import annotations

import os
import signal
import sys
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

from overbabel_core.config.audio_overlay import (
    audio_subtitle_roi_in_region,
    audio_subtitle_widget_rect,
)
from overbabel_core.config.loader import load_config, save_config
from overbabel_core.config.region_util import active_capture_region, write_region_to_settings
from overbabel_core.config.screen_coords import widget_rect_to_capture_region
from overbabel_core.roi import RegionOfInterest
from overbabel_core.config.user_flow import (
    should_show_raw_roi_boxes,
    should_show_region_picker,
    should_use_grpc_audio,
    should_use_grpc_vision,
)
from overbabel_core.utils import get_logger, setup_logging
from overbabel_ui.audio_client import AudioGrpcClient
from overbabel_ui.hotkey.manager import HotkeyManager
from overbabel_ui.ipc_client.vision_client import VisionGrpcClient
from overbabel_ui.overlay.label_stabilizer import LabelStabilizer
from overbabel_ui.overlay.window import OverlayWindow
from overbabel_ui.process_manager import ManagedProcess
from overbabel_ui.region_picker import RegionPickerDialog
from overbabel_ui.settings.window import SettingsWindow
from overbabel_ui.tray.tray import OverBabelTray
from overbabel_ui.vision_worker import VisionWorker
from overbabel_ui.welcome_dialog import WelcomeDialog

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
        debug_raw_rois: bool = False,
    ) -> None:
        super().__init__()
        self._log = get_logger("ui.app")
        self._debug_boxes = debug_boxes
        self._live_capture = live_capture
        self._use_grpc = use_grpc
        self._debug_raw_rois = debug_raw_rois
        self._config: OverBabelConfig = load_config()
        self._aborted = False

        # QApplication must exist before any QWidget (welcome, overlay, tray).
        self._qapp = QApplication.instance() or QApplication(sys.argv)
        assert isinstance(self._qapp, QApplication)
        self._qapp.setQuitOnLastWindowClosed(False)
        self._qapp.setApplicationName("OverBabel")

        if not self._run_startup_flow():
            self._aborted = True
            return

        # 音声だけ gRPC。画面テキスト OCR は通常どおりインライン（--use-grpc 時のみ vision gRPC）。
        self._use_grpc_vision = should_use_grpc_vision(cli_use_grpc=use_grpc)
        live = live_capture and (self._config.capture.enabled or debug_boxes)
        self._overlay = OverlayWindow(
            debug_boxes=debug_boxes and not live,
            live_mode=live,
        )
        self._overlay.set_capture_region_hint(active_capture_region(self._config))
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
        self._label_stabilizer = LabelStabilizer(hold_seconds=1.5, min_hits=2, max_visible=6)
        self._audio_label: object | None = None
        self._last_audio_text: str = ""
        self._label_paint_timer = QTimer(self)
        paint_ms = 400 if self._config.performance.quiet_mode else 250
        self._label_paint_timer.setInterval(paint_ms)
        self._label_paint_timer.timeout.connect(self._refresh_overlay_labels)

        self.overlay_toggle_requested.connect(self._on_toggle_overlay)
        self._tray.toggle_overlay_requested.connect(self.request_toggle_overlay)
        self._tray.settings_requested.connect(self._open_settings)
        self._tray.mode_change_requested.connect(self._open_welcome_menu)
        self._tray.region_pick_requested.connect(self._repick_capture_region)
        self._tray.quit_requested.connect(self.quit)

        signal.signal(signal.SIGINT, lambda *_: self.quit())
        self._sigint_timer = QTimer(self)
        self._sigint_timer.start(100)
        self._sigint_timer.timeout.connect(lambda: None)

        if live and not self._use_grpc_vision:
            self._start_inline_vision()
        elif live and self._use_grpc_vision:
            self._start_grpc_vision()

        if should_use_grpc_audio(self._config):
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

        show_raw = should_show_raw_roi_boxes(self._config, debug_raw_rois=self._debug_raw_rois)
        capture_region = active_capture_region(self._config)
        if self._config.text_scope == "text_region" and capture_region is None:
            self._log.error("vision.region_missing", hint="② requires a capture region")
            return
        if capture_region is not None:
            self._log.info(
                "vision.region_active",
                x=capture_region.x,
                y=capture_region.y,
                w=capture_region.w,
                h=capture_region.h,
            )

        def _process_rois(frame, rois):
            return processor.process(
                frame,
                rois,
                max_rois=self._config.capture.max_rois_per_frame,
                subtitle_band=self._config.capture.subtitle_band_only,
                capture_region=capture_region,
            )

        pipeline = VisionPipeline(
            cap,
            diff_threshold=self._config.capture.diff_threshold,
            min_roi_area=self._config.capture.min_roi_area,
            max_rois_per_frame=self._config.capture.max_rois_per_frame,
            process_rois=None if show_raw else _process_rois,
            capture_region=capture_region,
        )
        idle_fps = (
            self._config.performance.idle_fps_cap
            if self._config.performance.quiet_mode
            else self._config.capture.fps_cap
        )
        self._vision_worker = VisionWorker(
            pipeline,
            fps_cap=self._config.capture.fps_cap,
            idle_fps_cap=idle_fps,
        )
        if show_raw:
            self._log.warning(
                "overlay.raw_roi_mode",
                hint="赤い ROI 枠は開発用です。設定の「ROI 枠を表示」をオフにするか、--debug-roi を外してください。",
            )
            self._vision_worker.rois_updated.connect(self._overlay.set_rois)
        else:
            self._vision_worker.labels_updated.connect(self._on_vision_labels)
            self._label_paint_timer.start()

    @pyqtSlot(list)
    def _on_vision_labels(self, labels: list) -> None:
        """Vision thread -> stabilizer (main thread); paint at most ~4 Hz."""
        from overbabel_vision.pipeline import OverlayLabel

        typed = [lb for lb in labels if isinstance(lb, OverlayLabel)]
        self._label_stabilizer.push(typed)

    @pyqtSlot()
    def _refresh_overlay_labels(self) -> None:
        from overbabel_vision.pipeline import OverlayLabel

        combined: list[OverlayLabel] = list(self._label_stabilizer.snapshot())
        if isinstance(self._audio_label, OverlayLabel):
            combined.append(self._audio_label)
        combined.sort(key=lambda lb: lb.roi.y)
        self._overlay.set_labels(combined)

    def _start_grpc_vision(self) -> None:
        self._vision_proc.start("overbabel_vision.server")
        self._vision_grpc = VisionGrpcClient(port=self._config.grpc.vision_port)
        self._vision_grpc.labels_updated.connect(self._on_vision_labels)
        self._label_paint_timer.start()

    def _start_grpc_audio(self) -> None:
        self._audio_proc.start("overbabel_audio.server")
        self._audio_grpc = AudioGrpcClient(port=self._config.grpc.audio_port)
        self._audio_grpc.subtitle_updated.connect(self._on_audio_subtitle)

    def _audio_subtitle_roi(self) -> RegionOfInterest:
        band = self._config.audio.subtitle_band
        region = active_capture_region(self._config)
        if region is not None:
            return audio_subtitle_roi_in_region(region, band)
        w, h = self._overlay.width(), self._overlay.height()
        rect = audio_subtitle_widget_rect(w, h, band)
        return widget_rect_to_capture_region(rect, dpr=self._overlay.device_pixel_ratio)

    def _reposition_audio_label(self) -> None:
        from overbabel_vision.pipeline import OverlayLabel

        if not isinstance(self._audio_label, OverlayLabel):
            return
        self._audio_label = OverlayLabel(
            tag=self._audio_label.tag,
            text=self._audio_label.text,
            roi=self._audio_subtitle_roi(),
            accent=self._audio_label.accent,
        )
        self._refresh_overlay_labels()

    @pyqtSlot(str)
    def _on_audio_subtitle(self, text: str) -> None:
        from overbabel_vision.pipeline import OverlayLabel

        text = text.strip()
        if not text or text == self._last_audio_text:
            return
        self._last_audio_text = text
        roi = self._audio_subtitle_roi()
        self._audio_label = OverlayLabel(tag="AUDIO", text=text, roi=roi, accent=True)
        self._refresh_overlay_labels()

    def _run_startup_flow(self) -> bool:
        dirty = False
        welcome_shown = False
        if self._config.welcome.show_on_startup or not self._config.onboarding.completed:
            dlg = WelcomeDialog(self._config)
            if dlg.exec() != int(QDialog.DialogCode.Accepted):
                return False
            dlg.apply(self._config)
            dirty = True
            welcome_shown = True
        if should_show_region_picker(self._config, after_welcome=welcome_shown):
            if not self._pick_capture_region():
                return False
            dirty = True
        if dirty:
            save_config(self._config)
        return True

    def _pick_capture_region(self) -> bool:
        picker = RegionPickerDialog()
        if picker.exec() != int(QDialog.DialogCode.Accepted):
            QMessageBox.warning(
                None,
                "OverBabel",
                "範囲の指定が必要です。②を選んだときは矩形を囲んでから開始してください。",
            )
            return False
        region = picker.region()
        if region is None:
            QMessageBox.warning(
                None,
                "OverBabel",
                "範囲を保存できませんでした。もう一度ドラッグして囲んでください。",
            )
            return False
        write_region_to_settings(self._config.capture.region, region)
        self._log.info(
            "capture.region_set",
            x=region.x,
            y=region.y,
            w=region.w,
            h=region.h,
        )
        return True

    @pyqtSlot()
    def _repick_capture_region(self) -> None:
        if self._config.text_scope != "text_region":
            QMessageBox.information(
                None,
                "OverBabel",
                "範囲の再指定はモード②のときだけ使えます。",
            )
            return
        if not self._pick_capture_region():
            return
        save_config(self._config)
        self._overlay.set_capture_region_hint(active_capture_region(self._config))
        self._reposition_audio_label()
        self._restart_vision_pipeline()
        self._tray.show_message("OverBabel", "範囲を更新しました。")

    def _stop_vision_worker(self) -> None:
        if self._vision_worker is None:
            return
        try:
            self._vision_worker.labels_updated.disconnect(self._on_vision_labels)
        except (TypeError, RuntimeError):
            pass
        try:
            self._vision_worker.rois_updated.disconnect(self._overlay.set_rois)
        except (TypeError, RuntimeError):
            pass
        self._vision_worker.stop()
        self._vision_worker.wait(3000)
        self._vision_worker = None

    def _restart_vision_pipeline(self) -> None:
        self._stop_vision_worker()
        self._label_stabilizer = LabelStabilizer(hold_seconds=1.5, min_hits=2, max_visible=6)
        live = self._live_capture and (self._config.capture.enabled or self._debug_boxes)
        if live and not self._use_grpc_vision:
            self._start_inline_vision()
            if self._vision_worker is not None:
                self._vision_worker.start()

    @pyqtSlot()
    def _open_welcome_menu(self) -> None:
        dlg = WelcomeDialog(self._config)
        if dlg.exec() != int(QDialog.DialogCode.Accepted):
            return
        dlg.apply(self._config)
        if should_show_region_picker(self._config, after_welcome=True):
            if not self._pick_capture_region():
                return
        save_config(self._config)
        self._apply_runtime_config()
        self._tray.show_message("OverBabel", "モードを反映しました。")

    def _apply_runtime_config(self) -> None:
        """Reload overlay hint and vision/audio workers after user changed mode."""
        self._overlay.set_capture_region_hint(active_capture_region(self._config))
        self._reposition_audio_label()
        self._restart_vision_pipeline()
        if self._config.audio.enabled and self._audio_grpc is None:
            self._start_grpc_audio()
            if self._audio_grpc is not None:
                self._audio_grpc.start()
        elif not self._config.audio.enabled and self._audio_grpc is not None:
            self._audio_grpc.stop()
            self._audio_grpc.wait(3000)
            self._audio_grpc = None
            self._audio_proc.stop()
            self._audio_label = None
            self._last_audio_text = ""

    def run(self) -> int:
        if self._aborted:
            return 0
        self._log.info(
            "app.start",
            grpc_vision=self._use_grpc_vision,
            live=self._live_capture,
            text_scope=self._config.text_scope,
            audio=self._config.audio.enabled,
        )
        self._overlay.show()
        self._tray.show()
        self._hotkeys.start()
        if self._vision_worker is not None:
            self._vision_worker.start()
        if self._vision_grpc is not None:
            self._vision_grpc.start()
        if self._audio_grpc is not None:
            self._audio_grpc.start()
        scope = "① 画面全体" if self._config.text_scope == "text_full" else "② 範囲指定"
        audio = " ＋ 音声" if self._config.audio.enabled else ""
        self._tray.show_message("OverBabel", f"{scope}{audio} — Ctrl+Alt+T でオーバーレイ切替")
        try:
            return self._qapp.exec()
        finally:
            self._stop_workers()
            self._log.info("app.exit")

    def _stop_workers(self) -> None:
        self._hotkeys.stop()
        self._label_paint_timer.stop()
        self._stop_vision_worker()
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
        self._overlay.set_capture_region_hint(active_capture_region(self._config))
        self._reposition_audio_label()
        self._log.info("config.saved")


def run_app(
    *,
    debug_boxes: bool = False,
    live_capture: bool = True,
    use_grpc: bool = False,
    debug_raw_rois: bool = False,
) -> int:
    setup_logging()
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = OverBabelApp(
        debug_boxes=debug_boxes,
        live_capture=live_capture,
        use_grpc=use_grpc,
        debug_raw_rois=debug_raw_rois,
    )
    return app.run()
