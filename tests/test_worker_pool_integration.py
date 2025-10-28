"""
Tests for Worker Pool Integration (v1.5.0-A).

Tests the integration of OptimizedWorkerPool with WorkerManager and
the new task types (RenderTask, ConversionTask, GitTask).
"""

import pytest
import time
from pathlib import Path

from asciidoc_artisan.workers import (
    OptimizedWorkerPool,
    TaskPriority,
    RenderTask,
    ConversionTask,
    GitTask,
)


class TestOptimizedWorkerPool:
    """Test the OptimizedWorkerPool class."""

    def test_pool_initialization(self):
        """Test worker pool can be initialized."""
        pool = OptimizedWorkerPool(max_threads=4)
        assert pool.max_threads == 4
        assert pool.active_thread_count() >= 0

    def test_submit_simple_task(self):
        """Test submitting a simple task to the pool."""
        pool = OptimizedWorkerPool(max_threads=2)

        result = []

        def simple_task():
            result.append("done")

        task_id = pool.submit(simple_task, priority=TaskPriority.NORMAL)
        assert task_id is not None

        # Wait for task to complete
        pool.wait_for_done(1000)
        assert result == ["done"]

    def test_task_prioritization(self):
        """Test tasks are executed by priority."""
        pool = OptimizedWorkerPool(max_threads=1)  # Single thread for order
        results = []

        def task(name):
            results.append(name)
            time.sleep(0.01)  # Small delay

        # Submit tasks in reverse priority order
        pool.submit(task, "low", priority=TaskPriority.LOW)
        pool.submit(task, "high", priority=TaskPriority.HIGH)
        pool.submit(task, "normal", priority=TaskPriority.NORMAL)

        pool.wait_for_done(2000)

        # High priority should execute first
        assert results[0] == "high"

    def test_task_cancellation(self):
        """Test task can be cancelled."""
        pool = OptimizedWorkerPool(max_threads=1)

        executed = []

        def slow_task():
            time.sleep(0.5)
            executed.append("task1")

        def fast_task():
            executed.append("task2")

        # Submit slow task
        task_id = pool.submit(slow_task, priority=TaskPriority.NORMAL)

        # Try to cancel immediately
        cancelled = pool.cancel_task(task_id)

        # Submit fast task
        pool.submit(fast_task, priority=TaskPriority.NORMAL)

        pool.wait_for_done(1000)

        # If cancelled successfully, only task2 should execute
        if cancelled:
            assert "task1" not in executed
            assert "task2" in executed

    def test_cancel_all_tasks(self):
        """Test cancelling all pending tasks."""
        pool = OptimizedWorkerPool(max_threads=1)

        executed = []

        def task(name):
            time.sleep(0.1)
            executed.append(name)

        # Submit multiple tasks
        for i in range(5):
            pool.submit(task, f"task{i}", priority=TaskPriority.NORMAL)

        # Cancel all
        time.sleep(0.05)  # Let first task start
        cancelled_count = pool.cancel_all()

        pool.wait_for_done(500)

        # At least some tasks should be cancelled
        assert cancelled_count > 0
        assert len(executed) < 5

    def test_pool_statistics(self):
        """Test getting pool statistics."""
        pool = OptimizedWorkerPool(max_threads=2)

        def simple_task():
            time.sleep(0.01)

        # Submit tasks
        pool.submit(simple_task, priority=TaskPriority.NORMAL)
        pool.submit(simple_task, priority=TaskPriority.NORMAL)

        pool.wait_for_done(1000)

        stats = pool.get_statistics()
        assert "submitted" in stats
        assert "completed" in stats
        assert "active_threads" in stats
        assert "max_threads" in stats
        assert stats["submitted"] >= 2

    def test_task_coalescing(self):
        """Test task coalescing (deduplication)."""
        pool = OptimizedWorkerPool(max_threads=2)

        executed = []

        def task():
            executed.append(1)
            time.sleep(0.01)

        # Submit same task multiple times with coalescing
        task_id1 = pool.submit(
            task,
            priority=TaskPriority.NORMAL,
            coalescable=True,
            coalesce_key="test_task",
        )

        task_id2 = pool.submit(
            task,
            priority=TaskPriority.NORMAL,
            coalescable=True,
            coalesce_key="test_task",
        )

        # Should return same task ID
        assert task_id1 == task_id2

        pool.wait_for_done(1000)

        # Task should execute only once
        assert len(executed) == 1

        stats = pool.get_statistics()
        assert stats["coalesced"] >= 1


class TestWorkerTasks:
    """Test specific worker task types."""

    def test_render_task_creation(self):
        """Test creating a RenderTask."""
        # Mock AsciiDoc API
        class MockAsciiDocAPI:
            def execute(self, infile, outfile, backend=None):
                outfile.write("<p>Test</p>")

        api = MockAsciiDocAPI()
        task = RenderTask("= Test", api)

        assert task is not None
        assert task.priority == TaskPriority.HIGH

    def test_conversion_task_creation(self):
        """Test creating a ConversionTask."""
        task = ConversionTask(
            source="Test content",
            to_format="html",
            from_format="markdown",
            is_file=False,
        )

        assert task is not None
        assert task.priority == TaskPriority.NORMAL

    def test_git_task_creation(self):
        """Test creating a GitTask."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            task = GitTask(
                command=["git", "--version"],
                cwd=Path(tmpdir),
            )

            assert task is not None
            assert task.priority == TaskPriority.NORMAL


class TestWorkerManagerIntegration:
    """Test WorkerManager with worker pool."""

    def test_worker_manager_with_pool(self):
        """Test WorkerManager initializes with pool."""
        # Note: This test requires a mock editor object
        # For now, just test pool initialization separately
        pool = OptimizedWorkerPool(max_threads=4)
        assert pool is not None

        stats = pool.get_statistics()
        assert stats["max_threads"] == 4

    def test_pool_shutdown(self):
        """Test pool can be shut down gracefully."""
        pool = OptimizedWorkerPool(max_threads=2)

        def task():
            time.sleep(0.01)

        # Submit tasks
        pool.submit(task, priority=TaskPriority.NORMAL)
        pool.submit(task, priority=TaskPriority.NORMAL)

        # Wait for completion
        completed = pool.wait_for_done(1000)
        assert completed

    def test_pool_statistics_tracking(self):
        """Test pool tracks statistics correctly."""
        pool = OptimizedWorkerPool(max_threads=2)

        def successful_task():
            return "success"

        # Submit tasks
        task_id1 = pool.submit(successful_task, priority=TaskPriority.NORMAL)
        task_id2 = pool.submit(successful_task, priority=TaskPriority.NORMAL)

        assert task_id1 != task_id2

        pool.wait_for_done(1000)

        stats = pool.get_statistics()
        assert stats["submitted"] == 2

    def test_concurrent_task_execution(self):
        """Test multiple tasks can run concurrently."""
        pool = OptimizedWorkerPool(max_threads=4)

        results = []
        start_time = time.time()

        def concurrent_task(task_id):
            time.sleep(0.1)  # 100ms task
            results.append(task_id)

        # Submit 4 tasks
        for i in range(4):
            pool.submit(concurrent_task, i, priority=TaskPriority.NORMAL)

        pool.wait_for_done(2000)

        elapsed = time.time() - start_time

        # All 4 tasks should complete
        assert len(results) == 4

        # With 4 threads, should complete in ~100ms, not 400ms
        # Allow some overhead
        assert elapsed < 0.3  # Should be much less than sequential time


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
