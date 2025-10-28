"""Tests for ui.worker_manager module."""

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


class TestWorkerManager:
    """Test suite for WorkerManager."""

    def test_import(self):
        from asciidoc_artisan.ui.worker_manager import WorkerManager
        assert WorkerManager is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.worker_manager import WorkerManager
        manager = WorkerManager(main_window)
        assert manager is not None

    def test_worker_lifecycle_methods(self, main_window):
        from asciidoc_artisan.ui.worker_manager import WorkerManager
        manager = WorkerManager(main_window)
        # Should have methods for worker lifecycle
        methods = [m for m in dir(manager) if any(x in m.lower() for x in ["start", "stop", "worker"])]
        assert len(methods) > 0
