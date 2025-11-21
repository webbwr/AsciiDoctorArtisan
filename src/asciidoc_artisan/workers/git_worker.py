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
from typing import Any

from PySide6.QtCore import Signal, Slot

from asciidoc_artisan.core import GitResult, GitStatus
from asciidoc_artisan.workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)


class GitWorker(BaseWorker):
    """
    Background worker for Git command execution.

    Runs Git commands in a separate QThread to prevent UI blocking.
    Emits command_complete signal with GitResult when operation finishes.

    Signals:
        command_complete: Emitted with GitResult after command execution
        status_ready: Emitted with GitStatus for real-time status updates (v1.9.0+)
        detailed_status_ready: Emitted with detailed file-level status (v1.9.0+)
            Format: Dict with keys: branch (str), modified (List[Dict]), staged (List[Dict]), untracked (List[Dict])

    Example:
        ```python
        git_worker = GitWorker()
        git_thread = QThread()
        git_worker.moveToThread(git_thread)
        git_thread.start()

        git_worker.command_complete.connect(self._on_git_complete)
        git_worker.status_ready.connect(self._on_status_update)

        git_worker.run_git_command(
            ["git", "add", "document.adoc"],
            "/path/to/repo"
        )

        git_worker.get_repository_status("/path/to/repo")
        ```
    """

    command_complete = Signal(GitResult)
    status_ready = Signal(GitStatus)
    detailed_status_ready = Signal(dict)  # v1.9.0+

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
        """Determine timeout based on operation type (network vs local)."""
        network_ops = {"pull", "push", "fetch", "clone"}
        is_network_op = any(op in command for op in network_ops)
        return 60 if is_network_op else 30

    def _execute_git_subprocess(
        self, command: list[str], working_dir: str, timeout: int
    ) -> subprocess.CompletedProcess[str]:
        """Execute Git subprocess with security controls."""
        return subprocess.run(
            command,
            cwd=working_dir,
            capture_output=True,
            text=True,
            check=False,
            shell=False,  # Critical: prevents command injection
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

    def _create_success_result(self, stdout: str, stderr: str, exit_code: int) -> GitResult:
        """Create success result."""
        return GitResult(
            success=True,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            user_message="Git command successful.",
        )

    def _create_error_result(self, stdout: str, stderr: str, exit_code: int | None, command: list[str]) -> GitResult:
        """Create error result with analyzed message."""
        user_message = self._analyze_git_error(stderr, command)
        return GitResult(
            success=False,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            user_message=user_message,
        )

    def _emit_timeout_error(self, command: list[str], timeout: int) -> None:
        """Emit timeout error result."""
        timeout_msg = (
            f"Git operation timed out after {timeout}s. "
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

    def _emit_not_found_error(self) -> None:
        """Emit Git not found error result."""
        error_msg = "Git command not found. Ensure Git is installed and in system PATH."
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

    def _emit_general_error(self, e: Exception, stdout: str, stderr: str, exit_code: int | None) -> None:
        """Emit general exception error result."""
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

    @Slot(list, str)
    def run_git_command(self, command: list[str], working_dir: str) -> None:
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

        MA principle: Reduced from 121 lines to ~45 lines by extracting error
        handling and subprocess execution into focused helper methods.
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
            return "Git Authentication Failed. Check credentials (SSH key/token/helper)."
        elif "not a git repository" in stderr_lower:
            return "Directory is not a Git repository."
        elif "resolve host" in stderr_lower:
            return "Could not connect to Git host. Check internet and repository URL."
        elif "nothing to commit" in stderr_lower:
            return "Nothing to commit."
        else:
            return f"Git command failed: {stderr[:200]}"

    @Slot(str)
    def get_repository_status(self, working_dir: str) -> None:
        """
        Get Git repository status and emit status_ready signal.

        MA principle: Reduced from 79→29 lines by extracting 2 helpers (63% reduction).

        Retrieves current branch, modified/staged/untracked file counts,
        and ahead/behind commit counts relative to remote branch.

        This method runs in the worker thread and is non-blocking.

        Args:
            working_dir: Absolute path to Git repository root

        Emits:
            status_ready: GitStatus with repository status information

        Security:
            - Uses subprocess with shell=False to prevent command injection
            - 2 second timeout to avoid blocking
            - Graceful error handling (returns empty status on failure)

        Implementation:
            Uses `git status --porcelain=v2 --branch` for machine-readable output.
            Parses v2 format which includes:
            - Branch headers (# branch.oid, # branch.head, # branch.upstream, # branch.ab)
            - File status (1/2 prefix for tracked/untracked, XY status codes)
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
        """
        MA principle: Extracted helper (26 lines) - focused git status command execution.

        Execute git status command with security and timeout protections.

        Args:
            working_dir: Git repository root directory

        Returns:
            CompletedProcess if successful, None on error

        Security:
            - Uses subprocess with shell=False to prevent command injection
            - 2 second timeout to avoid blocking
        """
        try:
            # Run git status with porcelain v2 format (machine-readable)
            # Security: shell=False prevents command injection
            process = subprocess.run(
                ["git", "status", "--porcelain=v2", "--branch"],
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=False,
                shell=False,
                encoding="utf-8",
                errors="replace",
                timeout=2,  # Quick timeout for status checks
            )
            return process

        except subprocess.TimeoutExpired:
            logger.warning("Git status timed out after 2s")
        except FileNotFoundError:
            logger.warning("Git command not found")
        except Exception as e:
            logger.exception(f"Unexpected error executing git status: {e}")

        return None

    def _emit_status_or_default(self, process: subprocess.CompletedProcess[str] | None) -> None:
        """
        MA principle: Extracted helper (16 lines) - focused status emission.

        Parse process result and emit status_ready signal.

        Args:
            process: CompletedProcess from git status command, or None on error

        Emits:
            status_ready: GitStatus with parsed data, or default GitStatus on error
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
        """
        Parse branch name from git status v2 header.

        MA principle: Extracted from _parse_git_status_v2 (4 lines).

        Args:
            line: Branch head line (e.g., "# branch.head main")

        Returns:
            Branch name or "HEAD (detached)" for detached state
        """
        branch = line.split(" ", 2)[2]
        if branch == "(detached)":
            branch = "HEAD (detached)"
        return branch

    def _parse_ahead_behind(self, line: str) -> tuple[int, int]:
        """
        Parse ahead/behind counts from git status v2 header.

        MA principle: Extracted from _parse_git_status_v2 (8 lines).

        Args:
            line: Branch ahead/behind line (e.g., "# branch.ab +2 -1")

        Returns:
            Tuple of (ahead_count, behind_count)
        """
        parts = line.split()
        if len(parts) >= 4:
            try:
                ahead = int(parts[2].replace("+", ""))
                behind = int(parts[3].replace("-", ""))
                return ahead, behind
            except ValueError:
                logger.warning(f"Failed to parse branch.ab: {line}")
        return 0, 0

    def _parse_tracked_file_status(self, parts: list[str]) -> tuple[bool, bool, bool]:
        """
        Parse tracked file status codes.

        MA principle: Extracted from _parse_git_status_v2 (15 lines).

        Args:
            parts: Split status line parts

        Returns:
            Tuple of (has_conflict, is_staged, is_modified)
        """
        if len(parts) < 2:
            return False, False, False

        xy_status = parts[1]
        has_conflict = "U" in xy_status
        x_status = xy_status[0] if len(xy_status) > 0 else "."
        y_status = xy_status[1] if len(xy_status) > 1 else "."
        is_staged = x_status != "."
        is_modified = y_status != "."

        return has_conflict, is_staged, is_modified

    def _parse_status_line(self, line: str) -> dict[str, Any]:
        """
        Parse a single git status line and return updates to counters.

        MA principle: Extracted from _parse_git_status_v2 (30 lines) to reduce complexity.

        Args:
            line: Single line from git status --porcelain=v2 output

        Returns:
            Dictionary with keys: branch, ahead_behind, has_conflict, modified, staged, untracked
        """
        result: dict[str, Any] = {
            "branch": None,
            "ahead_behind": None,
            "has_conflict": False,
            "modified": 0,
            "staged": 0,
            "untracked": 0,
        }

        # Parse branch headers
        if line.startswith("# branch.head "):
            result["branch"] = self._parse_branch_head(line)
        elif line.startswith("# branch.ab "):
            result["ahead_behind"] = self._parse_ahead_behind(line)

        # Parse tracked file status
        elif line.startswith("1 ") or line.startswith("2 "):
            parts = line.split(maxsplit=8)
            conflict, staged, modified = self._parse_tracked_file_status(parts)
            if conflict:
                result["has_conflict"] = True
            if staged:
                result["staged"] = 1
            if modified:
                result["modified"] = 1

        # Unmerged entry (always a conflict)
        elif line.startswith("u "):
            result["has_conflict"] = True
            result["modified"] = 1
            result["staged"] = 1

        # Untracked file
        elif line.startswith("? "):
            result["untracked"] = 1

        return result

    def _parse_git_status_v2(self, stdout: str) -> GitStatus:
        """
        Parse git status --porcelain=v2 output into GitStatus model.

        MA principle: Reduced from 125→50 lines by extracting 4 helper methods.

        Porcelain v2 format documentation:
        https://git-scm.com/docs/git-status#_porcelain_format_version_2

        Format:
            # branch.oid <commit-hash>
            # branch.head <branch-name>
            # branch.upstream <upstream-branch>
            # branch.ab +<ahead> -<behind>
            1 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <path>   (tracked file)
            2 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <X><score> <path><sep><origPath>   (renamed)
            ? <path>   (untracked file)

        Status codes (XY):
            - First char (X): status in index (staged)
            - Second char (Y): status in working tree
            - '.' = unmodified, 'M' = modified, 'A' = added, 'D' = deleted
            - 'U' = unmerged (conflict)

        Args:
            stdout: Output from git status --porcelain=v2 --branch

        Returns:
            GitStatus with parsed repository information

        Example:
            >>> stdout = '''# branch.oid abc123
            ... # branch.head feature/new
            ... # branch.upstream origin/main
            ... # branch.ab +2 -1
            ... 1 .M N... 100644 100644 100644 abc123 def456 file1.txt
            ... 1 A. N... 000000 100644 100644 000000 abc123 file2.txt
            ... ? untracked.txt'''
            >>> status = worker._parse_git_status_v2(stdout)
            >>> status.branch
            'feature/new'
            >>> status.modified_count
            1
            >>> status.staged_count
            1
            >>> status.ahead_count
            2
        """
        # Initialize counters
        branch = "unknown"
        modified_count = 0
        staged_count = 0
        untracked_count = 0
        has_conflicts = False
        ahead_count = 0
        behind_count = 0

        # Parse each line
        for line in stdout.strip().split("\n"):
            if not line:
                continue

            # Parse line and update counters
            result = self._parse_status_line(line)
            if result["branch"]:
                branch = result["branch"]
            if result["ahead_behind"]:
                ahead_count, behind_count = result["ahead_behind"]
            if result["has_conflict"]:
                has_conflicts = True
            modified_count += result["modified"]
            staged_count += result["staged"]
            untracked_count += result["untracked"]

        # Calculate dirty status
        is_dirty = modified_count > 0 or staged_count > 0 or untracked_count > 0

        return GitStatus(
            branch=branch,
            modified_count=modified_count,
            staged_count=staged_count,
            untracked_count=untracked_count,
            has_conflicts=has_conflicts,
            ahead_count=ahead_count,
            behind_count=behind_count,
            is_dirty=is_dirty,
        )

    @Slot(str)
    def get_detailed_repository_status(self, working_dir: str) -> None:
        """
        Get detailed Git repository status with file-level information (v1.9.0+).

        Retrieves detailed status including:
        - Current branch name
        - Modified files with line change counts
        - Staged files with line change counts
        - Untracked files

        This method runs in the worker thread and is non-blocking.

        Args:
            working_dir: Absolute path to Git repository root

        Emits:
            detailed_status_ready: Dict with keys:
                - branch (str): Current branch name
                - modified (List[Dict]): Modified files [{path, status, lines_added, lines_deleted}]
                - staged (List[Dict]): Staged files (same format)
                - untracked (List[Dict]): Untracked files [{path}]

        Security:
            - Uses subprocess with shell=False to prevent command injection
            - 5 second timeout to avoid blocking
            - Graceful error handling
        """
        if self._check_cancellation():
            logger.info("Detailed Git status operation cancelled")
            self.reset_cancellation()
            return

        try:
            if not self._validate_working_directory(working_dir):
                logger.warning(f"Invalid Git working directory: {working_dir}")
                return

            logger.debug(f"Getting detailed Git status for {working_dir}")

            # Get basic status (branch + file lists)
            status_result = subprocess.run(
                ["git", "status", "--porcelain=v2", "--branch"],
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=False,
                shell=False,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )

            if status_result.returncode != 0:
                logger.warning(f"Git status failed (code {status_result.returncode})")
                return

            # Parse file lists from porcelain v2 output
            branch, modified_files, staged_files, untracked_files = self._parse_detailed_status_v2(status_result.stdout)

            # Get line counts for modified files (working tree changes)
            if modified_files:
                modified_files = self._add_line_counts(working_dir, modified_files, staged=False)

            # Get line counts for staged files (index changes)
            if staged_files:
                staged_files = self._add_line_counts(working_dir, staged_files, staged=True)

            # Emit detailed status
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

        except subprocess.TimeoutExpired:
            logger.warning("Detailed Git status timed out after 5s")
        except FileNotFoundError:
            logger.warning("Git command not found")
        except Exception as e:
            logger.exception(f"Unexpected error getting detailed Git status: {e}")

    def _parse_detailed_status_v2(
        self, stdout: str
    ) -> tuple[str, list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
        """
        Parse git status --porcelain=v2 output into file lists.

        Args:
            stdout: Output from git status --porcelain=v2 --branch

        Returns:
            Tuple of (branch, modified_files, staged_files, untracked_files)
            Each file list contains dicts with keys: path, status

        Example:
            >>> stdout = '''# branch.head main
            ... 1 .M N... 100644 100644 100644 abc123 def456 file1.txt
            ... 1 A. N... 000000 100644 100644 000000 abc123 file2.txt
            ... ? untracked.txt'''
            >>> branch, modified, staged, untracked = worker._parse_detailed_status_v2(stdout)
            >>> branch
            'main'
            >>> modified
            [{'path': 'file1.txt', 'status': 'M'}]
            >>> staged
            [{'path': 'file2.txt', 'status': 'A'}]
        """
        branch = "unknown"
        modified_files: list[dict[str, str]] = []
        staged_files: list[dict[str, str]] = []
        untracked_files: list[dict[str, str]] = []

        lines = stdout.strip().split("\n")

        for line in lines:
            if not line:
                continue

            # Parse branch header
            if line.startswith("# branch.head "):
                branch = line.split(" ", 2)[2]
                if branch == "(detached)":
                    branch = "HEAD (detached)"

            # Parse tracked files (format: 1/2 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <path>)
            elif line.startswith("1 ") or line.startswith("2 "):
                parts = line.split(maxsplit=8)
                if len(parts) >= 9:
                    xy_status = parts[1]
                    file_path = parts[8]

                    # X = index status (staged), Y = working tree status
                    x_status = xy_status[0] if len(xy_status) > 0 else "."
                    y_status = xy_status[1] if len(xy_status) > 1 else "."

                    # Add to staged files if X != '.'
                    if x_status != ".":
                        staged_files.append({"path": file_path, "status": x_status})

                    # Add to modified files if Y != '.'
                    if y_status != ".":
                        modified_files.append({"path": file_path, "status": y_status})

            # Parse untracked files (format: ? <path>)
            elif line.startswith("? "):
                file_path = line[2:]  # Skip "? " prefix
                untracked_files.append({"path": file_path})

        return branch, modified_files, staged_files, untracked_files

    def _add_line_counts(self, working_dir: str, files: list[dict[str, Any]], staged: bool) -> list[dict[str, Any]]:
        """
        Add line change counts to file list using git diff --numstat.

        MA principle: Reduced from 67→19 lines by extracting 3 helpers (72% reduction).

        Args:
            working_dir: Repository root directory
            files: List of file dicts (will be modified in place)
            staged: If True, get staged changes (--cached), else working tree changes

        Returns:
            Updated file list with lines_added and lines_deleted keys
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
        """
        MA principle: Extracted helper (23 lines) - focused git diff command execution.

        Execute git diff --numstat to get line change counts.

        Args:
            working_dir: Repository root directory
            staged: If True, get staged changes (--cached), else working tree changes

        Returns:
            Tuple of (CompletedProcess or None, timeout_occurred)
            - First element: CompletedProcess if successful, None on error
            - Second element: True if timeout occurred, False otherwise

        Security:
            - Uses subprocess with shell=False to prevent command injection
            - 3 second timeout to avoid blocking
        """
        try:
            cmd = ["git", "diff", "--numstat"]
            if staged:
                cmd.append("--cached")

            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=False,
                shell=False,
                encoding="utf-8",
                errors="replace",
                timeout=3,
            )
            return result, False

        except subprocess.TimeoutExpired:
            logger.warning("Git diff --numstat timed out after 3s")
            return None, True
        except Exception as e:
            logger.warning(f"Failed to get line counts: {e}")
            return None, False

    def _parse_numstat_output(self, stdout: str) -> dict[str, dict[str, int]]:
        """
        MA principle: Extracted helper (14 lines) - focused numstat parsing.

        Parse git diff --numstat output into line counts dictionary.

        Args:
            stdout: Output from git diff --numstat command

        Returns:
            Dictionary mapping file paths to {added, deleted} dicts

        Format:
            <added>\t<deleted>\t<path>
            Binary files show "-" for added/deleted
        """
        line_counts = {}
        for line in stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) >= 3:
                added = int(parts[0]) if parts[0] != "-" else 0
                deleted = int(parts[1]) if parts[1] != "-" else 0
                path = parts[2]
                line_counts[path] = {"added": added, "deleted": deleted}

        return line_counts

    def _update_files_with_line_counts(
        self, files: list[dict[str, Any]], line_counts: dict[str, dict[str, int]]
    ) -> None:
        """
        MA principle: Extracted helper (9 lines) - focused file dict updates.

        Update file dictionaries with line change counts.

        Args:
            files: List of file dicts (modified in place)
            line_counts: Dictionary mapping paths to {added, deleted} dicts
        """
        for file_dict in files:
            path = file_dict["path"]
            if path in line_counts:
                file_dict["lines_added"] = line_counts[path]["added"]
                file_dict["lines_deleted"] = line_counts[path]["deleted"]
            else:
                file_dict["lines_added"] = 0
                file_dict["lines_deleted"] = 0
