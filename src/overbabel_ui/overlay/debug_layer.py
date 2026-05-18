"""Phase 1 用のダミー描画。モック (docs/mockup.html) と同じ見た目を再現する。

- 半透明グレーの背景 (OverlayWindow が透明なので "透ける" 領域そのもの)
- 1.5px の赤い枠
- 左上に種別タグ
- 中央に翻訳テキスト
"""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen

# モックと同じ色定義
COL_GRAY_BG = QColor(180, 180, 180, int(0.18 * 255))  # rgba(180,180,180,.18)
COL_RED_FRAME = QColor(255, 59, 59, 255)
COL_RED_TAG_BG = QColor(255, 59, 59, 255)
COL_PURPLE_BG = QColor(120, 90, 255, int(0.18 * 255))
COL_PURPLE_FRAME = QColor(169, 139, 255, 255)
COL_TAG_TEXT = QColor(255, 255, 255, 255)
COL_TEXT = QColor(255, 236, 236, 255)
COL_TEXT_SHADOW = QColor(0, 0, 0, 220)


@dataclass(frozen=True)
class DebugSample:
    tag: str
    text: str
    rect: QRect
    accent: bool = False  # True なら紫系 (音声字幕風)


def draw_debug_layer(painter: QPainter, samples: list[DebugSample]) -> None:
    for s in samples:
        _draw_sample(painter, s)


def _draw_sample(painter: QPainter, s: DebugSample) -> None:
    frame_color = COL_PURPLE_FRAME if s.accent else COL_RED_FRAME
    bg_color = COL_PURPLE_BG if s.accent else COL_GRAY_BG
    tag_bg = COL_PURPLE_FRAME if s.accent else COL_RED_TAG_BG

    # 1) 背景
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(bg_color))
    painter.drawRoundedRect(s.rect, 4, 4)

    # 2) 赤枠
    pen = QPen(frame_color)
    pen.setWidthF(1.5)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(s.rect, 4, 4)

    # 3) 種別タグ (左上に出す小さなラベル)
    tag_font = QFont("Segoe UI", 8)
    tag_font.setBold(False)
    painter.setFont(tag_font)
    fm = painter.fontMetrics()
    tag_w = fm.horizontalAdvance(s.tag) + 12
    tag_h = fm.height() + 4
    tag_rect = QRect(s.rect.x(), s.rect.y() - tag_h - 2, tag_w, tag_h)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(tag_bg))
    painter.drawRoundedRect(tag_rect, 3, 3)
    painter.setPen(QPen(COL_TAG_TEXT))
    painter.drawText(tag_rect, Qt.AlignmentFlag.AlignCenter, s.tag)

    # 4) 翻訳テキスト本体 (縁取り = シャドウ)
    body_font = QFont("Noto Sans JP", 11)
    body_font.setBold(True)
    painter.setFont(body_font)

    # シャドウ
    shadow_pen = QPen(COL_TEXT_SHADOW)
    painter.setPen(shadow_pen)
    shadow_rect = s.rect.adjusted(9, 9, -7, -7)
    painter.drawText(
        shadow_rect,
        Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
        s.text,
    )

    # 本体
    painter.setPen(QPen(COL_TEXT))
    body_rect = s.rect.adjusted(8, 8, -8, -8)
    painter.drawText(
        body_rect,
        Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
        s.text,
    )
