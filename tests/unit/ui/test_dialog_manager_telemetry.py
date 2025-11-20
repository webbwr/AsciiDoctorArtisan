"""Extended tests for dialog_manager telemetry operations.

Covers previously untested code paths in DialogManager:
- Platform-specific file opening (_open_telemetry_file_editor)
- Directory change operations (_change_telemetry_directory)
- Error handling for telemetry operations

Targets 95%+ coverage for dialog_manager.py (currently 81%).
"""

import platform
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from PySide6.QtWidgets import QMainWindow, QMessageBox, QPlainTextEdit, QStatusBar, QTextBrowser


@pytest.fixture
def mock_telemetry_window(qapp):
    """Create a mock main window with telemetry configuration."""
    window = QMainWindow()

    # Settings
    window._settings = Mock()
    window._settings.telemetry_enabled = True
    window._settings.telemetry_session_id = "test-session-123"

    # UI components
    window.editor = Mock(spec=QPlainTextEdit)
    window.preview = Mock(spec=QTextBrowser)
    window.status_bar = QStatusBar()

    # Status manager
    window.status_manager = Mock()
    window.status_manager.show_message = Mock()

    # Telemetry collector
    window.telemetry_collector = Mock()
    window.telemetry_collector.data_dir = Path("/tmp/test_telemetry")
    window.telemetry_collector.telemetry_file = Path("/tmp/test_telemetry/telemetry.json")

    return window


