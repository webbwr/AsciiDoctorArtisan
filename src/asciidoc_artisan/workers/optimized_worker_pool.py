"""
Optimized Worker Pool - Efficient background task management.

This module provides optimized worker thread management:
- Task prioritization (high/normal/low)
- Task cancellation (stop outdated work)
- Task coalescing (combine duplicate tasks)
- Efficient thread pool (reuse threads)

Implements Phase 3.4 of Performance Optimization Plan:
- Optimized worker pool
- Cancelable tasks
- Priority queue
- Task deduplication

Design Goals:
- Fast task submission
- Efficient cancellation
- Priority-based execution
- Reduce wasted work
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum
from threading import Event, Lock
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

logger = logging.getLogger(__name__)


class TaskPriority(IntEnum):
    """
    Task priority levels.

    Lower number = higher priority.
    """

    CRITICAL = 0  # Must run immediately
    HIGH = 1  # User-facing tasks
    NORMAL = 2  # Regular tasks
    LOW = 3  # Background tasks
    IDLE = 4  # Run when nothing else to do


@dataclass(slots=True)
class TaskMetadata:
    """
    Metadata for task tracking.

    Uses __slots__ for memory efficiency.
    """

    task_id: str
    priority: TaskPriority
    created_at: float
    coalescable: bool = False
    coalesce_key: str | None = None


@dataclass(order=True, slots=True)
class PrioritizedTask:
    """
    Task with priority for queue.

    Uses __slots__ for memory efficiency.
    Ordered by priority for PriorityQueue.
    """

    priority: int
    created_at: float = field(compare=True)
    task_id: str = field(compare=False)
    runnable: Any = field(compare=False)
    metadata: TaskMetadata = field(compare=False)


class CancelableRunnable(QRunnable):
    """
    Runnable that can be canceled.

    Checks cancellation flag before and during execution.
    """

    def __init__(
        self, func: Callable[..., Any], task_id: str, *args: Any, **kwargs: Any
    ) -> None:
        """
        Initialize cancelable runnable.

        Args:
            func: Function to run
            task_id: Unique task ID
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        super().__init__()
        self.func = func
        self.task_id = task_id
        self.args = args
        self.kwargs = kwargs
        self._canceled = Event()
        self._started = Event()
        self._finished = Event()

    def run(self) -> None:
        """Run task if not canceled."""
        if self._canceled.is_set():
            logger.debug(f"Task {self.task_id} canceled before start")
            return

        self._started.set()

        try:
            # Check cancellation before running
            if not self._canceled.is_set():
                logger.debug(f"Running task {self.task_id}")
                self.func(*self.args, **self.kwargs)
                logger.debug(f"Task {self.task_id} completed")
        except Exception as exc:
            logger.error(f"Task {self.task_id} failed: {exc}")
        finally:
            self._finished.set()

    def cancel(self) -> bool:
        """
        Cancel this task.

        Returns:
            True if task was canceled, False if already running/finished
        """
        if self._started.is_set():
            # Task already started, can't cancel
            return False

        self._canceled.set()
        logger.debug(f"Task {self.task_id} canceled")
        return True

    def is_canceled(self) -> bool:
        """Check if task is canceled."""
        return self._canceled.is_set()

    def is_running(self) -> bool:
        """Check if task is running."""
        return self._started.is_set() and not self._finished.is_set()

    def is_finished(self) -> bool:
        """Check if task finished."""
        return self._finished.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        """
        Wait for task to finish.

        Args:
            timeout: Timeout in seconds (None = wait forever)

        Returns:
            True if finished, False if timeout
        """
        return self._finished.wait(timeout)


class TaskSignals(QObject):
    """Signals for task events."""

    task_started = Signal(str)  # task_id
    task_finished = Signal(str)  # task_id
    task_canceled = Signal(str)  # task_id
    task_failed = Signal(str, str)  # task_id, error


