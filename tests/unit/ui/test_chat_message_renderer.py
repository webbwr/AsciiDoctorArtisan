"""
Unit tests for ChatMessageRenderer.

Tests HTML rendering for chat messages with theme support.
Extracted as part of MA principle compliance (chat_panel_widget.py split).
"""

import pytest
import time

from asciidoc_artisan.core.models import ChatMessage
from asciidoc_artisan.ui.chat_message_renderer import ChatMessageRenderer


class TestChatMessageRendererInitialization:
    """Tests for ChatMessageRenderer initialization."""

    def test_initialization_default_theme(self):
        """Test renderer initializes with light mode by default."""
        renderer = ChatMessageRenderer()
        assert renderer._dark_mode is False

    def test_initialization_dark_mode(self):
        """Test renderer can be initialized with dark mode."""
        renderer = ChatMessageRenderer(dark_mode=True)
        assert renderer._dark_mode is True

    def test_set_dark_mode(self):
        """Test dark mode can be changed after initialization."""
        renderer = ChatMessageRenderer()
        renderer.set_dark_mode(True)
        assert renderer._dark_mode is True


class TestChatMessageRendererColors:
    """Tests for get_colors method."""

    def test_light_mode_colors(self):
        """Test light mode color palette."""
        renderer = ChatMessageRenderer(dark_mode=False)
        colors = renderer.get_colors()

        assert colors["user_bg"] == "#e3f2fd"
        assert colors["user_border"] == "#2196f3"
        assert colors["user_text"] == "#000000"
        assert colors["ai_bg"] == "#f5f5f5"
        assert colors["ai_border"] == "#4caf50"
        assert colors["ai_text"] == "#000000"

    def test_dark_mode_colors(self):
        """Test dark mode color palette."""
        renderer = ChatMessageRenderer(dark_mode=True)
        colors = renderer.get_colors()

        assert colors["user_bg"] == "#1e3a5f"
        assert colors["user_border"] == "#4a90e2"
        assert colors["user_text"] == "#ffffff"
        assert colors["ai_bg"] == "#1e4d2b"
        assert colors["ai_border"] == "#5cb85c"
        assert colors["ai_text"] == "#ffffff"


class TestChatMessageRendererMetadata:
    """Tests for format_metadata method."""

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        renderer = ChatMessageRenderer()
        message = ChatMessage(
            role="user",
            content="test",
            timestamp=1700000000,  # Fixed timestamp
            model="test-model",
            context_mode="general",
        )
        time_str, _ = renderer.format_metadata(message)
        # Verify it's in HH:MM:SS format
        assert ":" in time_str
        assert len(time_str.split(":")) == 3

    def test_format_context_mode_document(self):
        """Test document context mode formatting."""
        renderer = ChatMessageRenderer()
        message = ChatMessage(
            role="user",
            content="test",
            timestamp=time.time(),
            model="test-model",
            context_mode="document",
        )
        _, mode_display = renderer.format_metadata(message)
        assert mode_display == "📄 Doc"

    def test_format_context_mode_syntax(self):
        """Test syntax context mode formatting."""
        renderer = ChatMessageRenderer()
        message = ChatMessage(
            role="user",
            content="test",
            timestamp=time.time(),
            model="test-model",
            context_mode="syntax",
        )
        _, mode_display = renderer.format_metadata(message)
        assert mode_display == "📝 Syntax"

    def test_format_context_mode_general(self):
        """Test general context mode formatting."""
        renderer = ChatMessageRenderer()
        message = ChatMessage(
            role="user",
            content="test",
            timestamp=time.time(),
            model="test-model",
            context_mode="general",
        )
        _, mode_display = renderer.format_metadata(message)
        assert mode_display == "💬 Chat"

    def test_format_context_mode_editing(self):
        """Test editing context mode formatting."""
        renderer = ChatMessageRenderer()
        message = ChatMessage(
            role="user",
            content="test",
            timestamp=time.time(),
            model="test-model",
            context_mode="editing",
        )
        _, mode_display = renderer.format_metadata(message)
        assert mode_display == "✏️ Edit"

    # Note: Unknown context_mode test removed - ChatMessage model validates
    # context_mode to be one of {'document', 'syntax', 'general', 'editing'}


