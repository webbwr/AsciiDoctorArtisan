"""
Chat manager for coordinating Ollama AI chat components.

This module provides ChatManager, which orchestrates all chat-related UI
components and coordinates between them, the worker thread, and settings.

The manager handles:
- Chat bar and panel visibility based on settings
- Message flow between user, worker, and display
- Chat history persistence via Settings
- Model and context mode management
- Error handling and user feedback

Integration Points:
    - ChatBarWidget: User input controls
    - ChatPanelWidget: Conversation display
    - OllamaChatWorker: Background AI processing
    - Settings: Chat preferences and history persistence
    - StatusManager: Status bar messages

Specification Reference: Lines 228-329 (Ollama AI Chat Rules)
"""

import json
import logging
import subprocess
import time
from typing import List, Optional

from PySide6.QtCore import QObject, QTimer, Signal

from ..core.models import ChatMessage
from ..core.settings import Settings

logger = logging.getLogger(__name__)


class ChatManager(QObject):
    """
    Orchestrates all chat-related components and interactions.

    Coordinates between ChatBarWidget, ChatPanelWidget, OllamaChatWorker,
    and Settings to provide a cohesive chat experience.

    Signals:
        visibility_changed: Emitted with (bar_visible, panel_visible) when visibility changes
        message_sent_to_worker: Emitted with send_message args when user sends message
        status_message: Emitted with status text for status bar display
        settings_changed: Emitted when chat settings need to be saved

    Attributes:
        _chat_bar: ChatBarWidget instance
        _chat_panel: ChatPanelWidget instance
        _settings: Settings instance
        _document_content_provider: Callable that returns current document text
        _debounce_timer: QTimer for document content debouncing

    Example:
        ```python
        manager = ChatManager(chat_bar, chat_panel, settings)
        manager.set_document_content_provider(lambda: editor.toPlainText())
        manager.message_sent_to_worker.connect(worker.send_message)
        manager.initialize()
        ```
    """

    # Signals
    visibility_changed = Signal(bool, bool)  # bar_visible, panel_visible
    message_sent_to_worker = Signal(str, str, str, list, object)  # message, model, mode, history, doc_content
    status_message = Signal(str)
    settings_changed = Signal()

    def __init__(
        self,
        chat_bar,  # ChatBarWidget
        chat_panel,  # ChatPanelWidget
        settings: Settings,
        parent: Optional[QObject] = None,
    ) -> None:
        """
        Initialize the chat manager.

        Args:
            chat_bar: ChatBarWidget instance
            chat_panel: ChatPanelWidget instance
            settings: Settings instance for persistence
            parent: Parent QObject (usually MainWindow)
        """
        super().__init__(parent)
        self._chat_bar = chat_bar
        self._chat_panel = chat_panel
        self._settings = settings
        self._document_content_provider = None
        self._is_processing = False

        # Document content debouncing (500ms delay)
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(500)

        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect signals between chat components."""
        # Chat bar signals
        self._chat_bar.message_sent.connect(self._on_message_sent)
        self._chat_bar.clear_requested.connect(self._on_clear_requested)
        self._chat_bar.cancel_requested.connect(self._on_cancel_requested)
        self._chat_bar.model_changed.connect(self._on_model_changed)
        self._chat_bar.context_mode_changed.connect(self._on_context_mode_changed)

    def initialize(self) -> None:
        """
        Initialize chat UI based on current settings.

        Loads chat history, sets visibility, and configures UI state.
        Must be called after UI setup is complete.
        """
        # Load available models (placeholder - actual model detection in v1.7.1)
        self._load_available_models()

        # Set current model and context mode from settings
        if self._settings.ollama_model:
            self._chat_bar.set_model(self._settings.ollama_model)

        self._chat_bar.set_context_mode(self._settings.ollama_chat_context_mode)

        # Load chat history from settings
        self._load_chat_history()

        # Update visibility based on settings
        self._update_visibility()

        logger.info("Chat manager initialized")

    def _load_available_models(self) -> None:
        """
        Load available Ollama models into chat bar selector.

        Attempts to detect installed models via `ollama list` command.
        Falls back to hardcoded defaults if Ollama is not available.
        """
        models: List[str] = []
        ollama_available = False

        try:
            # Try to detect installed models
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )

            if result.returncode == 0:
                ollama_available = True
                # Parse output: skip header line, extract model names
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:  # Skip header
                    for line in lines[1:]:
                        parts = line.split()
                        if parts:
                            # Model name is first column (e.g., "phi3:mini")
                            model_name = parts[0]
                            models.append(model_name)

                if models:
                    logger.info(f"Ollama detected: {len(models)} model(s) available")
                    self.status_message.emit(f"Ollama: {len(models)} model(s) found")
                else:
                    logger.warning("Ollama running but no models installed")
                    self.status_message.emit("Ollama: No models installed (run 'ollama pull phi3:mini')")
            else:
                logger.warning(f"Ollama command failed: {result.stderr.strip()}")

        except FileNotFoundError:
            logger.info("Ollama not found in PATH")
            self.status_message.emit("Ollama not installed (see docs/OLLAMA_CHAT_GUIDE.md)")

        except subprocess.TimeoutExpired:
            logger.warning("Ollama list command timed out")
            self.status_message.emit("Ollama not responding")

        except Exception as e:
            logger.warning(f"Error detecting Ollama models: {e}")

        # Fallback to default models if detection failed
        if not models:
            models = [
                "phi3:mini",
                "llama2",
                "mistral",
                "codellama",
            ]
            if not ollama_available:
                logger.info("Using default model list (Ollama not detected)")

        # Add current model if not in list
        if self._settings.ollama_model and self._settings.ollama_model not in models:
            models.insert(0, self._settings.ollama_model)

        self._chat_bar.set_models(models)
        logger.debug(f"Loaded {len(models)} models into chat bar")

    def _load_chat_history(self) -> None:
        """Load chat history from settings and display in panel."""
        history_dicts = self._settings.ollama_chat_history or []

        if not history_dicts:
            logger.debug("No chat history to load")
            return

        # Convert dict history to ChatMessage objects
        messages: List[ChatMessage] = []
        for msg_dict in history_dicts:
            try:
                message = ChatMessage(**msg_dict)
                messages.append(message)
            except Exception as e:
                logger.warning(f"Invalid chat message in history: {e}")
                continue

        # Load into panel
        self._chat_panel.load_messages(messages)
        logger.info(f"Loaded {len(messages)} messages from history")

    def _save_chat_history(self) -> None:
        """Save current chat history to settings."""
        messages = self._chat_panel.get_messages()

        # Apply max history limit
        max_history = self._settings.ollama_chat_max_history
        if len(messages) > max_history:
            messages = messages[-max_history:]
            logger.info(f"Trimmed history to {max_history} messages")

        # Convert ChatMessage objects to dicts for JSON serialization
        history_dicts = [msg.model_dump() for msg in messages]

        # Update settings
        self._settings.ollama_chat_history = history_dicts
        self.settings_changed.emit()

    def _update_visibility(self) -> None:
        """Update chat UI visibility based on settings."""
        # Chat bar visible when: ollama_enabled=True AND ollama_model is set
        bar_visible = bool(
            self._settings.ollama_enabled and self._settings.ollama_model
        )

        # Chat panel visible when: bar is visible AND ollama_chat_enabled=True
        panel_visible = bar_visible and self._settings.ollama_chat_enabled

        self._chat_bar.setVisible(bar_visible)
        self._chat_panel.setVisible(panel_visible)

        self.visibility_changed.emit(bar_visible, panel_visible)
        logger.debug(f"Chat visibility: bar={bar_visible}, panel={panel_visible}")

    def _on_message_sent(self, message: str, model: str, context_mode: str) -> None:
        """
        Handle message sent from chat bar.

        Args:
            message: User's message text
            model: Selected Ollama model
            context_mode: Selected context mode
        """
        if self._is_processing:
            logger.warning("Already processing a message, ignoring new message")
            self.status_message.emit("AI is still processing previous message...")
            return

        # Add user message to panel
        self._chat_panel.add_user_message(message, model, context_mode)

        # Get current chat history
        history = self._chat_panel.get_messages()[:-1]  # Exclude just-added user message

        # Get document content if needed
        document_content = None
        if context_mode in ("document", "editing") and self._settings.ollama_chat_send_document:
            if self._document_content_provider:
                document_content = self._document_content_provider()
                logger.debug(f"Including document content ({len(document_content or '')} chars)")

        # Emit signal to send to worker
        self.message_sent_to_worker.emit(
            message, model, context_mode, history, document_content
        )

        # Update UI state
        self._is_processing = True
        self._chat_bar.set_processing(True)
        self.status_message.emit(f"AI is thinking ({model})...")

        logger.info(f"Sent message to worker: {message[:50]}... (mode: {context_mode})")

    def _on_clear_requested(self) -> None:
        """Handle clear history button click."""
        self._chat_panel.clear_messages()
        self._settings.ollama_chat_history = []
        self.settings_changed.emit()
        self.status_message.emit("Chat history cleared")
        logger.info("Chat history cleared")

    def _on_cancel_requested(self) -> None:
        """Handle cancel button click."""
        # Signal will be connected to worker.cancel_operation() by parent
        self.status_message.emit("Cancelling AI request...")
        logger.info("Cancel requested by user")

    def _on_model_changed(self, model: str) -> None:
        """
        Handle model selector change.

        Args:
            model: New model name
        """
        self._settings.ollama_model = model
        self.settings_changed.emit()
        self.status_message.emit(f"Switched to model: {model}")
        logger.info(f"Model changed to: {model}")

    def _on_context_mode_changed(self, mode: str) -> None:
        """
        Handle context mode selector change.

        Args:
            mode: New context mode
        """
        self._settings.ollama_chat_context_mode = mode
        self.settings_changed.emit()
        logger.info(f"Context mode changed to: {mode}")

    def handle_response_ready(self, message: ChatMessage) -> None:
        """
        Handle AI response from worker.

        Args:
            message: ChatMessage with AI response
        """
        # Add AI message to panel
        self._chat_panel.add_message(message)

        # Save updated history
        self._save_chat_history()

        # Update UI state
        self._is_processing = False
        self._chat_bar.set_processing(False)

        self.status_message.emit("AI response received")
        logger.info(f"AI response added ({len(message.content)} chars)")

    def handle_response_chunk(self, chunk: str) -> None:
        """
        Handle streaming response chunk from worker.

        Args:
            chunk: Partial response text
        """
        # Append to last message in panel
        self._chat_panel.append_to_last_message(chunk)

    def handle_error(self, error_message: str) -> None:
        """
        Handle error from worker.

        Args:
            error_message: Error description
        """
        # Update UI state
        self._is_processing = False
        self._chat_bar.set_processing(False)

        # Show error in status bar
        self.status_message.emit(f"AI error: {error_message}")
        logger.error(f"AI error: {error_message}")

    def handle_operation_cancelled(self) -> None:
        """Handle operation cancellation from worker."""
        # Update UI state
        self._is_processing = False
        self._chat_bar.set_processing(False)

        self.status_message.emit("AI request cancelled")
        logger.info("AI operation cancelled")

    def set_document_content_provider(self, provider) -> None:
        """
        Set callable that provides current document content.

        Args:
            provider: Callable that returns document text (e.g., editor.toPlainText)
        """
        self._document_content_provider = provider
        logger.debug("Document content provider set")

    def update_settings(self, settings: Settings) -> None:
        """
        Update chat UI when settings change.

        Args:
            settings: New settings instance
        """
        self._settings = settings

        # Update model selector
        if settings.ollama_model:
            self._chat_bar.set_model(settings.ollama_model)

        # Update context mode
        self._chat_bar.set_context_mode(settings.ollama_chat_context_mode)

        # Update visibility
        self._update_visibility()

        logger.info("Chat settings updated")

    def toggle_panel_visibility(self) -> None:
        """Toggle chat panel visibility (for toolbar button)."""
        current = self._chat_panel.isVisible()
        new_visible = not current

        self._settings.ollama_chat_enabled = new_visible
        self._chat_panel.setVisible(new_visible)
        self.settings_changed.emit()

        state = "shown" if new_visible else "hidden"
        self.status_message.emit(f"Chat panel {state}")
        logger.info(f"Chat panel visibility toggled: {new_visible}")

    def export_chat_history(self) -> str:
        """
        Export chat history to plain text.

        Returns:
            Plain text representation of chat history
        """
        return self._chat_panel.export_to_text()

    def get_message_count(self) -> int:
        """
        Get total number of messages in chat.

        Returns:
            Message count
        """
        return self._chat_panel.get_message_count()

    def is_processing(self) -> bool:
        """
        Check if AI is currently processing a request.

        Returns:
            True if processing, False otherwise
        """
        return self._is_processing
