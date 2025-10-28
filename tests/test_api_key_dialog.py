"""Tests for ui.api_key_dialog module."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


class TestApiKeyDialog:
    """Test suite for ApiKeyDialog."""

    def test_import(self):
        from asciidoc_artisan.ui.api_key_dialog import ApiKeyDialog
        assert ApiKeyDialog is not None

    def test_creation(self, qapp):
        from asciidoc_artisan.ui.api_key_dialog import ApiKeyDialog
        dialog = ApiKeyDialog()
        assert dialog is not None

    def test_has_input_field(self, qapp):
        from asciidoc_artisan.ui.api_key_dialog import ApiKeyDialog
        dialog = ApiKeyDialog()
        # Should have some way to input API key
        assert hasattr(dialog, "api_key") or hasattr(dialog, "get_api_key")
