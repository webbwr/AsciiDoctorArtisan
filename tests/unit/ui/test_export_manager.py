"""Tests for ui.export_manager module."""

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit
from unittest.mock import Mock, patch


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window(qapp):
    window = QMainWindow()
    # ExportManager expects these attributes from main_window
    window.editor = QPlainTextEdit()
    window.status_bar = Mock()
    window.status_bar.showMessage = Mock()
    window.status_manager = Mock()
    window._settings_manager = Mock()
    window._settings = Mock()
    window._asciidoc_api = Mock()
    return window


class TestExportManager:
    """Test suite for ExportManager."""

    def test_import(self):
        from asciidoc_artisan.ui.export_manager import ExportManager
        assert ExportManager is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        assert manager is not None

    def test_export_methods_exist(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        export_methods = [m for m in dir(manager) if "export" in m.lower()]
        assert len(export_methods) > 0

    def test_supported_formats(self, main_window):
        from asciidoc_artisan.ui.export_manager import ExportManager
        manager = ExportManager(main_window)
        # Should support common formats: PDF, DOCX, HTML, MD
        if hasattr(manager, "supported_formats") or hasattr(manager, "formats"):
            formats = getattr(manager, "supported_formats", getattr(manager, "formats", []))
            assert len(formats) > 0
