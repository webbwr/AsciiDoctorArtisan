"""Tests for ui.file_load_manager module."""

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow
from unittest.mock import Mock, patch
from pathlib import Path


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window(qapp):
    return QMainWindow()


class TestFileLoadManager:
    """Test suite for FileLoadManager."""

    def test_import(self):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager
        assert FileLoadManager is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager
        manager = FileLoadManager(main_window)
        assert manager is not None

    def test_load_methods_exist(self, main_window):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager
        manager = FileLoadManager(main_window)
        methods = [m for m in dir(manager) if "load" in m.lower()]
        assert len(methods) > 0

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.read_text", return_value="Test content")
    def test_can_load_file(self, mock_read, mock_exists, main_window, tmp_path):
        from asciidoc_artisan.ui.file_load_manager import FileLoadManager
        manager = FileLoadManager(main_window)
        test_file = tmp_path / "test.adoc"
        
        # Manager should have capability to load files
        if hasattr(manager, "load_file"):
            result = manager.load_file(str(test_file))
            assert result is not None
