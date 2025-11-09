"""
===============================================================================
USER DIALOGS - Pop-up Windows for Settings and Configuration
===============================================================================

FILE PURPOSE:
This file contains dialog windows (pop-up windows) that let users change
settings and configure features. When you click Edit → Preferences in the menu,
these dialogs appear.

WHAT THIS FILE CONTAINS:
1. Helper Functions: Reusable code for creating dialog buttons
2. PreferencesDialog: Main settings window (AI conversion)
3. OllamaSettingsDialog: AI model selection window

FOR BEGINNERS - WHAT IS A DIALOG?:
A "dialog" is a pop-up window that asks for user input or shows settings.
Examples: "Save file" dialogs, "Confirm delete" dialogs, preferences windows.

Qt provides QDialog as the base class for all dialog windows. Our dialogs
inherit from QDialog and add custom UI elements (checkboxes, buttons, etc.).

KEY QT CONCEPTS:
- QDialog: Base class for pop-up windows
- exec(): Shows dialog and waits for user to click OK/Cancel
- accept(): User clicked OK - save changes
- reject(): User clicked Cancel - discard changes
- Signals/Slots: When button clicked → call function

USAGE PATTERN:
    dialog = PreferencesDialog(settings)  # Create dialog
    if dialog.exec():  # Show dialog, wait for user
        settings = dialog.get_settings()  # User clicked OK - get new settings
        save_settings(settings)  # Save to disk
"""

import logging  # For debug logging
import os  # For reading environment variables (API keys)
from typing import Any, Optional  # For type hints (helps catch bugs)

from PySide6.QtCore import Qt  # Qt constants and enums

# Import Qt widgets we need for building the UI
from PySide6.QtWidgets import (
    QCheckBox,  # Checkbox widget (on/off toggle)
    QComboBox,  # Dropdown menu widget
    QDialog,  # Base class for pop-up windows
    QGroupBox,  # Box that groups related widgets together
    QHBoxLayout,  # Horizontal layout manager
    QLabel,  # Text label widget
    QMessageBox,  # Message box for confirmations
    QPushButton,  # Clickable button widget
    QSpinBox,  # Number input widget with up/down arrows
    QTableWidget,  # Table widget for displaying data
    QTableWidgetItem,  # Item for QTableWidget cells
    QVBoxLayout,  # Vertical layout manager
    QWidget,  # Base class for all UI widgets
)

# Import our Settings data class
from asciidoc_artisan.core import Settings

logger = logging.getLogger(__name__)

# === HELPER FUNCTIONS ===
# These functions are reused by multiple dialogs to avoid code duplication


