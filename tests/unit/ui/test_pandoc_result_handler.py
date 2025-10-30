"""Tests for ui.pandoc_result_handler module."""

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window(qapp):
    return QMainWindow()


class TestPandocResultHandler:
    """Test suite for PandocResultHandler."""

    def test_import(self):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        assert PandocResultHandler is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(main_window)
        assert handler is not None

    def test_has_result_handling_methods(self, main_window):
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler
        handler = PandocResultHandler(main_window)
        methods = [m for m in dir(handler) if "handle" in m.lower() or "result" in m.lower()]
        assert len(methods) > 0
