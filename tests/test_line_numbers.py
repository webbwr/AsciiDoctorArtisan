"""
Tests for line number functionality.

Tests the LineNumberPlainTextEdit widget and line number display.
"""

import pytest

from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit


def test_line_number_widget_creation(qtbot):
    """Test that LineNumberPlainTextEdit can be created."""
    editor = LineNumberPlainTextEdit()
    qtbot.addWidget(editor)
    assert editor is not None
    assert hasattr(editor, "line_number_area")


def test_line_number_area_width(qtbot):
    """Test that line number area width is calculated correctly."""
    editor = LineNumberPlainTextEdit()
    qtbot.addWidget(editor)
    width = editor.line_number_area_width()
    assert width > 0
    assert isinstance(width, int)


def test_line_numbers_with_text(qtbot):
    """Test line numbers with actual text content."""
    editor = LineNumberPlainTextEdit()
    qtbot.addWidget(editor)
    editor.setPlainText("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")

    # Should have 5 blocks
    assert editor.blockCount() == 5

    # Width should be sufficient for 1-digit line numbers
    width = editor.line_number_area_width()
    assert width > 10  # Should be at least 10 pixels


def test_line_numbers_with_many_lines(qtbot):
    """Test line numbers with 100+ lines (multi-digit)."""
    editor = LineNumberPlainTextEdit()
    qtbot.addWidget(editor)

    # Create 100 lines
    text = "\n".join([f"Line {i+1}" for i in range(100)])
    editor.setPlainText(text)

    # Should have 100 blocks
    assert editor.blockCount() == 100

    # Width should increase for 3-digit line numbers
    width = editor.line_number_area_width()
    assert width > 15  # Should be wider for 3 digits


def test_line_number_area_paint(qtbot):
    """Test that line number area can be painted."""
    editor = LineNumberPlainTextEdit()
    qtbot.addWidget(editor)
    editor.setPlainText("Test line")

    # Line number area should exist
    assert editor.line_number_area is not None

    # Should have paint event handler
    assert hasattr(editor, "line_number_area_paint_event")


def test_viewport_margins(qtbot):
    """Test that viewport margins are set for line numbers."""
    editor = LineNumberPlainTextEdit()
    qtbot.addWidget(editor)

    # Get viewport margins
    margins = editor.viewportMargins()

    # Left margin should be set for line numbers
    assert margins.left() > 0


def test_line_number_updates_on_text_change(qtbot):
    """Test that line numbers update when text changes."""
    editor = LineNumberPlainTextEdit()
    qtbot.addWidget(editor)

    # Start with one line
    editor.setPlainText("One line")
    initial_width = editor.line_number_area_width()

    # Add many lines to trigger width change
    text = "\n".join([f"Line {i+1}" for i in range(1000)])
    editor.setPlainText(text)
    new_width = editor.line_number_area_width()

    # Width should increase for 4-digit line numbers
    assert new_width > initial_width
