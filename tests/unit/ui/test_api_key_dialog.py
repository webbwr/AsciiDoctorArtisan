"""Tests for ui.api_key_dialog module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QLineEdit, QLabel, QPushButton
from PySide6.QtCore import Qt


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


@pytest.mark.unit
class TestApiKeyDialog:
    """Test suite for APIKeySetupDialog basic functionality."""

    def test_import(self):
        """Test APIKeySetupDialog can be imported."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        assert APIKeySetupDialog is not None

    def test_creation(self, qapp):
        """Test APIKeySetupDialog can be instantiated."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        assert dialog is not None

    def test_has_input_field(self, qapp):
        """Test dialog has get_api_key method."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        assert hasattr(dialog, "get_api_key")
        assert callable(dialog.get_api_key)


@pytest.mark.unit
class TestAPIKeySetupDialogUI:
    """Test suite for APIKeySetupDialog UI components."""

    def test_dialog_title(self, qapp):
        """Test dialog has correct title."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        assert dialog.windowTitle() == "API Key Setup"

    def test_dialog_is_modal(self, qapp):
        """Test dialog is modal."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        assert dialog.isModal()

    def test_dialog_minimum_width(self, qapp):
        """Test dialog has minimum width set."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        assert dialog.minimumWidth() == 500

    def test_anthropic_key_input_exists(self, qapp):
        """Test Anthropic API key input field exists."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        assert hasattr(dialog, "anthropic_key_input")
        assert isinstance(dialog.anthropic_key_input, QLineEdit)

    def test_anthropic_key_input_password_mode(self, qapp):
        """Test API key input is password-masked."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        assert dialog.anthropic_key_input.echoMode() == QLineEdit.EchoMode.Password

    def test_anthropic_key_input_placeholder(self, qapp):
        """Test API key input has placeholder text."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        assert "sk-ant" in dialog.anthropic_key_input.placeholderText()

    def test_anthropic_status_label_exists(self, qapp):
        """Test status label exists."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        assert hasattr(dialog, "anthropic_status")
        assert isinstance(dialog.anthropic_status, QLabel)

    def test_has_test_button(self, qapp):
        """Test dialog has test API key button."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()
        # Button should exist (created in _setup_ui)
        assert dialog.findChild(QPushButton, "")  # Find any push button


@pytest.mark.unit
class TestAPIKeyStatusUpdates:
    """Test suite for API key status updates."""

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_status_shows_configured_when_key_exists(self, mock_creds_class, qapp):
        """Test status shows configured when API key exists."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        # Mock credentials to return a key
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds
        # Mock is_available to return True so keyring checks pass
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()

        # Status should show "✓ Key is configured"
        assert "✓" in dialog.anthropic_status.text() and "configured" in dialog.anthropic_status.text().lower()

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_status_shows_not_set_when_no_key(self, mock_creds_class, qapp):
        """Test status shows not set when API key doesn't exist."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        # Mock credentials to return no key
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        # Mock is_available to return True so keyring checks pass
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()

        # Status should show "No key stored"
        assert "No key stored" in dialog.anthropic_status.text()


@pytest.mark.unit
class TestAPIKeyInputValidation:
    """Test suite for API key input validation."""

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_get_api_key_returns_text(self, mock_creds_class, qapp):
        """Test get_api_key returns stored key from keyring."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        # Mock credentials to return a key
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = True
        test_key = "sk-ant-test-key-123"
        mock_creds.get_anthropic_key.return_value = test_key
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()

        assert dialog.get_api_key() == test_key

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_get_api_key_returns_none_when_empty(self, mock_creds_class, qapp):
        """Test get_api_key returns None when no key stored."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        # Mock credentials to return no key
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds.get_anthropic_key.return_value = None
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()

        assert dialog.get_api_key() is None

    def test_on_key_changed_triggered(self, qapp):
        """Test _on_key_changed is triggered on text change."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
        dialog = APIKeySetupDialog()

        # Mock the _on_key_changed method
        with patch.object(dialog, "_on_key_changed") as mock_method:
            # Reconnect signal to mock
            dialog.anthropic_key_input.textChanged.disconnect()
            dialog.anthropic_key_input.textChanged.connect(mock_method)

            # Change text
            dialog.anthropic_key_input.setText("test-key")

            # Verify method was called
            mock_method.assert_called()


@pytest.mark.unit
class TestAPIKeySaveAndClear:
    """Test suite for API key save and clear operations."""

    @patch("asciidoc_artisan.ui.api_key_dialog.QMessageBox")
    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_save_stores_api_key(self, mock_creds_class, mock_msgbox, qapp):
        """Test _save_and_accept stores API key."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        # Mock credentials
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds.store_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        dialog.anthropic_key_input.setText("sk-ant-test-key")

        # Call save method
        with patch.object(dialog, "accept"):  # Prevent dialog from closing
            dialog._save_and_accept()

        # Verify store_anthropic_key was called
        mock_creds.store_anthropic_key.assert_called_once_with("sk-ant-test-key")

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_clear_removes_api_key(self, mock_creds_class, qapp):
        """Test _clear_stored_key removes API key."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        # Mock credentials
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = True
        mock_creds.delete_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()

        # Call clear - pytest environment auto-skips confirmation prompt
        dialog._clear_stored_key()

        # Verify delete was called
        mock_creds.delete_anthropic_key.assert_called_once()
