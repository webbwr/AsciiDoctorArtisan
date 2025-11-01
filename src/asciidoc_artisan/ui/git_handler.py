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
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import Signal
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
        self.pending_commit_message: Optional[str] = None

    def initialize(self) -> None:
        """
        Initialize Git handler from settings.

        Loads saved Git repository path from settings and validates it.
        Called after UI setup is complete.
        """
        settings = self.settings_manager.load_settings()

        # Load repository path from settings
        if hasattr(settings, "git_repo_path") and settings.git_repo_path:
            repo_path = settings.git_repo_path

            # Validate it's still a Git repository
            if (Path(repo_path) / ".git").is_dir():
                logger.info(f"Git repository loaded from settings: {repo_path}")

                # Update UI state
                if hasattr(self.window, "_update_ui_state"):
                    self.window._update_ui_state()
            else:
                logger.warning(
                    f"Saved Git repository no longer valid: {repo_path}"
                )
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
            self.window.status_bar.showMessage(f"Git repository set: {dir_path}")

        # Update UI state
        if hasattr(self.window, "_update_ui_state"):
            self.window._update_ui_state()

        logger.info(f"Git repository set: {dir_path}")

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
        if not self._ensure_ready():
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
        if not self._ensure_ready():
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

    def get_repository_path(self) -> Optional[str]:
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
