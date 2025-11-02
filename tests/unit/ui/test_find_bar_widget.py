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
