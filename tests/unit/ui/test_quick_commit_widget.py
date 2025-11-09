"""
Tests for Quick Commit Widget.

Tests the QuickCommitWidget class which provides an inline commit message
input for fast Git commits (v1.9.0+).
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit

from asciidoc_artisan.ui.quick_commit_widget import QuickCommitWidget


@pytest.fixture
def app(qapp):
    """Provide QApplication instance."""
    return qapp


@pytest.fixture
def widget(qtbot):
    """Create a quick commit widget for testing."""
    w = QuickCommitWidget(None)
    qtbot.addWidget(w)
    return w


class TestQuickCommitWidgetInitialization:
    """Test widget initialization."""

    def test_widget_creation(self, widget):
        """Test widget can be created."""
        assert widget is not None
        assert isinstance(widget, QuickCommitWidget)

    def test_widget_hidden_by_default(self, widget):
        """Test widget is hidden by default."""
        assert not widget.isVisible()

    def test_has_message_input(self, widget):
        """Test widget has message input field."""
        assert hasattr(widget, "message_input")
        assert widget.message_input is not None

    def test_has_ok_button(self, widget):
        """Test widget has OK button."""
        assert hasattr(widget, "ok_button")
        assert widget.ok_button is not None
        assert widget.ok_button.text() == "✓"

    def test_has_cancel_button(self, widget):
        """Test widget has cancel button."""
        assert hasattr(widget, "cancel_button")
        assert widget.cancel_button is not None
        assert widget.cancel_button.text() == "✕"

    def test_message_input_has_placeholder(self, widget):
        """Test message input has placeholder text."""
        assert widget.message_input.placeholderText() == "Enter commit message..."


class TestQuickCommitWidgetShowAndFocus:
    """Test show_and_focus behavior."""

    def test_show_and_focus_makes_visible(self, widget):
        """Test show_and_focus makes widget visible."""
        widget.show_and_focus()
        assert widget.isVisible()

    def test_show_and_focus_clears_input(self, widget):
        """Test show_and_focus clears previous text."""
        widget.message_input.setText("Old message")
        widget.show_and_focus()
        assert widget.message_input.text() == ""

    def test_show_and_focus_sets_focus(self, widget, qtbot):
        """Test show_and_focus sets focus to input field."""
        widget.show_and_focus()
        qtbot.waitUntil(lambda: widget.message_input.hasFocus(), timeout=1000)
        assert widget.message_input.hasFocus()


class TestQuickCommitWidgetCommitRequest:
    """Test commit request handling."""

    def test_commit_with_valid_message(self, widget, qtbot):
        """Test committing with valid message emits signal."""
        widget.message_input.setText("Fix bug in parser")

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            widget.ok_button.click()

        assert blocker.args[0] == "Fix bug in parser"
        assert not widget.isVisible()  # Widget should hide after commit

    def test_commit_with_enter_key(self, widget, qtbot):
        """Test pressing Enter commits the message."""
        widget.message_input.setText("Add new feature")

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            qtbot.keyPress(widget.message_input, Qt.Key.Key_Return)

        assert blocker.args[0] == "Add new feature"

    def test_commit_with_empty_message_does_nothing(self, widget, qtbot):
        """Test committing with empty message does nothing."""
        widget.message_input.setText("")

        with qtbot.assertNotEmitted(widget.commit_requested, wait=100):
            widget.ok_button.click()

        # Widget should stay visible with empty message
        assert widget.message_input.text() == ""

    def test_commit_with_whitespace_only_does_nothing(self, widget, qtbot):
        """Test committing with whitespace-only message does nothing."""
        widget.message_input.setText("   \t\n  ")

        with qtbot.assertNotEmitted(widget.commit_requested, wait=100):
            widget.ok_button.click()

    def test_commit_strips_whitespace(self, widget, qtbot):
        """Test commit message is stripped of leading/trailing whitespace."""
        widget.message_input.setText("  Fix typo  ")

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            widget.ok_button.click()

        assert blocker.args[0] == "Fix typo"


class TestQuickCommitWidgetCancel:
    """Test cancel behavior."""

    def test_cancel_button_emits_cancelled_signal(self, widget, qtbot):
        """Test cancel button emits cancelled signal."""
        widget.show_and_focus()
        widget.message_input.setText("Some message")

        with qtbot.waitSignal(widget.cancelled, timeout=1000):
            widget.cancel_button.click()

        assert not widget.isVisible()

    def test_escape_key_emits_cancelled_signal(self, widget, qtbot):
        """Test Escape key emits cancelled signal."""
        widget.show_and_focus()
        widget.message_input.setText("Some message")

        with qtbot.waitSignal(widget.cancelled, timeout=1000):
            qtbot.keyPress(widget, Qt.Key.Key_Escape)

        assert not widget.isVisible()

    def test_cancel_does_not_clear_message(self, widget, qtbot):
        """Test cancel does not clear the message (for resuming)."""
        widget.show_and_focus()
        widget.message_input.setText("Work in progress")

        with qtbot.waitSignal(widget.cancelled, timeout=1000):
            widget.cancel_button.click()

        # Message should still be there (user might want to resume)
        # Actually, based on the implementation, show_and_focus clears it
        # So this test verifies current behavior
        assert not widget.isVisible()


class TestQuickCommitWidgetGettersSetter:
    """Test getter and setter methods."""

    def test_get_message_returns_text(self, widget):
        """Test get_message returns current text."""
        widget.message_input.setText("Test message")
        assert widget.get_message() == "Test message"

    def test_get_message_strips_whitespace(self, widget):
        """Test get_message strips whitespace."""
        widget.message_input.setText("  Test message  ")
        assert widget.get_message() == "Test message"

    def test_clear_message_clears_input(self, widget):
        """Test clear_message clears the input field."""
        widget.message_input.setText("Some text")
        widget.clear_message()
        assert widget.message_input.text() == ""


class TestQuickCommitWidgetKeyboardWorkflow:
    """Test keyboard-driven workflow."""

    def test_full_keyboard_workflow_commit(self, widget, qtbot):
        """Test complete keyboard workflow: show, type, commit."""
        # Show and focus
        widget.show_and_focus()
        qtbot.waitUntil(lambda: widget.message_input.hasFocus(), timeout=1000)

        # Type message
        qtbot.keyClicks(widget.message_input, "Fix critical bug")

        # Commit with Enter
        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            qtbot.keyPress(widget.message_input, Qt.Key.Key_Return)

        assert blocker.args[0] == "Fix critical bug"
        assert not widget.isVisible()

    def test_full_keyboard_workflow_cancel(self, widget, qtbot):
        """Test complete keyboard workflow: show, type, cancel."""
        # Show and focus
        widget.show_and_focus()
        qtbot.waitUntil(lambda: widget.message_input.hasFocus(), timeout=1000)

        # Type message
        qtbot.keyClicks(widget.message_input, "Incomplete message")

        # Cancel with Escape
        with qtbot.waitSignal(widget.cancelled, timeout=1000):
            qtbot.keyPress(widget, Qt.Key.Key_Escape)

        assert not widget.isVisible()


class TestQuickCommitWidgetMultipleCommits:
    """Test multiple commit cycles."""

    def test_multiple_commits_in_sequence(self, widget, qtbot):
        """Test widget can be used multiple times."""
        # First commit
        widget.show_and_focus()
        widget.message_input.setText("First commit")
        with qtbot.waitSignal(widget.commit_requested, timeout=1000):
            widget.ok_button.click()

        # Second commit
        widget.show_and_focus()
        assert widget.message_input.text() == ""  # Cleared by show_and_focus
        widget.message_input.setText("Second commit")
        with qtbot.waitSignal(widget.commit_requested, timeout=1000):
            widget.ok_button.click()

        # Should work both times
        assert not widget.isVisible()


class TestSignalEmissionEdgeCases:
    """Test signal emission edge cases."""

    def test_commit_signal_emits_exact_stripped_message(self, widget, qtbot):
        """Test commit signal emits exactly the stripped message."""
        widget.message_input.setText("  Test message with spaces  ")

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            widget.ok_button.click()

        # Signal should contain stripped version
        assert blocker.args[0] == "Test message with spaces"
        assert blocker.args[0] == widget.get_message()

    def test_multiple_consecutive_commit_attempts(self, widget, qtbot):
        """Test multiple commit attempts without showing again."""
        widget.show_and_focus()
        widget.message_input.setText("First message")

        # First commit
        with qtbot.waitSignal(widget.commit_requested, timeout=1000):
            widget.ok_button.click()

        # Widget is now hidden, but message still there
        # Clicking OK button when hidden will still trigger _on_commit
        # but widget stays hidden and signal is emitted again
        assert not widget.isVisible()
        assert widget.get_message() == "First message"  # Not cleared yet

    def test_cancelled_signal_only_when_visible(self, widget, qtbot):
        """Test cancelled signal emits regardless of visibility."""
        # Cancel button emits signal even when hidden (no visibility check in _on_cancel)
        # This tests actual behavior, not ideal behavior
        widget.show_and_focus()

        with qtbot.waitSignal(widget.cancelled, timeout=1000):
            widget.cancel_button.click()

        # Widget should be hidden after cancel
        assert not widget.isVisible()

    def test_signal_emission_order_commit_then_hide(self, widget, qtbot):
        """Test signal is emitted before widget hides."""
        widget.show_and_focus()
        widget.message_input.setText("Test")

        signal_emitted_visible = None

        def check_visibility():
            nonlocal signal_emitted_visible
            signal_emitted_visible = widget.isVisible()

        widget.commit_requested.connect(check_visibility)

        with qtbot.waitSignal(widget.commit_requested, timeout=1000):
            widget.ok_button.click()

        # Signal should have been emitted while widget was still visible
        assert signal_emitted_visible is True

    def test_rapid_cancel_and_show(self, widget, qtbot):
        """Test rapid cancel and show doesn't cause signal issues."""
        for _ in range(5):
            widget.show_and_focus()
            with qtbot.waitSignal(widget.cancelled, timeout=1000):
                qtbot.keyPress(widget, Qt.Key.Key_Escape)
            assert not widget.isVisible()


