"""
Unit tests for GitWorker class.
"""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from adp_windows import GitResult, GitWorker


@pytest.mark.unit
class TestGitWorker:
    """Test GitWorker for Git operations."""

    def test_git_worker_initialization(self):
        """Test GitWorker can be instantiated."""
        worker = GitWorker()
        assert worker is not None

    @patch("adp_windows.subprocess.run")
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

    @patch("adp_windows.subprocess.run")
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

    @patch("adp_windows.subprocess.run")
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

    @patch("adp_windows.subprocess.run")
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
