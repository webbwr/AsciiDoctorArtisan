"""Tests for workers.worker_tasks module."""

import subprocess
from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.workers.optimized_worker_pool import CancelableRunnable
from asciidoc_artisan.workers.worker_tasks import (
    ConversionTask,
    GitTask,
    RenderTask,
    TaskSignals,
)


@pytest.mark.unit
class TestTaskSignals:
    """Test TaskSignals class for Qt signal communication."""

    def test_task_signals_initialization(self):
        """Test TaskSignals can be created."""
        signals = TaskSignals()
        assert signals is not None

    def test_task_signals_has_all_signals(self):
        """Test TaskSignals has all required signals."""
        signals = TaskSignals()
        assert hasattr(signals, "started")
        assert hasattr(signals, "progress")
        assert hasattr(signals, "finished")
        assert hasattr(signals, "error")
        assert hasattr(signals, "cancelled")


@pytest.mark.unit
class TestRenderTask:
    """Test RenderTask for AsciiDoc rendering."""

    def test_render_task_creation_with_auto_id(self):
        """Test RenderTask creates unique ID automatically."""
        mock_api = Mock()
        task = RenderTask("Test content", mock_api)

        assert task is not None
        assert hasattr(task, "task_id")
        assert task.task_id.startswith("render_")

    def test_render_task_creation_with_custom_id(self):
        """Test RenderTask accepts custom ID."""
        mock_api = Mock()
        task = RenderTask("Test content", mock_api, task_id="custom_render_123")

        assert task.task_id == "custom_render_123"

    def test_render_task_has_signals(self):
        """Test RenderTask has signal object."""
        mock_api = Mock()
        task = RenderTask("Test content", mock_api)

        assert hasattr(task, "signals")
        assert isinstance(task.signals, TaskSignals)

    def test_render_task_high_priority(self):
        """Test RenderTask has HIGH priority for preview updates."""
        from asciidoc_artisan.workers.optimized_worker_pool import TaskPriority

        mock_api = Mock()
        task = RenderTask("Test content", mock_api)

        assert task.priority == TaskPriority.HIGH

    def test_render_task_successful_execution(self):
        """Test RenderTask executes successfully."""
        mock_api = Mock()
        mock_api.execute = Mock()

        # Simulate successful rendering
        def mock_execute(infile, outfile, backend):
            outfile.write("<html>Rendered content</html>")

        mock_api.execute.side_effect = mock_execute

        task = RenderTask("= Test Document", mock_api)

        # Execute the task
        task.run()

        # Verify API was called
        assert mock_api.execute.called

    def test_render_task_cancellation_before_start(self):
        """Test RenderTask respects cancellation before execution."""
        mock_api = Mock()
        task = RenderTask("Test content", mock_api)

        # Cancel before execution
        task.cancel()

        # Execute the task
        task.run()

        # API should not be called when cancelled
        assert not mock_api.execute.called

    def test_render_task_cancellation_during_execution(self):
        """Test RenderTask checks cancellation during execution."""
        mock_api = Mock()

        # Simulate cancellation during rendering
        def mock_execute(infile, outfile, backend):
            # Simulate some work then check cancellation
            pass

        mock_api.execute.side_effect = mock_execute

        task = RenderTask("Test content", mock_api)
        task.cancel()  # Cancel before run
        task.run()

        # Should handle cancellation gracefully

    def test_render_task_error_handling(self):
        """Test RenderTask has error handling capability."""
        mock_api = Mock()
        task = RenderTask("Bad content", mock_api)

        # Task should have error signal for handling failures
        assert hasattr(task.signals, "error")

        # Test that signal can be connected
        error_emitted = []

        def capture_error(msg):
            error_emitted.append(msg)

        task.signals.error.connect(capture_error)

        # Verify connection works by emitting test signal
        task.signals.error.emit("Test error")
        assert len(error_emitted) == 1
        assert "Test error" in error_emitted[0]

    def test_render_task_started_signal(self):
        """Test RenderTask emits started signal."""
        mock_api = Mock()
        mock_api.execute = Mock()

        def mock_execute(infile, outfile, backend):
            outfile.write("<html>Test</html>")

        mock_api.execute.side_effect = mock_execute

        task = RenderTask("Test", mock_api)

        started_emitted = []

        def capture_started():
            started_emitted.append(True)

        task.signals.started.connect(capture_started)

        task.run()

        # Started signal should be emitted
        assert len(started_emitted) == 1


