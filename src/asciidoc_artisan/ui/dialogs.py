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

import os  # For reading environment variables (API keys)
from typing import Optional  # For type hints (helps catch bugs)

# Import Qt widgets we need for building the UI
from PySide6.QtWidgets import (
    QCheckBox,  # Checkbox widget (on/off toggle)
    QComboBox,  # Dropdown menu widget
    QDialog,  # Base class for pop-up windows
    QGroupBox,  # Box that groups related widgets together
    QHBoxLayout,  # Horizontal layout manager
    QLabel,  # Text label widget
    QPushButton,  # Clickable button widget
    QVBoxLayout,  # Vertical layout manager
    QWidget,  # Base class for all UI widgets
)

# Import our Settings data class
from asciidoc_artisan.core import Settings

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
            "Use local Ollama AI for document conversions\n"
            "Runs on your computer - no cloud services required"
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
            "• Install models with: ollama pull <model-name>\n"
            "• See docs/OLLAMA_SETUP.md for more information"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { color: gray; font-size: 10pt; }")
        ollama_layout.addWidget(info_label)

        ollama_group.setLayout(ollama_layout)
        layout.addWidget(ollama_group)

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
            Settings instance with updated Ollama configuration
        """
        # Store Ollama enabled state
        self.settings.ollama_enabled = self.ollama_enabled_checkbox.isChecked()

        # Store selected model if available
        if self.models and self.model_combo.currentIndex() >= 0:
            self.settings.ollama_model = self.model_combo.currentText()
        else:
            self.settings.ollama_model = None

        return self.settings
