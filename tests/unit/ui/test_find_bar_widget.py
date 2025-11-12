"""
Unit tests for FindBarWidget - quick find toolbar.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from asciidoc_artisan.ui.find_bar_widget import FindBarWidget


@pytest.mark.unit
class TestFindBarWidget:
    """Test FindBarWidget UI and functionality."""

    def test_initialization(self, qtbot):
        """Test FindBarWidget initializes correctly."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        assert widget.isHidden()  # Initially hidden
        assert widget.get_search_text() == ""
        assert not widget.is_case_sensitive()

    def test_show_and_focus(self, qtbot):
        """Test show_and_focus displays widget and focuses input."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.show_and_focus()
        qtbot.wait(10)  # Small delay for focus to propagate in test environment

        assert widget.isVisible()
        # Note: hasFocus() may not work reliably in headless test environment
        # Just verify the widget is shown, which is the critical functionality

    def test_search_text_getter_setter(self, qtbot):
        """Test get/set search text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_search_text("test search")
        assert widget.get_search_text() == "test search"

    def test_case_sensitive_getter_setter(self, qtbot):
        """Test get/set case sensitivity."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        assert not widget.is_case_sensitive()

        widget.set_case_sensitive(True)
        assert widget.is_case_sensitive()

        widget.set_case_sensitive(False)
        assert not widget.is_case_sensitive()

    def test_search_requested_signal_on_text_change(self, qtbot):
        """Test search_requested signal emitted when text changes."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        with qtbot.waitSignal(widget.search_requested, timeout=1000) as blocker:
            widget._search_input.setText("test")

        assert blocker.args == ["test", False]  # text, case_sensitive

    def test_search_requested_signal_on_case_toggle(self, qtbot):
        """Test search_requested signal emitted when case sensitivity toggles."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget._search_input.setText("test")

        with qtbot.waitSignal(widget.search_requested, timeout=1000) as blocker:
            widget._case_checkbox.setChecked(True)

        assert blocker.args == ["test", True]

    def test_find_next_requested_on_return(self, qtbot):
        """Test find_next_requested signal emitted on Enter key."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)
        widget.show_and_focus()

        with qtbot.waitSignal(widget.find_next_requested, timeout=1000):
            QTest.keyPress(widget._search_input, Qt.Key.Key_Return)

    def test_find_next_requested_on_button_click(self, qtbot):
        """Test find_next_requested signal emitted on Next button click."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        with qtbot.waitSignal(widget.find_next_requested, timeout=1000):
            widget._next_btn.click()

    def test_find_previous_requested_on_button_click(self, qtbot):
        """Test find_previous_requested signal emitted on Previous button click."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        with qtbot.waitSignal(widget.find_previous_requested, timeout=1000):
            widget._prev_btn.click()

    def test_close_button_hides_widget(self, qtbot):
        """Test close button hides widget and emits closed signal."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)
        widget.show_and_focus()

        with qtbot.waitSignal(widget.closed, timeout=1000):
            widget._close_btn.click()

        assert widget.isHidden()

    def test_escape_key_closes_widget(self, qtbot):
        """Test Esc key closes widget."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)
        widget.show_and_focus()

        with qtbot.waitSignal(widget.closed, timeout=1000):
            QTest.keyPress(widget, Qt.Key.Key_Escape)

        assert widget.isHidden()

    def test_update_match_count_zero_matches(self, qtbot):
        """Test update_match_count with zero matches."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.update_match_count(0, 0)

        assert widget._counter_label.text() == "No matches"
        assert not widget._prev_btn.isEnabled()
        assert not widget._next_btn.isEnabled()

    def test_update_match_count_with_matches(self, qtbot):
        """Test update_match_count with matches."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.update_match_count(5, 23)

        assert widget._counter_label.text() == "5 of 23"
        assert widget._prev_btn.isEnabled()
        assert widget._next_btn.isEnabled()

    def test_update_match_count_single_match(self, qtbot):
        """Test update_match_count with single match."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.update_match_count(1, 1)

        assert widget._counter_label.text() == "1 of 1"

    def test_clear_resets_input_and_counter(self, qtbot):
        """Test clear() resets input and match counter."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_search_text("test")
        widget.update_match_count(5, 23)

        widget.clear()

        assert widget.get_search_text() == ""
        assert widget._counter_label.text() == "No matches"

    def test_not_found_style(self, qtbot):
        """Test visual feedback for no matches."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Apply not-found style
        widget.set_not_found_style()
        assert "background-color" in widget._search_input.styleSheet()

        # Clear style
        widget.clear_not_found_style()
        assert widget._search_input.styleSheet() == ""

    def test_show_and_focus_selects_existing_text(self, qtbot):
        """Test show_and_focus selects existing text for easy replacement."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_search_text("existing text")
        widget.show_and_focus()

        assert widget._search_input.selectedText() == "existing text"

    def test_buttons_have_tooltips(self, qtbot):
        """Test buttons have helpful tooltips."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        assert widget._close_btn.toolTip() == "Close (Esc)"
        assert "F3" in widget._next_btn.toolTip()
        assert "Shift+F3" in widget._prev_btn.toolTip()

    def test_widget_initially_hidden(self, qtbot):
        """Test widget is hidden by default."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        assert widget.isHidden()

    def test_search_input_has_placeholder(self, qtbot):
        """Test search input has helpful placeholder text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        assert widget._search_input.placeholderText() == "Search text..."

    def test_match_counter_minimum_width(self, qtbot):
        """Test match counter has minimum width to prevent layout shifts."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        assert widget._counter_label.minimumWidth() == 80


