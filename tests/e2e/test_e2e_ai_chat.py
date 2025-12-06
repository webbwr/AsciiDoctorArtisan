"""E2E Tests for AI Chat workflows (Ollama and Claude backends)."""

import os
from unittest.mock import Mock, patch

import pytest

# Force software rendering for WSL2 compatibility
os.environ.setdefault("ASCIIDOC_ARTISAN_NO_WEBENGINE", "1")

from asciidoc_artisan.ui.main_window import AsciiDocEditor


@pytest.fixture
def app_window_with_chat(qtbot, test_settings, tmp_path):
    """Create main window with AI chat enabled."""
    test_settings.last_directory = str(tmp_path)
    test_settings.ollama_enabled = True
    test_settings.ollama_model = "test-model"

    with (
        patch(
            "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings",
            return_value=test_settings,
        ),
        patch("asciidoc_artisan.claude.claude_client.Anthropic"),
        patch("asciidoc_artisan.claude.claude_client.SecureCredentials") as mock_creds,
    ):
        mock_creds_instance = Mock()
        mock_creds_instance.get_anthropic_key.return_value = None
        mock_creds.return_value = mock_creds_instance

        window = AsciiDocEditor()
        qtbot.addWidget(window)
        yield window

        try:
            if hasattr(window, "spell_check_manager") and window.spell_check_manager:
                if hasattr(window.spell_check_manager, "check_timer"):
                    window.spell_check_manager.check_timer.stop()
            window.close()
        except RuntimeError:
            pass


@pytest.mark.e2e
@pytest.mark.forked
class TestAIChatWorkflow:
    """Test AI chat interaction workflows."""

    def test_chat_panel_initialization(self, app_window_with_chat, qtbot):
        """E2E: Verify chat panel is initialized."""
        assert hasattr(app_window_with_chat, "chat_panel")
        assert hasattr(app_window_with_chat, "chat_bar")

    def test_chat_bar_controls(self, app_window_with_chat, qtbot):
        """E2E: Verify chat bar controls exist."""
        if app_window_with_chat.chat_bar:
            assert hasattr(app_window_with_chat.chat_bar, "_input_field")
            assert hasattr(app_window_with_chat.chat_bar, "_model_selector")
            assert hasattr(app_window_with_chat.chat_bar, "_context_selector")

    def test_chat_manager_exists(self, app_window_with_chat, qtbot):
        """E2E: Verify chat manager is initialized."""
        assert hasattr(app_window_with_chat, "chat_manager")

    def test_context_mode_selection(self, app_window_with_chat, qtbot):
        """E2E: Test context mode switching."""
        if app_window_with_chat.chat_bar:
            # Test setting different context modes
            modes = ["document", "syntax", "general", "editing"]
            for mode in modes:
                app_window_with_chat.chat_bar.set_context_mode(mode)
                assert app_window_with_chat.chat_bar.get_current_context_mode() == mode


@pytest.mark.e2e
@pytest.mark.forked
class TestOllamaBackendWorkflow:
    """Test Ollama-specific workflows."""

    def test_ollama_settings_accessible(self, app_window_with_chat, qtbot):
        """E2E: Verify Ollama settings are accessible."""
        settings = app_window_with_chat._settings
        assert hasattr(settings, "ollama_enabled")
        assert hasattr(settings, "ollama_model")

    def test_model_loading_capability(self, app_window_with_chat, qtbot):
        """E2E: Verify model loading capability exists."""
        if hasattr(app_window_with_chat, "chat_manager"):
            manager = app_window_with_chat.chat_manager
            assert hasattr(manager, "model_manager")


@pytest.mark.e2e
@pytest.mark.forked
class TestClaudeBackendWorkflow:
    """Test Claude-specific workflows."""

    def test_claude_settings_accessible(self, app_window_with_chat, qtbot):
        """E2E: Verify Claude settings are accessible."""
        settings = app_window_with_chat._settings
        assert hasattr(settings, "claude_model")

    def test_api_key_handling(self, app_window_with_chat, qtbot):
        """E2E: Verify API key handling capability."""
        # SecureCredentials should be accessible
        from asciidoc_artisan.core import SecureCredentials

        creds = SecureCredentials()
        assert hasattr(creds, "has_anthropic_key")
        assert hasattr(creds, "get_anthropic_key")
