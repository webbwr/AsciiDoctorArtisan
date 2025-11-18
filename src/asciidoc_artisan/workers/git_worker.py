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

        try:
            # Validate working directory
            if not self._validate_working_directory(working_dir):
                logger.warning(f"Invalid Git working directory: {working_dir}")
                return

            logger.debug(f"Getting Git status for {working_dir}")

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

            if process.returncode == 0:
                status = self._parse_git_status_v2(process.stdout)
                logger.debug(
                    f"Git status parsed: branch={status.branch}, "
                    f"modified={status.modified_count}, staged={status.staged_count}, "
                    f"ahead/behind={status.ahead_count}/{status.behind_count}"
                )
                self.status_ready.emit(status)
            else:
                logger.warning(f"Git status failed (code {process.returncode})")
                # Emit default status on error (not a git repo, etc.)
                self.status_ready.emit(GitStatus())

        except subprocess.TimeoutExpired:
            logger.warning("Git status timed out after 2s")
            # Emit default status on timeout
            self.status_ready.emit(GitStatus())
        except FileNotFoundError:
            logger.warning("Git command not found")
            # Emit default status when git not found
            self.status_ready.emit(GitStatus())
        except Exception as e:
            logger.exception(f"Unexpected error getting Git status: {e}")
            # Emit default status on error
            self.status_ready.emit(GitStatus())

    def _parse_git_status_v2(self, stdout: str) -> GitStatus:  # noqa: C901
        """
        Parse git status --porcelain=v2 output into GitStatus model.

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
        branch = "unknown"
        modified_count = 0
        staged_count = 0
        untracked_count = 0
        has_conflicts = False
        ahead_count = 0
        behind_count = 0

        lines = stdout.strip().split("\n")

        for line in lines:
            if not line:
                continue

            # Parse branch headers
            if line.startswith("# branch.head "):
                branch = line.split(" ", 2)[2]
                if branch == "(detached)":
                    branch = "HEAD (detached)"

            elif line.startswith("# branch.ab "):
                # Format: "# branch.ab +<ahead> -<behind>"
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        ahead_count = int(parts[2].replace("+", ""))
                        behind_count = int(parts[3].replace("-", ""))
                    except ValueError:
                        logger.warning(f"Failed to parse branch.ab: {line}")

            # Parse file status
            elif line.startswith("1 ") or line.startswith("2 "):
                # Tracked file: 1/2 <XY> <other fields>
                # Status codes are in field 2 (XY)
                parts = line.split(maxsplit=8)
                if len(parts) >= 2:
                    xy_status = parts[1]

                    # Check for conflicts (U in either position)
                    if "U" in xy_status:
                        has_conflicts = True

                    # X = index status (staged), Y = working tree status
                    x_status = xy_status[0] if len(xy_status) > 0 else "."
                    y_status = xy_status[1] if len(xy_status) > 1 else "."

                    # Count staged changes (X != '.')
                    if x_status != ".":
                        staged_count += 1

                    # Count working tree changes (Y != '.')
                    if y_status != ".":
                        modified_count += 1

            elif line.startswith("u "):
                # Unmerged entry (conflict): u <XY> <other fields>
                # Always indicates conflicts
                has_conflicts = True
                # Count as both modified and staged (unresolved conflict)
                modified_count += 1
                staged_count += 1

            elif line.startswith("? "):
                # Untracked file
                untracked_count += 1

        # Working tree is dirty if any changes exist
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

    def _add_line_counts(  # noqa: C901
        self, working_dir: str, files: list[dict[str, Any]], staged: bool
    ) -> list[dict[str, Any]]:
        """
        Add line change counts to file list using git diff --numstat.

        Args:
            working_dir: Repository root directory
            files: List of file dicts (will be modified in place)
            staged: If True, get staged changes (--cached), else working tree changes

        Returns:
            Updated file list with lines_added and lines_deleted keys
        """
        try:
            # Build git diff command
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

            if result.returncode == 0:
                # Parse numstat output (format: <added>\t<deleted>\t<path>)
                line_counts = {}
                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue

                    parts = line.split("\t")
                    if len(parts) >= 3:
                        added = int(parts[0]) if parts[0] != "-" else 0
                        deleted = int(parts[1]) if parts[1] != "-" else 0
                        path = parts[2]
                        line_counts[path] = {"added": added, "deleted": deleted}

                # Add line counts to file dicts
                for file_dict in files:
                    path = file_dict["path"]
                    if path in line_counts:
                        file_dict["lines_added"] = line_counts[path]["added"]
                        file_dict["lines_deleted"] = line_counts[path]["deleted"]
                    else:
                        file_dict["lines_added"] = 0
                        file_dict["lines_deleted"] = 0

        except subprocess.TimeoutExpired:
            logger.warning("Git diff --numstat timed out after 3s")
        except Exception as e:
            logger.warning(f"Failed to get line counts: {e}")

            # Set default values on error
            for file_dict in files:
                file_dict.setdefault("lines_added", "0")
                file_dict.setdefault("lines_deleted", "0")

        return files
