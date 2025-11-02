"""Tests for ui.settings_manager module."""

import pytest
from PySide6.QtWidgets import QMainWindow


@pytest.fixture
def main_window(qapp):
    return QMainWindow()


class TestSettingsManager:
    """Test suite for SettingsManager."""

    def test_import(self):
        from asciidoc_artisan.ui.settings_manager import SettingsManager
        assert SettingsManager is not None

    def test_creation(self, qapp):
        from asciidoc_artisan.ui.settings_manager import SettingsManager
        manager = SettingsManager()  # Takes no arguments
        assert manager is not None

    def test_has_settings_methods(self, qapp):
        from asciidoc_artisan.ui.settings_manager import SettingsManager
        manager = SettingsManager()  # Takes no arguments
        methods = [m for m in dir(manager) if any(x in m.lower() for x in ["get", "set", "load", "save"])]
        assert len(methods) > 0
