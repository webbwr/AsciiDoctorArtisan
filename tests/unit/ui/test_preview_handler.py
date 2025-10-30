"""Tests for ui.preview_handler module."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


class TestPreviewHandler:
    """Test suite for PreviewHandler (software rendering)."""

    def test_import(self):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        assert PreviewHandler is not None

    def test_creation(self, qapp):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler()
        assert handler is not None

    def test_set_html(self, qapp):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler()
        handler.setHtml("<h1>Test</h1>")
        # Should not raise exception

    def test_is_widget(self, qapp):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        from PySide6.QtWidgets import QWidget
        handler = PreviewHandler()
        assert isinstance(handler, QWidget)
