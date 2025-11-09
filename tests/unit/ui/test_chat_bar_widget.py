"""
Tests for ui.chat_bar_widget module.

Tests chat bar widget for AI interaction including:
- Widget initialization and UI setup
- Signals (message_sent, clear_requested, cancel_requested, model_changed, context_mode_changed)
- Input field handling and send button state
- Model selector operations
- Context mode selector operations
- Processing state management
- Button visibility and enabled states
"""

import pytest
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QComboBox, QLineEdit, QPushButton

from asciidoc_artisan.ui.chat_bar_widget import ChatBarWidget


@pytest.mark.unit
class TestChatBarWidgetInitialization:
    """Test ChatBarWidget initialization."""

    def test_initialization_without_parent(self, qapp):
        """Test widget initializes without parent."""
        widget = ChatBarWidget()

        assert widget is not None

    def test_initialization_with_parent(self, qapp):
        """Test widget initializes with parent."""
        from PySide6.QtWidgets import QWidget

        parent = QWidget()
        widget = ChatBarWidget(parent)

        assert widget.parent() is parent

    def test_has_input_field(self, qapp):
        """Test widget has input field."""
        widget = ChatBarWidget()

        input_field = widget._input_field
        assert isinstance(input_field, QLineEdit)
        assert "Ask AI" in input_field.placeholderText()

    def test_has_send_button(self, qapp):
        """Test widget has send button."""
        widget = ChatBarWidget()

        send_button = widget._send_button
        assert isinstance(send_button, QPushButton)
        assert not send_button.isEnabled()  # Disabled initially

    def test_has_model_selector(self, qapp):
        """Test widget has model selector."""
        widget = ChatBarWidget()

        model_selector = widget._model_selector
        assert isinstance(model_selector, QComboBox)

    def test_has_context_selector(self, qapp):
        """Test widget has context selector."""
        widget = ChatBarWidget()

        context_selector = widget._context_selector
        assert isinstance(context_selector, QComboBox)
        assert context_selector.count() == 4  # Four context modes

    def test_context_selector_items(self, qapp):
        """Test context selector has correct items."""
        widget = ChatBarWidget()

        items = [
            widget._context_selector.itemText(i)
            for i in range(widget._context_selector.count())
        ]

        assert "Document Q&A" in items
        assert "Syntax Help" in items
        assert "General Chat" in items
        assert "Editing Suggestions" in items

    def test_has_clear_button(self, qapp):
        """Test widget has clear button."""
        widget = ChatBarWidget()

        clear_button = widget._clear_button
        assert isinstance(clear_button, QPushButton)
        assert "Clear" in clear_button.text()

    def test_has_scan_models_button(self, qapp):
        """Test widget has scan models button."""
        widget = ChatBarWidget()

        scan_button = widget._scan_models_button
        assert isinstance(scan_button, QPushButton)
        assert "Scan" in scan_button.text()

    def test_has_cancel_button_hidden(self, qapp):
        """Test widget has cancel button hidden by default."""
        widget = ChatBarWidget()

        cancel_button = widget._cancel_button
        assert isinstance(cancel_button, QPushButton)
        assert not cancel_button.isVisible()  # Hidden initially


@pytest.mark.unit
class TestSignals:
    """Test ChatBarWidget signals."""

    def test_message_sent_signal_exists(self, qapp):
        """Test message_sent signal exists."""
        widget = ChatBarWidget()

        assert hasattr(widget, "message_sent")

    def test_clear_requested_signal_exists(self, qapp):
        """Test clear_requested signal exists."""
        widget = ChatBarWidget()

        assert hasattr(widget, "clear_requested")

    def test_cancel_requested_signal_exists(self, qapp):
        """Test cancel_requested signal exists."""
        widget = ChatBarWidget()

        assert hasattr(widget, "cancel_requested")

    def test_model_changed_signal_exists(self, qapp):
        """Test model_changed signal exists."""
        widget = ChatBarWidget()

        assert hasattr(widget, "model_changed")

    def test_context_mode_changed_signal_exists(self, qapp):
        """Test context_mode_changed signal exists."""
        widget = ChatBarWidget()

        assert hasattr(widget, "context_mode_changed")

    def test_scan_models_requested_signal_exists(self, qapp):
        """Test scan_models_requested signal exists."""
        widget = ChatBarWidget()

        assert hasattr(widget, "scan_models_requested")


