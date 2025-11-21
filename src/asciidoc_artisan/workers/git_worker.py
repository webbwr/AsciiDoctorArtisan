"""
Git Worker - Background thread for Git operations.

Executes Git commands in QThread to prevent UI blocking. Delegates to:
- GitStatusParser: Parse git status output
- GitCommandExecutor: Execute subprocess commands
- GitErrorHandler: Error analysis and result creation

Security: shell=False, validated paths, no force flags (FR-031-040, NFR-005/008/010).
"""

import logging
import subprocess
from typing import Any

from PySide6.QtCore import Signal, Slot

from asciidoc_artisan.core import GitResult, GitStatus
from asciidoc_artisan.workers.base_worker import BaseWorker
from asciidoc_artisan.workers.git_command_executor import GitCommandExecutor
from asciidoc_artisan.workers.git_error_handler import GitErrorHandler
from asciidoc_artisan.workers.git_status_parser import GitStatusParser

logger = logging.getLogger(__name__)


class GitWorker(BaseWorker):
    """
    Background worker for Git command execution in QThread.

    Signals:
        command_complete: GitResult after command execution
        status_ready: GitStatus for real-time updates (v1.9.0+)
        detailed_status_ready: Dict with branch, modified/staged/untracked file lists (v1.9.0+)

    MA principle: Reduced from 904→333 lines via 3 extractions + docstring condensation (63.2% reduction).
    """

    command_complete = Signal(GitResult)
    status_ready = Signal(GitStatus)
    detailed_status_ready = Signal(dict)  # v1.9.0+

    def __init__(self) -> None:
        """Initialize GitWorker with parser, executor, and error handler instances."""
        super().__init__()
        self._parser = GitStatusParser()
        self._executor = GitCommandExecutor()
        self._error_handler = GitErrorHandler()

    def _check_and_handle_cancellation(self) -> bool:
        """Check for cancellation and emit result if cancelled. Returns True if cancelled."""
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
            return True
        return False

    def _get_timeout_for_command(self, command: list[str]) -> int:
        """Determine timeout (delegates to git_command_executor)."""
        return self._executor.get_timeout_for_command(command)

    def _execute_git_subprocess(
        self, command: list[str], working_dir: str, timeout: int
    ) -> subprocess.CompletedProcess[str]:
        """Execute Git subprocess (delegates to git_command_executor)."""
        return self._executor.execute_git_subprocess(command, working_dir, timeout)

    def _create_success_result(self, stdout: str, stderr: str, exit_code: int) -> GitResult:
        """Create success result (delegates to git_error_handler)."""
        return self._error_handler.create_success_result(stdout, stderr, exit_code)

    def _create_error_result(self, stdout: str, stderr: str, exit_code: int | None, command: list[str]) -> GitResult:
        """Create error result (delegates to git_error_handler)."""
        return self._error_handler.create_error_result(stdout, stderr, exit_code, command)

    def _emit_timeout_error(self, command: list[str], timeout: int) -> None:
        """Emit timeout error result (delegates to git_error_handler)."""
        result = self._error_handler.create_timeout_error(command, timeout)
        self.command_complete.emit(result)

    def _emit_not_found_error(self) -> None:
        """Emit Git not found error result (delegates to git_error_handler)."""
        result = self._error_handler.create_not_found_error()
        self.command_complete.emit(result)

    def _emit_general_error(self, e: Exception, stdout: str, stderr: str, exit_code: int | None) -> None:
        """Emit general exception error result (delegates to git_error_handler)."""
        result = self._error_handler.create_general_error(e, stdout, stderr, exit_code)
        self.command_complete.emit(result)

    @Slot(list, str)
    def run_git_command(self, command: list[str], working_dir: str) -> None:
        """
        Execute Git command in worker thread (non-blocking).

        Emits command_complete with GitResult. Security: shell=False, validated paths (NFR-010).
        """
        # Check for cancellation
        if self._check_and_handle_cancellation():
            return

        stdout, stderr, exit_code = "", "", None

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

            # Execute with appropriate timeout
            timeout = self._get_timeout_for_command(command)
            process = self._execute_git_subprocess(command, working_dir, timeout)

            exit_code = process.returncode
            stdout = process.stdout.strip() if process.stdout else ""
            stderr = process.stderr.strip() if process.stderr else ""

            # Create and emit result
            if exit_code == 0:
                logger.info(f"Git command successful: {' '.join(command)}")
                result = self._create_success_result(stdout, stderr, exit_code)
            else:
                logger.error(f"Git command failed (code {exit_code})")
                result = self._create_error_result(stdout, stderr, exit_code, command)

            self.command_complete.emit(result)

        except subprocess.TimeoutExpired as e:
            self._emit_timeout_error(command, int(e.timeout))
        except FileNotFoundError:
            self._emit_not_found_error()
        except Exception as e:
            self._emit_general_error(e, stdout, stderr, exit_code)

    def _analyze_git_error(self, stderr: str, command: list[str]) -> str:
        """Analyze Git error messages (delegates to git_error_handler)."""
        return self._error_handler.analyze_git_error(stderr, command)

    @Slot(str)
    def get_repository_status(self, working_dir: str) -> None:
        """
        Get repository status (branch, file counts, ahead/behind) and emit status_ready.

        Uses git status --porcelain=v2. Non-blocking, 2s timeout, shell=False.
        """
        # Check for cancellation
        if self._check_cancellation():
            logger.info("Git status operation cancelled")
            self.reset_cancellation()
            return

        # Validate working directory
        if not self._validate_working_directory(working_dir):
            logger.warning(f"Invalid Git working directory: {working_dir}")
            return

        logger.debug(f"Getting Git status for {working_dir}")

        # Execute git status command
        process = self._execute_git_status_command(working_dir)
        self._emit_status_or_default(process)

    def _execute_git_status_command(self, working_dir: str) -> subprocess.CompletedProcess[str] | None:
        """Execute git status command (delegates to git_command_executor)."""
        return self._executor.execute_git_status_command(working_dir)

    def _emit_status_or_default(self, process: subprocess.CompletedProcess[str] | None) -> None:
        """
        Parse process result and emit status_ready signal (or default on error).

        MA principle: Extracted helper (16 lines) - focused status emission.
        """
        if process and process.returncode == 0:
            status = self._parse_git_status_v2(process.stdout)
            logger.debug(
                f"Git status parsed: branch={status.branch}, "
                f"modified={status.modified_count}, staged={status.staged_count}, "
                f"ahead/behind={status.ahead_count}/{status.behind_count}"
            )
            self.status_ready.emit(status)
        else:
            if process:
                logger.warning(f"Git status failed (code {process.returncode})")
            # Emit default status on error (not a git repo, timeout, etc.)
            self.status_ready.emit(GitStatus())

    def _parse_branch_head(self, line: str) -> str:
        """Parse branch name (delegates to git_status_parser)."""
        return self._parser.parse_branch_head(line)

    def _parse_ahead_behind(self, line: str) -> tuple[int, int]:
        """Parse ahead/behind counts (delegates to git_status_parser)."""
        return self._parser.parse_ahead_behind(line)

    def _parse_tracked_file_status(self, parts: list[str]) -> tuple[bool, bool, bool]:
        """Parse tracked file status (delegates to git_status_parser)."""
        return self._parser.parse_tracked_file_status(parts)

    def _parse_status_line(self, line: str) -> dict[str, Any]:
        """Parse single status line (delegates to git_status_parser)."""
        return self._parser.parse_status_line(line)

    def _parse_git_status_v2(self, stdout: str) -> GitStatus:
        """Parse git status v2 output (delegates to git_status_parser)."""
        return self._parser.parse_git_status_v2(stdout)

    @Slot(str)
    def get_detailed_repository_status(self, working_dir: str) -> None:
        """
        Get detailed status (branch, file lists with line counts) and emit detailed_status_ready.

        Emits Dict with branch/modified/staged/untracked. Non-blocking, 5s timeout, shell=False.
        """
        if self._check_cancellation():
            logger.info("Detailed Git status operation cancelled")
            self.reset_cancellation()
            return

        try:
            # Validate and execute git status
            status_result = self._execute_detailed_status_command(working_dir)
            if not status_result:
                return

            # Parse and enrich file lists
            branch, modified_files, staged_files, untracked_files = self._parse_detailed_status_v2(status_result.stdout)

            if modified_files:
                modified_files = self._add_line_counts(working_dir, modified_files, staged=False)
            if staged_files:
                staged_files = self._add_line_counts(working_dir, staged_files, staged=True)

            # Emit detailed status
            self._emit_detailed_status(branch, modified_files, staged_files, untracked_files)

        except subprocess.TimeoutExpired:
            logger.warning("Detailed Git status timed out after 5s")
        except FileNotFoundError:
            logger.warning("Git command not found")
        except Exception as e:
            logger.exception(f"Unexpected error getting detailed Git status: {e}")

    def _execute_detailed_status_command(self, working_dir: str) -> subprocess.CompletedProcess[str] | None:
        """Execute detailed status command (delegates to git_command_executor)."""
        if not self._validate_working_directory(working_dir):
            logger.warning(f"Invalid Git working directory: {working_dir}")
            return None
        return self._executor.execute_detailed_status_command(working_dir)

    def _emit_detailed_status(
        self,
        branch: str,
        modified_files: list[dict[str, Any]],
        staged_files: list[dict[str, Any]],
        untracked_files: list[dict[str, str]],
    ) -> None:
        """
        Emit detailed status signal with file information.

        MA principle: Extracted helper (16 lines) - focused status emission.
        """
        detailed_status = {
            "branch": branch,
            "modified": modified_files,
            "staged": staged_files,
            "untracked": untracked_files,
        }

        self.detailed_status_ready.emit(detailed_status)
        logger.debug(
            f"Detailed Git status ready: {len(modified_files)} modified, "
            f"{len(staged_files)} staged, {len(untracked_files)} untracked"
        )

    def _parse_detailed_status_v2(
        self, stdout: str
    ) -> tuple[str, list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
        """Parse detailed status v2 output (delegates to git_status_parser)."""
        return self._parser.parse_detailed_status_v2(stdout)

    def _add_line_counts(self, working_dir: str, files: list[dict[str, Any]], staged: bool) -> list[dict[str, Any]]:
        """
        Add line change counts to file list using git diff --numstat.

        MA principle: Reduced from 67→19 lines by extracting 3 helpers (72% reduction).
        """
        result, timeout = self._execute_git_diff_numstat(working_dir, staged)
        if result and result.returncode == 0:
            line_counts = self._parse_numstat_output(result.stdout)
            self._update_files_with_line_counts(files, line_counts)
        elif not timeout:
            # Set default values on generic error (not timeout)
            for file_dict in files:
                file_dict.setdefault("lines_added", "0")
                file_dict.setdefault("lines_deleted", "0")

        return files

    def _execute_git_diff_numstat(
        self, working_dir: str, staged: bool
    ) -> tuple[subprocess.CompletedProcess[str] | None, bool]:
        """Execute git diff --numstat (delegates to git_command_executor)."""
        return self._executor.execute_git_diff_numstat(working_dir, staged)

    def _parse_numstat_output(self, stdout: str) -> dict[str, dict[str, int]]:
        """Parse numstat output (delegates to git_status_parser)."""
        return self._parser.parse_numstat_output(stdout)

    def _update_files_with_line_counts(
        self, files: list[dict[str, Any]], line_counts: dict[str, dict[str, int]]
    ) -> None:
        """Update files with line counts (delegates to git_status_parser)."""
        self._parser.update_files_with_line_counts(files, line_counts)