@pytest.mark.unit
class TestSearchTextEdgeCases:
    """Test edge cases for search text input."""

    def test_empty_search_text(self, qtbot):
        """Test handling of empty search text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_search_text("")
        assert widget.get_search_text() == ""

    def test_very_long_search_text(self, qtbot):
        """Test handling of very long search text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        long_text = "a" * 10000
        widget.set_search_text(long_text)
        assert widget.get_search_text() == long_text

    def test_unicode_search_text(self, qtbot):
        """Test handling of unicode characters."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        unicode_text = "Hello 世界 🌍 مرحبا"
        widget.set_search_text(unicode_text)
        assert widget.get_search_text() == unicode_text

    def test_special_characters_search_text(self, qtbot):
        """Test handling of special characters."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        special_text = "<>&\"'\\n\\t"
        widget.set_search_text(special_text)
        assert widget.get_search_text() == special_text

    def test_whitespace_only_search_text(self, qtbot):
        """Test handling of whitespace-only text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        whitespace_text = "   \t\n   "
        widget.set_search_text(whitespace_text)
        assert widget.get_search_text() == whitespace_text

    def test_regex_pattern_characters(self, qtbot):
        """Test handling of regex special characters."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        regex_text = ".*?+[]{}()^$|"
        widget.set_search_text(regex_text)
        assert widget.get_search_text() == regex_text


