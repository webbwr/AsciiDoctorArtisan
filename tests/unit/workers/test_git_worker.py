"""
Unit tests for GitWorker class.
"""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.core import GitResult
from asciidoc_artisan.workers import GitWorker


@pytest.mark.unit
class TestGitWorker:
    """Test GitWorker for Git operations."""

    def test_git_worker_initialization(self):
        """Test GitWorker can be instantiated."""
        worker = GitWorker()
        assert worker is not None

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_successful_git_command(self, mock_run):
        """Test successful Git command execution."""
        # Setup mock
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success output",
            stderr="",
        )

        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.run_git_command(["git", "status"], str(tmpdir))

        # Verify
        assert result is not None
        assert result.success is True
        assert result.stdout == "Success output"
        assert result.exit_code == 0

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_failed_git_command(self, mock_run):
        """Test failed Git command execution."""
        # Setup mock
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="fatal: not a git repository",
        )

        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.run_git_command(["git", "status"], str(tmpdir))

        # Verify
        assert result is not None
        assert result.success is False
        assert "not a git repository" in result.stderr

    def test_git_command_nonexistent_directory(self):
        """Test Git command with nonexistent working directory."""
        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        # Execute with non-existent path
        worker.run_git_command(["git", "status"], "/nonexistent/path/12345")

        # Verify
        assert result is not None
        assert result.success is False
        assert "not found" in result.user_message

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_git_error_analysis(self, mock_run):
        """Test Git error message analysis."""
        worker = GitWorker()

        # Test various error scenarios
        test_cases = [
            ("fatal: not a git repository", "not a Git repository"),
            ("error: failed to push", "push"),
            ("fatal: Authentication failed", "Authentication"),
        ]

        for stderr, expected_keyword in test_cases:
            error_msg = worker._analyze_git_error(stderr, ["git", "test"])
            assert expected_keyword.lower() in error_msg.lower()

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_git_command_timeout(self, mock_run):
        """Test Git command doesn't hang indefinitely."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("git", 30)

        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        with tempfile.TemporaryDirectory() as tmpdir:
            worker.run_git_command(["git", "status"], str(tmpdir))

        # Should handle timeout gracefully
        assert result is not None
        assert result.success is False


@pytest.mark.unit
class TestGitResult:
    """Test GitResult named tuple."""

    @pytest.mark.parametrize(
        "success,stdout,stderr,exit_code,user_message",
        [
            # Successful operation
            (True, "output", "", 0, "Success"),
            # Failed operation
            (False, "", "error output", 1, "Failed"),
            # Successful with both stdout and stderr
            (True, "output", "warning", 0, "Success with warnings"),
            # Failed with exit code 128 (git-specific error)
            (False, "", "fatal: not a git repository", 128, "Not a repository"),
        ],
        ids=[
            "success",
            "failure",
            "success_with_warnings",
            "fatal_error",
        ],
    )
    def test_git_result_variations(
        self, success, stdout, stderr, exit_code, user_message
    ):
        """Test GitResult with various success/failure combinations."""
        result = GitResult(
            success=success,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            user_message=user_message,
        )

        assert result.success is success
        assert result.stdout == stdout
        assert result.stderr == stderr
        assert result.exit_code == exit_code
        assert result.user_message == user_message


@pytest.mark.unit
class TestGitWorkerStatus:
    """Test GitWorker status functionality (v1.9.0+)."""

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_get_repository_status_clean(self, mock_run):
        """Test Git status parsing for clean repository."""
        # Porcelain v2 format for clean repository on main branch
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="# branch.oid abcd1234\n# branch.head main\n# branch.upstream origin/main\n# branch.ab +0 -0\n",
            stderr="",
        )

        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_repository_status(str(tmpdir))

        # Verify
        assert status is not None
        assert status.branch == "main"
        assert status.modified_count == 0
        assert status.staged_count == 0
        assert status.untracked_count == 0
        assert status.has_conflicts is False
        assert status.ahead_count == 0
        assert status.behind_count == 0
        assert status.is_dirty is False

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_get_repository_status_dirty(self, mock_run):
        """Test Git status parsing for dirty repository."""
        # Porcelain v2 format with modifications
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "# branch.oid abcd1234\n"
                "# branch.head feature-branch\n"
                "# branch.upstream origin/feature-branch\n"
                "# branch.ab +2 -1\n"
                "1 .M N... 100644 100644 100644 abc123 def456 file1.txt\n"
                "1 M. N... 100644 100644 100644 abc123 def456 file2.txt\n"
                "? file3.txt\n"
            ),
            stderr="",
        )

        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_repository_status(str(tmpdir))

        # Verify
        assert status is not None
        assert status.branch == "feature-branch"
        assert status.modified_count == 1  # .M (unstaged)
        assert status.staged_count == 1  # M. (staged)
        assert status.untracked_count == 1  # ?
        assert status.has_conflicts is False
        assert status.ahead_count == 2  # +2
        assert status.behind_count == 1  # -1
        assert status.is_dirty is True

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_get_repository_status_conflicts(self, mock_run):
        """Test Git status parsing for repository with conflicts."""
        # Porcelain v2 format with merge conflicts
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "# branch.oid abcd1234\n"
                "# branch.head main\n"
                "u UU N... 100644 100644 100644 100644 abc123 def456 ghi789 conflict.txt\n"
            ),
            stderr="",
        )

        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_repository_status(str(tmpdir))

        # Verify
        assert status is not None
        assert status.has_conflicts is True
        assert status.is_dirty is True

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_get_detailed_repository_status(self, mock_run):
        """Test detailed Git status parsing."""

        def mock_git_commands(args, **kwargs):
            """Mock multiple git commands."""
            if "status" in args:
                # git status --porcelain=v2 --branch
                return MagicMock(
                    returncode=0,
                    stdout=(
                        "# branch.oid abcd1234\n"
                        "# branch.head main\n"
                        "1 .M N... 100644 100644 100644 abc123 def456 file1.txt\n"
                        "1 M. N... 100644 100644 100644 abc123 def456 file2.txt\n"
                        "? file3.txt\n"
                    ),
                    stderr="",
                )
            elif "diff" in args:
                # git diff --numstat
                if "--cached" in args:  # Check for --cached (staged changes)
                    return MagicMock(
                        returncode=0, stdout="10\t5\tfile2.txt\n", stderr=""
                    )
                else:
                    return MagicMock(
                        returncode=0, stdout="8\t3\tfile1.txt\n", stderr=""
                    )
            return MagicMock(returncode=1, stdout="", stderr="Unknown command")

        mock_run.side_effect = mock_git_commands

        worker = GitWorker()
        status = None

        def capture_status(detailed_status):
            nonlocal status
            status = detailed_status

        worker.detailed_status_ready.connect(capture_status)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_detailed_repository_status(str(tmpdir))

        # Verify
        assert status is not None
        assert status["branch"] == "main"
        assert len(status["modified"]) == 1
        assert len(status["staged"]) == 1
        assert len(status["untracked"]) == 1

        # Check modified file details
        modified_file = status["modified"][0]
        assert modified_file["path"] == "file1.txt"
        assert modified_file["lines_added"] == 8
        assert modified_file["lines_deleted"] == 3

        # Check staged file details
        staged_file = status["staged"][0]
        assert staged_file["path"] == "file2.txt"
        assert staged_file["lines_added"] == 10
        assert staged_file["lines_deleted"] == 5

        # Check untracked file
        untracked_file = status["untracked"][0]
        assert untracked_file["path"] == "file3.txt"
        # Untracked files don't have line count keys

    def test_parse_git_status_v2_detached_head(self):
        """Test parsing detached HEAD state."""
        worker = GitWorker()
        output = "# branch.oid abcd1234\n# branch.head (detached)\n"

        status = worker._parse_git_status_v2(output)

        assert status.branch == "HEAD (detached)"
        assert status.is_dirty is False

    def test_parse_git_status_v2_renamed_file(self):
        """Test parsing renamed files."""
        worker = GitWorker()
        output = (
            "# branch.oid abcd1234\n"
            "# branch.head main\n"
            "2 R. N... 100644 100644 100644 abc123 def456 R100 old.txt\tnew.txt\n"
        )

        status = worker._parse_git_status_v2(output)

        assert status.staged_count == 1  # Renamed file is staged
        assert status.is_dirty is True

    def test_parse_git_status_v2_deleted_file(self):
        """Test parsing deleted files."""
        worker = GitWorker()
        output = "# branch.oid abcd1234\n# branch.head main\n1 .D N... 100644 000000 000000 abc123 000000 deleted.txt\n"

        status = worker._parse_git_status_v2(output)

        assert status.modified_count == 1  # .D = deleted (unstaged)
        assert status.is_dirty is True

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_get_repository_status_error(self, mock_run):
        """Test Git status with command error."""
        mock_run.return_value = MagicMock(
            returncode=128, stdout="", stderr="fatal: not a git repository"
        )

        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_repository_status(str(tmpdir))

        # Should emit default status on error
        assert status is not None
        assert status.branch == ""
        assert status.is_dirty is False


@pytest.mark.unit
class TestGitWorkerCancellation:
    """Test Git Worker cancellation functionality."""

    def test_git_command_cancelled_before_execution(self):
        """Test Git command respects cancellation before execution."""
        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        # Cancel before execution
        worker.cancel()

        # Execute with cancellation flag set
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.run_git_command(["git", "status"], str(tmpdir))

        # Verify cancelled result
        assert result is not None
        assert result.success is False
        assert "cancelled" in result.stderr.lower()
        assert result.exit_code == -1

    def test_get_repository_status_cancelled(self):
        """Test get_repository_status respects cancellation."""
        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Cancel before execution
        worker.cancel()

        # Execute - should not emit status when cancelled
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_repository_status(str(tmpdir))

        # Status should be None (not emitted) or have default values
        assert status is None or status.branch == ""


@pytest.mark.unit
class TestGitWorkerOperationTimeout:
    """Test Git Worker timeout configuration for different operation types."""

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_network_operation_timeout_pull(self, mock_run):
        """Test pull command uses 60 second timeout (network operation)."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Already up to date.", stderr=""
        )

        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        # Execute pull command
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.run_git_command(["git", "pull"], str(tmpdir))

        # Verify subprocess.run was called with timeout=60
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 60

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_network_operation_timeout_push(self, mock_run):
        """Test push command uses 60 second timeout (network operation)."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Everything up-to-date", stderr=""
        )

        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        # Execute push command
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.run_git_command(["git", "push", "origin", "main"], str(tmpdir))

        # Verify subprocess.run was called with timeout=60
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 60

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_network_operation_timeout_fetch(self, mock_run):
        """Test fetch command uses 60 second timeout (network operation)."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        # Execute fetch command
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.run_git_command(["git", "fetch"], str(tmpdir))

        # Verify subprocess.run was called with timeout=60
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 60

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_local_operation_timeout_commit(self, mock_run):
        """Test commit command uses 30 second timeout (local operation)."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="[main abc1234] Test commit",
            stderr="",
        )

        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        # Execute commit command
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.run_git_command(["git", "commit", "-m", "Test"], str(tmpdir))

        # Verify subprocess.run was called with timeout=30
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 30

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_local_operation_timeout_status(self, mock_run):
        """Test status command uses 30 second timeout (local operation)."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        # Execute status command
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.run_git_command(["git", "status"], str(tmpdir))

        # Verify subprocess.run was called with timeout=30
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 30


