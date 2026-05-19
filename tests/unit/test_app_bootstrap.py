"""Ensure QApplication is created before onboarding / overlay."""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6")
from PyQt6.QtWidgets import QApplication  # noqa: E402


def test_onboarding_requires_qapplication() -> None:
    from overbabel_core.config.schema import OverBabelConfig
    from overbabel_ui.onboarding import OnboardingDialog

    app = QApplication.instance() or QApplication([])
    assert isinstance(app, QApplication)
    dlg = OnboardingDialog(OverBabelConfig())
    dlg.close()