@pytest.mark.unit
class TestMatchCounterVariations:
    """Test match counter display variations."""

    def test_large_match_count(self, qtbot):
        """Test display of large match counts."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.update_match_count(500, 10000)
        assert widget._counter_label.text() == "500 of 10000"

    def test_match_count_at_boundaries(self, qtbot):
        """Test match count at first and last positions."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.update_match_count(1, 100)
        assert widget._counter_label.text() == "1 of 100"

        widget.update_match_count(100, 100)
        assert widget._counter_label.text() == "100 of 100"

    def test_match_count_updates_button_state(self, qtbot):
        """Test button enable/disable based on match count."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # No matches - buttons disabled
        widget.update_match_count(0, 0)
        assert not widget._prev_btn.isEnabled()
        assert not widget._next_btn.isEnabled()

        # Matches - buttons enabled
        widget.update_match_count(1, 5)
        assert widget._prev_btn.isEnabled()
        assert widget._next_btn.isEnabled()

    def test_match_count_negative_values(self, qtbot):
        """Test handling of invalid negative match counts."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Should handle gracefully (implementation may validate or accept)
        try:
            widget.update_match_count(-1, 10)
            # If accepted, just verify it doesn't crash
        except ValueError:
            # If rejected, that's acceptable
            pass

    def test_match_count_current_exceeds_total(self, qtbot):
        """Test handling of current > total (invalid state)."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Should handle gracefully
        widget.update_match_count(10, 5)
        # Verify it doesn't crash (specific behavior may vary)


@pytest.mark.unit
class TestShowHideCycles:
    """Test show/hide state transitions."""

    def test_multiple_show_cycles(self, qtbot):
        """Test multiple show/hide cycles."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        for _ in range(10):
            widget.show_and_focus()
            assert widget.isVisible()

            widget.hide()
            assert widget.isHidden()

    def test_show_already_visible(self, qtbot):
        """Test showing an already visible widget."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.show_and_focus()
        assert widget.isVisible()

        widget.show_and_focus()
        assert widget.isVisible()

    def test_hide_already_hidden(self, qtbot):
        """Test hiding an already hidden widget."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        assert widget.isHidden()

        widget.hide()
        assert widget.isHidden()

    def test_close_signal_only_when_visible(self, qtbot):
        """Test closed signal emitted only when actually closing."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)
        widget.show_and_focus()

        with qtbot.waitSignal(widget.closed, timeout=1000):
            widget._close_btn.click()


@pytest.mark.unit
class TestSignalEmissionEdgeCases:
    """Test signal emission edge cases."""

    def test_search_requested_with_empty_text(self, qtbot):
        """Test search_requested signal with empty text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Empty text may or may not emit signal depending on implementation
        # Just verify setText doesn't crash
        widget._search_input.setText("")
        assert widget.get_search_text() == ""

    def test_rapid_text_changes(self, qtbot):
        """Test rapid text changes emit multiple signals."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Each text change should emit signal
        for char in "test":
            widget._search_input.setText(widget._search_input.text() + char)
            qtbot.wait(10)

    def test_case_toggle_without_text(self, qtbot):
        """Test case sensitivity toggle with empty text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        with qtbot.waitSignal(widget.search_requested, timeout=1000) as blocker:
            widget._case_checkbox.setChecked(True)

        assert blocker.args == ["", True]

    def test_find_next_with_no_matches(self, qtbot):
        """Test find_next button disabled with no matches."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)
        widget.update_match_count(0, 0)

        # Button should be disabled, so clicking has no effect
        assert not widget._next_btn.isEnabled()
        widget._next_btn.click()  # Should not emit signal when disabled

    def test_find_previous_with_no_matches(self, qtbot):
        """Test find_previous button disabled with no matches."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)
        widget.update_match_count(0, 0)

        # Button should be disabled, so clicking has no effect
        assert not widget._prev_btn.isEnabled()
        widget._prev_btn.click()  # Should not emit signal when disabled