@pytest.mark.unit
class TestGitWorkerStatusParsingEdgeCases:
    """Test Git Worker status parsing for edge cases and complex scenarios."""

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_parse_git_status_no_branch_info(self, mock_run):
        """Test status parsing when branch info is missing."""
        # Porcelain v2 format without branch info (shouldn't happen but handle gracefully)
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="1 .M N... 100644 100644 100644 abc123 def456 file.txt\n",
            stderr="",
        )

        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_repository_status(str(tmpdir))

        # Should handle missing branch gracefully
        assert status is not None
        assert status.branch == "unknown"  # Default when branch info missing
        assert status.is_dirty is True  # Still detect modified files

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_parse_git_status_untracked_files_only(self, mock_run):
        """Test status parsing with only untracked files."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "# branch.oid abcd1234\n# branch.head main\n? untracked1.txt\n? untracked2.txt\n"
            ),
            stderr="",
        )

        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_repository_status(str(tmpdir))

        # Verify
        assert status is not None
        assert status.branch == "main"
        assert status.untracked_count == 2
        assert status.is_dirty is True

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_parse_git_status_staged_files_only(self, mock_run):
        """Test status parsing with only staged files."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "# branch.oid abcd1234\n# branch.head main\n1 M. N... 100644 100644 100644 abc123 def456 staged.txt\n"
            ),
            stderr="",
        )

        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_repository_status(str(tmpdir))

        # Verify
        assert status is not None
        assert status.branch == "main"
        assert status.staged_count == 1
        assert status.modified_count == 0  # Only counting unstaged
        assert status.is_dirty is True


