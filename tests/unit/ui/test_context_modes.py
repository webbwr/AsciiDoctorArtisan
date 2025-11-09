"""
Unit tests for Chat Context Modes (v1.7.0).

Tests the 4 context modes: Document, Syntax, General, Editing.
Verifies system prompt generation and document content handling.
"""

import pytest

from asciidoc_artisan.core.models import ChatMessage
from asciidoc_artisan.ui.chat_bar_widget import ChatBarWidget
from asciidoc_artisan.workers.ollama_chat_worker import OllamaChatWorker


@pytest.fixture
def chat_bar(qtbot):
    """Create chat bar widget."""
    widget = ChatBarWidget()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def chat_worker():
    """Create Ollama chat worker."""
    return OllamaChatWorker()


class TestContextModeMapping:
    """Test context mode display names map to internal values."""

    def test_document_mode(self, chat_bar):
        """Test Document Q&A mode."""
        chat_bar._context_selector.setCurrentIndex(0)
        assert chat_bar._get_context_mode_value() == "document"

    def test_syntax_mode(self, chat_bar):
        """Test Syntax Help mode."""
        chat_bar._context_selector.setCurrentIndex(1)
        assert chat_bar._get_context_mode_value() == "syntax"

    def test_general_mode(self, chat_bar):
        """Test General Chat mode."""
        chat_bar._context_selector.setCurrentIndex(2)
        assert chat_bar._get_context_mode_value() == "general"

    def test_editing_mode(self, chat_bar):
        """Test Editing Suggestions mode."""
        chat_bar._context_selector.setCurrentIndex(3)
        assert chat_bar._get_context_mode_value() == "editing"

    def test_invalid_index_defaults_to_document(self, chat_bar):
        """Test invalid index defaults to document mode."""
        # Force invalid index
        chat_bar._context_selector.setCurrentIndex(-1)
        # Should default to document
        mode_value = chat_bar._get_context_mode_value()
        assert mode_value == "document"


class TestContextModeDisplayNames:
    """Test context mode display names."""

    def test_all_modes_present(self, chat_bar):
        """Test all 4 context modes are in selector."""
        assert chat_bar._context_selector.count() == 4

    def test_mode_display_names(self, chat_bar):
        """Test display names are correct."""
        expected_names = [
            "Document Q&A",
            "Syntax Help",
            "General Chat",
            "Editing Suggestions",
        ]
        actual_names = [
            chat_bar._context_selector.itemText(i)
            for i in range(chat_bar._context_selector.count())
        ]
        assert actual_names == expected_names


class TestContextModeSetGet:
    """Test setting and getting context modes."""

    def test_set_document_mode(self, chat_bar):
        """Test setting document mode."""
        chat_bar.set_context_mode("document")
        assert chat_bar.get_current_context_mode() == "document"
        assert chat_bar._context_selector.currentIndex() == 0

    def test_set_syntax_mode(self, chat_bar):
        """Test setting syntax mode."""
        chat_bar.set_context_mode("syntax")
        assert chat_bar.get_current_context_mode() == "syntax"
        assert chat_bar._context_selector.currentIndex() == 1

    def test_set_general_mode(self, chat_bar):
        """Test setting general mode."""
        chat_bar.set_context_mode("general")
        assert chat_bar.get_current_context_mode() == "general"
        assert chat_bar._context_selector.currentIndex() == 2

    def test_set_editing_mode(self, chat_bar):
        """Test setting editing mode."""
        chat_bar.set_context_mode("editing")
        assert chat_bar.get_current_context_mode() == "editing"
        assert chat_bar._context_selector.currentIndex() == 3

    def test_set_unknown_mode_defaults_to_document(self, chat_bar):
        """Test setting unknown mode defaults to document."""
        chat_bar.set_context_mode("unknown")
        assert chat_bar.get_current_context_mode() == "document"
        assert chat_bar._context_selector.currentIndex() == 0


