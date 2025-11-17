"""
Tests for ui.chat_panel_widget module.

Tests chat panel widget for AI conversation display including:
- Widget initialization and UI setup
- User and AI message display
- Theme switching (dark/light mode)
- Message history management
- Auto-scrolling functionality
- HTML escaping for security
- Empty state display
- Message export to text
"""

import time

import pytest
from PySide6.QtWidgets import QTextBrowser

from asciidoc_artisan.core.models import ChatMessage
from asciidoc_artisan.ui.chat_panel_widget import ChatPanelWidget


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestChatPanelWidgetInitialization:
    """Test ChatPanelWidget initialization."""

    def test_initialization_without_parent(self, qapp):
        """Test widget initializes without parent."""
        widget = ChatPanelWidget()

        assert widget is not None

    def test_initialization_with_parent(self, qapp):
        """Test widget initializes with parent."""
        from PySide6.QtWidgets import QWidget

        parent = QWidget()
        widget = ChatPanelWidget(parent)

        assert widget.parent() is parent

    def test_has_text_display(self, qapp):
        """Test widget has text display browser."""
        widget = ChatPanelWidget()

        assert isinstance(widget._text_display, QTextBrowser)
        assert widget._text_display.isReadOnly()

    def test_initial_messages_empty(self, qapp):
        """Test initial message list is empty."""
        widget = ChatPanelWidget()

        assert widget._messages == []
        assert widget.get_message_count() == 0

    def test_auto_scroll_enabled_by_default(self, qapp):
        """Test auto-scroll is enabled by default."""
        widget = ChatPanelWidget()

        assert widget._auto_scroll is True

    def test_dark_mode_disabled_by_default(self, qapp):
        """Test dark mode is disabled by default."""
        widget = ChatPanelWidget()

        assert widget._dark_mode is False

    def test_shows_empty_state_initially(self, qapp):
        """Test empty state is shown when no messages."""
        widget = ChatPanelWidget()

        html = widget._text_display.toHtml()
        assert "AI Chat Ready" in html
        assert "Ask a question" in html


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestUserMessageDisplay:
    """Test user message display."""

    def test_add_user_message(self, qapp):
        """Test adding a user message."""
        widget = ChatPanelWidget()

        widget.add_user_message(
            content="Test question",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
        )

        assert len(widget._messages) == 1
        assert widget._messages[0].role == "user"
        assert widget._messages[0].content == "Test question"
        assert widget._messages[0].model == "qwen2.5-coder:7b"
        assert widget._messages[0].context_mode == "syntax"

    def test_add_user_message_generates_timestamp(self, qapp):
        """Test user message gets current timestamp if not provided."""
        widget = ChatPanelWidget()

        before = time.time()
        widget.add_user_message(
            content="Test",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
        )
        after = time.time()

        message_time = widget._messages[0].timestamp
        assert before <= message_time <= after

    def test_add_user_message_uses_provided_timestamp(self, qapp):
        """Test user message uses provided timestamp."""
        widget = ChatPanelWidget()
        timestamp = 1234567890.0

        widget.add_user_message(
            content="Test",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
            timestamp=timestamp,
        )

        assert widget._messages[0].timestamp == timestamp

    def test_add_user_message_clears_empty_state(self, qapp):
        """Test first user message clears empty state."""
        widget = ChatPanelWidget()

        widget.add_user_message(
            content="First message",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
        )

        html = widget._text_display.toHtml()
        assert "AI Chat Ready" not in html
        assert "First message" in html


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestAIMessageDisplay:
    """Test AI message display."""

    def test_add_ai_message(self, qapp):
        """Test adding an AI message."""
        widget = ChatPanelWidget()

        widget.add_ai_message(
            content="AI response",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
        )

        assert len(widget._messages) == 1
        assert widget._messages[0].role == "assistant"
        assert widget._messages[0].content == "AI response"
        assert widget._messages[0].model == "qwen2.5-coder:7b"

    def test_add_ai_message_generates_timestamp(self, qapp):
        """Test AI message gets current timestamp if not provided."""
        widget = ChatPanelWidget()

        before = time.time()
        widget.add_ai_message(
            content="Response",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
        )
        after = time.time()

        message_time = widget._messages[0].timestamp
        assert before <= message_time <= after

    def test_add_ai_message_uses_provided_timestamp(self, qapp):
        """Test AI message uses provided timestamp."""
        widget = ChatPanelWidget()
        timestamp = 1234567890.0

        widget.add_ai_message(
            content="Response",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
            timestamp=timestamp,
        )

        assert widget._messages[0].timestamp == timestamp

    def test_add_ai_message_displays_model_name(self, qapp):
        """Test AI message displays model name."""
        widget = ChatPanelWidget()

        widget.add_ai_message(
            content="Response",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
        )

        html = widget._text_display.toHtml()
        assert "qwen2.5-coder:7b" in html


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestMessageObject:
    """Test add_message with ChatMessage objects."""

    def test_add_message(self, qapp):
        """Test adding a ChatMessage object."""
        widget = ChatPanelWidget()

        message = ChatMessage(
            role="user",
            content="Test",
            timestamp=time.time(),
            model="qwen2.5-coder:7b",
            context_mode="syntax",
        )

        widget.add_message(message)

        assert len(widget._messages) == 1
        assert widget._messages[0] == message


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestThemeSwitching:
    """Test dark/light mode theme switching."""

    def test_set_dark_mode_true(self, qapp):
        """Test enabling dark mode."""
        widget = ChatPanelWidget()

        widget.set_dark_mode(True)

        assert widget._dark_mode is True

    def test_set_dark_mode_false(self, qapp):
        """Test disabling dark mode (light mode)."""
        widget = ChatPanelWidget()
        widget._dark_mode = True

        widget.set_dark_mode(False)

        assert widget._dark_mode is False

    def test_get_colors_dark_mode(self, qapp):
        """Test get_colors returns dark mode colors."""
        widget = ChatPanelWidget()
        widget._dark_mode = True

        colors = widget._get_colors()

        assert colors["user_bg"] == "#1e3a5f"
        assert colors["user_border"] == "#4a90e2"
        assert colors["ai_bg"] == "#1e4d2b"
        assert colors["ai_border"] == "#5cb85c"

    def test_get_colors_light_mode(self, qapp):
        """Test get_colors returns light mode colors."""
        widget = ChatPanelWidget()
        widget._dark_mode = False

        colors = widget._get_colors()

        assert colors["user_bg"] == "#e3f2fd"
        assert colors["user_border"] == "#2196f3"
        assert colors["ai_bg"] == "#f5f5f5"
        assert colors["ai_border"] == "#4caf50"


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestMessageRendering:
    """Test message rendering."""

    def test_render_message_formats_timestamp(self, qapp):
        """Test message rendering includes formatted timestamp."""
        widget = ChatPanelWidget()
        timestamp = 1234567890.0  # 2009-02-13 23:31:30 UTC

        widget.add_user_message(
            content="Test",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
            timestamp=timestamp,
        )

        html = widget._text_display.toHtml()
        # Should contain time in HH:MM:SS format
        time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
        assert time_str in html

    def test_render_message_shows_context_mode_document(self, qapp):
        """Test message shows document Q&A context mode."""
        widget = ChatPanelWidget()

        widget.add_user_message(
            content="Test",
            model="qwen2.5-coder:7b",
            context_mode="document",
        )

        html = widget._text_display.toHtml()
        assert "📄 Doc" in html

    def test_render_message_shows_context_mode_syntax(self, qapp):
        """Test message shows syntax help context mode."""
        widget = ChatPanelWidget()

        widget.add_user_message(
            content="Test",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
        )

        html = widget._text_display.toHtml()
        assert "📝 Syntax" in html

    def test_render_message_shows_context_mode_general(self, qapp):
        """Test message shows general chat context mode."""
        widget = ChatPanelWidget()

        widget.add_user_message(
            content="Test",
            model="qwen2.5-coder:7b",
            context_mode="general",
        )

        html = widget._text_display.toHtml()
        assert "💬 Chat" in html

    def test_render_message_shows_context_mode_editing(self, qapp):
        """Test message shows editing suggestions context mode."""
        widget = ChatPanelWidget()

        widget.add_user_message(
            content="Test",
            model="qwen2.5-coder:7b",
            context_mode="editing",
        )

        html = widget._text_display.toHtml()
        assert "✏️ Edit" in html


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestHTMLEscaping:
    """Test HTML escaping for security."""

    def test_escape_html_escapes_angle_brackets(self, qapp):
        """Test HTML escaping converts < and > to entities."""
        widget = ChatPanelWidget()

        escaped = widget._escape_html("<script>alert('XSS')</script>")

        assert "&lt;script&gt;" in escaped
        assert "&lt;/script&gt;" in escaped

    def test_escape_html_escapes_ampersand(self, qapp):
        """Test HTML escaping converts & to entity."""
        widget = ChatPanelWidget()

        escaped = widget._escape_html("Tom & Jerry")

        assert "&amp;" in escaped

    def test_escape_html_escapes_quotes(self, qapp):
        """Test HTML escaping converts quotes to entities."""
        widget = ChatPanelWidget()

        escaped = widget._escape_html("He said \"hello\" and 'goodbye'")

        assert "&quot;" in escaped
        assert "&#39;" in escaped

    def test_escape_html_converts_newlines_to_breaks(self, qapp):
        """Test HTML escaping converts newlines to <br> tags."""
        widget = ChatPanelWidget()

        escaped = widget._escape_html("Line 1\nLine 2\nLine 3")

        assert "<br>" in escaped
        assert escaped.count("<br>") == 2

    def test_add_message_escapes_content(self, qapp):
        """Test adding message with HTML content escapes it."""
        widget = ChatPanelWidget()

        widget.add_user_message(
            content="<b>Bold</b>",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
        )

        html = widget._text_display.toHtml()
        assert "&lt;b&gt;Bold&lt;/b&gt;" in html


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestMessageHistory:
    """Test message history management."""

    def test_clear_messages(self, qapp):
        """Test clearing all messages."""
        widget = ChatPanelWidget()
        widget.add_user_message("Test1", "model", "syntax")
        widget.add_ai_message("Response1", "model", "syntax")

        widget.clear_messages()

        assert len(widget._messages) == 0
        assert widget.get_message_count() == 0
        # Empty state should be shown
        html = widget._text_display.toHtml()
        assert "AI Chat Ready" in html

    def test_load_messages(self, qapp):
        """Test loading a list of messages."""
        widget = ChatPanelWidget()

        messages = [
            ChatMessage(
                role="user",
                content="Q1",
                timestamp=time.time(),
                model="model1",
                context_mode="syntax",
            ),
            ChatMessage(
                role="assistant",
                content="A1",
                timestamp=time.time(),
                model="model1",
                context_mode="syntax",
            ),
        ]

        widget.load_messages(messages)

        assert len(widget._messages) == 2
        assert widget._messages[0].content == "Q1"
        assert widget._messages[1].content == "A1"

    def test_load_messages_with_empty_list(self, qapp):
        """Test loading empty message list shows empty state."""
        widget = ChatPanelWidget()

        widget.load_messages([])

        assert len(widget._messages) == 0
        html = widget._text_display.toHtml()
        assert "AI Chat Ready" in html

    def test_get_messages(self, qapp):
        """Test getting all messages."""
        widget = ChatPanelWidget()
        widget.add_user_message("Q1", "model", "syntax")
        widget.add_ai_message("A1", "model", "syntax")

        messages = widget.get_messages()

        assert len(messages) == 2
        assert messages[0].content == "Q1"
        assert messages[1].content == "A1"

    def test_get_messages_returns_copy(self, qapp):
        """Test get_messages returns a copy, not reference."""
        widget = ChatPanelWidget()
        widget.add_user_message("Q1", "model", "syntax")

        messages = widget.get_messages()
        messages.clear()

        # Original should be unchanged
        assert len(widget._messages) == 1

    def test_get_message_history(self, qapp):
        """Test get_message_history returns dictionaries."""
        widget = ChatPanelWidget()
        widget.add_user_message("Q1", "model", "syntax")
        widget.add_ai_message("A1", "model", "syntax")

        history = widget.get_message_history()

        assert len(history) == 2
        assert isinstance(history[0], dict)
        assert isinstance(history[1], dict)
        assert history[0]["content"] == "Q1"
        assert history[1]["content"] == "A1"
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_get_message_count(self, qapp):
        """Test getting message count."""
        widget = ChatPanelWidget()

        assert widget.get_message_count() == 0

        widget.add_user_message("Q1", "model", "syntax")
        assert widget.get_message_count() == 1

        widget.add_ai_message("A1", "model", "syntax")
        assert widget.get_message_count() == 2


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestAutoScrolling:
    """Test auto-scrolling functionality."""

    def test_set_auto_scroll_true(self, qapp):
        """Test enabling auto-scroll."""
        widget = ChatPanelWidget()

        widget.set_auto_scroll(True)

        assert widget._auto_scroll is True

    def test_set_auto_scroll_false(self, qapp):
        """Test disabling auto-scroll."""
        widget = ChatPanelWidget()

        widget.set_auto_scroll(False)

        assert widget._auto_scroll is False


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestMessageAppending:
    """Test appending to last message (streaming support)."""

    def test_append_to_last_message(self, qapp):
        """Test appending text to last AI message."""
        widget = ChatPanelWidget()
        widget.add_ai_message("Initial", "model", "syntax")

        widget.append_to_last_message(" appended")

        assert widget._messages[-1].content == "Initial appended"

    def test_append_to_last_message_with_no_messages(self, qapp):
        """Test appending with no messages does nothing."""
        widget = ChatPanelWidget()

        # Should not crash
        widget.append_to_last_message("text")

        assert len(widget._messages) == 0

    def test_append_to_last_message_with_user_message_last(self, qapp):
        """Test appending when last message is user message does nothing."""
        widget = ChatPanelWidget()
        widget.add_user_message("Question", "model", "syntax")

        widget.append_to_last_message(" appended")

        # Should not append to user message
        assert widget._messages[0].content == "Question"


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestRefreshDisplay:
    """Test display refresh."""

    def test_refresh_display_with_messages(self, qapp):
        """Test refreshing display with existing messages."""
        widget = ChatPanelWidget()
        widget.add_user_message("Q1", "model", "syntax")
        widget.add_ai_message("A1", "model", "syntax")

        # Change theme
        widget._dark_mode = True

        # Refresh should re-render with new theme
        widget.refresh_display()

        html = widget._text_display.toHtml()
        assert "Q1" in html
        assert "A1" in html

    def test_refresh_display_with_no_messages(self, qapp):
        """Test refreshing display with no messages shows empty state."""
        widget = ChatPanelWidget()

        widget.refresh_display()

        html = widget._text_display.toHtml()
        assert "AI Chat Ready" in html


