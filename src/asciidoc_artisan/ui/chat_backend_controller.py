"""
Chat Backend Controller - Backend switching and visibility management for AI chat.

Extracted from ChatManager to reduce class size (MA principle).
Handles backend selection, visibility control, and UI layout updates.
"""

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, QTimer, Signal

if TYPE_CHECKING:
    from ..core import AppSettings
    from .chat_bar_widget import ChatBarWidget

logger = logging.getLogger(__name__)


class ChatBackendController(QObject):
    """
    Controller for AI backend management and visibility control.

    This class was extracted from ChatManager to reduce class size per MA principle.

    Handles:
    - Backend switching between Ollama (local) and Claude (remote)
    - Chat visibility based on backend availability
    - Splitter sizing for chat pane show/hide
    - Backend status logging for debugging

    Signals:
        visibility_changed: Emitted with (bar_visible, panel_visible) when visibility changes
        settings_changed: Settings were modified (trigger save)
    """

    visibility_changed = Signal(bool, bool)  # bar_visible, panel_visible
    settings_changed = Signal()

    def __init__(
        self,
        settings: "AppSettings",
        chat_bar: "ChatBarWidget",
        current_backend_getter: Any,
        current_backend_setter: Any,
        parent_getter: Any,
        load_models_callback: Any,
    ) -> None:
        """
        Initialize ChatBackendController.

        Args:
            settings: Application settings instance
            chat_bar: Chat bar widget for UI updates
            current_backend_getter: Callable that returns current backend name
            current_backend_setter: Callable that sets current backend name
            parent_getter: Callable that returns parent widget (for splitter access)
            load_models_callback: Callable to reload models after backend switch
        """
        super().__init__()
        self._settings = settings
        self._chat_bar = chat_bar
        self._get_current_backend = current_backend_getter
        self._set_current_backend = current_backend_setter
        self._get_parent = parent_getter
        self._load_models = load_models_callback

    def switch_backend(self, new_backend: str) -> None:
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
        current_backend = self._get_current_backend()
        logger.info(f"Switching backend from {current_backend} to {new_backend}")

        # Step 1: Update which backend is currently active
        # (We track this in two places: instance variable + saved settings)
        self._set_current_backend(new_backend)
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
        self._load_models()

        # Step 4: Update the selected model shown in chat bar dropdown
        if new_backend == "ollama" and self._settings.ollama_model:
            self._chat_bar.set_model(self._settings.ollama_model)
            logger.info(f"Switched to Ollama model: {self._settings.ollama_model}")
        elif new_backend == "claude" and self._settings.claude_model:
            self._chat_bar.set_model(self._settings.claude_model)
            logger.info(f"Switched to Claude model: {self._settings.claude_model}")

        # Step 5: Update AI backend checkmarks in Help menu (real-time visual feedback)
        parent = self._get_parent()
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

    def should_show_chat(self) -> bool:
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
        current_backend = self._get_current_backend()
        if not self._settings.ollama_enabled and has_claude_key:
            if current_backend != "claude":
                logger.info("Auto-switching to Claude backend (Ollama disabled, Claude available)")
                self.switch_backend("claude")
            return bool(self._settings.claude_model)

        # Check backend availability
        if current_backend == "ollama":
            return bool(self._settings.ollama_enabled and self._settings.ollama_model)
        elif current_backend == "claude":
            return bool(has_claude_key and self._settings.claude_model)
        else:
            return False

    def build_backend_status_log(self) -> str:
        """
        Build backend status string for logging.

        MA principle: Extracted from _update_visibility (14 lines).

        Returns:
            Backend status string with configuration details
        """
        current_backend = self._get_current_backend()
        backend_status = f"backend={current_backend}"
        if current_backend == "ollama":
            backend_status += (
                f", ollama_enabled={self._settings.ollama_enabled}, ollama_model={self._settings.ollama_model}"
            )
        elif current_backend == "claude":
            from ..core import SecureCredentials

            creds = SecureCredentials()
            backend_status += f", has_api_key={creds.has_anthropic_key()}, claude_model={self._settings.claude_model}"
        return backend_status

    def show_chat_pane(self, parent: Any) -> None:
        """
        Show chat pane with proportional sizing.

        MA principle: Extracted from _update_visibility (20 lines).

        Args:
            parent: Parent widget with splitter
        """

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

    def hide_chat_pane(self, parent: Any) -> None:
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

    def update_visibility(self) -> None:
        """
        Update chat UI visibility based on settings and active backend.

        MA principle: Reduced from 61→24 lines by extracting 3 helpers (61% reduction).
        """
        chat_visible = self.should_show_chat()

        # Log visibility update with backend details
        backend_status = self.build_backend_status_log()
        logger.info(
            f"Chat visibility update: {backend_status}, "
            f"ai_chat_enabled={self._settings.ai_chat_enabled}, "
            f"chat_visible={chat_visible}"
        )

        # Update chat container visibility
        parent = self._get_parent()
        if parent and hasattr(parent, "chat_container"):
            parent.chat_container.setVisible(chat_visible)

            # Update splitter sizes
            if hasattr(parent, "splitter") and len(parent.splitter.sizes()) == 3:
                sizes = parent.splitter.sizes()
                if chat_visible and sizes[2] == 0:
                    self.show_chat_pane(parent)
                elif not chat_visible and sizes[2] > 0:
                    self.hide_chat_pane(parent)

        self.visibility_changed.emit(chat_visible, chat_visible)
        logger.info(f"Chat pane visibility set: {chat_visible}")
