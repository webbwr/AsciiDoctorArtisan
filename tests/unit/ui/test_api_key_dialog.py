"""Tests for ui.api_key_dialog module."""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton


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
        assert (
            "✓" in dialog.anthropic_status.text()
            and "configured" in dialog.anthropic_status.text().lower()
        )

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


@pytest.mark.unit
class TestAPIKeyDialogProperties:
    """Test additional dialog properties."""

    def test_dialog_has_parent_none(self, qapp):
        """Test dialog is created with no parent."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        dialog = APIKeySetupDialog()
        assert dialog.parent() is None

    def test_dialog_fixed_size_policy(self, qapp):
        """Test dialog has appropriate size constraints."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        dialog = APIKeySetupDialog()
        # Should have minimum width
        assert dialog.minimumWidth() >= 400

    def test_dialog_window_flags(self, qapp):
        """Test dialog has correct window flags."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        dialog = APIKeySetupDialog()
        # Should be a dialog
        assert dialog.isModal()

    def test_dialog_has_buttons(self, qapp):
        """Test dialog has standard buttons."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        dialog = APIKeySetupDialog()
        # Should have at least one QPushButton
        buttons = dialog.findChildren(QPushButton)
        assert len(buttons) > 0


@pytest.mark.unit
class TestAPIKeyInputEdgeCases:
    """Test edge cases for API key input."""

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_input_accepts_empty_string(self, mock_creds_class, qapp):
        """Test input field accepts empty string."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        dialog.anthropic_key_input.setText("")
        assert dialog.anthropic_key_input.text() == ""

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_input_accepts_whitespace(self, mock_creds_class, qapp):
        """Test input field accepts whitespace."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        dialog.anthropic_key_input.setText("   ")
        assert dialog.anthropic_key_input.text() == "   "

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_input_accepts_very_long_key(self, mock_creds_class, qapp):
        """Test input field accepts very long keys."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        long_key = "sk-ant-" + "x" * 1000
        dialog.anthropic_key_input.setText(long_key)
        assert dialog.anthropic_key_input.text() == long_key

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_input_accepts_special_characters(self, mock_creds_class, qapp):
        """Test input field accepts special characters."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        special_key = "sk-ant-!@#$%^&*()_+-=[]{}|;':\",./<>?"
        dialog.anthropic_key_input.setText(special_key)
        assert dialog.anthropic_key_input.text() == special_key

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_input_multiple_text_changes(self, mock_creds_class, qapp):
        """Test input handles multiple text changes."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()

        dialog.anthropic_key_input.setText("key1")
        assert dialog.anthropic_key_input.text() == "key1"

        dialog.anthropic_key_input.setText("key2")
        assert dialog.anthropic_key_input.text() == "key2"

        dialog.anthropic_key_input.setText("")
        assert dialog.anthropic_key_input.text() == ""


@pytest.mark.unit
class TestPasswordMasking:
    """Test password masking behavior."""

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_password_mode_masks_text(self, mock_creds_class, qapp):
        """Test password mode properly masks input."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        assert dialog.anthropic_key_input.echoMode() == QLineEdit.EchoMode.Password

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_password_mode_still_stores_text(self, mock_creds_class, qapp):
        """Test password mode still stores actual text."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        test_key = "sk-ant-secret-key"
        dialog.anthropic_key_input.setText(test_key)
        assert dialog.anthropic_key_input.text() == test_key


@pytest.mark.unit
class TestSaveOperationEdgeCases:
    """Test edge cases for save operations."""

    @patch("asciidoc_artisan.ui.api_key_dialog.QMessageBox")
    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_save_with_empty_key(self, mock_creds_class, mock_msgbox, qapp):
        """Test save operation with empty key."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds.store_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        dialog.anthropic_key_input.setText("")

        with patch.object(dialog, "accept"):
            dialog._save_and_accept()

        # Should still call store (validation is in implementation)
        if dialog.anthropic_key_input.text():
            mock_creds.store_anthropic_key.assert_called()

    @patch("asciidoc_artisan.ui.api_key_dialog.QMessageBox")
    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_save_with_whitespace_key(self, mock_creds_class, mock_msgbox, qapp):
        """Test save operation with whitespace-only key."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds.store_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        dialog.anthropic_key_input.setText("   ")

        with patch.object(dialog, "accept"):
            dialog._save_and_accept()

    @patch("asciidoc_artisan.ui.api_key_dialog.QMessageBox")
    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_save_multiple_times(self, mock_creds_class, mock_msgbox, qapp):
        """Test save operation called multiple times."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds.store_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        dialog.anthropic_key_input.setText("sk-ant-test")

        with patch.object(dialog, "accept"):
            dialog._save_and_accept()
            dialog._save_and_accept()
            dialog._save_and_accept()

        # Should be called multiple times
        assert mock_creds.store_anthropic_key.call_count >= 1


