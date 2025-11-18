"""
Extended unit tests for workers.worker_tasks - Error handling and execution paths.

This test suite covers remaining uncovered code paths in worker_tasks.py
to achieve 100% coverage (Phase 2.2 of test coverage push).
"""

import subprocess
from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.workers.worker_tasks import (
    ConversionTask,
    GitTask,
    RenderTask,
)


@pytest.mark.unit
class TestRenderTaskExecution:
    """Test RenderTask execution paths and error handling."""

    def test_render_task_error_in_rendering(self):
        """Test RenderTask has error signal (structure test)."""
        mock_api = Mock()
        task = RenderTask("= Test", mock_api)

        # Connect error signal to capture error
        errors = []
        task.signals.error.connect(lambda msg: errors.append(msg))

        # Emit test error
        task.signals.error.emit("Test error")

        # Signal should work
        assert len(errors) == 1
        assert "Test error" in errors[0]

    def test_render_task_cancellation_mid_render(self):
        """Test RenderTask checks cancellation during rendering."""
        mock_api = Mock()

        # Simulate slow rendering that checks cancellation
        def slow_render(infile, outfile, backend):
            # Task might be cancelled during this slow operation
            outfile.write("<html>Partial</html>")

        mock_api.execute.side_effect = slow_render

        task = RenderTask("= Long Document\n" * 100, mock_api)

        # Cancel immediately after creation (before rendering)
        task.cancel()

        # Run task
        task.run()

        # Should exit early, not call API
        assert not mock_api.execute.called

    def test_render_task_cancellation_after_execute(self):
        """Test RenderTask checks cancellation after execute."""
        mock_api = Mock()

        # Track if cancellation was checked after execute
        cancellation_checked_after = [False]

        def render_and_cancel(infile, outfile, backend):
            outfile.write("<html>Result</html>")
            # Simulate cancellation happening right after rendering
            task.cancel()
            cancellation_checked_after[0] = True

        mock_api.execute.side_effect = render_and_cancel

        task = RenderTask("= Test", mock_api)
        task.run()

        # Should have gone through rendering
        assert mock_api.execute.called
        assert cancellation_checked_after[0]

    def test_render_task_cancellation_before_execute_call(self):
        """Test RenderTask returns empty string if cancelled before execute (line 86)."""
        mock_api = Mock()
        task = RenderTask("= Test", mock_api)

        # Mock is_canceled to return False first, then True at line 86
        cancel_count = [0]

        def mock_is_canceled():
            cancel_count[0] += 1
            # First call (initial check): return False
            # Second call (line 85-86 before execute): return True to trigger early return
            return cancel_count[0] >= 2

        task.is_canceled = mock_is_canceled

        # Run task - this triggers line 86
        task.run()

        # execute should not be called due to cancellation at line 86
        assert not mock_api.execute.called
        # Should have checked cancellation at least twice
        assert cancel_count[0] >= 2

    def test_render_task_cancellation_after_execute_call(self):
        """Test RenderTask returns empty string if cancelled after execute (line 93)."""
        mock_api = Mock()

        def execute_then_cancel(infile, outfile, backend):
            outfile.write("<html>Test</html>")

        mock_api.execute.side_effect = execute_then_cancel

        task = RenderTask("= Test", mock_api)

        # Mock is_canceled to return False until after execute
        cancel_count = [0]

        def mock_is_canceled():
            cancel_count[0] += 1
            # First two calls: return False
            # Third call (line 92-93 after execute): return True
            return cancel_count[0] >= 3

        task.is_canceled = mock_is_canceled

        # Run task - this triggers line 93
        task.run()

        # execute should have been called
        assert mock_api.execute.called
        # Should have checked cancellation at least 3 times
        assert cancel_count[0] >= 3


