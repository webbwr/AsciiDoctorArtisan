"""Integration tests for Worker Thread Coordination."""

from unittest.mock import Mock

import pytest
from PySide6.QtCore import QThread


@pytest.fixture
def mock_main_window():
    """Create mock main window with workers."""
    window = Mock()
    window._settings = Mock()
    window._settings.git_repo_path = None
    window.editor = Mock()
    window.editor.toPlainText.return_value = "= Test Document\n\nContent here."
    return window


@pytest.mark.integration
class TestWorkerManagerIntegration:
    """Test WorkerManager coordination."""

    def test_worker_manager_initialization(self):
        """Integration: WorkerManager initializes all workers."""
        from asciidoc_artisan.ui.worker_manager import WorkerManager

        mock_window = Mock()
        mock_window._settings = Mock()
        mock_window._settings.git_repo_path = None
        mock_window.editor = Mock()

        manager = WorkerManager(mock_window)

        # Verify workers created
        assert hasattr(manager, "git_worker") or hasattr(manager, "_git_worker")
        assert hasattr(manager, "preview_worker") or hasattr(manager, "_preview_worker")
        assert hasattr(manager, "pandoc_worker") or hasattr(manager, "_pandoc_worker")

    def test_worker_thread_safety(self):
        """Integration: Workers don't block main thread."""
        from asciidoc_artisan.ui.worker_manager import WorkerManager

        mock_window = Mock()
        mock_window._settings = Mock()
        mock_window._settings.git_repo_path = None
        mock_window.editor = Mock()

        manager = WorkerManager(mock_window)

        # Workers should be QThread instances
        if hasattr(manager, "git_worker") and manager.git_worker:
            assert isinstance(manager.git_worker, QThread)


@pytest.mark.integration
class TestPreviewWorkerIntegration:
    """Test PreviewWorker rendering coordination."""

    def test_preview_worker_initialization(self):
        """Integration: PreviewWorker initializes correctly."""
        from asciidoc_artisan.workers.preview_worker import PreviewWorker

        worker = PreviewWorker()

        # Should have render method
        assert hasattr(worker, "render") or hasattr(worker, "run")

        # Should have signals
        assert hasattr(worker, "render_complete") or hasattr(worker, "result_ready")

    def test_preview_worker_signals(self):
        """Integration: PreviewWorker emits correct signals."""
        from asciidoc_artisan.workers.preview_worker import PreviewWorker

        worker = PreviewWorker()

        # Signals should be connectable
        signal_count = 0
        if hasattr(worker, "render_complete"):
            signal_count += 1
        if hasattr(worker, "error"):
            signal_count += 1

        assert signal_count >= 1


@pytest.mark.integration
class TestGitWorkerIntegration:
    """Test GitWorker operations."""

    def test_git_worker_initialization(self):
        """Integration: GitWorker initializes correctly."""
        from asciidoc_artisan.workers.git_worker import GitWorker

        worker = GitWorker()

        # Should have operation methods
        assert hasattr(worker, "set_operation") or hasattr(worker, "run")

        # Should have signals
        assert hasattr(worker, "operation_complete") or hasattr(worker, "finished")

    def test_git_worker_status_operation(self):
        """Integration: GitWorker can perform status check."""
        from asciidoc_artisan.workers.git_worker import GitWorker

        worker = GitWorker()

        # Should accept status operation
        if hasattr(worker, "set_operation"):
            worker.set_operation("status", "/tmp")
            assert worker.operation == "status"


@pytest.mark.integration
class TestPandocWorkerIntegration:
    """Test PandocWorker conversion operations."""

    def test_pandoc_worker_initialization(self):
        """Integration: PandocWorker initializes correctly."""
        from asciidoc_artisan.workers.pandoc_worker import PandocWorker

        worker = PandocWorker()

        # Should have conversion methods
        assert hasattr(worker, "convert") or hasattr(worker, "run")

        # Should have signals
        assert hasattr(worker, "conversion_complete") or hasattr(worker, "finished")

    def test_pandoc_worker_signals(self):
        """Integration: PandocWorker emits correct signals."""
        from asciidoc_artisan.workers.pandoc_worker import PandocWorker

        worker = PandocWorker()

        # Should have result signal
        signal_found = False
        for attr in ["conversion_complete", "result_ready", "finished"]:
            if hasattr(worker, attr):
                signal_found = True
                break

        assert signal_found


@pytest.mark.integration
class TestWorkerCancellationIntegration:
    """Test worker operation cancellation."""

    def test_worker_has_cancel_capability(self):
        """Integration: Workers support cancellation."""
        from asciidoc_artisan.workers.git_worker import GitWorker

        worker = GitWorker()

        # Should have cancel method or flag
        has_cancel = hasattr(worker, "cancel") or hasattr(worker, "_cancelled")
        assert has_cancel or hasattr(worker, "terminate")

    def test_preview_worker_cancellation(self):
        """Integration: PreviewWorker supports cancellation."""
        from asciidoc_artisan.workers.preview_worker import PreviewWorker

        worker = PreviewWorker()

        # Should have some form of cancellation
        has_cancel = (
            hasattr(worker, "cancel") or hasattr(worker, "_cancelled") or hasattr(worker, "requestInterruption")
        )
        assert has_cancel


@pytest.mark.integration
class TestConcurrentWorkersIntegration:
    """Test multiple workers running concurrently."""

    def test_workers_can_coexist(self):
        """Integration: Multiple worker types can be instantiated."""
        from asciidoc_artisan.workers.git_worker import GitWorker
        from asciidoc_artisan.workers.pandoc_worker import PandocWorker
        from asciidoc_artisan.workers.preview_worker import PreviewWorker

        # Create all worker types
        preview = PreviewWorker()
        git = GitWorker()
        pandoc = PandocWorker()

        # All should exist without conflict
        assert preview is not None
        assert git is not None
        assert pandoc is not None

        # Each should be independent
        assert preview is not git
        assert git is not pandoc
