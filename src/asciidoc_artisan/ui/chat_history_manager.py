"""
Chat History Manager - Manages chat history persistence and operations.

Provides:
- History loading and saving
- History trimming and clearing
- Export functionality
"""

import logging
from typing import Any

from ..core.models import ChatMessage
from ..core.settings import Settings

logger = logging.getLogger(__name__)


class ChatHistoryManager:
    """Manages chat history operations for ChatManager.

    Handles loading, saving, clearing, and exporting chat history.
    """

    def __init__(
        self,
        settings: Settings,
        chat_panel: Any,  # ChatPanelWidget (circular import avoidance)
        settings_changed_callback: Any,  # Callable to emit settings_changed
    ) -> None:
        """Initialize ChatHistoryManager."""
        self._settings = settings
        self._chat_panel = chat_panel
        self._settings_changed_callback = settings_changed_callback
        self._chat_history: list[ChatMessage] = []

    def update_settings(self, settings: Settings) -> None:
        """Update settings reference."""
        self._settings = settings

    def load_history(self) -> None:
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

    def save_history(self) -> None:
        """Save current chat history to settings (backend-agnostic)."""
        messages = self._chat_panel.get_messages()

        # Apply max history limit (use most restrictive limit for backward compatibility)
        max_history = min(self._settings.chat_max_history, self._settings.ollama_chat_max_history)
        if len(messages) > max_history:
            messages = messages[-max_history:]
            logger.info(f"Trimmed history to {max_history} messages")

        # Convert ChatMessage objects to dicts for JSON serialization
        history_dicts = [msg.model_dump() for msg in messages]

        # Update both new and deprecated settings for backward compatibility
        self._settings.chat_history = history_dicts
        self._settings.ollama_chat_history = history_dicts
        self._settings_changed_callback()

    def clear_history(self) -> None:
        """Clear chat history from panel and settings (backend-agnostic)."""
        self._chat_panel.clear_messages()
        self._chat_history.clear()
        # Clear both new and deprecated settings
        self._settings.chat_history = []
        self._settings.ollama_chat_history = []
        self._settings_changed_callback()
        logger.info("Chat history cleared")

    def trim_history(self) -> None:
        """Trim chat history to max limit (backend-agnostic)."""
        max_history = self._settings.chat_max_history or self._settings.ollama_chat_max_history
        if len(self._chat_history) > max_history:
            self._chat_history = self._chat_history[-max_history:]
            logger.info(f"Trimmed internal history to {max_history} messages")

    def export_to_text(self) -> str:
        """Export chat history to plain text."""
        return str(self._chat_panel.export_to_text())

    def get_message_count(self) -> int:
        """Get total number of messages in chat."""
        return int(self._chat_panel.get_message_count())