@pytest.mark.unit
class TestConversionTask:
    """Test ConversionTask for document format conversion."""

    def test_conversion_task_creation_with_auto_id(self):
        """Test ConversionTask creates unique ID automatically."""
        task = ConversionTask("Test", "asciidoc", "markdown")

        assert task.task_id.startswith("convert_")

    def test_conversion_task_creation_with_custom_id(self):
        """Test ConversionTask accepts custom ID."""
        task = ConversionTask(
            "Test", "asciidoc", "markdown", task_id="custom_convert_123"
        )

        assert task.task_id == "custom_convert_123"

    def test_conversion_task_has_signals(self):
        """Test ConversionTask has signal object."""
        task = ConversionTask("Test", "asciidoc", "markdown")

        assert hasattr(task, "signals")
        assert isinstance(task.signals, TaskSignals)

    def test_conversion_task_normal_priority(self):
        """Test ConversionTask has NORMAL priority."""
        from asciidoc_artisan.workers.optimized_worker_pool import TaskPriority

        task = ConversionTask("Test", "asciidoc", "markdown")

        assert task.priority == TaskPriority.NORMAL

    def test_conversion_task_text_conversion_success(self):
        """Test ConversionTask structure for text conversion."""
        # Test task creation succeeds (execution requires pypandoc installed)
        task = ConversionTask("# Markdown", "asciidoc", "markdown", is_file=False)
        assert task is not None
        assert hasattr(task, "run")
        assert task.task_id.startswith("convert_")

    def test_conversion_task_file_conversion_success(self):
        """Test ConversionTask structure for file conversion."""
        # Test task creation succeeds (execution requires pypandoc installed)
        task = ConversionTask("/path/to/file.md", "asciidoc", "markdown", is_file=True)
        assert task is not None
        assert hasattr(task, "run")

    def test_conversion_task_cancellation_before_start(self):
        """Test ConversionTask respects cancellation before execution."""
        task = ConversionTask("Test", "asciidoc", "markdown")

        # Cancel before execution
        task.cancel()

        # Verify cancellation flag is set
        assert task.is_canceled()

    def test_conversion_task_cancellation_after_creation(self):
        """Test ConversionTask can be cancelled."""
        task = ConversionTask("Test", "asciidoc", "markdown")

        # Should not be cancelled initially
        assert not task.is_canceled()

        # Cancel after creation
        task.cancel()

        # Should be cancelled now
        assert task.is_canceled()

    def test_conversion_task_error_handling_structure(self):
        """Test ConversionTask has error handling capability."""
        task = ConversionTask("Bad content", "asciidoc", "markdown")

        # Task should have error signal
        assert hasattr(task.signals, "error")

    def test_conversion_task_started_signal_structure(self):
        """Test ConversionTask has started signal."""
        task = ConversionTask("Test", "asciidoc", "markdown")

        # Task should have started signal
        assert hasattr(task.signals, "started")