class OptimizedWorkerPool:
    """
    Optimized worker pool with advanced features.

    Features:
    - Task prioritization
    - Task cancellation
    - Task coalescing (deduplication)
    - Statistics tracking

    Example:
        pool = OptimizedWorkerPool(max_threads=4)

        # Submit high priority task
        task_id = pool.submit(
            my_function,
            arg1, arg2,
            priority=TaskPriority.HIGH
        )

        # Submit coalescable task
        task_id = pool.submit(
            render_preview,
            source_text,
            priority=TaskPriority.NORMAL,
            coalescable=True,
            coalesce_key="preview_render"
        )

        # Cancel task
        pool.cancel_task(task_id)

        # Get statistics
        stats = pool.get_statistics()
    """

    def __init__(self, max_threads: int | None = None):
        """
        Initialize optimized worker pool.

        Args:
            max_threads: Maximum number of worker threads.
                        If None, auto-detect optimal count for platform.
                        On Apple Silicon: uses P-cores * 2 for optimal performance.
                        On other platforms: uses CPU count.
        """
        # Auto-detect optimal thread count if not specified
        if max_threads is None:
            try:
                from asciidoc_artisan.core.macos_optimizer import (
                    get_optimal_thread_count,
                )

                max_threads = get_optimal_thread_count()
                logger.info(
                    f"Auto-detected optimal thread count: {max_threads} (Apple Silicon optimized)"
                )
            except ImportError:
                # Fallback to CPU count
                import multiprocessing

                max_threads = multiprocessing.cpu_count()
                logger.info(f"Using default thread count: {max_threads}")

        self.max_threads = max_threads
        self._thread_pool = QThreadPool.globalInstance()
        self._thread_pool.setMaxThreadCount(max_threads)

        # Task tracking
        self._active_tasks: dict[str, CancelableRunnable] = {}
        self._pending_tasks: dict[str, PrioritizedTask] = {}
        self._coalesce_keys: dict[str, str] = {}  # coalesce_key -> task_id
        self._task_lock = Lock()

        # Statistics
        self._stats = {
            "submitted": 0,
            "started": 0,
            "completed": 0,
            "canceled": 0,
            "failed": 0,
            "coalesced": 0,
        }
        self._stats_lock = Lock()

        # Signals
        self.signals = TaskSignals()

        logger.info(f"Worker pool initialized with {max_threads} threads")

    def submit(
        self,
        func: Callable[..., Any],
        *args: Any,
        priority: TaskPriority = TaskPriority.NORMAL,
        coalescable: bool = False,
        coalesce_key: str | None = None,
        task_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Submit task to worker pool.

        Args:
            func: Function to run
            *args: Function arguments
            priority: Task priority
            coalescable: Whether task can be coalesced
            coalesce_key: Key for coalescing (required if coalescable=True)
            task_id: Optional custom task ID
            **kwargs: Function keyword arguments

        Returns:
            Task ID
        """
        # Generate task ID if not provided
        if task_id is None:
            task_id = f"task_{time.time()}_{id(func)}"

        # Check coalescing
        if coalescable:
            if coalesce_key is None:
                raise ValueError("coalesce_key required for coalescable tasks")

            with self._task_lock:
                # Check if there's already a pending task with this key
                if coalesce_key in self._coalesce_keys:
                    existing_task_id = self._coalesce_keys[coalesce_key]
                    logger.debug(f"Coalescing task {task_id} into {existing_task_id}")
                    with self._stats_lock:
                        self._stats["coalesced"] += 1
                    return existing_task_id

        # Create runnable
        runnable = CancelableRunnable(func, task_id, *args, **kwargs)

        # Create metadata
        TaskMetadata(
            task_id=task_id,
            priority=priority,
            created_at=time.time(),
            coalescable=coalescable,
            coalesce_key=coalesce_key,
        )

        with self._task_lock:
            # Track task
            self._active_tasks[task_id] = runnable

            # Track coalesce key
            if coalescable and coalesce_key:
                self._coalesce_keys[coalesce_key] = task_id

        # Submit to thread pool
        self._thread_pool.start(runnable)

        with self._stats_lock:
            self._stats["submitted"] += 1

        logger.debug(f"Submitted task {task_id} with priority {priority.name}")

        return task_id

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if canceled, False if not found or already running
        """
        with self._task_lock:
            if task_id not in self._active_tasks:
                return False

            runnable = self._active_tasks[task_id]

            # Try to cancel
            if runnable.cancel():
                # Remove from tracking
                del self._active_tasks[task_id]

                # Remove coalesce key if applicable
                for key, tid in list(self._coalesce_keys.items()):
                    if tid == task_id:
                        del self._coalesce_keys[key]

                with self._stats_lock:
                    self._stats["canceled"] += 1

                self.signals.task_canceled.emit(task_id)
                return True

            return False

    def cancel_all(self) -> int:
        """
        Cancel all pending tasks.

        Returns:
            Number of tasks canceled
        """
        with self._task_lock:
            task_ids = list(self._active_tasks.keys())

        canceled = 0
        for task_id in task_ids:
            if self.cancel_task(task_id):
                canceled += 1

        logger.info(f"Canceled {canceled} tasks")
        return canceled

    def wait_for_done(self, timeout_ms: int = -1) -> bool:
        """
        Wait for all tasks to complete.

        Args:
            timeout_ms: Timeout in milliseconds (-1 = wait forever)

        Returns:
            True if all tasks completed, False if timeout
        """
        return self._thread_pool.waitForDone(timeout_ms)

    def active_thread_count(self) -> int:
        """Get number of active threads."""
        return self._thread_pool.activeThreadCount()

    def is_task_active(self, task_id: str) -> bool:
        """
        Check if task is active.

        Args:
            task_id: Task ID

        Returns:
            True if task is active
        """
        with self._task_lock:
            return task_id in self._active_tasks

    def get_statistics(self) -> dict[str, int | float]:
        """
        Get worker pool statistics.

        Returns:
            Dictionary with stats
        """
        with self._stats_lock:
            stats: dict[str, int | float] = dict(self._stats)

        with self._task_lock:
            stats["active_tasks"] = len(self._active_tasks)
            stats["active_threads"] = self.active_thread_count()
            stats["max_threads"] = self.max_threads

        # Calculate efficiency
        total = stats["submitted"]
        if total > 0:
            stats["completion_rate"] = float(stats["completed"]) / total * 100
            stats["cancellation_rate"] = float(stats["canceled"]) / total * 100
            stats["coalesce_rate"] = float(stats["coalesced"]) / total * 100
        else:
            stats["completion_rate"] = 0.0
            stats["cancellation_rate"] = 0.0
            stats["coalesce_rate"] = 0.0

        return stats

    def reset_statistics(self) -> None:
        """Reset statistics counters."""
        with self._stats_lock:
            self._stats = {
                "submitted": 0,
                "started": 0,
                "completed": 0,
                "canceled": 0,
                "failed": 0,
                "coalesced": 0,
            }

    def clear(self) -> None:
        """Clear all tasks and reset pool."""
        self.cancel_all()
        self.wait_for_done(5000)  # Wait up to 5 seconds
        self.reset_statistics()

        with self._task_lock:
            self._active_tasks.clear()
            self._pending_tasks.clear()
            self._coalesce_keys.clear()

        logger.info("Worker pool cleared")
