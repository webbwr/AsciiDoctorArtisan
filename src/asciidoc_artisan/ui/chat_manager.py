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
from typing import Any, Callable, List, Optional, cast

from PySide6.QtCore import QObject, QTimer, Signal

from ..core.models import ChatMessage
from ..core.settings import Settings

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
        self._current_backend: str = settings.ai_backend  # "ollama" or "claude"

        # Document content debouncing (500ms delay)
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(500)

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
        context_mode = (
            self._settings.chat_context_mode
            or self._settings.ollama_chat_context_mode
        )
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
        self.status_message.emit(
            f"Downloading {default_model}... (this may take a few minutes)"
        )

        try:
            # Run ollama pull in subprocess (non-blocking for UI)
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
        """
        Switch to a different AI backend and update UI accordingly.

        This method handles the complete backend switch process:
        1. Updates current backend tracking
        2. Updates settings
        3. Sets default model if needed
        4. Reloads models for new backend
        5. Updates chat bar dropdown

        Args:
            new_backend: Backend to switch to ("ollama" or "claude")
        """
        logger.info(f"Switching backend from {self._current_backend} to {new_backend}")

        # Update backend tracking
        self._current_backend = new_backend
        self._settings.ai_backend = new_backend

        # Set default model if not configured
        if new_backend == "claude" and not self._settings.claude_model:
            self._settings.claude_model = "claude-sonnet-4-20250514"
        elif new_backend == "ollama" and not self._settings.ollama_model:
            self._settings.ollama_model = "gnokit/improve-grammer"

        # Reload models for new backend
        self._load_available_models()

        # Update selected model in chat bar
        if new_backend == "ollama" and self._settings.ollama_model:
            self._chat_bar.set_model(self._settings.ollama_model)
            logger.info(f"Switched to Ollama model: {self._settings.ollama_model}")
        elif new_backend == "claude" and self._settings.claude_model:
            self._chat_bar.set_model(self._settings.claude_model)
            logger.info(f"Switched to Claude model: {self._settings.claude_model}")

        # Update AI backend checkmarks in Help menu (real-time)
        parent = self.parent()
        if parent and hasattr(parent, "_update_ai_backend_checkmarks"):
            parent._update_ai_backend_checkmarks()
            logger.debug(f"Updated AI backend checkmarks for {new_backend}")

        # Update Scan Models button visibility (only for Claude backend)
        self._chat_bar.set_scan_models_visible(new_backend == "claude")
        logger.debug(f"Scan Models button visible: {new_backend == 'claude'}")

        # Emit settings changed signal
        self.settings_changed.emit()

    def _load_available_models(self) -> None:
        """
        Load available models into chat bar selector based on active backend.

        For Ollama: Detects installed models via `ollama list` command
        For Claude: Uses hardcoded model list from ClaudeClient

        Falls back to defaults if backend is not available.
        """
        if self._current_backend == "ollama":
            self._load_ollama_models()
        elif self._current_backend == "claude":
            self._load_claude_models()
        else:
            logger.error(f"Unknown backend: {self._current_backend}")
            self.status_message.emit(f"Error: Unknown AI backend '{self._current_backend}'")

    def _load_ollama_models(self) -> None:
        """Load available Ollama models."""
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
                            # Model name is first column (e.g., "gnokit/improve-grammer")
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
                "gnokit/improve-grammer",
                "deepseek-coder",
                "codellama",
            ]
            if not ollama_available:
                logger.info("Using default Ollama model list (Ollama not detected)")

        # Add current model if not in list
        if self._settings.ollama_model and self._settings.ollama_model not in models:
            models.insert(0, self._settings.ollama_model)

        self._chat_bar.set_models(models)
        logger.debug(f"Loaded {len(models)} Ollama models into chat bar")

    def _load_claude_models(self) -> None:
        """Load available Claude models."""
        try:
            # Import ClaudeClient to get available models
            from ..claude import ClaudeClient

            models = ClaudeClient.AVAILABLE_MODELS.copy()
            logger.info(f"Claude models available: {len(models)}")

            # Check if API key is configured
            from ..core import SecureCredentials

            creds = SecureCredentials()
            if creds.has_anthropic_key():
                self.status_message.emit(f"Claude: {len(models)} model(s) available")
            else:
                self.status_message.emit(
                    "Claude: API key required (Tools → API Key Setup)"
                )

        except Exception as e:
            logger.error(f"Error loading Claude models: {e}")
            # Fallback to hardcoded defaults
            models = [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-sonnet-4-20250514",
            ]

        # Add current model if not in list
        if self._settings.claude_model and self._settings.claude_model not in models:
            models.insert(0, self._settings.claude_model)

        self._chat_bar.set_models(models)
        logger.debug(f"Loaded {len(models)} Claude models into chat bar")

    def _load_chat_history(self) -> None:
        """Load chat history from settings and display in panel."""
        # Use new backend-agnostic setting (with fallback to deprecated)
        history_dicts = (
            self._settings.chat_history or self._settings.ollama_chat_history or []
        )

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
        """Save current chat history to settings (backend-agnostic)."""
        messages = self._chat_panel.get_messages()

        # Apply max history limit (use new setting with fallback)
        max_history = (
            self._settings.chat_max_history or self._settings.ollama_chat_max_history
        )
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
        """
        Validate that a model exists for the active backend.

        For Ollama: Runs `ollama list` to check if model is installed
        For Claude: Checks against AVAILABLE_MODELS list

        Args:
            model: Model name to validate

        Returns:
            True if model is available, False otherwise
        """
        if not model:
            return False

        if self._current_backend == "claude":
            # Validate Claude model against available models
            try:
                from ..claude import ClaudeClient
                is_valid = model in ClaudeClient.AVAILABLE_MODELS
                logger.debug(f"Claude model validation: {model} -> {is_valid}")
                return is_valid
            except Exception as e:
                logger.error(f"Error validating Claude model: {e}")
                return False

        elif self._current_backend == "ollama":
            # Validate Ollama model via subprocess
            try:
                # Check if model exists via ollama list
                result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False,
                )

                if result.returncode == 0:
                    # Parse output and check if model is in list
                    lines = result.stdout.strip().split("\n")
                    if len(lines) > 1:  # Skip header
                        for line in lines[1:]:
                            parts = line.split()
                            if parts and parts[0] == model:
                                logger.debug(f"Ollama model validated: {model}")
                                return True

                    # Model not found in list
                    logger.debug(f"Model not found in ollama list: {model}")
                    return False
                else:
                    logger.warning(f"ollama list failed: {result.stderr.strip()}")
                    return False

            except FileNotFoundError:
                logger.warning("Ollama not found in PATH")
                return False

            except subprocess.TimeoutExpired:
                logger.warning("Model validation timed out")
                # If validation times out, assume model is valid to avoid blocking
                return True

            except Exception as e:
                logger.warning(f"Error validating Ollama model: {e}")
                # On error, assume model is valid to avoid blocking
                return True

        else:
            logger.error(f"Unknown backend: {self._current_backend}")
            return False

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
        chat_enabled = (
            self._settings.ai_chat_enabled or self._settings.ollama_chat_enabled
        )

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

    def _update_visibility(self) -> None:
        """Update chat UI visibility based on settings and active backend."""
        chat_visible = self._should_show_chat()

        backend_status = f"backend={self._current_backend}"
        if self._current_backend == "ollama":
            backend_status += f", ollama_enabled={self._settings.ollama_enabled}, ollama_model={self._settings.ollama_model}"
        elif self._current_backend == "claude":
            from ..core import SecureCredentials

            creds = SecureCredentials()
            backend_status += f", has_api_key={creds.has_anthropic_key()}, claude_model={self._settings.claude_model}"

        logger.info(
            f"Chat visibility update: {backend_status}, "
            f"ai_chat_enabled={self._settings.ai_chat_enabled}, "
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
        # Use new backend-agnostic setting (with fallback)
        send_document = (
            self._settings.chat_send_document or self._settings.ollama_chat_send_document
        )
        if context_mode in ("document", "editing") and send_document:
            if self._document_content_provider:
                document_content = self._document_content_provider()
                logger.debug(
                    f"Including document content ({len(document_content or '')} chars)"
                )

        # Emit signal to send to worker (worker routes to appropriate backend)
        self.message_sent_to_worker.emit(
            message, model, context_mode, history, document_content
        )

        # Update UI state
        self._is_processing = True
        self._chat_bar.set_processing(True)
        backend_name = self._current_backend.capitalize()
        self.status_message.emit(f"{backend_name} is thinking ({model})...")

        logger.info(
            f"Sent message to {backend_name} worker: {message[:50]}... (mode: {context_mode})"
        )

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
        """
        Handle model selector change with validation.

        Validates that the selected model exists for the active backend.
        Updates status bar with real-time feedback.

        Args:
            model: New model name
        """
        if not model:
            logger.warning("Empty model name provided")
            self.status_message.emit("Error: No model selected")
            return

        # Validate model exists for active backend
        logger.info(f"Validating model selection: {model}")
        self.status_message.emit(f"Validating model: {model}...")

        if self._validate_model(model):
            # Model is valid - update settings for active backend
            if self._current_backend == "ollama":
                self._settings.ollama_model = model
            elif self._current_backend == "claude":
                self._settings.claude_model = model

            self.settings_changed.emit()
            backend_name = self._current_backend.capitalize()
            self.status_message.emit(f"✓ Switched to {backend_name} model: {model}")
            logger.info(f"Model changed to: {model} (backend: {self._current_backend})")
        else:
            # Model is invalid - keep current model and show error
            if self._current_backend == "ollama":
                current_model = self._settings.ollama_model or "none"
            elif self._current_backend == "claude":
                current_model = self._settings.claude_model or "none"
            else:
                current_model = "none"

            logger.warning(f"Model validation failed: {model} not found")
            self.status_message.emit(
                f"✗ Model '{model}' not available (keeping {current_model})"
            )

            # Revert selector to current valid model
            if current_model and current_model != "none":
                self._chat_bar.set_model(current_model)

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
        """
        Handle scan models button click.

        Fetches available models from Anthropic API and displays in chat.
        Only works for Claude backend.
        """
        if self._current_backend != "claude":
            logger.warning("Scan models only available for Claude backend")
            self.status_message.emit("⚠️ Model scanning only available for Claude")
            return

        logger.info("Scanning Anthropic API for available models")
        self.status_message.emit("Scanning Anthropic API for models...")

        try:
            from asciidoc_artisan.claude import ClaudeClient

            client = ClaudeClient()
            result = client.fetch_available_models_from_api()

            if result.success:
                # Display models in chat panel as system message
                self._chat_panel.add_message("system", f"🔍 **Available Models**\n\n{result.content}")
                self.status_message.emit(f"✓ Model scan complete")
                logger.info("Model scan successful")
            else:
                # Display error in chat
                error_msg = f"❌ **Model Scan Failed**\n\n{result.error}"
                self._chat_panel.add_message("system", error_msg)
                self.status_message.emit(f"✗ Model scan failed")
                logger.error(f"Model scan failed: {result.error}")

        except Exception as e:
            logger.exception(f"Error scanning models: {e}")
            error_msg = f"❌ **Error Scanning Models**\n\n{str(e)}"
            self._chat_panel.add_message("system", error_msg)
            self.status_message.emit("✗ Error scanning models")

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
            logger.info(
                f"Backend switch triggered by settings change: {self._current_backend} → {target_backend}"
            )
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
        max_history = (
            self._settings.chat_max_history or self._settings.ollama_chat_max_history
        )
        if len(self._chat_history) > max_history:
            self._chat_history = self._chat_history[-max_history:]
            logger.info(f"Trimmed internal history to {max_history} messages")
