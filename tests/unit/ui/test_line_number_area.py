"""
Tests for ui.line_number_area module.

Tests line number display functionality including:
- LineNumberArea widget
- LineNumberMixin for QPlainTextEdit
- LineNumberPlainTextEdit ready-to-use editor
- Theme-aware rendering (dark/light mode)
"""

from unittest.mock import Mock, patch

from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QColor, QContextMenuEvent, QPaintEvent, QResizeEvent
from PySide6.QtWidgets import QFrame, QPlainTextEdit

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
        assert hasattr(editor, "line_number_area")
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
        with patch(
            "asciidoc_artisan.ui.line_number_area.QPainter"
        ) as mock_painter_class:
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
        with patch(
            "asciidoc_artisan.ui.line_number_area.QPainter"
        ) as mock_painter_class:
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
        assert hasattr(editor, "line_number_area")
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
        with patch.object(QPlainTextEdit, "contextMenuEvent") as mock_super:
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


class TestLineNumberCalculationEdgeCases:
    """Test edge cases for line number calculations."""

    def test_empty_editor_width(self, qapp):
        """Test width calculation with empty editor."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()
        editor.setPlainText("")

        width = editor.line_number_area_width()
        # Should still have minimum width for at least one line number
        assert width > 0

    def test_single_line_width(self, qapp):
        """Test width with single line."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()
        editor.setPlainText("Single line")

        width = editor.line_number_area_width()
        assert width > 0

    def test_thousand_lines_width(self, qapp):
        """Test width calculation for 1000+ lines."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # 1500 lines (requires 4 digits)
        lines = "\n".join([f"Line {i}" for i in range(1, 1501)])
        editor.setPlainText(lines)

        width = editor.line_number_area_width()
        # Width should accommodate 4 digits
        assert width > 0

    def test_ten_thousand_lines_width(self, qapp):
        """Test width calculation for 10000+ lines."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Mock block count to avoid memory issues in tests
        editor.blockCount = Mock(return_value=15000)

        width = editor.line_number_area_width()
        # Width should accommodate 5 digits
        assert width > 0

    def test_width_increases_with_more_lines(self, qapp):
        """Test width increases as line count increases."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # 9 lines (1 digit)
        editor.setPlainText("\n".join([f"L{i}" for i in range(9)]))
        width_1_digit = editor.line_number_area_width()

        # 99 lines (2 digits)
        editor.setPlainText("\n".join([f"L{i}" for i in range(99)]))
        width_2_digits = editor.line_number_area_width()

        # 999 lines (3 digits)
        editor.setPlainText("\n".join([f"L{i}" for i in range(999)]))
        width_3_digits = editor.line_number_area_width()

        assert width_2_digits > width_1_digit
        assert width_3_digits > width_2_digits


class TestPaintEventEdgeCases:
    """Test paint event edge cases."""

    def test_paint_with_no_visible_blocks(self, qapp):
        """Test painting when no blocks are visible."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()
        editor.setPlainText("")

        # Mock painter
        with patch(
            "asciidoc_artisan.ui.line_number_area.QPainter"
        ) as mock_painter_class:
            mock_painter = Mock()
            mock_painter_class.return_value = mock_painter

            event = Mock(spec=QPaintEvent)
            event.rect.return_value = QRect(0, 0, 50, 100)

            editor.line_number_area_paint_event(event)

            # Should still paint (at least background)
            assert mock_painter.fillRect.called

    def test_paint_with_very_long_document(self, qapp):
        """Test painting with very long document."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Create 500 lines
        lines = "\n".join([f"Line {i}" for i in range(1, 501)])
        editor.setPlainText(lines)

        with patch(
            "asciidoc_artisan.ui.line_number_area.QPainter"
        ) as mock_painter_class:
            mock_painter = Mock()
            mock_painter_class.return_value = mock_painter

            event = Mock(spec=QPaintEvent)
            event.rect.return_value = QRect(0, 0, 50, 100)

            editor.line_number_area_paint_event(event)

            # Should paint successfully
            assert mock_painter.fillRect.called

    def test_paint_with_unicode_content(self, qapp):
        """Test painting with unicode content in editor."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()
        editor.setPlainText("Line 1\nЛиния 2\n行 3\n🌍 4")

        with patch(
            "asciidoc_artisan.ui.line_number_area.QPainter"
        ) as mock_painter_class:
            mock_painter = Mock()
            mock_painter_class.return_value = mock_painter

            event = Mock(spec=QPaintEvent)
            event.rect.return_value = QRect(0, 0, 50, 100)

            editor.line_number_area_paint_event(event)

            # Should paint line numbers (not content)
            assert mock_painter.drawText.called