class TestChatMessageRendererHTML:
    """Tests for render_message method."""

    def test_render_user_message(self):
        """Test rendering a user message."""
        renderer = ChatMessageRenderer()
        message = ChatMessage(
            role="user",
            content="Hello world",
            timestamp=time.time(),
            model="test-model",
            context_mode="general",
        )
        time_str, mode_display = renderer.format_metadata(message)
        html = renderer.render_message(message, time_str, mode_display)

        assert "Hello world" in html
        assert "You" in html
        assert "#e3f2fd" in html  # Light mode user_bg

    def test_render_ai_message(self):
        """Test rendering an AI message."""
        renderer = ChatMessageRenderer()
        message = ChatMessage(
            role="assistant",
            content="Hello from AI",
            timestamp=time.time(),
            model="gpt-4",
            context_mode="general",
        )
        time_str, mode_display = renderer.format_metadata(message)
        html = renderer.render_message(message, time_str, mode_display)

        assert "Hello from AI" in html
        assert "AI (gpt-4)" in html
        assert "#f5f5f5" in html  # Light mode ai_bg

    def test_render_dark_mode_user_message(self):
        """Test rendering user message in dark mode."""
        renderer = ChatMessageRenderer(dark_mode=True)
        message = ChatMessage(
            role="user",
            content="Dark mode test",
            timestamp=time.time(),
            model="test-model",
            context_mode="general",
        )
        time_str, mode_display = renderer.format_metadata(message)
        html = renderer.render_message(message, time_str, mode_display)

        assert "Dark mode test" in html
        assert "#1e3a5f" in html  # Dark mode user_bg


class TestChatMessageRendererEscaping:
    """Tests for escape_html method."""

    def test_escape_ampersand(self):
        """Test ampersand escaping."""
        result = ChatMessageRenderer.escape_html("Tom & Jerry")
        assert "&amp;" in result
        assert "Tom &amp; Jerry" == result

    def test_escape_less_than(self):
        """Test less than escaping."""
        result = ChatMessageRenderer.escape_html("<script>")
        assert "&lt;script&gt;" == result

    def test_escape_greater_than(self):
        """Test greater than escaping."""
        result = ChatMessageRenderer.escape_html("5 > 3")
        assert "5 &gt; 3" == result

    def test_escape_double_quote(self):
        """Test double quote escaping."""
        result = ChatMessageRenderer.escape_html('Say "hello"')
        assert "&quot;" in result

    def test_escape_single_quote(self):
        """Test single quote escaping."""
        result = ChatMessageRenderer.escape_html("It's working")
        assert "&#39;" in result

    def test_escape_newlines(self):
        """Test newline to br conversion."""
        result = ChatMessageRenderer.escape_html("Line 1\nLine 2")
        assert "<br>" in result
        assert "Line 1<br>Line 2" == result

    def test_escape_xss_attempt(self):
        """Test XSS prevention."""
        result = ChatMessageRenderer.escape_html("<script>alert('hack')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result


class TestChatMessageRendererEmptyState:
    """Tests for render_empty_state method."""

    def test_empty_state_contains_title(self):
        """Test empty state contains AI Chat Ready title."""
        renderer = ChatMessageRenderer()
        html = renderer.render_empty_state()
        assert "AI Chat Ready" in html

    def test_empty_state_contains_instructions(self):
        """Test empty state contains instructions."""
        renderer = ChatMessageRenderer()
        html = renderer.render_empty_state()
        assert "Ask a question" in html

    def test_empty_state_contains_context_modes(self):
        """Test empty state lists context modes."""
        renderer = ChatMessageRenderer()
        html = renderer.render_empty_state()
        assert "Document Q&amp;A" in html or "Document Q&A" in html
        assert "Syntax Help" in html
        assert "General Chat" in html
        assert "Editing Suggestions" in html