@pytest.mark.unit
class TestInputFieldHandling:
    """Test input field handling."""

    def test_input_field_text_changes_enable_send_button(self, qapp):
        """Test entering text enables send button."""
        widget = ChatBarWidget()

        assert not widget._send_button.isEnabled()

        widget._input_field.setText("Hello AI")

        assert widget._send_button.isEnabled()

    def test_input_field_empty_disables_send_button(self, qapp):
        """Test empty text disables send button."""
        widget = ChatBarWidget()

        widget._input_field.setText("Hello")
        assert widget._send_button.isEnabled()

        widget._input_field.setText("")

        assert not widget._send_button.isEnabled()

    def test_input_field_whitespace_disables_send_button(self, qapp):
        """Test whitespace-only text disables send button."""
        widget = ChatBarWidget()

        widget._input_field.setText("   ")

        assert not widget._send_button.isEnabled()

    def test_clear_input(self, qapp):
        """Test clear_input method."""
        widget = ChatBarWidget()

        widget._input_field.setText("Some text")
        widget.clear_input()

        assert widget._input_field.text() == ""


@pytest.mark.unit
class TestSendMessage:
    """Test sending messages."""

    def test_send_button_emits_message_sent(self, qapp):
        """Test clicking send button emits message_sent signal."""
        widget = ChatBarWidget()
        widget.set_models(["model1"])

        spy = QSignalSpy(widget.message_sent)

        widget._input_field.setText("Test message")
        widget._send_button.click()

        assert spy.count() == 1
        # Access signal arguments from first emission
        signal_args = spy.at(0)
        assert signal_args[0] == "Test message"
        assert signal_args[1] == "model1"

    def test_enter_key_emits_message_sent(self, qapp):
        """Test pressing Enter emits message_sent signal."""
        widget = ChatBarWidget()
        widget.set_models(["model1"])

        spy = QSignalSpy(widget.message_sent)

        widget._input_field.setText("Test message")
        widget._input_field.returnPressed.emit()

        assert spy.count() == 1

    def test_send_clears_input_field(self, qapp):
        """Test sending message clears input field."""
        widget = ChatBarWidget()
        widget.set_models(["model1"])

        widget._input_field.setText("Test message")
        widget._send_button.click()

        assert widget._input_field.text() == ""

    def test_send_empty_message_does_nothing(self, qapp):
        """Test sending empty message does nothing."""
        widget = ChatBarWidget()

        spy = QSignalSpy(widget.message_sent)

        widget._input_field.setText("")
        widget._send_button.click()

        assert spy.count() == 0

    def test_send_whitespace_message_does_nothing(self, qapp):
        """Test sending whitespace-only message does nothing."""
        widget = ChatBarWidget()

        spy = QSignalSpy(widget.message_sent)

        widget._input_field.setText("   ")
        widget._send_button.click()

        assert spy.count() == 0

    def test_send_includes_context_mode(self, qapp):
        """Test message_sent includes context mode."""
        widget = ChatBarWidget()
        widget.set_models(["model1"])
        widget.set_context_mode("syntax")

        spy = QSignalSpy(widget.message_sent)

        widget._input_field.setText("Test")
        widget._send_button.click()

        assert spy.count() == 1
        signal_args = spy.at(0)
        assert signal_args[2] == "syntax"