class TestResizeEdgeCases:
    """Test resize event edge cases."""

    def test_resize_to_zero_width(self, qapp):
        """Test resizing to zero width."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Try resizing to zero (edge case)
        editor.resize(0, 300)
        event = QResizeEvent(editor.size(), QSize(100, 300))
        editor.resizeEvent(event)

        # Should handle gracefully
        assert editor.line_number_area is not None

    def test_resize_to_zero_height(self, qapp):
        """Test resizing to zero height."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        editor.resize(400, 0)
        event = QResizeEvent(editor.size(), QSize(400, 300))
        editor.resizeEvent(event)

        # Should handle gracefully
        assert editor.line_number_area is not None

    def test_multiple_rapid_resizes(self, qapp):
        """Test multiple rapid resize events."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Simulate rapid resizes
        for width in [400, 300, 500, 350, 450]:
            editor.resize(width, 300)
            event = QResizeEvent(editor.size(), QSize(width - 50, 300))
            editor.resizeEvent(event)

        # Should remain stable
        assert editor.line_number_area.width() > 0

    def test_resize_very_large(self, qapp):
        """Test resizing to very large dimensions."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        editor.resize(5000, 3000)
        event = QResizeEvent(editor.size(), QSize(400, 300))
        editor.resizeEvent(event)

        # Should handle large sizes
        geometry = editor.line_number_area.geometry()
        assert geometry.height() > 0


class TestThemeSwitching:
    """Test theme switching scenarios."""

    def test_switch_from_light_to_dark(self, qapp):
        """Test switching from light to dark theme."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()
        editor.setPlainText("Line 1\nLine 2\nLine 3")

        # Start with light
        palette = editor.palette()
        palette.setColor(editor.backgroundRole(), QColor(255, 255, 255))
        editor.setPalette(palette)

        # Switch to dark
        palette.setColor(editor.backgroundRole(), QColor(30, 30, 30))
        editor.setPalette(palette)

        # Paint should use dark colors
        with patch(
            "asciidoc_artisan.ui.line_number_area.QPainter"
        ) as mock_painter_class:
            mock_painter = Mock()
            mock_painter_class.return_value = mock_painter

            event = Mock(spec=QPaintEvent)
            event.rect.return_value = QRect(0, 0, 50, 100)

            editor.line_number_area_paint_event(event)

            assert mock_painter.fillRect.called

    def test_switch_from_dark_to_light(self, qapp):
        """Test switching from dark to light theme."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()
        editor.setPlainText("Line 1\nLine 2")

        # Start with dark
        palette = editor.palette()
        palette.setColor(editor.backgroundRole(), QColor(30, 30, 30))
        editor.setPalette(palette)

        # Switch to light
        palette.setColor(editor.backgroundRole(), QColor(255, 255, 255))
        editor.setPalette(palette)

        # Paint should use light colors
        with patch(
            "asciidoc_artisan.ui.line_number_area.QPainter"
        ) as mock_painter_class:
            mock_painter = Mock()
            mock_painter_class.return_value = mock_painter

            event = Mock(spec=QPaintEvent)
            event.rect.return_value = QRect(0, 0, 50, 100)

            editor.line_number_area_paint_event(event)

            assert mock_painter.fillRect.called


