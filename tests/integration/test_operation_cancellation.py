"""
Tests for Operation Cancellation System (v1.5.0-C).

Tests the cancellation infrastructure including:
- Cancellation methods in WorkerManager
- Cancellation support in GitWorker

Note: StatusManager UI tests are skipped due to Qt widget creation
issues in headless environments (WSL2). UI functionality should be
tested manually or in a GUI test environment.
"""

import pytest
from unittest.mock import Mock

from asciidoc_artisan.workers import GitWorker
from asciidoc_artisan.core import GitResult


@pytest.mark.integration
class TestWorkerManagerCancellation:
    """Test cancellation methods in WorkerManager."""

    def test_worker_manager_has_cancel_methods(self):
        """Test that WorkerManager has all cancel methods."""
        editor = Mock()

        from asciidoc_artisan.ui.worker_manager import WorkerManager

        worker_mgr = WorkerManager(editor, use_worker_pool=False)

        # Verify cancel methods exist
        assert hasattr(worker_mgr, "cancel_git_operation")
        assert hasattr(worker_mgr, "cancel_pandoc_operation")
        assert hasattr(worker_mgr, "cancel_preview_operation")

    def test_cancel_git_operation_calls_worker(self):
        """Test that cancel_git_operation calls worker's cancel method."""
        editor = Mock()

        from asciidoc_artisan.ui.worker_manager import WorkerManager

        worker_mgr = WorkerManager(editor, use_worker_pool=False)

        # Mock git worker with cancel method
        worker_mgr.git_worker = Mock()
        worker_mgr.git_worker.cancel = Mock()

        # Call cancel
        worker_mgr.cancel_git_operation()

        # Verify worker's cancel was called
        worker_mgr.git_worker.cancel.assert_called_once()


@pytest.mark.integration
class TestGitWorkerCancellation:
    """Test cancellation support in GitWorker."""

    def test_git_worker_has_cancel_method(self):
        """Test that GitWorker has cancel functionality."""
        worker = GitWorker()

        # Verify cancel infrastructure
        assert hasattr(worker, "cancel")
        assert hasattr(worker, "reset_cancellation")
        assert hasattr(worker, "_cancelled")
        assert worker._cancelled is False

    def test_git_worker_cancel_sets_flag(self):
        """Test that calling cancel() sets the cancellation flag."""
        worker = GitWorker()

        # Initially not cancelled
        assert not worker._cancelled

        # Cancel
        worker.cancel()

        # Now cancelled
        assert worker._cancelled

    def test_git_worker_reset_cancellation(self):
        """Test that reset_cancellation() clears the flag."""
        worker = GitWorker()

        # Cancel then reset
        worker.cancel()
        assert worker._cancelled

        worker.reset_cancellation()
        assert not worker._cancelled

    def test_git_worker_checks_cancellation_before_execution(self):
        """Test that GitWorker checks cancellation flag before running command."""
        worker = GitWorker()

        # Mock signal emission
        result_received = []

        def capture_result(result):
            result_received.append(result)

        worker.command_complete.connect(capture_result)

        # Cancel before running command
        worker.cancel()

        # Try to run command
        worker.run_git_command(["git", "status"], "/tmp")

        # Verify command was cancelled
        assert len(result_received) == 1
        result = result_received[0]
        assert isinstance(result, GitResult)
        assert not result.success
        assert "cancelled" in result.stderr.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