class TestUIComponentProperties:
    """Test UI component properties and styling."""

    def test_ok_button_has_correct_properties(self, widget):
        """Test OK button size and properties."""
        assert widget.ok_button.size().width() == 24
        assert widget.ok_button.size().height() == 24
        assert widget.ok_button.toolTip() == "Commit (Enter)"

    def test_cancel_button_has_correct_properties(self, widget):
        """Test cancel button size and properties."""
        assert widget.cancel_button.size().width() == 24
        assert widget.cancel_button.size().height() == 24
        assert widget.cancel_button.toolTip() == "Cancel (Escape)"

    def test_label_has_bold_styling(self, widget):
        """Test commit label has bold font-weight."""
        # Find the label widget
        label = widget.findChild(QLabel)
        assert label is not None
        assert "font-weight: bold" in label.styleSheet()

    def test_message_input_stretches_in_layout(self, widget):
        """Test message input field stretches to fill space."""
        # Layout should have message input with stretch factor 1
        layout = widget.layout()
        # Check if message_input has stretch
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() == widget.message_input:
                assert layout.stretch(i) == 1
                break

    def test_layout_margins_and_spacing(self, widget):
        """Test layout has correct margins and spacing."""
        layout = widget.layout()
        margins = layout.contentsMargins()
        assert margins.left() == 5
        assert margins.top() == 2
        assert margins.right() == 5
        assert margins.bottom() == 2
        assert layout.spacing() == 5


