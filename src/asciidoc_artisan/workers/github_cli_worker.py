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
from asciidoc_artisan.workers.github_command_builder import GitHubCommandBuilder
from asciidoc_artisan.workers.github_result_factory import GitHubResultFactory

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

    @property
    def _result_factory(self) -> GitHubResultFactory:
        """
        Lazy-initialized result factory for GitHub operations.

        MA principle: Delegates result/error creation to GitHubResultFactory (extracted class).
        """
        if not hasattr(self, "_factory_instance"):
            self._factory_instance = GitHubResultFactory(self.github_result_ready)
        return self._factory_instance

    @property
    def _command_builder(self) -> GitHubCommandBuilder:
        """
        Lazy-initialized command builder for GitHub operations.

        MA principle: Delegates command construction to GitHubCommandBuilder (extracted class).
        """
        if not hasattr(self, "_builder_instance"):
            self._builder_instance = GitHubCommandBuilder(self)
        return self._builder_instance

    @Slot(str, dict)
    def dispatch_github_operation(self, operation: str, kwargs: dict[str, Any]) -> None:
        """
        Dispatch GitHub operation based on operation type.

        This method is connected to the main window's request_github_command signal
        and routes to the appropriate worker method.

        Args:
            operation: Operation type (e.g., "create_pull_request", "list_pull_requests")
            kwargs: Keyword arguments for the operation

        MA principle: Delegates command building to GitHubCommandBuilder (extracted class).
        """
        logger.info(f"Dispatching GitHub operation: {operation}")

        # Route to appropriate method based on operation type.
        if operation == "create_pull_request":
            self._command_builder.create_pull_request(
                kwargs.get("title", ""),
                kwargs.get("body", ""),
                kwargs.get("base", "main"),
                kwargs.get("head", ""),
                kwargs.get("working_dir", ""),
            )
        elif operation == "list_pull_requests":
            self._command_builder.list_pull_requests(kwargs.get("state"), kwargs.get("working_dir", ""))
        elif operation == "create_issue":
            self._command_builder.create_issue(
                kwargs.get("title", ""),
                kwargs.get("body", ""),
                kwargs.get("working_dir", ""),
            )
        elif operation == "list_issues":
            self._command_builder.list_issues(kwargs.get("state"), kwargs.get("working_dir", ""))
        elif operation == "get_repo_info":
            self._command_builder.get_repo_info(kwargs.get("working_dir", ""))
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

    def _check_and_handle_gh_cancellation(self, operation: str | None) -> bool:
        """
        Check for cancellation and emit result if cancelled.

        Args:
            operation: Operation name for result tracking

        Returns:
            True if cancelled, False otherwise

        MA principle: Extracted from run_gh_command (8 lines).
        """
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
            return True
        return False

    def _execute_gh_subprocess(self, command: list[str], working_dir: str | None) -> subprocess.CompletedProcess[str]:
        """
        Execute GitHub CLI subprocess with security controls.

        Args:
            command: Full gh command (e.g., ["gh", "pr", "list"])
            working_dir: Optional working directory

        Returns:
            CompletedProcess with stdout/stderr/returncode

        MA principle: Extracted from run_gh_command (18 lines).
        Security: shell=False prevents command injection (NFR-010).
        """
        logger.info(f"Executing GitHub CLI: {' '.join(command)}")
        if working_dir:
            logger.info(f"Working directory: {working_dir}")

        return subprocess.run(
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

    @Slot(list, str, str)
    def run_gh_command(
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

        MA principle: Reduced from 160→50 lines by extracting 8 helper methods.
        """
        # Check cancellation before starting network operation.
        if self._check_and_handle_gh_cancellation(operation):
            return

        # Use provided operation name, or default to first command arg.
        if operation is None:
            operation = args[0] if args else "unknown"

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

            # Execute GitHub CLI command with security controls.
            command = ["gh"] + args
            process = self._execute_gh_subprocess(command, working_dir)

            exit_code = process.returncode
            stdout = process.stdout.strip() if process.stdout else ""
            stderr = process.stderr.strip() if process.stderr else ""

            # Create and emit result based on exit code.
            if exit_code == 0:
                data = self._result_factory.parse_json_output(stdout)
                result = self._result_factory.create_success_result(data, operation)
            else:
                result = self._result_factory.create_error_result(stderr, args, operation)

            self.github_result_ready.emit(result)

        except subprocess.TimeoutExpired as e:
            self._result_factory.emit_timeout_error(args, e.timeout, operation)
        except FileNotFoundError:
            self._result_factory.emit_not_found_error(operation)
        except Exception as e:
            self._result_factory.emit_general_error(e, operation)

    # Wrapper methods for backward compatibility (delegate to command builder)

    @Slot(str, str, str, str)
    def create_pull_request(self, title: str, body: str, base: str, head: str, working_dir: str | None = None) -> None:
        """Create a GitHub pull request (delegates to command builder)."""
        self._command_builder.create_pull_request(title, body, base, head, working_dir)

    @Slot(str)
    def list_pull_requests(self, state: str | None = None, working_dir: str | None = None) -> None:
        """List pull requests (delegates to command builder)."""
        self._command_builder.list_pull_requests(state, working_dir)

    @Slot(str, str)
    def create_issue(self, title: str, body: str, working_dir: str | None = None) -> None:
        """Create a GitHub issue (delegates to command builder)."""
        self._command_builder.create_issue(title, body, working_dir)

    @Slot(str)
    def list_issues(self, state: str | None = None, working_dir: str | None = None) -> None:
        """List issues (delegates to command builder)."""
        self._command_builder.list_issues(state, working_dir)

    @Slot()
    def get_repo_info(self, working_dir: str | None = None) -> None:
        """Get repository information (delegates to command builder)."""
        self._command_builder.get_repo_info(working_dir)
