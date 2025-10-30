"""Tests for ui.settings_manager module."""

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


class TestSettingsManager:
    """Test suite for SettingsManager."""

    def test_import(self):
        from asciidoc_artisan.ui.settings_manager import SettingsManager
        assert SettingsManager is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.settings_manager import SettingsManager
        manager = SettingsManager(main_window)
        assert manager is not None

    def test_has_settings_methods(self, main_window):
        from asciidoc_artisan.ui.settings_manager import SettingsManager
        manager = SettingsManager(main_window)
        methods = [m for m in dir(manager) if any(x in m.lower() for x in ["get", "set", "load", "save"])]
        assert len(methods) > 0
