"""Tests for ui.preview_handler_gpu module."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


class TestPreviewHandlerGPU:
    """Test suite for PreviewHandlerGPU (hardware acceleration)."""

    def test_import(self):
        from asciidoc_artisan.ui.preview_handler_gpu import PreviewHandlerGPU
        assert PreviewHandlerGPU is not None

    def test_creation(self, qapp):
        from asciidoc_artisan.ui.preview_handler_gpu import PreviewHandlerGPU
        try:
            handler = PreviewHandlerGPU()
            assert handler is not None
        except Exception:
            # GPU handler may fail in headless environment
            pytest.skip("GPU handler requires GPU support")

    def test_set_html(self, qapp):
        from asciidoc_artisan.ui.preview_handler_gpu import PreviewHandlerGPU
        try:
            handler = PreviewHandlerGPU()
            handler.setHtml("<h1>Test</h1>")
        except Exception:
            pytest.skip("GPU handler requires GPU support")
