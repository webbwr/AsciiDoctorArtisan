"""
Chat Manager - Orchestrates AI chat components (Ollama/Claude backends).

Coordinates ChatBarWidget, ChatPanelWidget, workers, and settings.
Delegates to ChatModelManager and ChatBackendController (MA principle).
"""

import logging
import subprocess
from collections.abc import Callable
from typing import Any, cast

from PySide6.QtCore import QObject, QTimer, Signal

from ..core.models import ChatMessage
from ..core.settings import Settings
from .chat_backend_controller import ChatBackendController
from .chat_model_manager import ChatModelManager

logger = logging.getLogger(__name__)


class ChatManager(QObject):
    """
    Orchestrates chat components (bar, panel, workers) for Ollama/Claude backends.

    Signals: visibility_changed, message_sent_to_worker, status_message, settings_changed

    MA principle: Reduced from 1079→<300 lines via ChatModelManager and ChatBackendController.
    """

    # Signals
    visibility_changed = Signal(bool, bool)  # bar_visible, panel_visible
    message_sent_to_worker = Signal(str, str, str, list, object)  # message, model, mode, history, doc_content
    status_message = Signal(str)
    settings_changed = Signal()

    def __init__(
        self,
        chat_bar: Any,  # ChatBarWidget (circular import)
        chat_panel: Any,  # ChatPanelWidget (circular import)
        settings: Settings,
        parent: QObject | None = None,
    ) -> None:
        """Initialize ChatManager with chat components, settings, and parent."""
        super().__init__(parent)
        self._chat_bar = chat_bar
        self._chat_panel = chat_panel
        self._settings = settings
        self._document_content_provider = None
        self._is_processing = False
        self._chat_history: list[ChatMessage] = []  # Internal history cache for testing
        self._current_backend: str = settings.ai_backend  # "ollama" or "claude"

        # Document content debouncing (500ms delay)
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(500)

        # Model management (MA principle extraction)
        self._model_manager = ChatModelManager(
            settings=self._settings,
            chat_bar=self._chat_bar,
            current_backend_getter=lambda: self._current_backend,
        )
        # Connect model manager signals
        self._model_manager.status_message.connect(self.status_message)
        self._model_manager.settings_changed.connect(self.settings_changed)

        # Backend control and visibility (MA principle extraction)
        self._backend_controller = ChatBackendController(
            settings=self._settings,
            chat_bar=self._chat_bar,
            current_backend_getter=lambda: self._current_backend,
            current_backend_setter=lambda backend: setattr(self, "_current_backend", backend),
            parent_getter=lambda: self.parent(),
            load_models_callback=lambda: self._load_available_models(),
        )
        # Connect backend controller signals
        self._backend_controller.visibility_changed.connect(self.visibility_changed)
        self._backend_controller.settings_changed.connect(self.settings_changed)

        self._connect_signals()
        logger.debug(f"ChatManager initialized with backend: {self._current_backend}")

    def _connect_signals(self) -> None:
        """Connect signals between chat components."""
        # Chat bar signals
        self._chat_bar.message_sent.connect(self._on_message_sent)
        self._chat_bar.clear_requested.connect(self._on_clear_requested)
        self._chat_bar.cancel_requested.connect(self._on_cancel_requested)
        self._chat_bar.model_changed.connect(self._on_model_changed)
        self._chat_bar.context_mode_changed.connect(self._on_context_mode_changed)
        self._chat_bar.scan_models_requested.connect(self._on_scan_models_requested)

    def initialize(self) -> None:
        """Initialize chat UI (history, visibility, models). Auto-switches to Claude if needed."""
        # Update current backend from settings (may have changed)
        self._current_backend = self._settings.ai_backend
        logger.info(f"Initializing chat with backend: {self._current_backend}")

        # Check for auto-switch to Claude scenario
        from ..core import SecureCredentials

        creds = SecureCredentials()
        if not self._settings.ollama_enabled and creds.has_anthropic_key():
            logger.info("Ollama disabled but Claude available - auto-switching to Claude")
            self._backend_controller.switch_backend("claude")
        else:
            # Load models and set current model for the active backend
            self._load_available_models()

            # Set current model from settings
            if self._current_backend == "ollama":
                if self._settings.ollama_model:
                    self._chat_bar.set_model(self._settings.ollama_model)
            elif self._current_backend == "claude":
                if self._settings.claude_model:
                    self._chat_bar.set_model(self._settings.claude_model)

        # Use new backend-agnostic setting (with fallback to deprecated)
        context_mode = self._settings.chat_context_mode or self._settings.ollama_chat_context_mode
        self._chat_bar.set_context_mode(context_mode)

        # Load chat history from settings
        self._load_chat_history()

        # Update visibility based on settings
        self._backend_controller.update_visibility()

        # Set Scan Models button visibility (only for Claude backend)
        self._chat_bar.set_scan_models_visible(self._current_backend == "claude")

        logger.info(f"Chat manager initialized (backend: {self._current_backend})")

    def _auto_download_default_model(self) -> None:
        """Auto-download default Ollama model (gnokit/improve-grammer) in background."""
        default_model = "gnokit/improve-grammer"
        logger.info(f"Auto-downloading default model: {default_model}")
        self.status_message.emit(f"Downloading {default_model}... (this may take a few minutes)")

        try:
            subprocess.Popen(
                ["ollama", "pull", default_model],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            logger.info(f"Started download of {default_model}")
        except Exception as e:
            logger.error(f"Failed to auto-download model: {e}")
            self.status_message.emit(f"Auto-download failed: {e}")

    def _switch_backend(self, new_backend: str) -> None:
        """Switch backend (delegates to chat_backend_controller)."""
        self._backend_controller.switch_backend(new_backend)

    def _load_available_models(self) -> None:
        """Load available models (delegates to chat_model_manager)."""
        self._model_manager.load_available_models()

    def _load_chat_history(self) -> None:
        """Load chat history from settings and display in panel."""
        # Use new backend-agnostic setting (with fallback to deprecated)
        history_dicts = self._settings.chat_history or self._settings.ollama_chat_history or []

        if not history_dicts:
            logger.debug("No chat history to load")
            return

        # Convert dict history to ChatMessage objects
        messages: list[ChatMessage] = []
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
        """Save current chat history to settings (backend-agnostic)."""
        messages = self._chat_panel.get_messages()

        # Apply max history limit (use most restrictive limit for backward compatibility)
        # Use min() to respect both new and deprecated settings
        max_history = min(self._settings.chat_max_history, self._settings.ollama_chat_max_history)
        if len(messages) > max_history:
            messages = messages[-max_history:]
            logger.info(f"Trimmed history to {max_history} messages")

        # Convert ChatMessage objects to dicts for JSON serialization
        history_dicts = [msg.model_dump() for msg in messages]

        # Update both new and deprecated settings for backward compatibility
        self._settings.chat_history = history_dicts
        self._settings.ollama_chat_history = history_dicts
        self.settings_changed.emit()

    def _validate_model(self, model: str) -> bool:
        """Validate model (delegates to chat_model_manager)."""
        return self._model_manager.validate_model(model)

    def _handle_user_message(self, message: str, model: str, context_mode: str) -> None:
        """Handle user message from chat bar (test wrapper for _on_message_sent)."""
        self._on_message_sent(message, model, context_mode)

    def _on_message_sent(self, message: str, model: str, context_mode: str) -> None:
        """Handle message sent from chat bar. Reentrancy guard prevents concurrent AI requests."""
        # REENTRANCY GUARD: Block concurrent requests (AI takes 2-30s)
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
        # Use new backend-agnostic setting (with fallback)
        send_document = self._settings.chat_send_document or self._settings.ollama_chat_send_document
        if context_mode in ("document", "editing") and send_document:
            if self._document_content_provider:
                document_content = self._document_content_provider()
                logger.debug(f"Including document content ({len(document_content or '')} chars)")

        # Emit signal to send to worker (worker routes to appropriate backend)
        self.message_sent_to_worker.emit(message, model, context_mode, history, document_content)

        # Update UI state
        self._is_processing = True
        self._chat_bar.set_processing(True)
        backend_name = self._current_backend.capitalize()
        self.status_message.emit(f"{backend_name} is thinking ({model})...")

        logger.info(f"Sent message to {backend_name} worker: {message[:50]}... (mode: {context_mode})")

    def _on_clear_requested(self) -> None:
        """Handle clear history button click."""
        self._chat_panel.clear_messages()
        # Clear both new and deprecated settings
        self._settings.chat_history = []
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
        """Handle model changed (delegates to chat_model_manager)."""
        self._model_manager.handle_model_changed(model)

    def _on_context_mode_changed(self, mode: str) -> None:
        """Handle context mode selector change."""
        # Save to both new and deprecated settings
        self._settings.chat_context_mode = mode
        self._settings.ollama_chat_context_mode = mode
        self.settings_changed.emit()
        logger.info(f"Context mode changed to: {mode}")

    def _on_scan_models_requested(self) -> None:
        """Handle scan models requested (delegates to chat_model_manager)."""
        self._model_manager.handle_scan_models_requested(self._chat_panel)

    def handle_response_ready(self, message: ChatMessage) -> None:
        """Handle AI response from worker."""
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
        """Handle streaming response chunk from worker."""
        # Append to last message in panel
        self._chat_panel.append_to_last_message(chunk)

    def handle_error(self, error_message: str) -> None:
        """Handle error from worker (display in status bar and chat panel)."""
        # Update UI state
        self._is_processing = False
        self._chat_bar.set_processing(False)

        # Add error message to chat panel
        import time

        from ..core.models import ChatMessage

        error_chat_message = ChatMessage(
            role="assistant",
            content=f"❌ **Error:** {error_message}",
            timestamp=int(time.time()),
            model=f"{self._current_backend} (error)",
            context_mode=self._settings.chat_context_mode or "general",
        )
        self._chat_panel.add_message(error_chat_message)

        # Save history with error message
        self._save_chat_history()

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

    def _get_document_context(self) -> str:
        """Get current document content from provider."""
        if self._document_content_provider:
            return self._document_content_provider()
        return ""

    def set_document_content_provider(self, provider: Callable[[], str]) -> None:
        """Set callable that provides current document content."""
        self._document_content_provider = provider
        logger.debug("Document content provider set")

    def update_settings(self, settings: Settings) -> None:
        """Update chat UI when settings change. Auto-switches backend if needed."""
        self._settings = settings
        # Update settings reference in sub-managers (critical for object reference sync)
        self._model_manager.update_settings(settings)
        self._backend_controller.update_settings(settings)

        # Check if backend should switch based on Ollama enabled state
        from ..core import SecureCredentials

        creds = SecureCredentials()
        has_claude_key = creds.has_anthropic_key()

        # Determine target backend based on Ollama state and Claude availability
        if not settings.ollama_enabled and has_claude_key:
            # Ollama disabled + Claude available → switch to Claude
            target_backend = "claude"
        elif settings.ollama_enabled:
            # Ollama enabled → switch to Ollama
            target_backend = "ollama"
        else:
            # Use current backend setting
            target_backend = settings.ai_backend

        # Perform backend switch if needed
        if target_backend != self._current_backend:
            logger.info(f"Backend switch triggered by settings change: {self._current_backend} → {target_backend}")
            self._switch_backend(target_backend)
        else:
            # No backend switch needed, just reload models and update UI
            self._current_backend = target_backend  # Ensure backend is correct
            self._load_available_models()

            # Update model selector based on active backend
            if target_backend == "ollama" and settings.ollama_model:
                self._chat_bar.set_model(settings.ollama_model)
                logger.info(f"Updated chat model to: {settings.ollama_model}")
            elif target_backend == "claude" and settings.claude_model:
                self._chat_bar.set_model(settings.claude_model)
                logger.info(f"Updated chat model to: {settings.claude_model}")

        # Update context mode (use new setting with fallback)
        context_mode = settings.chat_context_mode or settings.ollama_chat_context_mode
        self._chat_bar.set_context_mode(context_mode)

        # Update visibility
        self._backend_controller.update_visibility()

        logger.info(f"Chat settings updated (backend: {self._current_backend})")

    def toggle_panel_visibility(self) -> None:
        """Toggle chat pane visibility (for toolbar button)."""
        parent = self.parent()
        if not parent or not hasattr(parent, "chat_container"):
            return

        current = parent.chat_container.isVisible()
        new_visible = not current

        # Update both new and deprecated settings
        self._settings.ai_chat_enabled = new_visible
        self._settings.ollama_chat_enabled = new_visible
        self._backend_controller.update_visibility()
        self.settings_changed.emit()

        state = "shown" if new_visible else "hidden"
        self.status_message.emit(f"Chat pane {state}")
        logger.info(f"Chat pane visibility toggled: {new_visible}")

    def export_chat_history(self) -> str:
        """
        Export chat history to plain text.

        Returns:
            Plain text representation of chat history
        """
        return cast(str, self._chat_panel.export_to_text())

    def get_message_count(self) -> int:
        """
        Get total number of messages in chat.

        Returns:
            Message count
        """
        return cast(int, self._chat_panel.get_message_count())

    def is_processing(self) -> bool:
        """
        Check if AI is currently processing a request.

        Returns:
            True if processing, False otherwise
        """
        return self._is_processing

    def clear_history(self) -> None:
        """Clear chat history from panel and settings (backend-agnostic)."""
        self._chat_panel.clear_messages()
        self._chat_history.clear()
        # Clear both new and deprecated settings
        self._settings.chat_history = []
        self._settings.ollama_chat_history = []
        self.settings_changed.emit()
        logger.info("Chat history cleared via clear_history()")

    def _trim_history(self) -> None:
        """Trim chat history to max limit (backend-agnostic)."""
        max_history = self._settings.chat_max_history or self._settings.ollama_chat_max_history
        if len(self._chat_history) > max_history:
            self._chat_history = self._chat_history[-max_history:]
            logger.info(f"Trimmed internal history to {max_history} messages")
