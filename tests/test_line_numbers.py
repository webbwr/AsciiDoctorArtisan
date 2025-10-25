"""
Tests for line number functionality.

Tests the LineNumberPlainTextEdit widget and line number display.
"""

import pytest
from PySide6.QtWidgets import QApplication

from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for Qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_line_number_widget_creation(qapp):
    """Test that LineNumberPlainTextEdit can be created."""
    editor = LineNumberPlainTextEdit()
    assert editor is not None
    assert hasattr(editor, "line_number_area")


def test_line_number_area_width(qapp):
    """Test that line number area width is calculated correctly."""
    editor = LineNumberPlainTextEdit()
    width = editor.line_number_area_width()
    assert width > 0
    assert isinstance(width, int)


def test_line_numbers_with_text(qapp):
    """Test line numbers with actual text content."""
    editor = LineNumberPlainTextEdit()
    editor.setPlainText("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")

    # Should have 5 blocks
    assert editor.blockCount() == 5

    # Width should be sufficient for 1-digit line numbers
    width = editor.line_number_area_width()
    assert width > 10  # Should be at least 10 pixels


def test_line_numbers_with_many_lines(qapp):
    """Test line numbers with 100+ lines (multi-digit)."""
    editor = LineNumberPlainTextEdit()

    # Create 100 lines
    text = "\n".join([f"Line {i+1}" for i in range(100)])
    editor.setPlainText(text)

    # Should have 100 blocks
    assert editor.blockCount() == 100

    # Width should increase for 3-digit line numbers
    width = editor.line_number_area_width()
    assert width > 15  # Should be wider for 3 digits


def test_line_number_area_paint(qapp):
    """Test that line number area can be painted."""
    editor = LineNumberPlainTextEdit()
    editor.setPlainText("Test line")

    # Line number area should exist
    assert editor.line_number_area is not None

    # Should have paint event handler
    assert hasattr(editor, "line_number_area_paint_event")


def test_viewport_margins(qapp):
    """Test that viewport margins are set for line numbers."""
    editor = LineNumberPlainTextEdit()

    # Get viewport margins
    margins = editor.viewportMargins()

    # Left margin should be set for line numbers
    assert margins.left() > 0


def test_line_number_updates_on_text_change(qapp):
    """Test that line numbers update when text changes."""
    editor = LineNumberPlainTextEdit()

    # Start with one line
    editor.setPlainText("One line")
    initial_width = editor.line_number_area_width()

    # Add many lines to trigger width change
    text = "\n".join([f"Line {i+1}" for i in range(1000)])
    editor.setPlainText(text)
    new_width = editor.line_number_area_width()

    # Width should increase for 4-digit line numbers
    assert new_width > initial_width