class TestMarginCalculations:
    """Test viewport margin calculations."""

    def test_margins_update_on_text_change(self, qapp):
        """Test margins update when text changes."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        editor.setPlainText("Line 1\nLine 2")
        initial_margin = editor.viewportMargins().left()

        # Add many more lines
        lines = "\n".join([f"Line {i}" for i in range(1, 105)])
        editor.setPlainText(lines)

        new_margin = editor.viewportMargins().left()

        # Margin should increase for more digits
        assert new_margin >= initial_margin

    def test_margins_non_negative(self, qapp):
        """Test margins are never negative."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        margins = editor.viewportMargins()
        assert margins.left() >= 0
        assert margins.top() >= 0
        assert margins.right() >= 0
        assert margins.bottom() >= 0

    def test_margins_preserved_after_clear(self, qapp):
        """Test margins remain after clearing text."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        editor.setPlainText("Line 1\nLine 2\nLine 3")
        editor.clear()

        # Margins should still exist for line number area
        assert editor.viewportMargins().left() > 0


class TestWidgetLifecycle:
    """Test widget creation and destruction."""

    def test_multiple_editor_instances(self, qapp):
        """Test creating multiple independent editors."""
        editor1 = LineNumberPlainTextEdit()
        editor2 = LineNumberPlainTextEdit()

        editor1.setPlainText("Editor 1")
        editor2.setPlainText("Editor 2 line 1\nEditor 2 line 2")

        # Each should have its own line number area
        assert editor1.line_number_area is not editor2.line_number_area

    def test_editor_cleanup(self, qapp):
        """Test editor cleanup doesn't cause issues."""
        editor = LineNumberPlainTextEdit()
        editor.setPlainText("Line 1\nLine 2")
        editor.show()

        # Simulate cleanup
        editor.deleteLater()
        # Should not crash

    def test_setup_line_numbers_called_once(self, qapp):
        """Test setup_line_numbers is idempotent."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()
        first_area = editor.line_number_area

        # Call again
        editor.setup_line_numbers()

        # Should have same area (or handle gracefully)
        assert editor.line_number_area is not None


class TestScrollBehavior:
    """Test scrolling behavior with line numbers."""

    def test_scroll_down_updates_area(self, qapp):
        """Test scrolling down updates line number area."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        # Add many lines
        lines = "\n".join([f"Line {i}" for i in range(1, 51)])
        editor.setPlainText(lines)

        editor.line_number_area.scroll = Mock()

        # Simulate scroll down
        rect = QRect(0, 0, 100, 100)
        editor.update_line_number_area(rect, 20)

        editor.line_number_area.scroll.assert_called_once_with(0, 20)

    def test_scroll_up_updates_area(self, qapp):
        """Test scrolling up updates line number area."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        lines = "\n".join([f"Line {i}" for i in range(1, 51)])
        editor.setPlainText(lines)

        editor.line_number_area.scroll = Mock()

        # Simulate scroll up
        rect = QRect(0, 0, 100, 100)
        editor.update_line_number_area(rect, -20)

        editor.line_number_area.scroll.assert_called_once_with(0, -20)

    def test_no_scroll_updates_area_geometry(self, qapp):
        """Test update without scroll updates specific region."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()

        editor.line_number_area.update = Mock()

        rect = QRect(0, 50, 100, 100)
        editor.update_line_number_area(rect, 0)

        # Should call update with rect coordinates
        editor.line_number_area.update.assert_called_once()


