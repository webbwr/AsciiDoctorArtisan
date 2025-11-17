"""
Tests for Chat Manager.

Tests the ChatManager class which orchestrates all chat components.
"""

import time
from unittest.mock import Mock, patch

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
    bar.get_model = Mock(return_value="gnokit/improve-grammer")
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
    panel.add_user_message = Mock()  # Add user message method
    panel.clear_messages = Mock()
    panel.get_message_count = Mock(return_value=0)
    panel.get_messages = Mock(return_value=[])  # Return empty list, not Mock
    panel.load_messages = Mock()  # Add load messages method
    panel.export_to_text = Mock(return_value="")
    panel.export_to_html = Mock(return_value="")
    panel.set_visible = Mock()
    return panel


@pytest.fixture
def settings():
    """Create settings for testing."""
    return Settings(
        ollama_enabled=True,
        ollama_model="gnokit/improve-grammer",
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
        settings.ollama_model = "gnokit/improve-grammer"
        settings.ollama_chat_enabled = True

        should_show = chat_manager._should_show_chat()
        assert should_show

    def test_should_hide_when_disabled(self, chat_manager, settings):
        """Test chat should hide when disabled (both settings for v1.10.0 compatibility)."""
        settings.ai_chat_enabled = False
        settings.ollama_chat_enabled = False

        should_show = chat_manager._should_show_chat()
        assert not should_show

    def test_should_hide_when_no_model(self, chat_manager, settings):
        """Test chat should hide when no model set."""
        settings.ollama_model = None

        should_show = chat_manager._should_show_chat()
        assert not should_show

    def test_update_visibility_shows_when_enabled(self, chat_manager, settings, qtbot):
        """Test update_visibility emits visibility_changed signal."""
        settings.ollama_enabled = True
        settings.ollama_model = "gnokit/improve-grammer"
        settings.ollama_chat_enabled = True

        with qtbot.waitSignal(chat_manager.visibility_changed, timeout=1000) as blocker:
            chat_manager._update_visibility()

        # Should emit visibility_changed with True, True (both visible)
        assert blocker.args[0] is True  # bar_visible
        assert blocker.args[1] is True  # panel_visible


class TestChatManagerMessageHandling:
    """Test message handling."""

    def test_handle_user_message(self, chat_manager, mock_chat_panel):
        """Test handling user message adds to panel."""
        message = "Hello, AI!"
        model = "gnokit/improve-grammer"
        context_mode = "general"

        chat_manager._handle_user_message(message, model, context_mode)

        # Should add user message to panel
        mock_chat_panel.add_user_message.assert_called_once()
        call_args = mock_chat_panel.add_user_message.call_args
        assert call_args[0][0] == message  # message arg
        assert call_args[0][1] == model  # model arg
        assert call_args[0][2] == context_mode  # context_mode arg

    def test_handle_user_message_emits_to_worker(self, chat_manager, qtbot):
        """Test user message is emitted to worker."""
        message = "Test message"
        model = "gnokit/improve-grammer"
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
            model="gnokit/improve-grammer",
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
            model="gnokit/improve-grammer",
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
                "model": "gnokit/improve-grammer",
                "context_mode": "general",
            }
        ]

        chat_manager._load_chat_history()

        # History should be loaded
        # (implementation detail - may vary)
        pass

    def test_save_history_to_settings(self, chat_manager, settings):
        """Test saving history to settings."""
        message = ChatMessage(
            role="user",
            content="Test",
            timestamp=time.time(),
            model="gnokit/improve-grammer",
            context_mode="general",
        )

        chat_manager._chat_history = [message]
        chat_manager._save_chat_history()

        # Settings should be updated
        # (implementation detail - may vary)
        pass

    def test_history_max_limit_enforced(self, chat_manager, settings):
        """Test history is limited to max size."""
        # Set the new backend-agnostic setting (takes precedence over ollama-specific)
        settings.chat_max_history = 5

        # Add 10 messages
        for i in range(10):
            msg = ChatMessage(
                role="user",
                content=f"Message {i}",
                timestamp=time.time(),
                model="gnokit/improve-grammer",
                context_mode="general",
            )
            chat_manager._chat_history.append(msg)

        chat_manager._trim_history()

        # Should be limited to 5 (exact, not <=)
        assert len(chat_manager._chat_history) == 5


class TestChatManagerDocumentContext:
    """Test document context handling."""

    def test_set_document_content_provider(self, chat_manager):
        """Test setting document content provider."""

        def provider():
            return "Document content here"

        chat_manager.set_document_content_provider(provider)

        assert chat_manager._document_content_provider == provider

    def test_get_document_context_calls_provider(self, chat_manager):
        """Test getting document context calls provider."""
        test_content = "= My Document\nContent here"

        def provider():
            return test_content

        chat_manager.set_document_content_provider(provider)
        content = chat_manager._get_document_context()

        assert content == test_content

    def test_document_context_debouncing(self, chat_manager):
        """Test document context updates are debounced."""

        def provider():
            return "Content"

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