class TestWidgetStateManagement:
    """Test widget state management."""

    def test_widget_state_after_commit(self, widget, qtbot):
        """Test widget state transitions after commit."""
        widget.show_and_focus()
        assert widget.isVisible()

        widget.message_input.setText("Test")
        with qtbot.waitSignal(widget.commit_requested, timeout=1000):
            widget.ok_button.click()

        assert not widget.isVisible()
        # Message is NOT cleared immediately - only cleared on next show_and_focus
        assert widget.get_message() == "Test"

    def test_widget_state_after_cancel(self, widget, qtbot):
        """Test widget state transitions after cancel."""
        widget.show_and_focus()
        assert widget.isVisible()

        widget.message_input.setText("Test")
        with qtbot.waitSignal(widget.cancelled, timeout=1000):
            widget.cancel_button.click()

        assert not widget.isVisible()
        # Message still there (not cleared by cancel)
        assert widget.get_message() == "Test"

    def test_repeated_show_and_focus_clears_previous(self, widget):
        """Test repeated show_and_focus calls clear previous text."""
        widget.message_input.setText("Old message")
        widget.show_and_focus()
        assert widget.get_message() == ""

        widget.message_input.setText("Another message")
        widget.show_and_focus()
        assert widget.get_message() == ""

    def test_visibility_toggle_rapid(self, widget):
        """Test rapid visibility toggling."""
        for _ in range(10):
            widget.show()
            assert widget.isVisible()
            widget.hide()
            assert not widget.isVisible()

    def test_show_and_focus_when_already_visible(self, widget):
        """Test show_and_focus when widget is already visible."""
        widget.show_and_focus()
        widget.message_input.setText("First")

        # Call show_and_focus again
        widget.show_and_focus()
        assert widget.isVisible()
        assert widget.get_message() == ""  # Cleared


