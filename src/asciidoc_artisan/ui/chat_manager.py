"""
Chat Manager - Orchestrates AI chat components (Ollama/Claude backends).

Coordinates ChatBarWidget, ChatPanelWidget, workers, and settings.
Delegates to ChatModelManager, ChatBackendController, and ChatHistoryManager (MA principle).
"""

import logging
import subprocess
import time
from typing import Any

from PySide6.QtCore import QObject, Signal

from ..core.models import ChatMessage
from ..core.settings import Settings
from .chat_backend_controller import ChatBackendController
from .chat_history_manager import ChatHistoryManager
from .chat_model_manager import ChatModelManager

logger = logging.getLogger(__name__)


class ChatManager(QObject):
    """
    Orchestrates chat components (bar, panel, workers) for Ollama/Claude backends.

    Signals: visibility_changed, message_sent_to_worker, status_message, settings_changed

    MA principle: Delegates to ChatModelManager, ChatBackendController, ChatHistoryManager.
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
        self._current_backend: str = settings.ai_backend  # "ollama" or "claude"

        # History management (MA principle extraction)
        self._history_manager = ChatHistoryManager(
            settings=self._settings,
            chat_panel=self._chat_panel,
            settings_changed_callback=lambda: self.settings_changed.emit(),
        )

        # Model management (MA principle extraction)
        self._model_manager = ChatModelManager(
            settings=self._settings,
            chat_bar=self._chat_bar,
            current_backend_getter=lambda: self._current_backend,
        )
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
        self._backend_controller.visibility_changed.connect(self.visibility_changed)
        self._backend_controller.settings_changed.connect(self.settings_changed)

        self._connect_signals()
        logger.debug(f"ChatManager initialized with backend: {self._current_backend}")

    def _connect_signals(self) -> None:
        """Connect signals between chat components."""
        self._chat_bar.message_sent.connect(self._on_message_sent)
        self._chat_bar.clear_requested.connect(self._on_clear_requested)
        self._chat_bar.cancel_requested.connect(self._on_cancel_requested)
        self._chat_bar.model_changed.connect(self._on_model_changed)
        self._chat_bar.context_mode_changed.connect(self._on_context_mode_changed)
        self._chat_bar.scan_models_requested.connect(self._on_scan_models_requested)

    def initialize(self) -> None:
        """Initialize chat UI (history, visibility, models). Auto-switches to Claude if needed."""
        self._current_backend = self._settings.ai_backend
        logger.info(f"Initializing chat with backend: {self._current_backend}")

        from ..core import SecureCredentials

        creds = SecureCredentials()
        if not self._settings.ollama_enabled and creds.has_anthropic_key():
            logger.info("Ollama disabled but Claude available - auto-switching to Claude")
            self._backend_controller.switch_backend("claude")
        else:
            self._load_available_models()
            if self._current_backend == "ollama" and self._settings.ollama_model:
                self._chat_bar.set_model(self._settings.ollama_model)
            elif self._current_backend == "claude" and self._settings.claude_model:
                self._chat_bar.set_model(self._settings.claude_model)

        context_mode = self._settings.chat_context_mode or self._settings.ollama_chat_context_mode
        self._chat_bar.set_context_mode(context_mode)
        self._history_manager.load_history()
        self._backend_controller.update_visibility()
        self._chat_bar.set_scan_models_visible(self._current_backend == "claude")
        logger.info(f"Chat manager initialized (backend: {self._current_backend})")

    def _auto_download_default_model(self) -> None:
        """Auto-download default Ollama model in background."""
        default_model = "gnokit/improve-grammer"
        logger.info(f"Auto-downloading default model: {default_model}")
        self.status_message.emit(f"Downloading {default_model}...")

        try:
            subprocess.Popen(
                ["ollama", "pull", default_model],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except Exception as e:
            logger.error(f"Failed to auto-download model: {e}")
            self.status_message.emit(f"Auto-download failed: {e}")

    def _switch_backend(self, new_backend: str) -> None:
        """Switch backend (delegates to chat_backend_controller)."""
        self._backend_controller.switch_backend(new_backend)

    def _load_available_models(self) -> None:
        """Load available models (delegates to chat_model_manager)."""
        self._model_manager.load_available_models()

    def _validate_model(self, model: str) -> bool:
        """Validate model (delegates to chat_model_manager)."""
        return self._model_manager.validate_model(model)

    def _handle_user_message(self, message: str, model: str, context_mode: str) -> None:
        """Handle user message from chat bar (test wrapper)."""
        self._on_message_sent(message, model, context_mode)

    def _on_message_sent(self, message: str, model: str, context_mode: str) -> None:
        """Handle message sent from chat bar."""
        if self._is_processing:
            logger.warning("Already processing a message, ignoring new message")
            self.status_message.emit("AI is still processing previous message...")
            return

        self._chat_panel.add_user_message(message, model, context_mode)
        history = self._chat_panel.get_messages()[:-1]

        document_content = None
        send_document = self._settings.chat_send_document or self._settings.ollama_chat_send_document
        if context_mode in ("document", "editing") and send_document:
            if self._document_content_provider:
                document_content = self._document_content_provider()

        self.message_sent_to_worker.emit(message, model, context_mode, history, document_content)
        self._is_processing = True
        self._chat_bar.set_processing(True)
        self.status_message.emit(f"{self._current_backend.capitalize()} is thinking ({model})...")
        logger.info(f"Sent message to worker: {message[:50]}...")

    def _on_clear_requested(self) -> None:
        """Handle clear history button click."""
        self._history_manager.clear_history()
        self.status_message.emit("Chat history cleared")

    def _on_cancel_requested(self) -> None:
        """Handle cancel button click."""
        self.status_message.emit("Cancelling AI request...")
        logger.info("Cancel requested by user")

    def _on_model_changed(self, model: str) -> None:
        """Handle model changed."""
        self._model_manager.handle_model_changed(model)

    def _on_context_mode_changed(self, mode: str) -> None:
        """Handle context mode selector change."""
        self._settings.chat_context_mode = mode
        self._settings.ollama_chat_context_mode = mode
        self.settings_changed.emit()
        logger.info(f"Context mode changed to: {mode}")

    def _on_scan_models_requested(self) -> None:
        """Handle scan models requested."""
        self._model_manager.handle_scan_models_requested(self._chat_panel)

    def handle_response_ready(self, message: ChatMessage) -> None:
        """Handle AI response from worker."""
        self._chat_panel.add_message(message)
        self._history_manager.save_history()
        self._is_processing = False
        self._chat_bar.set_processing(False)
        self.status_message.emit("AI response received")
        logger.info(f"AI response added ({len(message.content)} chars)")

    def handle_response_chunk(self, chunk: str) -> None:
        """Handle streaming response chunk from worker."""
        self._chat_panel.append_to_last_message(chunk)

    def handle_error(self, error_message: str) -> None:
        """Handle error from worker."""
        self._is_processing = False
        self._chat_bar.set_processing(False)

        error_chat_message = ChatMessage(
            role="assistant",
            content=f"❌ **Error:** {error_message}",
            timestamp=int(time.time()),
            model=f"{self._current_backend} (error)",
            context_mode=self._settings.chat_context_mode or "general",
        )
        self._chat_panel.add_message(error_chat_message)
        self._history_manager.save_history()
        self.status_message.emit(f"AI error: {error_message}")
        logger.error(f"AI error: {error_message}")

    def handle_operation_cancelled(self) -> None:
        """Handle operation cancellation from worker."""
        self._is_processing = False
        self._chat_bar.set_processing(False)
        self.status_message.emit("AI request cancelled")
        logger.info("AI operation cancelled")

    def _get_document_context(self) -> str:
        """Get current document content from provider."""
        if self._document_content_provider:
            return self._document_content_provider()
        return ""

    def set_document_content_provider(self, provider: Any) -> None:
        """Set callable that provides current document content."""
        self._document_content_provider = provider

    def update_settings(self, settings: Settings) -> None:
        """Update chat UI when settings change."""
        self._settings = settings
        self._model_manager.update_settings(settings)
        self._backend_controller.update_settings(settings)
        self._history_manager.update_settings(settings)

        from ..core import SecureCredentials

        creds = SecureCredentials()
        has_claude_key = creds.has_anthropic_key()

        if not settings.ollama_enabled and has_claude_key:
            target_backend = "claude"
        elif settings.ollama_enabled:
            target_backend = "ollama"
        else:
            target_backend = settings.ai_backend

        if target_backend != self._current_backend:
            logger.info(f"Backend switch: {self._current_backend} → {target_backend}")
            self._switch_backend(target_backend)
        else:
            self._current_backend = target_backend
            self._load_available_models()
            if target_backend == "ollama" and settings.ollama_model:
                self._chat_bar.set_model(settings.ollama_model)
            elif target_backend == "claude" and settings.claude_model:
                self._chat_bar.set_model(settings.claude_model)

        context_mode = settings.chat_context_mode or settings.ollama_chat_context_mode
        self._chat_bar.set_context_mode(context_mode)
        self._backend_controller.update_visibility()
        logger.info(f"Chat settings updated (backend: {self._current_backend})")

    def toggle_panel_visibility(self) -> None:
        """Toggle chat pane visibility."""
        self._backend_controller.toggle_panel_visibility()
        parent = self.parent()
        if parent and hasattr(parent, "chat_container"):
            state = "shown" if parent.chat_container.isVisible() else "hidden"
            self.status_message.emit(f"Chat pane {state}")

    def export_chat_history(self) -> str:
        """Export chat history to plain text."""
        return self._history_manager.export_to_text()

    def get_message_count(self) -> int:
        """Get total number of messages in chat."""
        return self._history_manager.get_message_count()

    def is_processing(self) -> bool:
        """Check if AI is currently processing a request."""
        return self._is_processing

    def clear_history(self) -> None:
        """Clear chat history from panel and settings."""
        self._history_manager.clear_history()
        logger.info("Chat history cleared via clear_history()")
