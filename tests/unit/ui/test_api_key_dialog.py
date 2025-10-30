"""Tests for ui.api_key_dialog module."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


class TestApiKeyDialog:
    """Test suite for APIKeySetupDialog."""

    def test_import(self):
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        assert APIKeySetupDialog is not None

    def test_creation(self, qapp):
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        assert dialog is not None

    def test_has_input_field(self, qapp):
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        # Should have get_api_key method (line 281 in api_key_dialog.py)
        assert hasattr(dialog, "get_api_key")
        assert callable(dialog.get_api_key)
