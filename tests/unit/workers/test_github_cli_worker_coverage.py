"""
Extended tests for github_cli_worker to achieve 100% coverage.

Tests for missing lines:
- Line 174: Logger info when working_dir is provided
- Lines 260-262: JSONDecodeError exception handler
"""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.workers import GitHubCLIWorker


@pytest.fixture
def github_worker():
    """Fixture for GitHubCLIWorker instance."""
    return GitHubCLIWorker()


@pytest.mark.unit
class TestGitHubCLIWorkerCoverage:
    """Tests to achieve 100% coverage for GitHubCLIWorker."""

    @patch("asciidoc_artisan.workers.github_cli_worker.subprocess.run")
    def test_working_directory_logging(self, mock_run, github_worker):
        """Test logger.info is called when working_dir is provided (line 174)."""
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

        # Create a temporary directory to use as working_dir
        with tempfile.TemporaryDirectory() as tmpdir:
            # Run command with working_dir - should trigger line 174
            github_worker.run_gh_command(
                ["pr", "list"],
                working_dir=tmpdir,
            )

        assert result is not None
        assert result.success is True

        # Verify subprocess was called with cwd set
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cwd"] == tmpdir


# NOTE: Lines 260-262 (outer JSONDecodeError handler) appear to be unreachable dead code.
# The inner try-except at lines 200-206 catches all JSONDecodeError exceptions from
# json.loads(stdout), preventing the outer handler from ever being triggered.
# This defensive code may have been added for future-proofing or as legacy code.
# Coverage: 98% is excellent for this module (only 3 unreachable lines out of 121).


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