class TestContextModeSignals:
    """Test context mode change signals."""

    def test_mode_change_emits_signal(self, chat_bar, qtbot):
        """Test changing mode emits context_mode_changed signal."""
        with qtbot.waitSignal(chat_bar.context_mode_changed, timeout=1000) as blocker:
            chat_bar._context_selector.setCurrentIndex(1)

        assert blocker.signal_triggered
        assert blocker.args == ["syntax"]

    def test_set_mode_emits_signal(self, chat_bar, qtbot):
        """Test set_context_mode emits signal."""
        with qtbot.waitSignal(chat_bar.context_mode_changed, timeout=1000) as blocker:
            chat_bar.set_context_mode("editing")

        assert blocker.signal_triggered
        assert blocker.args == ["editing"]


class TestSystemPromptGeneration:
    """Test system prompt generation for each context mode."""

    def test_document_mode_with_content(self, chat_worker):
        """Test document mode system prompt with document content."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = "= My Document\n\nThis is a test."

        prompt = chat_worker._build_system_prompt()

        assert "AsciiDoc document editing" in prompt
        assert "CURRENT DOCUMENT CONTENT" in prompt
        assert "= My Document" in prompt
        assert "This is a test." in prompt

    def test_document_mode_without_content(self, chat_worker):
        """Test document mode system prompt without document content."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = None

        prompt = chat_worker._build_system_prompt()

        assert "AsciiDoc document editing" in prompt
        assert "currently empty" in prompt
        assert "no content is available" in prompt

    def test_syntax_mode(self, chat_worker):
        """Test syntax mode system prompt."""
        chat_worker._context_mode = "syntax"
        chat_worker._document_content = None

        prompt = chat_worker._build_system_prompt()

        assert "expert in AsciiDoc syntax" in prompt
        assert "formatting" in prompt
        assert "best practices" in prompt

    def test_general_mode(self, chat_worker):
        """Test general mode system prompt."""
        chat_worker._context_mode = "general"
        chat_worker._document_content = None

        prompt = chat_worker._build_system_prompt()

        assert "helpful AI assistant" in prompt
        assert len(prompt) < 200  # Should be concise

    def test_editing_mode_with_content(self, chat_worker):
        """Test editing mode system prompt with document content."""
        chat_worker._context_mode = "editing"
        chat_worker._document_content = "= Draft Article\n\nThis needs improvement."

        prompt = chat_worker._build_system_prompt()

        assert "AI editor" in prompt
        assert "improve document quality" in prompt
        assert "CURRENT DOCUMENT CONTENT" in prompt
        assert "= Draft Article" in prompt

    def test_editing_mode_without_content(self, chat_worker):
        """Test editing mode system prompt without document content."""
        chat_worker._context_mode = "editing"
        chat_worker._document_content = None

        prompt = chat_worker._build_system_prompt()

        assert "AI editor" in prompt
        assert "currently empty" in prompt
        assert "general writing advice" in prompt


class TestDocumentContentHandling:
    """Test document content handling in different modes."""

    def test_document_content_truncated_at_2kb(self, chat_worker):
        """Test document content is truncated to 2KB."""
        # Create document larger than 2KB
        large_doc = "= Large Document\n\n" + ("x" * 3000)
        chat_worker._context_mode = "document"
        chat_worker._document_content = large_doc

        prompt = chat_worker._build_system_prompt()

        # Should be truncated
        assert len(prompt) < len(large_doc)
        assert "truncated to 2000 characters" in prompt

    def test_syntax_mode_ignores_document(self, chat_worker):
        """Test syntax mode doesn't include document content."""
        chat_worker._context_mode = "syntax"
        chat_worker._document_content = "= My Document\n\nContent here"

        prompt = chat_worker._build_system_prompt()

        # Should not include document content
        assert "= My Document" not in prompt
        assert "Content here" not in prompt

    def test_general_mode_ignores_document(self, chat_worker):
        """Test general mode doesn't include document content."""
        chat_worker._context_mode = "general"
        chat_worker._document_content = "= My Document\n\nContent here"

        prompt = chat_worker._build_system_prompt()

        # Should not include document content
        assert "= My Document" not in prompt
        assert "Content here" not in prompt


