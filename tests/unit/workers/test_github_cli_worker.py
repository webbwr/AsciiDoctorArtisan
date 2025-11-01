"""
Unit tests for GitHubCLIWorker class.

Tests GitHub CLI integration for pull requests, issues, and repository operations.
All tests mock subprocess calls to avoid actual gh CLI operations.
"""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import QThread

from asciidoc_artisan.core import GitHubResult
from asciidoc_artisan.workers import GitHubCLIWorker


@pytest.fixture
def github_worker():
    """Fixture for GitHubCLIWorker instance."""
    worker = GitHubCLIWorker()
    yield worker
    # No thread cleanup needed since GitHubCLIWorker is QObject, not QThread


@pytest.mark.unit
class TestGitHubCLIWorkerInitialization:
    """Test GitHubCLIWorker initialization and basic setup."""

    def test_github_worker_initialization(self, github_worker):
        """Test GitHubCLIWorker initializes correctly."""
        assert github_worker is not None
        assert isinstance(github_worker, GitHubCLIWorker)

    def test_github_worker_has_signals(self, github_worker):
        """Test GitHubCLIWorker has required signals."""
        assert hasattr(github_worker, "github_result_ready")

    def test_github_worker_has_cancellation_support(self, github_worker):
        """Test GitHubCLIWorker supports cancellation."""
        assert hasattr(github_worker, "cancel")
        assert hasattr(github_worker, "reset_cancellation")
        assert hasattr(github_worker, "_cancelled")


@pytest.mark.unit
class TestGitHubCLIWorkerCommands:
    """Test basic GitHub CLI command execution."""

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_successful_gh_command(self, mock_run, github_worker):
        """Test successful gh command execution."""
        # Setup mock
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"result": "success"}',
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.run_gh_command(["repo", "view", "--json", "name"])

        # Verify
        assert result is not None
        assert result.success is True
        assert result.data == {"result": "success"}
        assert result.error == ""

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_failed_gh_command(self, mock_run, github_worker):
        """Test failed gh command execution."""
        # Setup mock
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="error: not authenticated",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.run_gh_command(["pr", "list"])

        # Verify
        assert result is not None
        assert result.success is False
        assert "not authenticated" in result.error or "not authenticated" in result.user_message.lower()

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_gh_command_timeout(self, mock_run, github_worker):
        """Test gh command timeout handling."""
        # Setup mock to raise timeout
        mock_run.side_effect = subprocess.TimeoutExpired("gh", 60)

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.run_gh_command(["pr", "list"])

        # Verify timeout handled gracefully
        assert result is not None
        assert result.success is False
        assert "timeout" in result.user_message.lower() or "timed out" in result.user_message.lower()

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_gh_not_installed(self, mock_run, github_worker):
        """Test handling when gh CLI is not installed."""
        # Setup mock to raise FileNotFoundError
        mock_run.side_effect = FileNotFoundError("gh not found")

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.run_gh_command(["gh", "pr", "list"])

        # Verify
        assert result is not None
        assert result.success is False
        assert "not found" in result.user_message.lower() or "not installed" in result.user_message.lower()

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_json_parsing_success(self, mock_run, github_worker):
        """Test successful JSON parsing from gh output."""
        # Setup mock with valid JSON
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"number": 42, "title": "Test PR", "state": "open"}',
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.run_gh_command(["gh", "pr", "view", "42", "--json", "number,title,state"])

        # Verify
        assert result is not None
        assert result.success is True
        assert result.data["number"] == 42
        assert result.data["title"] == "Test PR"
        assert result.data["state"] == "open"

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_json_parsing_failure(self, mock_run, github_worker):
        """Test handling of invalid JSON from gh output."""
        # Setup mock with invalid JSON
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="This is not valid JSON",
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.run_gh_command(["pr", "list", "--json", "number,title"])

        # Verify - worker wraps non-JSON output in {"output": ...} dict
        assert result is not None
        assert result.success is True  # Worker handles this gracefully
        assert result.data is not None
        assert "output" in result.data
        assert result.data["output"] == "This is not valid JSON"


