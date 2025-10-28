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

        # Grammar Settings Group (v1.3: Legendary Grammar System)
        grammar_group = QGroupBox("Grammar Checking")
        grammar_layout = QVBoxLayout()

        self.grammar_enabled_checkbox = QCheckBox("Enable automatic grammar checking")
        self.grammar_enabled_checkbox.setChecked(
            getattr(self.settings, "grammar_enabled", True)
        )
        self.grammar_enabled_checkbox.setToolTip(
            "Automatically check grammar as you type\n"
            "Uses LanguageTool (offline) and Ollama AI (optional)"
        )
        grammar_layout.addWidget(self.grammar_enabled_checkbox)

        self.grammar_ollama_checkbox = QCheckBox("Enable AI-powered style suggestions")
        self.grammar_ollama_checkbox.setChecked(
            getattr(self.settings, "grammar_use_ollama", True)
        )
        self.grammar_ollama_checkbox.setToolTip(
            "Use Ollama AI for context-aware style checking\n"
            "Provides deeper insights beyond basic grammar rules"
        )
        grammar_layout.addWidget(self.grammar_ollama_checkbox)

        # Grammar mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Checking mode:"))
        self.grammar_mode_combo = QComboBox()
        self.grammar_mode_combo.addItems(
            [
                "Hybrid (LanguageTool + AI)",
                "LanguageTool Only",
                "Ollama AI Only",
                "Disabled",
            ]
        )
        current_mode = getattr(self.settings, "grammar_mode", "hybrid")
        mode_map = {"hybrid": 0, "languagetool": 1, "ollama": 2, "disabled": 3}
        self.grammar_mode_combo.setCurrentIndex(mode_map.get(current_mode, 0))
        self.grammar_mode_combo.setToolTip(
            "Hybrid: Fast + smart (recommended)\n"
            "LanguageTool Only: Fastest, rules-based\n"
            "Ollama AI Only: Context-aware but slower\n"
            "Disabled: Turn off grammar checking"
        )
        mode_layout.addWidget(self.grammar_mode_combo)
        mode_layout.addStretch()
        grammar_layout.addLayout(mode_layout)

        # Performance profile selector
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Performance:"))
        self.grammar_profile_combo = QComboBox()
        self.grammar_profile_combo.addItems(
            [
                "Balanced (Recommended)",
                "Real-time (Fastest)",
                "Thorough (Most Accurate)",
            ]
        )
        current_profile = getattr(self.settings, "grammar_profile", "balanced")
        profile_map = {"balanced": 0, "realtime": 1, "thorough": 2}
        self.grammar_profile_combo.setCurrentIndex(profile_map.get(current_profile, 0))
        self.grammar_profile_combo.setToolTip(
            "Balanced: Good speed and accuracy\n"
            "Real-time: Fastest, no AI suggestions\n"
            "Thorough: Slower but most comprehensive"
        )
        profile_layout.addWidget(self.grammar_profile_combo)
        profile_layout.addStretch()
        grammar_layout.addLayout(profile_layout)

        # Information Label
        grammar_info_label = QLabel(
            "• F7: Check grammar now\n"
            "• Ctrl+.: Navigate to next issue\n"
            "• Ctrl+I: Ignore current suggestion\n"
            "• Grammar menu for more options"
        )
        grammar_info_label.setWordWrap(True)
        grammar_info_label.setStyleSheet("QLabel { color: gray; font-size: 10pt; }")
        grammar_layout.addWidget(grammar_info_label)

        grammar_group.setLayout(grammar_layout)
        layout.addWidget(grammar_group)

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
            Settings instance with updated ai_conversion_enabled and grammar values
        """
        self.settings.ai_conversion_enabled = self.ai_enabled_checkbox.isChecked()

        # Grammar settings (v1.3)
        self.settings.grammar_enabled = self.grammar_enabled_checkbox.isChecked()
        self.settings.grammar_use_ollama = self.grammar_ollama_checkbox.isChecked()

        # Grammar mode
        mode_index = self.grammar_mode_combo.currentIndex()
        mode_map = {0: "hybrid", 1: "languagetool", 2: "ollama", 3: "disabled"}
        self.settings.grammar_mode = mode_map.get(mode_index, "hybrid")

        # Performance profile
        profile_index = self.grammar_profile_combo.currentIndex()
        profile_map = {0: "balanced", 1: "realtime", 2: "thorough"}
        self.settings.grammar_profile = profile_map.get(profile_index, "balanced")

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
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

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
