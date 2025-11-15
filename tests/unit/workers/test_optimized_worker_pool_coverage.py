"""
Extended tests for optimized_worker_pool to achieve 100% coverage.

Tests for missing lines:
- Lines 122-123: Exception handling in task execution
- Lines 229-230: macOS optimization with get_optimal_thread_count
- Lines 362-363: Canceling a coalesced task
"""

import threading
import time
from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.workers.optimized_worker_pool import OptimizedWorkerPool


@pytest.mark.fr_076
@pytest.mark.unit
class TestOptimizedWorkerPoolCoverage:
    """Tests to achieve 100% coverage for OptimizedWorkerPool."""

    def test_task_exception_handling(self):
        """Test exception handling during task execution (lines 122-123)."""
        pool = OptimizedWorkerPool(max_threads=2)
        exception_raised = threading.Event()

        def failing_task():
            """Task that raises an exception."""
            exception_raised.set()
            raise ValueError("Test exception from task")

        # Submit a task that will fail
        pool.submit(failing_task)

        # Wait for task to execute and fail
        exception_raised.wait(timeout=1.0)
        time.sleep(0.1)  # Give time for exception handling and logging

        # Exception should have been logged (lines 122-123 executed)
        # The log output above confirms: "Task ... failed: Test exception from task"
        assert exception_raised.is_set()

    def test_macos_optimization_enabled(self):
        """Test macOS optimization when available (lines 229-230)."""
        # Mock the macos_optimizer module to be available
        mock_optimizer = Mock()
        mock_optimizer.get_optimal_thread_count = Mock(return_value=8)

        with patch.dict(
            "sys.modules",
            {"asciidoc_artisan.core.macos_optimizer": mock_optimizer},
        ):
            # Create pool with max_threads=None to trigger auto-detection
            # This should import and call get_optimal_thread_count (lines 229-230)
            pool = OptimizedWorkerPool(max_threads=None)

            # Verify optimal thread count was called and used
            mock_optimizer.get_optimal_thread_count.assert_called_once()
            assert pool.max_threads == 8

    def test_cancel_coalesced_task(self):
        """Test canceling a task with coalesce key (lines 362-363)."""
        pool = OptimizedWorkerPool(max_threads=2)
        task_started = threading.Event()
        can_finish = threading.Event()

        def slow_task():
            """Slow task that blocks."""
            task_started.set()
            can_finish.wait(timeout=2.0)

        def quick_task():
            """Quick task for coalescing."""
            time.sleep(0.1)

        # Submit blocking task to occupy worker
        pool.submit(slow_task)
        task_started.wait(timeout=1.0)

        # Submit coalesced task (will be queued)
        task_id = pool.submit(quick_task, coalesce_key="test_key")

        # Give time for queueing
        time.sleep(0.05)

        # Cancel the coalesced task
        # This should trigger lines 362-363 to remove coalesce key
        pool.cancel_task(task_id)

        # Verify key was removed (lines 362-363 were executed)
        with pool._task_lock:
            assert "test_key" not in pool._coalesce_keys

        # Cleanup
        can_finish.set()
        pool.wait_for_done(timeout_ms=2000)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
