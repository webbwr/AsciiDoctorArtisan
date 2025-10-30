"""
Git Worker - Background thread for Git operations.

This module provides the GitWorker class which executes Git commands
in a background QThread to prevent UI blocking during version control
operations.

Implements:
- FR-031 to FR-040: Git integration requirements
- NFR-005: Long-running operations in background threads
- NFR-008: Safe Git operations (no force flags)
- NFR-010: Parameterized subprocess calls (no shell injection)

Security:
- Never uses shell=True to prevent command injection
- All arguments passed as list to subprocess.run()
- No destructive force commands without user confirmation
"""

import logging
import subprocess
from typing import List

from PySide6.QtCore import Signal, Slot

from asciidoc_artisan.core import GitResult
from asciidoc_artisan.workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)


class GitWorker(BaseWorker):
    """
    Background worker for Git command execution.

    Runs Git commands in a separate QThread to prevent UI blocking.
    Emits command_complete signal with GitResult when operation finishes.

    Signals:
        command_complete: Emitted with GitResult after command execution

    Example:
        ```python
        git_worker = GitWorker()
        git_thread = QThread()
        git_worker.moveToThread(git_thread)
        git_thread.start()

        git_worker.command_complete.connect(self._on_git_complete)
        git_worker.run_git_command(
            ["git", "add", "document.adoc"],
            "/path/to/repo"
        )
        ```
    """

    command_complete = Signal(GitResult)

    @Slot(list, str)
    def run_git_command(self, command: List[str], working_dir: str) -> None:
        """
        Execute a Git command in the specified working directory.

        This method runs in the worker thread. Never blocks the UI.

        Args:
            command: Git command as list (e.g., ["git", "commit", "-m", "message"])
            working_dir: Absolute path to Git repository root

        Emits:
            command_complete: GitResult with success/failure and output

        Security:
            - Uses subprocess with shell=False to prevent command injection (NFR-010)
            - Validates working directory exists before execution
            - No destructive force flags without user confirmation (NFR-008)
        """
        # Check for cancellation
        if self._check_cancellation():
            logger.info("Git operation cancelled before execution")
            self.command_complete.emit(
                GitResult(
                    success=False,
                    stdout="",
                    stderr="Operation cancelled by user",
                    exit_code=-1,
                    user_message="Cancelled",
                )
            )
            self.reset_cancellation()
            return

        user_message = "Git command failed."
        stdout, stderr = "", ""
        exit_code = None

        try:
            # Validate working directory
            if not self._validate_working_directory(working_dir):
                user_message = f"Error: Git working directory not found: {working_dir}"
                self.command_complete.emit(
                    GitResult(
                        success=False,
                        stdout="",
                        stderr=user_message,
                        exit_code=None,
                        user_message=user_message,
                    )
                )
                return

            logger.info(f"Executing Git: {' '.join(command)} in {working_dir}")

            # Determine timeout based on operation type
            # Network operations (pull, push, fetch, clone) get 60s
            # Local operations (commit, add, status, diff, log) get 30s
            network_ops = {"pull", "push", "fetch", "clone"}
            is_network_op = any(op in command for op in network_ops)
            timeout_seconds = 60 if is_network_op else 30

            # SECURITY: Never use shell=True - always use list arguments to prevent command injection
            process = subprocess.run(
                command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=False,
                shell=False,  # Critical: prevents command injection
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,  # Security: Prevent indefinite hangs
            )

            exit_code = process.returncode
            stdout = process.stdout.strip() if process.stdout else ""
            stderr = process.stderr.strip() if process.stderr else ""

            if exit_code == 0:
                logger.info(f"Git command successful: {' '.join(command)}")
                result = GitResult(
                    success=True,
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                    user_message="Git command successful.",
                )
            else:
                user_message = self._analyze_git_error(stderr, command)
                logger.error(f"Git command failed (code {exit_code}): {user_message}")
                result = GitResult(
                    success=False,
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                    user_message=user_message,
                )

            self.command_complete.emit(result)

        except subprocess.TimeoutExpired as e:
            timeout_msg = (
                f"Git operation timed out after {e.timeout}s. "
                f"Command: {' '.join(command)}. "
                "Check network connection or try again."
            )
            logger.error(timeout_msg)
            self.command_complete.emit(
                GitResult(
                    success=False,
                    stdout="",
                    stderr=timeout_msg,
                    exit_code=None,
                    user_message="Git operation timed out",
                )
            )
        except FileNotFoundError:
            error_msg = (
                "Git command not found. Ensure Git is installed and in system PATH."
            )
            logger.error(error_msg)
            self.command_complete.emit(
                GitResult(
                    success=False,
                    stdout="",
                    stderr=error_msg,
                    exit_code=None,
                    user_message=error_msg,
                )
            )
        except Exception as e:
            error_msg = f"Unexpected error running Git command: {e}"
            logger.exception("Unexpected Git error")
            self.command_complete.emit(
                GitResult(
                    success=False,
                    stdout=stdout,
                    stderr=stderr or str(e),
                    exit_code=exit_code,
                    user_message=error_msg,
                )
            )

    def _analyze_git_error(self, stderr: str, command: List[str]) -> str:
        """
        Analyze Git error messages and provide user-friendly explanations.

        Args:
            stderr: Git command standard error output
            command: Git command that was executed

        Returns:
            Human-readable error message for status bar display

        Examples:
            >>> worker._analyze_git_error("authentication failed", ["git", "push"])
            "Git Authentication Failed. Check credentials (SSH key/token/helper)."
        """
        stderr_lower = stderr.lower()

        if "authentication failed" in stderr_lower:
            return (
                "Git Authentication Failed. Check credentials (SSH key/token/helper)."
            )
        elif "not a git repository" in stderr_lower:
            return "Directory is not a Git repository."
        elif "resolve host" in stderr_lower:
            return "Could not connect to Git host. Check internet and repository URL."
        elif "nothing to commit" in stderr_lower:
            return "Nothing to commit."
        else:
            return f"Git command failed: {stderr[:200]}"
