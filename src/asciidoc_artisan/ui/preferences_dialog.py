"""
Preferences Dialog - Main user preferences configuration.

Extracted from dialogs.py for MA principle compliance.
Handles AI conversion settings and API key status display.

Implements FR-055: AI-Enhanced Conversion option configuration.

Security: Uses SecureCredentials (OS keyring) for API key status.
Never reads API keys from environment variables (process exposure risk).
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core import Settings
from asciidoc_artisan.core.secure_credentials import SecureCredentials
from asciidoc_artisan.ui.dialog_factory import create_ok_cancel_buttons


class PreferencesDialog(QDialog):
    """
    Preferences dialog for user settings.

    Allows user to configure default AI conversion setting and view
    API key configuration status.

    Args:
        settings: Current Settings instance to edit
        parent: Parent QWidget (optional)

    Example:
        ```python
        dialog = PreferencesDialog(self.settings)
        if dialog.exec():
            self.settings = dialog.get_settings()
            self._save_settings()
        ```
    """

    def __init__(self, settings: Settings, parent: QWidget | None = None) -> None:
        """Initialize preferences dialog."""
        super().__init__(parent)
        self.settings = settings
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the preferences UI."""
        self.setWindowTitle("Preferences")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # AI Conversion Settings Group
        ai_group = QGroupBox("AI-Enhanced Conversion")
        ai_layout = QVBoxLayout()

        self.ai_enabled_checkbox = QCheckBox("Enable AI-enhanced conversion by default")
        self.ai_enabled_checkbox.setChecked(self.settings.ai_conversion_enabled)
        self.ai_enabled_checkbox.setToolTip(
            "Use Claude AI for better document conversions\nPreserves complex formatting like nested lists and tables"
        )
        ai_layout.addWidget(self.ai_enabled_checkbox)

        # API Key Status Display
        api_key_status = self._get_api_key_status()
        status_label = QLabel(f"API Key Status: {api_key_status}")
        status_label.setStyleSheet(
            "QLabel { color: green; }" if api_key_status == "✓ Configured" else "QLabel { color: red; }"
        )
        ai_layout.addWidget(status_label)

        # Information Label
        info_label = QLabel(
            "• API key stored in OS keyring (secure)\n"
            "• May incur usage costs (see anthropic.com for pricing)\n"
            "• Falls back to Pandoc automatically if unavailable\n"
            "• See Help → AI Conversion Setup for more information"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { color: gray; font-size: 10pt; }")
        ai_layout.addWidget(info_label)

        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        # Dialog Buttons
        layout.addLayout(create_ok_cancel_buttons(self))

    def _get_api_key_status(self) -> str:
        """
        Check if Anthropic API key is configured in OS keyring.

        Security: Uses SecureCredentials (OS keyring) instead of environment
        variables. Environment variables are exposed to process listings,
        child processes, and logs. Keyring provides OS-level encryption.

        Returns:
            "✓ Configured" if API key is set, "✗ Not Set" otherwise
        """
        credentials = SecureCredentials()
        if credentials.has_anthropic_key():
            return "✓ Configured"
        return "✗ Not Set"

    def get_settings(self) -> Settings:
        """
        Get updated settings from dialog.

        Returns:
            Settings instance with updated ai_conversion_enabled
        """
        self.settings.ai_conversion_enabled = self.ai_enabled_checkbox.isChecked()
        return self.settings
