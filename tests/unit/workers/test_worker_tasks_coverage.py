"""
Extended tests for worker_tasks to improve coverage from 99% to 100%.

Coverage improvements:
- Line 246: Cancellation check after subprocess completes in GitTask
"""

from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.workers.worker_tasks import GitTask


@pytest.mark.fr_076
@pytest.mark.unit
class TestWorkerTasksCoverage:
    """Tests to achieve 100% coverage for worker_tasks."""

    @patch("asciidoc_artisan.workers.worker_tasks.subprocess.run")
    def test_git_task_post_subprocess_cancellation(self, mock_run, tmp_path):
        """Test GitTask cancellation after subprocess completes (line 246)."""

        # Mock subprocess to simulate a slow operation
        def slow_subprocess(*args, **kwargs):
            # Simulate subprocess taking time
            return Mock(
                returncode=0,
                stdout="Success",
                stderr="",
                args=["git", "status"],
            )

        mock_run.side_effect = slow_subprocess

        task = GitTask(["git", "status"], tmp_path)

        # Track call count for is_canceled
        call_count = [0]

        def mock_is_canceled():
            call_count[0] += 1
            # Return False for first check (before subprocess)
            # Return True for second check (after subprocess at line 245-246)
            if call_count[0] >= 2:
                # Cancel after subprocess completes
                task.cancel()
                return True
            return False

        # Replace is_canceled with our mock
        task.is_canceled = mock_is_canceled

        # Execute the task function directly
        # The git_func is stored in task.func
        result = task.func()

        # Verify subprocess was called
        assert mock_run.called

        # Verify cancellation result (line 246)
        assert result is not None
        assert result.success is False
        assert "cancelled" in result.stderr.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
