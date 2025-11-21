"""
Chat bar widget for Ollama AI interaction.

This module provides ChatBarWidget, a horizontal bar with chat input controls
that appears above the status bar when AI mode is active.

The widget includes:
- Text input field with placeholder and Enter-to-send
- Model selector dropdown (switch models without settings dialog)
- Clear chat history button
- Stop/Cancel generation button (visible during processing)
- Context mode selector (document/syntax/general/editing)

Visibility Rules:
    - Shown when: ollama_enabled=True AND ollama_model is set
    - Hidden when: ollama_enabled=False OR ollama_model is None

Specification Reference: Lines 228-329 (Ollama AI Chat Rules)
"""

import logging

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QStyle,
    QWidget,
)

logger = logging.getLogger(__name__)


class ChatBarWidget(QWidget):
    """
    Horizontal chat input bar for Ollama AI interaction.

    Provides user input controls for sending chat messages, switching models,
    selecting context modes, and managing chat state.

    Signals:
        message_sent: Emitted with (message_text, model, context_mode) when user sends
        clear_requested: Emitted when user clicks clear history button
        cancel_requested: Emitted when user clicks stop/cancel button
        model_changed: Emitted with model_name when user switches models
        context_mode_changed: Emitted with mode_name when user changes context

    Attributes:
        _input_field: QLineEdit for user message input
        _model_selector: QComboBox for model selection
        _context_selector: QComboBox for context mode selection
        _send_button: QPushButton to send message
        _clear_button: QPushButton to clear chat history
        _scan_models_button: QPushButton to scan for available models from API
        _cancel_button: QPushButton to cancel generation (visible during processing)

    Example:
        ```python
        chat_bar = ChatBarWidget()
        chat_bar.set_models(["gnokit/improve-grammer", "deepseek-coder"])
        chat_bar.set_model("gnokit/improve-grammer")
        chat_bar.message_sent.connect(on_message_sent)

        chat_bar.show()  # When AI enabled + model set
        chat_bar.hide()  # When AI disabled or no model
        ```
    """

    # Signals
    message_sent = Signal(str, str, str)  # message, model, context_mode
    clear_requested = Signal()
    cancel_requested = Signal()
    model_changed = Signal(str)
    context_mode_changed = Signal(str)
    scan_models_requested = Signal()  # Scan for available models from API

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Initialize the chat bar widget.

        Args:
            parent: Parent widget (usually MainWindow)
        """
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _create_top_row_controls(self) -> QHBoxLayout:
        """
        Create top row with model selector, context selector, and action buttons.

        MA principle: Extracted from _setup_ui (46 lines).

        Returns:
            Configured QHBoxLayout with all top row controls
        """
        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        # Model selector
        self._model_selector = QComboBox()
        self._model_selector.setToolTip("Select Ollama model")
        self._model_selector.setMaximumWidth(120)
        top_row.addWidget(self._model_selector)

        # Context mode selector
        self._context_selector = QComboBox()
        self._context_selector.addItems(
            [
                "Document Q&A",
                "Syntax Help",
                "General Chat",
                "Editing Suggestions",
            ]
        )
        self._context_selector.setToolTip("Select interaction mode")
        self._context_selector.setMaximumWidth(120)
        top_row.addWidget(self._context_selector)

        top_row.addStretch(1)  # Push buttons to the right

        # Clear button
        self._clear_button = QPushButton("Clear")
        self._clear_button.setToolTip("Clear chat history")
        self._clear_button.setMaximumWidth(60)
        top_row.addWidget(self._clear_button)

        # Scan Models button (only visible for Claude backend)
        self._scan_models_button = QPushButton("Scan Models")
        self._scan_models_button.setToolTip("Scan Anthropic API for available models")
        self._scan_models_button.setMaximumWidth(90)
        top_row.addWidget(self._scan_models_button)

        # Cancel button (hidden by default, shown during processing)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.setToolTip("Cancel ongoing generation")
        self._cancel_button.setMaximumWidth(60)
        self._cancel_button.hide()
        top_row.addWidget(self._cancel_button)

        return top_row

    def _style_send_button(self) -> None:
        """
        Apply blue-themed styling to send button.

        MA principle: Extracted from _setup_ui (20 lines).
        """
        self._send_button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: 1px solid #4a9eff;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(74, 158, 255, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(74, 158, 255, 0.3);
            }
            QPushButton:disabled {
                opacity: 0.5;
                border-color: rgba(74, 158, 255, 0.5);
            }
        """
        )

    def _create_bottom_row_controls(self) -> QHBoxLayout:
        """
        Create bottom row with input field and send button.

        MA principle: Extracted from _setup_ui (32 lines).

        Returns:
            Configured QHBoxLayout with input and send controls
        """
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(6)

        # Input field
        self._input_field = QLineEdit()
        self._input_field.setPlaceholderText("Ask AI a question... (Enter to send)")
        self._input_field.setClearButtonEnabled(True)
        bottom_row.addWidget(self._input_field, 1)  # Stretch to fill space

        # Send button with standard media play icon
        self._send_button = QPushButton()
        self._send_button.setIcon(self._send_button.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self._send_button.setIconSize(QSize(24, 24))  # Set larger icon size
        self._send_button.setToolTip("Send message (or press Enter)")
        self._send_button.setMaximumWidth(40)
        self._send_button.setMinimumWidth(40)
        self._style_send_button()
        bottom_row.addWidget(self._send_button)

        return bottom_row

    def _setup_ui(self) -> None:
        """
        Set up the widget layout and controls.

        MA principle: Reduced from 100→16 lines by extracting 3 layout helpers (84% reduction).
        """
        from PySide6.QtWidgets import QVBoxLayout

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Add control rows
        main_layout.addLayout(self._create_top_row_controls())
        main_layout.addLayout(self._create_bottom_row_controls())

        # Set initial state
        self._send_button.setEnabled(False)  # Disabled until text entered

    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        self._input_field.returnPressed.connect(self._on_send)
        self._input_field.textChanged.connect(self._on_text_changed)
        self._send_button.clicked.connect(self._on_send)
        self._clear_button.clicked.connect(self._on_clear)
        self._scan_models_button.clicked.connect(self._on_scan_models)
        self._cancel_button.clicked.connect(self._on_cancel)
        self._model_selector.currentTextChanged.connect(self._on_model_changed)
        self._context_selector.currentIndexChanged.connect(self._on_context_changed)

    def _on_send(self) -> None:
        """Handle send button click or Enter key."""
        message = self._input_field.text().strip()
        if not message:  # pragma: no cover
            return

        model = self._model_selector.currentText()
        context_mode = self._get_context_mode_value()

        logger.info(f"Sending chat message: {message[:50]}... (mode: {context_mode})")

        # Emit signal with message data
        self.message_sent.emit(message, model, context_mode)

        # Clear input field
        self._input_field.clear()

    def _on_text_changed(self, text: str) -> None:
        """Handle input field text changes."""
        # Enable send button only when text is non-empty
        self._send_button.setEnabled(bool(text.strip()))

    def _on_clear(self) -> None:
        """Handle clear button click."""
        logger.info("Clear chat history requested")
        self.clear_requested.emit()

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        logger.info("Cancel generation requested")
        self.cancel_requested.emit()

    def _on_scan_models(self) -> None:
        """Handle scan models button click."""
        logger.info("Scan models requested")
        self.scan_models_requested.emit()

    def _on_model_changed(self, model: str) -> None:
        """Handle model selector change."""
        if model:
            logger.info(f"Model changed to: {model}")
            self.model_changed.emit(model)

    def _on_context_changed(self, index: int) -> None:
        """Handle context mode selector change."""
        context_mode = self._get_context_mode_value()
        logger.info(f"Context mode changed to: {context_mode}")
        self.context_mode_changed.emit(context_mode)

    def _get_context_mode_value(self) -> str:
        """
        Get the current context mode value.

        Returns:
            Context mode string (document/syntax/general/editing)
        """
        index = self._context_selector.currentIndex()
        mode_map = {
            0: "document",
            1: "syntax",
            2: "general",
            3: "editing",
        }
        return mode_map.get(index, "document")

    def set_models(self, models: list[str]) -> None:
        """
        Set available Ollama models in selector.

        Args:
            models: List of model names (e.g., ["gnokit/improve-grammer", "llama2"])
        """
        self._model_selector.clear()
        if models:
            self._model_selector.addItems(models)
            logger.debug(f"Set {len(models)} models in selector")
        else:
            logger.warning("No models provided to chat bar")

    def set_model(self, model: str) -> None:
        """
        Set the currently selected model.

        Args:
            model: Model name to select
        """
        index = self._model_selector.findText(model)
        if index >= 0:
            self._model_selector.setCurrentIndex(index)
            logger.debug(f"Selected model: {model}")
        else:
            logger.warning(f"Model not found in selector: {model}")

    def set_context_mode(self, mode: str) -> None:
        """
        Set the currently selected context mode.

        Args:
            mode: Context mode (document/syntax/general/editing)
        """
        mode_index_map = {
            "document": 0,
            "syntax": 1,
            "general": 2,
            "editing": 3,
        }
        index = mode_index_map.get(mode, 0)
        self._context_selector.setCurrentIndex(index)
        logger.debug(f"Selected context mode: {mode}")

    def set_processing(self, is_processing: bool) -> None:
        """
        Update UI state for processing status.

        When processing:
        - Input field disabled
        - Send button hidden
        - Cancel button shown

        Args:
            is_processing: True if AI is generating response
        """
        self._input_field.setEnabled(not is_processing)
        self._model_selector.setEnabled(not is_processing)
        self._context_selector.setEnabled(not is_processing)
        self._send_button.setVisible(not is_processing)
        self._cancel_button.setVisible(is_processing)
        self._clear_button.setEnabled(not is_processing)

        if is_processing:
            self._input_field.setPlaceholderText("AI is thinking...")
        else:
            self._input_field.setPlaceholderText("Ask AI a question... (Enter to send)")

    def clear_input(self) -> None:
        """Clear the input field."""
        self._input_field.clear()

    def get_current_model(self) -> str:
        """
        Get the currently selected model.

        Returns:
            Model name string
        """
        return self._model_selector.currentText()

    def get_current_context_mode(self) -> str:
        """
        Get the currently selected context mode.

        Returns:
            Context mode string (document/syntax/general/editing)
        """
        return self._get_context_mode_value()

    def set_scan_models_visible(self, visible: bool) -> None:
        """
        Set visibility of the Scan Models button.

        Args:
            visible: True to show button, False to hide it
        """
        self._scan_models_button.setVisible(visible)

    def set_enabled_state(self, enabled: bool) -> None:
        """
        Enable or disable the entire chat bar.

        Args:
            enabled: True to enable, False to disable all controls
        """
        self._input_field.setEnabled(enabled)
        self._model_selector.setEnabled(enabled)
        self._context_selector.setEnabled(enabled)
        self._send_button.setEnabled(enabled and bool(self._input_field.text().strip()))
        self._clear_button.setEnabled(enabled)
        self._cancel_button.setEnabled(enabled)
