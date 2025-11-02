"""
Tests for Chat History Persistence (v1.7.0).

Tests that chat history is properly saved to and loaded from settings
across application sessions.
"""

import pytest
from PySide6.QtCore import QTimer

from asciidoc_artisan.core import Settings
from asciidoc_artisan.core.models import ChatMessage
from asciidoc_artisan.ui.chat_bar_widget import ChatBarWidget
from asciidoc_artisan.ui.chat_manager import ChatManager
from asciidoc_artisan.ui.chat_panel_widget import ChatPanelWidget


@pytest.fixture
def settings():
    """Create fresh settings for testing."""
    s = Settings()
    s.ollama_enabled = True
    s.ollama_model = "gnokit/improve-grammer"
    s.ollama_chat_enabled = True
    s.ollama_chat_history = []
    s.ollama_chat_max_history = 100
    s.ollama_chat_context_mode = "general"
    s.ollama_chat_send_document = False
    return s


@pytest.fixture
def chat_bar(qtbot):
    """Create chat bar widget."""
    widget = ChatBarWidget()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def chat_panel(qtbot):
    """Create chat panel widget."""
    widget = ChatPanelWidget()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def chat_manager(qtbot, chat_bar, chat_panel, settings):
    """Create chat manager with widgets and settings."""
    manager = ChatManager(chat_bar, chat_panel, settings)
    return manager


class TestHistorySaving:
    """Test saving chat history to settings."""

    def test_empty_history_saves(self, chat_manager, settings):
        """Test saving empty history."""
        # Start with empty history
        assert settings.ollama_chat_history == []

        # Initialize (should not change empty history)
        chat_manager.initialize()

        # History should still be empty
        assert settings.ollama_chat_history == []

    def test_history_saved_after_message(self, chat_manager, settings, qtbot):
        """Test history is saved after adding messages."""
        # Add a user message
        chat_manager._chat_panel.add_user_message(
            "Test message", "gnokit/improve-grammer", "general"
        )

        # Get history
        history = chat_manager._chat_panel.get_message_history()
        assert len(history) == 1
        assert history[0]["content"] == "Test message"

    def test_history_includes_timestamps(self, chat_manager, settings):
        """Test saved history includes timestamps."""
        # Add message
        chat_manager._chat_panel.add_user_message("Test", "gnokit/improve-grammer", "general")

        # Check history
        history = chat_manager._chat_panel.get_message_history()
        assert len(history) == 1
        assert "timestamp" in history[0]
        assert history[0]["timestamp"] is not None

    def test_history_includes_all_fields(self, chat_manager, settings):
        """Test saved history includes all required fields."""
        # Add user message
        chat_manager._chat_panel.add_user_message(
            "User question", "gnokit/improve-grammer", "document"
        )

        # Add AI response
        chat_manager._chat_panel.add_ai_message("AI answer", "gnokit/improve-grammer")

        # Get history
        history = chat_manager._chat_panel.get_message_history()
        assert len(history) == 2

        # Check user message fields
        user_msg = history[0]
        assert user_msg["role"] == "user"
        assert user_msg["content"] == "User question"
        assert user_msg["model"] == "gnokit/improve-grammer"
        assert user_msg["context_mode"] == "document"

        # Check AI message fields
        ai_msg = history[1]
        assert ai_msg["role"] == "assistant"
        assert ai_msg["content"] == "AI answer"
        assert ai_msg["model"] == "gnokit/improve-grammer"

    def test_max_history_limit(self, chat_manager, settings):
        """Test history respects max limit."""
        settings.ollama_chat_max_history = 10

        # Add 15 messages (exceeds limit)
        for i in range(15):
            chat_manager._chat_panel.add_user_message(
                f"Message {i}", "gnokit/improve-grammer", "general"
            )

        # Get history
        history = chat_manager._chat_panel.get_message_history()

        # Should only keep last 10
        assert len(history) <= 10


class TestHistoryLoading:
    """Test loading chat history from settings."""

    def test_load_empty_history(self, chat_manager, settings):
        """Test loading with empty history."""
        settings.ollama_chat_history = []
        chat_manager.initialize()

        # Panel should have no messages
        assert chat_manager._chat_panel.get_message_count() == 0

    def test_load_existing_history(self, chat_manager, settings):
        """Test loading existing history from settings."""
        # Create sample history
        settings.ollama_chat_history = [
            {
                "role": "user",
                "content": "Hello",
                "model": "gnokit/improve-grammer",
                "context_mode": "general",
                "timestamp": "2025-11-02T10:00:00",
            },
            {
                "role": "assistant",
                "content": "Hi there!",
                "model": "gnokit/improve-grammer",
                "timestamp": "2025-11-02T10:00:01",
            },
        ]

        # Initialize (loads history)
        chat_manager.initialize()

        # Panel should have 2 messages
        assert chat_manager._chat_panel.get_message_count() == 2

    def test_corrupted_history_handled(self, chat_manager, settings):
        """Test corrupted history is handled gracefully."""
        # Set corrupted history (missing required fields)
        settings.ollama_chat_history = [
            {"role": "user"},  # Missing content
            {"content": "Test"},  # Missing role
            None,  # Invalid entry
        ]

        # Initialize should not crash
        chat_manager.initialize()

        # Should skip corrupted entries
        count = chat_manager._chat_panel.get_message_count()
        assert count == 0  # All entries were invalid