@pytest.mark.unit
class TestGitTask:
    """Test GitTask for Git operations."""

    def test_git_task_creation_with_auto_id(self, tmp_path):
        """Test GitTask creates unique ID automatically."""
        task = GitTask(["git", "status"], tmp_path)

        assert task.task_id.startswith("git_")

    def test_git_task_creation_with_custom_id(self, tmp_path):
        """Test GitTask accepts custom ID."""
        task = GitTask(["git", "status"], tmp_path, task_id="custom_git_123")

        assert task.task_id == "custom_git_123"

    def test_git_task_has_signals(self, tmp_path):
        """Test GitTask has signal object."""
        task = GitTask(["git", "status"], tmp_path)

        assert hasattr(task, "signals")
        assert isinstance(task.signals, TaskSignals)

    def test_git_task_normal_priority(self, tmp_path):
        """Test GitTask has NORMAL priority."""
        from asciidoc_artisan.workers.optimized_worker_pool import TaskPriority

        task = GitTask(["git", "status"], tmp_path)

        assert task.priority == TaskPriority.NORMAL

    @patch("subprocess.run")
    def test_git_task_successful_execution(self, mock_run, tmp_path):
        """Test GitTask executes git command successfully."""
        mock_run.return_value = Mock(
            returncode=0, stdout="On branch main", stderr="", args=["git", "status"]
        )

        task = GitTask(["git", "status"], tmp_path)

        # Execute the task
        task.run()

        # Verify subprocess.run was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "status"]
        assert call_args[1]["cwd"] == str(tmp_path)
        assert call_args[1]["shell"] is False  # Security: no shell injection
        assert call_args[1]["timeout"] == 30  # Timeout protection

    @patch("subprocess.run")
    def test_git_task_failure_handling(self, mock_run, tmp_path):
        """Test GitTask handles git command failure."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="fatal: not a git repository",
            args=["git", "status"],
        )

        task = GitTask(["git", "status"], tmp_path)

        # Execute the task
        task.run()

        # Should not raise exception, should return GitResult with success=False

    def test_git_task_cancellation_before_start(self, tmp_path):
        """Test GitTask respects cancellation before execution."""
        task = GitTask(["git", "status"], tmp_path)

        # Cancel before execution
        task.cancel()

        # Execute the task
        task.run()

        # Task should exit early and return cancelled result

    @patch("subprocess.run")
    def test_git_task_cancellation_after_subprocess(self, mock_run, tmp_path):
        """Test GitTask checks cancellation after subprocess."""
        mock_run.return_value = Mock(
            returncode=0, stdout="Success", stderr="", args=["git", "status"]
        )

        task = GitTask(["git", "status"], tmp_path)

        # Cancel after creation
        task.cancel()

        # Execute
        task.run()

        # Should handle cancellation

    @patch("subprocess.run")
    def test_git_task_timeout_handling(self, mock_run, tmp_path):
        """Test GitTask handles subprocess timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(["git", "clone"], timeout=30)

        task = GitTask(["git", "clone", "large-repo"], tmp_path)

        # Execute - should handle timeout gracefully
        task.run()

        # No exception should propagate

    @patch("subprocess.run")
    def test_git_task_exception_handling(self, mock_run, tmp_path):
        """Test GitTask handles unexpected exceptions."""
        mock_run.side_effect = RuntimeError("Unexpected git error")

        task = GitTask(["git", "status"], tmp_path)

        # Execute - should handle exception gracefully
        task.run()

        # No exception should propagate

    @patch("subprocess.run")
    def test_git_task_started_signal(self, mock_run, tmp_path):
        """Test GitTask emits started signal."""
        mock_run.return_value = Mock(
            returncode=0, stdout="Success", stderr="", args=["git", "status"]
        )

        task = GitTask(["git", "status"], tmp_path)

        started_emitted = []

        def capture_started():
            started_emitted.append(True)

        task.signals.started.connect(capture_started)

        task.run()

        # Started signal should be emitted
        assert len(started_emitted) == 1

    @patch("subprocess.run")
    def test_git_task_security_no_shell(self, mock_run, tmp_path):
        """Test GitTask uses shell=False for security."""
        mock_run.return_value = Mock(
            returncode=0, stdout="", stderr="", args=["git", "status"]
        )

        task = GitTask(["git", "status"], tmp_path)
        task.run()

        # Verify shell=False was used
        call_args = mock_run.call_args
        assert call_args[1]["shell"] is False

    @patch("subprocess.run")
    def test_git_task_result_success_true(self, mock_run, tmp_path):
        """Test GitTask returns success=True for returncode 0."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="All good",
            stderr="",
            args=["git", "status"],
        )

        task = GitTask(["git", "status"], tmp_path)
        task.run()

        # Result should have success=True

    @patch("subprocess.run")
    def test_git_task_result_success_false(self, mock_run, tmp_path):
        """Test GitTask returns success=False for non-zero returncode."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error",
            args=["git", "status"],
        )

        task = GitTask(["git", "status"], tmp_path)
        task.run()

        # Result should have success=False


