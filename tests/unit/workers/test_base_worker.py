"""
Tests for BaseWorker (v2.0.0).

Tests the base worker class functionality including cancellation,
directory validation, and subprocess execution.
"""

import subprocess
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.workers.base_worker import BaseWorker


@pytest.mark.unit
class TestInitialization:
    """Test BaseWorker initialization."""

    def test_init_cancellation_flag(self):
        """Test worker initializes with cancelled=False."""
        worker = BaseWorker()

        assert worker._cancelled is False

    def test_init_inherits_qobject(self):
        """Test worker inherits from QObject."""
        worker = BaseWorker()

        # Should have QObject methods
        assert hasattr(worker, "deleteLater")
        assert hasattr(worker, "objectName")


@pytest.mark.unit
class TestCancellation:
    """Test cancellation functionality."""

    def test_cancel_sets_flag(self):
        """Test cancel() sets cancellation flag."""
        worker = BaseWorker()

        worker.cancel()

        assert worker._cancelled is True

    def test_cancel_logs_message(self, caplog):
        """Test cancel() logs cancellation request."""
        import logging

        caplog.set_level(logging.INFO)

        worker = BaseWorker()

        worker.cancel()

        assert "cancellation requested" in caplog.text.lower()
        assert "BaseWorker" in caplog.text

    def test_reset_cancellation_clears_flag(self):
        """Test reset_cancellation() clears flag."""
        worker = BaseWorker()
        worker._cancelled = True

        worker.reset_cancellation()

        assert worker._cancelled is False

    def test_check_cancellation_returns_flag_state(self):
        """Test _check_cancellation() returns current flag state."""
        worker = BaseWorker()

        # Initially False
        assert worker._check_cancellation() is False

        # After cancel
        worker.cancel()
        assert worker._check_cancellation() is True

        # After reset
        worker.reset_cancellation()
        assert worker._check_cancellation() is False


@pytest.mark.unit
class TestWorkingDirectoryValidation:
    """Test working directory validation."""

    def test_validate_existing_directory(self):
        """Test validation passes for existing directory."""
        worker = BaseWorker()

        with tempfile.TemporaryDirectory() as tmpdir:
            result = worker._validate_working_directory(tmpdir)

            assert result is True

    def test_validate_nonexistent_directory(self):
        """Test validation fails for nonexistent directory."""
        worker = BaseWorker()

        result = worker._validate_working_directory("/nonexistent/path/12345")

        assert result is False

    def test_validate_file_not_directory(self):
        """Test validation fails when path is a file."""
        worker = BaseWorker()

        with tempfile.NamedTemporaryFile() as tmpfile:
            result = worker._validate_working_directory(tmpfile.name)

            assert result is False

    def test_validate_empty_string(self):
        """Test validation returns True for empty string (current directory)."""
        worker = BaseWorker()

        # Empty string resolves to current directory which exists
        result = worker._validate_working_directory("")

        # Path("").is_dir() returns True (current directory)
        assert result is True


@pytest.mark.unit
class TestBuildSubprocessKwargs:
    """Test _build_subprocess_kwargs method."""

    def test_build_kwargs_default_values(self):
        """Test kwargs built with default values."""
        worker = BaseWorker()

        kwargs = worker._build_subprocess_kwargs()

        assert kwargs["cwd"] is None
        assert kwargs["timeout"] == 30
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert kwargs["check"] is False
        assert kwargs["shell"] is False  # Critical security
        assert kwargs["encoding"] == "utf-8"
        assert kwargs["errors"] == "replace"

    def test_build_kwargs_custom_working_dir(self):
        """Test kwargs with custom working directory."""
        worker = BaseWorker()

        kwargs = worker._build_subprocess_kwargs(working_dir="/tmp")

        assert kwargs["cwd"] == "/tmp"

    def test_build_kwargs_custom_timeout(self):
        """Test kwargs with custom timeout."""
        worker = BaseWorker()

        kwargs = worker._build_subprocess_kwargs(timeout=60)

        assert kwargs["timeout"] == 60

    def test_build_kwargs_both_custom(self):
        """Test kwargs with both custom values."""
        worker = BaseWorker()

        kwargs = worker._build_subprocess_kwargs(working_dir="/usr/local", timeout=120)

        assert kwargs["cwd"] == "/usr/local"
        assert kwargs["timeout"] == 120

    def test_build_kwargs_shell_always_false(self):
        """Test shell=False is always set (security)."""
        worker = BaseWorker()

        # Try various configurations
        kwargs1 = worker._build_subprocess_kwargs()
        kwargs2 = worker._build_subprocess_kwargs(working_dir="/tmp")
        kwargs3 = worker._build_subprocess_kwargs(timeout=5)

        assert kwargs1["shell"] is False
        assert kwargs2["shell"] is False
        assert kwargs3["shell"] is False