@pytest.mark.unit
class TestTelemetryFileOpening:
    """Test suite for platform-specific telemetry file opening."""

    @patch("platform.system", return_value="Windows")
    @patch("subprocess.run")
    def test_open_telemetry_file_windows(self, mock_run, mock_system, mock_telemetry_window):
        """Test opening telemetry file on Windows with notepad."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        # Setup
        mock_run.return_value = Mock(stdout="", stderr="", returncode=0)
        manager = DialogManager(mock_telemetry_window)
        telemetry_file = Path("/tmp/test_telemetry/telemetry.json")

        # Execute
        manager._open_telemetry_file(telemetry_file)

        # Verify
        mock_run.assert_called_once_with(
            ["notepad", str(telemetry_file)],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.run")
    def test_open_telemetry_file_macos(self, mock_run, mock_system, mock_telemetry_window):
        """Test opening telemetry file on macOS with open command."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        # Setup
        mock_run.return_value = Mock(stdout="", stderr="", returncode=0)
        manager = DialogManager(mock_telemetry_window)
        telemetry_file = Path("/tmp/test_telemetry/telemetry.json")

        # Execute
        manager._open_telemetry_file(telemetry_file)

        # Verify
        mock_run.assert_called_once_with(
            ["open", str(telemetry_file)],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("platform.system", return_value="Linux")
    @patch("subprocess.run")
    @patch("builtins.open", create=True)
    def test_open_telemetry_file_linux_xdg(self, mock_open_file, mock_run, mock_system, mock_telemetry_window):
        """Test opening telemetry file on Linux with xdg-open."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        # Setup - not WSL
        mock_file_handle = Mock()
        mock_file_handle.read.return_value = "Linux version 5.0.0"
        mock_file_handle.__enter__ = Mock(return_value=mock_file_handle)
        mock_file_handle.__exit__ = Mock(return_value=False)
        mock_open_file.return_value = mock_file_handle

        mock_run.return_value = Mock(stdout="", stderr="", returncode=0)
        manager = DialogManager(mock_telemetry_window)
        telemetry_file = Path("/tmp/test_telemetry/telemetry.json")

        # Execute
        manager._open_telemetry_file(telemetry_file)

        # Verify xdg-open was called
        mock_run.assert_called_with(
            ["xdg-open", str(telemetry_file)],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("platform.system", return_value="Linux")
    @patch("subprocess.run")
    @patch("builtins.open", create=True)
    def test_open_telemetry_file_wsl(self, mock_open_file, mock_run, mock_system, mock_telemetry_window):
        """Test opening telemetry file on WSL with Windows notepad."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        # Setup - WSL detected
        mock_file_handle = Mock()
        mock_file_handle.read.return_value = "Linux version microsoft-standard-WSL2"
        mock_file_handle.__enter__ = Mock(return_value=mock_file_handle)
        mock_file_handle.__exit__ = Mock(return_value=False)
        mock_open_file.return_value = mock_file_handle

        # Mock wslpath and notepad.exe calls
        def run_side_effect(*args, **kwargs):
            cmd = args[0]
            if cmd[0] == "wslpath":
                return Mock(stdout="C:\\\\tmp\\\\telemetry.json\\n", stderr="", returncode=0)
            elif "notepad.exe" in cmd[0]:
                return Mock(stdout="", stderr="", returncode=0)
            return Mock(stdout="", stderr="", returncode=0)

        mock_run.side_effect = run_side_effect
        manager = DialogManager(mock_telemetry_window)
        telemetry_file = Path("/tmp/test_telemetry/telemetry.json")

        # Execute
        manager._open_telemetry_file(telemetry_file)

        # Verify wslpath was called
        assert any(
            call[0][0][0] == "wslpath" for call in mock_run.call_args_list
        ), "wslpath should be called for WSL path conversion"

    @patch("platform.system", return_value="Linux")
    @patch("subprocess.run", side_effect=FileNotFoundError("xdg-open not found"))
    @patch("builtins.open", create=True)
    def test_open_telemetry_file_linux_fallback(self, mock_open_file, mock_run, mock_system, mock_telemetry_window):
        """Test opening telemetry file on Linux with less fallback."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        # Setup - not WSL, xdg-open fails
        mock_file_handle = Mock()
        mock_file_handle.read.return_value = "Linux version 5.0.0"
        mock_file_handle.__enter__ = Mock(return_value=mock_file_handle)
        mock_file_handle.__exit__ = Mock(return_value=False)
        mock_open_file.return_value = mock_file_handle

        manager = DialogManager(mock_telemetry_window)
        telemetry_file = Path("/tmp/test_telemetry/telemetry.json")

        # Execute
        manager._open_telemetry_file(telemetry_file)

        # Verify fallback to less was attempted
        assert mock_run.call_count >= 2, "Should attempt xdg-open then fallback"

    @patch("platform.system", return_value="Windows")
    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "notepad", stderr="File not found"))
    @patch("PySide6.QtWidgets.QMessageBox.warning")
    def test_open_telemetry_file_error_handling(self, mock_warning, mock_run, mock_system, mock_telemetry_window):
        """Test error handling when file opening fails."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        # Setup
        manager = DialogManager(mock_telemetry_window)
        telemetry_file = Path("/tmp/test_telemetry/telemetry.json")

        # Execute
        manager._open_telemetry_file(telemetry_file)

        # Verify error message shown
        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0]
        assert "Open File Failed" in call_args

    @patch("platform.system", return_value="Windows")
    @patch("subprocess.run", side_effect=Exception("Unexpected error"))
    @patch("PySide6.QtWidgets.QMessageBox.warning")
    def test_open_telemetry_file_unexpected_error(self, mock_warning, mock_run, mock_system, mock_telemetry_window):
        """Test handling of unexpected errors during file opening."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        # Setup
        manager = DialogManager(mock_telemetry_window)
        telemetry_file = Path("/tmp/test_telemetry/telemetry.json")

        # Execute
        manager._open_telemetry_file(telemetry_file)

        # Verify error message shown
        mock_warning.assert_called_once()
        call_args = mock_warning.call_args[0]
        assert "Open File Failed" in call_args
        assert "Unexpected error" in str(mock_warning.call_args)


@pytest.mark.unit
class TestTelemetryDirectoryChange:
    """Test suite for telemetry directory change operations."""

    @patch("shutil.copy2")
    @patch("PySide6.QtWidgets.QMessageBox.information")
    def test_change_telemetry_directory_success(self, mock_info, mock_copy, mock_telemetry_window, tmp_path):
        """Test successful telemetry directory change."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        # Setup
        manager = DialogManager(mock_telemetry_window)
        old_file = tmp_path / "old" / "telemetry.json"
        old_file.parent.mkdir()
        old_file.write_text('{"test": "data"}')

        new_dir = tmp_path / "new"

        mock_msg_box = Mock(spec=QMessageBox)
        mock_msg_box.done = Mock()

        # Execute
        manager._change_telemetry_directory(old_file, tmp_path / "old", mock_msg_box, new_dir)

        # Verify
        assert new_dir.exists(), "New directory should be created"
        mock_copy.assert_called_once()
        mock_info.assert_called_once()
        mock_msg_box.done.assert_called_once()

    @patch("PySide6.QtWidgets.QMessageBox.information")
    def test_change_telemetry_directory_no_existing_file(self, mock_info, mock_telemetry_window, tmp_path):
        """Test directory change when no existing telemetry file."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        # Setup
        manager = DialogManager(mock_telemetry_window)
        new_dir = tmp_path / "new"

        mock_msg_box = Mock(spec=QMessageBox)
        mock_msg_box.done = Mock()

        # Execute - no existing file
        manager._change_telemetry_directory(None, tmp_path / "old", mock_msg_box, new_dir)

        # Verify
        assert new_dir.exists(), "New directory should be created"
        mock_info.assert_called_once()
        mock_msg_box.done.assert_called_once()

    @patch("PySide6.QtWidgets.QMessageBox.critical")
    def test_change_telemetry_directory_error(self, mock_critical, mock_telemetry_window, tmp_path):
        """Test error handling during directory change."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        # Setup
        manager = DialogManager(mock_telemetry_window)
        old_file = tmp_path / "old" / "telemetry.json"

        mock_msg_box = Mock(spec=QMessageBox)

        # Execute with invalid path (should raise exception)
        invalid_dir = Path("/invalid/readonly/path/that/cannot/be/created")
        manager._change_telemetry_directory(old_file, tmp_path / "old", mock_msg_box, invalid_dir)

        # Verify error handling
        mock_critical.assert_called_once()
        call_args = str(mock_critical.call_args)
        assert "Change Directory Failed" in call_args

    @patch("PySide6.QtWidgets.QMessageBox.information")
    def test_change_telemetry_directory_updates_collector(self, mock_info, mock_telemetry_window, tmp_path):
        """Test that telemetry collector is updated with new directory."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager

        # Setup
        manager = DialogManager(mock_telemetry_window)
        new_dir = tmp_path / "new"

        mock_msg_box = Mock(spec=QMessageBox)
        mock_msg_box.done = Mock()

        # Execute
        manager._change_telemetry_directory(None, tmp_path / "old", mock_msg_box, new_dir)

        # Verify telemetry_collector was updated
        assert mock_telemetry_window.telemetry_collector.data_dir == new_dir
        expected_file = new_dir / "telemetry.json"
        assert mock_telemetry_window.telemetry_collector.telemetry_file == expected_file