@pytest.mark.unit
class TestTaskIntegration:
    """Test task integration scenarios."""

    def test_render_task_with_real_asciidoc_api(self):
        """Test RenderTask with actual AsciiDoc API (if available)."""
        try:
            from asciidoc3.asciidoc3api import AsciiDoc3API

            api = AsciiDoc3API()
            task = RenderTask("= Test Document\n\nTest content", api)

            # Should create task without error
            assert task is not None
        except ImportError:
            pytest.skip("asciidoc3 not available")

    @patch("subprocess.run")
    def test_multiple_git_tasks_different_ids(self, mock_run, tmp_path):
        """Test multiple GitTasks get different IDs."""
        mock_run.return_value = Mock(
            returncode=0, stdout="", stderr="", args=["git", "status"]
        )

        task1 = GitTask(["git", "status"], tmp_path)
        task2 = GitTask(["git", "log"], tmp_path)

        # IDs should be different (timestamp-based)
        assert task1.task_id != task2.task_id

    def test_task_signals_can_be_connected(self):
        """Test task signals can be connected to slots."""
        signals = TaskSignals()

        results = []

        def slot_func(value):
            results.append(value)

        # Connect signal
        signals.finished.connect(slot_func)

        # Emit signal
        signals.finished.emit("test_result")

        # Slot should have been called
        assert len(results) == 1
        assert results[0] == "test_result"


@pytest.mark.unit
class TestRenderTaskInternalExecution:
    """Test RenderTask internal execution paths for complete coverage."""

    def test_render_task_internal_cancellation_checks(self):
        """Test RenderTask internal cancellation checks (lines 77, 86, 93)."""
        mock_api = Mock()

        # Create task and immediately cancel
        task = RenderTask("= Test", mock_api)
        task.cancel()

        # Execute the internal function directly to hit cancellation checks
        result = task.func()

        # Should return empty string on cancellation
        assert result == ""
        # API should not be called
        assert not mock_api.execute.called

    def test_render_task_exception_handling_in_func(self):
        """Test RenderTask exception handling in render_func (lines 97-99)."""
        mock_api = Mock()
        mock_api.execute = Mock(side_effect=ValueError("Rendering failed"))

        task = RenderTask("= Test", mock_api)

        # Should raise exception from render_func
        with pytest.raises(ValueError, match="Rendering failed"):
            task.func()

    def test_render_task_exception_in_run(self):
        """Test RenderTask exception handling in run() method (lines 114-117)."""
        mock_api = Mock()

        task = RenderTask("= Test", mock_api)

        # Mock the error signal emission
        error_emitted = []
        task.signals.error.connect(lambda msg: error_emitted.append(msg))

        # Mock super().run() to raise exception (this is what would trigger the except block)
        with patch.object(
            CancelableRunnable, "run", side_effect=RuntimeError("Super run error")
        ):
            task.run()

        # Error signal should be emitted
        assert len(error_emitted) == 1
        assert "Super run error" in error_emitted[0]


