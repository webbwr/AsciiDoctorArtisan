"""
GitHub Handler - Manage GitHub operations via gh CLI.

MA principle: Reduced from 434→~320 lines by extracting github_result_handler.py.

This module handles all GitHub-related operations:
- Create and list pull requests
- Create and list issues
- Get repository information
- Coordinate between UI dialogs and GitHubCLIWorker

Works with GitHandler to share repository path.
"""

import logging
import shutil
from typing import Any

from PySide6.QtCore import QObject, Signal

from asciidoc_artisan.core import GitHubResult
from asciidoc_artisan.ui.base_vcs_handler import BaseVCSHandler
from asciidoc_artisan.ui.github_dialogs import (
    CreateIssueDialog,
    CreatePullRequestDialog,
    IssueListDialog,
    PullRequestListDialog,
)
from asciidoc_artisan.ui.github_result_handler import GitHubResultHandler

logger = logging.getLogger(__name__)


class GitHubHandler(BaseVCSHandler, QObject):
    """Handle GitHub operations via gh CLI."""

    # Signals
    github_operation_started = Signal(str)  # Emitted when operation starts
    github_operation_completed = Signal(bool, str)  # Emitted when operation completes (success, message)

    def __init__(
        self,
        parent_window: Any,
        settings_manager: Any,
        status_manager: Any,
        git_handler: Any,
    ) -> None:
        """
        Initialize GitHubHandler.

        Args:
            parent_window: Main window (for dialogs and signals)
            settings_manager: Settings manager instance
            status_manager: Status manager instance
            git_handler: GitHandler instance (to share repository path)
        """
        # Initialize both parent classes
        BaseVCSHandler.__init__(self, parent_window, settings_manager, status_manager)
        QObject.__init__(self)

        # GitHub-specific dependencies
        self.git_handler = git_handler

        # GitHub-specific state
        self.current_dialog: Any | None = None

        # Result handler (extracted per MA principle)
        self._result_handler = GitHubResultHandler(
            status_manager=status_manager,
            parent_window=parent_window,
        )

    def initialize(self) -> None:
        """
        Initialize GitHub handler and fetch repository info if Git repo is set.

        Called after UI setup is complete and Git repository is loaded.
        Automatically fetches and displays repository information in status bar.
        """
        # Check if gh CLI is available
        if not shutil.which("gh"):  # pragma: no cover
            logger.debug("GitHub CLI (gh) not found - skipping automatic repo info fetch")
            return

        # Check if Git repository is set
        if self.git_handler.is_repository_set():
            # Silently fetch repository info to update status bar
            logger.info("Git repository is set, fetching GitHub repository info...")
            self.get_repo_info(silent=True)

    def create_pull_request(self) -> None:
        """Show dialog and create a GitHub pull request."""
        if not self._ensure_ready():
            return

        # Get current branch for pre-population
        current_branch = self._get_current_branch()

        # Show dialog
        dialog = CreatePullRequestDialog(self.window, current_branch=current_branch)
        if not dialog.exec():
            return  # User cancelled

        # Get PR data from dialog
        pr_data = dialog.get_pr_data()

        # Start operation
        self.is_processing = True
        self.last_operation = "pr_create"
        self._update_ui_state()

        # Show status
        self.status_manager.show_message("info", "Creating Pull Request", f"Creating PR: {pr_data['title']}...")

        # Emit signal to worker (via main window)
        repo_path = self.git_handler.get_repository_path()
        if hasattr(self.window, "request_github_command"):
            self.window.request_github_command.emit(
                "create_pull_request",
                {
                    "title": pr_data["title"],
                    "body": pr_data["body"],
                    "base": pr_data["base"],
                    "head": pr_data["head"],
                    "working_dir": repo_path,
                },
            )

        # Emit our signal
        self.github_operation_started.emit("pr_create")

        logger.info(f"Creating PR: {pr_data['title']}")

    def list_pull_requests(self) -> None:
        """Show dialog and list GitHub pull requests."""
        if not self._ensure_ready():
            return

        # Create and show dialog with cached data (will update when worker responds)
        self.current_dialog = PullRequestListDialog(self.window, pr_data=self.cached_prs)

        # Start operation to fetch fresh data
        self.is_processing = True
        self.last_operation = "pr_list"
        self._update_ui_state()

        # Show status
        if not self.cached_prs:
            self.status_manager.show_message("info", "Loading Pull Requests", "Fetching pull requests...")

        # Emit signal to worker
        repo_path = self.git_handler.get_repository_path()
        if hasattr(self.window, "request_github_command"):
            self.window.request_github_command.emit("list_pull_requests", {"state": "open", "working_dir": repo_path})

        # Emit our signal
        self.github_operation_started.emit("pr_list")

        # Show dialog (non-modal)
        self.current_dialog.show()

        logger.info("Listing pull requests")

    def create_issue(self) -> None:
        """Show dialog and create a GitHub issue."""
        if not self._ensure_ready():
            return

        # Show dialog
        dialog = CreateIssueDialog(self.window)
        if not dialog.exec():
            return  # User cancelled

        # Get issue data from dialog
        issue_data = dialog.get_issue_data()

        # Start operation
        self.is_processing = True
        self.last_operation = "issue_create"
        self._update_ui_state()

        # Show status
        self.status_manager.show_message("info", "Creating Issue", f"Creating issue: {issue_data['title']}...")

        # Emit signal to worker
        repo_path = self.git_handler.get_repository_path()
        if hasattr(self.window, "request_github_command"):
            self.window.request_github_command.emit(
                "create_issue",
                {
                    "title": issue_data["title"],
                    "body": issue_data["body"],
                    "working_dir": repo_path,
                },
            )

        # Emit our signal
        self.github_operation_started.emit("issue_create")

        logger.info(f"Creating issue: {issue_data['title']}")

    def list_issues(self) -> None:
        """Show dialog and list GitHub issues."""
        if not self._ensure_ready():
            return

        # Create and show dialog with cached data
        self.current_dialog = IssueListDialog(self.window, issue_data=self.cached_issues)

        # Start operation to fetch fresh data
        self.is_processing = True
        self.last_operation = "issue_list"
        self._update_ui_state()

        # Show status
        if not self.cached_issues:
            self.status_manager.show_message("info", "Loading Issues", "Fetching issues...")

        # Emit signal to worker
        repo_path = self.git_handler.get_repository_path()
        if hasattr(self.window, "request_github_command"):
            self.window.request_github_command.emit("list_issues", {"state": "open", "working_dir": repo_path})

        # Emit our signal
        self.github_operation_started.emit("issue_list")

        # Show dialog (non-modal)
        self.current_dialog.show()

        logger.info("Listing issues")

    def get_repo_info(self, silent: bool = False) -> None:
        """Get GitHub repository information.

        Args:
            silent: If True, fetches info silently without showing "Fetching..." status
                   (used for automatic updates on startup)
        """
        if not self._ensure_ready():
            return

        # Start operation
        self.is_processing = True
        self.last_operation = "repo_info" if not silent else "repo_info_silent"
        self._update_ui_state()

        # Show status in status bar only if not silent
        if not silent:
            self.status_manager.show_status("Fetching repository information...", timeout=5000)

        # Emit signal to worker
        repo_path = self.git_handler.get_repository_path()
        if hasattr(self.window, "request_github_command"):
            self.window.request_github_command.emit("get_repo_info", {"working_dir": repo_path})

        # Emit our signal
        self.github_operation_started.emit("repo_info")

        logger.info(f"Fetching repository info (silent={silent})")

    def handle_github_result(self, result: GitHubResult) -> None:
        """
        Handle GitHub operation result from worker.

        Args:
            result: GitHubResult object with operation outcome
        """
        # Operation complete
        self.is_processing = False
        self._update_ui_state()

        # Handle success
        if result.success:
            # Update UI based on operation type (delegated to result handler)
            if result.operation == "pr_create":
                self._result_handler.handle_pr_created(result)
            elif result.operation == "pr_list":
                self._result_handler.handle_pr_list(result, self.current_dialog)
            elif result.operation == "issue_create":
                self._result_handler.handle_issue_created(result)
            elif result.operation == "issue_list":
                self._result_handler.handle_issue_list(result, self.current_dialog)
            elif result.operation == "repo_info":
                self._result_handler.handle_repo_info(result, self.last_operation)

            # Show success message (skip dialog for repo_info - already shown in status bar)
            if result.operation != "repo_info":
                self.status_manager.show_message("info", "Success", result.user_message)
            logger.info(f"GitHub {self.last_operation} succeeded: {result.user_message}")

            # Emit our signal
            self.github_operation_completed.emit(True, result.user_message)
        else:
            # Show error message
            self.status_manager.show_message("critical", "GitHub Error", result.user_message)
            logger.error(f"GitHub {self.last_operation} failed: {result.user_message}")

            # Emit our signal
            self.github_operation_completed.emit(False, result.user_message)

        # Clear state
        self.last_operation = ""

    def _check_repository_ready(self) -> bool:
        """
        Check if Git repository is configured (required for GitHub operations).

        Returns:
            True if repository ready, False otherwise
        """
        # Check if Git repository is set (required for GitHub operations)
        if not self.git_handler.is_repository_set():
            self.status_manager.show_message(
                "info",
                "No Repository",
                "Please set a Git repository first (Git → Set Repository).",
            )
            return False

        # Authentication check is performed by GitHubCLIWorker
        # This allows operations to proceed immediately without blocking on `gh auth status`
        # If authentication fails, worker will return a clear error message to the user
        return True

    def _get_busy_message(self) -> str:
        """Get GitHub-specific busy message."""
        return "GitHub operation in progress."

    def _get_current_branch(self) -> str:
        """
        Get current Git branch name from GitHandler.

        Returns:
            Branch name or empty string if unavailable

        Example:
            >>> handler._get_current_branch()
            'main'

            >>> handler._get_current_branch()  # No git_handler
            ''
        """
        # Use GitHandler to get actual current branch (v1.9.0+)
        if hasattr(self.window, "git_handler") and self.window.git_handler:
            return self.window.git_handler.get_current_branch()
        return ""

    def is_busy(self) -> bool:
        """Check if GitHub operation is in progress."""
        return self.is_processing

    # Backward compatibility properties for cached data
    @property
    def cached_prs(self) -> list[dict[str, Any]]:
        """Get cached PRs (backward compatibility)."""
        return self._result_handler.cached_prs

    @cached_prs.setter
    def cached_prs(self, value: list[dict[str, Any]]) -> None:
        """Set cached PRs (backward compatibility)."""
        self._result_handler.cached_prs = value

    @property
    def cached_issues(self) -> list[dict[str, Any]]:
        """Get cached issues (backward compatibility)."""
        return self._result_handler.cached_issues

    @cached_issues.setter
    def cached_issues(self, value: list[dict[str, Any]]) -> None:
        """Set cached issues (backward compatibility)."""
        self._result_handler.cached_issues = value
