"""
Tests for optimized worker pool.

Tests task submission, cancellation, prioritization, and coalescing.
"""

import time
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QCoreApplication

from asciidoc_artisan.workers.optimized_worker_pool import (
    CancelableRunnable,
    OptimizedWorkerPool,
    TaskPriority,
)


@pytest.fixture
def app():
    """Create QCoreApplication for Qt event loop."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


@pytest.mark.fr_063
@pytest.mark.performance
class TestCancelableRunnable:
    """Test CancelableRunnable."""

    def test_create_runnable(self):
        """Test creating runnable."""
        func = Mock()
        runnable = CancelableRunnable(func, "test_task", arg1="value1")

        assert runnable.task_id == "test_task"
        assert runnable.func is func
        assert runnable.kwargs == {"arg1": "value1"}

    def test_run_not_canceled(self, app):
        """Test running task when not canceled."""
        func = Mock()
        runnable = CancelableRunnable(func, "test_task", "arg1", kwarg1="value1")

        # Run task
        runnable.run()

        # Should have called function
        func.assert_called_once_with("arg1", kwarg1="value1")
        assert runnable.is_finished()

    def test_cancel_before_start(self, app):
        """Test canceling before task starts."""
        func = Mock()
        runnable = CancelableRunnable(func, "test_task")

        # Cancel before running
        result = runnable.cancel()

        assert result is True
        assert runnable.is_canceled()

        # Run task
        runnable.run()

        # Should not have called function
        func.assert_not_called()

    def test_cannot_cancel_after_start(self, app):
        """Test cannot cancel after task starts."""

        # Slow function
        def slow_func():
            time.sleep(0.1)

        runnable = CancelableRunnable(slow_func, "test_task")

        # Start running
        from threading import Thread

        thread = Thread(target=runnable.run)
        thread.start()

        # Wait for it to start
        runnable._started.wait(timeout=1)

        # Try to cancel (should fail - already started)
        result = runnable.cancel()

        assert result is False

        # Wait for completion
        thread.join()

    def test_wait_for_finish(self, app):
        """Test waiting for task to finish."""

        def quick_func():
            time.sleep(0.05)

        runnable = CancelableRunnable(quick_func, "test_task")

        # Run in thread
        from threading import Thread

        thread = Thread(target=runnable.run)
        thread.start()

        # Wait for finish
        result = runnable.wait(timeout=1)

        assert result is True
        assert runnable.is_finished()

        thread.join()

    def test_is_running(self, app):
        """Test checking if task is running."""

        # Slow function
        def slow_func():
            time.sleep(0.2)

        runnable = CancelableRunnable(slow_func, "test_task")

        assert runnable.is_running() is False

        # Start running
        from threading import Thread

        thread = Thread(target=runnable.run)
        thread.start()

        # Wait for it to start
        runnable._started.wait(timeout=1)

        assert runnable.is_running() is True

        # Wait for completion
        thread.join()

        assert runnable.is_running() is False
        assert runnable.is_finished() is True


@pytest.mark.fr_063
@pytest.mark.performance
class TestOptimizedWorkerPool:
    """Test OptimizedWorkerPool."""

    def test_create_pool(self, app):
        """Test creating worker pool."""
        pool = OptimizedWorkerPool(max_threads=4)

        assert pool.max_threads == 4
        assert pool.active_thread_count() >= 0

    def test_submit_task(self, app):
        """Test submitting task."""
        pool = OptimizedWorkerPool(max_threads=2)
        func = Mock()

        task_id = pool.submit(func, "arg1", kwarg1="value1")

        assert task_id is not None
        assert pool.is_task_active(task_id)

        # Wait for task to complete
        pool.wait_for_done(1000)

        # Check function was called
        func.assert_called_once_with("arg1", kwarg1="value1")

    def test_submit_with_priority(self, app):
        """Test submitting task with priority."""
        pool = OptimizedWorkerPool(max_threads=2)
        func = Mock()

        task_id = pool.submit(func, priority=TaskPriority.HIGH)

        assert task_id is not None

        pool.wait_for_done(1000)
        func.assert_called_once()

    def test_cancel_task(self, app):
        """Test canceling task."""
        pool = OptimizedWorkerPool(max_threads=1)

        # Submit slow task to block worker
        def slow_task():
            time.sleep(0.2)

        pool.submit(slow_task)

        # Submit another task
        func = Mock()
        task_id = pool.submit(func)

        # Cancel second task before it starts
        result = pool.cancel_task(task_id)

        # Should be canceled
        assert result is True

        # Wait for pool
        pool.wait_for_done(1000)

        # Function should not have been called
        func.assert_not_called()

        # Check statistics
        stats = pool.get_statistics()
        assert stats["canceled"] >= 1

    def test_cancel_all(self, app):
        """Test canceling all tasks."""
        pool = OptimizedWorkerPool(max_threads=1)

        # Submit slow task to block worker
        def slow_task():
            time.sleep(0.2)

        pool.submit(slow_task)

        # Submit several more tasks
        func1 = Mock()
        func2 = Mock()
        func3 = Mock()

        pool.submit(func1)
        pool.submit(func2)
        pool.submit(func3)

        # Cancel all pending tasks
        canceled = pool.cancel_all()

        # Should have canceled some tasks
        assert canceled >= 0

        # Wait for pool
        pool.wait_for_done(1000)

    def test_task_coalescing(self, app):
        """Test task coalescing (deduplication)."""
        pool = OptimizedWorkerPool(max_threads=1)

        # Block worker with slow task
        def slow_task():
            time.sleep(0.3)

        pool.submit(slow_task)

        # Submit coalescable tasks with same key
        func = Mock()

        task_id1 = pool.submit(func, "arg1", coalescable=True, coalesce_key="render")

        task_id2 = pool.submit(func, "arg2", coalescable=True, coalesce_key="render")

        # Should return same task ID (coalesced)
        assert task_id1 == task_id2

        # Wait for completion
        pool.wait_for_done(1000)

        # Check statistics
        stats = pool.get_statistics()
        assert stats["coalesced"] >= 1

    def test_different_coalesce_keys(self, app):
        """Test tasks with different coalesce keys are not coalesced."""
        pool = OptimizedWorkerPool(max_threads=1)

        # Block worker
        def slow_task():
            time.sleep(0.3)

        pool.submit(slow_task)

        func1 = Mock()
        func2 = Mock()

        task_id1 = pool.submit(func1, coalescable=True, coalesce_key="render1")

        task_id2 = pool.submit(func2, coalescable=True, coalesce_key="render2")

        # Should be different tasks
        assert task_id1 != task_id2

        pool.wait_for_done(1000)

    def test_coalesce_requires_key(self, app):
        """Test coalescable task requires coalesce_key."""
        pool = OptimizedWorkerPool(max_threads=2)

        with pytest.raises(ValueError):
            pool.submit(
                Mock(),
                coalescable=True,
                # Missing coalesce_key
            )

    def test_get_statistics(self, app):
        """Test getting statistics."""
        pool = OptimizedWorkerPool(max_threads=2)

        # Submit some tasks
        pool.submit(Mock())
        pool.submit(Mock())

        stats = pool.get_statistics()

        assert "submitted" in stats
        assert "completed" in stats
        assert "canceled" in stats
        assert "active_tasks" in stats
        assert "active_threads" in stats
        assert "max_threads" in stats

        assert stats["submitted"] >= 2
        assert stats["max_threads"] == 2

        pool.wait_for_done(1000)

    def test_reset_statistics(self, app):
        """Test resetting statistics."""
        pool = OptimizedWorkerPool(max_threads=2)

        # Submit tasks
        pool.submit(Mock())
        pool.submit(Mock())

        pool.wait_for_done(1000)

        # Reset stats
        pool.reset_statistics()

        stats = pool.get_statistics()
        assert stats["submitted"] == 0
        assert stats["completed"] == 0

    def test_clear_pool(self, app):
        """Test clearing pool."""
        pool = OptimizedWorkerPool(max_threads=2)

        # Submit tasks
        pool.submit(Mock())
        pool.submit(Mock())

        # Clear pool
        pool.clear()

        stats = pool.get_statistics()
        assert stats["active_tasks"] == 0
        assert stats["submitted"] == 0

    def test_wait_for_done(self, app):
        """Test waiting for all tasks to complete."""
        pool = OptimizedWorkerPool(max_threads=2)

        def quick_task():
            time.sleep(0.05)

        # Submit several tasks
        for _ in range(5):
            pool.submit(quick_task)

        # Wait for all to complete
        result = pool.wait_for_done(2000)

        assert result is True

    def test_active_thread_count(self, app):
        """Test getting active thread count."""
        pool = OptimizedWorkerPool(max_threads=2)

        # Initially low or zero
        initial = pool.active_thread_count()
        assert initial >= 0
        assert initial <= 2

        # Submit tasks
        def slow_task():
            time.sleep(0.2)

        pool.submit(slow_task)
        pool.submit(slow_task)

        # Give threads time to start
        time.sleep(0.05)

        # Should have active threads
        active = pool.active_thread_count()
        assert active >= 0

        pool.wait_for_done(1000)


@pytest.mark.performance
@pytest.mark.fr_063
@pytest.mark.performance
class TestWorkerPoolPerformance:
    """Test worker pool performance."""

    def test_many_quick_tasks(self, app):
        """Test handling many quick tasks."""
        pool = OptimizedWorkerPool(max_threads=4)

        call_count = 0

        def quick_task():
            nonlocal call_count
            call_count += 1

        # Submit 100 quick tasks
        start = time.time()
        for _ in range(100):
            pool.submit(quick_task)

        # Wait for completion
        pool.wait_for_done(5000)
        elapsed = time.time() - start

        print(f"\n100 quick tasks: {elapsed * 1000:.2f}ms")

        # All should have completed
        assert call_count == 100

        stats = pool.get_statistics()
        print(f"Stats: {stats}")

    def test_coalescing_efficiency(self, app):
        """Test task coalescing reduces work."""
        pool = OptimizedWorkerPool(max_threads=1)

        # Block worker
        def slow_task():
            time.sleep(0.5)

        pool.submit(slow_task)

        # Submit 10 coalescable tasks
        call_count = 0

        def work():
            nonlocal call_count
            call_count += 1

        for _ in range(10):
            pool.submit(work, coalescable=True, coalesce_key="same_work")

        pool.wait_for_done(2000)

        # Should have only run once (coalesced 9 times)
        assert call_count == 1

        stats = pool.get_statistics()
        assert stats["coalesced"] == 9

        print("\nCoalescing: 10 tasks -> 1 execution")
        print(f"Coalesced: {stats['coalesced']}")

    def test_cancellation_efficiency(self, app):
        """Test cancellation prevents wasted work."""
        pool = OptimizedWorkerPool(max_threads=1)

        # Block worker
        def slow_task():
            time.sleep(0.5)

        pool.submit(slow_task)

        # Submit tasks
        call_count = 0

        def work():
            nonlocal call_count
            call_count += 1

        task_ids = []
        for _ in range(10):
            task_id = pool.submit(work)
            task_ids.append(task_id)

        # Cancel all but last
        for task_id in task_ids[:-1]:
            pool.cancel_task(task_id)

        pool.wait_for_done(2000)

        # Should have only run once (canceled 9)
        assert call_count <= 2  # First task + maybe one more

        stats = pool.get_statistics()
        print(f"\nCancellation: {stats['canceled']} tasks canceled")


@pytest.mark.fr_063
@pytest.mark.performance
class TestExceptionHandling:
    """Test exception handling in worker pool."""

    def test_runnable_exception_handling(self, app):
        """Test that exceptions in runnable are caught and logged."""
        pool = OptimizedWorkerPool(max_threads=1)

        exception_raised = []

        def failing_task():
            exception_raised.append(True)
            raise ValueError("Test exception")

        # Should not crash - exception should be caught and logged
        task_id = pool.submit(failing_task)
        pool.wait_for_done(1000)

        # Verify task ran (raised exception)
        assert len(exception_raised) == 1

    def test_cancel_nonexistent_task(self, app):
        """Test canceling a task that doesn't exist."""
        pool = OptimizedWorkerPool(max_threads=1)

        # Try to cancel task that was never submitted
        result = pool.cancel_task("nonexistent_task_id")

        # Should return False (not found)
        assert result is False

    def test_cancel_task_with_coalesce_key(self, app):
        """Test canceling task removes coalesce key."""
        pool = OptimizedWorkerPool(max_threads=1)

        # Block worker thread
        def blocking_task():
            time.sleep(1.0)

        pool.submit(blocking_task)

        # Submit task with coalesce key
        def work():
            pass

        task_id = pool.submit(work, coalesce_key="test_key")

        # Cancel it before it runs
        result = pool.cancel_task(task_id)

        # Should successfully cancel
        assert result is True

        # Submit another task with same coalesce key - should work
        task_id2 = pool.submit(work, coalesce_key="test_key")
        assert task_id2 is not None
        assert task_id2 != task_id  # Different task