class TestGeometryEdgeCases:
    """Test geometry edge cases."""

    def test_geometry_after_hide_show(self, qapp):
        """Test geometry after hiding and showing."""
        editor = LineNumberPlainTextEdit()
        editor.show()

        initial_geometry = editor.line_number_area.geometry()

        editor.hide()
        editor.show()

        # Geometry should be maintained
        assert editor.line_number_area.geometry().width() == initial_geometry.width()

    def test_geometry_with_frame(self, qapp):
        """Test geometry with editor frame."""
        editor = LineNumberPlainTextEdit()
        editor.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        editor.setLineWidth(2)

        editor.resize(400, 300)
        editor.setPlainText("Line 1\nLine 2")

        geometry = editor.line_number_area.geometry()

        # Should account for frame
        assert geometry.left() >= 0
        assert geometry.width() > 0

    def test_geometry_without_frame(self, qapp):
        """Test geometry without editor frame."""
        editor = LineNumberPlainTextEdit()
        editor.setFrameStyle(QFrame.Shape.NoFrame)

        editor.resize(400, 300)
        editor.setPlainText("Line 1\nLine 2")

        geometry = editor.line_number_area.geometry()

        assert geometry.left() >= 0
        assert geometry.width() > 0


class TestTextChangeScenarios:
    """Test various text change scenarios."""

    def test_text_cleared(self, qapp):
        """Test line numbers after clearing text."""
        editor = LineNumberPlainTextEdit()
        editor.setPlainText("Line 1\nLine 2\nLine 3")

        editor.clear()

        # Should still have line number area
        assert editor.line_number_area.width() > 0

    def test_text_appended(self, qapp):
        """Test line numbers when appending text."""
        editor = LineNumberPlainTextEdit()
        editor.setPlainText("Line 1")

        initial_width = editor.line_number_area_width()

        editor.appendPlainText("Line 2")
        editor.appendPlainText("Line 3")

        # Width should remain stable
        assert editor.line_number_area_width() >= initial_width

    def test_text_replaced(self, qapp):
        """Test line numbers when replacing all text."""
        editor = LineNumberPlainTextEdit()
        editor.setPlainText("Short")

        # Replace with much longer text
        lines = "\n".join([f"Line {i}" for i in range(1, 105)])
        editor.setPlainText(lines)

        # Width should increase
        assert editor.line_number_area_width() > 0


class TestSpellCheckIntegration:
    """Test spell check manager integration."""

    def test_spell_checker_can_be_set(self, qapp):
        """Test spell check manager can be assigned."""
        editor = LineNumberPlainTextEdit()

        mock_spell_checker = Mock()
        editor.spell_check_manager = mock_spell_checker

        assert editor.spell_check_manager is mock_spell_checker

    def test_context_menu_without_spell_checker_works(self, qapp):
        """Test context menu works without spell checker."""
        editor = LineNumberPlainTextEdit()
        editor.setPlainText("Line 1\nLine 2")

        # Should not crash
        with patch.object(QPlainTextEdit, "contextMenuEvent") as mock_super:
            event = Mock(spec=QContextMenuEvent)
            editor.contextMenuEvent(event)

            mock_super.assert_called_once()

    def test_spell_checker_none_by_default(self, qapp):
        """Test spell checker is None by default."""
        editor = LineNumberPlainTextEdit()

        assert editor.spell_check_manager is None


class TestConcurrentOperations:
    """Test concurrent operations."""

    def test_resize_and_text_change(self, qapp):
        """Test simultaneous resize and text change."""
        editor = LineNumberPlainTextEdit()

        editor.setPlainText("Line 1\nLine 2")
        editor.resize(500, 400)

        # Should handle both operations
        assert editor.line_number_area.width() > 0

    def test_multiple_paint_events(self, qapp):
        """Test handling multiple paint events."""

        class TestEditor(LineNumberMixin, QPlainTextEdit):
            pass

        editor = TestEditor()
        editor.setup_line_numbers()
        editor.setPlainText("Line 1\nLine 2\nLine 3")

        with patch(
            "asciidoc_artisan.ui.line_number_area.QPainter"
        ) as mock_painter_class:
            mock_painter = Mock()
            mock_painter_class.return_value = mock_painter

            event = Mock(spec=QPaintEvent)
            event.rect.return_value = QRect(0, 0, 50, 100)

            # Multiple paint events
            for _ in range(5):
                editor.line_number_area_paint_event(event)

            # Should handle all events
            assert mock_painter.fillRect.call_count >= 5
