"""
GitHub Result Factory - Creates GitHubResult objects for various outcomes.

Extracted from GitHubCLIWorker to reduce class size (MA principle).
Handles result creation, error parsing, and error emission.
"""

import json
import logging
from typing import Any

from asciidoc_artisan.core.models import GitHubResult

logger = logging.getLogger(__name__)


class GitHubResultFactory:
    """
    Factory for creating GitHubResult objects.

    This class was extracted from GitHubCLIWorker to reduce class size
    per MA principle (520→244 lines).

    Handles:
    - Result creation for success/error cases
    - Error message parsing
    - Error result emission
    """

    def __init__(self, result_signal: Any) -> None:
        """
        Initialize the result factory.

        Args:
            result_signal: Signal to emit results (github_result_ready, PySide6 SignalInstance)
        """
        self.result_signal = result_signal

    def check_and_handle_cancellation(self, operation: str | None) -> bool:
        """
        Check for cancellation and emit result if cancelled.

        Note: Cancellation checking is delegated to worker's _check_cancellation method.
        This is a placeholder for the pattern - actual implementation needs worker reference.

        Args:
            operation: Operation name for result tracking

        Returns:
            True if cancelled, False otherwise

        MA principle: Extracted from run_gh_command (8 lines).
        """
        # Note: This method is kept in GitHubCLIWorker as it needs self._check_cancellation()
        # and self.reset_cancellation(). This is a documentation placeholder.
        return False

    def parse_json_output(self, stdout: str) -> Any:
        """
        Parse GitHub CLI JSON output or wrap plain text.

        Args:
            stdout: GitHub CLI command output

        Returns:
            Parsed JSON data or dict with "output" key for plain text

        MA principle: Extracted from run_gh_command (9 lines).
        """
        if not stdout:
            return None

        try:
            # GitHub CLI returns JSON when --json flag is used.
            return json.loads(stdout)
        except json.JSONDecodeError:
            # Not JSON (e.g. plain text output from gh auth status).
            logger.debug("GitHub CLI output is not JSON")
            return {"output": stdout}

    def create_success_result(self, data: Any, operation: str) -> GitHubResult:
        """
        Create success GitHubResult.

        Args:
            data: Parsed JSON data or None
            operation: Operation name for result tracking

        Returns:
            GitHubResult with success=True

        MA principle: Extracted from run_gh_command (7 lines).
        """
        logger.info("GitHub CLI command successful")
        return GitHubResult(
            success=True,
            data=data,
            error="",
            user_message="GitHub command successful.",
            operation=operation,
        )

    def create_error_result(self, stderr: str, args: list[str], operation: str) -> GitHubResult:
        """
        Create error GitHubResult with parsed user message.

        Args:
            stderr: GitHub CLI error output
            args: GitHub CLI arguments (for error parsing)
            operation: Operation name for result tracking

        Returns:
            GitHubResult with success=False and user-friendly message

        MA principle: Extracted from run_gh_command (10 lines).
        """
        user_message = self.parse_error(stderr, args)
        logger.error(f"GitHub CLI command failed: {user_message}")
        return GitHubResult(
            success=False,
            data=None,
            error=stderr,
            user_message=user_message,
            operation=operation,
        )

    def emit_timeout_error(self, args: list[str], timeout: float, operation: str) -> None:
        """
        Emit timeout error result.

        Args:
            args: GitHub CLI arguments that timed out
            timeout: Timeout value in seconds
            operation: Operation name for result tracking

        MA principle: Extracted from run_gh_command (15 lines).
        """
        timeout_msg = (
            f"GitHub CLI operation timed out after {timeout}s. "
            f"Command: {' '.join(['gh'] + args)}. "
            "Check network connection or try again."
        )
        logger.error(timeout_msg)
        self.result_signal.emit(
            GitHubResult(
                success=False,
                data=None,
                error=timeout_msg,
                user_message="GitHub operation timed out",
                operation=operation,
            )
        )

    def emit_not_found_error(self, operation: str) -> None:
        """
        Emit GitHub CLI not found error result.

        Args:
            operation: Operation name for result tracking

        MA principle: Extracted from run_gh_command (13 lines).
        """
        error_msg = (
            "GitHub CLI (gh) not found. Ensure gh is installed and in system PATH. Install: https://cli.github.com/"
        )
        logger.error(error_msg)
        self.result_signal.emit(
            GitHubResult(
                success=False,
                data=None,
                error=error_msg,
                user_message="GitHub CLI not found",
                operation=operation,
            )
        )

    def emit_general_error(self, e: Exception, operation: str) -> None:
        """
        Emit general exception error result.

        Args:
            e: Exception that occurred
            operation: Operation name for result tracking

        MA principle: Extracted from run_gh_command (11 lines).
        """
        error_msg = f"Unexpected error running GitHub CLI command: {e}"
        logger.exception("Unexpected GitHub CLI error")
        self.result_signal.emit(
            GitHubResult(
                success=False,
                data=None,
                error=str(e),
                user_message=error_msg,
                operation=operation,
            )
        )

    def parse_error(self, stderr: str, command: list[str]) -> str:
        """
        Parse GitHub CLI error messages and provide user-friendly explanations.

        MA principle: Reduced from depth=7 to depth=1 using error pattern mapping (86% reduction).

        Args:
            stderr: GitHub CLI command standard error output
            command: GitHub CLI command that was executed

        Returns:
            Human-readable error message for status bar display

        Examples:
            >>> factory.parse_error("not logged into any GitHub hosts", ["pr", "list"])
            "Not authenticated. Run 'gh auth login' in terminal."
        """
        stderr_lower = stderr.lower()

        # Error pattern mapping (keywords -> user message)
        error_patterns = [
            (["not logged into", "not authenticated"], "Not authenticated. Run 'gh auth login' in terminal."),
            (
                ["no default remote", "not a git repository"],
                "No GitHub remote found. Add remote with 'git remote add origin <url>'.",
            ),
            (["rate limit"], "GitHub API rate limit exceeded. Try again in 1 hour."),
            (["permission denied", "forbidden"], "Permission denied. Check repository access and token scopes."),
            (["not found", "repository"], "Repository not found. Check repository name and access."),
            (["network", "could not resolve host"], "Network error. Check internet connection."),
            (["timeout"], "Request timed out. Check network connection."),
        ]

        # Check each pattern (OR logic - any keyword matches)
        for keywords, message in error_patterns:
            if any(keyword in stderr_lower for keyword in keywords):
                return message

        # Default: return first 200 chars of error
        return f"GitHub CLI error: {stderr[:200]}"