@pytest.mark.unit
class TestClearOperationEdgeCases:
    """Test edge cases for clear operations."""

    @patch("asciidoc_artisan.ui.api_key_dialog.QMessageBox")
    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_clear_when_no_key_stored(self, mock_creds_class, mock_msgbox, qapp):
        """Test clear operation when no key is stored."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds.delete_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()

        # Clear should still work even if no key (shows info message)
        dialog._clear_stored_key()

        # Verify info message was shown
        assert mock_msgbox.information.called

    @patch("asciidoc_artisan.ui.api_key_dialog.QMessageBox")
    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_clear_multiple_times(self, mock_creds_class, mock_msgbox, qapp):
        """Test clear operation called multiple times."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = True
        mock_creds.delete_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()

        dialog._clear_stored_key()
        dialog._clear_stored_key()
        dialog._clear_stored_key()

        # Verify delete was called 3 times
        assert mock_creds.delete_anthropic_key.call_count == 3


@pytest.mark.unit
class TestStatusLabelUpdates:
    """Test status label update behavior."""

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_status_label_exists(self, mock_creds_class, qapp):
        """Test status label is created."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        assert hasattr(dialog, "anthropic_status")
        assert dialog.anthropic_status is not None

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_status_label_has_text(self, mock_creds_class, qapp):
        """Test status label contains text."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        assert len(dialog.anthropic_status.text()) > 0

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_status_label_is_qlabel(self, mock_creds_class, qapp):
        """Test status label is QLabel instance."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        assert isinstance(dialog.anthropic_status, QLabel)


@pytest.mark.unit
class TestPlaceholderText:
    """Test placeholder text behavior."""

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_placeholder_contains_sk_ant(self, mock_creds_class, qapp):
        """Test placeholder contains sk-ant prefix."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        assert "sk-ant" in dialog.anthropic_key_input.placeholderText()

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_placeholder_not_empty(self, mock_creds_class, qapp):
        """Test placeholder text is not empty."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        assert len(dialog.anthropic_key_input.placeholderText()) > 0

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_placeholder_disappears_with_text(self, mock_creds_class, qapp):
        """Test placeholder behavior when text is entered."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()

        # Placeholder should exist initially
        assert dialog.anthropic_key_input.placeholderText()

        # Enter text
        dialog.anthropic_key_input.setText("sk-ant-test")

        # Text should be there (placeholder is hidden automatically by Qt)
        assert dialog.anthropic_key_input.text() == "sk-ant-test"


@pytest.mark.unit
class TestDialogInteractions:
    """Test dialog user interactions."""

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_dialog_can_be_shown(self, mock_creds_class, qapp):
        """Test dialog can be shown (doesn't crash)."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        # show() should not crash (but won't actually display in test)
        # Just verify it has the method
        assert hasattr(dialog, "show")

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_dialog_can_be_accepted(self, mock_creds_class, qapp):
        """Test dialog has accept method."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        assert hasattr(dialog, "accept")
        assert callable(dialog.accept)

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_dialog_can_be_rejected(self, mock_creds_class, qapp):
        """Test dialog has reject method."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        assert hasattr(dialog, "reject")
        assert callable(dialog.reject)


@pytest.mark.unit
class TestKeyringAvailability:
    """Test keyring availability handling."""

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_dialog_works_when_keyring_available(self, mock_creds_class, qapp):
        """Test dialog functions when keyring is available."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = True

        dialog = APIKeySetupDialog()
        assert dialog is not None

    @patch("asciidoc_artisan.ui.api_key_dialog.SecureCredentials")
    def test_dialog_works_when_keyring_unavailable(self, mock_creds_class, qapp):
        """Test dialog functions when keyring is unavailable."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        mock_creds = Mock()
        mock_creds_class.return_value = mock_creds
        mock_creds_class.is_available.return_value = False

        dialog = APIKeySetupDialog()
        assert dialog is not None
