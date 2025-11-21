"""
Chat manager for coordinating AI chat components (Ollama/Claude).

This module provides ChatManager, which orchestrates all chat-related UI
components and coordinates between them, the worker threads, and settings.

The manager handles:
- AI backend selection (Ollama local or Claude remote)
- Chat bar and panel visibility based on settings
- Message flow between user, worker, and display
- Chat history persistence via Settings
- Model and context mode management
- Error handling and user feedback

Integration Points:
    - ChatBarWidget: User input controls
    - ChatPanelWidget: Conversation display
    - OllamaChatWorker: Background AI processing (local)
    - ClaudeWorker: Background AI processing (remote, v1.10.0+)
    - Settings: Chat preferences and history persistence
    - StatusManager: Status bar messages

Architecture (v1.10.0+):
    User can select between two AI backends:
    - Ollama: Local AI models (free, offline)
    - Claude: Cloud AI via Anthropic API (requires API key, online)

    Only one backend is active at a time. Backend is selected via
    Settings.ai_backend ("ollama" or "claude").

Specification Reference: Lines 228-329 (Ollama AI Chat Rules)
"""

import logging
import subprocess
from collections.abc import Callable
from typing import Any, cast

from PySide6.QtCore import QObject, QTimer, Signal

from ..core.models import ChatMessage
from ..core.settings import Settings
from .chat_model_manager import ChatModelManager

logger = logging.getLogger(__name__)


