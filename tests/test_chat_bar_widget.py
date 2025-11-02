"""
Tests for Chat Bar Widget.

Tests the ChatBarWidget class which provides the user input interface
for Ollama AI chat.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from asciidoc_artisan.ui.chat_bar_widget import ChatBarWidget


@pytest.fixture
def app(qapp):
    """Provide QApplication instance."""
    return qapp


@pytest.fixture
def chat_bar(qtbot):
    """Create a chat bar widget for testing."""
    widget = ChatBarWidget()
    qtbot.addWidget(widget)
    return widget


class TestChatBarWidgetInitialization:
    """Test widget initialization."""

    def test_widget_creation(self, chat_bar):
        """Test widget can be created."""
        assert chat_bar is not None
        assert isinstance(chat_bar, ChatBarWidget)

    def test_has_input_field(self, chat_bar):
        """Test widget has input field."""
        assert hasattr(chat_bar, "_input_field")
        assert chat_bar._input_field is not None

    def test_has_model_selector(self, chat_bar):
        """Test widget has model selector."""
        assert hasattr(chat_bar, "_model_selector")
        assert chat_bar._model_selector is not None

    def test_has_context_selector(self, chat_bar):
        """Test widget has context mode selector."""
        assert hasattr(chat_bar, "_context_selector")
        assert chat_bar._context_selector is not None

    def test_has_send_button(self, chat_bar):
        """Test widget has send button."""
        assert hasattr(chat_bar, "_send_button")
        assert chat_bar._send_button is not None

    def test_has_clear_button(self, chat_bar):
        """Test widget has clear button."""
        assert hasattr(chat_bar, "_clear_button")
        assert chat_bar._clear_button is not None

    def test_has_cancel_button(self, chat_bar):
        """Test widget has cancel button."""
        assert hasattr(chat_bar, "_cancel_button")
        assert chat_bar._cancel_button is not None

    def test_initial_visibility(self, chat_bar):
        """Test initial visibility state."""
        # Should be hidden by default until models are set
        assert not chat_bar.isVisible() or chat_bar._model_selector.count() == 0


class TestChatBarWidgetSignals:
    """Test widget signals."""

    def test_has_message_sent_signal(self, chat_bar):
        """Test widget has message_sent signal."""
        assert hasattr(chat_bar, "message_sent")

    def test_has_clear_requested_signal(self, chat_bar):
        """Test widget has clear_requested signal."""
        assert hasattr(chat_bar, "clear_requested")

    def test_has_cancel_requested_signal(self, chat_bar):
        """Test widget has cancel_requested signal."""
        assert hasattr(chat_bar, "cancel_requested")

    def test_has_model_changed_signal(self, chat_bar):
        """Test widget has model_changed signal."""
        assert hasattr(chat_bar, "model_changed")

    def test_has_context_mode_changed_signal(self, chat_bar):
        """Test widget has context_mode_changed signal."""
        assert hasattr(chat_bar, "context_mode_changed")


class TestChatBarWidgetModelManagement:
    """Test model management functionality."""

    def test_set_models(self, chat_bar):
        """Test setting available models."""
        models = ["phi3:mini", "llama2", "mistral"]
        chat_bar.set_models(models)

        assert chat_bar._model_selector.count() == len(models)
        for i, model in enumerate(models):
            assert chat_bar._model_selector.itemText(i) == model

    def test_set_model_selects_current(self, chat_bar):
        """Test setting current model."""
        models = ["phi3:mini", "llama2", "mistral"]
        chat_bar.set_models(models)
        chat_bar.set_model("llama2")

        assert chat_bar.get_model() == "llama2"
        assert chat_bar._model_selector.currentText() == "llama2"

    def test_get_model_returns_current(self, chat_bar):
        """Test getting current model."""
        models = ["phi3:mini"]
        chat_bar.set_models(models)
        chat_bar.set_model("phi3:mini")

        assert chat_bar.get_model() == "phi3:mini"

    def test_model_changed_signal_emits(self, chat_bar, qtbot):
        """Test model_changed signal emits when model changes."""
        models = ["phi3:mini", "llama2"]
        chat_bar.set_models(models)

        with qtbot.waitSignal(chat_bar.model_changed, timeout=1000) as blocker:
            chat_bar._model_selector.setCurrentIndex(1)

        assert blocker.args[0] == "llama2"


class TestChatBarWidgetContextModes:
    """Test context mode functionality."""

    def test_has_four_context_modes(self, chat_bar):
        """Test widget has all four context modes."""
        # Context modes should be: document, syntax, general, editing
        assert chat_bar._context_selector.count() == 4

    def test_default_context_mode(self, chat_bar):
        """Test default context mode is document."""
        # Default should be "document"
        context = chat_bar.get_context_mode()
        assert context in ["document", "syntax", "general", "editing"]

    def test_set_context_mode(self, chat_bar):
        """Test setting context mode."""
        modes = ["document", "syntax", "general", "editing"]
        for mode in modes:
            chat_bar.set_context_mode(mode)
            assert chat_bar.get_context_mode() == mode

    def test_context_mode_changed_signal(self, chat_bar, qtbot):
        """Test context_mode_changed signal emits."""
        # Find index of "syntax" mode
        for i in range(chat_bar._context_selector.count()):
            if "syntax" in chat_bar._context_selector.itemText(i).lower():
                with qtbot.waitSignal(
                    chat_bar.context_mode_changed, timeout=1000
                ) as blocker:
                    chat_bar._context_selector.setCurrentIndex(i)
                break


class TestChatBarWidgetMessageInput:
    """Test message input functionality."""

    def test_input_field_accepts_text(self, chat_bar, qtbot):
        """Test input field accepts text."""
        test_message = "Hello, AI!"
        qtbot.keyClicks(chat_bar._input_field, test_message)
        assert chat_bar._input_field.text() == test_message

    def test_get_message_returns_input_text(self, chat_bar, qtbot):
        """Test get_message returns input field text."""
        test_message = "Test message"
        qtbot.keyClicks(chat_bar._input_field, test_message)
        assert chat_bar.get_message() == test_message

    def test_clear_input_clears_field(self, chat_bar, qtbot):
        """Test clear_input clears the input field."""
        qtbot.keyClicks(chat_bar._input_field, "Some text")
        chat_bar.clear_input()
        assert chat_bar._input_field.text() == ""

    def test_send_button_click_emits_signal(self, chat_bar, qtbot):
        """Test clicking send button emits message_sent signal."""
        models = ["phi3:mini"]
        chat_bar.set_models(models)
        chat_bar.set_model("phi3:mini")

        test_message = "Test message"
        qtbot.keyClicks(chat_bar._input_field, test_message)

        with qtbot.waitSignal(chat_bar.message_sent, timeout=1000) as blocker:
            qtbot.mouseClick(chat_bar._send_button, Qt.LeftButton)

        message, model, context_mode = blocker.args
        assert message == test_message
        assert model == "phi3:mini"

    def test_enter_key_sends_message(self, chat_bar, qtbot):
        """Test pressing Enter sends message."""
        models = ["phi3:mini"]
        chat_bar.set_models(models)
        chat_bar.set_model("phi3:mini")

        test_message = "Test message"
        chat_bar._input_field.setText(test_message)

        with qtbot.waitSignal(chat_bar.message_sent, timeout=1000) as blocker:
            qtbot.keyPress(chat_bar._input_field, Qt.Key_Return)

        message, model, context_mode = blocker.args
        assert message == test_message

    def test_empty_message_not_sent(self, chat_bar, qtbot):
        """Test empty messages are not sent."""
        models = ["phi3:mini"]
        chat_bar.set_models(models)
        chat_bar.set_model("phi3:mini")

        chat_bar._input_field.clear()

        # Try to send empty message - should not emit signal
        with qtbot.assertNotEmitted(chat_bar.message_sent):
            qtbot.mouseClick(chat_bar._send_button, Qt.LeftButton)


class TestChatBarWidgetButtons:
    """Test button functionality."""

    def test_clear_button_emits_signal(self, chat_bar, qtbot):
        """Test clear button emits clear_requested signal."""
        with qtbot.waitSignal(chat_bar.clear_requested, timeout=1000):
            qtbot.mouseClick(chat_bar._clear_button, Qt.LeftButton)

    def test_cancel_button_emits_signal(self, chat_bar, qtbot):
        """Test cancel button emits cancel_requested signal."""
        with qtbot.waitSignal(chat_bar.cancel_requested, timeout=1000):
            qtbot.mouseClick(chat_bar._cancel_button, Qt.LeftButton)

    def test_cancel_button_visibility_control(self, chat_bar):
        """Test cancel button can be shown/hidden."""
        chat_bar.set_processing(True)
        assert chat_bar._cancel_button.isVisible()

        chat_bar.set_processing(False)
        assert not chat_bar._cancel_button.isVisible()


class TestChatBarWidgetEnabledState:
    """Test enabled/disabled state."""

    def test_set_enabled_enables_controls(self, chat_bar):
        """Test set_enabled enables all controls."""
        chat_bar.set_enabled(True)

        assert chat_bar._input_field.isEnabled()
        assert chat_bar._send_button.isEnabled()
        assert chat_bar._model_selector.isEnabled()
        assert chat_bar._context_selector.isEnabled()

    def test_set_enabled_disables_controls(self, chat_bar):
        """Test set_enabled(False) disables controls."""
        chat_bar.set_enabled(False)

        assert not chat_bar._input_field.isEnabled()
        assert not chat_bar._send_button.isEnabled()

    def test_processing_state_disables_input(self, chat_bar):
        """Test processing state disables input but enables cancel."""
        chat_bar.set_processing(True)

        assert not chat_bar._send_button.isEnabled()
        assert chat_bar._cancel_button.isVisible()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