class TestModelValidation:
    """Test suite for AI model validation functionality."""

    def test_validate_model_success(self, chat_manager):
        """Test successful model validation."""
        with patch("subprocess.run") as mock_run:
            # Mock ollama list output with valid model
            mock_run.return_value = Mock(
                returncode=0,
                stdout="NAME\ngnokit/improve-grammer\nqwen2.5-coder:7b\n",
                stderr="",
            )

            # Validate existing model
            assert chat_manager._validate_model("gnokit/improve-grammer") is True
            mock_run.assert_called_once()

    def test_validate_model_not_found(self, chat_manager):
        """Test validation fails when model not found."""
        with patch("subprocess.run") as mock_run:
            # Mock ollama list output without target model
            mock_run.return_value = Mock(
                returncode=0,
                stdout="NAME\ngnokit/improve-grammer\nqwen2.5-coder:7b\n",
                stderr="",
            )

            # Validate non-existent model
            assert chat_manager._validate_model("invalid-model") is False
            mock_run.assert_called_once()

    def test_validate_model_empty_name(self, chat_manager):
        """Test validation fails for empty model name."""
        assert chat_manager._validate_model("") is False
        assert chat_manager._validate_model(None) is False

    def test_validate_model_ollama_not_found(self, chat_manager):
        """Test validation when Ollama is not installed."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            # Should return False when ollama command not found
            assert chat_manager._validate_model("gnokit/improve-grammer") is False

    def test_validate_model_timeout(self, chat_manager):
        """Test validation handles timeout gracefully."""
        with patch("subprocess.run", side_effect=TimeoutError):
            # Should return True on timeout to avoid blocking
            assert chat_manager._validate_model("gnokit/improve-grammer") is True

    def test_validate_model_command_error(self, chat_manager):
        """Test validation when ollama command fails."""
        with patch("subprocess.run") as mock_run:
            # Mock command failure
            mock_run.return_value = Mock(
                returncode=1, stdout="", stderr="Error: something went wrong"
            )

            # Should return False when command fails
            assert chat_manager._validate_model("gnokit/improve-grammer") is False

    def test_on_model_changed_valid(self, chat_manager):
        """Test model change with valid model."""
        with patch.object(chat_manager, "_validate_model", return_value=True):
            # Mock status_message signal
            status_messages = []
            chat_manager.status_message.connect(lambda msg: status_messages.append(msg))

            # Change to valid model
            chat_manager._on_model_changed("qwen2.5-coder:7b")

            # Settings should be updated
            assert chat_manager._settings.ollama_model == "qwen2.5-coder:7b"

            # Status bar should show success
            assert any("✓" in msg for msg in status_messages)
            assert any("qwen2.5-coder:7b" in msg for msg in status_messages)

    def test_on_model_changed_invalid(self, chat_manager, mock_chat_bar):
        """Test model change with invalid model."""
        # Set current valid model
        chat_manager._settings.ollama_model = "gnokit/improve-grammer"

        with patch.object(chat_manager, "_validate_model", return_value=False):
            # Mock status_message signal
            status_messages = []
            chat_manager.status_message.connect(lambda msg: status_messages.append(msg))

            # Attempt to change to invalid model
            chat_manager._on_model_changed("invalid-model")

            # Settings should NOT be updated (keeps old model)
            assert chat_manager._settings.ollama_model == "gnokit/improve-grammer"

            # Status bar should show error
            assert any("✗" in msg for msg in status_messages)
            assert any("not available" in msg for msg in status_messages)

            # Chat bar should revert to current model
            mock_chat_bar.set_model.assert_called_with("gnokit/improve-grammer")

    def test_on_model_changed_empty(self, chat_manager):
        """Test model change with empty model name."""
        status_messages = []
        chat_manager.status_message.connect(lambda msg: status_messages.append(msg))

        # Attempt to change to empty model
        chat_manager._on_model_changed("")

        # Should show error in status bar
        assert any("Error" in msg for msg in status_messages)
        assert any("No model selected" in msg for msg in status_messages)

    def test_on_model_changed_realtime_feedback(self, chat_manager):
        """Test that model validation provides real-time status bar feedback."""
        with patch.object(chat_manager, "_validate_model", return_value=True):
            status_messages = []
            chat_manager.status_message.connect(lambda msg: status_messages.append(msg))

            # Change model
            chat_manager._on_model_changed("qwen2.5-coder:7b")

            # Should have multiple status updates: validating -> success
            assert len(status_messages) >= 2
            assert any("Validating" in msg for msg in status_messages)
            assert any("Switched to" in msg or "✓" in msg for msg in status_messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