def _create_ok_cancel_buttons(dialog: QDialog) -> QHBoxLayout:
    """
    Create Standard OK/Cancel Buttons for Dialogs.

    WHY THIS EXISTS:
    Every dialog needs OK and Cancel buttons. Instead of writing the same
    10 lines of code in every dialog, we write it once here and reuse it.
    This follows the DRY principle: "Don't Repeat Yourself"

    WHAT IT DOES:
    1. Creates a horizontal layout (buttons side by side)
    2. Adds a "stretch" (pushes buttons to the right side)
    3. Creates OK button → connected to dialog.accept()
    4. Creates Cancel button → connected to dialog.reject()
    5. Returns the layout ready to add to your dialog

    HOW TO USE:
        layout = QVBoxLayout()
        # ... add your dialog widgets here ...
        layout.addLayout(_create_ok_cancel_buttons(self))  # Add buttons at bottom

    PARAMETERS:
        dialog: The QDialog that these buttons belong to. We need this to
                connect the buttons to the dialog's accept/reject methods.

    RETURNS:
        A QHBoxLayout containing OK and Cancel buttons, properly connected.

    TECHNICAL NOTE:
    - dialog.accept() closes the dialog and returns True from exec()
    - dialog.reject() closes the dialog and returns False from exec()
    """
    # Create horizontal layout for buttons (side by side)
    button_layout = QHBoxLayout()

    # Add a "stretch" - this pushes buttons to the right side of the window
    # Without this, buttons would be left-aligned (looks bad)
    button_layout.addStretch()

    # === CREATE OK BUTTON ===
    ok_button = QPushButton("OK")  # Create button with text "OK"

    # Connect button click to dialog.accept()
    # When user clicks OK: dialog closes, exec() returns True
    ok_button.clicked.connect(dialog.accept)

    # Add OK button to layout
    button_layout.addWidget(ok_button)

    # === CREATE CANCEL BUTTON ===
    cancel_button = QPushButton("Cancel")  # Create button with text "Cancel"

    # Connect button click to dialog.reject()
    # When user clicks Cancel: dialog closes, exec() returns False
    cancel_button.clicked.connect(dialog.reject)

    # Add Cancel button to layout
    button_layout.addWidget(cancel_button)

    # Return the complete layout
    return button_layout


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
            "Use Claude AI for better document conversions\nPreserves complex formatting like nested lists and tables"
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
        layout.addLayout(_create_ok_cancel_buttons(self))

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
            Settings instance with updated ai_conversion_enabled
        """
        self.settings.ai_conversion_enabled = self.ai_enabled_checkbox.isChecked()
        return self.settings


class OllamaSettingsDialog(QDialog):
    """
    Ollama AI settings dialog with model selection.

    Allows users to:
    - Enable/disable Ollama AI integration
    - Select which AI model to use for conversions
    - View service status and installed models

    Args:
        settings: Current Settings instance to edit
        parent: Parent QWidget (optional)

    Example:
        ```python
        dialog = OllamaSettingsDialog(self.settings)
        if dialog.exec():
            self.settings = dialog.get_settings()
            self._save_settings()
        ```
    """

    def __init__(self, settings: Settings, parent: Optional[QWidget] = None) -> None:
        """Initialize Ollama settings dialog."""
        super().__init__(parent)
        self.settings = settings
        self.models = []
        self._init_ui()
        self._load_models()

    def _init_ui(self) -> None:
        """Initialize the Ollama settings UI."""
        self.setWindowTitle("Ollama AI Settings")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Ollama Settings Group
        ollama_group = QGroupBox("Ollama AI Configuration")
        ollama_layout = QVBoxLayout()

        # Enable/Disable Toggle
        self.ollama_enabled_checkbox = QCheckBox("Enable Ollama AI integration")
        self.ollama_enabled_checkbox.setChecked(
            getattr(self.settings, "ollama_enabled", False)
        )
        self.ollama_enabled_checkbox.setToolTip(
            "Use local Ollama AI for document conversions\nRuns on your computer - no cloud services required"
        )
        self.ollama_enabled_checkbox.stateChanged.connect(self._on_enabled_changed)
        ollama_layout.addWidget(self.ollama_enabled_checkbox)

        # Model Selection
        model_layout = QHBoxLayout()
        model_label = QLabel("AI Model:")
        model_layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.setToolTip("Select which AI model to use for conversions")
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.model_combo)

        ollama_layout.addLayout(model_layout)

        # Service Status
        self.status_label = QLabel("Checking Ollama service...")
        self.status_label.setStyleSheet("QLabel { color: gray; font-size: 10pt; }")
        ollama_layout.addWidget(self.status_label)

        # Information Label
        info_label = QLabel(
            "• Ollama runs locally on your computer\n"
            "• No API keys or cloud services required\n"
            "• Install models with: ollama pull qwen2.5-coder:7b\n"
            "• See docs/OLLAMA_SETUP.md for more information"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { color: gray; font-size: 10pt; }")
        ollama_layout.addWidget(info_label)

        ollama_group.setLayout(ollama_layout)
        layout.addWidget(ollama_group)

        # === Chat Settings Group (v1.7.0) ===
        chat_group = QGroupBox("Chat Settings (Experimental)")
        chat_layout = QVBoxLayout()

        # Enable/Disable Chat Toggle
        self.chat_enabled_checkbox = QCheckBox("Enable AI chat interface")
        self.chat_enabled_checkbox.setChecked(
            getattr(self.settings, "ollama_chat_enabled", False)
        )
        self.chat_enabled_checkbox.setToolTip(
            "Show chat bar and panel for interactive conversations with AI"
        )
        chat_layout.addWidget(self.chat_enabled_checkbox)

        # Max History Setting
        history_layout = QHBoxLayout()
        history_label = QLabel("Max chat history:")
        history_layout.addWidget(history_label)

        self.max_history_spin = QSpinBox()
        self.max_history_spin.setRange(10, 500)
        self.max_history_spin.setValue(
            getattr(self.settings, "ollama_chat_max_history", 100)
        )
        self.max_history_spin.setToolTip(
            "Maximum number of messages to store in chat history\nOlder messages are automatically removed"
        )
        history_layout.addWidget(self.max_history_spin)
        history_layout.addStretch()

        chat_layout.addLayout(history_layout)

        # Default Context Mode
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Default context mode:")
        mode_layout.addWidget(mode_label)

        self.context_mode_combo = QComboBox()
        self.context_mode_combo.addItems(
            [
                "Document Q&A",
                "Syntax Help",
                "General Chat",
                "Editing Suggestions",
            ]
        )
        self.context_mode_combo.setToolTip(
            "Default interaction mode when chat starts\nYou can change this in the chat bar at any time"
        )

        # Map current setting to combo index
        current_mode = getattr(self.settings, "ollama_chat_context_mode", "document")
        mode_index_map = {
            "document": 0,
            "syntax": 1,
            "general": 2,
            "editing": 3,
        }
        self.context_mode_combo.setCurrentIndex(mode_index_map.get(current_mode, 0))

        mode_layout.addWidget(self.context_mode_combo)
        mode_layout.addStretch()

        chat_layout.addLayout(mode_layout)

        # Send Document Content Toggle
        self.send_document_checkbox = QCheckBox(
            "Include document content in context-aware modes"
        )
        self.send_document_checkbox.setChecked(
            getattr(self.settings, "ollama_chat_send_document", True)
        )
        self.send_document_checkbox.setToolTip(
            "For 'Document Q&A' and 'Editing Suggestions' modes:\n"
            "Send current document content to AI for better context\n"
            "Disable if you have privacy concerns about local documents"
        )
        chat_layout.addWidget(self.send_document_checkbox)

        # Chat Information Label
        chat_info_label = QLabel(
            "• Chat provides 4 interaction modes for different needs\n"
            "• All conversations are stored locally\n"
            "• Configure Anthropic API key via Tools → AI Status → Anthropic Settings"
        )
        chat_info_label.setWordWrap(True)
        chat_info_label.setStyleSheet("QLabel { color: gray; font-size: 10pt; }")
        chat_layout.addWidget(chat_info_label)

        chat_group.setLayout(chat_layout)
        layout.addWidget(chat_group)

        # Dialog Buttons
        layout.addLayout(_create_ok_cancel_buttons(self))

        # Update enabled state of controls
        self._on_enabled_changed()

    def _load_models(self) -> None:
        """Load available Ollama models from the service."""
        import logging

        logger = logging.getLogger(__name__)

        try:
            import ollama

            try:
                response = ollama.list()
                logger.info(f"Ollama API response type: {type(response)}")

                # Handle both old API (dict with "models" key) and new API (direct list)
                if isinstance(response, dict):
                    models_data = response.get("models", [])
                    logger.info(f"Using dict API - found {len(models_data)} models")
                elif hasattr(response, "models"):
                    models_data = (
                        response.models
                        if isinstance(response.models, list)
                        else list(response.models)
                    )
                    logger.info(
                        f"Using new API with .models attribute - found {len(models_data)} models"
                    )
                else:
                    # Assume response is the models list directly
                    models_data = response if isinstance(response, list) else []
                    logger.info(
                        f"Using direct list API - found {len(models_data)} models"
                    )

                if not models_data:
                    self.status_label.setText("⚠️ No models installed")
                    self.status_label.setStyleSheet(
                        "QLabel { color: orange; font-size: 10pt; }"
                    )
                    self.model_combo.addItem("No models available")
                    self.model_combo.setEnabled(False)
                    return

                # Extract model names properly
                self.models = []
                for model in models_data:
                    # Handle both dict (old API) and object (new API) formats
                    if isinstance(model, dict):
                        name = model.get("name") or model.get("model", "Unknown")
                    elif hasattr(model, "model"):
                        name = model.model
                    elif hasattr(model, "name"):
                        name = model.name
                    else:
                        name = str(model)

                    logger.info(f"Found model: {name}")
                    self.models.append(name)
                    self.model_combo.addItem(name)

                # Select the previously chosen model or first one
                saved_model = getattr(self.settings, "ollama_model", None)
                if saved_model and saved_model in self.models:
                    index = self.models.index(saved_model)
                    self.model_combo.setCurrentIndex(index)

                self.status_label.setText(
                    f"✅ Ollama service running - {len(self.models)} model(s) available"
                )
                self.status_label.setStyleSheet(
                    "QLabel { color: green; font-size: 10pt; }"
                )

            except Exception as e:
                logger.error(
                    f"Ollama service error: {type(e).__name__}: {e}", exc_info=True
                )
                self.status_label.setText(f"❌ Ollama service not running: {str(e)}")
                self.status_label.setStyleSheet(
                    "QLabel { color: red; font-size: 10pt; }"
                )
                self.model_combo.addItem("Service not available")
                self.model_combo.setEnabled(False)

        except ImportError as e:
            logger.error(f"Ollama import error: {e}", exc_info=True)
            self.status_label.setText("❌ Ollama library not installed")
            self.status_label.setStyleSheet("QLabel { color: red; font-size: 10pt; }")
            self.model_combo.addItem("Library not installed")
            self.model_combo.setEnabled(False)

    def _on_enabled_changed(self) -> None:
        """Handle enable/disable checkbox state change."""
        enabled = self.ollama_enabled_checkbox.isChecked()
        self.model_combo.setEnabled(enabled and len(self.models) > 0)

        # Update parent window's status bar immediately
        self._update_parent_status_bar()

    def _on_model_changed(self) -> None:
        """Handle model selection change."""
        # Update parent window's status bar immediately
        self._update_parent_status_bar()

    def _update_parent_status_bar(self) -> None:
        """Update parent window's status bar with current settings."""
        if self.parent() and hasattr(self.parent(), "_update_ai_status_bar"):
            # Temporarily update settings
            self.settings.ollama_enabled = self.ollama_enabled_checkbox.isChecked()
            if self.models and self.model_combo.currentIndex() >= 0:
                self.settings.ollama_model = self.model_combo.currentText()
            else:
                self.settings.ollama_model = None

            # Update parent's status bar
            self.parent()._update_ai_status_bar()

    def get_settings(self) -> Settings:
        """
        Get updated settings from dialog.

        Returns:
            Settings instance with updated Ollama configuration and chat settings
        """
        # Store Ollama enabled state
        self.settings.ollama_enabled = self.ollama_enabled_checkbox.isChecked()

        # Store selected model if available
        if self.models and self.model_combo.currentIndex() >= 0:
            self.settings.ollama_model = self.model_combo.currentText()
        else:
            self.settings.ollama_model = None

        # === Store Chat Settings (v1.7.0) ===
        self.settings.ollama_chat_enabled = self.chat_enabled_checkbox.isChecked()
        self.settings.ollama_chat_max_history = self.max_history_spin.value()
        self.settings.ollama_chat_send_document = (
            self.send_document_checkbox.isChecked()
        )

        # Map context mode combo index to setting value
        mode_value_map = {
            0: "document",
            1: "syntax",
            2: "general",
            3: "editing",
        }
        self.settings.ollama_chat_context_mode = mode_value_map.get(
            self.context_mode_combo.currentIndex(), "document"
        )

        return self.settings