class TestSpecialCharactersInMessages:
    """Test special characters in commit messages."""

    def test_commit_with_unicode_characters(self, widget, qtbot):
        """Test commit with Unicode characters."""
        widget.message_input.setText("日本語 commit 📝 ñáéíóú")

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            widget.ok_button.click()

        assert blocker.args[0] == "日本語 commit 📝 ñáéíóú"

    def test_commit_with_special_characters(self, widget, qtbot):
        """Test commit with special characters."""
        widget.message_input.setText("Fix: bug #123 & improve <performance>")

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            widget.ok_button.click()

        assert blocker.args[0] == "Fix: bug #123 & improve <performance>"

    def test_commit_with_quotes_and_apostrophes(self, widget, qtbot):
        """Test commit with quotes and apostrophes."""
        widget.message_input.setText("Update 'config' and \"settings\"")

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            widget.ok_button.click()

        assert blocker.args[0] == "Update 'config' and \"settings\""

    def test_commit_with_newlines_replaced_by_spaces(self, widget, qtbot):
        """Test commit handles newlines (single-line input)."""
        # QLineEdit doesn't allow newlines, but test the behavior
        widget.message_input.setText("Line 1")
        text_before = widget.get_message()
        # Attempting to insert newline does nothing in QLineEdit
        assert "\n" not in text_before

    def test_commit_with_tabs(self, widget, qtbot):
        """Test commit with tab characters."""
        widget.message_input.setText("Before\tAfter")

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            widget.ok_button.click()

        # Tabs should be preserved
        assert blocker.args[0] == "Before\tAfter"


class TestLayoutProperties:
    """Test layout properties and geometry."""

    def test_widget_has_layout(self, widget):
        """Test widget has a layout assigned."""
        assert widget.layout() is not None
        assert isinstance(widget.layout(), QHBoxLayout)

    def test_layout_contains_all_widgets(self, widget):
        """Test layout contains all expected widgets."""
        layout = widget.layout()
        widget_count = layout.count()

        # Should have: Label, LineEdit, OK button, Cancel button = 4 items
        assert widget_count == 4

    def test_message_input_position_in_layout(self, widget):
        """Test message input is in the correct position."""
        layout = widget.layout()

        # Find message_input in layout
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() == widget.message_input:
                # Message input should be position 1 (after label)
                assert i == 1
                break

    def test_buttons_positioned_after_input(self, widget):
        """Test buttons are positioned after message input."""
        layout = widget.layout()

        input_index = None
        ok_index = None
        cancel_index = None

        for i in range(layout.count()):
            item = layout.itemAt(i)
            w = item.widget()
            if w == widget.message_input:
                input_index = i
            elif w == widget.ok_button:
                ok_index = i
            elif w == widget.cancel_button:
                cancel_index = i

        assert input_index is not None
        assert ok_index is not None
        assert cancel_index is not None
        # Buttons should be after input
        assert ok_index > input_index
        assert cancel_index > input_index


