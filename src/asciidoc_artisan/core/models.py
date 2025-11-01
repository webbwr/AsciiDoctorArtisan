"""
Core data models for AsciiDoc Artisan.

This module contains simple data structures used throughout the application:
- GitResult: Result of Git operations
- GitHubResult: Result of GitHub CLI operations
- ChatMessage: Single message in Ollama AI chat conversation
- Additional models as needed

These models use Pydantic for runtime validation and type safety (v1.7.0+).
"""

from typing import Any, Dict, Optional

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
    exit_code: Optional[int] = Field(
        default=None, description="Process exit code (-1 for errors/cancelled)"
    )
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
    data: Optional[Dict[str, Any] | list[Dict[str, Any]]] = Field(
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
            raise ValueError(
                f"Unknown operation: {v}. Must be one of {allowed_operations}"
            )
        return v

    model_config = {
        "frozen": False,  # Allow mutation for compatibility
        "validate_assignment": True,  # Validate on field assignment
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }


class ChatMessage(BaseModel):
    """
    Single message in an Ollama AI chat conversation.

    Used by OllamaChatWorker and ChatManager to represent both user messages
    and AI responses in the chat history.

    Attributes:
        role: Message sender ("user" or "assistant")
        content: Message text content
        timestamp: Unix timestamp when message was created
        model: Name of Ollama model that generated this message (for assistant messages)
        context_mode: Interaction mode when message was sent

    Validation:
        - role must be "user" or "assistant"
        - content cannot be empty
        - timestamp must be non-negative
        - context_mode must be one of allowed modes

    Example:
        ```python
        import time

        # User message
        user_msg = ChatMessage(
            role="user",
            content="How do I create a table in AsciiDoc?",
            timestamp=time.time(),
            model="phi3:mini",
            context_mode="syntax"
        )

        # AI response
        ai_msg = ChatMessage(
            role="assistant",
            content="Here's how to create a table:\\n|===\\n|Header 1 |Header 2\\n|Cell 1   |Cell 2\\n|===",
            timestamp=time.time(),
            model="phi3:mini",
            context_mode="syntax"
        )
        ```
    """

    role: str = Field(..., description='Message sender: "user" or "assistant"')
    content: str = Field(..., description="Message text content")
    timestamp: float = Field(..., description="Unix timestamp when message was created")
    model: str = Field(..., description="Ollama model name (e.g., phi3:mini)")
    context_mode: str = Field(
        ..., description='Context mode: "document", "syntax", "general", or "editing"'
    )

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Ensure role is either user or assistant."""
        allowed_roles = {"user", "assistant"}
        if v not in allowed_roles:
            raise ValueError(f"role must be one of {allowed_roles}, got '{v}'")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v.strip()

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: float) -> float:
        """Ensure timestamp is non-negative."""
        if v < 0:
            raise ValueError("timestamp must be non-negative")
        return v

    @field_validator("context_mode")
    @classmethod
    def validate_context_mode(cls, v: str) -> str:
        """Validate context mode is known."""
        allowed_modes = {"document", "syntax", "general", "editing"}
        if v not in allowed_modes:
            raise ValueError(
                f"context_mode must be one of {allowed_modes}, got '{v}'"
            )
        return v

    model_config = {
        "frozen": False,  # Allow mutation for compatibility
        "validate_assignment": True,  # Validate on field assignment
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }
