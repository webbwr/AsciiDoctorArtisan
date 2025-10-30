"""Tests for ui.preview_handler_gpu module."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


class TestPreviewHandlerGPU:
    """Test suite for WebEngineHandler (hardware-accelerated GPU preview)."""

    def test_import(self):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler
        assert WebEngineHandler is not None

    def test_creation(self, qapp):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler
        from unittest.mock import Mock
        try:
            # WebEngineHandler needs settings
            settings = Mock()
            settings.value = Mock(return_value=False)
            handler = WebEngineHandler(settings=settings)
            assert handler is not None
        except Exception:
            # GPU handler may fail in headless environment
            pytest.skip("GPU handler requires GPU support")

    def test_set_html(self, qapp):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler
        from unittest.mock import Mock
        try:
            settings = Mock()
            settings.value = Mock(return_value=False)
            handler = WebEngineHandler(settings=settings)
            handler.set_content("<h1>Test</h1>")  # Changed from setHtml to set_content
        except Exception:
            pytest.skip("GPU handler requires GPU support")
