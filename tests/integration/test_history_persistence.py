"""
Integration test for Chat History Persistence (v1.7.0).

Tests that chat history is properly saved and loaded across sessions.
"""

import time

import pytest

from asciidoc_artisan.core import Settings
from asciidoc_artisan.core.models import ChatMessage
from asciidoc_artisan.ui.chat_bar_widget import ChatBarWidget
from asciidoc_artisan.ui.chat_manager import ChatManager
from asciidoc_artisan.ui.chat_panel_widget import ChatPanelWidget


@pytest.fixture
def settings():
    """Create fresh settings."""
    s = Settings()
    s.ollama_enabled = True
    s.ollama_model = "phi3:mini"
    s.ollama_chat_enabled = True
    s.ollama_chat_history = []
    s.ollama_chat_max_history = 100
    s.ollama_chat_context_mode = "general"
    s.ollama_chat_send_document = False
    return s


@pytest.fixture
def chat_components(qtbot, settings):
    """Create chat components."""
    bar = ChatBarWidget()
    panel = ChatPanelWidget()
    manager = ChatManager(bar, panel, settings)
    qtbot.addWidget(bar)
    qtbot.addWidget(panel)
    return manager, bar, panel, settings


class TestHistoryPersistence:
    """Test history persists across manager recreations."""

    def test_history_saves_and_loads(self, qtbot, settings):
        """Test complete save/load cycle."""
        # === Session 1: Create and populate history ===
        bar1 = ChatBarWidget()
        panel1 = ChatPanelWidget()
        manager1 = ChatManager(bar1, panel1, settings)
        qtbot.addWidget(bar1)
        qtbot.addWidget(panel1)

        # Initialize
        manager1.initialize()

        # Add messages directly to panel
        msg1 = ChatMessage(
            role="user",
            content="Hello",
            model="phi3:mini",
            context_mode="general",
            timestamp=time.time(),
        )
        msg2 = ChatMessage(
            role="assistant",
            content="Hi there!",
            model="phi3:mini",
            context_mode="general",
            timestamp=time.time(),
        )

        panel1.add_message(msg1)
        panel1.add_message(msg2)

        # Verify messages added
        assert panel1.get_message_count() == 2

        # Save history
        manager1._save_chat_history()

        # Verify saved to settings
        assert len(settings.ollama_chat_history) == 2

        # === Session 2: Reload history ===
        bar2 = ChatBarWidget()
        panel2 = ChatPanelWidget()
        manager2 = ChatManager(bar2, panel2, settings)
        qtbot.addWidget(bar2)
        qtbot.addWidget(panel2)

        # Initialize (loads history)
        manager2.initialize()

        # Verify history restored
        assert panel2.get_message_count() == 2

        # Verify content matches
        messages = panel2.get_messages()
        assert messages[0].content == "Hello"
        assert messages[1].content == "Hi there!"

    def test_empty_history_loads_correctly(self, chat_components):
        """Test loading with empty history."""
        manager, bar, panel, settings = chat_components

        # Start with empty history
        settings.ollama_chat_history = []

        # Initialize
        manager.initialize()

        # Should have no messages
        assert panel.get_message_count() == 0

    def test_history_max_limit_enforced(self, chat_components):
        """Test history respects max limit."""
        manager, bar, panel, settings = chat_components
        settings.ollama_chat_max_history = 5

        # Add 10 messages
        for i in range(10):
            msg = ChatMessage(
                role="user",
                content=f"Message {i}",
                model="phi3:mini",
                context_mode="general",
                timestamp=time.time(),
            )
            panel.add_message(msg)

        # Save history
        manager._save_chat_history()

        # Should only keep last 5
        assert len(settings.ollama_chat_history) <= 5

    def test_corrupted_history_handled(self, qtbot, settings):
        """Test corrupted history doesn't crash."""
        # Set corrupted history
        settings.ollama_chat_history = [
            {"invalid": "data"},
            None,
            "not a dict",
        ]

        bar = ChatBarWidget()
        panel = ChatPanelWidget()
        manager = ChatManager(bar, panel, settings)
        qtbot.addWidget(bar)
        qtbot.addWidget(panel)

        # Should not crash
        manager.initialize()

        # Should handle gracefully (likely no messages loaded)
        assert panel.get_message_count() >= 0

    def test_history_includes_all_message_types(self, chat_components):
        """Test history saves both user and assistant messages."""
        manager, bar, panel, settings = chat_components
        manager.initialize()

        # Add user message
        user_msg = ChatMessage(
            role="user",
            content="User question",
            model="phi3:mini",
            context_mode="document",
            timestamp=time.time(),
        )
        panel.add_message(user_msg)

        # Add assistant message
        ai_msg = ChatMessage(
            role="assistant",
            content="AI response",
            model="phi3:mini",
            context_mode="document",
            timestamp=time.time(),
        )
        panel.add_message(ai_msg)

        # Save
        manager._save_chat_history()

        # Verify both saved
        assert len(settings.ollama_chat_history) == 2
        assert settings.ollama_chat_history[0]["role"] == "user"
        assert settings.ollama_chat_history[1]["role"] == "assistant"

    def test_timestamp_preserved(self, chat_components):
        """Test timestamps are preserved across save/load."""
        manager, bar, panel, settings = chat_components
        manager.initialize()

        # Add message with specific timestamp
        original_time = time.time()
        msg = ChatMessage(
            role="user",
            content="Test",
            model="phi3:mini",
            context_mode="general",
            timestamp=original_time,
        )
        panel.add_message(msg)

        # Save
        manager._save_chat_history()

        # Timestamp should be in settings (as float)
        assert len(settings.ollama_chat_history) == 1
        saved_time = settings.ollama_chat_history[0]["timestamp"]
        assert isinstance(saved_time, float)
        assert abs(saved_time - original_time) < 0.1  # Within 100ms

    def test_context_mode_preserved(self, chat_components):
        """Test context mode is preserved."""
        manager, bar, panel, settings = chat_components
        manager.initialize()

        # Add message with specific context mode
        msg = ChatMessage(
            role="user",
            content="Test",
            model="phi3:mini",
            context_mode="editing",
            timestamp=time.time(),
        )
        panel.add_message(msg)

        # Save
        manager._save_chat_history()

        # Context mode should be preserved
        assert settings.ollama_chat_history[0]["context_mode"] == "editing"

    def test_model_preserved(self, chat_components):
        """Test model name is preserved."""
        manager, bar, panel, settings = chat_components
        manager.initialize()

        # Add message with specific model
        msg = ChatMessage(
            role="user",
            content="Test",
            model="llama2",
            context_mode="general",
            timestamp=time.time(),
        )
        panel.add_message(msg)

        # Save
        manager._save_chat_history()

        # Model should be preserved
        assert settings.ollama_chat_history[0]["model"] == "llama2"


class TestClearHistory:
    """Test clearing history."""

    def test_clear_removes_all_messages(self, chat_components):
        """Test clearing removes all messages."""
        manager, bar, panel, settings = chat_components
        manager.initialize()

        # Add messages
        for i in range(3):
            msg = ChatMessage(
                role="user",
                content=f"Message {i}",
                model="phi3:mini",
                context_mode="general",
                timestamp=time.time(),
            )
            panel.add_message(msg)

        assert panel.get_message_count() == 3

        # Clear
        panel.clear_messages()

        # Should be empty
        assert panel.get_message_count() == 0

    def test_clear_and_save_empties_settings(self, chat_components):
        """Test clearing and saving empties settings."""
        manager, bar, panel, settings = chat_components
        manager.initialize()

        # Add message
        msg = ChatMessage(
            role="user",
            content="Test",
            model="phi3:mini",
            context_mode="general",
            timestamp=time.time(),
        )
        panel.add_message(msg)

        # Save
        manager._save_chat_history()
        assert len(settings.ollama_chat_history) > 0

        # Clear and save again
        panel.clear_messages()
        manager._save_chat_history()

        # Settings should be empty
        assert len(settings.ollama_chat_history) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