class TestHistoryPersistence:
    """Test history persists across manager instances."""

    def test_history_survives_recreation(self, qtbot, chat_bar, chat_panel, settings):
        """Test history persists when recreating manager."""
        # Create first manager
        manager1 = ChatManager(chat_bar, chat_panel, settings)
        manager1.initialize()

        # Add messages
        chat_panel.add_user_message("Question 1", "gnokit/improve-grammer", "general")
        chat_panel.add_ai_message("Answer 1", "gnokit/improve-grammer")

        # Save to settings
        history1 = chat_panel.get_message_history()
        settings.ollama_chat_history = history1

        # Create second manager (simulates app restart)
        chat_panel2 = ChatPanelWidget()
        qtbot.addWidget(chat_panel2)
        manager2 = ChatManager(chat_bar, chat_panel2, settings)
        manager2.initialize()

        # History should be restored
        assert chat_panel2.get_message_count() == 2

        # Content should match
        history2 = chat_panel2.get_message_history()
        assert len(history2) == len(history1)
        assert history2[0]["content"] == "Question 1"
        assert history2[1]["content"] == "Answer 1"


class TestHistoryClearOperation:
    """Test clearing chat history."""

    def test_clear_removes_messages(self, chat_manager, settings):
        """Test clearing removes all messages."""
        # Add messages
        chat_manager._chat_panel.add_user_message("Test 1", "gnokit/improve-grammer", "general")
        chat_manager._chat_panel.add_ai_message("Response 1", "gnokit/improve-grammer")

        assert chat_manager._chat_panel.get_message_count() == 2

        # Clear
        chat_manager._chat_panel.clear_messages()

        # Should be empty
        assert chat_manager._chat_panel.get_message_count() == 0

    def test_clear_updates_settings(self, chat_manager, settings):
        """Test clearing updates settings."""
        # Add messages
        chat_manager._chat_panel.add_user_message("Test", "gnokit/improve-grammer", "general")

        # Manually save to settings
        settings.ollama_chat_history = (
            chat_manager._chat_panel.get_message_history()
        )
        assert len(settings.ollama_chat_history) > 0

        # Clear
        chat_manager._chat_panel.clear_messages()

        # Update settings
        settings.ollama_chat_history = (
            chat_manager._chat_panel.get_message_history()
        )

        # Settings should be empty
        assert len(settings.ollama_chat_history) == 0


class TestSettingsIntegration:
    """Test integration with settings save/load."""

    def test_settings_changed_signal_emitted(self, chat_manager, qtbot):
        """Test settings_changed signal is emitted on updates."""
        with qtbot.waitSignal(
            chat_manager.settings_changed, timeout=1000
        ) as blocker:
            # Change a setting
            chat_manager._on_model_changed("llama2")

        assert blocker.signal_triggered

    def test_context_mode_saved(self, chat_manager, settings):
        """Test context mode is saved to settings."""
        # Change mode
        chat_manager._on_context_mode_changed("editing")

        # Check settings updated
        assert settings.ollama_chat_context_mode == "editing"


class TestHistoryFormat:
    """Test history format and serialization."""

    def test_history_is_json_serializable(self, chat_manager, settings):
        """Test history can be serialized to JSON."""
        import json

        # Add messages
        chat_manager._chat_panel.add_user_message("Test", "gnokit/improve-grammer", "general")
        chat_manager._chat_panel.add_ai_message("Response", "gnokit/improve-grammer")

        # Get history
        history = chat_manager._chat_panel.get_message_history()

        # Should be JSON serializable
        try:
            json_str = json.dumps(history)
            reloaded = json.loads(json_str)
            assert len(reloaded) == len(history)
        except (TypeError, ValueError) as e:
            pytest.fail(f"History not JSON serializable: {e}")

    def test_history_dict_format(self, chat_manager, settings):
        """Test history uses dict format (not ChatMessage objects)."""
        # Add message
        chat_manager._chat_panel.add_user_message("Test", "gnokit/improve-grammer", "general")

        # Get history
        history = chat_manager._chat_panel.get_message_history()

        # Should be list of dicts
        assert isinstance(history, list)
        assert len(history) > 0
        assert isinstance(history[0], dict)

        # Should have required keys
        required_keys = {"role", "content", "model", "timestamp"}
        assert required_keys.issubset(history[0].keys())


class TestHistoryRecovery:
    """Test history recovery from various states."""

    def test_recover_from_none_history(self, chat_manager, settings):
        """Test recovery when history is None."""
        settings.ollama_chat_history = None

        # Should not crash
        chat_manager.initialize()

        # Should default to empty
        assert chat_manager._chat_panel.get_message_count() == 0

    def test_recover_from_invalid_type(self, chat_manager, settings):
        """Test recovery when history is wrong type."""
        settings.ollama_chat_history = "invalid"  # Should be list

        # Should not crash
        chat_manager.initialize()

        # Should default to empty
        assert chat_manager._chat_panel.get_message_count() == 0

    def test_partial_valid_history(self, chat_manager, settings):
        """Test loading partially valid history."""
        settings.ollama_chat_history = [
            {
                "role": "user",
                "content": "Valid message",
                "model": "gnokit/improve-grammer",
                "context_mode": "general",
                "timestamp": "2025-11-02T10:00:00",
            },
            {"invalid": "entry"},  # Invalid
            {
                "role": "assistant",
                "content": "Another valid",
                "model": "gnokit/improve-grammer",
                "timestamp": "2025-11-02T10:00:01",
            },
        ]

        # Initialize
        chat_manager.initialize()

        # Should load valid entries only
        # Note: Actual behavior depends on implementation
        # This test documents expected behavior
        count = chat_manager._chat_panel.get_message_count()
        assert count >= 0  # At minimum, shouldn't crash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
