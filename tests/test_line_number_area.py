"""Tests for ui.line_number_area module."""

import pytest
from PySide6.QtWidgets import QApplication, QPlainTextEdit


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


class TestLineNumberArea:
    """Test suite for LineNumberArea."""

    def test_import(self):
        from asciidoc_artisan.ui.line_number_area import LineNumberArea
        assert LineNumberArea is not None

    def test_creation(self, qapp):
        from asciidoc_artisan.ui.line_number_area import LineNumberArea, CodeEditor
        editor = CodeEditor()
        # LineNumberArea is typically created automatically by CodeEditor
        assert hasattr(editor, "lineNumberArea") or hasattr(editor, "line_number_area")
