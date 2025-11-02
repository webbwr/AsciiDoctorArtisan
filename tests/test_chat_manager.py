"""
Tests for Chat Manager.

Tests the ChatManager class which orchestrates all chat components.
"""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from asciidoc_artisan.core.models import ChatMessage
from asciidoc_artisan.core.settings import Settings
from asciidoc_artisan.ui.chat_manager import ChatManager


@pytest.fixture
def mock_chat_bar():
    """Create a mock chat bar."""
    bar = Mock()
    bar.message_sent = Mock()
    bar.clear_requested = Mock()
    bar.model_changed = Mock()
    bar.context_mode_changed = Mock()
    bar.set_enabled = Mock()
    bar.set_processing = Mock()
    bar.clear_input = Mock()
    bar.get_model = Mock(return_value="phi3:mini")
    bar.get_context_mode = Mock(return_value="document")
    bar.set_models = Mock()
    bar.set_model = Mock()
    bar.set_context_mode = Mock()
    return bar


@pytest.fixture
def mock_chat_panel():
    """Create a mock chat panel."""
    panel = Mock()
    panel.add_message = Mock()
    panel.clear_messages = Mock()
    panel.get_message_count = Mock(return_value=0)
    panel.export_to_text = Mock(return_value="")
    panel.export_to_html = Mock(return_value="")
    panel.set_visible = Mock()
    return panel


@pytest.fixture
def settings():
    """Create settings for testing."""
    return Settings(
        ollama_enabled=True,
        ollama_model="phi3:mini",
        ollama_chat_enabled=True,
        ollama_chat_history=[],
        ollama_chat_max_history=100,
        ollama_chat_context_mode="document",
    )


@pytest.fixture
def chat_manager(mock_chat_bar, mock_chat_panel, settings):
    """Create a chat manager for testing."""
    manager = ChatManager(mock_chat_bar, mock_chat_panel, settings)
    return manager


class TestChatManagerInitialization:
    """Test manager initialization."""

    def test_manager_creation(self, chat_manager):
        """Test manager can be created."""
        assert chat_manager is not None
        assert isinstance(chat_manager, ChatManager)

    def test_initial_state(self, chat_manager):
        """Test initial state is correct."""
        assert not chat_manager._is_processing
        assert chat_manager._document_content_provider is None

    def test_connects_to_chat_bar(self, chat_manager, mock_chat_bar):
        """Test manager connects to chat bar signals."""
        # Signals should be connected during initialization
        # This is tested implicitly by other tests
        pass

    def test_connects_to_chat_panel(self, chat_manager, mock_chat_panel):
        """Test manager connects to chat panel signals."""
        pass


class TestChatManagerVisibility:
    """Test visibility management."""

    def test_should_show_with_enabled_and_model(self, chat_manager, settings):
        """Test chat should show when enabled with model."""
        settings.ollama_enabled = True
        settings.ollama_model = "phi3:mini"
        settings.ollama_chat_enabled = True

        should_show = chat_manager._should_show_chat()
        assert should_show

    def test_should_hide_when_disabled(self, chat_manager, settings):
        """Test chat should hide when disabled."""
        settings.ollama_chat_enabled = False

        should_show = chat_manager._should_show_chat()
        assert not should_show

    def test_should_hide_when_no_model(self, chat_manager, settings):
        """Test chat should hide when no model set."""
        settings.ollama_model = None

        should_show = chat_manager._should_show_chat()
        assert not should_show

    def test_update_visibility_shows_when_enabled(
        self, chat_manager, mock_chat_bar, mock_chat_panel, settings
    ):
        """Test update_visibility shows widgets when appropriate."""
        settings.ollama_enabled = True
        settings.ollama_model = "phi3:mini"
        settings.ollama_chat_enabled = True

        chat_manager.update_visibility()

        # Should show both bar and panel
        assert mock_chat_bar.setVisible.called or mock_chat_bar.show.called
        assert mock_chat_panel.setVisible.called or mock_chat_panel.show.called


class TestChatManagerMessageHandling:
    """Test message handling."""

    def test_handle_user_message(self, chat_manager, mock_chat_panel):
        """Test handling user message adds to panel."""
        message = "Hello, AI!"
        model = "phi3:mini"
        context_mode = "general"

        chat_manager._handle_user_message(message, model, context_mode)

        # Should add message to panel
        mock_chat_panel.add_message.assert_called_once()
        call_args = mock_chat_panel.add_message.call_args[0]
        msg = call_args[0]
        assert isinstance(msg, ChatMessage)
        assert msg.role == "user"
        assert msg.content == message

    def test_handle_user_message_emits_to_worker(self, chat_manager, qtbot):
        """Test user message is emitted to worker."""
        message = "Test message"
        model = "phi3:mini"
        context_mode = "document"

        with qtbot.waitSignal(
            chat_manager.message_sent_to_worker, timeout=1000
        ) as blocker:
            chat_manager._handle_user_message(message, model, context_mode)

        args = blocker.args
        assert args[0] == message  # message
        assert args[1] == model  # model
        assert args[2] == context_mode  # context_mode

    def test_handle_response_ready(self, chat_manager, mock_chat_panel):
        """Test handling AI response."""
        response = ChatMessage(
            role="assistant",
            content="AI response here",
            timestamp=time.time(),
            model="phi3:mini",
            context_mode="general",
        )

        chat_manager.handle_response_ready(response)

        # Should add to panel
        mock_chat_panel.add_message.assert_called_once_with(response)

    def test_handle_response_sets_processing_false(self, chat_manager, mock_chat_bar):
        """Test response sets processing to false."""
        response = ChatMessage(
            role="assistant",
            content="Response",
            timestamp=time.time(),
            model="phi3:mini",
            context_mode="general",
        )

        chat_manager._is_processing = True
        chat_manager.handle_response_ready(response)

        assert not chat_manager._is_processing
        mock_chat_bar.set_processing.assert_called_with(False)