@pytest.mark.unit
class TestExecuteSubprocess:
    """Test _execute_subprocess method."""

    @patch("asciidoc_artisan.workers.base_worker.subprocess.run")
    def test_execute_subprocess_success(self, mock_run):
        """Test successful subprocess execution."""
        worker = BaseWorker()

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success output",
            stderr="",
        )

        result = worker._execute_subprocess(["echo", "test"])

        assert result.returncode == 0
        assert result.stdout == "Success output"
        mock_run.assert_called_once()

    @patch("asciidoc_artisan.workers.base_worker.subprocess.run")
    def test_execute_subprocess_with_working_dir(self, mock_run):
        """Test subprocess execution with working directory."""
        worker = BaseWorker()

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        worker._execute_subprocess(["ls"], working_dir="/tmp")

        # Check that cwd was passed to subprocess.run
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cwd"] == "/tmp"

    @patch("asciidoc_artisan.workers.base_worker.subprocess.run")
    def test_execute_subprocess_with_custom_timeout(self, mock_run):
        """Test subprocess execution with custom timeout."""
        worker = BaseWorker()

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        worker._execute_subprocess(["sleep", "1"], timeout=5)

        # Check that timeout was passed
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 5

    @patch("asciidoc_artisan.workers.base_worker.subprocess.run")
    def test_execute_subprocess_timeout_error(self, mock_run):
        """Test subprocess execution raises TimeoutExpired."""
        worker = BaseWorker()

        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)

        with pytest.raises(subprocess.TimeoutExpired):
            worker._execute_subprocess(["sleep", "100"], timeout=1)

    @patch("asciidoc_artisan.workers.base_worker.subprocess.run")
    def test_execute_subprocess_file_not_found(self, mock_run):
        """Test subprocess execution raises FileNotFoundError."""
        worker = BaseWorker()

        mock_run.side_effect = FileNotFoundError("Command not found")

        with pytest.raises(FileNotFoundError):
            worker._execute_subprocess(["nonexistent_command"])

    @patch("asciidoc_artisan.workers.base_worker.subprocess.run")
    def test_execute_subprocess_shell_never_true(self, mock_run):
        """Test subprocess always called with shell=False (security)."""
        worker = BaseWorker()

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        worker._execute_subprocess(["echo", "test"])

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["shell"] is False

    @patch("asciidoc_artisan.workers.base_worker.subprocess.run")
    def test_execute_subprocess_command_as_list(self, mock_run):
        """Test command passed as list (not string)."""
        worker = BaseWorker()

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        command = ["git", "status", "--short"]
        worker._execute_subprocess(command)

        # First arg to subprocess.run should be the command list
        call_args = mock_run.call_args[0]
        assert call_args[0] == command

    @patch("asciidoc_artisan.workers.base_worker.subprocess.run")
    def test_execute_subprocess_logs_command(self, mock_run, caplog):
        """Test subprocess execution logs command."""
        import logging

        caplog.set_level(logging.INFO)

        worker = BaseWorker()

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        worker._execute_subprocess(["echo", "test"])

        assert "Executing command" in caplog.text
        assert "echo test" in caplog.text

    @patch("asciidoc_artisan.workers.base_worker.subprocess.run")
    def test_execute_subprocess_logs_working_dir(self, mock_run, caplog):
        """Test subprocess execution logs working directory."""
        import logging

        caplog.set_level(logging.INFO)

        worker = BaseWorker()

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        worker._execute_subprocess(["ls"], working_dir="/tmp")

        assert "Working directory" in caplog.text
        assert "/tmp" in caplog.text


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_multiple_cancel_calls(self):
        """Test multiple cancel() calls are safe."""
        worker = BaseWorker()

        worker.cancel()
        worker.cancel()
        worker.cancel()

        assert worker._cancelled is True

    def test_cancel_reset_cycle(self):
        """Test cancel/reset cycle works correctly."""
        worker = BaseWorker()

        # Cycle 1
        worker.cancel()
        assert worker._check_cancellation() is True
        worker.reset_cancellation()
        assert worker._check_cancellation() is False

        # Cycle 2
        worker.cancel()
        assert worker._check_cancellation() is True
        worker.reset_cancellation()
        assert worker._check_cancellation() is False

    def test_validate_directory_with_unicode(self):
        """Test directory validation with unicode characters."""
        worker = BaseWorker()

        # Test with non-existent unicode path
        result = worker._validate_working_directory("/tmp/测试目录")

        # Should return False (doesn't exist)
        assert result is False

    @patch("asciidoc_artisan.workers.base_worker.subprocess.run")
    def test_execute_subprocess_empty_command_list(self, mock_run):
        """Test executing empty command list."""
        worker = BaseWorker()

        # Mock subprocess to raise IndexError for empty list
        mock_run.side_effect = IndexError("list index out of range")

        # Empty command list should raise error from subprocess
        with pytest.raises(IndexError):
            worker._execute_subprocess([])

    def test_build_kwargs_zero_timeout(self):
        """Test building kwargs with zero timeout."""
        worker = BaseWorker()

        kwargs = worker._build_subprocess_kwargs(timeout=0)

        assert kwargs["timeout"] == 0

    def test_build_kwargs_negative_timeout(self):
        """Test building kwargs with negative timeout."""
        worker = BaseWorker()

        kwargs = worker._build_subprocess_kwargs(timeout=-1)

        # Negative timeout accepted (will cause error in subprocess.run)
        assert kwargs["timeout"] == -1