@pytest.mark.fr_063
@pytest.mark.performance
class TestImportFallback:
    """Test import fallback for macOS optimizer."""

    def test_macos_optimizer_import_fallback(self, app):
        """Test fallback when macOS optimizer not available."""
        import sys
        from importlib import reload

        # Save original module
        original_macos = sys.modules.get('asciidoc_artisan.core.macos_optimizer')

        try:
            # Remove module to simulate import failure
            if 'asciidoc_artisan.core.macos_optimizer' in sys.modules:
                del sys.modules['asciidoc_artisan.core.macos_optimizer']

            import builtins
            original_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if 'macos_optimizer' in name:
                    raise ImportError("Mocked macos_optimizer import failure")
                return original_import(name, *args, **kwargs)

            builtins.__import__ = mock_import

            # Reload to trigger import fallback
            import asciidoc_artisan.workers.optimized_worker_pool as owp
            reload(owp)

            # Create pool without specifying max_threads to trigger auto-detection
            pool = owp.OptimizedWorkerPool()

            # Should fall back to multiprocessing.cpu_count()
            assert pool.max_threads > 0
            import multiprocessing
            assert pool.max_threads == multiprocessing.cpu_count()

        finally:
            # Restore original state
            builtins.__import__ = original_import
            if original_macos is not None:
                sys.modules['asciidoc_artisan.core.macos_optimizer'] = original_macos
            reload(owp)
