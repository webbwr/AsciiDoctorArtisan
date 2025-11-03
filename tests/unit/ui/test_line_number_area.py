"""
Tests for ui.line_number_area module.

Tests line number display functionality including:
- LineNumberArea widget
- LineNumberMixin for QPlainTextEdit
- LineNumberPlainTextEdit ready-to-use editor
- Theme-aware rendering (dark/light mode)
"""

import pytest
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QContextMenuEvent, QPaintEvent, QResizeEvent
from PySide6.QtWidgets import QPlainTextEdit
from unittest.mock import Mock, MagicMock, patch

from asciidoc_artisan.ui.line_number_area import (
    LineNumberArea,
    LineNumberMixin,
    LineNumberPlainTextEdit,
)


class TestLineNumberArea:
    """Test LineNumberArea widget."""

    def test_initialization(self, qapp):
        """Test LineNumberArea initializes with editor."""
        editor = QPlainTextEdit()
        area = LineNumberArea(editor)

        assert area.editor is editor
        assert area.parent() is editor

    def test_size_hint(self, qapp):
        """Test size hint returns width from editor."""
        editor = QPlainTextEdit()

        # Mock line_number_area_width method
        editor.line_number_area_width = Mock(return_value=50)

        area = LineNumberArea(editor)
        size = area.sizeHint()

        assert isinstance(size, QSize)
        assert size.width() == 50
        assert size.height() == 0

    def test_paint_event_delegates_to_editor(self, qapp):
        """Test paint event delegates to editor's paint method."""
        editor = QPlainTextEdit()
        editor.line_number_area_paint_event = Mock()

        area = LineNumberArea(editor)
        event = Mock(spec=QPaintEvent)

        area.paintEvent(event)

        editor.line_number_area_paint_event.assert_called_once_with(event)


class TestLineNumberMixin:
    """Test LineNumberMixin functionality."""

    def test_setup_line_numbers(self, qapp):
        """Test setup_line_numbers creates area and connects signals."""
        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Line number area should be created
        assert hasattr(editor, 'line_number_area')
        assert isinstance(editor.line_number_area, LineNumberArea)
        assert editor.line_number_area.editor is editor

    def test_line_number_area_width_single_digit(self, qapp):
        """Test width calculation for single digit line numbers."""
        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Set text with less than 10 lines
        editor.setPlainText("Line 1\nLine 2\nLine 3")

        width = editor.line_number_area_width()

        # Width should be: 3px + (1 digit * char_width) + 3px
        assert width > 0
        assert isinstance(width, int)

    def test_line_number_area_width_double_digit(self, qapp):
        """Test width calculation for double digit line numbers."""
        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Set text with more than 10 lines
        lines = "\n".join([f"Line {i}" for i in range(1, 15)])
        editor.setPlainText(lines)

        width = editor.line_number_area_width()

        # Width should accommodate 2 digits
        assert width > 0
        assert isinstance(width, int)

    def test_line_number_area_width_triple_digit(self, qapp):
        """Test width calculation for triple digit line numbers."""
        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Set text with more than 100 lines
        lines = "\n".join([f"Line {i}" for i in range(1, 105)])
        editor.setPlainText(lines)

        width = editor.line_number_area_width()

        # Width should accommodate 3 digits
        assert width > 0
        assert isinstance(width, int)

    def test_update_line_number_area_width(self, qapp):
        """Test updating viewport margins."""
        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Trigger update
        editor.update_line_number_area_width(0)

        # Viewport margins should be set
        margins = editor.viewportMargins()
        assert margins.left() > 0  # Line number area width

    def test_update_line_number_area_with_scroll(self, qapp):
        """Test updating area when scrolling."""
        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Mock scroll method
        editor.line_number_area.scroll = Mock()

        rect = QRect(0, 0, 100, 100)
        dy = 10  # Scrolled down

        editor.update_line_number_area(rect, dy)

        # Should call scroll with dy offset
        editor.line_number_area.scroll.assert_called_once_with(0, dy)

    def test_update_line_number_area_without_scroll(self, qapp):
        """Test updating area without scrolling."""
        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Mock update method
        editor.line_number_area.update = Mock()

        rect = QRect(0, 10, 100, 50)
        dy = 0  # No scroll

        editor.update_line_number_area(rect, dy)

        # Should call update with rect parameters
        editor.line_number_area.update.assert_called_once()
        call_args = editor.line_number_area.update.call_args[0]
        assert call_args[0] == 0  # x
        assert call_args[1] == rect.y()  # y
        assert call_args[2] == editor.line_number_area.width()  # width
        assert call_args[3] == rect.height()  # height

    def test_resize_event_repositions_area(self, qapp):
        """Test resize event repositions line number area."""
        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Trigger resize
        editor.resize(400, 300)
        event = QResizeEvent(editor.size(), editor.size())
        editor.resizeEvent(event)

        # Line number area should be positioned on left side
        geometry = editor.line_number_area.geometry()
        assert geometry.left() == editor.contentsRect().left()
        assert geometry.top() == editor.contentsRect().top()
        assert geometry.height() == editor.contentsRect().height()

    def test_paint_event_dark_mode(self, qapp):
        """Test painting line numbers in dark mode."""
        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Set dark palette
        palette = editor.palette()
        palette.setColor(editor.backgroundRole(), QColor(30, 30, 30))
        editor.setPalette(palette)

        # Add some text
        editor.setPlainText("Line 1\nLine 2\nLine 3")

        # Mock painter
        with patch('asciidoc_artisan.ui.line_number_area.QPainter') as mock_painter_class:
            mock_painter = Mock()
            mock_painter_class.return_value = mock_painter

            event = Mock(spec=QPaintEvent)
            event.rect.return_value = QRect(0, 0, 50, 100)

            editor.line_number_area_paint_event(event)

            # Should have painted background with dark colors
            assert mock_painter.fillRect.called
            # Should have drawn text
            assert mock_painter.drawText.called

    def test_paint_event_light_mode(self, qapp):
        """Test painting line numbers in light mode."""
        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Set light palette
        palette = editor.palette()
        palette.setColor(editor.backgroundRole(), QColor(255, 255, 255))
        editor.setPalette(palette)

        # Add some text
        editor.setPlainText("Line 1\nLine 2\nLine 3")

        # Mock painter
        with patch('asciidoc_artisan.ui.line_number_area.QPainter') as mock_painter_class:
            mock_painter = Mock()
            mock_painter_class.return_value = mock_painter

            event = Mock(spec=QPaintEvent)
            event.rect.return_value = QRect(0, 0, 50, 100)

            editor.line_number_area_paint_event(event)

            # Should have painted background with light colors
            assert mock_painter.fillRect.called
            # Should have drawn text
            assert mock_painter.drawText.called


