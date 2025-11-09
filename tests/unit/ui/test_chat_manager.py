"""
Tests for ui.chat_manager module.

Tests chat manager orchestration including:
- Initialization and signal connections
- Backend switching (Ollama ↔ Claude)
- Model loading (both backends)
- Message flow (user → worker → panel)
- Chat history persistence
- Visibility management
- Error handling and cancellation
"""

import subprocess
from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.core.models import ChatMessage
from asciidoc_artisan.core.settings import Settings
from asciidoc_artisan.ui.chat_manager import ChatManager


@pytest.fixture
def mock_chat_bar():
    """Create mock ChatBarWidget."""
    bar = Mock()
    bar.message_sent = Mock()
    bar.clear_requested = Mock()
    bar.cancel_requested = Mock()
    bar.model_changed = Mock()
    bar.context_mode_changed = Mock()
    bar.scan_models_requested = Mock()
    return bar


@pytest.fixture
def mock_chat_panel():
    """Create mock ChatPanelWidget."""
    panel = Mock()
    panel.get_messages = Mock(return_value=[])
    return panel


@pytest.fixture
def mock_settings():
    """Create mock Settings."""
    settings = Mock(spec=Settings)
    settings.ai_backend = "ollama"
    settings.ai_chat_enabled = True  # Backend-agnostic chat enable flag
    settings.ollama_enabled = True
    settings.ollama_model = "qwen2.5-coder:7b"
    settings.ollama_chat_enabled = True
    settings.ollama_chat_history = []
    settings.ollama_chat_max_history = 100
    settings.chat_history = []  # Backend-agnostic history
    settings.chat_max_history = 100  # Backend-agnostic max history
    settings.ollama_chat_context_mode = "syntax"
    settings.chat_context_mode = "syntax"
    settings.claude_model = None
    settings.claude_enabled = False
    return settings