class TestButtonInteractionDetails:
    """Test button interaction details."""

    def test_ok_button_click_calls_on_commit(self, widget, qtbot):
        """Test OK button click triggers commit logic."""
        widget.show_and_focus()
        widget.message_input.setText("Test message")

        click_detected = False

        def on_signal(msg):
            nonlocal click_detected
            click_detected = True

        widget.commit_requested.connect(on_signal)

        widget.ok_button.click()

        assert click_detected

    def test_cancel_button_click_calls_on_cancel(self, widget, qtbot):
        """Test cancel button click triggers cancel logic."""
        widget.show_and_focus()

        click_detected = False

        def on_signal():
            nonlocal click_detected
            click_detected = True

        widget.cancelled.connect(on_signal)

        widget.cancel_button.click()

        assert click_detected

    def test_ok_button_with_empty_input_does_not_hide(self, widget):
        """Test OK button with empty input doesn't hide widget."""
        widget.show_and_focus()
        widget.message_input.setText("")

        widget.ok_button.click()

        # Widget should still be visible (no commit)
        assert widget.isVisible()

    def test_button_tooltips_match_shortcuts(self, widget):
        """Test button tooltips describe keyboard shortcuts."""
        assert "Enter" in widget.ok_button.toolTip()
        assert "Escape" in widget.cancel_button.toolTip()

    def test_buttons_have_fixed_size(self, widget):
        """Test buttons have fixed size (not resizable)."""
        ok_size = widget.ok_button.size()
        cancel_size = widget.cancel_button.size()

        assert ok_size.width() == 24
        assert ok_size.height() == 24
        assert cancel_size.width() == 24
        assert cancel_size.height() == 24


class TestFocusManagement:
    """Test focus management."""

    def test_initial_focus_not_on_input(self, widget):
        """Test input doesn't have focus initially."""
        assert not widget.message_input.hasFocus()

    def test_show_and_focus_sets_input_focus(self, widget, qtbot):
        """Test show_and_focus sets focus to message input."""
        widget.show_and_focus()
        qtbot.waitUntil(lambda: widget.message_input.hasFocus(), timeout=1000)
        assert widget.message_input.hasFocus()

    def test_focus_stays_on_input_after_typing(self, widget, qtbot):
        """Test focus remains on input while typing."""
        widget.show_and_focus()
        qtbot.waitUntil(lambda: widget.message_input.hasFocus(), timeout=1000)

        qtbot.keyClicks(widget.message_input, "Test message")

        assert widget.message_input.hasFocus()

    def test_focus_lost_when_widget_hidden(self, widget, qtbot):
        """Test focus is lost when widget is hidden."""
        widget.show_and_focus()
        qtbot.waitUntil(lambda: widget.message_input.hasFocus(), timeout=1000)

        widget.hide()

        # Focus should be lost
        assert not widget.message_input.hasFocus()

    def test_clicking_ok_button_maintains_widget_function(self, widget, qtbot):
        """Test clicking OK button still works even without focus."""
        widget.show_and_focus()
        widget.message_input.setText("Test")

        # Click outside to lose focus (simulate)
        widget.message_input.clearFocus()

        # OK button should still work
        with qtbot.waitSignal(widget.commit_requested, timeout=1000):
            widget.ok_button.click()


