"""Tests for ui.preview_handler module."""

import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser, QMainWindow


@pytest.fixture
def mock_editor(qapp):
    """Create mock editor widget."""
    return QPlainTextEdit()


@pytest.fixture
def mock_preview(qapp):
    """Create mock preview widget."""
    return QTextBrowser()


@pytest.fixture
def mock_window(qapp):
    """Create mock parent window."""
    return QMainWindow()


class TestPreviewHandler:
    """Test suite for PreviewHandler (software rendering)."""

    def test_import(self):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        assert PreviewHandler is not None

    def test_creation(self, mock_editor, mock_preview, mock_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_window)
        assert handler is not None

    def test_clear_preview(self, mock_editor, mock_preview, mock_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_window)
        handler.clear_preview()
        # Should not raise exception

    def test_is_qobject(self, mock_editor, mock_preview, mock_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        from PySide6.QtCore import QObject
        handler = PreviewHandler(mock_editor, mock_preview, mock_window)
        assert isinstance(handler, QObject)
