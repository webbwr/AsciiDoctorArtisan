"""
Chat panel widget for displaying Ollama AI conversation.

This module provides ChatPanelWidget, a scrollable panel that displays
the full chat conversation with visual distinction between user and AI messages.

The widget includes:
- Auto-scrolling message display
- Visual differentiation for user vs AI messages
- Timestamp display for each message
- Model name display for AI responses
- Context mode indicators
- Copy message functionality

Visibility Rules:
    - Shown when: Chat bar is visible (AI enabled + model set)
    - Hidden when: Chat bar is hidden
    - Initially collapsed (can be toggled via UI button)

Specification Reference: FR-039 to FR-044 (Ollama AI Chat)

MA principle: Rendering logic extracted to ChatMessageRenderer (~100 lines saved).
"""

import logging
import time
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ..core.models import ChatMessage
from .chat_message_renderer import ChatMessageRenderer

logger = logging.getLogger(__name__)


class ChatPanelWidget(QWidget):
    """
    Scrollable panel for displaying chat conversation.

    Displays full chat history with visual formatting for user/AI messages,
    timestamps, model names, and context modes.

    Signals:
        copy_requested: Emitted with message text when user wants to copy

    Attributes:
        _text_display: QTextBrowser for message rendering
        _messages: List of ChatMessage objects
        _auto_scroll: Flag to enable auto-scroll to bottom

    Example:
        ```python
        chat_panel = ChatPanelWidget()
        chat_panel.add_user_message("How do I make a table?", model="qwen2.5-coder:7b", mode="syntax")
        chat_panel.add_ai_message("Here's how...", model="qwen2.5-coder:7b")
        chat_panel.show()
        ```
    """

    # Signals
    copy_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Initialize the chat panel widget.

        Args:
            parent: Parent widget (usually MainWindow)
        """
        super().__init__(parent)
        self._messages: list[ChatMessage] = []
        self._auto_scroll = True
        self._dark_mode = False  # Track current theme
        self._renderer = ChatMessageRenderer(dark_mode=self._dark_mode)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the widget layout and display."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Text browser for message display
        self._text_display = QTextBrowser()
        self._text_display.setOpenExternalLinks(False)
        self._text_display.setOpenLinks(False)
        self._text_display.setReadOnly(True)
        layout.addWidget(self._text_display)

        # Set initial empty state
        self._show_empty_state()

    def _show_empty_state(self) -> None:
        """Show placeholder when chat is empty (delegates to renderer)."""
        self._text_display.setHtml(self._renderer.render_empty_state())

    def set_dark_mode(self, enabled: bool) -> None:
        """
        Update theme colors for dark/light mode.

        Args:
            enabled: True for dark mode, False for light mode
        """
        self._dark_mode = enabled
        self._renderer.set_dark_mode(enabled)
        # Refresh all messages with new theme
        self.refresh_display()

    def _get_colors(self) -> dict[str, str]:
        """Get theme-aware colors for message styling (delegates to renderer)."""
        return self._renderer.get_colors()

    def add_user_message(
        self,
        content: str,
        model: str,
        context_mode: str,
        timestamp: float | None = None,
    ) -> None:
        """
        Add a user message to the chat display.

        Args:
            content: User's message text
            model: Model name for this conversation
            context_mode: Context mode (document/syntax/general/editing)
            timestamp: Message timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()

        message = ChatMessage(
            role="user",
            content=content,
            timestamp=timestamp,
            model=model,
            context_mode=context_mode,
        )

        self._messages.append(message)
        self._render_message(message)
        logger.debug(f"Added user message: {content[:50]}...")

    def add_ai_message(
        self,
        content: str,
        model: str,
        context_mode: str,
        timestamp: float | None = None,
    ) -> None:
        """
        Add an AI response message to the chat display.

        Args:
            content: AI's response text
            model: Model that generated the response
            context_mode: Context mode for this response
            timestamp: Message timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()

        message = ChatMessage(
            role="assistant",
            content=content,
            timestamp=timestamp,
            model=model,
            context_mode=context_mode,
        )

        self._messages.append(message)
        self._render_message(message)
        logger.debug(f"Added AI message: {content[:50]}...")

    def add_message(self, message: ChatMessage) -> None:
        """
        Add a ChatMessage object to the display.

        Args:
            message: ChatMessage to display
        """
        self._messages.append(message)
        self._render_message(message)

    def _render_message(self, message: ChatMessage) -> None:
        """
        Render a single message in the display.

        MA principle: Reduced from 63→16 lines by extracting 3 helper methods.

        Args:
            message: ChatMessage to render
        """
        # Clear empty state on first message
        if len(self._messages) == 1:
            self._text_display.clear()

        time_str, mode_display = self._format_message_metadata(message)
        html = self._create_message_html(message, time_str, mode_display)

        # Append to display
        cursor = self._text_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._text_display.setTextCursor(cursor)
        self._text_display.insertHtml(html)

        # Auto-scroll to bottom
        if self._auto_scroll:
            self._scroll_to_bottom()

    def _format_message_metadata(self, message: ChatMessage) -> tuple[str, str]:
        """Format timestamp and context mode display (delegates to renderer)."""
        return self._renderer.format_metadata(message)

    def _create_message_html(self, message: ChatMessage, time_str: str, mode_display: str) -> str:
        """Create HTML for message based on role (delegates to renderer)."""
        return self._renderer.render_message(message, time_str, mode_display)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters (delegates to renderer)."""
        return ChatMessageRenderer.escape_html(text)

    def _scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the chat display."""
        scrollbar = self._text_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_messages(self) -> None:
        """Clear all messages from the display and internal history."""
        self._messages.clear()
        self._text_display.clear()
        self._show_empty_state()
        logger.info("Chat history cleared")

    def load_messages(self, messages: list[ChatMessage]) -> None:
        """
        Load and display a list of chat messages.

        Args:
            messages: List of ChatMessage objects to display
        """
        self._messages = messages.copy()
        self._text_display.clear()

        if not messages:
            self._show_empty_state()
            return

        # Render all messages
        for message in messages:
            self._render_message(message)

        logger.info(f"Loaded {len(messages)} messages")

    def refresh_display(self) -> None:
        """Refresh all messages with current theme."""
        if not self._messages:
            self._show_empty_state()
            return

        self._text_display.clear()
        for message in self._messages:
            self._render_message(message)

    def get_messages(self) -> list[ChatMessage]:
        """
        Get all messages currently in the chat.

        Returns:
            List of ChatMessage objects
        """
        return self._messages.copy()

    def get_message_history(self) -> list[dict[str, Any]]:
        """
        Get message history as dictionaries (for settings/JSON serialization).

        Returns:
            List of message dictionaries
        """
        return [msg.model_dump() for msg in self._messages]

    def set_auto_scroll(self, enabled: bool) -> None:
        """
        Enable or disable auto-scrolling to bottom.

        Args:
            enabled: True to auto-scroll, False to disable
        """
        self._auto_scroll = enabled

    def append_to_last_message(self, text: str) -> None:
        """
        Append text to the last AI message (for streaming support).

        Args:
            text: Text chunk to append
        """
        if not self._messages or self._messages[-1].role != "assistant":
            logger.warning("Cannot append: no AI message to append to")
            return

        # Update last message content
        last_message = self._messages[-1]
        last_message.content += text

        # Re-render the entire chat (simple approach for v1.7.0)
        self._text_display.clear()
        for message in self._messages:
            self._render_message(message)

    def get_message_count(self) -> int:
        """
        Get the total number of messages in the chat.

        Returns:
            Message count
        """
        return len(self._messages)

    def export_to_text(self) -> str:
        """
        Export chat history to plain text format.

        Returns:
            Plain text representation of chat history
        """
        if not self._messages:
            return "No messages in chat history."

        lines = ["Chat History Export", "=" * 50, ""]

        for message in self._messages:
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(message.timestamp))
            role = "You" if message.role == "user" else f"AI ({message.model})"
            lines.append(f"[{time_str}] {role} ({message.context_mode}):")
            lines.append(message.content)
            lines.append("")

        return "\n".join(lines)