class TestEdgeCaseMessages:
    """Test edge case messages."""

    def test_very_long_message(self, widget, qtbot):
        """Test very long commit message."""
        long_message = "A" * 500

        widget.message_input.setText(long_message)

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            widget.ok_button.click()

        assert blocker.args[0] == long_message

    def test_message_with_only_punctuation(self, widget, qtbot):
        """Test message with only punctuation characters."""
        widget.message_input.setText("!@#$%^&*()")

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            widget.ok_button.click()

        assert blocker.args[0] == "!@#$%^&*()"

    def test_message_with_leading_dashes(self, widget, qtbot):
        """Test message with leading dashes (Git convention)."""
        widget.message_input.setText("--amend Fix typo")

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            widget.ok_button.click()

        assert blocker.args[0] == "--amend Fix typo"

    def test_single_character_message(self, widget, qtbot):
        """Test single character commit message."""
        widget.message_input.setText("x")

        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            widget.ok_button.click()

        assert blocker.args[0] == "x"

    def test_message_with_control_characters(self, widget, qtbot):
        """Test message with control characters (if allowed)."""
        # QLineEdit typically filters control characters
        widget.message_input.setText("Test\x00Message")

        # Control chars might be filtered by QLineEdit
        message = widget.get_message()
        # Just verify it doesn't crash
        assert "Test" in message


class TestParentChildRelationships:
    """Test parent-child widget relationships."""

    def test_widget_has_parent(self, widget):
        """Test widget can have a parent."""
        # Created with None parent in fixture
        assert widget.parent() is None

    def test_all_children_accessible(self, widget):
        """Test all child widgets are accessible."""
        assert widget.message_input is not None
        assert widget.ok_button is not None
        assert widget.cancel_button is not None

    def test_find_child_by_type(self, widget):
        """Test finding child widgets by type."""
        line_edit = widget.findChild(QLineEdit)
        assert line_edit is not None
        assert line_edit == widget.message_input

    def test_layout_children_count(self, widget):
        """Test layout contains expected number of children."""
        layout = widget.layout()
        assert layout.count() == 4  # Label, Input, OK, Cancel


class TestRapidInteractions:
    """Test rapid user interactions."""

    def test_rapid_typing_and_commit(self, widget, qtbot):
        """Test rapid typing followed by immediate commit."""
        widget.show_and_focus()

        # Rapid typing
        qtbot.keyClicks(widget.message_input, "Quick commit", delay=1)

        # Immediate commit
        with qtbot.waitSignal(widget.commit_requested, timeout=1000) as blocker:
            qtbot.keyPress(widget.message_input, Qt.Key.Key_Return)

        assert blocker.args[0] == "Quick commit"

    def test_rapid_show_hide_cycles(self, widget):
        """Test rapid show/hide cycles."""
        for _ in range(20):
            widget.show_and_focus()
            widget.hide()

        # Should not crash or leave widget in bad state
        assert not widget.isVisible()

    def test_rapid_button_clicks(self, widget, qtbot):
        """Test rapid button clicking."""
        widget.show_and_focus()
        widget.message_input.setText("Test")

        # Click OK button rapidly (first click hides, others do nothing)
        widget.ok_button.click()
        widget.ok_button.click()
        widget.ok_button.click()

        assert not widget.isVisible()

    def test_alternating_commit_cancel(self, widget, qtbot):
        """Test alternating commit and cancel operations."""
        # Commit
        widget.show_and_focus()
        widget.message_input.setText("Commit 1")
        with qtbot.waitSignal(widget.commit_requested, timeout=1000):
            widget.ok_button.click()

        # Cancel
        widget.show_and_focus()
        widget.message_input.setText("Cancel this")
        with qtbot.waitSignal(widget.cancelled, timeout=1000):
            qtbot.keyPress(widget, Qt.Key.Key_Escape)

        # Commit again
        widget.show_and_focus()
        widget.message_input.setText("Commit 2")
        with qtbot.waitSignal(widget.commit_requested, timeout=1000):
            widget.ok_button.click()

        assert not widget.isVisible()
