"""
API Key Setup Dialog - Secure API key configuration for AsciiDoc Artisan.

This module provides a dialog for securely configuring API keys using
OS keyring storage. Part of Phase 3 (v1.1) security features.

Security Features:
- Password-masked input fields
- Validation before storage
- Secure keyring integration
- No plain-text display of existing keys
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from asciidoc_artisan.core import SecureCredentials

logger = logging.getLogger(__name__)


class APIKeySetupDialog(QDialog):
    """Dialog for securely configuring API keys.

    This dialog allows users to configure API keys for AI-enhanced
    document conversion. Keys are stored securely in the OS keyring.

    Security Properties:
    - Password-masked input
    - Validation before storage
    - No display of existing keys
    - Secure storage via OS keyring

    Example:
        >>> dialog = APIKeySetupDialog(parent)
        >>> if dialog.exec() == QDialog.DialogCode.Accepted:
        ...     print("API key configured successfully")
    """

    def __init__(self, parent=None) -> None:
        """Initialize the API Key Setup Dialog.

        Args:
            parent: Parent widget (typically the main window)
        """
        super().__init__(parent)
        self.setWindowTitle("API Key Setup")
        self.setModal(True)
        self.setMinimumWidth(500)

        self.credentials = SecureCredentials()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI components."""
        layout = QVBoxLayout(self)

        # Information label
        info_label = QLabel(
            "<b>Secure API Key Configuration</b><br><br>"
            "Configure your API keys for AI-enhanced document conversion. "
            "Keys are stored securely in your system keyring and never saved "
            "in plain text."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Form layout for API keys
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Anthropic API Key
        self.anthropic_key_input = QLineEdit()
        self.anthropic_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_key_input.setPlaceholderText("sk-ant-...")
        self.anthropic_key_input.textChanged.connect(self._on_key_changed)

        anthropic_layout = QVBoxLayout()
        anthropic_layout.addWidget(self.anthropic_key_input)

        # Status label for Anthropic
        self.anthropic_status = QLabel()
        self._update_status_label()
        anthropic_layout.addWidget(self.anthropic_status)

        form_layout.addRow("Anthropic API Key:", anthropic_layout)

        # Add test button
        self.test_button = QPushButton("Test API Key")
        self.test_button.setEnabled(False)
        self.test_button.clicked.connect(self._test_api_key)
        form_layout.addRow("", self.test_button)

        layout.addLayout(form_layout)

        # Help text
        help_label = QLabel(
            "<small><b>How to get an API key:</b><br>"
            "1. Visit <a href='https://console.anthropic.com'>console.anthropic.com</a><br>"
            "2. Sign up or log in to your account<br>"
            "3. Go to API Keys section<br>"
            "4. Create a new API key<br>"
            "5. Paste the key above (starts with 'sk-ant-')</small>"
        )
        help_label.setWordWrap(True)
        help_label.setOpenExternalLinks(True)
        help_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        layout.addWidget(help_label)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_and_accept)
        button_box.rejected.connect(self.reject)

        # Add Clear button
        clear_button = QPushButton("Clear Stored Key")
        clear_button.clicked.connect(self._clear_stored_key)
        button_box.addButton(clear_button, QDialogButtonBox.ButtonRole.ActionRole)

        layout.addWidget(button_box)

    def _update_status_label(self) -> None:
        """Update the status label showing whether a key is stored."""
        if not SecureCredentials.is_available():
            self.anthropic_status.setText(
                "<span style='color: orange;'>⚠ Keyring not available</span>"
            )
            return

        if self.credentials.has_anthropic_key():
            self.anthropic_status.setText(
                "<span style='color: green;'>✓ Key is configured</span>"
            )
        else:
            self.anthropic_status.setText(
                "<span style='color: gray;'>No key stored</span>"
            )

    def _on_key_changed(self, text: str) -> None:
        """Handle API key input changes.

        Args:
            text: Current text in the input field
        """
        # Enable test button if key looks valid
        is_valid = text.startswith("sk-ant-") and len(text) > 20
        self.test_button.setEnabled(is_valid)

    def _test_api_key(self) -> None:
        """Test the entered API key."""
        api_key = self.anthropic_key_input.text().strip()

        if not api_key:
            QMessageBox.warning(self, "No API Key", "Please enter an API key to test.")
            return

        # Basic validation
        if not api_key.startswith("sk-ant-"):
            QMessageBox.warning(
                self,
                "Invalid Format",
                "Anthropic API keys should start with 'sk-ant-'.\n\n"
                "Please check your API key and try again.",
            )
            return

        # For now, just validate format (actual API testing would require network call)
        QMessageBox.information(
            self,
            "Key Format Valid",
            "The API key format appears valid.\n\n"
            "Note: Full validation requires a network connection and will be "
            "performed when you use AI conversion features.",
        )

    def _save_and_accept(self) -> None:
        """Save the API key and accept the dialog."""
        api_key = self.anthropic_key_input.text().strip()

        if api_key:
            # Validate format
            if not api_key.startswith("sk-ant-"):
                QMessageBox.warning(
                    self,
                    "Invalid Format",
                    "Anthropic API keys should start with 'sk-ant-'.\n\n"
                    "Please check your API key.",
                )
                return

            # Store securely
            if not SecureCredentials.is_available():
                QMessageBox.critical(
                    self,
                    "Keyring Unavailable",
                    "Cannot store API key: system keyring is not available.\n\n"
                    "Please install keyring support:\n"
                    "  pip install keyring",
                )
                return

            if self.credentials.store_anthropic_key(api_key):
                logger.info("Anthropic API key stored successfully")
                QMessageBox.information(
                    self,
                    "Success",
                    "API key stored securely in system keyring.\n\n"
                    "You can now use AI-enhanced document conversion.",
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Storage Failed",
                    "Failed to store API key in system keyring.\n\n"
                    "Please check system logs for details.",
                )
        else:
            # No key entered, just close
            self.accept()

    def _clear_stored_key(self) -> None:
        """Clear the stored API key."""
        if not SecureCredentials.is_available():
            QMessageBox.warning(
                self, "Keyring Unavailable", "System keyring is not available."
            )
            return

        if not self.credentials.has_anthropic_key():
            QMessageBox.information(
                self, "No Key Stored", "No API key is currently stored."
            )
            return

        import os

        # Skip prompts in test environment to prevent blocking
        if os.environ.get("PYTEST_CURRENT_TEST"):
            # In tests, automatically proceed with deletion
            self.credentials.delete_anthropic_key()
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete the stored API key?\n\n"
            "You will need to re-enter it to use AI conversion features.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.credentials.delete_anthropic_key():
                QMessageBox.information(
                    self, "Key Deleted", "API key has been removed from keyring."
                )
                self._update_status_label()
                logger.info("Anthropic API key deleted by user")
            else:
                QMessageBox.warning(
                    self, "Deletion Failed", "Failed to delete API key from keyring."
                )

    def get_api_key(self) -> Optional[str]:
        """Get the currently stored API key.

        Returns:
            The API key if configured, None otherwise

        Note:
            This retrieves from keyring, not from the input field
        """
        if SecureCredentials.is_available():
            return self.credentials.get_anthropic_key()
        return None