class ChatManager(QObject):
    """
    Orchestrates all chat-related components and interactions.

    Coordinates between ChatBarWidget, ChatPanelWidget, AI workers (Ollama/Claude),
    and Settings to provide a cohesive chat experience.

    Supports dual AI backends (v1.10.0+):
    - Ollama: Local AI models (free, offline, no API key)
    - Claude: Anthropic Cloud AI (requires API key, online)

    Backend is selected via Settings.ai_backend and only one is active at a time.

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
        _current_backend: Current AI backend ("ollama" or "claude")

    Example:
        ```python
        manager = ChatManager(chat_bar, chat_panel, settings)
        manager.set_document_content_provider(lambda: editor.toPlainText())
        manager.message_sent_to_worker.connect(ollama_worker.send_message)
        manager.message_sent_to_worker.connect(claude_worker.send_message)
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
        chat_bar: Any,  # ChatBarWidget (circular import)
        chat_panel: Any,  # ChatPanelWidget (circular import)
        settings: Settings,
        parent: QObject | None = None,
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
        """
        Initialize chat UI based on current settings.

        Loads chat history, sets visibility, and configures UI state.
        Detects active AI backend and loads appropriate models.
        Auto-switches to Claude if Ollama disabled but Claude available.
        Must be called after UI setup is complete.
        """
        # Update current backend from settings (may have changed)
        self._current_backend = self._settings.ai_backend
        logger.info(f"Initializing chat with backend: {self._current_backend}")

        # Check for auto-switch to Claude scenario
        from ..core import SecureCredentials

        creds = SecureCredentials()
        if not self._settings.ollama_enabled and creds.has_anthropic_key():
            logger.info("Ollama disabled but Claude available - auto-switching to Claude")
            self._switch_backend("claude")
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
        self._update_visibility()

        # Set Scan Models button visibility (only for Claude backend)
        self._chat_bar.set_scan_models_visible(self._current_backend == "claude")

        logger.info(f"Chat manager initialized (backend: {self._current_backend})")

    def _auto_download_default_model(self) -> None:
        """
        Automatically download the default model if Ollama is running but no models installed.

        Runs 'ollama pull gnokit/improve-grammer' in background and updates status.
        """
        default_model = "gnokit/improve-grammer"
        logger.info(f"Auto-downloading default model: {default_model}")
        self.status_message.emit(f"Downloading {default_model}... (this may take a few minutes)")

        try:
            # Use Popen (not run) because download takes minutes and we don't want to freeze the UI
            # SECURITY: List form prevents command injection attacks
            # (Never use shell=True with user input - that allows hackers to run malicious commands!)
            subprocess.Popen(
                ["ollama", "pull", default_model],  # Safe: list form, no shell
                stdout=subprocess.PIPE,  # Capture output for logging
                stderr=subprocess.PIPE,  # Capture errors
                text=True,  # Get strings, not bytes
            )
            logger.info(f"Started download of {default_model}")
        except Exception as e:
            logger.error(f"Failed to auto-download model: {e}")
            self.status_message.emit(f"Auto-download failed: {e}")

    def _switch_backend(self, new_backend: str) -> None:
        """
        Switch to a different AI backend and update UI accordingly.

        WHY THIS EXISTS:
        Users can switch between two AI backends:
        - Ollama: Local AI running on your computer (free, private, no API key)
        - Claude: Cloud AI from Anthropic (requires API key, more powerful)

        When they switch, we need to update the entire UI to show the right
        options for the new backend. This method handles all 6 steps needed.

        This method handles the complete backend switch process:
        1. Updates current backend tracking
        2. Updates settings (saves preference)
        3. Sets default model if needed (prevents empty dropdown)
        4. Reloads models for new backend (Ollama = local, Claude = API list)
        5. Updates chat bar dropdown (shows selected model)
        6. Updates UI elements (menu checkmarks, scan button visibility)

        Args:
            new_backend: Backend to switch to ("ollama" or "claude")
        """
        logger.info(f"Switching backend from {self._current_backend} to {new_backend}")

        # Step 1: Update which backend is currently active
        # (We track this in two places: instance variable + saved settings)
        self._current_backend = new_backend
        self._settings.ai_backend = new_backend

        # Step 2: Set default model if user hasn't chosen one yet
        # (This prevents showing an empty dropdown on first switch)
        if new_backend == "claude" and not self._settings.claude_model:
            # Use Sonnet 4 as default (best balance of speed/quality/cost)
            self._settings.claude_model = "claude-sonnet-4-20250514"
        elif new_backend == "ollama" and not self._settings.ollama_model:
            # Use improve-grammer as default (good for document editing)
            self._settings.ollama_model = "gnokit/improve-grammer"

        # Step 3: Load available models for the new backend
        # (Ollama = scan local system, Claude = load from API client)
        self._load_available_models()

        # Step 4: Update the selected model shown in chat bar dropdown
        if new_backend == "ollama" and self._settings.ollama_model:
            self._chat_bar.set_model(self._settings.ollama_model)
            logger.info(f"Switched to Ollama model: {self._settings.ollama_model}")
        elif new_backend == "claude" and self._settings.claude_model:
            self._chat_bar.set_model(self._settings.claude_model)
            logger.info(f"Switched to Claude model: {self._settings.claude_model}")

        # Step 5: Update AI backend checkmarks in Help menu (real-time visual feedback)
        parent = self.parent()
        if parent and hasattr(parent, "_update_ai_backend_checkmarks"):
            parent._update_ai_backend_checkmarks()
            logger.debug(f"Updated AI backend checkmarks for {new_backend}")

        # Step 6: Update Scan Models button visibility
        # (Only Claude needs this button - Ollama scans automatically)
        self._chat_bar.set_scan_models_visible(new_backend == "claude")
        logger.debug(f"Scan Models button visible: {new_backend == 'claude'}")

        # Notify other parts of app that settings changed
        # (Triggers save to disk + updates any listening widgets)
        self.settings_changed.emit()

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

    def _should_show_chat(self) -> bool:
        """
        Determine if chat should be visible based on settings and active backend.

        Chat is shown when:
        1. Chat is enabled (ai_chat_enabled=True)
        2. Either backend is available:
           - Ollama: ollama_enabled=True AND model selected
           - Claude: ollama_enabled=False AND valid API key exists
        3. Auto-switches to Claude if Ollama disabled but Claude available

        Returns:
            True if chat should be shown, False otherwise
        """
        # Use new backend-agnostic setting (with fallback)
        chat_enabled = self._settings.ai_chat_enabled or self._settings.ollama_chat_enabled

        if not chat_enabled:
            return False

        # Check if Claude API key is configured
        from ..core import SecureCredentials

        creds = SecureCredentials()
        has_claude_key = creds.has_anthropic_key()

        # Auto-switch to Claude if Ollama is disabled but Claude is available
        if not self._settings.ollama_enabled and has_claude_key:
            if self._current_backend != "claude":
                logger.info("Auto-switching to Claude backend (Ollama disabled, Claude available)")
                self._switch_backend("claude")
            return bool(self._settings.claude_model)

        # Check backend availability
        if self._current_backend == "ollama":
            return bool(self._settings.ollama_enabled and self._settings.ollama_model)
        elif self._current_backend == "claude":
            return bool(has_claude_key and self._settings.claude_model)
        else:
            return False

    def _build_backend_status_log(self) -> str:
        """
        Build backend status string for logging.

        MA principle: Extracted from _update_visibility (14 lines).

        Returns:
            Backend status string with configuration details
        """
        backend_status = f"backend={self._current_backend}"
        if self._current_backend == "ollama":
            backend_status += (
                f", ollama_enabled={self._settings.ollama_enabled}, ollama_model={self._settings.ollama_model}"
            )
        elif self._current_backend == "claude":
            from ..core import SecureCredentials

            creds = SecureCredentials()
            backend_status += f", has_api_key={creds.has_anthropic_key()}, claude_model={self._settings.claude_model}"
        return backend_status

    def _show_chat_pane(self, parent: Any) -> None:
        """
        Show chat pane with proportional sizing.

        MA principle: Extracted from _update_visibility (20 lines).

        Args:
            parent: Parent widget with splitter
        """
        from PySide6.QtCore import QTimer

        def show_chat() -> None:
            try:
                # Proportional sizing: 40% editor, 40% preview, 20% chat
                window_width = parent.width()
                editor_width = int(window_width * 0.4)
                preview_width = int(window_width * 0.4)
                chat_width = int(window_width * 0.2)
                parent.splitter.setSizes([editor_width, preview_width, chat_width])
                logger.info(f"Chat pane shown (proportional): {editor_width}, {preview_width}, {chat_width}")
            except RuntimeError:
                # Parent widget was deleted (common in tests)
                logger.debug("Parent widget deleted before show_chat callback")

        QTimer.singleShot(150, show_chat)

    def _hide_chat_pane(self, parent: Any) -> None:
        """
        Hide chat pane and redistribute space.

        MA principle: Extracted from _update_visibility (6 lines).

        Args:
            parent: Parent widget with splitter
        """
        window_width = parent.width()
        editor_width = int(window_width * 0.5)
        preview_width = int(window_width * 0.5)
        parent.splitter.setSizes([editor_width, preview_width, 0])
        logger.info(f"Chat pane hidden (redistributed): {editor_width}, {preview_width}, 0")

    def _update_visibility(self) -> None:
        """
        Update chat UI visibility based on settings and active backend.

        MA principle: Reduced from 61→24 lines by extracting 3 helpers (61% reduction).
        """
        chat_visible = self._should_show_chat()

        # Log visibility update with backend details
        backend_status = self._build_backend_status_log()
        logger.info(
            f"Chat visibility update: {backend_status}, "
            f"ai_chat_enabled={self._settings.ai_chat_enabled}, "
            f"chat_visible={chat_visible}"
        )

        # Update chat container visibility
        parent = self.parent()
        if parent and hasattr(parent, "chat_container"):
            parent.chat_container.setVisible(chat_visible)

            # Update splitter sizes
            if hasattr(parent, "splitter") and len(parent.splitter.sizes()) == 3:
                sizes = parent.splitter.sizes()
                if chat_visible and sizes[2] == 0:
                    self._show_chat_pane(parent)
                elif not chat_visible and sizes[2] > 0:
                    self._hide_chat_pane(parent)

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
        # REENTRANCY GUARD: Prevent multiple AI requests at the same time
        #
        # WHY THIS MATTERS:
        # 1. AI takes 2-30 seconds to respond
        # 2. User might click Send multiple times while waiting (impatience!)
        # 3. Multiple requests would queue up and waste resources
        # 4. Results would arrive out of order, confusing the UI
        # 5. Could overwhelm the AI service or local Ollama
        #
        # SOLUTION:
        # Block new requests until current one finishes.
        # Show helpful message so user knows we're still working.
        if self._is_processing:
            logger.warning("Already processing a message, ignoring new message")
            self.status_message.emit("AI is still processing previous message...")
            return  # Exit early - don't start new request

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
        """
        Handle context mode selector change.

        Args:
            mode: New context mode
        """
        # Save to both new and deprecated settings
        self._settings.chat_context_mode = mode
        self._settings.ollama_chat_context_mode = mode
        self.settings_changed.emit()
        logger.info(f"Context mode changed to: {mode}")

    def _on_scan_models_requested(self) -> None:
        """Handle scan models requested (delegates to chat_model_manager)."""
        self._model_manager.handle_scan_models_requested(self._chat_panel)

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

        Displays error in both status bar and chat panel so user can see
        what went wrong in their conversation history.

        Args:
            error_message: Error description
        """
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
        Update chat UI when settings change (backend-agnostic).

        Checks if backend should switch based on new Ollama enabled state.
        If Ollama was disabled and Claude is available, auto-switches to Claude.
        If Ollama was enabled, switches back to Ollama.

        Args:
            settings: New settings instance
        """
        self._settings = settings

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
            self._current_backend = settings.ai_backend
            self._load_available_models()

            # Update model selector based on active backend
            if self._current_backend == "ollama" and settings.ollama_model:
                self._chat_bar.set_model(settings.ollama_model)
            elif self._current_backend == "claude" and settings.claude_model:
                self._chat_bar.set_model(settings.claude_model)

        # Update context mode (use new setting with fallback)
        context_mode = settings.chat_context_mode or settings.ollama_chat_context_mode
        self._chat_bar.set_context_mode(context_mode)

        # Update visibility
        self._update_visibility()

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
