"""
Core data models for AsciiDoc Artisan.

This module contains simple data structures used throughout the application:
- GitResult: Result of Git operations
- Additional models as needed

These models represent the return types and data structures that don't
belong to specific worker classes or UI components.
"""

from typing import NamedTuple, Optional


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