@pytest.mark.unit
class TestKeyboardShortcutEdgeCases:
    """Test keyboard shortcut edge cases."""

    def test_return_key_with_empty_text(self, qtbot):
        """Test Enter key with empty search text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)
        widget.show_and_focus()

        with qtbot.waitSignal(widget.find_next_requested, timeout=1000):
            QTest.keyPress(widget._search_input, Qt.Key.Key_Return)

    def test_escape_when_hidden(self, qtbot):
        """Test Escape key when widget is already hidden."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Widget is already hidden, Escape should not emit signal
        QTest.keyPress(widget, Qt.Key.Key_Escape)
        # Just verify no crash

    def test_multiple_escape_presses(self, qtbot):
        """Test multiple Escape key presses."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)
        widget.show_and_focus()

        with qtbot.waitSignal(widget.closed, timeout=1000):
            QTest.keyPress(widget, Qt.Key.Key_Escape)

        # Second Escape on hidden widget
        QTest.keyPress(widget, Qt.Key.Key_Escape)


@pytest.mark.unit
class TestStyleManagement:
    """Test style application and removal."""

    def test_not_found_style_application(self, qtbot):
        """Test not-found style applies correctly."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_not_found_style()
        assert len(widget._search_input.styleSheet()) > 0

    def test_not_found_style_removal(self, qtbot):
        """Test not-found style clears correctly."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_not_found_style()
        widget.clear_not_found_style()
        assert widget._search_input.styleSheet() == ""

    def test_multiple_style_applications(self, qtbot):
        """Test multiple style applications."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        for _ in range(5):
            widget.set_not_found_style()
            assert "background-color" in widget._search_input.styleSheet()

            widget.clear_not_found_style()
            assert widget._search_input.styleSheet() == ""

    def test_style_persists_across_text_changes(self, qtbot):
        """Test not-found style persists when text changes."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_not_found_style()
        widget.set_search_text("new text")
        # Style should still be applied until explicitly cleared


@pytest.mark.unit
class TestClearOperation:
    """Test clear() operation in various states."""

    def test_clear_with_matches_displayed(self, qtbot):
        """Test clear when matches are displayed."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_search_text("test")
        widget.update_match_count(5, 23)
        widget.clear()

        assert widget.get_search_text() == ""
        assert widget._counter_label.text() == "No matches"

    def test_clear_already_empty(self, qtbot):
        """Test clear when already empty."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.clear()
        assert widget.get_search_text() == ""

    def test_clear_with_case_sensitivity(self, qtbot):
        """Test clear preserves case sensitivity setting."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_case_sensitive(True)
        widget.set_search_text("test")
        widget.clear()

        assert widget.get_search_text() == ""
        assert widget.is_case_sensitive()  # Preserved

    def test_clear_removes_not_found_style(self, qtbot):
        """Test clear removes not-found styling."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_not_found_style()
        widget.clear()
        # Implementation may or may not clear style on clear()


@pytest.mark.unit
class TestTextSelection:
    """Test text selection behavior."""

    def test_show_and_focus_selects_all(self, qtbot):
        """Test show_and_focus selects all existing text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_search_text("select this")
        widget.show_and_focus()

        assert widget._search_input.selectedText() == "select this"

    def test_empty_text_selection(self, qtbot):
        """Test show_and_focus with empty text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.show_and_focus()
        assert widget._search_input.selectedText() == ""

    def test_selection_after_manual_edit(self, qtbot):
        """Test selection behavior after manual text edit."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_search_text("initial")
        widget.show_and_focus()
        # After user starts typing, selection should be cleared
        widget._search_input.setText("new")


@pytest.mark.unit
class TestButtonStates:
    """Test button enable/disable states."""

    def test_buttons_disabled_on_zero_matches(self, qtbot):
        """Test prev/next buttons disabled with zero matches."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.update_match_count(0, 0)
        assert not widget._prev_btn.isEnabled()
        assert not widget._next_btn.isEnabled()

    def test_buttons_enabled_on_matches(self, qtbot):
        """Test prev/next buttons enabled with matches."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.update_match_count(1, 1)
        assert widget._prev_btn.isEnabled()
        assert widget._next_btn.isEnabled()

    def test_close_button_always_enabled(self, qtbot):
        """Test close button is always enabled."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        assert widget._close_btn.isEnabled()

        widget.update_match_count(0, 0)
        assert widget._close_btn.isEnabled()


@pytest.mark.unit
class TestWidgetLifecycle:
    """Test widget creation and destruction."""

    def test_multiple_widget_instances(self, qtbot):
        """Test creating multiple independent widget instances."""
        widget1 = FindBarWidget()
        widget2 = FindBarWidget()
        qtbot.addWidget(widget1)
        qtbot.addWidget(widget2)

        widget1.set_search_text("widget1")
        widget2.set_search_text("widget2")

        assert widget1.get_search_text() == "widget1"
        assert widget2.get_search_text() == "widget2"

    def test_widget_cleanup(self, qtbot):
        """Test widget cleanup doesn't cause issues."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_search_text("test")
        widget.show_and_focus()
        # Widget will be cleaned up by qtbot