class SettingsEditorDialog(QDialog):
    """
    Settings Editor dialog for viewing and editing all application settings.

    Allows users to:
    - View all stored settings in a table format
    - Edit individual settings with real-time validation
    - Clear all settings to defaults
    - Save changes automatically on edit

    Args:
        settings: Current Settings instance to edit
        settings_manager: SettingsManager instance for saving
        parent: Parent QWidget (optional)

    Example:
        ```python
        dialog = SettingsEditorDialog(self.settings, self.settings_manager)
        if dialog.exec():
            # Settings have been saved automatically
            self._refresh_from_settings()
        ```
    """

    def __init__(
        self,
        settings: Settings,
        settings_manager: Any,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize settings editor dialog."""
        super().__init__(parent)
        self.settings = settings
        self.settings_manager = settings_manager
        self.parent_window = parent
        self._init_ui()
        self._load_settings()

    def _init_ui(self) -> None:
        """Initialize the settings editor UI."""
        self.setWindowTitle("Application Settings")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Edit Application Settings")
        header_label.setStyleSheet("QLabel { font-size: 14pt; font-weight: bold; }")
        layout.addWidget(header_label)

        info_label = QLabel(
            "Changes are saved automatically. Click 'Clear All' to reset to defaults."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { color: gray; font-size: 10pt; }")
        layout.addWidget(info_label)

        # Settings Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Setting", "Value", "Type"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnWidth(0, 250)
        self.table.setColumnWidth(1, 350)
        self.table.setColumnWidth(2, 150)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        clear_all_button = QPushButton("Clear All Settings")
        clear_all_button.setToolTip("Reset all settings to default values")
        clear_all_button.clicked.connect(self._clear_all_settings)
        button_layout.addWidget(clear_all_button)

        button_layout.addStretch()

        # Close button (settings are saved automatically)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _load_settings(self) -> None:
        """Load settings into the table."""
        # Convert settings to dictionary
        settings_dict = self.settings.to_dict()

        # Block signals while populating
        self.table.blockSignals(True)

        # Set row count
        self.table.setRowCount(len(settings_dict))

        # Populate table
        row = 0
        for key, value in sorted(settings_dict.items()):
            # Setting name (read-only)
            name_item = QTableWidgetItem(key)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, name_item)

            # Setting value (editable)
            value_str = self._value_to_string(value)
            value_item = QTableWidgetItem(value_str)
            self.table.setItem(row, 1, value_item)

            # Setting type (read-only)
            type_name = type(value).__name__
            type_item = QTableWidgetItem(type_name)
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, type_item)

            row += 1

        # Re-enable signals
        self.table.blockSignals(False)

    def _value_to_string(self, value: Any) -> str:
        """Convert a setting value to string for display."""
        if value is None:
            return "None"
        elif isinstance(value, bool):
            return "True" if value else "False"
        elif isinstance(value, (list, dict)):
            return str(value)
        else:
            return str(value)

    def _string_to_value(self, value_str: str, value_type: str) -> Any:
        """Convert string back to appropriate type."""
        if value_type == "NoneType":
            return None
        elif value_type == "bool":
            return value_str.lower() in ("true", "1", "yes")
        elif value_type == "int":
            try:
                return int(value_str)
            except ValueError:
                return 0
        elif value_type == "float":
            try:
                return float(value_str)
            except ValueError:
                return 0.0
        elif value_type == "list":
            try:
                import ast

                return ast.literal_eval(value_str)
            except (ValueError, SyntaxError):
                return []
        elif value_type == "dict":
            try:
                import ast

                return ast.literal_eval(value_str)
            except (ValueError, SyntaxError):
                return {}
        else:
            return value_str

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """Handle setting value change - save automatically."""
        # Only handle value column changes
        if item.column() != 1:
            return

        row = item.row()
        setting_name = self.table.item(row, 0).text()
        new_value_str = item.text()
        value_type = self.table.item(row, 2).text()

        # Convert string to appropriate type
        new_value = self._string_to_value(new_value_str, value_type)

        # Update settings object
        setattr(self.settings, setting_name, new_value)

        # Save settings automatically
        self.settings_manager.save_settings(self.settings, self.parent_window)

        # Refresh parent window if available
        if self.parent_window and hasattr(self.parent_window, "_refresh_from_settings"):
            self.parent_window._refresh_from_settings()

    def _clear_all_settings(self) -> None:
        """Clear all settings to defaults after confirmation."""
        reply = QMessageBox.question(
            self,
            "Clear All Settings",
            "Are you sure you want to reset all settings to defaults?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Create new default settings
            self.settings = Settings()

            # Save to disk
            self.settings_manager.save_settings(self.settings, self.parent_window)

            # Reload table
            self._load_settings()

            # Refresh parent window if available
            if self.parent_window and hasattr(
                self.parent_window, "_refresh_from_settings"
            ):
                self.parent_window._refresh_from_settings()

            QMessageBox.information(
                self, "Settings Cleared", "All settings have been reset to defaults."
            )


class FontSettingsDialog(QDialog):
    """
    Font Settings dialog for customizing fonts in editor, preview, and chat.

    Allows users to:
    - Set font family for editor pane (monospace recommended)
    - Set font size for editor pane
    - Set font family for preview pane
    - Set font size for preview pane
    - Set font family for chat pane
    - Set font size for chat pane

    Args:
        settings: Current Settings instance to edit
        parent: Parent QWidget (optional)

    Example:
        ```python
        dialog = FontSettingsDialog(self.settings)
        if dialog.exec():
            new_settings = dialog.get_settings()
            self._apply_font_settings(new_settings)
        ```
    """

    def __init__(self, settings: Settings, parent: Optional[QWidget] = None) -> None:
        """Initialize font settings dialog."""
        super().__init__(parent)
        self.settings = settings
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the font settings UI."""
        self.setWindowTitle("Font Settings")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Customize Fonts")
        header_label.setStyleSheet("QLabel { font-size: 14pt; font-weight: bold; }")
        layout.addWidget(header_label)

        info_label = QLabel(
            "Set font family and size for editor, preview, and chat panes."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { color: gray; font-size: 10pt; }")
        layout.addWidget(info_label)

        # Editor Font Group
        editor_group = QGroupBox("Editor Font")
        editor_layout = QVBoxLayout()

        # Editor font family
        editor_family_layout = QHBoxLayout()
        editor_family_layout.addWidget(QLabel("Font Family:"))
        self.editor_font_combo = QComboBox()
        self._populate_font_list(self.editor_font_combo)
        self.editor_font_combo.setCurrentText(self.settings.editor_font_family)
        editor_family_layout.addWidget(self.editor_font_combo)
        editor_layout.addLayout(editor_family_layout)

        # Editor font size
        editor_size_layout = QHBoxLayout()
        editor_size_layout.addWidget(QLabel("Font Size:"))
        self.editor_size_spin = QSpinBox()
        self.editor_size_spin.setRange(6, 72)
        self.editor_size_spin.setValue(self.settings.editor_font_size)
        self.editor_size_spin.setSuffix(" pt")
        editor_size_layout.addWidget(self.editor_size_spin)
        editor_size_layout.addStretch()
        editor_layout.addLayout(editor_size_layout)

        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)

        # Preview Font Group
        preview_group = QGroupBox("Preview Font")
        preview_layout = QVBoxLayout()

        # Preview font family
        preview_family_layout = QHBoxLayout()
        preview_family_layout.addWidget(QLabel("Font Family:"))
        self.preview_font_combo = QComboBox()
        self._populate_font_list(self.preview_font_combo)
        self.preview_font_combo.setCurrentText(self.settings.preview_font_family)
        preview_family_layout.addWidget(self.preview_font_combo)
        preview_layout.addLayout(preview_family_layout)

        # Preview font size
        preview_size_layout = QHBoxLayout()
        preview_size_layout.addWidget(QLabel("Font Size:"))
        self.preview_size_spin = QSpinBox()
        self.preview_size_spin.setRange(6, 72)
        self.preview_size_spin.setValue(self.settings.preview_font_size)
        self.preview_size_spin.setSuffix(" pt")
        preview_size_layout.addWidget(self.preview_size_spin)
        preview_size_layout.addStretch()
        preview_layout.addLayout(preview_size_layout)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Chat Font Group
        chat_group = QGroupBox("Chat Font")
        chat_layout = QVBoxLayout()

        # Chat font family
        chat_family_layout = QHBoxLayout()
        chat_family_layout.addWidget(QLabel("Font Family:"))
        self.chat_font_combo = QComboBox()
        self._populate_font_list(self.chat_font_combo)
        self.chat_font_combo.setCurrentText(self.settings.chat_font_family)
        chat_family_layout.addWidget(self.chat_font_combo)
        chat_layout.addLayout(chat_family_layout)

        # Chat font size
        chat_size_layout = QHBoxLayout()
        chat_size_layout.addWidget(QLabel("Font Size:"))
        self.chat_size_spin = QSpinBox()
        self.chat_size_spin.setRange(6, 72)
        self.chat_size_spin.setValue(self.settings.chat_font_size)
        self.chat_size_spin.setSuffix(" pt")
        chat_size_layout.addWidget(self.chat_size_spin)
        chat_size_layout.addStretch()
        chat_layout.addLayout(chat_size_layout)

        chat_group.setLayout(chat_layout)
        layout.addWidget(chat_group)

        # Dialog Buttons
        layout.addLayout(_create_ok_cancel_buttons(self))

    def _populate_font_list(self, combo: QComboBox) -> None:
        """Populate combo box with common fonts."""
        # Common monospace fonts for editor
        monospace_fonts = [
            "Courier New",
            "Consolas",
            "Monaco",
            "Menlo",
            "Ubuntu Mono",
            "Fira Code",
            "Source Code Pro",
            "JetBrains Mono",
            "DejaVu Sans Mono",
        ]

        # Common sans-serif fonts for preview/chat
        sans_fonts = [
            "Arial",
            "Helvetica",
            "Verdana",
            "Tahoma",
            "Trebuchet MS",
            "Segoe UI",
            "Ubuntu",
            "Roboto",
            "Open Sans",
        ]

        # Common serif fonts
        serif_fonts = [
            "Times New Roman",
            "Georgia",
            "Garamond",
            "Palatino",
            "Book Antiqua",
        ]

        # Combine all fonts
        all_fonts = sorted(set(monospace_fonts + sans_fonts + serif_fonts))
        combo.addItems(all_fonts)

    def get_settings(self) -> Settings:
        """
        Get updated settings with font changes.

        Returns:
            Settings instance with new font values
        """
        self.settings.editor_font_family = self.editor_font_combo.currentText()
        self.settings.editor_font_size = self.editor_size_spin.value()
        self.settings.preview_font_family = self.preview_font_combo.currentText()
        self.settings.preview_font_size = self.preview_size_spin.value()
        self.settings.chat_font_family = self.chat_font_combo.currentText()
        self.settings.chat_font_size = self.chat_size_spin.value()

        return self.settings