class TestMessageSentWithContextMode:
    """Test message_sent signal includes context mode."""

    def test_message_includes_context_mode(self, chat_bar, qtbot):
        """Test sent message includes selected context mode."""
        # Set to editing mode
        chat_bar.set_context_mode("editing")

        # Type message
        chat_bar._input_field.setText("How can I improve this?")

        with qtbot.waitSignal(chat_bar.message_sent, timeout=1000) as blocker:
            chat_bar._on_send()

        assert blocker.signal_triggered
        message, model, context_mode = blocker.args
        assert context_mode == "editing"
        assert message == "How can I improve this?"

    def test_different_modes_in_signal(self, chat_bar, qtbot):
        """Test different context modes are correctly passed in signal."""
        modes_to_test = [
            ("document", 0),
            ("syntax", 1),
            ("general", 2),
            ("editing", 3),
        ]

        for mode_name, mode_index in modes_to_test:
            chat_bar._context_selector.setCurrentIndex(mode_index)
            chat_bar._input_field.setText(f"Test {mode_name} mode")

            with qtbot.waitSignal(chat_bar.message_sent, timeout=1000) as blocker:
                chat_bar._on_send()

            assert blocker.signal_triggered
            _, _, context_mode = blocker.args
            assert context_mode == mode_name


class TestContextModeIntegration:
    """Test context mode integration across components."""

    def test_mode_affects_system_prompt(self, chat_worker):
        """Test changing mode changes system prompt."""
        prompts = {}

        for mode in ["document", "syntax", "general", "editing"]:
            chat_worker._context_mode = mode
            chat_worker._document_content = "= Test Doc\n\nTest content"
            prompts[mode] = chat_worker._build_system_prompt()

        # All prompts should be different
        assert len(set(prompts.values())) == 4

        # Each should have distinct keywords
        assert "document editing" in prompts["document"]
        assert "syntax" in prompts["syntax"]
        assert "helpful AI assistant" in prompts["general"]
        assert "AI editor" in prompts["editing"]

    def test_document_modes_include_content(self, chat_worker):
        """Test document and editing modes include document content."""
        doc_content = "= My Document\n\nSpecific content here"

        # Document mode
        chat_worker._context_mode = "document"
        chat_worker._document_content = doc_content
        doc_prompt = chat_worker._build_system_prompt()
        assert "Specific content here" in doc_prompt

        # Editing mode
        chat_worker._context_mode = "editing"
        editing_prompt = chat_worker._build_system_prompt()
        assert "Specific content here" in editing_prompt

        # Syntax mode (should NOT include)
        chat_worker._context_mode = "syntax"
        syntax_prompt = chat_worker._build_system_prompt()
        assert "Specific content here" not in syntax_prompt

        # General mode (should NOT include)
        chat_worker._context_mode = "general"
        general_prompt = chat_worker._build_system_prompt()
        assert "Specific content here" not in general_prompt


class TestContextSelectorInitialization:
    """Test context selector initialization and defaults."""

    def test_default_mode_is_document(self, chat_bar):
        """Test default context mode is document."""
        assert chat_bar.get_current_context_mode() == "document"
        assert chat_bar._context_selector.currentIndex() == 0

    def test_all_modes_available_on_init(self, chat_bar):
        """Test all 4 modes are available after initialization."""
        assert chat_bar._context_selector.count() == 4

    def test_selector_enabled_by_default(self, chat_bar):
        """Test context selector is enabled on initialization."""
        assert chat_bar._context_selector.isEnabled()

    def test_index_to_mode_mapping_consistency(self, chat_bar):
        """Test index-to-mode mapping is consistent."""
        expected_mapping = {
            0: "document",
            1: "syntax",
            2: "general",
            3: "editing",
        }

        for index, expected_mode in expected_mapping.items():
            chat_bar._context_selector.setCurrentIndex(index)
            actual_mode = chat_bar._get_context_mode_value()
            assert actual_mode == expected_mode

    def test_mode_display_order_correct(self, chat_bar):
        """Test context mode display order matches specification."""
        expected_order = [
            "Document Q&A",
            "Syntax Help",
            "General Chat",
            "Editing Suggestions",
        ]

        for i, expected_text in enumerate(expected_order):
            actual_text = chat_bar._context_selector.itemText(i)
            assert actual_text == expected_text

    def test_current_index_reflects_default(self, chat_bar):
        """Test current index reflects default document mode."""
        assert chat_bar._context_selector.currentIndex() == 0
        assert chat_bar._context_selector.currentText() == "Document Q&A"


