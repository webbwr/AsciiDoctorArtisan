"""Tests for ui.line_number_area module - Line number display functionality."""

import pytest
from unittest.mock import Mock, patch
from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QContextMenuEvent, QPaintEvent
from PySide6.QtWidgets import QPlainTextEdit


@pytest.mark.unit
class TestLineNumberPlainTextEditBasics:
    """Test suite for LineNumberPlainTextEdit basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        assert LineNumberPlainTextEdit is not None

    def test_creation(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        assert editor is not None

    def test_is_qplaintextedit(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        assert isinstance(editor, QPlainTextEdit)

    def test_has_line_number_area(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        assert hasattr(editor, "line_number_area")
        assert editor.line_number_area is not None

    def test_spell_check_manager_initially_none(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        assert hasattr(editor, "spell_check_manager")
        assert editor.spell_check_manager is None


@pytest.mark.unit
class TestLineNumberArea:
    """Test suite for LineNumberArea widget."""

    def test_line_number_area_creation(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberArea, LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        area = editor.line_number_area
        assert isinstance(area, LineNumberArea)

    def test_line_number_area_has_editor_reference(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        area = editor.line_number_area
        assert hasattr(area, "editor")
        assert area.editor == editor

    def test_line_number_area_size_hint(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        area = editor.line_number_area
        size_hint = area.sizeHint()
        assert isinstance(size_hint, QSize)
        assert size_hint.width() > 0

    def test_line_number_area_paint_event_calls_editor(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        area = editor.line_number_area

        # Mock the editor's paint method
        editor.line_number_area_paint_event = Mock()

        # Create a paint event
        event = QPaintEvent(QRect(0, 0, 50, 100))
        area.paintEvent(event)

        # Should call editor's paint method
        editor.line_number_area_paint_event.assert_called_once_with(event)


@pytest.mark.unit
class TestLineNumberWidth:
    """Test suite for line number width calculation."""

    def test_line_number_area_width_empty(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        width = editor.line_number_area_width()
        # Empty editor has 1 block, so 1 digit needed
        assert width > 0
        assert isinstance(width, int)

    def test_line_number_area_width_single_digit(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        editor.setPlainText("Line 1\nLine 2\nLine 3")
        width = editor.line_number_area_width()
        # 3 lines = 1 digit
        assert width > 10

    def test_line_number_area_width_two_digit(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        # Create 15 lines (2 digits)
        text = "\n".join([f"Line {i+1}" for i in range(15)])
        editor.setPlainText(text)
        width = editor.line_number_area_width()
        assert editor.blockCount() == 15
        assert width > 15

    def test_line_number_area_width_three_digit(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        # Create 100 lines (3 digits)
        text = "\n".join([f"Line {i+1}" for i in range(100)])
        editor.setPlainText(text)
        width = editor.line_number_area_width()
        assert editor.blockCount() == 100
        assert width > 20

    def test_line_number_area_width_formula(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        editor.setPlainText("Test")
        width = editor.line_number_area_width()
        # Formula: 3px + digit_width + 3px
        assert width >= 6  # At minimum 6px padding


@pytest.mark.unit
class TestViewportMarginsAndUpdates:
    """Test suite for viewport margins and line number updates."""

    def test_viewport_margins_set_on_init(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        margins = editor.viewportMargins()
        # Left margin should be set for line numbers
        assert margins.left() > 0
        assert margins.left() == editor.line_number_area_width()

    def test_update_line_number_area_width_updates_margins(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)

        initial_width = editor.line_number_area_width()
        initial_margin = editor.viewportMargins().left()
        assert initial_margin == initial_width

        # Add many lines to increase width
        text = "\n".join([f"Line {i+1}" for i in range(1000)])
        editor.setPlainText(text)

        new_width = editor.line_number_area_width()
        new_margin = editor.viewportMargins().left()
        assert new_width > initial_width
        assert new_margin == new_width

    def test_update_line_number_area_with_scroll(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        editor.setPlainText("\n".join([f"Line {i+1}" for i in range(50)]))

        area = editor.line_number_area
        area.scroll = Mock()

        # Trigger update with scroll (dy != 0)
        rect = QRect(0, 0, 50, 100)
        dy = 10
        editor.update_line_number_area(rect, dy)

        # Should call scroll on area
        area.scroll.assert_called_once_with(0, dy)

    def test_update_line_number_area_without_scroll(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)

        area = editor.line_number_area
        area.update = Mock()

        # Trigger update without scroll (dy == 0)
        rect = QRect(0, 10, 50, 20)
        dy = 0
        editor.update_line_number_area(rect, dy)

        # Should call update on area
        area.update.assert_called_once()
        call_args = area.update.call_args[0]
        assert call_args[0] == 0  # x
        assert call_args[1] == rect.y()  # y
        assert call_args[2] == area.width()  # width
        assert call_args[3] == rect.height()  # height

    def test_update_line_number_area_with_full_viewport(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        editor.setPlainText("Test")

        # Create rect that contains entire viewport
        viewport_rect = editor.viewport().rect()
        editor.update_line_number_area_width = Mock()

        # Should trigger width update if rect contains viewport
        editor.update_line_number_area(viewport_rect, 0)
        editor.update_line_number_area_width.assert_called()


@pytest.mark.unit
class TestSignalConnections:
    """Test suite for signal connections."""

    def test_block_count_changed_signal_connected(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)

        # Spy on update_line_number_area_width
        editor.update_line_number_area_width = Mock()

        # Change block count
        editor.setPlainText("Line 1\nLine 2")

        # Signal should have triggered update
        editor.update_line_number_area_width.assert_called()

    def test_update_request_signal_connected(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        editor.setPlainText("Test line")

        # Spy on update_line_number_area
        editor.update_line_number_area = Mock()

        # Trigger update by modifying text
        editor.setPlainText("Modified")

        # Signal should have triggered update
        editor.update_line_number_area.assert_called()


@pytest.mark.unit
class TestResizeHandling:
    """Test suite for resize event handling."""

    def test_resize_event_has_handler(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)

        # Should have resizeEvent method
        assert hasattr(editor, "resizeEvent")
        assert callable(editor.resizeEvent)

    def test_resize_does_not_crash(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        editor.setPlainText("\n".join([f"Line {i+1}" for i in range(100)]))

        # Resize should not crash
        editor.resize(500, 400)
        editor.resize(300, 200)

        # Line number area should still exist
        assert editor.line_number_area is not None


@pytest.mark.unit
class TestContextMenu:
    """Test suite for context menu handling."""

    def test_context_menu_without_spell_check_manager(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)

        # Should use default context menu when spell_check_manager is None
        with patch.object(QPlainTextEdit, "contextMenuEvent") as mock_super:
            event = Mock(spec=QContextMenuEvent)
            editor.contextMenuEvent(event)
            mock_super.assert_called_once_with(event)

    def test_context_menu_with_spell_check_manager(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)

        # Set up spell check manager
        mock_spell_check = Mock()
        mock_spell_check.show_context_menu = Mock()
        editor.spell_check_manager = mock_spell_check

        # Should use spell check context menu
        event = Mock(spec=QContextMenuEvent)
        editor.contextMenuEvent(event)
        mock_spell_check.show_context_menu.assert_called_once_with(event)

    def test_spell_check_manager_can_be_set(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)

        # Initially None
        assert editor.spell_check_manager is None

        # Can be set
        mock_manager = Mock()
        editor.spell_check_manager = mock_manager
        assert editor.spell_check_manager == mock_manager


@pytest.mark.unit
class TestPaintEvent:
    """Test suite for paint event handling."""

    def test_paint_event_does_not_crash(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        editor.setPlainText("Line 1\nLine 2\nLine 3")

        # Force a paint event (should not crash)
        editor.line_number_area.update()

    def test_paint_event_with_many_lines(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)

        # Create many lines
        text = "\n".join([f"Line {i+1}" for i in range(1000)])
        editor.setPlainText(text)

        # Force paint (should not crash)
        editor.line_number_area.update()


@pytest.mark.unit
class TestEdgeCases:
    """Test suite for edge cases."""

    def test_empty_editor(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)

        # Empty editor should still work
        assert editor.blockCount() >= 1  # Qt always has at least 1 block
        width = editor.line_number_area_width()
        assert width > 0

    def test_single_line(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)
        editor.setPlainText("Single line")

        assert editor.blockCount() == 1
        width = editor.line_number_area_width()
        assert width > 0

    def test_very_long_document(self, qtbot):
        from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
        editor = LineNumberPlainTextEdit()
        qtbot.addWidget(editor)

        # 10,000 lines (5 digits)
        text = "\n".join([f"Line {i+1}" for i in range(10000)])
        editor.setPlainText(text)

        assert editor.blockCount() == 10000
        width = editor.line_number_area_width()
        # Should handle 5-digit line numbers
        assert width > 30
