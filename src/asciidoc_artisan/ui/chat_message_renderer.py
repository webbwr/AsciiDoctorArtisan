"""
Chat Message Renderer - HTML rendering for chat messages.

Extracted from chat_panel_widget.py for MA principle compliance.
Handles theme-aware message styling and HTML generation.
"""

from asciidoc_artisan.core.models import ChatMessage
from asciidoc_artisan.ui.style_constants import DarkTheme, LightTheme


class ChatMessageRenderer:
    """
    Renders ChatMessage objects to HTML with theme support.

    MA principle: Extracted from ChatPanelWidget to reduce class size
    and separate rendering logic from widget management.

    Attributes:
        _dark_mode: Current theme mode (True for dark, False for light)
    """

    def __init__(self, dark_mode: bool = False) -> None:
        """Initialize renderer with theme mode."""
        self._dark_mode = dark_mode

    def set_dark_mode(self, enabled: bool) -> None:
        """Update theme mode."""
        self._dark_mode = enabled

    def get_colors(self) -> dict[str, str]:
        """Get theme-aware colors for message styling.

        Returns:
            Dictionary with color keys for user and AI messages
        """
        if self._dark_mode:
            return {
                "user_bg": DarkTheme.NOTE_BG,  # #1e3a5f
                "user_border": DarkTheme.NOTE_BORDER,  # #4a90e2
                "user_text": "#ffffff",
                "user_meta": "#aaaaaa",
                "ai_bg": DarkTheme.TIP_BG,  # #1e4d2b
                "ai_border": DarkTheme.TIP_BORDER,  # #5cb85c
                "ai_text": "#ffffff",
                "ai_meta": "#aaaaaa",
            }
        else:
            return {
                "user_bg": LightTheme.NOTE_BG,  # #e3f2fd
                "user_border": LightTheme.NOTE_BORDER,  # #2196f3
                "user_text": "#000000",
                "user_meta": "#666666",
                "ai_bg": LightTheme.BG_TERTIARY,  # #f5f5f5
                "ai_border": LightTheme.TIP_BORDER,  # #4caf50
                "ai_text": "#000000",
                "ai_meta": "#666666",
            }

    def format_metadata(self, message: ChatMessage) -> tuple[str, str]:
        """Format timestamp and context mode display for message.

        Args:
            message: ChatMessage to format metadata for

        Returns:
            Tuple of (time_str, mode_display)
        """
        import time

        time_str = time.strftime("%H:%M:%S", time.localtime(message.timestamp))

        # Format context mode badge with user-friendly labels
        mode_display = {
            "document": "📄 Doc",
            "syntax": "📝 Syntax",
            "general": "💬 Chat",
            "editing": "✏️ Edit",
        }.get(message.context_mode, message.context_mode)

        return time_str, mode_display

    def render_message(self, message: ChatMessage, time_str: str, mode_display: str) -> str:
        """Create HTML for message based on role.

        Args:
            message: ChatMessage to render
            time_str: Formatted timestamp string
            mode_display: Formatted context mode display

        Returns:
            HTML string for the message
        """
        colors = self.get_colors()

        if message.role == "user":
            return f"""
            <div style='margin: 10px; padding: 10px; background-color: {colors["user_bg"]};
                        border-left: 4px solid {colors["user_border"]}; border-radius: 4px;'>
                <div style='font-size: 10px; color: {colors["user_meta"]}; margin-bottom: 5px;'>
                    <b>You</b> • {time_str} • {mode_display}
                </div>
                <div style='font-size: 12px; color: {colors["user_text"]};'>
                    {self.escape_html(message.content)}
                </div>
            </div>
            """
        else:
            return f"""
            <div style='margin: 10px; padding: 10px; background-color: {colors["ai_bg"]};
                        border-left: 4px solid {colors["ai_border"]}; border-radius: 4px;'>
                <div style='font-size: 10px; color: {colors["ai_meta"]}; margin-bottom: 5px;'>
                    <b>AI ({message.model})</b> • {time_str} • {mode_display}
                </div>
                <div style='font-size: 12px; color: {colors["ai_text"]}; white-space: pre-wrap;'>
                    {self.escape_html(message.content)}
                </div>
            </div>
            """

    @staticmethod
    def escape_html(text: str) -> str:
        """
        Escape HTML special characters in message text.

        Security: Prevents XSS attacks by escaping HTML entities.
        Order matters: & must be replaced first (otherwise we'd double-escape).

        Args:
            text: Raw message text (possibly containing HTML-like text)

        Returns:
            HTML-safe text ready for display
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
            .replace("\n", "<br>")
        )

    def render_empty_state(self) -> str:
        """Generate HTML for empty chat state.

        Returns:
            HTML string for empty state placeholder
        """
        return """
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
