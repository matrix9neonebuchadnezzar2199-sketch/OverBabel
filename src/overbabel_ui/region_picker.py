"""Fullscreen region picker: draw -> lock -> move -> confirm."""

from __future__ import annotations

from PyQt6.QtCore import QPoint, QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QGuiApplication, QPainter, QPen
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from overbabel_core.config.screen_coords import global_rect_to_capture_region
from overbabel_core.roi import RegionOfInterest

# Logical pixels on canvas (physical minimum checked on confirm)
_MIN_LOGICAL_W = 40
_MIN_LOGICAL_H = 24
_MIN_PHYSICAL_W = 80
_MIN_PHYSICAL_H = 48


def clamp_rect_to_bounds(rect: QRect, bounds: QRect) -> QRect:
    """Keep *rect* fully inside *bounds*."""
    r = rect.normalized()
    if r.width() < 1:
        r.setWidth(1)
    if r.height() < 1:
        r.setHeight(1)
    if r.left() < bounds.left():
        r.moveLeft(bounds.left())
    if r.top() < bounds.top():
        r.moveTop(bounds.top())
    if r.right() > bounds.right():
        r.moveLeft(bounds.right() - r.width() + 1)
    if r.bottom() > bounds.bottom():
        r.moveTop(bounds.bottom() - r.height() + 1)
    return r


class _PickerCanvas(QWidget):
    """Phase 1: drag new rect. Phase 2: drag inside locked rect to move."""

    rect_locked = pyqtSignal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._locked: QRect | None = None
        self._draft_origin: QPoint | None = None
        self._draft_current: QPoint | None = None
        self._move_grab_offset: QPoint | None = None
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def locked_rect(self) -> QRect | None:
        return self._locked

    def _draft_rect(self) -> QRect | None:
        if self._draft_origin is None or self._draft_current is None:
            return None
        return QRect(self._draft_origin, self._draft_current).normalized()

    def _emit_locked(self) -> None:
        self.rect_locked.emit(self._locked is not None)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.position().toPoint()
        if self._locked is not None:
            if self._locked.contains(pos):
                self._move_grab_offset = pos - self._locked.topLeft()
            return
        self._draft_origin = pos
        self._draft_current = pos
        self.update()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        pos = event.position().toPoint()
        if self._locked is not None and self._move_grab_offset is not None:
            top_left = pos - self._move_grab_offset
            self._locked = clamp_rect_to_bounds(
                QRect(top_left, self._locked.size()),
                self.rect(),
            )
            self.update()
            return
        if self._draft_origin is not None and self._locked is None:
            self._draft_current = pos
            self.update()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._move_grab_offset is not None:
            self._move_grab_offset = None
            return
        if self._draft_origin is None or self._locked is not None:
            return
        pos = event.position().toPoint()
        draft = QRect(self._draft_origin, pos).normalized()
        self._draft_origin = None
        self._draft_current = None
        if draft.width() >= _MIN_LOGICAL_W and draft.height() >= _MIN_LOGICAL_H:
            self._locked = clamp_rect_to_bounds(draft, self.rect())
            self._emit_locked()
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
        if self._locked is not None:
            painter.setPen(QPen(Qt.GlobalColor.cyan, 2, Qt.PenStyle.SolidLine))
            painter.drawRect(self._locked)
            painter.fillRect(self._locked, QColor(0, 200, 255, 35))
        draft = self._draft_rect()
        if draft is not None and self._locked is None:
            painter.setPen(QPen(Qt.GlobalColor.cyan, 2, Qt.PenStyle.DashLine))
            painter.drawRect(draft)


