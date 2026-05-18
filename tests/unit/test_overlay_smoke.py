"""Phase 1 smoke test for overlay window.

CI 環境 (ヘッドレス) でも動くように QT_QPA_PLATFORM=offscreen を強制する。
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6")
from PyQt6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance() or QApplication([])
    assert isinstance(app, QApplication)
    return app


def test_overlay_window_constructs(qapp: QApplication) -> None:
    from overbabel_ui.overlay.window import OverlayWindow

    w = OverlayWindow(debug_boxes=True)
    assert w is not None
    assert w.windowTitle() == "OverBabel Overlay"
    # geometry は offscreen でも primaryScreen が返るはず
    assert w.width() > 0
    assert w.height() > 0
    w.close()


def test_overlay_debug_samples_build(qapp: QApplication) -> None:
    from overbabel_ui.overlay.window import OverlayWindow

    w = OverlayWindow(debug_boxes=True)
    samples = w._build_debug_samples()
    tags = [s.tag for s in samples]
    assert "UI" in tags
    assert "DIALOG" in tags
    assert "SUBTITLE" in tags
    assert any("AUDIO" in t for t in tags)
    w.close()


def test_tray_constructs(qapp: QApplication) -> None:
    from overbabel_ui.tray.tray import OverBabelTray

    tray = OverBabelTray()
    tray.set_overlay_state(False)
    tray.set_overlay_state(True)
    # show() は offscreen でも呼んで例外が出ないことだけ確認
    tray.show()
    tray.hide()