@pytest.mark.unit
class TestGitHubCLIWorkerPullRequests:
    """Test pull request operations."""

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_create_pull_request_success(self, mock_run, github_worker):
        """Test successful pull request creation."""
        # Setup mock
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"number": 42, "url": "https://github.com/user/repo/pull/42"}',
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.create_pull_request(
            title="Test PR",
            body="Test description",
            base="main",
            head="feature-branch"
        )

        # Verify
        assert result is not None
        assert result.success is True
        assert result.data["number"] == 42
        assert result.data["url"] == "https://github.com/user/repo/pull/42"

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_list_pull_requests_open(self, mock_run, github_worker):
        """Test listing open pull requests."""
        # Setup mock
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([
                {"number": 42, "title": "PR 1", "state": "open"},
                {"number": 41, "title": "PR 2", "state": "open"}
            ]),
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.list_pull_requests(state="open")

        # Verify
        assert result is not None
        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["number"] == 42
        assert result.data[1]["number"] == 41

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_list_pull_requests_all_states(self, mock_run, github_worker):
        """Test listing all pull requests regardless of state."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([
                {"number": 42, "title": "Open PR", "state": "open"},
                {"number": 41, "title": "Closed PR", "state": "closed"},
                {"number": 40, "title": "Merged PR", "state": "merged"}
            ]),
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.list_pull_requests(state=None)

        # Verify
        assert result is not None
        assert result.success is True
        assert len(result.data) == 3


@pytest.mark.unit
class TestGitHubCLIWorkerIssues:
    """Test issue operations."""

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_create_issue_success(self, mock_run, github_worker):
        """Test successful issue creation."""
        # Setup mock
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"number": 15, "url": "https://github.com/user/repo/issues/15"}',
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.create_issue(
            title="Bug report",
            body="Something is broken"
        )

        # Verify
        assert result is not None
        assert result.success is True
        assert result.data["number"] == 15
        assert result.data["url"] == "https://github.com/user/repo/issues/15"

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_list_issues_open(self, mock_run, github_worker):
        """Test listing open issues."""
        # Setup mock
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([
                {"number": 15, "title": "Issue 1", "state": "open"},
                {"number": 14, "title": "Issue 2", "state": "open"}
            ]),
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.list_issues(state="open")

        # Verify
        assert result is not None
        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["number"] == 15

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_list_issues_closed(self, mock_run, github_worker):
        """Test listing closed issues."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps([
                {"number": 13, "title": "Fixed issue", "state": "closed"}
            ]),
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.list_issues(state="closed")

        # Verify
        assert result is not None
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["state"] == "closed"


@pytest.mark.unit
class TestGitHubCLIWorkerRepository:
    """Test repository operations."""

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_get_repo_info_success(self, mock_run, github_worker):
        """Test successful repository info retrieval."""
        # Setup mock
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "name": "AsciiDoctorArtisan",
                "nameWithOwner": "user/AsciiDoctorArtisan",
                "description": "AsciiDoc editor",
                "stargazerCount": 42,
                "forkCount": 10,
                "defaultBranchRef": {"name": "main"},
                "visibility": "PUBLIC",
                "url": "https://github.com/user/AsciiDoctorArtisan"
            }),
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.get_repo_info()

        # Verify
        assert result is not None
        assert result.success is True
        assert result.data["name"] == "AsciiDoctorArtisan"
        assert result.data["stargazerCount"] == 42

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_get_repo_info_no_remote(self, mock_run, github_worker):
        """Test handling when no GitHub remote is configured."""
        # Setup mock
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="error: no default remote configured",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Execute
        github_worker.get_repo_info()

        # Verify
        assert result is not None
        assert result.success is False
        assert "remote" in result.error.lower()


@pytest.mark.unit
class TestGitHubCLIWorkerCancellation:
    """Test worker cancellation support."""

    def test_worker_cancel(self, github_worker):
        """Test worker cancellation flag."""
        # Start with not cancelled
        assert github_worker._cancelled is False

        # Cancel
        github_worker.cancel()
        assert github_worker._cancelled is True

        # Reset
        github_worker.reset_cancellation()
        assert github_worker._cancelled is False

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_cancel_prevents_execution(self, mock_run, github_worker):
        """Test cancellation prevents operation execution."""
        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Cancel before operation
        github_worker.cancel()

        # Try to run command
        github_worker.run_gh_command(["pr", "list"])

        # Should emit cancelled result without calling subprocess
        assert result is not None
        assert result.success is False
        assert "cancel" in result.error.lower()
        assert not mock_run.called


@pytest.mark.unit
class TestGitHubResult:
    """Test GitHubResult named tuple."""

    def test_github_result_creation_success(self):
        """Test GitHubResult creation for successful operation."""
        result = GitHubResult(
            success=True,
            data={"number": 42, "url": "https://github.com/..."},
            error="",
            user_message="PR created successfully",
            operation="pr_create"
        )

        assert result.success is True
        assert result.data["number"] == 42
        assert result.error == ""
        assert result.operation == "pr_create"

    def test_github_result_creation_failure(self):
        """Test GitHubResult creation for failed operation."""
        result = GitHubResult(
            success=False,
            data=None,
            error="Not authenticated",
            user_message="Please authenticate with 'gh auth login'",
            operation="pr_list"
        )

        assert result.success is False
        assert result.data is None
        assert "authenticated" in result.error
        assert result.operation == "pr_list"
