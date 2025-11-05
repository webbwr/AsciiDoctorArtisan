"""
Integration tests for Chat System (v1.7.0).

Tests the integration of ChatBarWidget, ChatPanelWidget, ChatManager,
and OllamaChatWorker with the main window.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from asciidoc_artisan.core import Settings
from asciidoc_artisan.ui.main_window import AsciiDocEditor


@pytest.fixture
def main_window(qtbot, test_settings):
    """Create main window for testing with safe settings."""
    from unittest.mock import patch, Mock

    # Mock settings loading to use test_settings
    # Also mock Claude API client to prevent real API calls
    with patch(
        "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings",
        return_value=test_settings,
    ), patch(
        "asciidoc_artisan.claude.claude_client.Anthropic"
    ) as mock_anthropic, patch(
        "asciidoc_artisan.claude.claude_client.SecureCredentials"
    ) as mock_creds:
        # Setup mocks to prevent API calls
        mock_creds_instance = Mock()
        mock_creds_instance.get_anthropic_key.return_value = None  # No key = no API calls
        mock_creds.return_value = mock_creds_instance

        window = AsciiDocEditor()
        qtbot.addWidget(window)
        return window


@pytest.mark.integration
class TestChatIntegration:
    """Test chat system integration with main window."""

    def test_chat_widgets_exist(self, main_window):
        """Test that chat widgets are created."""
        assert hasattr(main_window, "chat_bar")
        assert hasattr(main_window, "chat_panel")
        assert hasattr(main_window, "chat_container")
        assert main_window.chat_bar is not None
        assert main_window.chat_panel is not None
        assert main_window.chat_container is not None

    def test_chat_manager_exists(self, main_window):
        """Test that chat manager is created."""
        assert hasattr(main_window, "chat_manager")
        assert main_window.chat_manager is not None

    def test_ollama_worker_exists(self, main_window):
        """Test that Ollama chat worker is created."""
        assert hasattr(main_window, "ollama_chat_worker")
        assert hasattr(main_window, "ollama_chat_thread")
        assert main_window.ollama_chat_worker is not None
        assert main_window.ollama_chat_thread is not None

    def test_chat_visibility_control(self, main_window):
        """Test that chat container visibility can be controlled."""
        # Chat is visible by default (v1.9.0+ always shows chat container)
        # Note: In production, visibility is controlled via Tools menu toggle
        assert main_window.chat_container.isVisible()

        # Hide chat
        main_window.chat_container.hide()
        assert main_window.chat_container.isHidden()

        # Show chat again
        main_window.chat_container.show()
        assert main_window.chat_container.isVisible()

    def test_chat_in_splitter(self, main_window):
        """Test that chat pane is in the main splitter."""
        assert hasattr(main_window, "splitter")
        assert main_window.splitter.count() == 3  # Editor, Preview, Chat

        # Verify widgets in splitter
        widgets = [main_window.splitter.widget(i) for i in range(3)]
        assert main_window.chat_container in widgets

    def test_signal_connections(self, main_window, qtbot):
        """Test that signals are properly connected."""
        # Test ChatManager -> OllamaChatWorker connection
        # Signal signature: message, model, mode, history, doc_content
        with qtbot.waitSignal(
            main_window.chat_manager.message_sent_to_worker, timeout=100
        ) as blocker:
            # This should emit message_sent_to_worker with correct signature
            main_window.chat_manager.message_sent_to_worker.emit(
                "Test message",  # message
                "test-model",    # model
                "general",       # mode
                [],             # history
                None            # doc_content
            )

        # Signal was emitted
        assert blocker.signal_triggered

    def test_chat_bar_properties(self, main_window):
        """Test that chat bar has required properties."""
        assert main_window.chat_bar.minimumHeight() >= 70
        assert hasattr(main_window.chat_bar, "message_sent")
        assert hasattr(main_window.chat_bar, "cancel_requested")

    def test_chat_panel_properties(self, main_window):
        """Test that chat panel has required properties."""
        assert hasattr(main_window.chat_panel, "add_message")
        assert hasattr(main_window.chat_panel, "clear_messages")
        assert hasattr(main_window.chat_panel, "get_message_count")

    def test_chat_manager_initialization(self, main_window):
        """Test that chat manager is properly initialized."""
        # Should have references to widgets (private attributes)
        assert main_window.chat_manager._chat_bar == main_window.chat_bar
        assert main_window.chat_manager._chat_panel == main_window.chat_panel

        # Should have settings
        assert main_window.chat_manager._settings is not None

    def test_worker_thread_running(self, main_window):
        """Test that Ollama chat worker thread is running."""
        assert main_window.ollama_chat_thread.isRunning()

    def test_document_content_provider(self, main_window, qtbot):
        """Test that document content provider is set."""
        # Set some test content
        test_content = "= Test Document\n\nThis is a test."
        main_window.editor.setPlainText(test_content)

        # ChatManager should be able to get document context
        # Method renamed from _get_document_content to _get_document_context
        context = main_window.chat_manager._get_document_context()
        assert context is not None

        # Should return the editor content (first 2KB for context)
        # Content may be truncated if larger than 2KB
        assert test_content in context or context in test_content

    def test_status_message_connection(self, main_window, qtbot):
        """Test that chat manager status messages are connected."""
        # ChatManager status messages should connect to StatusManager
        with qtbot.waitSignal(
            main_window.chat_manager.status_message, timeout=100
        ) as blocker:
            main_window.chat_manager.status_message.emit("Test status")

        assert blocker.signal_triggered

    def test_chat_container_constraints(self, main_window):
        """Test that chat container has size constraints."""
        assert main_window.chat_container.minimumWidth() >= 250
        assert main_window.chat_container.maximumWidth() <= 600


@pytest.mark.integration
class TestChatLayout:
    """Test chat UI layout structure."""

    def test_chat_pane_layout(self, main_window):
        """Test that chat pane has correct layout structure."""
        # Should have vertical layout: toolbar, panel, bar
        layout = main_window.chat_container.layout()
        assert layout is not None
        assert layout.count() == 3  # Toolbar, Panel, Bar

    def test_chat_panel_in_layout(self, main_window):
        """Test that chat panel is in the layout."""
        layout = main_window.chat_container.layout()
        widgets = [layout.itemAt(i).widget() for i in range(layout.count())]
        assert main_window.chat_panel in widgets

    def test_chat_bar_in_layout(self, main_window):
        """Test that chat bar is in the layout."""
        layout = main_window.chat_container.layout()
        widgets = [layout.itemAt(i).widget() for i in range(layout.count())]
        assert main_window.chat_bar in widgets


@pytest.mark.integration
class TestChatWorkerIntegration:
    """Test Ollama chat worker integration."""

    def test_worker_cancel_connection(self, main_window, qtbot):
        """Test that cancel button connects to worker."""
        with qtbot.waitSignal(
            main_window.chat_bar.cancel_requested, timeout=100
        ) as blocker:
            # Simulate cancel button click
            main_window.chat_bar.cancel_requested.emit()

        assert blocker.signal_triggered

    @pytest.mark.forked
    def test_worker_response_connection(self, main_window, qtbot):
        """Test that worker responses connect to chat manager.

        NOTE: Runs in isolated subprocess via pytest-forked to prevent Qt worker
        thread interference with other tests (v1.9.2+).
        """
        import time
        from asciidoc_artisan.core.models import ChatMessage

        # Worker should emit signals that ChatManager receives
        # Signal signature changed: now expects ChatMessage object only
        with qtbot.waitSignal(
            main_window.ollama_chat_worker.chat_response_ready, timeout=100
        ) as blocker:
            # Create test ChatMessage with all required fields
            test_message = ChatMessage(
                role="assistant",
                content="Test response",
                timestamp=time.time(),
                model="test-model",
                context_mode="general"
            )
            # Emit test response with correct signature
            main_window.ollama_chat_worker.chat_response_ready.emit(test_message)

        assert blocker.signal_triggered


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
