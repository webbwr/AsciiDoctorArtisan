"""
Base Worker - Shared functionality for background worker threads.

This module provides the BaseWorker class which implements common patterns
for QThread workers including cancellation support and subprocess execution.

Used by:
- GitWorker (Git command execution)
- GitHubCLIWorker (GitHub CLI command execution)

Implements:
- NFR-005: Long-running operations in background threads
- NFR-010: Parameterized subprocess calls (no shell injection)
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject

logger = logging.getLogger(__name__)


class BaseWorker(QObject):
    """
    Base class for background worker threads.

    Provides common functionality for workers that execute subprocess
    commands in background QThreads.

    Features:
    - Cancellation support (request-based, cannot interrupt running subprocess)
    - Working directory validation
    - Consistent logging patterns

    Subclasses should:
    - Define their own Signal for results
    - Implement command execution logic using _check_cancellation()
    - Use _validate_working_directory() before subprocess execution
    """

    def __init__(self) -> None:
        """Initialize base worker with cancellation support."""
        super().__init__()
        self._cancelled = False

    def cancel(self) -> None:
        """
        Request cancellation of current operation.

        Note: Operations use blocking subprocess.run() so cancellation
        only prevents new operations from starting. In-progress subprocess
        commands cannot be interrupted.

        Subclasses should check _cancelled flag at operation start using
        _check_cancellation() method.
        """
        logger.info(f"{self.__class__.__name__} cancellation requested")
        self._cancelled = True

    def reset_cancellation(self) -> None:
        """
        Reset cancellation flag for next operation.

        Should be called after operation completes (success or cancelled).
        """
        self._cancelled = False

    def _check_cancellation(self) -> bool:
        """
        Check if operation has been cancelled.

        Returns:
            True if cancelled, False otherwise
        """
        return self._cancelled

    def _validate_working_directory(self, working_dir: str) -> bool:
        """
        Validate that working directory exists.

        Args:
            working_dir: Absolute path to working directory

        Returns:
            True if directory exists, False otherwise
        """
        return Path(working_dir).is_dir()

    def _build_subprocess_kwargs(
        self,
        working_dir: Optional[str] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        Build common kwargs for subprocess.run() with security settings.

        Args:
            working_dir: Optional working directory for subprocess
            timeout: Timeout in seconds (default: 30)

        Returns:
            Dictionary of kwargs for subprocess.run()

        Security:
            - shell=False prevents command injection (NFR-010)
            - timeout prevents indefinite hangs
            - capture_output=True isolates subprocess output
            - text=True with encoding='utf-8' for consistent string handling
        """
        return {
            "cwd": working_dir,
            "capture_output": True,
            "text": True,
            "check": False,
            "shell": False,  # Critical: prevents command injection
            "encoding": "utf-8",
            "errors": "replace",
            "timeout": timeout,
        }

    def _execute_subprocess(
        self,
        command: list[str],
        working_dir: Optional[str] = None,
        timeout: int = 30,
    ) -> subprocess.CompletedProcess[str]:
        """
        Execute subprocess command with common security settings.

        Args:
            command: Command and arguments as list
            working_dir: Optional working directory
            timeout: Timeout in seconds (default: 30)

        Returns:
            CompletedProcess instance with results

        Raises:
            subprocess.TimeoutExpired: If command times out
            FileNotFoundError: If command executable not found
            Exception: Other subprocess errors

        Security:
            - Never uses shell=True (prevents command injection)
            - All arguments passed as list
            - Timeout enforced to prevent hangs
        """
        kwargs = self._build_subprocess_kwargs(working_dir, timeout)
        logger.info(f"Executing command: {' '.join(command)}")
        if working_dir:
            logger.info(f"Working directory: {working_dir}")

        return subprocess.run(command, **kwargs)
