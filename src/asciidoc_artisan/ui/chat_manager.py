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

import logging
import subprocess
from typing import Any, Callable, List, Optional, cast

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
    message_sent_to_worker = Signal(
        str, str, str, list, object
    )  # message, model, mode, history, doc_content
    status_message = Signal(str)
    settings_changed = Signal()

    def __init__(
        self,
        chat_bar: Any,  # ChatBarWidget (circular import)
        chat_panel: Any,  # ChatPanelWidget (circular import)
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
        self._chat_history: List[ChatMessage] = []  # Internal history cache for testing

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

    def _auto_download_default_model(self) -> None:
        """
        Automatically download the default model if Ollama is running but no models installed.

        Runs 'ollama pull qwen2.5-coder:7b' in background and updates status.
        """
        default_model = "qwen2.5-coder:7b"
        logger.info(f"Auto-downloading default model: {default_model}")
        self.status_message.emit(f"Downloading {default_model}... (this may take a few minutes)")

        try:
            # Run ollama pull in subprocess (non-blocking for UI)
            subprocess.Popen(
                ["ollama", "pull", default_model],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info(f"Started download of {default_model}")
        except Exception as e:
            logger.error(f"Failed to auto-download model: {e}")
            self.status_message.emit(f"Auto-download failed: {e}")

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
                    self.status_message.emit(
                        "Ollama: No models installed (run 'ollama pull qwen2.5-coder:7b')"
                    )
                    # Auto-download default model if none installed
                    self._auto_download_default_model()
            else:
                logger.warning(f"Ollama command failed: {result.stderr.strip()}")

        except FileNotFoundError:
            logger.info("Ollama not found in PATH")
            self.status_message.emit(
                "Ollama not installed (see docs/OLLAMA_CHAT_GUIDE.md)"
            )

        except subprocess.TimeoutExpired:
            logger.warning("Ollama list command timed out")
            self.status_message.emit("Ollama not responding")

        except Exception as e:
            logger.warning(f"Error detecting Ollama models: {e}")

        # Fallback to default models if detection failed
        if not models:
            models = [
                "qwen2.5-coder:7b",
                "phi3:mini",
                "deepseek-coder",
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

    def _should_show_chat(self) -> bool:
        """
        Determine if chat should be visible based on settings.

        Returns:
            True if chat should be shown, False otherwise
        """
        return bool(
            self._settings.ollama_enabled
            and self._settings.ollama_model
            and self._settings.ollama_chat_enabled
        )

    def _update_visibility(self) -> None:
        """Update chat UI visibility based on settings."""
        # Chat pane visible when: ollama_enabled=True AND ollama_model is set AND ollama_chat_enabled=True
        chat_visible = self._should_show_chat()

        logger.info(
            f"Chat visibility update: ollama_enabled={self._settings.ollama_enabled}, "
            f"ollama_model={self._settings.ollama_model}, "
            f"ollama_chat_enabled={self._settings.ollama_chat_enabled}, "
            f"chat_visible={chat_visible}"
        )

        # Get reference to chat container from parent
        parent = self.parent()
        if parent and hasattr(parent, "chat_container"):
            # Control entire chat pane visibility
            parent.chat_container.setVisible(chat_visible)

            # Update splitter sizes to show/hide chat pane with proportional sizing
            if hasattr(parent, "splitter") and len(parent.splitter.sizes()) == 3:
                sizes = parent.splitter.sizes()
                if chat_visible and sizes[2] == 0:
                    # Show chat with proportional sizing: 2/5 editor, 2/5 preview, 1/5 chat
                    # Use QTimer to delay until layout is stable
                    from PySide6.QtCore import QTimer

                    def show_chat() -> None:
                        window_width = parent.width()
                        editor_width = int(window_width * 0.4)
                        preview_width = int(window_width * 0.4)
                        chat_width = int(window_width * 0.2)
                        parent.splitter.setSizes(
                            [editor_width, preview_width, chat_width]
                        )
                        logger.info(
                            f"Chat pane shown (proportional): {editor_width}, {preview_width}, {chat_width}"
                        )

                    QTimer.singleShot(150, show_chat)
                elif not chat_visible and sizes[2] > 0:
                    # Hide chat and redistribute: 1/2 editor, 1/2 preview
                    window_width = parent.width()
                    editor_width = int(window_width * 0.5)
                    preview_width = int(window_width * 0.5)
                    parent.splitter.setSizes([editor_width, preview_width, 0])
                    logger.info(
                        f"Chat pane hidden (redistributed): {editor_width}, {preview_width}, 0"
                    )

        self.visibility_changed.emit(chat_visible, chat_visible)
        logger.info(f"Chat pane visibility set: {chat_visible}")

    def _handle_user_message(self, message: str, model: str, context_mode: str) -> None:
        """
        Handle user message from chat bar (test-friendly wrapper).

        Args:
            message: User's message text
            model: Selected Ollama model
            context_mode: Selected context mode
        """
        self._on_message_sent(message, model, context_mode)

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
        history = self._chat_panel.get_messages()[
            :-1
        ]  # Exclude just-added user message

        # Get document content if needed
        document_content = None
        if (
            context_mode in ("document", "editing")
            and self._settings.ollama_chat_send_document
        ):
            if self._document_content_provider:
                document_content = self._document_content_provider()
                logger.debug(
                    f"Including document content ({len(document_content or '')} chars)"
                )

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

    def _get_document_context(self) -> str:
        """
        Get current document content from provider.

        Returns:
            Document text, or empty string if no provider set
        """
        if self._document_content_provider:
            return self._document_content_provider()
        return ""

    def set_document_content_provider(self, provider: Callable[[], str]) -> None:
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

        # Reload available models (in case new ones were installed)
        self._load_available_models()

        # Update model selector
        if settings.ollama_model:
            self._chat_bar.set_model(settings.ollama_model)

        # Update context mode
        self._chat_bar.set_context_mode(settings.ollama_chat_context_mode)

        # Update visibility
        self._update_visibility()

        logger.info("Chat settings updated")

    def toggle_panel_visibility(self) -> None:
        """Toggle chat pane visibility (for toolbar button)."""
        parent = self.parent()
        if not parent or not hasattr(parent, "chat_container"):
            return

        current = parent.chat_container.isVisible()
        new_visible = not current

        self._settings.ollama_chat_enabled = new_visible
        self._update_visibility()
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
        """Clear chat history from panel and settings."""
        self._chat_panel.clear_messages()
        self._chat_history.clear()
        self._settings.ollama_chat_history = []
        self.settings_changed.emit()
        logger.info("Chat history cleared via clear_history()")

    def _trim_history(self) -> None:
        """Trim chat history to max limit."""
        max_history = self._settings.ollama_chat_max_history
        if len(self._chat_history) > max_history:
            self._chat_history = self._chat_history[-max_history:]
            logger.info(f"Trimmed internal history to {max_history} messages")