class TestChatManagerInitialization:
    """Test ChatManager initialization."""

    def test_initialization(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test manager initializes with components."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        assert manager._chat_bar is mock_chat_bar
        assert manager._chat_panel is mock_chat_panel
        assert manager._settings is mock_settings
        assert manager._current_backend == "ollama"

    def test_initialization_connects_signals(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test initialization connects chat bar signals."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        mock_chat_bar.message_sent.connect.assert_called_once()
        mock_chat_bar.clear_requested.connect.assert_called_once()
        mock_chat_bar.cancel_requested.connect.assert_called_once()
        mock_chat_bar.model_changed.connect.assert_called_once()
        mock_chat_bar.context_mode_changed.connect.assert_called_once()
        mock_chat_bar.scan_models_requested.connect.assert_called_once()

    def test_initialization_creates_debounce_timer(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test initialization creates debounce timer."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        assert manager._debounce_timer is not None
        assert manager._debounce_timer.interval() == 500
        assert manager._debounce_timer.isSingleShot()

    def test_initialization_not_processing_initially(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test manager is not processing initially."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        assert manager._is_processing is False

    def test_initialization_empty_chat_history(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test manager starts with empty chat history cache."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        assert manager._chat_history == []


class TestBackendSwitching:
    """Test AI backend switching."""

    def test_switch_backend_to_claude(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test switching from Ollama to Claude."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models"):
            manager._switch_backend("claude")

        assert manager._current_backend == "claude"
        assert mock_settings.ai_backend == "claude"

    def test_switch_backend_sets_default_claude_model(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test switching to Claude sets default model if not configured."""
        mock_settings.claude_model = None
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models"):
            manager._switch_backend("claude")

        assert mock_settings.claude_model == "claude-sonnet-4-20250514"

    def test_switch_backend_reloads_models(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test backend switch reloads available models."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models") as mock_load:
            manager._switch_backend("claude")

        mock_load.assert_called_once()

    def test_switch_backend_updates_chat_bar_model(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test backend switch updates selected model in chat bar."""
        mock_settings.claude_model = "claude-haiku-3-20250307"
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models"):
            manager._switch_backend("claude")

        mock_chat_bar.set_model.assert_called_with("claude-haiku-3-20250307")

    def test_switch_backend_updates_scan_button_visibility(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test backend switch updates Scan Models button visibility."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models"):
            manager._switch_backend("claude")

        # Scan button visible for Claude
        mock_chat_bar.set_scan_models_visible.assert_called_with(True)

    def test_switch_backend_emits_settings_changed(
        self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot
    ):
        """Test backend switch emits settings changed signal."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models"):
            with qtbot.waitSignal(manager.settings_changed, timeout=1000):
                manager._switch_backend("claude")


class TestModelLoading:
    """Test model loading for both backends."""

    def test_load_available_models_ollama(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test load_available_models calls Ollama loader."""
        mock_settings.ai_backend = "ollama"
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        with patch.object(manager, "_load_ollama_models") as mock_load:
            manager._load_available_models()

        mock_load.assert_called_once()

    def test_load_available_models_claude(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test load_available_models calls Claude loader."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        with patch.object(manager, "_load_claude_models") as mock_load:
            manager._load_available_models()

        mock_load.assert_called_once()

    def test_load_ollama_models_success(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test loading Ollama models when ollama list succeeds."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stdout="NAME\nqwen2.5-coder:7b\ndeepseek-coder\n"
            )

            manager._load_ollama_models()

        # Should load detected models
        mock_chat_bar.set_models.assert_called_once()
        models = mock_chat_bar.set_models.call_args[0][0]
        assert "qwen2.5-coder:7b" in models
        assert "deepseek-coder" in models

    def test_load_ollama_models_not_found(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test loading Ollama models when ollama not found."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch("subprocess.run", side_effect=FileNotFoundError):
            manager._load_ollama_models()

        # Should fall back to default models
        mock_chat_bar.set_models.assert_called_once()
        models = mock_chat_bar.set_models.call_args[0][0]
        assert "gnokit/improve-grammer" in models

    def test_load_ollama_models_timeout(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test loading Ollama models handles timeout."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch(
            "subprocess.run", side_effect=subprocess.TimeoutExpired("ollama", 3)
        ):
            manager._load_ollama_models()

        # Should fall back to defaults
        mock_chat_bar.set_models.assert_called_once()

    def test_load_claude_models(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test loading Claude models."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # Mock ClaudeClient at the correct import location (inside the method)
        with patch(
            "asciidoc_artisan.claude.claude_client.ClaudeClient"
        ) as mock_client_class:
            mock_client_class.AVAILABLE_MODELS = [
                "claude-sonnet-4-20250514",
                "claude-haiku-3-20250307",
            ]

            manager._load_claude_models()

        # Should load Claude models
        mock_chat_bar.set_models.assert_called_once()
        models = mock_chat_bar.set_models.call_args[0][0]
        assert "claude-sonnet-4-20250514" in models


class TestMessageHandling:
    """Test message handling and flow."""

    def test_on_message_sent(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test handling message_sent signal."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # _on_message_sent directly handles the message (doesn't call _handle_user_message)
        # Just verify it doesn't crash
        manager._on_message_sent("Test message", "qwen2.5-coder:7b", "syntax")

        # Should have added message to panel
        mock_chat_panel.add_user_message.assert_called_once()

    def test_handle_user_message_adds_to_panel(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test user message is added to chat panel."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        manager._handle_user_message("Test question", "qwen2.5-coder:7b", "syntax")

        # Verify add_user_message was called with correct positional arguments
        mock_chat_panel.add_user_message.assert_called_once()
        call_args = mock_chat_panel.add_user_message.call_args[
            0
        ]  # positional args tuple
        assert call_args[0] == "Test question"  # message
        assert call_args[1] == "qwen2.5-coder:7b"  # model
        assert call_args[2] == "syntax"  # context_mode

    def test_handle_user_message_emits_to_worker(
        self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot
    ):
        """Test user message is sent to worker."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with qtbot.waitSignal(manager.message_sent_to_worker, timeout=1000):
            manager._handle_user_message("Test", "model", "syntax")

    def test_handle_response_ready(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test handling AI response."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        response = ChatMessage(
            role="assistant",
            content="AI response",
            timestamp=1234567890.0,
            model="qwen2.5-coder:7b",
            context_mode="syntax",
        )

        manager.handle_response_ready(response)

        # Should add to panel
        mock_chat_panel.add_message.assert_called_once_with(response)
        # Should stop processing
        assert manager._is_processing is False

    def test_handle_error(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test handling AI error."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with qtbot.waitSignal(manager.status_message, timeout=1000) as blocker:
            manager.handle_error("Connection failed")

        # Should emit status message
        assert "Connection failed" in blocker.args[0]

    def test_handle_operation_cancelled(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test handling operation cancellation."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._is_processing = True

        manager.handle_operation_cancelled()

        assert manager._is_processing is False
        mock_chat_bar.set_processing.assert_called_with(False)


class TestHistoryManagement:
    """Test chat history persistence."""

    def test_load_chat_history_from_settings(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test loading chat history from settings."""
        mock_settings.ollama_chat_history = [
            {
                "role": "user",
                "content": "Q1",
                "timestamp": 1234567890.0,
                "model": "qwen2.5-coder:7b",
                "context_mode": "syntax",
            }
        ]
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        manager._load_chat_history()

        # Should load messages into panel
        mock_chat_panel.load_messages.assert_called_once()

    def test_save_chat_history_to_settings(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test saving chat history to settings."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        messages = [
            ChatMessage(
                role="user",
                content="Q1",
                timestamp=1234567890.0,
                model="qwen2.5-coder:7b",
                context_mode="syntax",
            )
        ]
        mock_chat_panel.get_messages.return_value = messages

        manager._save_chat_history()

        # Should save to settings
        assert len(mock_settings.ollama_chat_history) == 1

    def test_save_chat_history_limits_to_max(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test chat history is limited to max size."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # Create 150 messages (max is 100)
        messages = [
            ChatMessage(
                role="user",
                content=f"Q{i}",
                timestamp=float(i),
                model="model",
                context_mode="syntax",
            )
            for i in range(150)
        ]
        mock_chat_panel.get_messages.return_value = messages

        manager._save_chat_history()

        # Should only save last 100
        assert len(mock_settings.ollama_chat_history) == 100


class TestVisibilityManagement:
    """Test chat visibility management."""

    def test_should_show_chat_when_enabled_and_model_set(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test chat should show when enabled with model."""
        mock_settings.ollama_enabled = True
        mock_settings.ollama_chat_enabled = True
        mock_settings.ollama_model = "qwen2.5-coder:7b"
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        result = manager._should_show_chat()

        assert result is True

    def test_should_show_chat_false_when_disabled(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test chat should not show when disabled."""
        mock_settings.ai_chat_enabled = False  # Backend-agnostic flag
        mock_settings.ollama_chat_enabled = False
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        result = manager._should_show_chat()

        assert result is False

    def test_should_show_chat_false_when_no_model(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test chat should not show when no model set."""
        mock_settings.ollama_model = None
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        result = manager._should_show_chat()

        assert result is False

    def test_update_visibility_shows_when_should_show(
        self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot
    ):
        """Test update_visibility shows chat when conditions met."""
        manager = ChatManager(
            mock_chat_bar, mock_chat_panel, mock_settings, parent=None
        )

        # Mock the parent after initialization
        mock_parent = Mock()
        mock_parent.chat_container = Mock()
        mock_parent.splitter = Mock()
        mock_parent.splitter.sizes.return_value = [100, 100, 0]  # Chat hidden
        mock_parent.width.return_value = 1000

        # Manually set the parent (after __init__)
        manager.setParent(None)  # Clear Qt parent
        manager._parent = mock_parent  # Use internal reference

        with patch.object(manager, "_should_show_chat", return_value=True):
            with patch.object(manager, "parent", return_value=mock_parent):
                with qtbot.waitSignal(manager.visibility_changed, timeout=1000):
                    manager._update_visibility()

        # Should set chat_container visible
        mock_parent.chat_container.setVisible.assert_called_with(True)

    def test_update_visibility_hides_when_should_not_show(
        self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot
    ):
        """Test update_visibility hides chat when conditions not met."""
        manager = ChatManager(
            mock_chat_bar, mock_chat_panel, mock_settings, parent=None
        )

        # Mock the parent after initialization
        mock_parent = Mock()
        mock_parent.chat_container = Mock()
        mock_parent.splitter = Mock()
        mock_parent.splitter.sizes.return_value = [100, 100, 100]  # Chat visible
        mock_parent.width.return_value = 1000

        # Manually set the parent (after __init__)
        manager.setParent(None)  # Clear Qt parent
        manager._parent = mock_parent  # Use internal reference

        with patch.object(manager, "_should_show_chat", return_value=False):
            with patch.object(manager, "parent", return_value=mock_parent):
                with qtbot.waitSignal(manager.visibility_changed, timeout=1000):
                    manager._update_visibility()

        # Should set chat_container hidden
        mock_parent.chat_container.setVisible.assert_called_with(False)


class TestSignalHandlers:
    """Test signal handler methods."""

    def test_on_clear_requested(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test clearing chat history."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        manager._on_clear_requested()

        mock_chat_panel.clear_messages.assert_called_once()

    def test_on_clear_requested_saves_history(
        self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot
    ):
        """Test clearing chat saves empty history."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # Call _on_clear_requested - it clears panel and emits signals
        with qtbot.waitSignal(manager.settings_changed, timeout=1000):
            manager._on_clear_requested()

        # Verify panel was cleared
        mock_chat_panel.clear_messages.assert_called_once()

    def test_on_cancel_requested(
        self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot
    ):
        """Test cancel request emits status message."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with qtbot.waitSignal(manager.status_message, timeout=1000) as blocker:
            manager._on_cancel_requested()

        # Should emit canceling message
        assert "cancel" in blocker.args[0].lower()

    def test_on_model_changed_ollama(
        self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot
    ):
        """Test model changed updates Ollama settings."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        # Mock successful validation
        with patch.object(manager, "_validate_model", return_value=True):
            with qtbot.waitSignal(manager.settings_changed, timeout=1000):
                manager._on_model_changed("new-model")

        assert mock_settings.ollama_model == "new-model"

    def test_on_model_changed_claude(
        self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot
    ):
        """Test model changed updates Claude settings."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        # Mock successful validation
        with patch.object(manager, "_validate_model", return_value=True):
            with qtbot.waitSignal(manager.settings_changed, timeout=1000):
                manager._on_model_changed("claude-haiku-3-20250307")

        assert mock_settings.claude_model == "claude-haiku-3-20250307"

    def test_on_context_mode_changed(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test context mode changed updates settings."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        manager._on_context_mode_changed("document")

        assert mock_settings.chat_context_mode == "document"


class TestDocumentContext:
    """Test document context provider."""

    def test_set_document_content_provider(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test setting document content provider."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        provider = Mock(return_value="Document text")
        manager.set_document_content_provider(provider)

        assert manager._document_content_provider is provider

    def test_get_document_context_returns_content(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test getting document context."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        provider = Mock(return_value="Document content")
        manager._document_content_provider = provider

        result = manager._get_document_context()

        assert result == "Document content"

    def test_get_document_context_returns_empty_when_no_provider(
        self, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test getting document context without provider returns empty."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        result = manager._get_document_context()

        assert result == ""


class TestSettingsUpdate:
    """Test settings update handling."""

    def test_update_settings(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test updating settings."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        new_settings = Mock(spec=Settings)
        new_settings.ai_backend = "claude"
        new_settings.claude_model = "claude-sonnet-4-20250514"

        with patch.object(manager, "_load_available_models"):
            with patch.object(manager, "_update_visibility"):
                manager.update_settings(new_settings)

        assert manager._settings is new_settings


class TestExportAndStats:
    """Test export and statistics methods."""

    def test_export_chat_history(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test exporting chat history to text."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        mock_chat_panel.export_to_text.return_value = "Chat history text"

        result = manager.export_chat_history()

        assert result == "Chat history text"
        mock_chat_panel.export_to_text.assert_called_once()

    def test_get_message_count(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test getting message count."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        mock_chat_panel.get_message_count.return_value = 10

        result = manager.get_message_count()

        assert result == 10
        mock_chat_panel.get_message_count.assert_called_once()
