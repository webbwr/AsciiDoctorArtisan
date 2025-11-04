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

Specification Reference: Lines 228-329 (Ollama AI Chat Rules)
"""

import logging
import time
from typing import List, Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ..core.models import ChatMessage

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

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the chat panel widget.

        Args:
            parent: Parent widget (usually MainWindow)
        """
        super().__init__(parent)
        self._messages: List[ChatMessage] = []
        self._auto_scroll = True
        self._dark_mode = False  # Track current theme
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
        """Show placeholder when chat is empty."""
        empty_html = """
        <div style='text-align: center; padding: 40px; color: #888;'>
            <p style='font-size: 14px; margin-bottom: 10px;'>
                <b>AI Chat Ready</b>
            </p>
            <p style='font-size: 12px;'>
                Ask a question in the chat bar below to start a conversation.
            </p>
            <p style='font-size: 11px; margin-top: 20px;'>
                Context modes:<br>
                • <b>Document Q&A</b>: Questions about current document<br>
                • <b>Syntax Help</b>: AsciiDoc formatting help<br>
                • <b>General Chat</b>: General questions<br>
                • <b>Editing Suggestions</b>: Get editing feedback
            </p>
        </div>
        """
        self._text_display.setHtml(empty_html)

    def set_dark_mode(self, enabled: bool) -> None:
        """
        Update theme colors for dark/light mode.

        Args:
            enabled: True for dark mode, False for light mode
        """
        self._dark_mode = enabled
        # Refresh all messages with new theme
        self.refresh_display()

    def _get_colors(self) -> dict:
        """Get theme-aware colors for message styling."""
        if self._dark_mode:
            return {
                "user_bg": "#1e3a5f",
                "user_border": "#4a90e2",
                "user_text": "#ffffff",
                "user_meta": "#aaaaaa",
                "ai_bg": "#1e4d2b",
                "ai_border": "#5cb85c",
                "ai_text": "#ffffff",
                "ai_meta": "#aaaaaa",
            }
        else:
            return {
                "user_bg": "#e3f2fd",
                "user_border": "#2196f3",
                "user_text": "#000000",
                "user_meta": "#666666",
                "ai_bg": "#f5f5f5",
                "ai_border": "#4caf50",
                "ai_text": "#000000",
                "ai_meta": "#666666",
            }

    def add_user_message(
        self,
        content: str,
        model: str,
        context_mode: str,
        timestamp: Optional[float] = None,
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
        timestamp: Optional[float] = None,
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

        Args:
            message: ChatMessage to render
        """
        # Clear empty state on first message
        if len(self._messages) == 1:
            self._text_display.clear()

        # Format timestamp
        time_str = time.strftime("%H:%M:%S", time.localtime(message.timestamp))

        # Format context mode badge
        mode_display = {
            "document": "📄 Doc",
            "syntax": "📝 Syntax",
            "general": "💬 Chat",
            "editing": "✏️ Edit",
        }.get(message.context_mode, message.context_mode)

        colors = self._get_colors()

        if message.role == "user":
            # User message styling
            html = f"""
            <div style='margin: 10px; padding: 10px; background-color: {colors['user_bg']};
                        border-left: 4px solid {colors['user_border']}; border-radius: 4px;'>
                <div style='font-size: 10px; color: {colors['user_meta']}; margin-bottom: 5px;'>
                    <b>You</b> • {time_str} • {mode_display}
                </div>
                <div style='font-size: 12px; color: {colors['user_text']};'>
                    {self._escape_html(message.content)}
                </div>
            </div>
            """
        else:
            # AI message styling
            html = f"""
            <div style='margin: 10px; padding: 10px; background-color: {colors['ai_bg']};
                        border-left: 4px solid {colors['ai_border']}; border-radius: 4px;'>
                <div style='font-size: 10px; color: {colors['ai_meta']}; margin-bottom: 5px;'>
                    <b>AI ({message.model})</b> • {time_str} • {mode_display}
                </div>
                <div style='font-size: 12px; color: {colors['ai_text']}; white-space: pre-wrap;'>
                    {self._escape_html(message.content)}
                </div>
            </div>
            """

        # Append to display
        cursor = self._text_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._text_display.setTextCursor(cursor)
        self._text_display.insertHtml(html)

        # Auto-scroll to bottom
        if self._auto_scroll:
            self._scroll_to_bottom()

    def _escape_html(self, text: str) -> str:
        """
        Escape HTML special characters in message text.

        Args:
            text: Raw message text

        Returns:
            HTML-escaped text
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
            .replace("\n", "<br>")
        )

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

    def load_messages(self, messages: List[ChatMessage]) -> None:
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

    def get_messages(self) -> List[ChatMessage]:
        """
        Get all messages currently in the chat.

        Returns:
            List of ChatMessage objects
        """
        return self._messages.copy()

    def get_message_history(self) -> List[dict]:
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
            time_str = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(message.timestamp)
            )
            role = "You" if message.role == "user" else f"AI ({message.model})"
            lines.append(f"[{time_str}] {role} ({message.context_mode}):")
            lines.append(message.content)
            lines.append("")

        return "\n".join(lines)
