"""
GitHub Handler - Manage GitHub operations via gh CLI.

This module handles all GitHub-related operations:
- Create and list pull requests
- Create and list issues
- Get repository information
- Coordinate between UI dialogs and GitHubCLIWorker

Works with GitHandler to share repository path.
"""

import logging
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal

from asciidoc_artisan.core import GitHubResult
from asciidoc_artisan.ui.base_vcs_handler import BaseVCSHandler
from asciidoc_artisan.ui.github_dialogs import (
    CreateIssueDialog,
    CreatePullRequestDialog,
    IssueListDialog,
    PullRequestListDialog,
)

logger = logging.getLogger(__name__)


class GitHubHandler(BaseVCSHandler, QObject):
    """Handle GitHub operations via gh CLI."""

    # Signals
    github_operation_started = Signal(str)  # Emitted when operation starts
    github_operation_completed = Signal(
        bool, str
    )  # Emitted when operation completes (success, message)

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
        self.current_dialog: Optional[Any] = None

        # Cached data for list dialogs
        self.cached_prs: List[Dict[str, Any]] = []
        self.cached_issues: List[Dict[str, Any]] = []

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
        self.status_manager.show_message(
            "info", "Creating Pull Request", f"Creating PR: {pr_data['title']}..."
        )

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
        self.current_dialog = PullRequestListDialog(
            self.window, pr_data=self.cached_prs
        )

        # Start operation to fetch fresh data
        self.is_processing = True
        self.last_operation = "pr_list"
        self._update_ui_state()

        # Show status
        if not self.cached_prs:
            self.status_manager.show_message(
                "info", "Loading Pull Requests", "Fetching pull requests..."
            )

        # Emit signal to worker
        repo_path = self.git_handler.get_repository_path()
        if hasattr(self.window, "request_github_command"):
            self.window.request_github_command.emit(
                "list_pull_requests", {"state": "open", "working_dir": repo_path}
            )

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
        self.status_manager.show_message(
            "info", "Creating Issue", f"Creating issue: {issue_data['title']}..."
        )

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
        self.current_dialog = IssueListDialog(
            self.window, issue_data=self.cached_issues
        )

        # Start operation to fetch fresh data
        self.is_processing = True
        self.last_operation = "issue_list"
        self._update_ui_state()

        # Show status
        if not self.cached_issues:
            self.status_manager.show_message(
                "info", "Loading Issues", "Fetching issues..."
            )

        # Emit signal to worker
        repo_path = self.git_handler.get_repository_path()
        if hasattr(self.window, "request_github_command"):
            self.window.request_github_command.emit(
                "list_issues", {"state": "open", "working_dir": repo_path}
            )

        # Emit our signal
        self.github_operation_started.emit("issue_list")

        # Show dialog (non-modal)
        self.current_dialog.show()

        logger.info("Listing issues")

    def get_repo_info(self) -> None:
        """Get GitHub repository information."""
        if not self._ensure_ready():
            return

        # Start operation
        self.is_processing = True
        self.last_operation = "repo_info"
        self._update_ui_state()

        # Show status
        self.status_manager.show_message(
            "info", "Repository Info", "Fetching repository information..."
        )

        # Emit signal to worker
        repo_path = self.git_handler.get_repository_path()
        if hasattr(self.window, "request_github_command"):
            self.window.request_github_command.emit(
                "get_repo_info", {"working_dir": repo_path}
            )

        # Emit our signal
        self.github_operation_started.emit("repo_info")

        logger.info("Fetching repository info")

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
            # Update UI based on operation type
            if result.operation == "pr_create":
                self._handle_pr_created(result)
            elif result.operation == "pr_list":
                self._handle_pr_list(result)
            elif result.operation == "issue_create":
                self._handle_issue_created(result)
            elif result.operation == "issue_list":
                self._handle_issue_list(result)
            elif result.operation == "repo_info":
                self._handle_repo_info(result)

            # Show success message
            self.status_manager.show_message("info", "Success", result.user_message)
            logger.info(
                f"GitHub {self.last_operation} succeeded: {result.user_message}"
            )

            # Emit our signal
            self.github_operation_completed.emit(True, result.user_message)
        else:
            # Show error message
            self.status_manager.show_message(
                "critical", "GitHub Error", result.user_message
            )
            logger.error(f"GitHub {self.last_operation} failed: {result.user_message}")

            # Emit our signal
            self.github_operation_completed.emit(False, result.user_message)

        # Clear state
        self.last_operation = ""

    def _handle_pr_created(self, result: GitHubResult) -> None:
        """Handle successful PR creation."""
        if result.data and "url" in result.data:
            pr_number = result.data.get("number", "?")
            pr_url = result.data.get("url", "")
            logger.info(f"PR #{pr_number} created: {pr_url}")

    def _handle_pr_list(self, result: GitHubResult) -> None:
        """Handle successful PR list retrieval."""
        if result.data:
            # Update cached data
            self.cached_prs = result.data if isinstance(result.data, list) else []

            # Update dialog if it's open
            if self.current_dialog and isinstance(
                self.current_dialog, PullRequestListDialog
            ):
                self.current_dialog.set_pr_data(self.cached_prs)

            logger.info(f"Loaded {len(self.cached_prs)} pull requests")

    def _handle_issue_created(self, result: GitHubResult) -> None:
        """Handle successful issue creation."""
        if result.data and "url" in result.data:
            issue_number = result.data.get("number", "?")
            issue_url = result.data.get("url", "")
            logger.info(f"Issue #{issue_number} created: {issue_url}")

    def _handle_issue_list(self, result: GitHubResult) -> None:
        """Handle successful issue list retrieval."""
        if result.data:
            # Update cached data
            self.cached_issues = result.data if isinstance(result.data, list) else []

            # Update dialog if it's open
            if self.current_dialog and isinstance(self.current_dialog, IssueListDialog):
                self.current_dialog.set_issue_data(self.cached_issues)

            logger.info(f"Loaded {len(self.cached_issues)} issues")

    def _handle_repo_info(self, result: GitHubResult) -> None:
        """Handle successful repo info retrieval."""
        if result.data:
            # Extract repository information
            repo_name = result.data.get("nameWithOwner", "Unknown")
            name = result.data.get("name", "Unknown")
            description = result.data.get("description", "No description")
            stars = result.data.get("stargazerCount", 0)
            forks = result.data.get("forkCount", 0)
            visibility = result.data.get("visibility", "Unknown")
            url = result.data.get("url", "")

            # Get default branch name from nested object
            default_branch_ref = result.data.get("defaultBranchRef", {})
            default_branch = default_branch_ref.get("name", "Unknown") if default_branch_ref else "Unknown"

            # Log detailed information
            logger.info(f"Repository: {repo_name}")
            logger.info(f"  Description: {description}")
            logger.info(f"  Default Branch: {default_branch}")
            logger.info(f"  Visibility: {visibility}")
            logger.info(f"  Stars: {stars}, Forks: {forks}")
            logger.info(f"  URL: {url}")

            # Show concise info in status bar
            status_msg = f"{repo_name} | {visibility} | ★{stars} ⑂{forks} | {default_branch}"
            self.status_manager.show_message("info", "Repository Info", status_msg)

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

        # Check if gh CLI is authenticated (advisory check)
        # Note: Worker will provide detailed error if authentication fails
        # TODO: Add optional gh auth status check here if desired

        return True

    def _get_busy_message(self) -> str:
        """Get GitHub-specific busy message."""
        return "GitHub operation in progress."

    def _get_current_branch(self) -> str:
        """
        Get current Git branch name.

        Returns:
            Branch name or empty string if unavailable
        """
        # TODO: Integrate with GitWorker to get actual branch
        # For now, return empty string (dialog will use editable combobox)
        return ""

    def is_busy(self) -> bool:
        """Check if GitHub operation is in progress."""
        return self.is_processing
