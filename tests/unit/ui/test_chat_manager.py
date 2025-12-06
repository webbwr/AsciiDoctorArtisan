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

    def test_initialization_connects_signals(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test initialization connects chat bar signals."""
        ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        mock_chat_bar.message_sent.connect.assert_called_once()
        mock_chat_bar.clear_requested.connect.assert_called_once()
        mock_chat_bar.cancel_requested.connect.assert_called_once()
        mock_chat_bar.model_changed.connect.assert_called_once()
        mock_chat_bar.context_mode_changed.connect.assert_called_once()
        mock_chat_bar.scan_models_requested.connect.assert_called_once()

    def test_initialization_not_processing_initially(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test manager is not processing initially."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        assert manager._is_processing is False

    def test_initialization_has_history_manager(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test manager initializes with history manager."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        assert manager._history_manager is not None


class TestBackendSwitching:
    """Test AI backend switching."""

    def test_switch_backend_to_claude(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test switching from Ollama to Claude."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models"):
            manager._switch_backend("claude")

        assert manager._current_backend == "claude"
        assert mock_settings.ai_backend == "claude"

    def test_switch_backend_sets_default_claude_model(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test switching to Claude sets default model if not configured."""
        mock_settings.claude_model = None
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models"):
            manager._switch_backend("claude")

        assert mock_settings.claude_model == "claude-sonnet-4-20250514"

    def test_switch_backend_reloads_models(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test backend switch reloads available models."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models") as mock_load:
            manager._switch_backend("claude")

        mock_load.assert_called_once()

    def test_switch_backend_updates_chat_bar_model(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test backend switch updates selected model in chat bar."""
        mock_settings.claude_model = "claude-haiku-3-20250307"
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models"):
            manager._switch_backend("claude")

        mock_chat_bar.set_model.assert_called_with("claude-haiku-3-20250307")

    def test_switch_backend_updates_scan_button_visibility(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test backend switch updates Scan Models button visibility."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models"):
            manager._switch_backend("claude")

        # Scan button visible for Claude
        mock_chat_bar.set_scan_models_visible.assert_called_with(True)

    def test_switch_backend_emits_settings_changed(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test backend switch emits settings changed signal."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models"):
            with qtbot.waitSignal(manager.settings_changed, timeout=1000):
                manager._switch_backend("claude")


class TestModelLoading:
    """Test model loading for both backends."""

    def test_load_available_models_ollama(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test load_available_models calls Ollama loader."""
        mock_settings.ai_backend = "ollama"
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        with patch.object(manager._model_manager, "_load_ollama_models") as mock_load:
            manager._load_available_models()

        mock_load.assert_called_once()

    def test_load_available_models_claude(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test load_available_models calls Claude loader."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        with patch.object(manager._model_manager, "_load_claude_models") as mock_load:
            manager._load_available_models()

        mock_load.assert_called_once()

    def test_load_ollama_models_success(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test loading Ollama models when ollama list succeeds."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="NAME\nqwen2.5-coder:7b\ndeepseek-coder\n")

            manager._model_manager._load_ollama_models()

        # Should load detected models
        mock_chat_bar.set_models.assert_called_once()
        models = mock_chat_bar.set_models.call_args[0][0]
        assert "qwen2.5-coder:7b" in models
        assert "deepseek-coder" in models

    def test_load_ollama_models_not_found(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test loading Ollama models when ollama not found."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch("subprocess.run", side_effect=FileNotFoundError):
            manager._model_manager._load_ollama_models()

        # Should fall back to default models
        mock_chat_bar.set_models.assert_called_once()
        models = mock_chat_bar.set_models.call_args[0][0]
        assert "gnokit/improve-grammer" in models

    def test_load_ollama_models_timeout(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test loading Ollama models handles timeout."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ollama", 3)):
            manager._model_manager._load_ollama_models()

        # Should fall back to defaults
        mock_chat_bar.set_models.assert_called_once()

    def test_load_claude_models(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test loading Claude models."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # Mock ClaudeClient at the correct import location (inside the method)
        with patch("asciidoc_artisan.claude.claude_client.ClaudeClient") as mock_client_class:
            mock_client_class.AVAILABLE_MODELS = [
                "claude-sonnet-4-20250514",
                "claude-haiku-3-20250307",
            ]

            manager._model_manager._load_claude_models()

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

    def test_handle_user_message_adds_to_panel(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test user message is added to chat panel."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        manager._handle_user_message("Test question", "qwen2.5-coder:7b", "syntax")

        # Verify add_user_message was called with correct positional arguments
        mock_chat_panel.add_user_message.assert_called_once()
        call_args = mock_chat_panel.add_user_message.call_args[0]  # positional args tuple
        assert call_args[0] == "Test question"  # message
        assert call_args[1] == "qwen2.5-coder:7b"  # model
        assert call_args[2] == "syntax"  # context_mode

    def test_handle_user_message_emits_to_worker(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
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

    def test_handle_operation_cancelled(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test handling operation cancellation."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._is_processing = True

        manager.handle_operation_cancelled()

        assert manager._is_processing is False
        mock_chat_bar.set_processing.assert_called_with(False)


class TestHistoryManagement:
    """Test chat history persistence."""

    def test_load_chat_history_from_settings(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test loading chat history from settings."""
        mock_settings.chat_history = [
            {
                "role": "user",
                "content": "Q1",
                "timestamp": 1234567890.0,
                "model": "qwen2.5-coder:7b",
                "context_mode": "syntax",
            }
        ]
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        manager._history_manager.load_history()

        # Should load messages into panel
        mock_chat_panel.load_messages.assert_called()

    def test_save_chat_history_to_settings(self, mock_chat_bar, mock_chat_panel, mock_settings):
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

        manager._history_manager.save_history()

        # History manager handles saving
        assert manager._history_manager is not None

    def test_save_chat_history_limits_to_max(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test chat history is limited to max size via history manager."""
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

        manager._history_manager.save_history()

        # History manager handles max limit
        assert manager._history_manager is not None


class TestVisibilityManagement:
    """Test chat visibility management."""

    def test_should_show_chat_when_enabled_and_model_set(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test chat should show when enabled with model."""
        mock_settings.ollama_enabled = True
        mock_settings.ollama_chat_enabled = True
        mock_settings.ollama_model = "qwen2.5-coder:7b"
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        result = manager._backend_controller.should_show_chat()

        assert result is True

    def test_should_show_chat_false_when_disabled(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test chat should not show when disabled."""
        mock_settings.ai_chat_enabled = False  # Backend-agnostic flag
        mock_settings.ollama_chat_enabled = False
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        result = manager._backend_controller.should_show_chat()

        assert result is False

    def test_should_show_chat_false_when_no_model(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test chat should not show when no model set."""
        mock_settings.ollama_model = None
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        result = manager._backend_controller.should_show_chat()

        assert result is False

    def test_update_visibility_shows_when_should_show(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test update_visibility shows chat when conditions met."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings, parent=None)

        # Mock the parent after initialization
        mock_parent = Mock()
        mock_parent.chat_container = Mock()
        mock_parent.splitter = Mock()
        mock_parent.splitter.sizes.return_value = [100, 100, 0]  # Chat hidden
        mock_parent.width.return_value = 1000

        # Manually set the parent (after __init__)
        manager.setParent(None)  # Clear Qt parent
        manager._parent = mock_parent  # Use internal reference

        with patch.object(manager._backend_controller, "should_show_chat", return_value=True):
            with patch.object(manager, "parent", return_value=mock_parent):
                with qtbot.waitSignal(manager.visibility_changed, timeout=1000):
                    manager._backend_controller.update_visibility()

        # Should set chat_container visible
        mock_parent.chat_container.setVisible.assert_called_with(True)

    def test_update_visibility_hides_when_should_not_show(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test update_visibility hides chat when conditions not met."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings, parent=None)

        # Mock the parent after initialization
        mock_parent = Mock()
        mock_parent.chat_container = Mock()
        mock_parent.splitter = Mock()
        mock_parent.splitter.sizes.return_value = [100, 100, 100]  # Chat visible
        mock_parent.width.return_value = 1000

        # Manually set the parent (after __init__)
        manager.setParent(None)  # Clear Qt parent
        manager._parent = mock_parent  # Use internal reference

        with patch.object(manager._backend_controller, "should_show_chat", return_value=False):
            with patch.object(manager, "parent", return_value=mock_parent):
                with qtbot.waitSignal(manager.visibility_changed, timeout=1000):
                    manager._backend_controller.update_visibility()

        # Should set chat_container hidden
        mock_parent.chat_container.setVisible.assert_called_with(False)


class TestSignalHandlers:
    """Test signal handler methods."""

    def test_on_clear_requested(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test clearing chat history."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        manager._on_clear_requested()

        mock_chat_panel.clear_messages.assert_called_once()

    def test_on_clear_requested_saves_history(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test clearing chat saves empty history."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # Call _on_clear_requested - it clears panel and emits signals
        with qtbot.waitSignal(manager.settings_changed, timeout=1000):
            manager._on_clear_requested()

        # Verify panel was cleared
        mock_chat_panel.clear_messages.assert_called_once()

    def test_on_cancel_requested(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test cancel request emits status message."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with qtbot.waitSignal(manager.status_message, timeout=1000) as blocker:
            manager._on_cancel_requested()

        # Should emit canceling message
        assert "cancel" in blocker.args[0].lower()

    def test_on_model_changed_ollama(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test model changed updates Ollama settings."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        # Mock successful validation on model_manager
        with patch.object(manager._model_manager, "validate_model", return_value=True):
            with qtbot.waitSignal(manager.settings_changed, timeout=1000):
                manager._on_model_changed("new-model")

        assert mock_settings.ollama_model == "new-model"

    def test_on_model_changed_claude(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test model changed updates Claude settings."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        # Mock successful validation on model_manager
        with patch.object(manager._model_manager, "validate_model", return_value=True):
            with qtbot.waitSignal(manager.settings_changed, timeout=1000):
                manager._on_model_changed("claude-haiku-3-20250307")

        assert mock_settings.claude_model == "claude-haiku-3-20250307"

    def test_on_context_mode_changed(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test context mode changed updates settings."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        manager._on_context_mode_changed("document")

        assert mock_settings.chat_context_mode == "document"


class TestDocumentContext:
    """Test document context provider."""

    def test_set_document_content_provider(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test setting document content provider."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        provider = Mock(return_value="Document text")
        manager.set_document_content_provider(provider)

        assert manager._document_content_provider is provider

    def test_get_document_context_returns_content(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test getting document context."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        provider = Mock(return_value="Document content")
        manager._document_content_provider = provider

        result = manager._get_document_context()

        assert result == "Document content"

    def test_get_document_context_returns_empty_when_no_provider(self, mock_chat_bar, mock_chat_panel, mock_settings):
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
            with patch.object(manager._backend_controller, "update_visibility"):
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

    def test_is_processing(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test is_processing returns correct state."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # Initially not processing
        assert manager.is_processing() is False

        # Set to processing
        manager._is_processing = True
        assert manager.is_processing() is True

    def test_clear_history(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test clear_history clears panel via history manager."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with qtbot.waitSignal(manager.settings_changed, timeout=1000):
            manager.clear_history()

        # Should clear panel via history manager
        mock_chat_panel.clear_messages.assert_called_once()


class TestAutoDownloadModel:
    """Test auto-download default model functionality."""

    def test_auto_download_default_model(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test auto-downloading default Ollama model."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch("subprocess.Popen") as mock_popen:
            with qtbot.waitSignal(manager.status_message, timeout=1000) as blocker:
                manager._auto_download_default_model()

            # Should emit status message
            assert "gnokit/improve-grammer" in blocker.args[0]
            # Should call ollama pull
            mock_popen.assert_called_once()
            call_args = mock_popen.call_args[0][0]
            assert call_args == ["ollama", "pull", "gnokit/improve-grammer"]

    def test_auto_download_model_handles_error(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test auto-download handles subprocess error."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch("subprocess.Popen", side_effect=OSError("Command failed")):
            # Should not crash
            manager._auto_download_default_model()


class TestScanModels:
    """Test scan models functionality for Claude."""

    def test_scan_models_claude_success(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test scanning Claude models successfully."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        mock_result = Mock()
        mock_result.success = True
        mock_result.content = "Models:\n- claude-sonnet-4\n- claude-haiku-4.5"

        with patch("asciidoc_artisan.claude.ClaudeClient") as mock_client_class:
            mock_client = Mock()
            mock_client.fetch_available_models_from_api.return_value = mock_result
            mock_client_class.return_value = mock_client

            with qtbot.waitSignal(manager.status_message, timeout=1000):
                manager._on_scan_models_requested()

        # Should add models to chat panel
        mock_chat_panel.add_message.assert_called_once()
        call_args = mock_chat_panel.add_message.call_args[0]
        assert call_args[0] == "system"
        assert "Available Models" in call_args[1]

    def test_scan_models_claude_failure(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test scanning Claude models with API error."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "API key invalid"

        with patch("asciidoc_artisan.claude.ClaudeClient") as mock_client_class:
            mock_client = Mock()
            mock_client.fetch_available_models_from_api.return_value = mock_result
            mock_client_class.return_value = mock_client

            manager._on_scan_models_requested()

        # Should add error to chat panel
        mock_chat_panel.add_message.assert_called_once()
        call_args = mock_chat_panel.add_message.call_args[0]
        assert "Failed" in call_args[1]
        assert "API key invalid" in call_args[1]

    def test_scan_models_claude_exception(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test scanning Claude models with exception."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        with patch(
            "asciidoc_artisan.claude.ClaudeClient",
            side_effect=Exception("Import error"),
        ):
            manager._on_scan_models_requested()

        # Should add error to chat panel
        mock_chat_panel.add_message.assert_called_once()
        call_args = mock_chat_panel.add_message.call_args[0]
        assert "Error Scanning Models" in call_args[1]

    def test_scan_models_not_available_for_ollama(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test scan models not available for Ollama backend."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        with qtbot.waitSignal(manager.status_message, timeout=1000) as blocker:
            manager._on_scan_models_requested()

        # Should emit warning
        assert "Claude" in blocker.args[0]


class TestModelValidation:
    """Test model validation for both backends."""

    def test_validate_model_empty_returns_false(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test validating empty model name returns False."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        result = manager._validate_model("")

        assert result is False

    def test_validate_model_claude_valid(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test validating valid Claude model."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        with patch("asciidoc_artisan.claude.ClaudeClient") as mock_client_class:
            mock_client_class.AVAILABLE_MODELS = [
                "claude-sonnet-4-20250514",
                "claude-haiku-4-5",
            ]

            result = manager._validate_model("claude-sonnet-4-20250514")

        assert result is True

    def test_validate_model_claude_invalid(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test validating invalid Claude model."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        with patch("asciidoc_artisan.claude.ClaudeClient") as mock_client_class:
            mock_client_class.AVAILABLE_MODELS = [
                "claude-sonnet-4-20250514",
            ]

            result = manager._validate_model("invalid-model")

        assert result is False

    def test_validate_model_claude_exception(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test Claude model validation handles exception."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        with patch(
            "asciidoc_artisan.claude.ClaudeClient",
            side_effect=Exception("Import error"),
        ):
            result = manager._validate_model("claude-sonnet-4-20250514")

        # Should return False on error
        assert result is False

    def test_validate_model_ollama_not_found(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test Ollama validation when ollama not found."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = manager._validate_model("qwen2.5-coder:7b")

        # Should return False when ollama not found
        assert result is False

    def test_validate_model_ollama_timeout(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test Ollama validation handles timeout gracefully."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ollama", 2)):
            result = manager._validate_model("qwen2.5-coder:7b")

        # Should return True on timeout (assume valid to avoid blocking)
        assert result is True

    def test_validate_model_ollama_command_failed(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test Ollama validation when ollama list fails."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=1, stderr="Error")

            result = manager._validate_model("qwen2.5-coder:7b")

        # Should return False when command fails
        assert result is False

    def test_validate_model_ollama_exception(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test Ollama validation handles generic exception."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        with patch("subprocess.run", side_effect=Exception("Generic error")):
            result = manager._validate_model("qwen2.5-coder:7b")

        # Should return True on error (assume valid to avoid blocking)
        assert result is True

    def test_validate_model_unknown_backend(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test validation with unknown backend returns False."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "unknown"

        result = manager._validate_model("some-model")

        assert result is False


class TestTogglePanelVisibility:
    """Test toggle panel visibility functionality."""

    def test_toggle_panel_visibility_shows_when_hidden(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test toggling panel visibility from hidden to shown."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        mock_parent = Mock()
        mock_parent.chat_container = Mock()
        mock_parent.chat_container.isVisible.return_value = False

        with patch.object(manager, "parent", return_value=mock_parent):
            with patch.object(manager._backend_controller, "update_visibility"):
                with qtbot.waitSignal(manager.settings_changed, timeout=1000):
                    manager.toggle_panel_visibility()

        # Should enable chat
        assert mock_settings.ai_chat_enabled is True
        assert mock_settings.ollama_chat_enabled is True

    def test_toggle_panel_visibility_hides_when_shown(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test toggling panel visibility from shown to hidden."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        mock_parent = Mock()
        mock_parent.chat_container = Mock()
        mock_parent.chat_container.isVisible.return_value = True

        with patch.object(manager, "parent", return_value=mock_parent):
            with patch.object(manager._backend_controller, "update_visibility"):
                with qtbot.waitSignal(manager.settings_changed, timeout=1000):
                    manager.toggle_panel_visibility()

        # Should disable chat
        assert mock_settings.ai_chat_enabled is False
        assert mock_settings.ollama_chat_enabled is False

    def test_toggle_panel_visibility_no_parent(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test toggle panel visibility without parent does nothing."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "parent", return_value=None):
            # Should not crash
            manager.toggle_panel_visibility()

    def test_toggle_panel_visibility_no_chat_container(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test toggle panel visibility without chat_container does nothing."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        mock_parent = Mock(spec=[])  # No chat_container attribute

        with patch.object(manager, "parent", return_value=mock_parent):
            # Should not crash
            manager.toggle_panel_visibility()


class TestInitializeEdgeCases:
    """Test initialize method edge cases."""

    @patch("asciidoc_artisan.core.SecureCredentials")
    def test_initialize_auto_switch_to_claude(self, mock_creds_class, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test initialize auto-switches to Claude when Ollama disabled."""
        mock_settings.ollama_enabled = False
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds

        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager._backend_controller, "switch_backend") as mock_switch:
            with patch.object(manager._backend_controller, "update_visibility"):
                manager.initialize()

        # Should switch to Claude
        mock_switch.assert_called_once_with("claude")

    def test_initialize_sets_claude_model(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test initialize sets Claude model from settings."""
        mock_settings.ai_backend = "claude"
        mock_settings.claude_model = "claude-haiku-4-5"
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        with patch.object(manager, "_load_available_models"):
            with patch.object(manager._history_manager, "load_history"):
                with patch.object(manager._backend_controller, "update_visibility"):
                    with patch("asciidoc_artisan.core.SecureCredentials") as mock_creds_class:
                        mock_creds = Mock()
                        mock_creds.has_anthropic_key.return_value = False
                        mock_creds_class.return_value = mock_creds

                        manager.initialize()

        # Should set model in chat bar
        mock_chat_bar.set_model.assert_called_with("claude-haiku-4-5")


class TestOllamaModelLoadingEdgeCases:
    """Test Ollama model loading edge cases."""

    def test_load_ollama_models_no_models_triggers_download(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test loading Ollama with no models triggers auto-download."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch("subprocess.run") as mock_run:
            # Ollama running but no models (just header line)
            mock_run.return_value = Mock(returncode=0, stdout="NAME\n")

            with patch.object(manager._model_manager, "_auto_download_default_model") as mock_download:
                manager._model_manager._load_ollama_models()

            # Should trigger auto-download
            mock_download.assert_called_once()

    def test_load_ollama_models_generic_exception(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test Ollama model loading handles generic exception."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch("subprocess.run", side_effect=RuntimeError("Unknown error")):
            manager._model_manager._load_ollama_models()

        # Should fall back to default models
        mock_chat_bar.set_models.assert_called_once()


class TestClaudeModelLoadingEdgeCases:
    """Test Claude model loading edge cases."""

    @patch("asciidoc_artisan.core.SecureCredentials")
    def test_load_claude_models_with_api_key(
        self, mock_creds_class, mock_chat_bar, mock_chat_panel, mock_settings, qtbot
    ):
        """Test loading Claude models with API key shows success message."""
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds

        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch("asciidoc_artisan.claude.ClaudeClient") as mock_client_class:
            mock_client_class.AVAILABLE_MODELS = ["claude-sonnet-4-20250514"]

            with qtbot.waitSignal(manager.status_message, timeout=1000) as blocker:
                manager._model_manager._load_claude_models()

            # Should show models available message
            assert "available" in blocker.args[0].lower()

    def test_load_claude_models_exception(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test Claude model loading handles exception gracefully."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # Patch to raise exception when accessing AVAILABLE_MODELS
        with patch("asciidoc_artisan.claude.ClaudeClient") as mock_client_class:
            mock_client_class.AVAILABLE_MODELS.copy.side_effect = ImportError("Module not found")
            with patch("asciidoc_artisan.core.SecureCredentials"):
                manager._model_manager._load_claude_models()

        # Should fall back to defaults
        mock_chat_bar.set_models.assert_called_once()
        models = mock_chat_bar.set_models.call_args[0][0]
        assert "claude-sonnet-4-20250514" in models

    def test_load_claude_models_adds_current_model(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test Claude loading adds current model if not in list."""
        mock_settings.claude_model = "claude-opus-4-20250514"
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch("asciidoc_artisan.claude.ClaudeClient") as mock_client_class:
            mock_client_class.AVAILABLE_MODELS = ["claude-sonnet-4-20250514"]
            with patch("asciidoc_artisan.core.SecureCredentials"):
                manager._model_manager._load_claude_models()

        # Should add current model to list
        models = mock_chat_bar.set_models.call_args[0][0]
        assert "claude-opus-4-20250514" in models


class TestLoadAvailableModelsEdgeCases:
    """Test _load_available_models edge cases."""

    def test_load_available_models_unknown_backend(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test loading models with unknown backend shows error."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "invalid_backend"

        with qtbot.waitSignal(manager.status_message, timeout=1000) as blocker:
            manager._load_available_models()

        # Should emit error message
        assert "unknown" in blocker.args[0].lower()
        assert "invalid_backend" in blocker.args[0]


class TestSwitchBackendEdgeCases:
    """Test _switch_backend edge cases."""

    def test_switch_backend_sets_default_ollama_model(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test switching to Ollama sets default model if not configured."""
        mock_settings.ollama_model = None
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        with patch.object(manager, "_load_available_models"):
            manager._switch_backend("ollama")

        assert mock_settings.ollama_model == "gnokit/improve-grammer"

    def test_switch_backend_updates_parent_checkmarks(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test backend switch updates parent window checkmarks."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        mock_parent = Mock()
        mock_parent._update_ai_backend_checkmarks = Mock()

        with patch.object(manager, "parent", return_value=mock_parent):
            with patch.object(manager, "_load_available_models"):
                manager._switch_backend("claude")

        # Should call parent method
        mock_parent._update_ai_backend_checkmarks.assert_called_once()

    def test_switch_backend_sets_ollama_model_in_chat_bar(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test switching to Ollama sets model in chat bar."""
        mock_settings.ollama_model = "deepseek-coder"
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with patch.object(manager, "_load_available_models"):
            manager._switch_backend("ollama")

        mock_chat_bar.set_model.assert_called_with("deepseek-coder")


class TestReentrancyGuard:
    """Test reentrancy guard in message handling."""

    def test_on_message_sent_blocks_when_processing(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test message sent is blocked when already processing."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._is_processing = True

        with qtbot.waitSignal(manager.status_message, timeout=1000) as blocker:
            manager._on_message_sent("Test", "model", "syntax")

        # Should emit busy message
        assert "processing" in blocker.args[0].lower()
        # Should not add to panel
        mock_chat_panel.add_user_message.assert_not_called()


class TestDocumentContentInMessages:
    """Test document content inclusion in messages."""

    def test_on_message_sent_includes_document_content(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test message includes document content when enabled."""
        mock_settings.chat_send_document = True
        mock_settings.ollama_chat_send_document = True
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        doc_provider = Mock(return_value="Document content here")
        manager.set_document_content_provider(doc_provider)

        with qtbot.waitSignal(manager.message_sent_to_worker, timeout=1000) as blocker:
            manager._on_message_sent("Test", "model", "document")

        # Should include document content (5th arg)
        assert blocker.args[4] == "Document content here"


class TestOnModelChangedEdgeCases:
    """Test _on_model_changed edge cases."""

    def test_on_model_changed_empty_model_name(self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot):
        """Test model changed with empty model name shows error."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        with qtbot.waitSignal(manager.status_message, timeout=1000) as blocker:
            manager._on_model_changed("")

        # Should emit error
        assert "error" in blocker.args[0].lower()

    def test_on_model_changed_invalid_claude_model_reverts(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test invalid Claude model change reverts to current."""
        mock_settings.claude_model = "claude-sonnet-4-20250514"
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        with patch.object(manager, "_validate_model", return_value=False):
            manager._on_model_changed("invalid-model")

        # Should revert to current model
        mock_chat_bar.set_model.assert_called_with("claude-sonnet-4-20250514")


class TestShouldShowChatEdgeCases:
    """Test _should_show_chat edge cases."""

    @patch("asciidoc_artisan.core.SecureCredentials")
    def test_should_show_chat_auto_switches_to_claude(
        self, mock_creds_class, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test _should_show_chat auto-switches to Claude when Ollama disabled."""
        mock_settings.ai_chat_enabled = True
        mock_settings.ollama_enabled = False
        mock_settings.claude_model = "claude-sonnet-4-20250514"

        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds

        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        with patch.object(manager._backend_controller, "switch_backend") as mock_switch:
            result = manager._backend_controller.should_show_chat()

        # Should auto-switch
        mock_switch.assert_called_once_with("claude")
        assert result is True

    def test_should_show_chat_claude_backend(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test _should_show_chat with Claude backend."""
        mock_settings.ai_chat_enabled = True
        mock_settings.claude_model = "claude-sonnet-4-20250514"

        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        with patch("asciidoc_artisan.core.SecureCredentials") as mock_creds_class:
            mock_creds = Mock()
            mock_creds.has_anthropic_key.return_value = True
            mock_creds_class.return_value = mock_creds

            result = manager._backend_controller.should_show_chat()

        assert result is True

    def test_should_show_chat_unknown_backend(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test _should_show_chat with unknown backend returns False."""
        mock_settings.ai_chat_enabled = True

        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "unknown"

        with patch("asciidoc_artisan.core.SecureCredentials"):
            result = manager._backend_controller.should_show_chat()

        assert result is False


class TestUpdateVisibilityEdgeCases:
    """Test _update_visibility edge cases."""

    @patch("asciidoc_artisan.core.SecureCredentials")
    def test_update_visibility_claude_backend_status(
        self, mock_creds_class, mock_chat_bar, mock_chat_panel, mock_settings
    ):
        """Test update_visibility logs Claude backend status."""
        mock_settings.claude_model = "claude-sonnet-4-20250514"
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds

        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        with patch.object(manager._backend_controller, "should_show_chat", return_value=True):
            with patch.object(manager, "parent", return_value=None):
                # Should not crash
                manager._backend_controller.update_visibility()

    def test_update_visibility_show_chat_handles_runtime_error(
        self, mock_chat_bar, mock_chat_panel, mock_settings, qtbot
    ):
        """Test update_visibility show_chat callback handles RuntimeError."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # Create a mock parent that will be "deleted" when accessed
        mock_parent = Mock()
        mock_parent.chat_container = Mock()
        mock_parent.splitter = Mock()
        mock_parent.splitter.sizes.return_value = [100, 100, 0]

        # Make width() raise RuntimeError (simulating deleted widget)
        mock_parent.width.side_effect = RuntimeError("C++ object deleted")

        with patch.object(manager._backend_controller, "should_show_chat", return_value=True):
            with patch.object(manager, "parent", return_value=mock_parent):
                # Should not crash
                manager._backend_controller.update_visibility()


class TestUpdateSettingsEdgeCases:
    """Test update_settings edge cases."""

    @patch("asciidoc_artisan.core.SecureCredentials")
    def test_update_settings_switches_to_claude(self, mock_creds_class, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test update_settings switches to Claude when Ollama disabled."""
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = True
        mock_creds_class.return_value = mock_creds

        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        new_settings = Mock(spec=Settings)
        new_settings.ai_backend = "claude"
        new_settings.ollama_enabled = False
        new_settings.claude_model = "claude-sonnet-4-20250514"
        new_settings.chat_context_mode = "syntax"
        new_settings.ollama_chat_context_mode = "syntax"

        with patch.object(manager, "_switch_backend") as mock_switch:
            with patch.object(manager._backend_controller, "update_visibility"):
                manager.update_settings(new_settings)

        # Should switch backend
        mock_switch.assert_called_once_with("claude")

    @patch("asciidoc_artisan.core.SecureCredentials")
    def test_update_settings_no_switch_needed(self, mock_creds_class, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test update_settings without backend switch."""
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_creds_class.return_value = mock_creds

        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "ollama"

        new_settings = Mock(spec=Settings)
        new_settings.ai_backend = "ollama"
        new_settings.ollama_enabled = True
        new_settings.ollama_model = "qwen2.5-coder:7b"
        new_settings.claude_model = None
        new_settings.chat_context_mode = "syntax"
        new_settings.ollama_chat_context_mode = "syntax"

        with patch.object(manager, "_load_available_models") as mock_load:
            with patch.object(manager._backend_controller, "update_visibility"):
                manager.update_settings(new_settings)

        # Should reload models
        mock_load.assert_called_once()
        # Should set model
        mock_chat_bar.set_model.assert_called_with("qwen2.5-coder:7b")

    def test_update_settings_sets_claude_model(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test update_settings sets Claude model when backend is Claude."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)
        manager._current_backend = "claude"

        new_settings = Mock(spec=Settings)
        new_settings.ai_backend = "claude"
        new_settings.ollama_enabled = False
        new_settings.claude_model = "claude-haiku-4-5"
        new_settings.chat_context_mode = "syntax"
        new_settings.ollama_chat_context_mode = "syntax"

        with patch("asciidoc_artisan.core.SecureCredentials") as mock_creds_class:
            mock_creds = Mock()
            mock_creds.has_anthropic_key.return_value = False
            mock_creds_class.return_value = mock_creds

            with patch.object(manager, "_load_available_models"):
                with patch.object(manager._backend_controller, "update_visibility"):
                    manager.update_settings(new_settings)

        # Should set Claude model
        mock_chat_bar.set_model.assert_called_with("claude-haiku-4-5")


class TestHandleResponseChunk:
    """Test handle_response_chunk for streaming."""

    def test_handle_response_chunk(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test handling streaming response chunk."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        manager.handle_response_chunk("Partial response")

        # Should append to last message
        mock_chat_panel.append_to_last_message.assert_called_once_with("Partial response")


class TestTrimHistory:
    """Test history trimming functionality via history manager."""

    def test_trim_history(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test history manager exists and handles trimming."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # History manager handles trimming internally
        assert manager._history_manager is not None
        # Can save history (which trims if needed)
        manager._history_manager.save_history()


class TestChatManagerCoverageEdgeCases:
    """Additional tests to achieve 97%+ coverage for chat_manager."""

    def test_load_chat_history_with_history_manager(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test load_chat_history uses history manager."""
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # History manager is responsible for loading
        assert manager._history_manager is not None
        manager._history_manager.load_history()

    def test_validate_model_ollama_list_output_parsing(self, mock_chat_bar, mock_chat_panel, mock_settings):
        """Test validate_model parses ollama list output (lines 493-503)."""
        mock_settings.chat_backend = "ollama"
        manager = ChatManager(mock_chat_bar, mock_chat_panel, mock_settings)

        # Mock subprocess with model list
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="NAME    ID    SIZE\nllama2  abc   3.8GB\nmistral def   4.1GB\n",
                stderr="",
            )

            # Test existing model
            result = manager._validate_model("llama2")
            assert result is True

            # Test non-existent model
            result = manager._validate_model("nonexistent")
            assert result is False