class TestLineNumberPlainTextEdit:
    """Test LineNumberPlainTextEdit ready-to-use editor."""

    def test_initialization(self, qapp):
        """Test LineNumberPlainTextEdit initializes correctly."""
        editor = LineNumberPlainTextEdit()

        # Line numbers should be set up automatically
        assert hasattr(editor, 'line_number_area')
        assert isinstance(editor.line_number_area, LineNumberArea)

        # Spell check manager should be None initially
        assert editor.spell_check_manager is None

    def test_initialization_with_parent(self, qapp):
        """Test initialization with parent widget."""
        from PySide6.QtWidgets import QWidget

        parent = QWidget()
        editor = LineNumberPlainTextEdit(parent)

        assert editor.parent() is parent

    def test_context_menu_with_spell_checker(self, qapp):
        """Test context menu delegates to spell checker when available."""
        editor = LineNumberPlainTextEdit()

        # Set up mock spell check manager
        mock_spell_checker = Mock()
        mock_spell_checker.show_context_menu = Mock()
        editor.spell_check_manager = mock_spell_checker

        # Trigger context menu
        event = Mock(spec=QContextMenuEvent)
        editor.contextMenuEvent(event)

        # Should delegate to spell checker
        mock_spell_checker.show_context_menu.assert_called_once_with(event)

    def test_context_menu_without_spell_checker(self, qapp):
        """Test context menu uses default when spell checker not available."""
        editor = LineNumberPlainTextEdit()

        # No spell check manager set
        assert editor.spell_check_manager is None

        # Mock parent contextMenuEvent
        with patch.object(QPlainTextEdit, 'contextMenuEvent') as mock_super:
            event = Mock(spec=QContextMenuEvent)
            editor.contextMenuEvent(event)

            # Should call parent's context menu
            mock_super.assert_called_once_with(event)

    def test_line_numbers_update_with_text(self, qapp):
        """Test line numbers update when text changes."""
        editor = LineNumberPlainTextEdit()

        # Start with a few lines
        editor.setPlainText("Line 1\nLine 2\nLine 3")
        initial_width = editor.line_number_area_width()

        # Add many more lines to require more digits
        lines = "\n".join([f"Line {i}" for i in range(1, 105)])
        editor.setPlainText(lines)
        new_width = editor.line_number_area_width()

        # Width should increase for triple digit line numbers
        assert new_width > initial_width

    def test_line_numbers_visible(self, qapp):
        """Test line number area is visible."""
        editor = LineNumberPlainTextEdit()
        editor.setPlainText("Line 1\nLine 2\nLine 3")
        editor.show()

        # Line number area should be visible
        assert editor.line_number_area.isVisible()

    def test_viewport_margins_set(self, qapp):
        """Test viewport margins are set for line numbers."""
        editor = LineNumberPlainTextEdit()
        editor.setPlainText("Line 1\nLine 2")

        # Viewport should have left margin for line numbers
        margins = editor.viewportMargins()
        assert margins.left() > 0

    def test_line_number_area_geometry(self, qapp):
        """Test line number area has correct geometry."""
        editor = LineNumberPlainTextEdit()
        editor.resize(400, 300)
        editor.setPlainText("Line 1\nLine 2")

        geometry = editor.line_number_area.geometry()

        # Should be on left side
        assert geometry.left() <= 1  # At left edge (0) or just inside frame (1)
        # Should have non-zero width for line numbers
        assert geometry.width() > 0
        # Line number area should exist and be positioned
        assert geometry.x() >= 0
        assert geometry.y() >= 0
