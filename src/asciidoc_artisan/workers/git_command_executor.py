"""
Git Command Executor - Executes git subprocess commands with security controls.

Extracted from GitWorker to reduce class size (MA principle).
Handles subprocess execution with timeouts, security controls, and error handling.
"""

import logging
import subprocess

logger = logging.getLogger(__name__)


class GitCommandExecutor:
    """
    Executor for git subprocess commands.

    This class was extracted from GitWorker to reduce class size per MA principle.

    Handles:
    - Subprocess execution with shell=False security
    - Timeout management (network vs local operations)
    - Error handling and logging
    """

    def get_timeout_for_command(self, command: list[str]) -> int:
        """Determine timeout based on operation type (network vs local)."""
        network_ops = {"pull", "push", "fetch", "clone"}
        is_network_op = any(op in command for op in network_ops)
        return 60 if is_network_op else 30

    def execute_git_subprocess(
        self, command: list[str], working_dir: str, timeout: int
    ) -> subprocess.CompletedProcess[str]:
        """
        Execute Git subprocess with security controls.

        Args:
            command: Git command as list (e.g., ["git", "status"])
            working_dir: Working directory path
            timeout: Timeout in seconds

        Returns:
            CompletedProcess with stdout/stderr

        Security:
            - shell=False prevents command injection
            - Timeout prevents hanging
        """
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

    def execute_git_status_command(self, working_dir: str) -> subprocess.CompletedProcess[str] | None:
        """
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

    def execute_detailed_status_command(self, working_dir: str) -> subprocess.CompletedProcess[str] | None:
        """
        Execute git status command for detailed repository status.

        Args:
            working_dir: Working directory path (caller must validate)

        Returns:
            CompletedProcess if successful, None otherwise

        Note: Caller must validate working_dir before calling
        """
        try:
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
                return None

            return status_result

        except subprocess.TimeoutExpired:
            logger.warning("Git status timed out after 5s")
        except FileNotFoundError:
            logger.warning("Git command not found")
        except Exception as e:
            logger.exception(f"Unexpected error getting detailed status: {e}")

        return None

    def execute_git_diff_numstat(
        self, working_dir: str, staged: bool
    ) -> tuple[subprocess.CompletedProcess[str] | None, bool]:
        """
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
