"""
Cancelable Runnable - Thread-safe cancelable task for Qt thread pools.

Extracted from OptimizedWorkerPool to reduce class size (MA principle).
Provides a QRunnable that can be canceled before or during execution.
"""

import logging
from collections.abc import Callable
from threading import Event
from typing import Any

from PySide6.QtCore import QRunnable

logger = logging.getLogger(__name__)


class CancelableRunnable(QRunnable):
    """
    Runnable that can be canceled.

    Extracted from OptimizedWorkerPool per MA principle (~85 lines).

    Checks cancellation flag before and during execution.
    Thread-safe through Event synchronization.

    Example:
        runnable = CancelableRunnable(my_func, "task_1", arg1, arg2)

        # Check if started
        if not runnable.is_running():
            # Cancel before it runs
            runnable.cancel()

        # Wait for completion
        runnable.wait(timeout=5.0)
    """

    def __init__(self, func: Callable[..., Any], task_id: str, *args: Any, **kwargs: Any) -> None:
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
