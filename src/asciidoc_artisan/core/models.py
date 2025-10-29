"""
Core data models for AsciiDoc Artisan.

This module contains simple data structures used throughout the application:
- GitResult: Result of Git operations
- GitHubResult: Result of GitHub CLI operations
- Additional models as needed

These models represent the return types and data structures that don't
belong to specific worker classes or UI components.
"""

from dataclasses import dataclass
from typing import Any, Dict, NamedTuple, Optional


class GitResult(NamedTuple):
    """
    Result of a Git operation execution.

    Used by GitWorker to communicate the outcome of Git commands
    back to the main UI thread.

    Attributes:
        success: True if Git command completed successfully
        stdout: Standard output from Git command
        stderr: Standard error from Git command
        exit_code: Process exit code (None if not executed)
        user_message: Human-readable message for status bar display
    """

    success: bool
    stdout: str
    stderr: str
    exit_code: Optional[int]
    user_message: str


@dataclass
class GitHubResult:
    """
    Result of a GitHub CLI operation execution.

    Used by GitHubCLIWorker to communicate the outcome of GitHub CLI commands
    back to the main UI thread.

    Attributes:
        success: True if GitHub CLI command completed successfully
        data: Parsed JSON data from GitHub CLI output (None if failed or no JSON)
        error: Error message from GitHub CLI standard error
        user_message: Human-readable message for status bar display
        operation: Operation type (e.g., "pr_create", "issue_list", "repo_view")

    Example:
        ```python
        # Successful PR creation
        result = GitHubResult(
            success=True,
            data={"number": 42, "url": "https://github.com/user/repo/pull/42"},
            error="",
            user_message="Pull request #42 created successfully",
            operation="pr_create"
        )

        # Failed authentication
        result = GitHubResult(
            success=False,
            data=None,
            error="not logged into any GitHub hosts",
            user_message="Not authenticated. Run 'gh auth login' in terminal.",
            operation="pr_list"
        )
        ```
    """

    success: bool
    data: Optional[Dict[str, Any]]
    error: str
    user_message: str
    operation: str
