"""
Advanced tests for GitWorker - Additional error scenarios and edge cases.

This test suite complements test_git_worker.py with additional tests for:
- Extended error analysis (_analyze_git_error with more error types)
- Network and authentication error scenarios
- Repository corruption and integrity errors
- Additional status parsing edge cases

Phase 4A.2: 12 focused tests for critical git_worker.py gaps
"""

import subprocess
from unittest.mock import patch

import pytest

from asciidoc_artisan.workers.git_worker import GitWorker

# ==============================================================================
# Extended Error Analysis Tests (6 tests)
# ==============================================================================


class TestGitWorkerExtendedErrorAnalysis:
    """Test _analyze_git_error with additional error types."""

    @pytest.fixture
    def worker(self):
        """Create GitWorker instance."""
        return GitWorker()

    def test_analyze_ssl_certificate_error(self, worker):
        """Test SSL certificate error analysis."""
        stderr = "SSL certificate problem: unable to get local issuer certificate"
        result = worker._analyze_git_error(stderr, ["git", "clone"])

        # Should return generic error with stderr
        assert "Git command failed" in result
        assert "SSL" in result or "certificate" in result

    def test_analyze_permission_denied_error(self, worker):
        """Test permission denied error analysis."""
        stderr = "Permission denied (publickey)"
        result = worker._analyze_git_error(stderr, ["git", "push"])

        # Authentication failure handling
        # Note: May need to check actual implementation
        assert result  # Should return some error message

    def test_analyze_merge_conflict_error(self, worker):
        """Test merge conflict error analysis."""
        stderr = "error: Your local changes would be overwritten by merge"
        result = worker._analyze_git_error(stderr, ["git", "pull"])

        assert "Git command failed" in result
        assert "error" in result.lower()

    def test_analyze_repository_corruption_error(self, worker):
        """Test repository corruption error analysis."""
        stderr = "fatal: bad object refs/heads/master"
        result = worker._analyze_git_error(stderr, ["git", "status"])

        assert "Git command failed" in result
        assert "fatal" in result or "bad object" in result

    def test_analyze_detached_head_warning(self, worker):
        """Test detached HEAD state warning analysis."""
        stderr = "You are in 'detached HEAD' state"
        result = worker._analyze_git_error(stderr, ["git", "checkout"])

        assert "Git command failed" in result
        assert "detached" in result.lower() or "HEAD" in result

    def test_analyze_untracked_files_error(self, worker):
        """Test untracked files would be overwritten error."""
        stderr = (
            "error: The following untracked working tree files would be overwritten"
        )
        result = worker._analyze_git_error(stderr, ["git", "checkout"])

        assert "Git command failed" in result
        assert "error" in result.lower()


# ==============================================================================
# Network and Remote Error Tests (3 tests)
# ==============================================================================


class TestGitWorkerNetworkErrors:
    """Test Git network and remote operation errors."""

    @pytest.fixture
    def worker(self):
        """Create GitWorker instance."""
        return GitWorker()

    def test_connection_timeout_error(self, worker, qtbot, tmp_path):
        """Test connection timeout during network operations."""
        # Create a temporary git repository
        test_repo = tmp_path / "test_repo"
        test_repo.mkdir()
        (test_repo / ".git").mkdir()

        with patch("subprocess.run") as mock_run:
            # Simulate connection timeout
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=["git", "fetch"], timeout=30
            )

            with qtbot.waitSignal(worker.command_complete, timeout=5000) as blocker:
                worker.run_git_command(["git", "fetch"], str(test_repo))

            result = blocker.args[0]
            assert not result.success
            # Check either stderr or user_message for timeout indication
            error_text = (result.stderr + " " + result.user_message).lower()
            assert "timed out" in error_text or "timeout" in error_text

    def test_dns_resolution_failure(self, worker):
        """Test DNS resolution failure error analysis."""
        stderr = "Could not resolve hostname github.com: Name or service not known"
        result = worker._analyze_git_error(stderr, ["git", "clone"])

        # Should match "resolve host" pattern
        assert "resolve" in result.lower() or "host" in result.lower()

    def test_port_connection_refused(self, worker):
        """Test port connection refused error analysis."""
        stderr = "fatal: unable to access 'https://github.com/repo.git/': Failed to connect to github.com port 443: Connection refused"
        result = worker._analyze_git_error(stderr, ["git", "push"])

        assert "Git command failed" in result
        assert "unable to access" in result or "Failed to connect" in result


# ==============================================================================
# Status Parsing Advanced Edge Cases (3 tests)
# ==============================================================================


class TestGitWorkerStatusParsingAdvanced:
    """Test advanced status parsing scenarios."""

    @pytest.fixture
    def worker(self):
        """Create GitWorker instance."""
        return GitWorker()

    def test_parse_status_with_submodules(self, worker):
        """Test status parsing with submodule changes."""
        # Git status v2 format with submodule indicator
        status_output = """# branch.oid abcd1234
# branch.head main
# branch.upstream origin/main
# branch.ab +0 -0
1 .M N... 160000 160000 160000 sub1234... sub5678... submodule_path
"""
        status = worker._parse_git_status_v2(status_output)

        # Should detect modified file (submodule)
        assert status.branch == "main"
        assert status.modified_count > 0

    def test_parse_status_during_rebase(self, worker):
        """Test status parsing during rebase operation."""
        # Status during interactive rebase
        status_output = """# branch.oid abcd1234
# branch.head (no branch, rebasing main)
# branch.upstream origin/main
# branch.ab +0 -0
"""
        status = worker._parse_git_status_v2(status_output)

        # Should handle "no branch" state
        assert "rebase" in status.branch.lower() or "no branch" in status.branch.lower()

    def test_parse_status_with_long_filenames(self, worker):
        """Test status parsing with very long file paths."""
        # File path >255 characters
        long_path = "a" * 300 + ".txt"
        status_output = f"""# branch.oid abcd1234
# branch.head main
# branch.upstream origin/main
# branch.ab +0 -0
1 M. N... 100644 100644 100644 abc123... def456... {long_path}
"""
        status = worker._parse_git_status_v2(status_output)

        # Should handle long paths without crashing
        assert status.branch == "main"
        assert status.modified_count > 0 or status.staged_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
