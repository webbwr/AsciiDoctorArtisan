"""
GitHub CLI Worker - Background thread for GitHub operations.

This module provides the GitHubCLIWorker class which executes GitHub CLI (gh)
commands in a background QThread to prevent UI blocking during GitHub API
operations.

Implements:
- FR-TBD: GitHub CLI integration (planned for v1.6.0+)
- NFR-005: Long-running operations in background threads
- NFR-010: Parameterized subprocess calls (no shell injection)

Security:
- Never uses shell=True to prevent command injection
- All arguments passed as list to subprocess.run()
- 60-second timeout for all network operations
- JSON output parsing for structured data
"""

import json
import logging
import subprocess
from typing import Any

from PySide6.QtCore import Signal, Slot

from asciidoc_artisan.core.models import GitHubResult
from asciidoc_artisan.workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)


class GitHubCLIWorker(BaseWorker):
    """
    Background worker for GitHub CLI command execution.

    Runs GitHub CLI (gh) commands in a separate QThread to prevent UI blocking.
    Emits github_result_ready signal with GitHubResult when operation finishes.

    Signals:
        github_result_ready: Emitted with GitHubResult after command execution

    Example:
        ```python
        github_worker = GitHubCLIWorker()
        github_thread = QThread()
        github_worker.moveToThread(github_thread)
        github_thread.start()

        github_worker.github_result_ready.connect(self._on_github_complete)
        github_worker.create_pull_request(
            "Add new feature",
            "This PR adds...",
            "main",
            "feature-branch"
        )
        ```
    """

    github_result_ready = Signal(GitHubResult)

    @Slot(str, dict)
    def dispatch_github_operation(self, operation: str, kwargs: dict[str, Any]) -> None:
        """
        Dispatch GitHub operation based on operation type.

        This method is connected to the main window's request_github_command signal
        and routes to the appropriate worker method.

        Args:
            operation: Operation type (e.g., "create_pull_request", "list_pull_requests")
            kwargs: Keyword arguments for the operation
        """
        logger.info(f"Dispatching GitHub operation: {operation}")

        # Route to appropriate method based on operation type.
        if operation == "create_pull_request":
            self.create_pull_request(
                kwargs.get("title", ""),
                kwargs.get("body", ""),
                kwargs.get("base", "main"),
                kwargs.get("head", ""),
                kwargs.get("working_dir", ""),
            )
        elif operation == "list_pull_requests":
            self.list_pull_requests(kwargs.get("state"), kwargs.get("working_dir", ""))
        elif operation == "create_issue":
            self.create_issue(
                kwargs.get("title", ""),
                kwargs.get("body", ""),
                kwargs.get("working_dir", ""),
            )
        elif operation == "list_issues":
            self.list_issues(kwargs.get("state"), kwargs.get("working_dir", ""))
        elif operation == "get_repo_info":
            self.get_repo_info(kwargs.get("working_dir", ""))
        else:
            # Unknown operation - emit error result immediately.
            error_msg = f"Unknown GitHub operation: {operation}"
            logger.error(error_msg)
            result = GitHubResult(
                success=False,
                data=None,
                error=error_msg,
                user_message=error_msg,
                operation=operation,
            )
            self.github_result_ready.emit(result)

    @Slot(list, str, str)
    def run_gh_command(  # noqa: C901
        self,
        args: list[str],
        working_dir: str | None = None,
        operation: str | None = None,
    ) -> None:
        """
        Execute a GitHub CLI command.

        This method runs in the worker thread. Never blocks the UI.

        Args:
            args: GitHub CLI arguments (e.g., ["pr", "list", "--json", "number,title"])
            working_dir: Optional working directory (defaults to current directory)
            operation: Optional operation name for result tracking (defaults to args[0])

        Emits:
            github_result_ready: GitHubResult with success/failure and parsed JSON data

        Security:
            - Uses subprocess with shell=False to prevent command injection (NFR-010)
            - 60-second timeout for all network operations
            - Validates working directory exists before execution
        """
        # Check cancellation flag before starting network operation.
        if self._check_cancellation():
            logger.info("GitHub CLI operation cancelled before execution")
            self.github_result_ready.emit(
                GitHubResult(
                    success=False,
                    data=None,
                    error="Operation cancelled by user",
                    user_message="Cancelled",
                    operation=operation or "cancelled",
                )
            )
            self.reset_cancellation()
            return

        # Use provided operation name, or default to first command arg.
        if operation is None:
            operation = args[0] if args else "unknown"
        user_message = "GitHub CLI command failed."

        try:
            # Validate directory exists before running subprocess.
            if working_dir and not self._validate_working_directory(working_dir):
                user_message = f"Error: Working directory not found: {working_dir}"
                self.github_result_ready.emit(
                    GitHubResult(
                        success=False,
                        data=None,
                        error=user_message,
                        user_message=user_message,
                        operation=operation,
                    )
                )
                return

            # Prepend 'gh' to user's args to build full command.
            command = ["gh"] + args
            logger.info(f"Executing GitHub CLI: {' '.join(command)}")
            if working_dir:
                logger.info(f"Working directory: {working_dir}")

            # SECURITY: shell=False prevents command injection attacks.
            # timeout=60 prevents hung network requests from blocking forever.
            process = subprocess.run(
                command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=False,
                shell=False,  # Critical: prevents command injection
                encoding="utf-8",
                errors="replace",  # Replace invalid UTF-8 with placeholder.
                timeout=60,  # 60s is enough for most GitHub API calls.
            )

            exit_code = process.returncode
            stdout = process.stdout.strip() if process.stdout else ""
            stderr = process.stderr.strip() if process.stderr else ""

            if exit_code == 0:
                logger.info(f"GitHub CLI command successful: {' '.join(command)}")

                # Parse JSON if available, otherwise wrap plain text.
                data = None
                if stdout:
                    try:
                        # GitHub CLI returns JSON when --json flag is used.
                        data = json.loads(stdout)
                    except json.JSONDecodeError:
                        # Not JSON (e.g. plain text output from gh auth status).
                        logger.debug("GitHub CLI output is not JSON")
                        data = {"output": stdout}

                result = GitHubResult(
                    success=True,
                    data=data,
                    error="",
                    user_message="GitHub command successful.",
                    operation=operation,
                )
            else:
                # Parse error message to give user-friendly feedback.
                user_message = self._parse_gh_error(stderr, args)
                logger.error(
                    f"GitHub CLI command failed (code {exit_code}): {user_message}"
                )
                result = GitHubResult(
                    success=False,
                    data=None,
                    error=stderr,
                    user_message=user_message,
                    operation=operation,
                )

            self.github_result_ready.emit(result)

        except subprocess.TimeoutExpired as e:
            timeout_msg = (
                f"GitHub CLI operation timed out after {e.timeout}s. "
                f"Command: {' '.join(['gh'] + args)}. "
                "Check network connection or try again."
            )
            logger.error(timeout_msg)
            self.github_result_ready.emit(
                GitHubResult(
                    success=False,
                    data=None,
                    error=timeout_msg,
                    user_message="GitHub operation timed out",
                    operation=operation,
                )
            )
        except FileNotFoundError:
            error_msg = "GitHub CLI (gh) not found. Ensure gh is installed and in system PATH. Install: https://cli.github.com/"
            logger.error(error_msg)
            self.github_result_ready.emit(
                GitHubResult(
                    success=False,
                    data=None,
                    error=error_msg,
                    user_message="GitHub CLI not found",
                    operation=operation,
                )
            )
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse GitHub CLI JSON output: {e}"
            logger.error(error_msg)
            self.github_result_ready.emit(
                GitHubResult(
                    success=False,
                    data=None,
                    error=error_msg,
                    user_message="GitHub CLI returned invalid JSON",
                    operation=operation,
                )
            )
        except Exception as e:
            error_msg = f"Unexpected error running GitHub CLI command: {e}"
            logger.exception("Unexpected GitHub CLI error")
            self.github_result_ready.emit(
                GitHubResult(
                    success=False,
                    data=None,
                    error=str(e),
                    user_message=error_msg,
                    operation=operation,
                )
            )

    @Slot(str, str, str, str)
    def create_pull_request(
        self,
        title: str,
        body: str,
        base: str,
        head: str,
        working_dir: str | None = None,
    ) -> None:
        """
        Create a GitHub pull request.

        Args:
            title: PR title
            body: PR description/body
            base: Base branch (e.g., "main")
            head: Head branch (e.g., "feature-x")
            working_dir: Optional repository path

        Emits:
            github_result_ready: GitHubResult with PR number and URL in data field
        """
        # Build gh pr create command with JSON output
        args = [
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--base",
            base,
            "--head",
            head,
            "--json",
            "number,url",
        ]
        self.run_gh_command(args, working_dir, operation="pr_create")

    @Slot(str)
    def list_pull_requests(
        self, state: str | None = None, working_dir: str | None = None
    ) -> None:
        """
        List pull requests in the repository.

        Args:
            state: Filter by state: "open", "closed", "merged", or None for all
            working_dir: Optional repository path

        Emits:
            github_result_ready: GitHubResult with list of PRs in data field
        """
        args = [
            "pr",
            "list",
            "--json",
            "number,title,state,url,headRefName,author,createdAt",
        ]

        if state:
            args.extend(["--state", state])

        self.run_gh_command(args, working_dir, operation="pr_list")

    @Slot(str, str)
    def create_issue(
        self, title: str, body: str, working_dir: str | None = None
    ) -> None:
        """
        Create a GitHub issue.

        Args:
            title: Issue title
            body: Issue description/body
            working_dir: Optional repository path

        Emits:
            github_result_ready: GitHubResult with issue number and URL in data field
        """
        args = [
            "issue",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--json",
            "number,url",
        ]
        self.run_gh_command(args, working_dir, operation="issue_create")

    @Slot(str)
    def list_issues(
        self, state: str | None = None, working_dir: str | None = None
    ) -> None:
        """
        List issues in the repository.

        Args:
            state: Filter by state: "open", "closed", or None for all
            working_dir: Optional repository path

        Emits:
            github_result_ready: GitHubResult with list of issues in data field
        """
        args = [
            "issue",
            "list",
            "--json",
            "number,title,state,url,labels,author,createdAt",
        ]

        if state:
            args.extend(["--state", state])

        self.run_gh_command(args, working_dir, operation="issue_list")

    @Slot()
    def get_repo_info(self, working_dir: str | None = None) -> None:
        """
        Get repository information.

        Args:
            working_dir: Optional repository path

        Emits:
            github_result_ready: GitHubResult with repo info in data field
        """
        args = [
            "repo",
            "view",
            "--json",
            "name,nameWithOwner,description,stargazerCount,forkCount,defaultBranchRef,visibility,url",
        ]
        self.run_gh_command(args, working_dir, operation="repo_info")

    def _parse_gh_error(self, stderr: str, command: list[str]) -> str:
        """
        Parse GitHub CLI error messages and provide user-friendly explanations.

        Args:
            stderr: GitHub CLI command standard error output
            command: GitHub CLI command that was executed

        Returns:
            Human-readable error message for status bar display

        Examples:
            >>> worker._parse_gh_error("not logged into any GitHub hosts", ["pr", "list"])
            "Not authenticated. Run 'gh auth login' in terminal."
        """
        stderr_lower = stderr.lower()

        if "not logged into" in stderr_lower or "not authenticated" in stderr_lower:
            return "Not authenticated. Run 'gh auth login' in terminal."
        elif (
            "no default remote" in stderr_lower
            or "not a git repository" in stderr_lower
        ):
            return (
                "No GitHub remote found. Add remote with 'git remote add origin <url>'."
            )
        elif "rate limit" in stderr_lower:
            return "GitHub API rate limit exceeded. Try again in 1 hour."
        elif "permission denied" in stderr_lower or "forbidden" in stderr_lower:
            return "Permission denied. Check repository access and token scopes."
        elif "not found" in stderr_lower and "repository" in stderr_lower:
            return "Repository not found. Check repository name and access."
        elif "network" in stderr_lower or "could not resolve host" in stderr_lower:
            return "Network error. Check internet connection."
        elif "timeout" in stderr_lower:
            return "Request timed out. Check network connection."
        else:
            # Return first 200 chars of error
            return f"GitHub CLI error: {stderr[:200]}"