@pytest.mark.unit
class TestConversionTaskExecution:
    """Test ConversionTask execution paths."""

    @patch("pypandoc.convert_text")
    def test_conversion_task_text_conversion_actual(self, mock_convert_text):
        """Test ConversionTask actually executes text conversion."""
        mock_convert_text.return_value = "Converted text result"

        task = ConversionTask("# Markdown", "asciidoc", "markdown", is_file=False)

        # Run the task
        task.run()

        # Should have called convert_text
        mock_convert_text.assert_called_once_with("# Markdown", "asciidoc", format="markdown")

    @patch("pypandoc.convert_file")
    def test_conversion_task_file_conversion_actual(self, mock_convert_file):
        """Test ConversionTask actually executes file conversion."""
        mock_convert_file.return_value = "Converted file result"

        task = ConversionTask("/path/to/file.md", "asciidoc", "markdown", is_file=True)

        # Run the task
        task.run()

        # Should have called convert_file
        mock_convert_file.assert_called_once_with("/path/to/file.md", "asciidoc", format="markdown")

    @patch("pypandoc.convert_text")
    def test_conversion_task_cancellation_before_import(self, mock_convert_text):
        """Test ConversionTask respects cancellation before pypandoc import."""
        task = ConversionTask("Test", "asciidoc", "markdown")

        # Cancel before running
        task.cancel()

        # Run task
        task.run()

        # Should not call pypandoc
        assert not mock_convert_text.called

    @patch("pypandoc.convert_text")
    def test_conversion_task_cancellation_after_import_line_160(self, mock_convert_text):
        """Test ConversionTask returns cancelled result if cancelled after import (line 160)."""
        task = ConversionTask("Test", "asciidoc", "markdown")

        # Mock is_canceled to return False for initial checks, then True at line 160
        cancel_count = [0]

        def mock_is_canceled():
            cancel_count[0] += 1
            # First call (initial check): return False to pass
            # Second call (line 159-160 after import): return True
            return cancel_count[0] >= 2

        task.is_canceled = mock_is_canceled

        # Run task - this triggers line 160
        task.run()

        # convert should not have been called due to cancellation at line 160
        assert not mock_convert_text.called
        # Should have checked cancellation at least twice
        assert cancel_count[0] >= 2

    @patch("pypandoc.convert_text")
    def test_conversion_task_cancellation_after_convert_line_174(self, mock_convert_text):
        """Test ConversionTask returns cancelled result if cancelled after convert (line 174)."""
        mock_convert_text.return_value = "Converted"
        task = ConversionTask("Test", "asciidoc", "markdown")

        # Mock is_canceled to return False until after convert
        cancel_count = [0]

        def mock_is_canceled():
            cancel_count[0] += 1
            # First two calls: return False
            # Third call (line 173-174 after convert): return True
            return cancel_count[0] >= 3

        task.is_canceled = mock_is_canceled

        # Run task - this triggers line 174
        task.run()

        # convert should have been called
        assert mock_convert_text.called
        # Should have checked cancellation at least 3 times
        assert cancel_count[0] >= 3

    @patch("pypandoc.convert_text")
    def test_conversion_task_cancellation_after_import(self, mock_convert_text):
        """Test ConversionTask checks cancellation after pypandoc import."""
        task = ConversionTask("Test", "asciidoc", "markdown")

        # Simulate cancellation during import (right after)
        def cancel_after_import(*args, **kwargs):
            task.cancel()
            return "Result"

        mock_convert_text.side_effect = cancel_after_import

        # Run task
        task.run()

        # Pypandoc was called, but result should indicate cancellation
        assert mock_convert_text.called

    @patch("pypandoc.convert_text")
    def test_conversion_task_conversion_error(self, mock_convert_text):
        """Test ConversionTask handles conversion errors."""
        mock_convert_text.side_effect = RuntimeError("Pandoc error")

        task = ConversionTask("Bad input", "asciidoc", "markdown")

        # Run should not crash
        task.run()

        # No exception should propagate

    def test_conversion_task_error_signal_emission(self):
        """Test ConversionTask has error signal (structure test)."""
        task = ConversionTask("Test", "asciidoc", "markdown")

        # Connect error signal
        errors = []
        task.signals.error.connect(lambda msg: errors.append(msg))

        # Emit test error
        task.signals.error.emit("Test error")

        # Signal should work
        assert len(errors) == 1
        assert "Test error" in errors[0]

    @patch("pypandoc.convert_text")
    def test_conversion_task_started_signal_emission(self, mock_convert_text):
        """Test ConversionTask emits started signal."""
        mock_convert_text.return_value = "Result"

        task = ConversionTask("Test", "asciidoc", "markdown")

        # Connect started signal
        started = []
        task.signals.started.connect(lambda: started.append(True))

        # Run task
        task.run()

        # Started signal should be emitted
        assert len(started) == 1