class RegionPickerDialog(QDialog):
    """Pick capture region: draw once, adjust by dragging inside box, then confirm."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("翻訳する範囲を指定")
        self._picked: RegionOfInterest | None = None
        self._monitor_geo = QRect(0, 0, 1920, 1080)

        screen = QGuiApplication.primaryScreen()
        if screen is None:
            QMessageBox.critical(parent, "OverBabel", "ディスプレイを取得できません。")
            return
        self._monitor_geo = screen.geometry()
        self.setGeometry(self._monitor_geo)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._canvas = _PickerCanvas(self)
        self._canvas.rect_locked.connect(self._on_rect_locked)
        root.addWidget(self._canvas, stretch=1)

        self._hint = QLabel(self._canvas)
        self._hint.setStyleSheet(
            "color: white; background: rgba(0,0,0,190); padding: 10px; border-radius: 6px;"
        )
        self._hint.setText(self._hint_create())
        self._hint.adjustSize()
        self._hint.move(16, 16)
        self._hint.raise_()

        footer = QWidget()
        footer.setObjectName("regionPickerFooter")
        footer.setStyleSheet(
            """
            #regionPickerFooter {
                background-color: rgba(20, 24, 32, 230);
                border-top: 1px solid rgba(0, 200, 255, 120);
            }
            QPushButton {
                min-height: 36px;
                min-width: 120px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton#btnConfirm {
                background-color: #0d9bd8;
                color: white;
                border: 1px solid #5ed4ff;
            }
            QPushButton#btnConfirm:hover:enabled {
                background-color: #12b0f0;
            }
            QPushButton#btnConfirm:disabled {
                background-color: #3a4555;
                color: #8899aa;
                border: 1px solid #556677;
            }
            QPushButton#btnCancel {
                background-color: #3a3f4a;
                color: #e8e8e8;
                border: 1px solid #666;
            }
            QPushButton#btnCancel:hover {
                background-color: #4d5360;
            }
            """
        )
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(16, 12, 16, 16)

        bar = QDialogButtonBox()
        self._btn_confirm = QPushButton("範囲を決定")
        self._btn_confirm.setObjectName("btnConfirm")
        self._btn_confirm.setEnabled(False)
        self._btn_confirm.clicked.connect(self._on_confirm)
        btn_cancel = QPushButton("キャンセル")
        btn_cancel.setObjectName("btnCancel")
        btn_cancel.clicked.connect(self.reject)
        bar.addButton(self._btn_confirm, QDialogButtonBox.ButtonRole.AcceptRole)
        bar.addButton(btn_cancel, QDialogButtonBox.ButtonRole.RejectRole)
        footer_layout.addWidget(bar)
        root.addWidget(footer)

    @staticmethod
    def _hint_create() -> str:
        return (
            "① ドラッグして範囲を作成（離すと水色の枠が固定）\n"
            "② 枠の中をドラッグして位置を調整\n"
            "③ 「範囲を決定」を押して開始"
        )

    @staticmethod
    def _hint_adjust() -> str:
        return "枠の中をドラッグして位置を調整し、「範囲を決定」を押してください。"

    def _on_rect_locked(self, locked: bool) -> None:
        self._btn_confirm.setEnabled(locked)
        if locked:
            self._hint.setText(self._hint_adjust())
            self._hint.adjustSize()

    def _canvas_rect_to_monitor(self, rect: QRect) -> RegionOfInterest:
        global_rect = QRect(
            self._canvas.mapToGlobal(QPoint(rect.x(), rect.y())),
            rect.size(),
        )
        screen = QGuiApplication.primaryScreen()
        return global_rect_to_capture_region(global_rect, screen)

    def _on_confirm(self) -> None:
        rect = self._canvas.locked_rect()
        if rect is None:
            QMessageBox.warning(self, "OverBabel", "先にドラッグして範囲を作成してください。")
            return
        roi = self._canvas_rect_to_monitor(rect)
        if roi.w < _MIN_PHYSICAL_W or roi.h < _MIN_PHYSICAL_H:
            QMessageBox.warning(
                self,
                "OverBabel",
                f"範囲が小さすぎます。もう少し大きく囲むか、枠を広げてから決定してください。"
                f"（目安: {_MIN_PHYSICAL_W}×{_MIN_PHYSICAL_H} px 以上）",
            )
            return
        self._picked = roi
        self.accept()

    def region(self) -> RegionOfInterest | None:
        return self._picked
