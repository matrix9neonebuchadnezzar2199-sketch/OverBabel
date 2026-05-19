"""Fullscreen drag-to-select rectangle on the primary monitor."""

from __future__ import annotations

from PyQt6.QtCore import QPoint, QRect, Qt
from PyQt6.QtGui import QColor, QGuiApplication, QPainter, QPen
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget

from overbabel_core.roi import RegionOfInterest


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

        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.geometry()
        self.setGeometry(geo)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        root = QVBoxLayout(self)
        hint = QLabel(
            "マウスでドラッグして、翻訳対象の範囲を囲んでください。\n"
            "（動画プレイヤーや字幕ウィンドウのあたり）"
        )
        hint.setStyleSheet("color: white; background: rgba(0,0,0,160); padding: 8px;")
        root.addWidget(hint)

        self._canvas = _PickerCanvas(self)
        root.addWidget(self._canvas, stretch=1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("この範囲で開始")
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _on_accept(self) -> None:
        rect = self._canvas.selection_rect()
        if rect is None or rect.width() < 80 or rect.height() < 48:
            return
        self._picked = RegionOfInterest(rect.x(), rect.y(), rect.width(), rect.height())
        self.accept()

    def region(self) -> RegionOfInterest | None:
        return self._picked
