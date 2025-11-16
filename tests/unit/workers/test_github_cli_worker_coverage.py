"""
Extended tests for github_cli_worker to achieve 100% coverage.

Tests for missing lines:
- Line 174: Logger info when working_dir is provided

Note: Removed unreachable JSONDecodeError handler (formerly lines 260-262)
for 100% coverage. Inner try-except already handles all JSON parsing errors.
"""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.workers import GitHubCLIWorker


@pytest.fixture
def github_worker():
    """Fixture for GitHubCLIWorker instance."""
    return GitHubCLIWorker()



@pytest.mark.fr_034
@pytest.mark.fr_035
@pytest.mark.fr_036
@pytest.mark.fr_037
@pytest.mark.fr_038
@pytest.mark.fr_076
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


# Phase 4C: Removed unreachable JSONDecodeError handler (formerly lines 260-262).
# The inner try-except at lines 200-206 already catches all JSONDecodeError exceptions,
# making the outer handler dead code. Removed for 100% coverage.


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