@pytest.mark.unit
class TestModelSelector:
    """Test model selector operations."""

    def test_set_models(self, qapp):
        """Test setting available models."""
        widget = ChatBarWidget()

        widget.set_models(["model1", "model2", "model3"])

        assert widget._model_selector.count() == 3
        assert widget._model_selector.itemText(0) == "model1"
        assert widget._model_selector.itemText(1) == "model2"
        assert widget._model_selector.itemText(2) == "model3"

    def test_set_models_clears_previous(self, qapp):
        """Test set_models clears previous models."""
        widget = ChatBarWidget()

        widget.set_models(["model1", "model2"])
        widget.set_models(["model3"])

        assert widget._model_selector.count() == 1
        assert widget._model_selector.itemText(0) == "model3"

    def test_set_models_empty_list(self, qapp):
        """Test set_models with empty list."""
        widget = ChatBarWidget()

        widget.set_models([])

        assert widget._model_selector.count() == 0

    def test_set_model(self, qapp):
        """Test setting current model."""
        widget = ChatBarWidget()
        widget.set_models(["model1", "model2", "model3"])

        widget.set_model("model2")

        assert widget._model_selector.currentText() == "model2"

    def test_set_model_not_in_list(self, qapp):
        """Test setting model not in list."""
        widget = ChatBarWidget()
        widget.set_models(["model1", "model2"])

        # Should not crash
        widget.set_model("model3")

        # Should still have original selection
        assert widget._model_selector.currentText() in ["model1", "model2", ""]

    def test_get_current_model(self, qapp):
        """Test getting current model."""
        widget = ChatBarWidget()
        widget.set_models(["model1", "model2"])
        widget.set_model("model2")

        model = widget.get_current_model()

        assert model == "model2"

    def test_model_changed_signal(self, qapp):
        """Test model_changed signal emitted."""
        widget = ChatBarWidget()
        widget.set_models(["model1", "model2"])

        spy = QSignalSpy(widget.model_changed)

        widget._model_selector.setCurrentText("model2")

        assert spy.count() == 1
        signal_args = spy.at(0)
        assert signal_args[0] == "model2"


@pytest.mark.unit
class TestContextModeSelector:
    """Test context mode selector operations."""

    def test_set_context_mode_document(self, qapp):
        """Test setting context mode to document."""
        widget = ChatBarWidget()

        widget.set_context_mode("document")

        assert widget._context_selector.currentIndex() == 0
        assert widget.get_current_context_mode() == "document"

    def test_set_context_mode_syntax(self, qapp):
        """Test setting context mode to syntax."""
        widget = ChatBarWidget()

        widget.set_context_mode("syntax")

        assert widget._context_selector.currentIndex() == 1
        assert widget.get_current_context_mode() == "syntax"

    def test_set_context_mode_general(self, qapp):
        """Test setting context mode to general."""
        widget = ChatBarWidget()

        widget.set_context_mode("general")

        assert widget._context_selector.currentIndex() == 2
        assert widget.get_current_context_mode() == "general"

    def test_set_context_mode_editing(self, qapp):
        """Test setting context mode to editing."""
        widget = ChatBarWidget()

        widget.set_context_mode("editing")

        assert widget._context_selector.currentIndex() == 3
        assert widget.get_current_context_mode() == "editing"

    def test_set_context_mode_invalid(self, qapp):
        """Test setting invalid context mode defaults to document."""
        widget = ChatBarWidget()

        widget.set_context_mode("invalid")

        assert widget._context_selector.currentIndex() == 0
        assert widget.get_current_context_mode() == "document"

    def test_get_current_context_mode(self, qapp):
        """Test getting current context mode."""
        widget = ChatBarWidget()

        widget._context_selector.setCurrentIndex(2)
        mode = widget.get_current_context_mode()

        assert mode == "general"

    def test_context_mode_changed_signal(self, qapp):
        """Test context_mode_changed signal emitted."""
        widget = ChatBarWidget()

        spy = QSignalSpy(widget.context_mode_changed)

        widget._context_selector.setCurrentIndex(1)

        assert spy.count() == 1
        signal_args = spy.at(0)
        assert signal_args[0] == "syntax"