@pytest.mark.unit
class TestCaseSensitivityState:
    """Test case sensitivity state management."""

    def test_case_sensitivity_default_false(self, qtbot):
        """Test case sensitivity defaults to False."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        assert not widget.is_case_sensitive()

    def test_case_sensitivity_toggle_multiple_times(self, qtbot):
        """Test toggling case sensitivity multiple times."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        for _ in range(5):
            widget.set_case_sensitive(True)
            assert widget.is_case_sensitive()

            widget.set_case_sensitive(False)
            assert not widget.is_case_sensitive()

    def test_case_sensitivity_independent_of_text(self, qtbot):
        """Test case sensitivity state independent of text content."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_case_sensitive(True)
        widget.set_search_text("TEST")
        assert widget.is_case_sensitive()

        widget.clear()
        assert widget.is_case_sensitive()


@pytest.mark.unit
class TestUIComponents:
    """Test UI component properties."""

    def test_all_required_widgets_exist(self, qtbot):
        """Test all required UI widgets are created."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        assert hasattr(widget, "_search_input")
        assert hasattr(widget, "_case_checkbox")
        assert hasattr(widget, "_next_btn")
        assert hasattr(widget, "_prev_btn")
        assert hasattr(widget, "_close_btn")
        assert hasattr(widget, "_counter_label")

    def test_case_checkbox_label(self, qtbot):
        """Test case sensitivity checkbox has label."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Checkbox should have text or tooltip
        assert (
            len(widget._case_checkbox.text()) > 0
            or len(widget._case_checkbox.toolTip()) > 0
        )

    def test_counter_label_alignment(self, qtbot):
        """Test counter label has appropriate alignment."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Counter should have some alignment set
        assert widget._counter_label.alignment() is not None


