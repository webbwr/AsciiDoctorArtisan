"""Tests for ui.file_operations_manager module."""

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


class TestFileOperationsManager:
    """Test suite for FileOperationsManager."""

    def test_import(self):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        assert FileOperationsManager is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(main_window)
        assert manager is not None

    def test_has_file_operation_methods(self, main_window):
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        manager = FileOperationsManager(main_window)
        ops = [m for m in dir(manager) if any(x in m.lower() for x in ["save", "open", "load"])]
        assert len(ops) > 0
