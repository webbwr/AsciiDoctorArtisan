"""
UI Dialogs - Import/Export options and Preferences dialogs.

This module contains QDialog subclasses for user interaction:
- ImportOptionsDialog: Per-import AI conversion choice
- ExportOptionsDialog: Per-export AI conversion choice
- PreferencesDialog: Application preferences (AI settings)

All dialogs implement FR-055: AI-Enhanced Conversion user configuration.

Usage Example:
    ```python
    from asciidoc_artisan.ui.dialogs import ImportOptionsDialog

    dialog = ImportOptionsDialog("docx", "document.docx", default_use_ai=True)
    if dialog.exec():
        use_ai = dialog.get_use_ai()
        # Proceed with import using AI if enabled
    ```
"""

import os
from typing import Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core import Settings

# Check for Claude client availability
try:
    import claude_client  # noqa: F401

    CLAUDE_CLIENT_AVAILABLE = True
except ImportError:
    CLAUDE_CLIENT_AVAILABLE = False


class ImportOptionsDialog(QDialog):
    """
    Import options dialog for per-operation AI conversion choice.

    Allows user to override default AI conversion setting for a specific
    import operation. Displays file information and AI availability status.

    Implements FR-055: AI-Enhanced Conversion option with per-operation override.

    Args:
        format_type: Source format (e.g., "docx", "markdown")
        filename: Name of file being imported
        default_use_ai: Default AI setting from Settings
        parent: Parent QWidget (optional)

    Example:
        ```python
        dialog = ImportOptionsDialog("docx", "document.docx", default_use_ai=True)
        if dialog.exec():
            use_ai = dialog.get_use_ai()
        ```
    """

    def __init__(
        self,
        format_type: str,
        filename: str,
        default_use_ai: bool,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize import options dialog."""
        super().__init__(parent)
        self.format_type = format_type
        self.filename = filename
        self.default_use_ai = default_use_ai
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the import options UI."""
        self.setWindowTitle(f"Import {self.format_type.upper()}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        info_label = QLabel(
            f"Converting '{self.filename}' from {self.format_type.upper()} to AsciiDoc."
        )
        layout.addWidget(info_label)

        self.ai_checkbox = QCheckBox("Use AI-enhanced conversion for this import")
        self.ai_checkbox.setChecked(self.default_use_ai)
        self.ai_checkbox.setToolTip(
            "AI conversion preserves complex formatting like nested lists and tables.\n"
            "Requires ANTHROPIC_API_KEY environment variable and may incur costs."
        )

        if not CLAUDE_CLIENT_AVAILABLE:
            self.ai_checkbox.setEnabled(False)
            self.ai_checkbox.setToolTip(
                "Claude AI is not available (missing anthropic library or API key)"
            )

        layout.addWidget(self.ai_checkbox)

        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("Import")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def get_use_ai(self) -> bool:
        """
        Get the user's choice for AI conversion.

        Returns:
            True if user chose AI conversion and it's available, False otherwise
        """
        return self.ai_checkbox.isChecked() if CLAUDE_CLIENT_AVAILABLE else False


class ExportOptionsDialog(QDialog):
    """
    Export options dialog for per-operation AI conversion choice.

    Allows user to override default AI conversion setting for a specific
    export operation. Displays format information and AI availability status.

    Implements FR-055: AI-Enhanced Conversion option with per-operation override.

    Args:
        format_type: Target format (e.g., "markdown", "html")
        default_use_ai: Default AI setting from Settings
        parent: Parent QWidget (optional)

    Example:
        ```python
        dialog = ExportOptionsDialog("markdown", default_use_ai=False)
        if dialog.exec():
            use_ai = dialog.get_use_ai()
        ```
    """

    def __init__(
        self, format_type: str, default_use_ai: bool, parent: Optional[QWidget] = None
    ) -> None:
        """Initialize export options dialog."""
        super().__init__(parent)
        self.format_type = format_type
        self.default_use_ai = default_use_ai
        self.use_ai = default_use_ai
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the export options UI."""
        self.setWindowTitle(f"Export to {self.format_type.upper()}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        info_label = QLabel(f"Exporting document to {self.format_type.upper()} format.")
        layout.addWidget(info_label)

        self.ai_checkbox = QCheckBox("Use AI-enhanced conversion for this export")
        self.ai_checkbox.setChecked(self.default_use_ai)
        self.ai_checkbox.setToolTip(
            "AI conversion preserves complex formatting like nested lists and tables.\n"
            "Requires ANTHROPIC_API_KEY environment variable and may incur costs."
        )

        if not CLAUDE_CLIENT_AVAILABLE:
            self.ai_checkbox.setEnabled(False)
            self.ai_checkbox.setToolTip(
                "Claude AI is not available (missing anthropic library or API key)"
            )

        layout.addWidget(self.ai_checkbox)

        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("Export")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def get_use_ai(self) -> bool:
        """
        Get the user's choice for AI conversion.

        Returns:
            True if user chose AI conversion and it's available, False otherwise
        """
        return self.ai_checkbox.isChecked() if CLAUDE_CLIENT_AVAILABLE else False


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
