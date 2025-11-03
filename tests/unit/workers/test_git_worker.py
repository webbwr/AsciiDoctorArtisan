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

    def test_git_result_creation(self):
        """Test GitResult can be created with all fields."""
        result = GitResult(
            success=True,
            stdout="output",
            stderr="",
            exit_code=0,
            user_message="Success",
        )

        assert result.success is True
        assert result.stdout == "output"
        assert result.stderr == ""
        assert result.exit_code == 0
        assert result.user_message == "Success"

    def test_git_result_failure(self):
        """Test GitResult for failed operation."""
        result = GitResult(
            success=False,
            stdout="",
            stderr="error output",
            exit_code=1,
            user_message="Failed",
        )

        assert result.success is False
        assert result.exit_code == 1
        assert result.user_message == "Failed"


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
        output = (
            "# branch.oid abcd1234\n"
            "# branch.head main\n"
            "1 .D N... 100644 000000 000000 abc123 000000 deleted.txt\n"
        )

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
