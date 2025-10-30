"""Tests for ui.dialogs module."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


class TestDialogs:
    """Test suite for dialog classes."""

    def test_import_dialogs(self):
        from asciidoc_artisan.ui import dialogs
        assert dialogs is not None

    def test_preferences_dialog_exists(self, qapp):
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog()
        assert dialog is not None
        assert dialog.windowTitle() != ""

    def test_dialog_has_accept_reject(self, qapp):
        from asciidoc_artisan.ui.dialogs import PreferencesDialog
        dialog = PreferencesDialog()
        assert hasattr(dialog, "accept")
        assert hasattr(dialog, "reject")