@pytest.mark.unit
class TestGitWorkerExceptionHandling:
    """Test GitWorker exception handling paths."""

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_git_command_file_not_found_error(self, mock_run):
        """Test FileNotFoundError when git command not found."""
        # Mock subprocess.run to raise FileNotFoundError
        mock_run.side_effect = FileNotFoundError("git command not found")

        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.run_git_command(["git", "status"], str(tmpdir))

        # Verify
        assert result is not None
        assert result.success is False
        assert "Git command not found" in result.user_message
        assert "Git command not found" in result.stderr
        assert result.exit_code is None

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_git_command_unexpected_exception(self, mock_run):
        """Test generic Exception handling in _run_git_command."""
        # Mock subprocess.run to raise unexpected exception
        mock_run.side_effect = RuntimeError("Unexpected error")

        worker = GitWorker()
        result = None

        def capture_result(git_result):
            nonlocal result
            result = git_result

        worker.command_complete.connect(capture_result)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.run_git_command(["git", "status"], str(tmpdir))

        # Verify
        assert result is not None
        assert result.success is False
        assert "Unexpected error" in result.user_message
        assert result.exit_code is None

    def test_get_repository_status_invalid_directory(self):
        """Test get_repository_status with invalid working directory."""
        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Execute with invalid path (should emit default status or nothing)
        worker.get_repository_status("/nonexistent/invalid/path/12345")

        # Verify - invalid directory returns early, no signal emitted
        # (behavior is to return without emitting)
        assert status is None

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_get_repository_status_timeout_expired(self, mock_run):
        """Test TimeoutExpired exception in get_repository_status."""
        import subprocess

        # Mock subprocess.run to raise TimeoutExpired
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["git", "status"], timeout=2
        )

        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_repository_status(str(tmpdir))

        # Verify - should emit default GitStatus on timeout
        assert status is not None
        assert status.branch == ""
        assert status.is_dirty is False

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_get_repository_status_file_not_found(self, mock_run):
        """Test FileNotFoundError in get_repository_status."""
        # Mock subprocess.run to raise FileNotFoundError
        mock_run.side_effect = FileNotFoundError("git not found")

        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_repository_status(str(tmpdir))

        # Verify - should emit default GitStatus when git not found
        assert status is not None
        assert status.branch == ""
        assert status.is_dirty is False

    @patch("asciidoc_artisan.workers.git_worker.subprocess.run")
    def test_get_repository_status_unexpected_exception(self, mock_run):
        """Test generic Exception handling in get_repository_status."""
        # Mock subprocess.run to raise unexpected exception
        mock_run.side_effect = RuntimeError("Unexpected error")

        worker = GitWorker()
        status = None

        def capture_status(git_status):
            nonlocal status
            status = git_status

        worker.status_ready.connect(capture_status)

        # Execute
        with tempfile.TemporaryDirectory() as tmpdir:
            worker.get_repository_status(str(tmpdir))

        # Verify - should emit default GitStatus on error
        assert status is not None
        assert status.branch == ""
        assert status.is_dirty is False
