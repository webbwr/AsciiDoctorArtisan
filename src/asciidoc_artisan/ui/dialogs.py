"""
UI Dialogs - Preferences dialog.

This module contains QDialog subclasses for user interaction:
- PreferencesDialog: Application preferences (AI settings)

Implements FR-055: AI-Enhanced Conversion user configuration.

Usage Example:
    ```python
    from asciidoc_artisan.ui.dialogs import PreferencesDialog

    dialog = PreferencesDialog(self.settings)
    if dialog.exec():
        self.settings = dialog.get_settings()
        self._save_settings()
    ```
"""

import os
from typing import Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core import Settings


class PreferencesDialog(QDialog):
    """
    Preferences dialog for user settings.

    Allows user to configure default AI conversion setting and view
    API key configuration status.

    Implements FR-055: AI-Enhanced Conversion option configuration.

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

    def __init__(self, settings: Settings, parent: Optional[QWidget] = None) -> None:
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
            "Use Claude AI for better document conversions\n"
            "Preserves complex formatting like nested lists and tables"
        )
        ai_layout.addWidget(self.ai_enabled_checkbox)

        # API Key Status Display
        api_key_status = self._get_api_key_status()
        status_label = QLabel(f"API Key Status: {api_key_status}")
        status_label.setStyleSheet(
            "QLabel { color: green; }"
            if api_key_status == "✓ Configured"
            else "QLabel { color: red; }"
        )
        ai_layout.addWidget(status_label)

        # Information Label
        info_label = QLabel(
            "• Requires ANTHROPIC_API_KEY environment variable\n"
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
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _get_api_key_status(self) -> str:
        """
        Check if ANTHROPIC_API_KEY is configured.

        Returns:
            "✓ Configured" if API key is set, "✗ Not Set" otherwise
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key and len(api_key) > 0:
            return "✓ Configured"
        return "✗ Not Set"

    def get_settings(self) -> Settings:
        """
        Get updated settings from dialog.

        Returns:
            Settings instance with updated ai_conversion_enabled value
        """
        self.settings.ai_conversion_enabled = self.ai_enabled_checkbox.isChecked()
        return self.settings
