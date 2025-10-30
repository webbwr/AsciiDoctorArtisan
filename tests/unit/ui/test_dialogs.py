"""Tests for ui.dialogs module."""

import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


@pytest.fixture
def mock_settings(qapp):
    """Create mock settings for PreferencesDialog."""
    # Use a simple object instead of Mock to avoid Mock return values
    class SimpleSettings:
        def __init__(self):
            self.dark_mode = False
            self.font_size = 12
            self.sync_scroll = True
            self.auto_preview = True
            self.ai_conversion_enabled = False

    return SimpleSettings()


class TestDialogs:
    """Test suite for dialog classes."""

    def test_import_dialogs(self):
        from asciidoc_artisan.ui import dialogs
        assert dialogs is not None

    def test_preferences_dialog_exists(self, mock_settings):
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)  # Requires settings argument
        assert dialog is not None
        assert dialog.windowTitle() != ""

    def test_dialog_has_accept_reject(self, mock_settings):
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog(mock_settings)  # Requires settings argument
        assert hasattr(dialog, "accept")
        assert hasattr(dialog, "reject")
