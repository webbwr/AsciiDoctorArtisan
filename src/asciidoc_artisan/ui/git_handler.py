"""
Git Handler - Manage Git version control operations.

This module handles all Git-related operations:
- Select Git repository
- Trigger Git commands (commit, pull, push)
- Handle Git results from worker
- Validate Git repository state

Extracted from main_window.py to improve maintainability and testability.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QFileDialog, QInputDialog

from asciidoc_artisan.core import GitResult
from asciidoc_artisan.ui.base_vcs_handler import BaseVCSHandler

logger = logging.getLogger(__name__)


class GitHandler(BaseVCSHandler):
    """Handle Git version control operations."""

    # Signals
    git_operation_started = Signal(str)  # Emitted when Git operation starts
    git_operation_completed = Signal(
        bool, str
    )  # Emitted when operation completes (success, message)

    def __init__(
        self, parent_window: Any, settings_manager: Any, status_manager: Any
    ) -> None:
        """
        Initialize GitHandler.

        Args:
            parent_window: Main window (for dialogs and signals)
            settings_manager: Settings manager instance
            status_manager: Status manager instance
        """
        super().__init__(parent_window, settings_manager, status_manager)

        # Git-specific state
        self.pending_commit_message: str | None = None

        # Git status refresh timer (v1.9.0+)
        self.status_timer: QTimer = QTimer()
        self.status_timer.timeout.connect(self._refresh_git_status)
        self.status_timer.setInterval(5000)  # 5 seconds
        self.status_refresh_enabled: bool = False

    def initialize(self) -> None:
        """
        Initialize Git handler from settings.

        Loads saved Git repository path from settings and validates it.
        Called after UI setup is complete.

        Note: Does not update UI state - UI state will be updated later
        in the initialization sequence when all managers are ready.
        """
        settings = self.settings_manager.load_settings()

        # Load repository path from settings
        if hasattr(settings, "git_repo_path") and settings.git_repo_path:
            repo_path = settings.git_repo_path

            # Validate it's still a Git repository
            if (Path(repo_path) / ".git").is_dir():
                logger.info(f"Git repository loaded from settings: {repo_path}")
                # Note: UI state will be updated later in initialization sequence
                # Start status refresh for valid repository (v1.9.0+)
                self.start_status_refresh()
            else:
                logger.warning(f"Saved Git repository no longer valid: {repo_path}")
                # Clear invalid path from settings
                settings.git_repo_path = None
                self.settings_manager.save_settings(settings, self.window)
        else:
            logger.debug("No Git repository configured in settings")

    def select_repository(self) -> None:
        """Select a Git repository via file dialog."""
        settings = self.settings_manager.load_settings()
        start_dir = (
            settings.git_repo_path
            if hasattr(settings, "git_repo_path")
            else settings.last_directory
        )

        dir_path = QFileDialog.getExistingDirectory(
            self.window,
            "Select Git Repository",
            start_dir or "",  # Convert None to empty string
            QFileDialog.Option.ShowDirsOnly,
        )

        if not dir_path:
            return

        # Validate it's a Git repository
        if not (Path(dir_path) / ".git").is_dir():
            self.status_manager.show_message(
                "warning",
                "Not a Git Repository",
                "Selected directory is not a Git repository.",
            )
            return

        # Save to settings
        settings.git_repo_path = dir_path
        self.settings_manager.save_settings(settings, self.window)

        # Update UI
        if hasattr(self.window, "status_bar"):
            self.window.status_bar.showMessage(f"Git repository: {dir_path}")

        # Update UI state
        if hasattr(self.window, "_update_ui_state"):
            self.window._update_ui_state()

        logger.info(f"Git repository: {dir_path}")

    def commit_changes(self) -> None:
        """Trigger Git commit operation."""
        if not self._ensure_ready():
            return

        # Save file if there are unsaved changes
        if hasattr(self.window, "_unsaved_changes") and self.window._unsaved_changes:
            if hasattr(self.window, "save_file"):
                if not self.window.save_file():
                    return

        # Get commit message from user
        message, ok = QInputDialog.getMultiLineText(
            self.window, "Commit Message", "Enter commit message:", ""
        )

        if not ok or not message.strip():
            return

        # Start commit operation
        self.is_processing = True
        self.last_operation = "commit"
        self.pending_commit_message = message

        # Update UI
        self._update_ui_state()
        if hasattr(self.window, "status_bar"):
            self.window.status_bar.showMessage("Committing changes...")

        # Emit signal to worker (via main window)
        settings = self.settings_manager.load_settings()
        repo_path = settings.git_repo_path if hasattr(settings, "git_repo_path") else ""

        if hasattr(self.window, "request_git_command"):
            self.window.request_git_command.emit(["git", "add", "."], repo_path)

        # Emit our signal
        self.git_operation_started.emit("commit")

        logger.info("Git commit started")

    def pull_changes(self) -> None:
        """Trigger Git pull operation."""
        if not self._ensure_ready():  # pragma: no cover
            return

        # Start pull operation
        self.is_processing = True
        self.last_operation = "pull"

        # Update UI
        self._update_ui_state()
        if hasattr(self.window, "status_bar"):
            self.window.status_bar.showMessage("Pulling from remote...")

        # Emit signal to worker
        settings = self.settings_manager.load_settings()
        repo_path = settings.git_repo_path if hasattr(settings, "git_repo_path") else ""

        if hasattr(self.window, "request_git_command"):
            self.window.request_git_command.emit(["git", "pull"], repo_path)

        # Emit our signal
        self.git_operation_started.emit("pull")

        logger.info("Git pull started")

    def push_changes(self) -> None:
        """Trigger Git push operation."""
        if not self._ensure_ready():  # pragma: no cover
            return

        # Start push operation
        self.is_processing = True
        self.last_operation = "push"

        # Update UI
        self._update_ui_state()
        if hasattr(self.window, "status_bar"):
            self.window.status_bar.showMessage("Pushing to remote...")

        # Emit signal to worker
        settings = self.settings_manager.load_settings()
        repo_path = settings.git_repo_path if hasattr(settings, "git_repo_path") else ""

        if hasattr(self.window, "request_git_command"):
            self.window.request_git_command.emit(["git", "push"], repo_path)

        # Emit our signal
        self.git_operation_started.emit("push")

        logger.info("Git push started")

    def quick_commit(self, message: str) -> None:
        """
        Quick commit with inline message (v1.9.0+).

        Stages all files and commits with the provided message in one operation.
        Used by QuickCommitWidget for keyboard-driven commits.

        Args:
            message: Commit message
        """
        if not self._ensure_ready():
            return

        if not message or not message.strip():  # pragma: no cover
            logger.warning("Quick commit cancelled: empty message")
            if hasattr(self.window, "status_manager"):
                self.window.status_manager.show_status(
                    "Commit cancelled: empty message", 2000
                )
            return

        # Start commit operation
        self.is_processing = True
        self.last_operation = "commit"
        self.pending_commit_message = message.strip()

        # Update UI
        self._update_ui_state()
        if hasattr(self.window, "status_manager"):  # pragma: no cover
            self.window.status_manager.show_status("Committing changes...", 0)

        # Emit signal to worker (via main window)
        settings = self.settings_manager.load_settings()
        repo_path = settings.git_repo_path if hasattr(settings, "git_repo_path") else ""

        if hasattr(self.window, "request_git_command"):
            self.window.request_git_command.emit(["git", "add", "."], repo_path)

        # Emit our signal
        self.git_operation_started.emit("quick_commit")

        logger.info(f"Quick commit started: '{message[:50]}...'")

    def handle_git_result(self, result: GitResult) -> None:
        """
        Handle Git operation result from worker.

        Args:
            result: GitResult object with operation outcome
        """
        # Handle commit staging -> commit message step
        if self.last_operation == "commit" and result.success:
            # Stage was successful, now do the actual commit
            settings = self.settings_manager.load_settings()
            repo_path = (
                settings.git_repo_path if hasattr(settings, "git_repo_path") else ""
            )

            if hasattr(self.window, "request_git_command"):
                self.window.request_git_command.emit(
                    ["git", "commit", "-m", self.pending_commit_message],
                    repo_path,
                )

            self.last_operation = "commit_final"
            return

        # Operation complete
        self.is_processing = False
        self._update_ui_state()

        # Show result to user
        if result.success:
            self.status_manager.show_message("info", "Success", result.user_message)
            logger.info(f"Git {self.last_operation} succeeded: {result.user_message}")
        else:
            self.status_manager.show_message(
                "critical", "Git Error", result.user_message
            )
            logger.error(f"Git {self.last_operation} failed: {result.user_message}")

        # Emit our signal
        self.git_operation_completed.emit(result.success, result.user_message)

        # Clear state
        self.last_operation = ""
        self.pending_commit_message = None

    def _check_repository_ready(self) -> bool:
        """
        Check if Git repository is configured and ready.

        Returns:
            True if repository ready, False otherwise
        """
        settings = self.settings_manager.load_settings()

        # Check if repository is set
        if not hasattr(settings, "git_repo_path") or not settings.git_repo_path:
            self.status_manager.show_message(
                "info", "No Repository", "Please set a Git repository first."
            )
            return False

        return True

    def _get_busy_message(self) -> str:
        """Get Git-specific busy message."""
        return "Git operation in progress."

    def get_repository_path(self) -> str | None:
        """
        Get current Git repository path.

        Returns:
            Repository path or None
        """
        settings = self.settings_manager.load_settings()
        return settings.git_repo_path if hasattr(settings, "git_repo_path") else None

    def is_repository_set(self) -> bool:
        """Check if Git repository is set."""
        return self.get_repository_path() is not None

    def is_busy(self) -> bool:
        """Check if Git operation is in progress."""
        return self.is_processing

    def get_current_branch(self) -> str:
        """
        Get current Git branch name synchronously.

        This is a fast local operation (<50ms) that runs synchronously
        to provide immediate results for UI operations like GitHub PR creation.

        Returns:
            Branch name (e.g., "main", "feature/new") or empty string if unavailable

        Security:
            - Uses subprocess with shell=False to prevent command injection
            - 2 second timeout to prevent UI blocking
            - Graceful error handling (returns empty string on failure)

        Example:
            >>> handler.get_current_branch()
            'main'

            >>> handler.get_current_branch()  # Detached HEAD
            'HEAD (detached)'

            >>> handler.get_current_branch()  # No repo
            ''
        """
        if not self.is_repository_set():
            return ""

        repo_path = self.get_repository_path()
        if not repo_path:  # pragma: no cover
            return ""

        try:
            # Run git branch --show-current (fast local operation)
            # Security: shell=False prevents command injection
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=2,  # 2 second timeout (local operation)
                shell=False,  # Critical: prevents command injection
                encoding="utf-8",
                errors="replace",
            )

            if result.returncode == 0:
                branch = result.stdout.strip()

                # Handle detached HEAD (empty output from --show-current)
                if not branch:
                    # Try to get commit hash for detached HEAD
                    result2 = subprocess.run(
                        ["git", "rev-parse", "--short", "HEAD"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=2,
                        shell=False,
                        encoding="utf-8",
                        errors="replace",
                    )
                    if result2.returncode == 0:
                        commit_hash = result2.stdout.strip()
                        return f"HEAD (detached at {commit_hash})"
                    else:
                        return "HEAD (detached)"

                return branch

            logger.warning(f"Git branch command failed (code {result.returncode})")

        except subprocess.TimeoutExpired:
            logger.warning("Git branch command timed out after 2s")
        except FileNotFoundError:
            logger.warning("Git command not found")
        except Exception as e:
            logger.exception(f"Unexpected error getting current branch: {e}")

        return ""

    def start_status_refresh(self) -> None:
        """
        Start periodic Git status refresh (v1.9.0+).

        Starts a timer that queries Git status every 5 seconds to update
        the status bar display in real-time.

        Note: Only starts if repository is set and not already running.
        """
        if not self.status_refresh_enabled and self.is_repository_set():
            self.status_refresh_enabled = True
            self.status_timer.start()
            self._refresh_git_status()  # Initial immediate fetch
            logger.info("Git status refresh started (5 second interval)")

    def stop_status_refresh(self) -> None:
        """
        Stop periodic Git status refresh (v1.9.0+).

        Stops the status refresh timer. Called when repository is unset
        or when the application is shutting down.
        """
        if self.status_refresh_enabled:
            self.status_refresh_enabled = False
            self.status_timer.stop()
            logger.info("Git status refresh stopped")

    def _refresh_git_status(self) -> None:
        """
        Request Git status update (non-blocking, v1.9.0+).

        Emits request_git_status signal to trigger GitWorker to fetch
        current repository status. Worker will emit status_ready signal
        with GitStatus object which will update the status bar.

        Skips refresh if:
        - Repository not set
        - Git operation in progress (avoid conflicts)
        """
        if not self.is_repository_set() or self.is_processing:
            return

        repo_path = self.get_repository_path()
        if repo_path and hasattr(self.window, "request_git_status"):
            self.window.request_git_status.emit(repo_path)
            logger.debug("Git status refresh requested")