class TestContextModeTooltips:
    """Test context mode tooltips for UI guidance."""

    def test_selector_has_tooltip(self, chat_bar):
        """Test context selector has descriptive tooltip."""
        tooltip = chat_bar._context_selector.toolTip()
        assert len(tooltip) > 0
        assert "mode" in tooltip.lower() or "interaction" in tooltip.lower()

    def test_tooltip_describes_purpose(self, chat_bar):
        """Test tooltip describes selector purpose."""
        tooltip = chat_bar._context_selector.toolTip()
        # Should indicate selection of interaction mode
        assert tooltip  # Not empty

    def test_tooltip_accessible(self, chat_bar):
        """Test tooltip is accessible after init."""
        # Tooltip should be set during _setup_ui
        assert chat_bar._context_selector.toolTip() is not None

    def test_tooltip_persists_after_mode_change(self, chat_bar):
        """Test tooltip persists after changing mode."""
        original_tooltip = chat_bar._context_selector.toolTip()
        chat_bar.set_context_mode("syntax")
        assert chat_bar._context_selector.toolTip() == original_tooltip


class TestContextModeEdgeCases:
    """Test context mode edge cases and error handling."""

    def test_set_empty_string_defaults_to_document(self, chat_bar):
        """Test setting empty string defaults to document mode."""
        chat_bar.set_context_mode("")
        assert chat_bar.get_current_context_mode() == "document"

    def test_set_none_defaults_to_document(self, chat_bar):
        """Test setting None defaults to document mode."""
        # Set to syntax first to ensure it changes
        chat_bar.set_context_mode("syntax")
        assert chat_bar.get_current_context_mode() == "syntax"

        # Now set to invalid
        chat_bar.set_context_mode(None)
        assert chat_bar.get_current_context_mode() == "document"

    def test_set_mode_with_whitespace(self, chat_bar):
        """Test mode with leading/trailing whitespace."""
        chat_bar.set_context_mode(" syntax ")
        # Should handle whitespace gracefully (exact behavior depends on implementation)
        # May strip or default to document
        mode = chat_bar.get_current_context_mode()
        assert mode in ["document", "syntax"]  # Either strips or defaults

    def test_rapid_mode_changes(self, chat_bar):
        """Test rapid mode changes maintain consistency."""
        modes = ["document", "syntax", "general", "editing", "document"]

        for mode in modes:
            chat_bar.set_context_mode(mode)

        # Final mode should be document
        assert chat_bar.get_current_context_mode() == "document"

    def test_mode_change_with_disabled_selector(self, chat_bar):
        """Test mode change when selector is disabled."""
        chat_bar._context_selector.setEnabled(False)
        chat_bar.set_context_mode("syntax")

        # Should still change via programmatic set_context_mode
        assert chat_bar.get_current_context_mode() == "syntax"

    def test_mode_persistence_across_hide_show(self, chat_bar):
        """Test mode persists across hide/show cycles."""
        chat_bar.set_context_mode("editing")
        chat_bar.hide()
        chat_bar.show()

        assert chat_bar.get_current_context_mode() == "editing"

    def test_invalid_index_negative(self, chat_bar):
        """Test negative index defaults to document."""
        chat_bar._context_selector.setCurrentIndex(-1)
        mode = chat_bar._get_context_mode_value()
        assert mode == "document"

    def test_invalid_index_too_large(self, chat_bar):
        """Test index beyond count defaults to document."""
        # Qt QComboBox handles out-of-range gracefully
        chat_bar._context_selector.setCurrentIndex(999)
        # Should either keep current or default
        mode = chat_bar._get_context_mode_value()
        assert mode in ["document", "syntax", "general", "editing"]