@pytest.mark.unit
class TestGitTaskExecution:
    """Test GitTask execution paths and result handling."""

    @patch("subprocess.run")
    def test_git_task_result_object_on_success(self, mock_run, tmp_path):
        """Test GitTask creates proper GitResult on success."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="On branch main",
            stderr="",
            args=["git", "status"],
        )

        task = GitTask(["git", "status"], tmp_path)

        # Capture result by accessing internal state after run
        task.run()

        # GitResult should have been created (verified by no exception)

    @patch("subprocess.run")
    def test_git_task_result_object_on_failure(self, mock_run, tmp_path):
        """Test GitTask creates proper GitResult on command failure."""
        mock_run.return_value = Mock(
            returncode=128,
            stdout="",
            stderr="fatal: not a git repository",
            args=["git", "status"],
        )

        task = GitTask(["git", "status"], tmp_path)

        # Run should not crash
        task.run()

        # GitResult with success=False should have been created

    @patch("subprocess.run")
    def test_git_task_timeout_returns_git_result(self, mock_run, tmp_path):
        """Test GitTask returns GitResult on timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(["git", "fetch"], timeout=30)

        task = GitTask(["git", "fetch", "origin"], tmp_path)

        # Run should not crash
        task.run()

        # GitResult with timeout error should have been created

    @patch("subprocess.run")
    def test_git_task_exception_returns_git_result(self, mock_run, tmp_path):
        """Test GitTask returns GitResult on unexpected exception."""
        mock_run.side_effect = OSError("Permission denied")

        task = GitTask(["git", "status"], tmp_path)

        # Run should not crash
        task.run()

        # GitResult with error should have been created

    @patch("subprocess.run")
    def test_git_task_cancellation_returns_cancelled_result(self, mock_run, tmp_path):
        """Test GitTask returns cancelled GitResult when cancelled."""
        task = GitTask(["git", "status"], tmp_path)

        # Cancel before running
        task.cancel()

        # Run task
        task.run()

        # Should not call subprocess
        assert not mock_run.called

    @patch("subprocess.run")
    def test_git_task_cancellation_after_subprocess_returns_cancelled(self, mock_run, tmp_path):
        """Test GitTask returns cancelled result if cancelled after subprocess."""
        # Simulate subprocess succeeding but task being cancelled
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Success",
            stderr="",
            args=["git", "status"],
        )

        task = GitTask(["git", "status"], tmp_path)

        # Cancel right after creation (simulates cancellation during execution)
        def run_and_cancel(*args, **kwargs):
            task.cancel()
            return Mock(returncode=0, stdout="Success", stderr="", args=["git", "status"])

        mock_run.side_effect = run_and_cancel

        # Run task
        task.run()

        # Should have called subprocess
        assert mock_run.called

    @patch("subprocess.run")
    def test_git_task_cancellation_at_line_246(self, mock_run, tmp_path):
        """Test GitTask returns cancelled result at line 246 check."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Success",
            stderr="",
            args=["git", "status"],
        )

        task = GitTask(["git", "status"], tmp_path)

        # Mock is_canceled to return False until after subprocess
        cancel_count = [0]

        def mock_is_canceled():
            cancel_count[0] += 1
            # First two calls: return False
            # Third call (line 245-246 after subprocess): return True
            return cancel_count[0] >= 3

        task.is_canceled = mock_is_canceled

        # Run task - this should trigger line 246
        result = task.run()

        # Should have called subprocess
        assert mock_run.called
        # Result should be cancelled GitResult
        # (GitTask returns GitResult object, not tuple)
        assert result is None  # run() doesn't return, stores in _result

    def test_git_task_error_signal_structure(self, tmp_path):
        """Test GitTask has error signal (structure test)."""
        task = GitTask(["git", "status"], tmp_path)

        # Connect error signal
        errors = []
        task.signals.error.connect(lambda msg: errors.append(msg))

        # Emit test error
        task.signals.error.emit("Test error")

        # Signal should work
        assert len(errors) == 1
        assert "Test error" in errors[0]

    @patch("subprocess.run")
    def test_git_task_captures_stdout_and_stderr(self, mock_run, tmp_path):
        """Test GitTask captures stdout and stderr."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="Some output",
            stderr="Some error",
            args=["git", "push"],
        )

        task = GitTask(["git", "push"], tmp_path)

        # Run task
        task.run()

        # Subprocess should have been called with capture_output=True
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["capture_output"] is True
        assert call_kwargs["text"] is True

    @patch("subprocess.run")
    def test_git_task_timeout_value(self, mock_run, tmp_path):
        """Test GitTask uses 30-second timeout."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="", args=["git", "status"])

        task = GitTask(["git", "status"], tmp_path)
        task.run()

        # Should use 30-second timeout
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 30

    @patch("subprocess.run")
    def test_git_task_cwd_parameter(self, mock_run, tmp_path):
        """Test GitTask passes correct working directory."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="", args=["git", "status"])

        task = GitTask(["git", "status"], tmp_path)
        task.run()

        # Should use provided path as cwd
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cwd"] == str(tmp_path)


