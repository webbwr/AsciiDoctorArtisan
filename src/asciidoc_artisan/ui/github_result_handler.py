"""
GitHub Result Handler - Processes GitHub operation results.

Extracted from GitHubHandler to reduce class size (MA principle).
Handles parsing and displaying results from GitHub CLI operations.
"""

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from asciidoc_artisan.core import GitHubResult

logger = logging.getLogger(__name__)


class GitHubResultHandler:
    """
    Processes GitHub operation results.

    Extracted from GitHubHandler per MA principle (~120 lines).

    Handles:
    - PR creation results
    - PR list results
    - Issue creation results
    - Issue list results
    - Repository info results

    Example:
        handler = GitHubResultHandler(
            status_manager=status_manager,
            parent_window=window,
        )
        handler.handle_pr_created(result)
    """

    def __init__(
        self,
        status_manager: Any,
        parent_window: Any,
    ) -> None:
        """
        Initialize result handler.

        Args:
            status_manager: Status manager for showing messages
            parent_window: Parent window for dialogs
        """
        self.status_manager = status_manager
        self.window = parent_window

        # Cached data for list dialogs
        self.cached_prs: list[dict[str, Any]] = []
        self.cached_issues: list[dict[str, Any]] = []

    def handle_pr_created(self, result: "GitHubResult") -> None:
        """Handle successful PR creation."""
        if result.data and "url" in result.data:
            pr_number = result.data.get("number", "?")
            pr_url = result.data.get("url", "")
            logger.info(f"PR #{pr_number} created: {pr_url}")

    def handle_pr_list(
        self,
        result: "GitHubResult",
        current_dialog: Any | None,
    ) -> list[dict[str, Any]]:
        """
        Handle successful PR list retrieval.

        Args:
            result: GitHub result with PR data
            current_dialog: Current open dialog (if any)

        Returns:
            Updated list of PRs
        """
        if result.data:
            # Update cached data
            self.cached_prs = result.data if isinstance(result.data, list) else []

            # Update dialog if it's open
            if current_dialog is not None:
                # Import here to avoid circular imports
                from asciidoc_artisan.ui.github_dialogs import PullRequestListDialog

                if isinstance(current_dialog, PullRequestListDialog):
                    current_dialog.set_pr_data(self.cached_prs)

            logger.info(f"Loaded {len(self.cached_prs)} pull requests")

        return self.cached_prs

    def handle_issue_created(self, result: "GitHubResult") -> None:
        """Handle successful issue creation."""
        if result.data and "url" in result.data:
            issue_number = result.data.get("number", "?")
            issue_url = result.data.get("url", "")
            logger.info(f"Issue #{issue_number} created: {issue_url}")

    def handle_issue_list(
        self,
        result: "GitHubResult",
        current_dialog: Any | None,
    ) -> list[dict[str, Any]]:
        """
        Handle successful issue list retrieval.

        Args:
            result: GitHub result with issue data
            current_dialog: Current open dialog (if any)

        Returns:
            Updated list of issues
        """
        if result.data:
            # Update cached data
            self.cached_issues = result.data if isinstance(result.data, list) else []

            # Update dialog if it's open
            if current_dialog is not None:
                # Import here to avoid circular imports
                from asciidoc_artisan.ui.github_dialogs import IssueListDialog

                if isinstance(current_dialog, IssueListDialog):
                    current_dialog.set_issue_data(self.cached_issues)

            logger.info(f"Loaded {len(self.cached_issues)} issues")

        return self.cached_issues

    def handle_repo_info(
        self,
        result: "GitHubResult",
        last_operation: str,
    ) -> None:
        """
        Handle successful repo info retrieval.

        Args:
            result: GitHub result with repo data
            last_operation: The operation that triggered this (repo_info or repo_info_silent)
        """
        if not result.data:
            return

        # Extract repository information
        repo_name = result.data.get("nameWithOwner", "Unknown")
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

        # Update status bar with concise info
        status_msg = f"GitHub: {repo_name} | {visibility} | ★{stars} ⑂{forks} | {default_branch}"
        self.status_manager.show_status(status_msg, timeout=0)  # Permanent
        logger.info(f"Status bar updated: {status_msg}")

        # Show full repository information in a dialog
        # (only if user explicitly requested it, not on silent startup)
        if last_operation == "repo_info" and last_operation != "repo_info_silent":
            self._show_repo_info_dialog(
                repo_name=repo_name,
                description=description,
                default_branch=default_branch,
                visibility=visibility,
                stars=stars,
                forks=forks,
                url=url,
            )

    def _show_repo_info_dialog(
        self,
        repo_name: str,
        description: str,
        default_branch: str,
        visibility: str,
        stars: int,
        forks: int,
        url: str,
    ) -> None:
        """Show repository information dialog."""
        from PySide6.QtWidgets import QMessageBox

        info_text = f"""<b>Repository:</b> {repo_name}<br><br>
<b>Description:</b> {description}<br><br>
<b>Default Branch:</b> {default_branch}<br>
<b>Visibility:</b> {visibility}<br>
<b>Stars:</b> {stars} ★<br>
<b>Forks:</b> {forks} ⑂<br><br>
<b>URL:</b> <a href="{url}">{url}</a>"""

        msg_box = QMessageBox(self.window)
        msg_box.setWindowTitle("Repository Information")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(info_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

        logger.info("Repository info dialog shown")