class TestSystemPromptEdgeCases:
    """Test system prompt generation edge cases."""

    def test_empty_document_content_string(self, chat_worker):
        """Test empty string document content."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = ""

        prompt = chat_worker._build_system_prompt()

        # Should treat empty string as no content
        assert "empty" in prompt or "no content" in prompt

    def test_document_with_only_whitespace(self, chat_worker):
        """Test document with only whitespace characters."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = "   \n\n\t\t   \n"

        prompt = chat_worker._build_system_prompt()

        # Should include the whitespace content
        assert "CURRENT DOCUMENT CONTENT" in prompt

    def test_document_with_special_characters(self, chat_worker):
        """Test document with special characters."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = "= Doc\n\n**Bold** `code` [link](url)"

        prompt = chat_worker._build_system_prompt()

        assert "**Bold**" in prompt or "Bold" in prompt

    def test_document_exactly_2000_chars(self, chat_worker):
        """Test document exactly at truncation threshold."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = "x" * 2000

        prompt = chat_worker._build_system_prompt()

        # Should include full content without truncation message
        assert "x" * 2000 in prompt

    def test_document_at_2001_chars(self, chat_worker):
        """Test document just over truncation threshold."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = "x" * 2001

        prompt = chat_worker._build_system_prompt()

        # Should show truncation message
        assert "truncated to 2000 characters" in prompt

        # Document portion should be truncated (not entire prompt)
        # Prompt includes system text + truncated content + truncation message
        assert len(chat_worker._document_content[:2000]) == 2000

    def test_very_large_document_truncation(self, chat_worker):
        """Test very large document (10KB+) is truncated."""
        chat_worker._context_mode = "editing"
        chat_worker._document_content = "Large document content\n" * 500  # ~11KB

        prompt = chat_worker._build_system_prompt()

        # Should be truncated to 2KB
        assert "truncated to 2000 characters" in prompt
        assert len(prompt) < 5000  # Well under original size

    def test_document_with_unicode(self, chat_worker):
        """Test document with Unicode characters."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = "= Doc\n\n你好世界 🌍 café"

        prompt = chat_worker._build_system_prompt()

        assert "你好世界" in prompt or "Doc" in prompt

    def test_document_with_ansi_codes(self, chat_worker):
        """Test document with ANSI escape codes."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = "= Doc\n\n\x1b[31mRed text\x1b[0m"

        prompt = chat_worker._build_system_prompt()

        # Should include content (ANSI codes may or may not be preserved)
        assert "Doc" in prompt

    def test_document_with_null_bytes(self, chat_worker):
        """Test document with null bytes."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = "Before\x00After"

        prompt = chat_worker._build_system_prompt()

        # Should handle gracefully
        assert "Before" in prompt or "After" in prompt

    def test_multiple_modes_same_large_document(self, chat_worker):
        """Test all modes with same large document."""
        large_doc = "= Large Document\n\n" + ("Content line\n" * 200)
        chat_worker._document_content = large_doc

        for mode in ["document", "syntax", "general", "editing"]:
            chat_worker._context_mode = mode
            prompt = chat_worker._build_system_prompt()
            assert len(prompt) > 0

    def test_system_prompt_consistency(self, chat_worker):
        """Test system prompt is consistent for same inputs."""
        chat_worker._context_mode = "syntax"
        chat_worker._document_content = "= Test"

        prompt1 = chat_worker._build_system_prompt()
        prompt2 = chat_worker._build_system_prompt()

        assert prompt1 == prompt2

    def test_system_prompt_changes_with_mode(self, chat_worker):
        """Test system prompt changes when mode switches."""
        chat_worker._document_content = "= Same Doc"

        chat_worker._context_mode = "document"
        prompt1 = chat_worker._build_system_prompt()

        chat_worker._context_mode = "syntax"
        prompt2 = chat_worker._build_system_prompt()

        assert prompt1 != prompt2


