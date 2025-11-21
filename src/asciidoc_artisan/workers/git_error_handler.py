"""
Git Error Handler - Error analysis and GitResult creation.

Extracted from GitWorker to reduce class size (MA principle).
Handles error message analysis and GitResult object creation.
"""

import logging

from asciidoc_artisan.core import GitResult

logger = logging.getLogger(__name__)


class GitErrorHandler:
    """
    Handler for Git error analysis and result creation.

    This class was extracted from GitWorker to reduce class size per MA principle.

    Handles:
    - GitResult creation for success/error cases
    - User-friendly error message generation
    - Error categorization (timeout, not found, general)
    """

    def create_success_result(self, stdout: str, stderr: str, exit_code: int) -> GitResult:
        """Create success result."""
        return GitResult(
            success=True,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            user_message="Git command successful.",
        )

    def create_error_result(
        self, stdout: str, stderr: str, exit_code: int | None, command: list[str]
    ) -> GitResult:
        """Create error result with analyzed message."""
        user_message = self.analyze_git_error(stderr, command)
        return GitResult(
            success=False,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            user_message=user_message,
        )

    def create_timeout_error(self, command: list[str], timeout: int) -> GitResult:
        """Create timeout error result."""
        timeout_msg = (
            f"Git operation timed out after {timeout}s. "
            f"Command: {' '.join(command)}. "
            "Check network connection or try again."
        )
        logger.error(timeout_msg)
        return GitResult(
            success=False,
            stdout="",
            stderr=timeout_msg,
            exit_code=None,
            user_message="Git operation timed out",
        )

    def create_not_found_error(self) -> GitResult:
        """Create Git not found error result."""
        error_msg = "Git command not found. Ensure Git is installed and in system PATH."
        logger.error(error_msg)
        return GitResult(
            success=False,
            stdout="",
            stderr=error_msg,
            exit_code=None,
            user_message=error_msg,
        )

    def create_general_error(self, e: Exception, stdout: str, stderr: str, exit_code: int | None) -> GitResult:
        """Create general exception error result."""
        error_msg = f"Unexpected error running Git command: {e}"
        logger.exception("Unexpected Git error")
        return GitResult(
            success=False,
            stdout=stdout,
            stderr=stderr or str(e),
            exit_code=exit_code,
            user_message=error_msg,
        )

    def analyze_git_error(self, stderr: str, command: list[str]) -> str:
        """
        Analyze Git error messages and provide user-friendly explanations.

        Args:
            stderr: Git command standard error output
            command: Git command that was executed

        Returns:
            Human-readable error message for status bar display
        """
        stderr_lower = stderr.lower()

        if "authentication failed" in stderr_lower:
            return "Git Authentication Failed. Check credentials (SSH key/token/helper)."
        elif "not a git repository" in stderr_lower:
            return "Directory is not a Git repository."
        elif "resolve host" in stderr_lower:
            return "Could not connect to Git host. Check internet and repository URL."
        elif "nothing to commit" in stderr_lower:
            return "Nothing to commit."
        else:
            return f"Git command failed: {stderr[:200]}"
