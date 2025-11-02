"""Tests for ui.ui_setup_manager module."""

import pytest
from PySide6.QtWidgets import QMainWindow


@pytest.fixture
def main_window(qapp):
    return QMainWindow()


class TestUISetupManager:
    """Test suite for UISetupManager."""

    def test_import(self):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager
        assert UISetupManager is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager
        manager = UISetupManager(main_window)
        assert manager is not None

    def test_has_setup_methods(self, main_window):
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager
        manager = UISetupManager(main_window)
        methods = [m for m in dir(manager) if "setup" in m.lower()]
        assert len(methods) > 0
