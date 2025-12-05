"""
Ollama Settings Dialog - AI model selection and chat configuration.

Extracted from dialogs.py for MA principle compliance.
Handles Ollama AI integration, model selection, and chat settings.

Implements FR-042: Ollama AI Integration configuration.
"""

import logging
from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.core import Settings
from asciidoc_artisan.ui.dialog_factory import create_ok_cancel_buttons

logger = logging.getLogger(__name__)


class OllamaSettingsDialog(QDialog):
    """
    Ollama AI settings dialog with model selection.

    Allows users to:
    - Enable/disable Ollama AI integration
    - Select which AI model to use for conversions
    - View service status and installed models
    - Configure chat settings

    Args:
        settings: Current Settings instance to edit
        parent: Parent QWidget (optional)
    """

    def __init__(self, settings: Settings, parent: QWidget | None = None) -> None:
        """Initialize Ollama settings dialog."""
        super().__init__(parent)
        self.settings = settings
        self.models: list[str] = []
        self._init_ui()
        self._load_models()
        # Re-evaluate enabled state after models are loaded
        self._on_enabled_changed()

    def _create_model_selector(self) -> QHBoxLayout:
        """Create model selection layout."""
        model_layout = QHBoxLayout()
        model_label = QLabel("AI Model:")
        model_layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.setToolTip("Select which AI model to use for conversions")
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.model_combo)

        # Browse Models button
        self.browse_btn = QPushButton("Browse All Models...")
        self.browse_btn.setToolTip("Browse and download models from Ollama library")
        self.browse_btn.clicked.connect(self._open_model_browser)
        model_layout.addWidget(self.browse_btn)

        return model_layout

    def _create_ollama_settings_group(self) -> QGroupBox:
        """Create Ollama AI configuration group."""
        ollama_group = QGroupBox("Ollama AI Configuration")
        ollama_layout = QVBoxLayout()

        # Enable/Disable Toggle
        self.ollama_enabled_checkbox = QCheckBox("Enable Ollama AI integration")
        self.ollama_enabled_checkbox.setChecked(getattr(self.settings, "ollama_enabled", False))
        self.ollama_enabled_checkbox.setToolTip(
            "Use local Ollama AI for document conversions\nRuns on your computer - no cloud services required"
        )
        self.ollama_enabled_checkbox.stateChanged.connect(self._on_enabled_changed)
        ollama_layout.addWidget(self.ollama_enabled_checkbox)

        # Model Selection
        ollama_layout.addLayout(self._create_model_selector())

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
        return ollama_group

    def _create_history_selector(self) -> QHBoxLayout:
        """Create chat history limit selector."""
        history_layout = QHBoxLayout()
        history_label = QLabel("Max chat history:")
        history_layout.addWidget(history_label)

        self.max_history_spin = QSpinBox()
        self.max_history_spin.setRange(10, 500)
        self.max_history_spin.setValue(getattr(self.settings, "ollama_chat_max_history", 100))
        self.max_history_spin.setToolTip(
            "Maximum number of messages to store in chat history\nOlder messages are automatically removed"
        )
        history_layout.addWidget(self.max_history_spin)
        history_layout.addStretch()

        return history_layout

    def _create_context_mode_selector(self) -> QHBoxLayout:
        """Create context mode selector."""
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Default context mode:")
        mode_layout.addWidget(mode_label)

        self.context_mode_combo = QComboBox()
        self.context_mode_combo.addItems(["Document Q&A", "Syntax Help", "General Chat", "Editing Suggestions"])
        self.context_mode_combo.setToolTip(
            "Default interaction mode when chat starts\nYou can change this in the chat bar at any time"
        )

        # Map current setting to combo index
        current_mode = getattr(self.settings, "ollama_chat_context_mode", "document")
        mode_index_map = {"document": 0, "syntax": 1, "general": 2, "editing": 3}
        self.context_mode_combo.setCurrentIndex(mode_index_map.get(current_mode, 0))

        mode_layout.addWidget(self.context_mode_combo)
        mode_layout.addStretch()

        return mode_layout

    def _create_chat_settings_group(self) -> QGroupBox:
        """Create chat settings configuration group."""
        chat_group = QGroupBox("Chat Settings (Experimental)")
        chat_layout = QVBoxLayout()

        # Enable/Disable Chat Toggle
        self.chat_enabled_checkbox = QCheckBox("Enable AI chat interface")
        self.chat_enabled_checkbox.setChecked(getattr(self.settings, "ollama_chat_enabled", False))
        self.chat_enabled_checkbox.setToolTip("Show chat bar and panel for interactive conversations with AI")
        chat_layout.addWidget(self.chat_enabled_checkbox)

        # Max History Setting
        chat_layout.addLayout(self._create_history_selector())

        # Default Context Mode
        chat_layout.addLayout(self._create_context_mode_selector())

        # Send Document Content Toggle
        self.send_document_checkbox = QCheckBox("Include document content in context-aware modes")
        self.send_document_checkbox.setChecked(getattr(self.settings, "ollama_chat_send_document", True))
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
        return chat_group

    def _init_ui(self) -> None:
        """Initialize the Ollama settings UI."""
        self.setWindowTitle("Ollama AI Settings")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Add Ollama and Chat configuration groups
        layout.addWidget(self._create_ollama_settings_group())
        layout.addWidget(self._create_chat_settings_group())

        # Dialog Buttons
        layout.addLayout(create_ok_cancel_buttons(self))

        # Update enabled state of controls
        self._on_enabled_changed()

    def _load_models(self) -> None:
        """Load available Ollama models from the service."""
        try:
            import ollama

            try:
                response = ollama.list()
                models_data = self._parse_ollama_response(response)

                if not models_data:
                    self._show_no_models_status()
                    return

                self._extract_model_names(models_data)
                self._populate_model_list()

            except Exception as e:
                logger.error(f"Ollama service error: {type(e).__name__}: {e}", exc_info=True)
                self._show_model_load_error(f"❌ Ollama service not running: {e!s}", "Service not available")

        except ImportError as e:
            logger.error(f"Ollama import error: {e}", exc_info=True)
            self._show_model_load_error("❌ Ollama library not installed", "Library not installed")

    def _parse_ollama_response(self, response: Any) -> list[Any]:
        """Parse Ollama API response handling different formats."""
        logger.info(f"Ollama API response type: {type(response)}")

        # Handle both old API (dict with "models" key) and new API (direct list)
        if isinstance(response, dict):
            models_data: list[Any] = response.get("models", [])
            logger.info(f"Using dict API - found {len(models_data)} models")
        elif hasattr(response, "models"):
            models_data = response.models if isinstance(response.models, list) else list(response.models)
            logger.info(f"Using new API with .models attribute - found {len(models_data)} models")
        else:
            # Assume response is the models list directly
            models_data = response if isinstance(response, list) else []
            logger.info(f"Using direct list API - found {len(models_data)} models")

        return models_data

    def _extract_model_names(self, models_data: list[Any]) -> None:
        """Extract model names from models data."""
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

    def _populate_model_list(self) -> None:
        """Populate model combo box and select saved model."""
        # Select the previously chosen model or first one
        saved_model = getattr(self.settings, "ollama_model", None)
        if saved_model and saved_model in self.models:
            index = self.models.index(saved_model)
            self.model_combo.setCurrentIndex(index)

        self.status_label.setText(f"✅ Ollama service running - {len(self.models)} model(s) available")
        self.status_label.setStyleSheet("QLabel { color: green; font-size: 10pt; }")

    def _show_no_models_status(self) -> None:
        """Show status when no models are installed."""
        self.status_label.setText("⚠️ No models installed")
        self.status_label.setStyleSheet("QLabel { color: orange; font-size: 10pt; }")
        self.model_combo.addItem("No models available")
        self.model_combo.setEnabled(False)

    def _show_model_load_error(self, status_text: str, combo_text: str) -> None:
        """Show error status when model loading fails."""
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet("QLabel { color: red; font-size: 10pt; }")
        self.model_combo.addItem(combo_text)
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

    def _open_model_browser(self) -> None:
        """Open the Ollama model browser dialog."""
        from asciidoc_artisan.ui.ollama_model_browser import OllamaModelBrowser

        browser = OllamaModelBrowser(self)
        browser.model_downloaded.connect(self._on_model_downloaded)
        browser.model_deleted.connect(self._on_model_deleted)
        browser.exec()

    def _on_model_downloaded(self, model_name: str) -> None:
        """Handle when a new model is downloaded from the browser."""
        logger.info(f"Model downloaded: {model_name}")
        self._refresh_model_list()
        # Select the newly downloaded model
        if model_name in self.models:
            self.model_combo.setCurrentIndex(self.models.index(model_name))
        # Refresh main window's chat models
        self._notify_parent_model_change(f"Downloaded Ollama model: {model_name}")

    def _on_model_deleted(self, model_name: str) -> None:
        """Handle when a model is deleted from the browser."""
        logger.info(f"Model deleted: {model_name}")
        self._refresh_model_list()
        # Refresh main window's chat models
        self._notify_parent_model_change(f"Deleted Ollama model: {model_name}")

    def _refresh_model_list(self) -> None:
        """Refresh the model combo box."""
        self.model_combo.clear()
        self.models.clear()
        self._load_models()

    def _notify_parent_model_change(self, message: str) -> None:
        """Notify parent window to refresh Ollama models."""
        if self.parent() and hasattr(self.parent(), "refresh_ollama_models"):
            self.parent().refresh_ollama_models(message)

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
        """Get updated settings from dialog."""
        # Store Ollama enabled state
        self.settings.ollama_enabled = self.ollama_enabled_checkbox.isChecked()

        # Store selected model if available
        if self.models and self.model_combo.currentIndex() >= 0:
            self.settings.ollama_model = self.model_combo.currentText()
        else:
            self.settings.ollama_model = None

        # Store Chat Settings (v1.7.0)
        self.settings.ollama_chat_enabled = self.chat_enabled_checkbox.isChecked()
        self.settings.ollama_chat_max_history = self.max_history_spin.value()
        self.settings.ollama_chat_send_document = self.send_document_checkbox.isChecked()

        # Map context mode combo index to setting value
        mode_value_map = {0: "document", 1: "syntax", 2: "general", 3: "editing"}
        self.settings.ollama_chat_context_mode = mode_value_map.get(self.context_mode_combo.currentIndex(), "document")

        return self.settings