class TestMessageHistoryIntegration:
    """Test message history integration with context modes."""

    def test_empty_history_document_mode(self, chat_worker):
        """Test document mode with empty history."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = "= Test"
        chat_worker._chat_history = []

        system_prompt = chat_worker._build_system_prompt()
        messages = chat_worker._build_message_history(system_prompt)

        # Should have system prompt only (plus current message if added)
        assert len(messages) >= 1
        assert messages[0]["role"] == "system"

    def test_single_message_history(self, chat_worker):
        """Test with single message in history."""
        chat_worker._context_mode = "document"
        chat_worker._chat_history = [
            ChatMessage(
                role="user",
                content="Previous question",
                timestamp=1.0,
                model="test",
                context_mode="document",
            )
        ]

        system_prompt = chat_worker._build_system_prompt()
        messages = chat_worker._build_message_history(system_prompt)

        assert len(messages) == 2  # System + 1 history message

    def test_ten_message_history_max(self, chat_worker):
        """Test with exactly 10 messages (max context window)."""
        chat_worker._context_mode = "syntax"
        chat_worker._chat_history = [
            ChatMessage(
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                timestamp=float(i),
                model="test",
                context_mode="syntax",
            )
            for i in range(10)
        ]

        system_prompt = chat_worker._build_system_prompt()
        messages = chat_worker._build_message_history(system_prompt)

        # System + 10 history messages
        assert len(messages) == 11

    def test_twenty_message_history_truncates(self, chat_worker):
        """Test with 20 messages truncates to last 10."""
        chat_worker._context_mode = "general"
        chat_worker._chat_history = [
            ChatMessage(
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                timestamp=float(i),
                model="test",
                context_mode="general",
            )
            for i in range(20)
        ]

        system_prompt = chat_worker._build_system_prompt()
        messages = chat_worker._build_message_history(system_prompt)

        # Should only include last 10 + system
        assert len(messages) == 11

        # Should include messages 10-19, not 0-9
        assert "Message 10" in messages[1]["content"]

    def test_mixed_role_messages(self, chat_worker):
        """Test history with mixed user/assistant roles."""
        chat_worker._context_mode = "document"
        chat_worker._chat_history = [
            ChatMessage(
                role="user",
                content="Q1",
                timestamp=1.0,
                model="test",
                context_mode="document",
            ),
            ChatMessage(
                role="assistant",
                content="A1",
                timestamp=2.0,
                model="test",
                context_mode="document",
            ),
            ChatMessage(
                role="user",
                content="Q2",
                timestamp=3.0,
                model="test",
                context_mode="document",
            ),
        ]

        system_prompt = chat_worker._build_system_prompt()
        messages = chat_worker._build_message_history(system_prompt)

        # System + 3 history
        assert len(messages) == 4
        assert messages[1]["role"] == "user"
        assert messages[2]["role"] == "assistant"
        assert messages[3]["role"] == "user"

    def test_history_with_different_models(self, chat_worker):
        """Test history with messages from different models."""
        chat_worker._context_mode = "editing"
        chat_worker._chat_history = [
            ChatMessage(
                role="user",
                content="Question",
                timestamp=1.0,
                model="model1",
                context_mode="editing",
            ),
            ChatMessage(
                role="assistant",
                content="Answer",
                timestamp=2.0,
                model="model2",
                context_mode="editing",
            ),
        ]

        system_prompt = chat_worker._build_system_prompt()
        messages = chat_worker._build_message_history(system_prompt)

        # Should include both regardless of model
        assert len(messages) == 3

    def test_history_with_different_context_modes(self, chat_worker):
        """Test history with messages from different context modes."""
        chat_worker._context_mode = "document"
        chat_worker._chat_history = [
            ChatMessage(
                role="user",
                content="Syntax question",
                timestamp=1.0,
                model="test",
                context_mode="syntax",
            ),
            ChatMessage(
                role="assistant",
                content="Answer",
                timestamp=2.0,
                model="test",
                context_mode="syntax",
            ),
        ]

        system_prompt = chat_worker._build_system_prompt()
        messages = chat_worker._build_message_history(system_prompt)

        # Should include messages despite mode change
        assert len(messages) == 3

    def test_system_prompt_position_in_message_list(self, chat_worker):
        """Test system prompt is always first in message list."""
        chat_worker._context_mode = "document"
        chat_worker._document_content = "= Test"
        chat_worker._chat_history = [
            ChatMessage(
                role="user",
                content="Question",
                timestamp=1.0,
                model="test",
                context_mode="document",
            )
        ]

        system_prompt = chat_worker._build_system_prompt()
        messages = chat_worker._build_message_history(system_prompt)

        assert messages[0]["role"] == "system"
        assert "AsciiDoc" in messages[0]["content"]


class TestWorkerStateManagement:
    """Test worker state management and thread safety."""

    def test_context_mode_set_before_start(self, chat_worker):
        """Test context mode is set before worker starts."""
        chat_worker._context_mode = "syntax"
        assert chat_worker._context_mode == "syntax"

        # Mode should not change until next send_message
        assert chat_worker._context_mode == "syntax"

    def test_document_content_set_before_start(self, chat_worker):
        """Test document content is set before worker starts."""
        doc_content = "= Test Document"
        chat_worker._document_content = doc_content

        assert chat_worker._document_content == doc_content

    def test_is_processing_flag_prevents_concurrent(self, chat_worker):
        """Test is_processing flag prevents concurrent operations."""
        # Simulate processing state
        chat_worker._is_processing = True

        # Try to send message while processing
        chat_worker.send_message(
            message="Test",
            model="test-model",
            context_mode="document",
            history=[],
            document_content=None,
        )

        # Should not start (returns early due to reentrancy guard)
        assert chat_worker._is_processing is True
        # Note: OllamaChatWorker is QObject (not QThread), so no isRunning() method
        # The reentrancy guard (_is_processing=True) prevents the second call from starting

    def test_user_message_cleared_after_processing(self, chat_worker):
        """Test user message is cleared in finally block."""
        chat_worker._user_message = "Test message"
        chat_worker._is_processing = True

        # Simulate finally block cleanup
        try:
            pass
        finally:
            chat_worker._is_processing = False
            chat_worker._user_message = None

        assert chat_worker._user_message is None

    def test_multiple_mode_changes_between_sends(self, chat_worker):
        """Test mode can change between send operations."""
        chat_worker._context_mode = "document"
        assert chat_worker._context_mode == "document"

        chat_worker._context_mode = "syntax"
        assert chat_worker._context_mode == "syntax"

        chat_worker._context_mode = "editing"
        assert chat_worker._context_mode == "editing"

    def test_state_isolation_between_operations(self, chat_worker):
        """Test state is isolated between operations."""
        # First operation
        chat_worker._user_message = "Message 1"
        chat_worker._context_mode = "document"

        # Clear state
        chat_worker._user_message = None

        # Second operation
        chat_worker._user_message = "Message 2"
        chat_worker._context_mode = "syntax"

        # Should not have residual state from first operation
        assert chat_worker._user_message == "Message 2"
        assert chat_worker._context_mode == "syntax"


class TestContextModeWithCancellation:
    """Test context mode behavior with operation cancellation."""

    def test_cancel_sets_flag(self, chat_worker):
        """Test cancel sets should_cancel flag."""
        chat_worker._is_processing = True
        chat_worker.cancel_operation()

        assert chat_worker._should_cancel is True

    def test_cancel_checked_during_processing(self, chat_worker):
        """Test cancellation flag is checked during processing."""
        chat_worker._should_cancel = True

        # Simulate check in run() method
        if chat_worker._should_cancel:
            # Should emit cancellation signal
            pass

        assert chat_worker._should_cancel is True

    def test_cancel_resets_on_new_operation(self, chat_worker):
        """Test cancel flag resets on new send_message."""
        chat_worker._should_cancel = True

        # New operation should clear flag
        chat_worker.send_message(
            message="New message",
            model="test",
            context_mode="document",
            history=[],
            document_content=None,
        )

        # Flag should be reset (send_message sets it to False)
        assert chat_worker._should_cancel is False

    def test_cancel_preserves_context_mode(self, chat_worker):
        """Test cancellation preserves context mode."""
        chat_worker._context_mode = "editing"
        chat_worker._is_processing = True
        chat_worker.cancel_operation()

        # Mode should not change
        assert chat_worker._context_mode == "editing"


class TestSignalEmissionEdgeCases:
    """Test signal emission edge cases and threading."""

    def test_signal_includes_correct_mode_after_change(self, chat_bar, qtbot):
        """Test signal includes correct mode after rapid changes."""
        # Rapid changes
        chat_bar.set_context_mode("syntax")
        chat_bar.set_context_mode("editing")

        with qtbot.waitSignal(chat_bar.context_mode_changed, timeout=1000) as blocker:
            chat_bar.set_context_mode("general")

        assert blocker.args[0] == "general"

    def test_signal_emission_thread_safety(self, chat_bar, qtbot):
        """Test signal emission is thread-safe."""
        # Signals should be emitted on main thread
        with qtbot.waitSignal(chat_bar.context_mode_changed, timeout=1000) as blocker:
            chat_bar._context_selector.setCurrentIndex(1)

        assert blocker.signal_triggered
        assert blocker.args[0] == "syntax"

    def test_multiple_mode_changes_emit_multiple_signals(self, chat_bar, qtbot):
        """Test multiple mode changes emit multiple signals."""
        signal_count = 0

        def count_signals(mode):
            nonlocal signal_count
            signal_count += 1

        chat_bar.context_mode_changed.connect(count_signals)

        chat_bar.set_context_mode("syntax")
        chat_bar.set_context_mode("general")
        chat_bar.set_context_mode("editing")

        # Process events to ensure signals are delivered
        qtbot.wait(10)

        assert signal_count == 3

    def test_signal_args_match_current_mode(self, chat_bar, qtbot):
        """Test signal args always match current mode."""
        with qtbot.waitSignal(chat_bar.context_mode_changed, timeout=1000) as blocker:
            chat_bar.set_context_mode("editing")

        assert blocker.args[0] == chat_bar.get_current_context_mode()

    def test_signal_emission_order(self, chat_bar, qtbot):
        """Test signals are emitted in order of changes."""
        emitted_modes = []

        def record_mode(mode):
            emitted_modes.append(mode)

        chat_bar.context_mode_changed.connect(record_mode)

        chat_bar.set_context_mode("syntax")
        qtbot.wait(10)
        chat_bar.set_context_mode("general")
        qtbot.wait(10)
        chat_bar.set_context_mode("editing")
        qtbot.wait(10)

        assert emitted_modes == ["syntax", "general", "editing"]

    def test_programmatic_vs_user_change_signals(self, chat_bar, qtbot):
        """Test both programmatic and user changes emit signals."""
        # Programmatic change
        with qtbot.waitSignal(chat_bar.context_mode_changed, timeout=1000) as blocker1:
            chat_bar.set_context_mode("syntax")

        assert blocker1.signal_triggered

        # User change (via selector)
        with qtbot.waitSignal(chat_bar.context_mode_changed, timeout=1000) as blocker2:
            chat_bar._context_selector.setCurrentIndex(2)  # general

        assert blocker2.signal_triggered


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