@pytest.mark.fr_039
@pytest.mark.fr_042
@pytest.mark.fr_044
@pytest.mark.unit
class TestExportToText:
    """Test exporting chat history to text."""

    def test_export_to_text_with_messages(self, qapp):
        """Test exporting chat history to plain text."""
        widget = ChatPanelWidget()
        widget.add_user_message("Question 1", "qwen2.5-coder:7b", "syntax")
        widget.add_ai_message("Answer 1", "qwen2.5-coder:7b", "syntax")

        text = widget.export_to_text()

        assert "Chat History Export" in text
        assert "Question 1" in text
        assert "Answer 1" in text
        assert "You" in text
        assert "AI (qwen2.5-coder:7b)" in text

    def test_export_to_text_with_no_messages(self, qapp):
        """Test exporting empty chat returns no messages message."""
        widget = ChatPanelWidget()

        text = widget.export_to_text()

        assert "no messages" in text.lower()

    def test_export_to_text_includes_timestamps(self, qapp):
        """Test exported text includes formatted timestamps."""
        widget = ChatPanelWidget()
        timestamp = 1234567890.0  # 2009-02-13 23:31:30 UTC

        widget.add_user_message("Test", "model", "syntax", timestamp=timestamp)

        text = widget.export_to_text()

        # Should contain full timestamp in YYYY-MM-DD HH:MM:SS format
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        assert time_str in text

    def test_export_to_text_includes_context_modes(self, qapp):
        """Test exported text includes context modes."""
        widget = ChatPanelWidget()
        widget.add_user_message("Q1", "model", "document")
        widget.add_user_message("Q2", "model", "syntax")

        text = widget.export_to_text()

        assert "(document)" in text
        assert "(syntax)" in text