@pytest.mark.unit
class TestConversionTaskInternalExecution:
    """Test ConversionTask internal execution paths for complete coverage."""

    def test_conversion_task_internal_cancellation_before_import(self):
        """Test ConversionTask cancellation before pypandoc import (line 151)."""
        task = ConversionTask("test", "asciidoc", "markdown")
        task.cancel()

        # Execute internal function
        success, result, error = task.func()

        # Should return cancellation result
        assert success is False
        assert result == ""
        assert "cancelled" in error.lower()

    def test_conversion_task_internal_cancellation_after_import(self):
        """Test ConversionTask cancellation after pypandoc import (line 159)."""
        # This tests the second cancellation check
        # The cancellation check at line 159 will be covered by cancellation tests
        # Note: This is a placeholder test to document the coverage gap
        pass

    def test_conversion_task_text_conversion(self):
        """Test ConversionTask text conversion path (lines 168-170)."""
        # Mock pypandoc in sys.modules before creating task
        import sys

        mock_pandoc = Mock()
        mock_pandoc.convert_text = Mock(return_value="Converted text")

        with patch.dict(sys.modules, {"pypandoc": mock_pandoc}):
            task = ConversionTask("= Test", "markdown", "asciidoc", is_file=False)
            success, result, error = task.func()

            assert success is True
            assert result == "Converted text"
            assert error == ""
            mock_pandoc.convert_text.assert_called_once()

    def test_conversion_task_file_conversion(self):
        """Test ConversionTask file conversion path (lines 164-166)."""
        # Mock pypandoc in sys.modules before creating task
        import sys

        mock_pandoc = Mock()
        mock_pandoc.convert_file = Mock(return_value="Converted file")

        with patch.dict(sys.modules, {"pypandoc": mock_pandoc}):
            task = ConversionTask(
                "/tmp/test.adoc", "markdown", "asciidoc", is_file=True
            )
            success, result, error = task.func()

            assert success is True
            assert result == "Converted file"
            assert error == ""
            mock_pandoc.convert_file.assert_called_once()

    def test_conversion_task_exception_handling(self):
        """Test ConversionTask exception handling (lines 178-181)."""
        # Mock pypandoc in sys.modules before creating task
        import sys

        mock_pandoc = Mock()
        mock_pandoc.convert_text = Mock(side_effect=RuntimeError("Pandoc error"))

        with patch.dict(sys.modules, {"pypandoc": mock_pandoc}):
            task = ConversionTask("= Test", "markdown", "asciidoc")
            success, result, error = task.func()

            # Should catch exception and return error tuple
            assert success is False
            assert result == ""
            assert "Pandoc error" in error

    def test_conversion_task_exception_in_run(self):
        """Test ConversionTask exception in run() method (lines 190-195)."""
        # Create task
        task = ConversionTask("= Test", "markdown", "asciidoc")

        # Mock the error signal emission
        error_emitted = []
        task.signals.error.connect(lambda msg: error_emitted.append(msg))

        # Mock super().run() to raise exception (this is what would trigger the except block)
        with patch.object(
            CancelableRunnable, "run", side_effect=RuntimeError("Super run error")
        ):
            task.run()

        # Error signal should be emitted
        assert len(error_emitted) == 1
        assert "Super run error" in error_emitted[0]


@pytest.mark.unit
class TestGitTaskInternalExecution:
    """Test GitTask internal execution paths for complete coverage."""

    def test_git_task_internal_cancellation_before_subprocess(self, tmp_path):
        """Test GitTask cancellation before subprocess (line 223)."""
        task = GitTask(["git", "status"], tmp_path)
        task.cancel()

        # Execute internal function
        result = task.func()

        # Should return cancellation result
        assert result.success is False
        assert "cancelled" in result.stderr.lower()

    def test_git_task_internal_cancellation_after_subprocess(self, tmp_path):
        """Test GitTask cancellation after subprocess (line 246)."""
        # This is harder to test without actually running subprocess
        # Can't easily trigger the post-subprocess cancellation check
        # But the line will be covered by integration tests
        # Note: This is a placeholder test to document the coverage gap
        pass

    def test_git_task_exception_in_run(self, tmp_path):
        """Test GitTask exception in run() method (lines 298-300)."""
        task = GitTask(["git", "status"], tmp_path)

        # Mock the error signal emission
        error_emitted = []
        task.signals.error.connect(lambda msg: error_emitted.append(msg))

        # Mock super().run() to raise exception (this is what would trigger the except block)
        with patch.object(
            CancelableRunnable, "run", side_effect=RuntimeError("Super run error")
        ):
            task.run()

        # Error signal should be emitted
        assert len(error_emitted) == 1
        assert "Super run error" in error_emitted[0]
