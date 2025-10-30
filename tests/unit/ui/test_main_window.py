"""Tests for ui.main_window module - Integration tests for 100% coverage."""

import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import Mock, patch


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


class TestMainWindow:
    """Test suite for AsciiDocEditor main window."""

    def test_import(self):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        assert AsciiDocEditor is not None

    @patch("asciidoc_artisan.ui.main_window.GitWorker")
    @patch("asciidoc_artisan.ui.main_window.PandocWorker")
    @patch("asciidoc_artisan.ui.main_window.PreviewWorker")
    def test_creation(self, mock_preview, mock_pandoc, mock_git, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        assert window is not None
        assert window.windowTitle() != ""

    @patch("asciidoc_artisan.ui.main_window.GitWorker")
    @patch("asciidoc_artisan.ui.main_window.PandocWorker")
    @patch("asciidoc_artisan.ui.main_window.PreviewWorker")
    def test_has_editor_and_preview(self, mock_preview, mock_pandoc, mock_git, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        # Should have editor and preview widgets
        assert hasattr(window, "editor") or hasattr(window, "text_editor")
        assert hasattr(window, "preview") or hasattr(window, "preview_widget")

    @patch("asciidoc_artisan.ui.main_window.GitWorker")
    @patch("asciidoc_artisan.ui.main_window.PandocWorker")
    @patch("asciidoc_artisan.ui.main_window.PreviewWorker")
    def test_has_workers(self, mock_preview, mock_pandoc, mock_git, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        # Should have worker threads
        assert hasattr(window, "git_worker")
        assert hasattr(window, "pandoc_worker")
        assert hasattr(window, "preview_worker")

    @patch("asciidoc_artisan.ui.main_window.GitWorker")
    @patch("asciidoc_artisan.ui.main_window.PandocWorker")
    @patch("asciidoc_artisan.ui.main_window.PreviewWorker")
    def test_has_managers(self, mock_preview, mock_pandoc, mock_git, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        # Should have UI managers
        manager_attrs = [a for a in dir(window) if "manager" in a.lower()]
        assert len(manager_attrs) > 0

    @patch("asciidoc_artisan.ui.main_window.GitWorker")
    @patch("asciidoc_artisan.ui.main_window.PandocWorker")
    @patch("asciidoc_artisan.ui.main_window.PreviewWorker")
    def test_window_geometry(self, mock_preview, mock_pandoc, mock_git, qapp):
        from asciidoc_artisan.ui.main_window import AsciiDocEditor
        window = AsciiDocEditor()
        # Should have reasonable default size
        assert window.width() > 0
        assert window.height() > 0