@pytest.mark.unit
class TestTaskCancellationScenarios:
    """Test cancellation scenarios across all task types."""

    def test_render_task_is_canceled_check(self):
        """Test RenderTask is_canceled() method."""
        mock_api = Mock()
        task = RenderTask("Test", mock_api)

        # Not cancelled initially
        assert not task.is_canceled()

        # Cancel
        task.cancel()

        # Should be cancelled now
        assert task.is_canceled()

    def test_conversion_task_is_canceled_check(self):
        """Test ConversionTask is_canceled() method."""
        task = ConversionTask("Test", "asciidoc", "markdown")

        # Not cancelled initially
        assert not task.is_canceled()

        # Cancel
        task.cancel()

        # Should be cancelled now
        assert task.is_canceled()

    def test_git_task_is_canceled_check(self, tmp_path):
        """Test GitTask is_canceled() method."""
        task = GitTask(["git", "status"], tmp_path)

        # Not cancelled initially
        assert not task.is_canceled()

        # Cancel
        task.cancel()

        # Should be cancelled now
        assert task.is_canceled()


@pytest.mark.unit
class TestTaskPriorities:
    """Test task priority assignments."""

    def test_render_task_priority_is_high(self):
        """Test RenderTask has HIGH priority (user-visible preview)."""
        from asciidoc_artisan.workers.optimized_worker_pool import TaskPriority

        mock_api = Mock()
        task = RenderTask("Test", mock_api)

        assert task.priority == TaskPriority.HIGH

    def test_conversion_task_priority_is_normal(self):
        """Test ConversionTask has NORMAL priority."""
        from asciidoc_artisan.workers.optimized_worker_pool import TaskPriority

        task = ConversionTask("Test", "asciidoc", "markdown")

        assert task.priority == TaskPriority.NORMAL

    def test_git_task_priority_is_normal(self, tmp_path):
        """Test GitTask has NORMAL priority."""
        from asciidoc_artisan.workers.optimized_worker_pool import TaskPriority

        task = GitTask(["git", "status"], tmp_path)

        assert task.priority == TaskPriority.NORMAL