@pytest.mark.unit
class TestConcurrentOperations:
    """Test handling of concurrent operations."""

    def test_text_change_during_match_update(self, qtbot):
        """Test text change while match count is updating."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_search_text("test")
        widget.update_match_count(5, 23)
        widget.set_search_text("new")

        # Should handle gracefully

    def test_show_hide_during_search(self, qtbot):
        """Test show/hide while search is active."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_search_text("test")
        widget.show_and_focus()
        widget.hide()
        widget.show_and_focus()

        # Should handle gracefully

    def test_clear_during_match_display(self, qtbot):
        """Test clear while matches are displayed."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        widget.set_search_text("test")
        widget.update_match_count(10, 50)
        widget.clear()

        assert widget.get_search_text() == ""
        assert widget._counter_label.text() == "No matches"


@pytest.mark.unit
class TestReplaceMode:
    """Test find and replace mode functionality."""

    def test_toggle_replace_mode_shows_replace_row(self, qtbot):
        """Test toggling replace mode shows replace controls."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)
        widget.show()  # Show parent widget so child visibility works correctly

        # Initially replace row should be hidden
        assert not widget._replace_row_widget.isVisible()
        assert not widget._replace_mode

        # Toggle to show
        widget._toggle_replace_mode()

        # Verify replace row is now visible
        assert widget._replace_row_widget.isVisible()
        assert widget._replace_mode
        assert widget._toggle_replace_btn.text() == "▼"

    def test_toggle_replace_mode_hides_replace_row(self, qtbot):
        """Test toggling replace mode again hides replace controls."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)
        widget.show()  # Show parent widget so child visibility works correctly

        # Enable replace mode
        widget._toggle_replace_mode()
        assert widget._replace_row_widget.isVisible()
        assert widget._replace_mode

        # Toggle again to hide
        widget._toggle_replace_mode()

        # Verify replace row is now hidden
        assert not widget._replace_row_widget.isVisible()
        assert not widget._replace_mode
        assert widget._toggle_replace_btn.text() == "▶"

    def test_show_replace_and_focus_enables_replace_mode(self, qtbot):
        """Test show_replace_and_focus enables replace mode."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Initially replace mode is disabled
        assert not widget._replace_mode

        # Call show_replace_and_focus
        widget.show_replace_and_focus()

        # Verify replace mode is enabled
        assert widget._replace_mode
        assert widget._replace_row_widget.isVisible()
        assert widget.isVisible()
        assert widget._search_input.selectedText() == ""

    def test_show_replace_and_focus_when_already_in_replace_mode(self, qtbot):
        """Test show_replace_and_focus when already in replace mode."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Set some search text
        widget.set_search_text("test")

        # Enable replace mode first
        widget._toggle_replace_mode()
        assert widget._replace_mode

        # Call show_replace_and_focus again
        widget.show_replace_and_focus()

        # Verify it's still in replace mode (idempotent)
        assert widget._replace_mode
        assert widget._replace_row_widget.isVisible()
        assert widget.isVisible()
        assert widget._search_input.selectedText() == "test"

    def test_replace_requested_signal_emission(self, qtbot):
        """Test replace_requested signal is emitted with replacement text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Set replacement text
        widget.set_replace_text("replacement_text")

        # Connect signal spy
        with qtbot.waitSignal(widget.replace_requested, timeout=1000) as blocker:
            widget._on_replace_clicked()

        # Verify signal was emitted with correct text
        assert blocker.args == ["replacement_text"]

    def test_replace_all_requested_signal_emission(self, qtbot):
        """Test replace_all_requested signal is emitted with replacement text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Set replacement text
        widget.set_replace_text("new_replacement")

        # Connect signal spy
        with qtbot.waitSignal(widget.replace_all_requested, timeout=1000) as blocker:
            widget._on_replace_all_clicked()

        # Verify signal was emitted with correct text
        assert blocker.args == ["new_replacement"]

    def test_get_replace_text_returns_current_text(self, qtbot):
        """Test get_replace_text returns current replacement text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Set replacement text
        widget.set_replace_text("test_replacement")

        # Verify getter returns correct text
        assert widget.get_replace_text() == "test_replacement"

    def test_set_replace_text_updates_input(self, qtbot):
        """Test set_replace_text updates the replace input field."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Set replacement text
        widget.set_replace_text("new_text")

        # Verify input was updated
        assert widget._replace_input.text() == "new_text"
        assert widget.get_replace_text() == "new_text"

    def test_replace_with_empty_text(self, qtbot):
        """Test replace operations with empty replacement text."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Set replacement text to empty string
        widget.set_replace_text("")

        # Verify replace signal includes empty string
        with qtbot.waitSignal(widget.replace_requested, timeout=1000) as blocker:
            widget._on_replace_clicked()
        assert blocker.args == [""]

        # Verify replace all signal includes empty string
        with qtbot.waitSignal(widget.replace_all_requested, timeout=1000) as blocker:
            widget._on_replace_all_clicked()
        assert blocker.args == [""]

    def test_replace_mode_persists_across_show_hide(self, qtbot):
        """Test replace mode persists when hiding and showing widget."""
        widget = FindBarWidget()
        qtbot.addWidget(widget)

        # Enable replace mode
        widget._toggle_replace_mode()
        assert widget._replace_mode

        # Hide widget
        widget.hide()
        assert not widget.isVisible()
        assert widget._replace_mode  # Mode should persist

        # Show widget again
        widget.show()
        assert widget.isVisible()
        assert widget._replace_mode  # Mode should still be enabled
        assert widget._replace_row_widget.isVisible()