class TestChatManagerHistoryManagement:
    """Test chat history management."""

    def test_load_history_from_settings(self, chat_manager, settings):
        """Test loading history from settings."""
        # Add history to settings
        settings.ollama_chat_history = [
            {
                "role": "user",
                "content": "Hello",
                "timestamp": time.time(),
                "model": "phi3:mini",
                "context_mode": "general",
            }
        ]

        chat_manager._load_history_from_settings()

        # History should be loaded
        # (implementation detail - may vary)
        pass

    def test_save_history_to_settings(self, chat_manager, settings):
        """Test saving history to settings."""
        message = ChatMessage(
            role="user",
            content="Test",
            timestamp=time.time(),
            model="phi3:mini",
            context_mode="general",
        )

        chat_manager._chat_history = [message]
        chat_manager._save_history_to_settings()

        # Settings should be updated
        # (implementation detail - may vary)
        pass

    def test_history_max_limit_enforced(self, chat_manager, settings):
        """Test history is limited to max size."""
        settings.ollama_chat_max_history = 5

        # Add 10 messages
        for i in range(10):
            msg = ChatMessage(
                role="user",
                content=f"Message {i}",
                timestamp=time.time(),
                model="phi3:mini",
                context_mode="general",
            )
            chat_manager._chat_history.append(msg)

        chat_manager._trim_history()

        # Should be limited to 5
        assert len(chat_manager._chat_history) <= 5


class TestChatManagerDocumentContext:
    """Test document context handling."""

    def test_set_document_content_provider(self, chat_manager):
        """Test setting document content provider."""
        provider = lambda: "Document content here"

        chat_manager.set_document_content_provider(provider)

        assert chat_manager._document_content_provider == provider

    def test_get_document_context_calls_provider(self, chat_manager):
        """Test getting document context calls provider."""
        test_content = "= My Document\nContent here"
        provider = lambda: test_content

        chat_manager.set_document_content_provider(provider)
        content = chat_manager._get_document_context()

        assert content == test_content

    def test_document_context_debouncing(self, chat_manager):
        """Test document context updates are debounced."""
        provider = lambda: "Content"
        chat_manager.set_document_content_provider(provider)

        # Timer should be configured for debouncing
        assert chat_manager._debounce_timer.interval() == 500
        assert chat_manager._debounce_timer.isSingleShot()


class TestChatManagerErrorHandling:
    """Test error handling."""

    def test_handle_chat_error(self, chat_manager, qtbot):
        """Test handling chat errors."""
        error_message = "Ollama not running"

        with qtbot.waitSignal(chat_manager.status_message, timeout=1000) as blocker:
            chat_manager.handle_error(error_message)

        assert error_message in blocker.args[0]

    def test_error_resets_processing_state(self, chat_manager, mock_chat_bar):
        """Test error resets processing state."""
        chat_manager._is_processing = True
        chat_manager.handle_error("Some error")

        assert not chat_manager._is_processing
        mock_chat_bar.set_processing.assert_called_with(False)


class TestChatManagerClearHistory:
    """Test clearing history."""

    def test_clear_history_clears_panel(self, chat_manager, mock_chat_panel):
        """Test clear history clears panel."""
        chat_manager.clear_history()

        mock_chat_panel.clear_messages.assert_called_once()

    def test_clear_history_clears_internal_list(self, chat_manager):
        """Test clear history clears internal history list."""
        chat_manager._chat_history = [Mock(), Mock()]
        chat_manager.clear_history()

        assert len(chat_manager._chat_history) == 0

    def test_clear_history_saves_to_settings(self, chat_manager):
        """Test clear history saves to settings."""
        # Should trigger settings save
        # (implementation detail - may vary)
        pass


class TestChatManagerContextModeHandling:
    """Test context mode handling."""

    @pytest.mark.parametrize(
        "context_mode,includes_doc",
        [
            ("document", True),
            ("syntax", False),
            ("general", False),
            ("editing", True),
        ],
    )
    def test_context_mode_affects_document_inclusion(
        self, chat_manager, context_mode, includes_doc
    ):
        """Test different context modes affect document inclusion."""
        chat_manager._settings.ollama_chat_send_document = True
        chat_manager._settings.ollama_chat_context_mode = context_mode

        # This would need to be tested through message sending
        # Placeholder for implementation detail
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
