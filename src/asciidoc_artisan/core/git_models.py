"""
Git and GitHub Data Models.

Extracted from models.py for MA principle compliance.
Contains models for Git operations and GitHub CLI integration.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class GitResult(BaseModel):
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

    Validation:
        - user_message cannot be empty when provided
        - exit_code must be non-negative if provided

    Example:
        ```python
        # Successful operation
        result = GitResult(
            success=True,
            stdout="On branch main\\nYour branch is up to date",
            stderr="",
            exit_code=0,
            user_message="Git status retrieved successfully"
        )

        # Failed operation
        result = GitResult(
            success=False,
            stdout="",
            stderr="fatal: not a git repository",
            exit_code=128,
            user_message="Not a Git repository"
        )
        ```
    """

    success: bool = Field(..., description="True if operation succeeded")
    stdout: str = Field(default="", description="Standard output from Git command")
    stderr: str = Field(default="", description="Standard error from Git command")
    exit_code: int | None = Field(default=None, description="Process exit code (-1 for errors/cancelled)")
    user_message: str = Field(..., description="Human-readable status message")

    @field_validator("user_message")
    @classmethod
    def validate_user_message(cls, v: str) -> str:
        """Ensure user message is not empty."""
        if not v or not v.strip():
            raise ValueError("user_message cannot be empty")
        return v.strip()

    model_config = {
        "frozen": False,  # Allow mutation for compatibility
        "validate_assignment": True,  # Validate on field assignment
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }


class GitStatus(BaseModel):
    """
    Git repository status information.

    Used by GitWorker to provide real-time repository status updates
    for display in the status bar.

    Attributes:
        branch: Current branch name
        modified_count: Number of modified files (working tree)
        staged_count: Number of staged files (index)
        untracked_count: Number of untracked files
        has_conflicts: Whether merge conflicts exist
        ahead_count: Number of commits ahead of remote
        behind_count: Number of commits behind remote
        is_dirty: Whether working tree has uncommitted changes

    Validation:
        - branch cannot be empty
        - All count fields must be non-negative

    Example:
        ```python
        # Clean repository
        status = GitStatus(
            branch="main",
            modified_count=0,
            staged_count=0,
            untracked_count=0,
            has_conflicts=False,
            ahead_count=0,
            behind_count=0,
            is_dirty=False
        )

        # Dirty repository with changes
        status = GitStatus(
            branch="feature/git-improvements",
            modified_count=3,
            staged_count=1,
            untracked_count=2,
            has_conflicts=False,
            ahead_count=2,
            behind_count=0,
            is_dirty=True
        )
        ```
    """

    branch: str = Field(default="", description="Current branch name")
    modified_count: int = Field(default=0, description="Number of modified files")
    staged_count: int = Field(default=0, description="Number of staged files")
    untracked_count: int = Field(default=0, description="Number of untracked files")
    has_conflicts: bool = Field(default=False, description="Whether conflicts exist")
    ahead_count: int = Field(default=0, description="Commits ahead of remote")
    behind_count: int = Field(default=0, description="Commits behind remote")
    is_dirty: bool = Field(default=False, description="Whether working tree has uncommitted changes")

    @field_validator(
        "modified_count",
        "staged_count",
        "untracked_count",
        "ahead_count",
        "behind_count",
    )
    @classmethod
    def validate_count(cls, v: int) -> int:
        """Ensure count is non-negative."""
        if v < 0:
            raise ValueError("count must be non-negative")
        return v

    model_config = {
        "frozen": False,  # Allow mutation for compatibility
        "validate_assignment": True,  # Validate on field assignment
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }


class GitHubResult(BaseModel):
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

    Validation:
        - operation must be one of the allowed operation types
        - user_message cannot be empty when provided
        - data must be present when success=True for most operations

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

    success: bool = Field(..., description="True if operation succeeded")
    data: dict[str, Any] | list[dict[str, Any]] | None = Field(
        default=None,
        description="Parsed JSON data from GitHub CLI (dict for single results, list for list operations)",
    )
    error: str = Field(default="", description="Error message from GitHub CLI")
    user_message: str = Field(..., description="Human-readable status message")
    operation: str = Field(..., description="Operation type identifier")

    @field_validator("user_message")
    @classmethod
    def validate_user_message(cls, v: str) -> str:
        """Ensure user message is not empty."""
        if not v or not v.strip():
            raise ValueError("user_message cannot be empty")
        return v.strip()

    @field_validator("operation")
    @classmethod
    def validate_operation(cls, v: str) -> str:
        """Validate operation type is known."""
        allowed_operations = {
            # Specific operations (full names)
            "pr_create",
            "pr_list",
            "issue_create",
            "issue_list",
            "repo_view",
            "repo_info",
            # Generic subcommands (from args[0])
            "pr",
            "issue",
            "repo",
            "gh",
            # Special operations
            "cancelled",
            "unknown",
        }
        if v not in allowed_operations:
            raise ValueError(f"Unknown operation: {v}. Must be one of {allowed_operations}")
        return v

    model_config = {
        "frozen": False,  # Allow mutation for compatibility
        "validate_assignment": True,  # Validate on field assignment
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }
