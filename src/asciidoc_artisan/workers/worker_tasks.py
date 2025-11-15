"""
Worker Tasks - Specific task implementations for the worker pool.

This module defines task types that can be executed in the worker pool:
- RenderTask: AsciiDoc to HTML rendering
- ConversionTask: Document format conversion (Pandoc)
- GitTask: Git version control operations

Each task type implements the CancelableRunnable interface from the
optimized worker pool.
"""

import io
import logging
import subprocess
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal

from asciidoc_artisan.core import GitResult
from asciidoc_artisan.workers.optimized_worker_pool import (
    CancelableRunnable,
    TaskPriority,
)

logger = logging.getLogger(__name__)


class TaskSignals(QObject):
    """
    Signals for task communication with the main thread.

    Signals:
        started: Emitted when task starts
        progress: Emitted with progress updates (0-100)
        finished: Emitted with result on completion
        error: Emitted with error message on failure
        cancelled: Emitted when task is cancelled
    """

    started = Signal()
    progress = Signal(int, str)  # (percentage, message)
    finished = Signal(object)  # result
    error = Signal(str)  # error_message
    cancelled = Signal()


class RenderTask(CancelableRunnable):
    """
    Task for rendering AsciiDoc to HTML.

    This task runs AsciiDoc rendering in a background thread and emits
    the result via signals.

    Args:
        text: AsciiDoc source text to render
        asciidoc_api: AsciiDoc API instance for rendering
        task_id: Optional task ID (auto-generated if not provided)
    """

    def __init__(
        self, text: str, asciidoc_api: Any, task_id: str | None = None
    ) -> None:
        """Initialize render task."""
        # Generate unique ID using timestamp if not provided.
        if task_id is None:
            import time

            task_id = f"render_{time.time()}"

        # Create render function
        def render_func() -> str:
            """Render AsciiDoc to HTML."""
            # Exit early if task was cancelled.
            if self.is_canceled():
                return ""

            try:
                # Use string buffers to avoid file I/O overhead.
                infile = io.StringIO(text)
                outfile = io.StringIO()

                # Check again before slow rendering starts.
                if self.is_canceled():
                    return ""

                # Perform rendering
                asciidoc_api.execute(infile, outfile, backend="html5")

                # Final check before returning result.
                if self.is_canceled():
                    return ""

                return outfile.getvalue()

            except Exception as exc:
                logger.error(f"Render failed: {exc}")
                raise

        super().__init__(render_func, task_id)
        self.signals = TaskSignals()
        # High priority because user sees this in preview pane.
        self.priority = TaskPriority.HIGH

    def run(self) -> None:
        """Override run to emit signals."""
        try:
            # Tell main thread task is starting.
            self.signals.started.emit()
            # Execute the actual rendering
            super().run()
            # Note: finished signal emitted by caller after checking result.
        except Exception as exc:
            logger.exception(f"RenderTask failed: {exc}")
            # Send error to main thread for display.
            self.signals.error.emit(str(exc))


class ConversionTask(CancelableRunnable):
    """
    Task for document format conversion using Pandoc.

    Args:
        source: Source text or file path
        to_format: Target format (e.g., "asciidoc", "docx", "markdown")
        from_format: Source format
        is_file: Whether source is a file path (True) or text (False)
        task_id: Optional task ID
    """

    def __init__(
        self,
        source: str,
        to_format: str,
        from_format: str,
        is_file: bool = False,
        task_id: str | None = None,
    ) -> None:
        """Initialize conversion task."""
        # Generate unique ID using timestamp if not provided.
        if task_id is None:
            import time

            task_id = f"convert_{time.time()}"

        # Create conversion function
        def convert_func() -> tuple[bool, Any, str]:
            """Perform conversion."""
            # Exit early if task was cancelled.
            if self.is_canceled():
                return (False, "", "Conversion cancelled")

            try:
                # Lazy import to speed up app startup.
                import pypandoc

                # Check again after slow import completes.
                if self.is_canceled():
                    return (False, "", "Conversion cancelled")

                # Use file or text method based on source type.
                if is_file:
                    result = pypandoc.convert_file(
                        source, to_format, format=from_format
                    )
                else:
                    result = pypandoc.convert_text(
                        source, to_format, format=from_format
                    )

                # Final check before returning result.
                if self.is_canceled():
                    return (False, "", "Conversion cancelled")

                return (True, result, "")

            except Exception as exc:
                logger.error(f"Conversion failed: {exc}")
                # Return error instead of raising to avoid thread crash.
                return (False, "", str(exc))

        super().__init__(convert_func, task_id)
        self.signals = TaskSignals()
        # Normal priority - not as urgent as preview rendering.
        self.priority = TaskPriority.NORMAL

    def run(self) -> None:
        """Override run to emit signals."""
        try:
            self.signals.started.emit()
            super().run()
        except Exception as exc:
            logger.exception(f"ConversionTask failed: {exc}")
            self.signals.error.emit(str(exc))


class GitTask(CancelableRunnable):
    """
    Task for Git operations.

    Args:
        command: Git command as list (e.g., ["git", "status"])
        cwd: Working directory for git command
        task_id: Optional task ID
    """

    def __init__(
        self, command: list[str], cwd: Path, task_id: str | None = None
    ) -> None:
        """Initialize git task."""
        # Generate unique ID using timestamp if not provided.
        if task_id is None:
            import time

            task_id = f"git_{time.time()}"

        # Create git function
        def git_func() -> GitResult:
            """Execute git command."""
            # Exit early if task was cancelled.
            if self.is_canceled():
                return GitResult(
                    success=False,
                    stdout="",
                    stderr="Git operation cancelled",
                    exit_code=-1,
                    user_message="Git operation cancelled",
                )

            try:
                # Execute git command with security safeguards.
                result = subprocess.run(
                    command,
                    cwd=str(cwd),
                    capture_output=True,
                    text=True,
                    # Prevent hang on slow operations.
                    timeout=30,
                    # Security: prevent shell injection attacks.
                    shell=False,
                )

                # Check again after slow subprocess completes.
                if self.is_canceled():
                    return GitResult(
                        success=False,
                        stdout="",
                        stderr="Git operation cancelled",
                        exit_code=-1,
                        user_message="Git operation cancelled",
                    )

                # Build result from subprocess output.
                return GitResult(
                    success=result.returncode == 0,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=result.returncode,
                    user_message=(
                        "Git operation completed"
                        if result.returncode == 0
                        else "Git operation failed"
                    ),
                )

            except subprocess.TimeoutExpired:
                # Handle slow network or large repos.
                logger.error("Git command timed out")
                return GitResult(
                    success=False,
                    stdout="",
                    stderr="Git command timed out",
                    exit_code=-1,
                    user_message="Git command timed out",
                )
            except Exception as exc:
                # Catch all other errors to avoid thread crash.
                logger.error(f"Git command failed: {exc}")
                return GitResult(
                    success=False,
                    stdout="",
                    stderr=str(exc),
                    exit_code=-1,
                    user_message=f"Git command failed: {exc}",
                )

        super().__init__(git_func, task_id)
        self.signals = TaskSignals()
        # Normal priority - not as urgent as preview rendering.
        self.priority = TaskPriority.NORMAL

    def run(self) -> None:
        """Override run to emit signals."""
        try:
            self.signals.started.emit()
            super().run()
        except Exception as exc:
            logger.exception(f"GitTask failed: {exc}")
            self.signals.error.emit(str(exc))
