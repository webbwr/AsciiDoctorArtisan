"""
Unit tests for Chat Context Modes (v1.7.0).

Tests the 4 context modes: Document, Syntax, General, Editing.
Verifies system prompt generation and document content handling.
"""

import pytest
from PySide6.QtCore import Qt

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
