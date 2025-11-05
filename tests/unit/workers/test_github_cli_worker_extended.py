"""
Extended unit tests for GitHubCLIWorker - Coverage completion.

This test suite covers remaining uncovered code paths in github_cli_worker.py
to achieve 100% coverage (Phase 2.3 of test coverage push).
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.core import GitHubResult
from asciidoc_artisan.workers import GitHubCLIWorker


@pytest.fixture
def github_worker():
    """Fixture for GitHubCLIWorker instance."""
    return GitHubCLIWorker()


@pytest.mark.unit
class TestDispatchGitHubOperation:
    """Test dispatch_github_operation method for all operation types."""

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_dispatch_create_pull_request(self, mock_run, github_worker):
        """Test dispatching create_pull_request operation."""
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

        # Dispatch create_pull_request
        github_worker.dispatch_github_operation(
            "create_pull_request",
            {
                "title": "Test PR",
                "body": "Test body",
                "base": "main",
                "head": "feature",
                "working_dir": "",
            },
        )

        assert result is not None
        assert result.success is True

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_dispatch_list_pull_requests(self, mock_run, github_worker):
        """Test dispatching list_pull_requests operation."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"number": 1, "title": "PR 1"}]',
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Dispatch list_pull_requests
        github_worker.dispatch_github_operation(
            "list_pull_requests", {"state": "open", "working_dir": ""}
        )

        assert result is not None
        assert result.success is True

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_dispatch_create_issue(self, mock_run, github_worker):
        """Test dispatching create_issue operation."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"number": 10, "url": "https://github.com/user/repo/issues/10"}',
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Dispatch create_issue
        github_worker.dispatch_github_operation(
            "create_issue",
            {"title": "Bug report", "body": "Issue body", "working_dir": ""},
        )

        assert result is not None
        assert result.success is True

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_dispatch_list_issues(self, mock_run, github_worker):
        """Test dispatching list_issues operation."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"number": 1, "title": "Issue 1"}]',
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Dispatch list_issues
        github_worker.dispatch_github_operation(
            "list_issues", {"state": "open", "working_dir": ""}
        )

        assert result is not None
        assert result.success is True

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_dispatch_get_repo_info(self, mock_run, github_worker):
        """Test dispatching get_repo_info operation."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"name": "repo", "nameWithOwner": "user/repo"}',
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Dispatch get_repo_info
        github_worker.dispatch_github_operation("get_repo_info", {"working_dir": ""})

        assert result is not None
        assert result.success is True

    def test_dispatch_unknown_operation(self, github_worker):
        """Test dispatching unknown operation returns error."""
        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Dispatch unknown operation (using "unknown" which is in allowed set)
        github_worker.dispatch_github_operation("unknown", {})

        assert result is not None
        assert result.success is False
        assert "unknown" in result.error.lower() or "not supported" in result.error.lower()


@pytest.mark.unit
class TestParseGhError:
    """Test _parse_gh_error method for all error types."""

    def test_parse_not_logged_in_error(self, github_worker):
        """Test parsing 'not logged into' error."""
        stderr = "error: not logged into any GitHub hosts"
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert "not authenticated" in result.lower()
        assert "gh auth login" in result.lower()

    def test_parse_not_authenticated_error(self, github_worker):
        """Test parsing 'not authenticated' error."""
        stderr = "error: not authenticated"
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert "not authenticated" in result.lower()

    def test_parse_no_default_remote_error(self, github_worker):
        """Test parsing 'no default remote' error."""
        stderr = "error: no default remote defined"
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert "no github remote" in result.lower()
        assert "git remote add" in result.lower()

    def test_parse_not_git_repository_error(self, github_worker):
        """Test parsing 'not a git repository' error."""
        stderr = "fatal: not a git repository"
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert "no github remote" in result.lower()

    def test_parse_rate_limit_error(self, github_worker):
        """Test parsing 'rate limit' error."""
        stderr = "error: rate limit exceeded"
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert "rate limit" in result.lower()
        assert "1 hour" in result.lower()

    def test_parse_permission_denied_error(self, github_worker):
        """Test parsing 'permission denied' error."""
        stderr = "error: permission denied to access repository"
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert "permission denied" in result.lower()
        assert "token" in result.lower()

    def test_parse_forbidden_error(self, github_worker):
        """Test parsing 'forbidden' error."""
        stderr = "HTTP 403: Forbidden"
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert "permission denied" in result.lower()

    def test_parse_repository_not_found_error(self, github_worker):
        """Test parsing 'repository not found' error."""
        stderr = "error: repository not found"
        result = github_worker._parse_gh_error(stderr, ["repo", "view"])

        assert "not found" in result.lower()
        assert "repository" in result.lower()

    def test_parse_network_error(self, github_worker):
        """Test parsing 'network' error."""
        stderr = "error: network connection failed"
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert "network error" in result.lower()
        assert "internet" in result.lower()

    def test_parse_could_not_resolve_host_error(self, github_worker):
        """Test parsing 'could not resolve host' error."""
        stderr = "error: could not resolve host github.com"
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert "network error" in result.lower()

    def test_parse_timeout_error(self, github_worker):
        """Test parsing 'timeout' error."""
        stderr = "error: request timeout after 30 seconds"
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert "timeout" in result.lower() or "timed out" in result.lower()

    def test_parse_generic_error(self, github_worker):
        """Test parsing generic error message."""
        stderr = "Some unexpected error occurred"
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert "some unexpected error" in result.lower()

    def test_parse_long_error_truncated(self, github_worker):
        """Test long error message is truncated to 200 chars."""
        stderr = "A" * 300  # 300 character error
        result = github_worker._parse_gh_error(stderr, ["pr", "list"])

        assert len(result) < 250  # Should be truncated


@pytest.mark.unit
class TestRunGhCommandEdgeCases:
    """Test run_gh_command edge cases and error paths."""

    def test_cancellation_before_execution(self, github_worker):
        """Test cancellation prevents command execution."""
        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Cancel before running
        github_worker.cancel()

        # Run command
        github_worker.run_gh_command(["pr", "list"])

        # Should return cancelled result
        assert result is not None
        assert result.success is False
        assert "cancel" in result.error.lower()

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_invalid_working_directory(self, mock_run, github_worker):
        """Test invalid working directory is caught."""
        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Run with non-existent directory
        github_worker.run_gh_command(
            ["pr", "list"], working_dir="/nonexistent/path/12345"
        )

        # Should not call subprocess
        assert not mock_run.called
        assert result is not None
        assert result.success is False
        assert "not found" in result.error.lower()

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_non_json_output_wrapped(self, mock_run, github_worker):
        """Test non-JSON output is wrapped in dict."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Plain text output, not JSON",
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Run command (using "gh" as operation which is in allowed set)
        github_worker.run_gh_command(["gh", "status"], operation="gh")

        assert result is not None
        assert result.success is True
        assert result.data == {"output": "Plain text output, not JSON"}

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_empty_stdout(self, mock_run, github_worker):
        """Test empty stdout is handled."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Run command
        github_worker.run_gh_command(["pr", "list"])

        assert result is not None
        assert result.success is True
        assert result.data is None

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_json_decode_error_handling(self, mock_run, github_worker):
        """Test invalid JSON is wrapped as plain text (not an error)."""
        # Mock successful process but with invalid JSON in stdout
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="{invalid json}",
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Run command
        github_worker.run_gh_command(["pr", "list", "--json", "number"])

        assert result is not None
        # Invalid JSON is wrapped as plain text, not treated as error
        assert result.success is True
        assert result.data == {"output": "{invalid json}"}

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_unexpected_exception_handling(self, mock_run, github_worker):
        """Test unexpected exception is caught."""
        mock_run.side_effect = RuntimeError("Unexpected error")

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Run command
        github_worker.run_gh_command(["pr", "list"])

        assert result is not None
        assert result.success is False
        assert "unexpected" in result.error.lower() or "unexpected" in result.user_message.lower()

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_operation_parameter_default(self, mock_run, github_worker):
        """Test operation parameter defaults to first arg."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"result": "ok"}',
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Run command without operation parameter
        github_worker.run_gh_command(["repo", "view"])

        assert result is not None
        assert result.operation == "repo"

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_empty_args_list(self, mock_run, github_worker):
        """Test empty args list is handled."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="{}",
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # Run command with empty args
        github_worker.run_gh_command([])

        assert result is not None
        assert result.operation == "unknown"


@pytest.mark.unit
class TestOperationMethods:
    """Test individual operation methods."""

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_list_pull_requests_with_state(self, mock_run, github_worker):
        """Test list_pull_requests with state parameter."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"number": 1}]',
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # List PRs with specific state
        github_worker.list_pull_requests(state="closed")

        assert result is not None
        assert result.success is True
        # Verify --state flag was added to command
        call_args = mock_run.call_args[0][0]
        assert "--state" in call_args
        assert "closed" in call_args

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_list_issues_with_state(self, mock_run, github_worker):
        """Test list_issues with state parameter."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"number": 1}]',
            stderr="",
        )

        result = None

        def capture_result(github_result):
            nonlocal result
            result = github_result

        github_worker.github_result_ready.connect(capture_result)

        # List issues with specific state
        github_worker.list_issues(state="closed")

        assert result is not None
        assert result.success is True
        # Verify --state flag was added to command
        call_args = mock_run.call_args[0][0]
        assert "--state" in call_args
        assert "closed" in call_args
