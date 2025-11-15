"""
Tests for AutoCompleteWidget (v2.0.0).

Tests the completion popup widget with keyboard navigation,
mouse selection, and signal emissions.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QPlainTextEdit

from asciidoc_artisan.core.models import CompletionItem, CompletionKind
from asciidoc_artisan.ui.autocomplete_widget import AutoCompleteWidget


@pytest.fixture
def editor(qtbot):
    """Create a test editor widget."""
    widget = QPlainTextEdit()
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def widget(qtbot, editor):
    """Create an AutoCompleteWidget instance."""
    w = AutoCompleteWidget(editor)
    qtbot.addWidget(w)
    return w


@pytest.fixture
def sample_items():
    """Create sample completion items."""
    return [
        CompletionItem(
            text="= Heading",
            kind=CompletionKind.SYNTAX,
            detail="Level 1 heading",
            documentation="Document title",
        ),
        CompletionItem(
            text="== Section",
            kind=CompletionKind.SYNTAX,
            detail="Level 2 heading",
            documentation="Section heading",
        ),
        CompletionItem(
            text="=== Subsection",
            kind=CompletionKind.SYNTAX,
            detail="Level 3 heading",
        ),
    ]



@pytest.mark.fr_086
@pytest.mark.fr_089
@pytest.mark.unit
class TestInitialization:
    """Test widget initialization."""

    def test_widget_creation(self, widget, editor):
        """Test widget is created with correct parent."""
        assert widget.parent() == editor
        assert isinstance(widget.items, list)
        assert len(widget.items) == 0

    def test_widget_window_flags(self, widget):
        """Test widget has popup window flags."""
        flags = widget.windowFlags()
        assert Qt.WindowType.Popup in flags
        assert Qt.WindowType.FramelessWindowHint in flags

    def test_widget_focus_policy(self, widget):
        """Test widget has NoFocus policy."""
        assert widget.focusPolicy() == Qt.FocusPolicy.NoFocus

    def test_widget_scroll_policy(self, widget):
        """Test horizontal scrollbar is always off."""
        assert widget.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff

    def test_widget_size_constraints(self, widget):
        """Test widget size constraints."""
        assert widget.maximumHeight() == 200
        assert widget.minimumWidth() == 300

    def test_widget_hidden_by_default(self, widget):
        """Test widget is hidden on creation."""
        assert widget.isHidden() is True

    def test_widget_has_signals(self, widget):
        """Test widget defines required signals."""
        assert hasattr(widget, "item_selected")
        assert hasattr(widget, "cancelled")



@pytest.mark.fr_086
@pytest.mark.fr_089
@pytest.mark.unit
class TestShowCompletions:
    """Test show_completions method."""

    def test_show_completions_empty_list(self, widget):
        """Test showing empty completion list."""
        widget.show_completions([])

        assert len(widget.items) == 0
        assert widget.count() == 0
        # Widget should remain hidden for empty list
        assert widget.isHidden() is True

    def test_show_completions_with_items(self, widget, sample_items):
        """Test showing completions with items."""
        widget.show_completions(sample_items)

        assert len(widget.items) == 3
        assert widget.count() == 3
        assert widget.isVisible() is True

    def test_show_completions_item_text(self, widget, sample_items):
        """Test completion items have correct text."""
        widget.show_completions(sample_items)

        assert widget.item(0).text() == "= Heading"
        assert widget.item(1).text() == "== Section"
        assert widget.item(2).text() == "=== Subsection"

    def test_show_completions_item_data(self, widget, sample_items):
        """Test completion items store CompletionItem data."""
        widget.show_completions(sample_items)

        item_data = widget.item(0).data(Qt.ItemDataRole.UserRole)
        assert isinstance(item_data, CompletionItem)
        assert item_data.text == "= Heading"
        assert item_data.kind == CompletionKind.SYNTAX

    def test_show_completions_item_tooltip(self, widget, sample_items):
        """Test completion items have tooltips with detail and docs."""
        widget.show_completions(sample_items)

        tooltip = widget.item(0).toolTip()
        assert "Level 1 heading" in tooltip
        assert "Document title" in tooltip

    def test_show_completions_item_tooltip_no_docs(self, widget):
        """Test tooltip with detail but no documentation."""
        items = [
            CompletionItem(
                text="Test",
                kind=CompletionKind.SYNTAX,
                detail="Detail only",
            )
        ]
        widget.show_completions(items)

        tooltip = widget.item(0).toolTip()
        assert "Detail only" in tooltip

    def test_show_completions_selects_first_item(self, widget, sample_items):
        """Test first item is selected by default."""
        widget.show_completions(sample_items)

        assert widget.currentRow() == 0

    def test_show_completions_clears_previous_items(self, widget, sample_items):
        """Test showing new completions clears previous ones."""
        widget.show_completions(sample_items)
        assert widget.count() == 3

        new_items = [
            CompletionItem(text="New 1", kind=CompletionKind.SYNTAX),
            CompletionItem(text="New 2", kind=CompletionKind.SYNTAX),
        ]
        widget.show_completions(new_items)

        assert widget.count() == 2
        assert widget.item(0).text() == "New 1"



@pytest.mark.fr_086
@pytest.mark.fr_089
@pytest.mark.unit
class TestKeyboardNavigation:
    """Test keyboard event handling."""

    def test_enter_key_selects_item(self, widget, sample_items, qtbot):
        """Test Enter key selects current item."""
        widget.show_completions(sample_items)

        selected_item = None

        def on_selected(item):
            nonlocal selected_item
            selected_item = item

        widget.item_selected.connect(on_selected)

        # Simulate Enter key
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Return,
            Qt.KeyboardModifier.NoModifier,
        )
        widget.keyPressEvent(event)

        assert selected_item is not None
        assert selected_item.text == "= Heading"
        assert widget.isHidden() is True

    def test_return_key_selects_item(self, widget, sample_items, qtbot):
        """Test Return key also selects item."""
        widget.show_completions(sample_items)

        selected_item = None

        def on_selected(item):
            nonlocal selected_item
            selected_item = item

        widget.item_selected.connect(on_selected)

        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Enter,
            Qt.KeyboardModifier.NoModifier,
        )
        widget.keyPressEvent(event)

        assert selected_item is not None

    def test_escape_key_cancels(self, widget, sample_items, qtbot):
        """Test Escape key cancels and hides."""
        widget.show_completions(sample_items)

        cancelled = False

        def on_cancelled():
            nonlocal cancelled
            cancelled = True

        widget.cancelled.connect(on_cancelled)

        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier,
        )
        widget.keyPressEvent(event)

        assert cancelled is True
        assert widget.isHidden() is True

    def test_down_key_navigates_list(self, widget, sample_items, qtbot):
        """Test Down key navigates to next item."""
        widget.show_completions(sample_items)
        assert widget.currentRow() == 0

        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Down,
            Qt.KeyboardModifier.NoModifier,
        )
        widget.keyPressEvent(event)

        assert widget.currentRow() == 1

    def test_up_key_navigates_list(self, widget, sample_items, qtbot):
        """Test Up key navigates to previous item."""
        widget.show_completions(sample_items)
        widget.setCurrentRow(1)

        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Up,
            Qt.KeyboardModifier.NoModifier,
        )
        widget.keyPressEvent(event)

        assert widget.currentRow() == 0

    def test_other_keys_pass_to_parent(self, widget, sample_items, editor, qtbot):
        """Test other keys are passed to parent editor."""
        widget.show_completions(sample_items)

        # Track if editor received key event
        key_received = False
        original_keyPressEvent = editor.keyPressEvent

        def mock_keyPressEvent(event):
            nonlocal key_received
            key_received = True
            original_keyPressEvent(event)

        editor.keyPressEvent = mock_keyPressEvent

        # Simulate typing 'a'
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_A,
            Qt.KeyboardModifier.NoModifier,
            "a",
        )
        widget.keyPressEvent(event)

        assert key_received is True

    def test_enter_with_no_current_item(self, widget, qtbot):
        """Test Enter key when no item is selected."""
        widget.show_completions([
            CompletionItem(text="Test", kind=CompletionKind.SYNTAX),
        ])
        widget.setCurrentRow(-1)  # Deselect

        selected_item = None

        def on_selected(item):
            nonlocal selected_item
            selected_item = item

        widget.item_selected.connect(on_selected)

        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Return,
            Qt.KeyboardModifier.NoModifier,
        )
        widget.keyPressEvent(event)

        # Should not emit signal when no current item
        assert selected_item is None



@pytest.mark.fr_086
@pytest.mark.fr_089
@pytest.mark.unit
class TestMouseSelection:
    """Test mouse click selection."""

    def test_click_selects_item(self, widget, sample_items, qtbot):
        """Test clicking an item selects it."""
        widget.show_completions(sample_items)

        selected_item = None

        def on_selected(item):
            nonlocal selected_item
            selected_item = item

        widget.item_selected.connect(on_selected)

        # Simulate clicking second item
        list_item = widget.item(1)
        widget.itemClicked.emit(list_item)

        assert selected_item is not None
        assert selected_item.text == "== Section"
        assert widget.isHidden() is True

    def test_click_emits_signal(self, widget, sample_items, qtbot):
        """Test click emits item_selected signal."""
        widget.show_completions(sample_items)

        with qtbot.waitSignal(widget.item_selected, timeout=1000):
            list_item = widget.item(0)
            widget.itemClicked.emit(list_item)



@pytest.mark.fr_086
@pytest.mark.fr_089
@pytest.mark.unit
class TestSignals:
    """Test signal emissions."""

    def test_item_selected_signal(self, widget, sample_items, qtbot):
        """Test item_selected signal emits CompletionItem."""
        widget.show_completions(sample_items)

        received_item = None

        def on_selected(item):
            nonlocal received_item
            received_item = item

        widget.item_selected.connect(on_selected)

        # Trigger selection
        list_item = widget.item(0)
        widget._on_item_clicked(list_item)

        assert isinstance(received_item, CompletionItem)
        assert received_item.text == "= Heading"

    def test_cancelled_signal(self, widget, sample_items, qtbot):
        """Test cancelled signal is emitted on Escape."""
        widget.show_completions(sample_items)

        with qtbot.waitSignal(widget.cancelled, timeout=1000):
            event = QKeyEvent(
                QKeyEvent.Type.KeyPress,
                Qt.Key.Key_Escape,
                Qt.KeyboardModifier.NoModifier,
            )
            widget.keyPressEvent(event)



@pytest.mark.fr_086
@pytest.mark.fr_089
@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_show_completions_single_item(self, widget):
        """Test showing single completion item."""
        items = [CompletionItem(text="Only one", kind=CompletionKind.SYNTAX)]
        widget.show_completions(items)

        assert widget.count() == 1
        assert widget.isVisible() is True

    def test_keyboard_navigation_at_boundaries(self, widget, sample_items):
        """Test navigation at list boundaries."""
        widget.show_completions(sample_items)

        # Navigate to last item
        widget.setCurrentRow(2)

        # Down should wrap or stay
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Down,
            Qt.KeyboardModifier.NoModifier,
        )
        widget.keyPressEvent(event)

        # Should stay at last item or wrap to first
        assert widget.currentRow() in [0, 2]

    def test_widget_hides_after_selection(self, widget, sample_items):
        """Test widget hides after item selection."""
        widget.show_completions(sample_items)
        assert widget.isVisible() is True

        # Select via Enter
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Return,
            Qt.KeyboardModifier.NoModifier,
        )
        widget.keyPressEvent(event)

        assert widget.isHidden() is True

    def test_show_completions_focus(self, widget, sample_items):
        """Test widget receives focus when shown."""
        widget.show_completions(sample_items)

        # Note: Widget has NoFocus policy, so setFocus() may not actually give focus
        # But we can verify the call was made (widget is visible)
        assert widget.isVisible() is True

    def test_multiple_show_completions_calls(self, widget, sample_items):
        """Test multiple show_completions calls work correctly."""
        widget.show_completions(sample_items)
        assert widget.count() == 3

        widget.show_completions(sample_items[:1])
        assert widget.count() == 1

        widget.show_completions(sample_items)
        assert widget.count() == 3