@pytest.mark.unit
class TestProcessingState:
    """Test processing state management."""

    def test_set_processing_true_disables_input(self, qapp):
        """Test set_processing(True) disables input field."""
        widget = ChatBarWidget()

        widget.set_processing(True)

        assert not widget._input_field.isEnabled()

    def test_set_processing_true_disables_selectors(self, qapp):
        """Test set_processing(True) disables selectors."""
        widget = ChatBarWidget()

        widget.set_processing(True)

        assert not widget._model_selector.isEnabled()
        assert not widget._context_selector.isEnabled()

    def test_set_processing_true_hides_send_button(self, qapp):
        """Test set_processing(True) hides send button."""
        widget = ChatBarWidget()

        widget.set_processing(True)

        assert not widget._send_button.isVisible()

    def test_set_processing_true_shows_cancel_button(self, qapp):
        """Test set_processing(True) shows cancel button."""
        widget = ChatBarWidget()

        # Show widget and process events to ensure visibility updates
        widget.show()
        qapp.processEvents()

        widget.set_processing(True)
        qapp.processEvents()

        assert widget._cancel_button.isVisible()

    def test_set_processing_true_changes_placeholder(self, qapp):
        """Test set_processing(True) changes placeholder text."""
        widget = ChatBarWidget()

        widget.set_processing(True)

        assert "thinking" in widget._input_field.placeholderText().lower()

    def test_set_processing_false_enables_input(self, qapp):
        """Test set_processing(False) enables input field."""
        widget = ChatBarWidget()

        widget.set_processing(True)
        widget.set_processing(False)

        assert widget._input_field.isEnabled()

    def test_set_processing_false_enables_selectors(self, qapp):
        """Test set_processing(False) enables selectors."""
        widget = ChatBarWidget()

        widget.set_processing(True)
        widget.set_processing(False)

        assert widget._model_selector.isEnabled()
        assert widget._context_selector.isEnabled()

    def test_set_processing_false_shows_send_button(self, qapp):
        """Test set_processing(False) shows send button."""
        widget = ChatBarWidget()

        # Show widget and process events to ensure visibility updates
        widget.show()
        qapp.processEvents()

        widget.set_processing(True)
        qapp.processEvents()
        widget.set_processing(False)
        qapp.processEvents()

        assert widget._send_button.isVisible()

    def test_set_processing_false_hides_cancel_button(self, qapp):
        """Test set_processing(False) hides cancel button."""
        widget = ChatBarWidget()

        widget.set_processing(True)
        widget.set_processing(False)

        assert not widget._cancel_button.isVisible()

    def test_set_processing_false_restores_placeholder(self, qapp):
        """Test set_processing(False) restores placeholder text."""
        widget = ChatBarWidget()

        widget.set_processing(True)
        widget.set_processing(False)

        assert "Ask AI" in widget._input_field.placeholderText()


@pytest.mark.unit
class TestButtons:
    """Test button operations."""

    def test_clear_button_emits_signal(self, qapp):
        """Test clear button emits clear_requested signal."""
        widget = ChatBarWidget()

        spy = QSignalSpy(widget.clear_requested)

        widget._clear_button.click()

        assert spy.count() == 1

    def test_cancel_button_emits_signal(self, qapp):
        """Test cancel button emits cancel_requested signal."""
        widget = ChatBarWidget()

        spy = QSignalSpy(widget.cancel_requested)

        widget._cancel_button.click()

        assert spy.count() == 1

    def test_scan_models_button_emits_signal(self, qapp):
        """Test scan models button emits scan_models_requested signal."""
        widget = ChatBarWidget()

        spy = QSignalSpy(widget.scan_models_requested)

        widget._scan_models_button.click()

        assert spy.count() == 1

    def test_set_scan_models_visible_true(self, qapp):
        """Test showing scan models button."""
        widget = ChatBarWidget()

        # Show widget and process events to ensure visibility updates
        widget.show()
        qapp.processEvents()

        widget.set_scan_models_visible(True)
        qapp.processEvents()

        assert widget._scan_models_button.isVisible()

    def test_set_scan_models_visible_false(self, qapp):
        """Test hiding scan models button."""
        widget = ChatBarWidget()

        widget.set_scan_models_visible(False)

        assert not widget._scan_models_button.isVisible()


@pytest.mark.unit
class TestEnabledState:
    """Test enabled state management."""

    def test_set_enabled_state_true(self, qapp):
        """Test set_enabled_state(True) enables controls."""
        widget = ChatBarWidget()

        widget.set_enabled_state(False)
        widget.set_enabled_state(True)

        assert widget._input_field.isEnabled()
        assert widget._model_selector.isEnabled()
        assert widget._context_selector.isEnabled()
        assert widget._clear_button.isEnabled()

    def test_set_enabled_state_false(self, qapp):
        """Test set_enabled_state(False) disables controls."""
        widget = ChatBarWidget()

        widget.set_enabled_state(False)

        assert not widget._input_field.isEnabled()
        assert not widget._model_selector.isEnabled()
        assert not widget._context_selector.isEnabled()
        assert not widget._clear_button.isEnabled()

    def test_set_enabled_state_respects_text_for_send_button(self, qapp):
        """Test set_enabled_state respects text state for send button."""
        widget = ChatBarWidget()

        widget._input_field.setText("Text")
        widget.set_enabled_state(True)

        assert widget._send_button.isEnabled()

        widget._input_field.clear()
        widget.set_enabled_state(True)

        assert not widget._send_button.isEnabled()
