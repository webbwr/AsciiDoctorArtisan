"""
Worker Manager - Handles worker thread initialization and lifecycle.

Implements:
- Git worker thread setup
- Pandoc worker thread setup
- Preview worker thread setup
- Signal/slot connections
- Thread lifecycle management
- Worker pool for optimized task execution (v1.5.0)

Extracted from main_window.py as part of Phase 6 refactoring to reduce
main window complexity and improve modularity.

v1.5.0: Added OptimizedWorkerPool support for better resource management
and cancellable operations.
"""

import logging
import os
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QThread

from asciidoc_artisan.claude import ClaudeWorker
from asciidoc_artisan.workers import (
    GitHubCLIWorker,
    GitWorker,
    OllamaChatWorker,
    OptimizedWorkerPool,
    PandocWorker,
    PreviewWorker,
)

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)

# Check for AsciiDoc3 availability
try:
    from asciidoc3 import asciidoc3

    ASCIIDOC3_AVAILABLE = True
except ImportError:
    asciidoc3 = None
    ASCIIDOC3_AVAILABLE = False


class WorkerManager:
    """Manages worker threads for Git, Pandoc, and Preview operations.

    This class encapsulates all worker thread initialization, signal/slot
    connections, and lifecycle management.

    v1.5.0: Added OptimizedWorkerPool for better resource management.
    The pool is used alongside dedicated threads for backward compatibility.

    Args:
        editor: Reference to the main AsciiDocEditor window
        use_worker_pool: Enable worker pool (default: True for v1.5.0+)
        max_pool_threads: Maximum threads in pool (default: CPU count * 2)
    """

    def __init__(
        self,
        editor: "AsciiDocEditor",
        use_worker_pool: bool = True,
        max_pool_threads: int | None = None,
    ) -> None:
        """Initialize the WorkerManager with a reference to the main editor."""
        self.editor = editor
        self.git_thread: QThread | None = None
        self.git_worker: GitWorker | None = None
        self.github_thread: QThread | None = None
        self.github_worker: GitHubCLIWorker | None = None
        self.pandoc_thread: QThread | None = None
        self.pandoc_worker: PandocWorker | None = None
        self.preview_thread: QThread | None = None
        self.preview_worker: PreviewWorker | None = None
        self.ollama_chat_thread: QThread | None = None
        self.ollama_chat_worker: OllamaChatWorker | None = None
        self.claude_thread: QThread | None = None
        self.claude_worker: ClaudeWorker | None = None

        # Worker pool (v1.5.0)
        self.use_worker_pool = use_worker_pool
        self.worker_pool: OptimizedWorkerPool | None = None

        if self.use_worker_pool:
            # Default to CPU count * 2 if not specified
            if max_pool_threads is None:
                max_pool_threads = os.cpu_count() or 4
                max_pool_threads = max(4, max_pool_threads * 2)

            self.worker_pool = OptimizedWorkerPool(max_threads=max_pool_threads)
            logger.info(f"Worker pool enabled with {max_pool_threads} threads")

    def _setup_git_worker(self) -> None:
        """
        Setup Git worker thread with signal connections.

        MA principle: Extracted from setup_workers_and_threads (12 lines).
        """
        self.git_thread = QThread(self.editor)
        self.git_worker = GitWorker()
        self.git_worker.moveToThread(self.git_thread)
        self.editor.request_git_command.connect(self.git_worker.run_git_command)
        self.editor.request_git_status.connect(self.git_worker.get_repository_status)
        self.editor.request_detailed_git_status.connect(self.git_worker.get_detailed_repository_status)
        self.git_worker.command_complete.connect(self.editor._handle_git_result)
        self.git_worker.status_ready.connect(self.editor._handle_git_status)
        self.git_worker.detailed_status_ready.connect(self.editor._handle_detailed_git_status)
        self.git_thread.finished.connect(self.git_worker.deleteLater)
        self.git_thread.start()

    def _setup_github_worker(self) -> None:
        """
        Setup GitHub CLI worker thread with signal connections.

        MA principle: Extracted from setup_workers_and_threads (8 lines).
        """
        self.github_thread = QThread(self.editor)
        self.github_worker = GitHubCLIWorker()
        self.github_worker.moveToThread(self.github_thread)
        self.editor.request_github_command.connect(self.github_worker.dispatch_github_operation)
        self.github_worker.github_result_ready.connect(self.editor._handle_github_result)
        self.github_thread.finished.connect(self.github_worker.deleteLater)
        self.github_thread.start()

    def _setup_pandoc_worker(self) -> None:
        """
        Setup Pandoc worker thread with signal connections.

        MA principle: Extracted from setup_workers_and_threads (22 lines).
        """
        self.pandoc_thread = QThread(self.editor)
        self.pandoc_worker = PandocWorker()
        self.pandoc_worker.moveToThread(self.pandoc_thread)

        # Initialize Ollama configuration from settings
        self.pandoc_worker.set_ollama_config(
            getattr(self.editor._settings, "ollama_enabled", False),
            getattr(self.editor._settings, "ollama_model", None),
        )

        self.editor.request_pandoc_conversion.connect(self.pandoc_worker.run_pandoc_conversion)
        self.pandoc_worker.conversion_complete.connect(
            self.editor.pandoc_result_handler.handle_pandoc_result,
            Qt.ConnectionType.QueuedConnection,
        )
        self.pandoc_worker.conversion_error.connect(
            self.editor.pandoc_result_handler.handle_pandoc_error_result,
            Qt.ConnectionType.QueuedConnection,
        )
        self.pandoc_thread.finished.connect(self.pandoc_worker.deleteLater)
        self.pandoc_thread.start()

    def _setup_preview_worker(self) -> None:
        """
        Setup Preview worker thread with signal connections.

        MA principle: Extracted from setup_workers_and_threads (17 lines).
        """
        self.preview_thread = QThread(self.editor)
        self.preview_worker = PreviewWorker()
        self.preview_worker.moveToThread(self.preview_thread)

        # Connect signals BEFORE starting thread
        self.editor.request_preview_render.connect(self.preview_worker.render_preview)
        self.preview_worker.render_complete.connect(self.editor._handle_preview_complete)
        self.preview_worker.render_error.connect(self.editor._handle_preview_error)
        self.preview_thread.finished.connect(self.preview_worker.deleteLater)

        # Initialize AsciiDoc API on worker thread after thread starts
        if ASCIIDOC3_AVAILABLE and asciidoc3:
            self.preview_thread.started.connect(lambda: self.preview_worker.initialize_asciidoc(asciidoc3.__file__))

        self.preview_thread.start()

    def _setup_ollama_chat_worker(self) -> None:
        """
        Setup Ollama chat worker thread.

        MA principle: Extracted from setup_workers_and_threads (10 lines).
        Note: Chat worker signals connected via ChatManager after initialization.
        """
        self.ollama_chat_thread = QThread(self.editor)
        self.ollama_chat_worker = OllamaChatWorker()
        self.ollama_chat_worker.moveToThread(self.ollama_chat_thread)
        self.ollama_chat_thread.finished.connect(self.ollama_chat_worker.deleteLater)
        self.ollama_chat_thread.start()

    def _setup_claude_worker(self) -> None:
        """
        Setup Claude AI worker thread.

        MA principle: Extracted from setup_workers_and_threads (10 lines).
        Note: Claude worker signals connected via main_window adapter pattern.
        """
        self.claude_thread = QThread(self.editor)
        self.claude_worker = ClaudeWorker()
        self.claude_worker.moveToThread(self.claude_thread)
        self.claude_thread.finished.connect(self.claude_worker.deleteLater)
        self.claude_thread.start()

    def _store_worker_references(self) -> None:
        """
        Store worker/thread references on main window for backward compatibility.

        MA principle: Extracted from setup_workers_and_threads (13 lines).
        """
        self.editor.git_thread = self.git_thread
        self.editor.git_worker = self.git_worker
        self.editor.github_thread = self.github_thread
        self.editor.github_worker = self.github_worker
        self.editor.pandoc_thread = self.pandoc_thread
        self.editor.pandoc_worker = self.pandoc_worker
        self.editor.preview_thread = self.preview_thread
        self.editor.preview_worker = self.preview_worker
        self.editor.ollama_chat_thread = self.ollama_chat_thread
        self.editor.ollama_chat_worker = self.ollama_chat_worker
        self.editor.claude_thread = self.claude_thread
        self.editor.claude_worker = self.claude_worker

    def setup_workers_and_threads(self) -> None:
        """
        Set up all worker threads with signal connections.

        MA principle: Reduced from 105→20 lines by extracting 7 helper methods.
        """
        logger.info("Setting up worker threads...")

        # Setup all workers using dedicated helper methods
        self._setup_git_worker()
        self._setup_github_worker()
        self._setup_pandoc_worker()
        self._setup_preview_worker()
        self._setup_ollama_chat_worker()
        self._setup_claude_worker()

        logger.info("All worker threads started (Git, GitHub, Pandoc, Preview, Ollama, Claude)")

        # Store references on main window for backward compatibility
        self._store_worker_references()

    def get_pool_statistics(self) -> dict[str, Any]:
        """
        Get worker pool statistics.

        Returns:
            Dictionary with pool stats, or empty dict if pool not enabled
        """
        if self.worker_pool:
            return self.worker_pool.get_statistics()
        return {}

    def cancel_all_pool_tasks(self) -> int:
        """
        Cancel all pending tasks in the worker pool.

        Returns:
            Number of tasks cancelled, or 0 if pool not enabled
        """
        if self.worker_pool:
            return self.worker_pool.cancel_all()
        return 0

    def wait_for_pool_done(self, timeout_ms: int = 5000) -> bool:
        """
        Wait for all pool tasks to complete.

        Args:
            timeout_ms: Timeout in milliseconds (default: 5 seconds)

        Returns:
            True if all tasks completed, False if timeout or pool not enabled
        """
        if self.worker_pool:
            return self.worker_pool.wait_for_done(timeout_ms)
        return True

    def cancel_git_operation(self) -> None:
        """Cancel the current Git operation.

        Note: Git operations use blocking subprocess calls, so cancellation
        only prevents queued operations from starting. In-progress operations
        cannot be interrupted.
        """
        logger.info("Cancelling Git operation")
        if self.git_worker and hasattr(self.git_worker, "cancel"):
            self.git_worker.cancel()

    def cancel_github_operation(self) -> None:
        """Cancel the current GitHub operation.

        Note: GitHub CLI operations use blocking subprocess calls, so cancellation
        only prevents queued operations from starting. In-progress operations
        cannot be interrupted.
        """
        logger.info("Cancelling GitHub operation")
        if self.github_worker and hasattr(self.github_worker, "cancel"):
            self.github_worker.cancel()

    def cancel_pandoc_operation(self) -> None:
        """Cancel the current Pandoc operation.

        Note: Pandoc operations use blocking subprocess calls, so cancellation
        only prevents queued operations from starting. In-progress operations
        cannot be interrupted.
        """
        logger.info("Cancelling Pandoc operation")
        if self.pandoc_worker and hasattr(self.pandoc_worker, "cancel"):
            self.pandoc_worker.cancel()

    def cancel_preview_operation(self) -> None:
        """Cancel the current preview rendering operation.

        Note: Preview rendering cannot currently be interrupted once started.
        """
        logger.info("Cancelling preview operation")
        if self.preview_worker and hasattr(self.preview_worker, "cancel"):
            self.preview_worker.cancel()

    def shutdown(self) -> None:  # noqa: C901
        """
        Shutdown all workers and threads gracefully.

        This method should be called when the application is closing.
        """
        logger.info("Shutting down workers...")

        # Cancel and wait for pool tasks if pool is enabled
        if self.worker_pool:
            cancelled = self.cancel_all_pool_tasks()
            if cancelled > 0:
                logger.info(f"Cancelled {cancelled} pool tasks")
            self.wait_for_pool_done(5000)

        # Stop dedicated threads with force-termination fallback
        # IMPORTANT: Must wait for threads to fully exit AND explicitly delete them
        # to avoid "QThread: Destroyed while thread is still running" crash

        if self.git_thread:
            if self.git_thread.isRunning():
                self.git_thread.quit()
                if not self.git_thread.wait(3000):
                    logger.warning("Git thread did not exit cleanly, force terminating")
                    self.git_thread.terminate()
                    self.git_thread.wait(1000)
            # Explicitly delete the thread to avoid destructor issues
            self.git_thread.deleteLater()
            self.git_thread = None

        if self.github_thread:
            if self.github_thread.isRunning():
                self.github_thread.quit()
                if not self.github_thread.wait(3000):
                    logger.warning("GitHub thread did not exit cleanly, force terminating")
                    self.github_thread.terminate()
                    self.github_thread.wait(1000)
            self.github_thread.deleteLater()
            self.github_thread = None

        if self.pandoc_thread:
            if self.pandoc_thread.isRunning():
                self.pandoc_thread.quit()
                if not self.pandoc_thread.wait(3000):
                    logger.warning("Pandoc thread did not exit cleanly, force terminating")
                    self.pandoc_thread.terminate()
                    self.pandoc_thread.wait(1000)
            self.pandoc_thread.deleteLater()
            self.pandoc_thread = None

        if self.preview_thread:
            if self.preview_thread.isRunning():
                self.preview_thread.quit()
                if not self.preview_thread.wait(3000):
                    logger.warning("Preview thread did not exit cleanly, force terminating")
                    self.preview_thread.terminate()
                    self.preview_thread.wait(1000)
            self.preview_thread.deleteLater()
            self.preview_thread = None

        if self.ollama_chat_thread:
            if self.ollama_chat_thread.isRunning():
                self.ollama_chat_thread.quit()
                if not self.ollama_chat_thread.wait(3000):
                    logger.warning("Ollama chat thread did not exit cleanly, force terminating")
                    self.ollama_chat_thread.terminate()
                    self.ollama_chat_thread.wait(1000)
            self.ollama_chat_thread.deleteLater()
            self.ollama_chat_thread = None

        if self.claude_thread:
            if self.claude_thread.isRunning():
                self.claude_thread.quit()
                if not self.claude_thread.wait(3000):
                    logger.warning("Claude thread did not exit cleanly, force terminating")
                    self.claude_thread.terminate()
                    self.claude_thread.wait(1000)
            self.claude_thread.deleteLater()
            self.claude_thread = None

        logger.info("All workers shutdown complete")
