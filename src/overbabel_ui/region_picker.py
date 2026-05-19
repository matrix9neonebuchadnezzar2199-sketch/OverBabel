"""Fullscreen drag-to-select rectangle on the primary monitor."""

from __future__ import annotations

from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QPainter, QPen
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QMessageBox, QVBoxLayout, QWidget

from overbabel_core.roi import RegionOfInterest

_MIN_W = 80
_MIN_H = 48


class _PickerCanvas(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._origin: QPoint | None = None
        self._current: QPoint | None = None
        self.setMouseTracking(True)

    def selection_rect(self) -> QRect | None:
        if self._origin is None or self._current is None:
            return None
        return QRect(self._origin, self._current).normalized()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._origin = event.position().toPoint()
            self._current = self._origin
            self.update()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._origin is not None:
            self._current = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._origin is not None:
            self._current = event.position().toPoint()
            self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
        rect = self.selection_rect()
        if rect is None or rect.width() < 4 or rect.height() < 4:
            return
        painter.setPen(QPen(Qt.GlobalColor.cyan, 2, Qt.PenStyle.DashLine))
        painter.drawRect(rect)


class RegionPickerDialog(QDialog):
    """Let the user drag a monitor-local ROI (same coords as dxcam frame)."""

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
        root.addWidget(self._canvas, stretch=1)

        hint = QLabel(
            "マウスでドラッグして範囲を囲んでください（80×48px 以上）。\n"
            "動画・字幕ウィンドウ全体を大きめに囲むと認識しやすいです。",
            self._canvas,
        )
        hint.setStyleSheet(
            "color: white; background: rgba(0,0,0,180); padding: 10px; border-radius: 6px;"
        )
        hint.adjustSize()
        hint.move(16, 16)
        hint.raise_()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        assert ok_btn is not None
        ok_btn.setText("この範囲で開始")
        ok_btn.clicked.connect(self._on_ok_clicked)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _canvas_rect_to_monitor(self, rect: QRect) -> RegionOfInterest:
        top_left = self._canvas.mapToGlobal(QPoint(rect.x(), rect.y()))
        geo = self._monitor_geo
        x = top_left.x() - geo.x()
        y = top_left.y() - geo.y()
        return RegionOfInterest(x, y, rect.width(), rect.height())

    def _on_ok_clicked(self) -> None:
        rect = self._canvas.selection_rect()
        if rect is None or rect.width() < _MIN_W or rect.height() < _MIN_H:
            QMessageBox.warning(
                self,
                "OverBabel",
                f"範囲が小さすぎます。ドラッグで {_MIN_W}×{_MIN_H} ピクセル以上の"
                "矩形を囲んでから「この範囲で開始」を押してください。",
            )
            return
        self._picked = self._canvas_rect_to_monitor(rect)
        self.accept()

    def region(self) -> RegionOfInterest | None:
        return self._picked
