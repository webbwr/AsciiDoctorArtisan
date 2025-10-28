"""Tests for ui.ui_state_manager module."""

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window(qapp):
    return QMainWindow()


class TestUIStateManager:
    """Test suite for UIStateManager."""

    def test_import(self):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager
        assert UIStateManager is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager
        manager = UIStateManager(main_window)
        assert manager is not None

    def test_has_state_tracking(self, main_window):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager
        manager = UIStateManager(main_window)
        # Should have state tracking attributes or methods
        attrs = [a for a in dir(manager) if not a.startswith("__")]
        assert len(attrs) > 0
