"""
Telemetry Dialog Handler - Handles telemetry status and file operations.

Extracted from DialogManager to reduce class size (MA principle).
Handles telemetry file operations, directory management, and status display.

MA principle: Reduced from 495→~300 lines by extracting platform_file_opener.py.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFileDialog, QMessageBox

from asciidoc_artisan.ui.platform_file_opener import PlatformFileOpener

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class TelemetryDialogHandler:
    """
    Handler for telemetry-related dialogs and file operations.

    This class was extracted from DialogManager to reduce class size per MA principle.

    Handles:
    - Telemetry file opening (cross-platform)
    - Telemetry directory management
    - Telemetry status display
    - Platform-specific file operations (Windows, macOS, WSL, Linux)
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize TelemetryDialogHandler with reference to main editor."""
        self.editor = editor
        self._file_opener = PlatformFileOpener(parent_widget=editor)

    def _open_telemetry_file(self, telemetry_file: "Path") -> None:
        """
        Open telemetry file in default application.

        Delegated to PlatformFileOpener per MA principle.

        Args:
            telemetry_file: Path to telemetry file to open
        """
        self._file_opener.open_file(telemetry_file)

    def _select_telemetry_directory(self, telemetry_dir: "Path | None") -> "Path | None":
        """
        Show directory selection dialog for telemetry.

        MA principle: Extracted from _change_telemetry_directory (10 lines).

        Args:
            telemetry_dir: Current telemetry directory

        Returns:
            Selected directory path or None if cancelled
        """
        new_dir = QFileDialog.getExistingDirectory(
            self.editor,
            "Select Telemetry Directory",
            str(telemetry_dir) if telemetry_dir else str(Path.home()),
            QFileDialog.Option.ShowDirsOnly,
        )

        if not new_dir:
            logger.info("User cancelled directory selection")
            return None

        new_dir_path = Path(new_dir)
        logger.info(f"User selected new directory: {new_dir_path}")
        return new_dir_path

    def _confirm_directory_change(self, new_dir_path: "Path") -> bool:
        """
        Show confirmation dialog for directory change.

        MA principle: Extracted from _change_telemetry_directory (10 lines).

        Args:
            new_dir_path: New directory path

        Returns:
            True if user confirmed, False otherwise
        """
        reply = QMessageBox.question(
            self.editor,
            "Confirm Directory Change",
            f"Change telemetry directory to:\n{new_dir_path}\n\nThis will move all telemetry data to the new location.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            logger.info("User cancelled directory change confirmation")
            return False

        return True

    def _move_telemetry_data(self, telemetry_file: "Path | None", new_dir_path: "Path") -> None:
        """
        Move telemetry data to new directory and update collector.

        MA principle: Extracted from _change_telemetry_directory (15 lines).

        Args:
            telemetry_file: Current telemetry file path
            new_dir_path: New directory path

        Raises:
            Exception: If file move or directory creation fails
        """
        # Create new directory if it doesn't exist
        new_dir_path.mkdir(parents=True, exist_ok=True)

        # Move existing telemetry file if it exists
        if telemetry_file and telemetry_file.exists():
            new_file_path = new_dir_path / "telemetry.toon"
            import shutil

            shutil.copy2(telemetry_file, new_file_path)
            logger.info(f"Copied telemetry file to: {new_file_path}")

        # Update telemetry collector
        self.editor.telemetry_collector.data_dir = new_dir_path
        self.editor.telemetry_collector.telemetry_file = new_dir_path / "telemetry.toon"

        logger.info("Telemetry directory changed successfully")

    def _show_directory_change_success(self, new_dir_path: "Path", msg_box: QMessageBox) -> None:
        """
        Show success message and reopen telemetry status.

        MA principle: Extracted from _change_telemetry_directory (8 lines).

        Args:
            new_dir_path: New directory path
            msg_box: Parent message box to close
        """
        QMessageBox.information(
            self.editor,
            "Directory Changed",
            f"Telemetry directory changed to:\n{new_dir_path}\n\nPrevious data has been copied to the new location.",
        )

        # Close the dialog and reopen to show updated info
        msg_box.done(QMessageBox.StandardButton.Ok)
        self.show_telemetry_status()

    def _change_telemetry_directory(
        self, telemetry_file: "Path | None", telemetry_dir: "Path | None", msg_box: QMessageBox
    ) -> None:
        """
        Allow user to select a new telemetry directory.

        MA principle: Reduced from 80→28 lines by extracting 4 dialog/operation helpers (65% reduction).

        Args:
            telemetry_file: Current telemetry file path
            telemetry_dir: Current telemetry directory
            msg_box: Parent message box (for closing/reopening)
        """
        logger.info("User requested to change telemetry directory")

        # Show directory selection dialog
        new_dir_path = self._select_telemetry_directory(telemetry_dir)
        if not new_dir_path:
            return

        # Confirm change
        if not self._confirm_directory_change(new_dir_path):
            return

        try:
            # Move data and update collector
            self._move_telemetry_data(telemetry_file, new_dir_path)

            # Show success and reopen dialog
            self._show_directory_change_success(new_dir_path, msg_box)

        except Exception as e:
            error_msg = f"Failed to change directory: {type(e).__name__}: {e}"
            logger.error(error_msg, exc_info=True)
            QMessageBox.critical(
                self.editor,
                "Change Directory Failed",
                f"Could not change telemetry directory:\n{str(e)}",
            )

    def _get_telemetry_file_info(self) -> tuple["Path | None", "Path | None"]:
        """
        Get telemetry file and directory paths.

        MA principle: Extracted from show_telemetry_status (7 lines).

        Returns:
            Tuple of (telemetry_file, telemetry_dir) or (None, None)
        """
        if hasattr(self.editor, "telemetry_collector"):
            telemetry_file = self.editor.telemetry_collector.telemetry_file
            return telemetry_file, telemetry_file.parent
        return None, None

    def _build_enabled_status_message(self, telemetry_file: "Path | None", telemetry_dir: "Path | None") -> str:
        """
        Build status message for enabled telemetry.

        MA principle: Extracted from show_telemetry_status (32 lines).

        Args:
            telemetry_file: Telemetry file path
            telemetry_dir: Telemetry directory path

        Returns:
            Formatted status message string
        """
        status = "✅ Telemetry: Enabled\n"

        # Show session ID
        if self.editor._settings.telemetry_session_id:
            session_id = self.editor._settings.telemetry_session_id
            status += f"Session ID: {session_id}\n\n"
        else:
            status += "⚠️ No session ID generated yet\n\n"

        # Show storage location
        if telemetry_file:
            status += "Storage Location:\n"
            status += f"  File: {telemetry_file}\n"
            status += f"  Directory: {telemetry_dir}\n\n"

        # Data collection info
        status += "Data Collected:\n"
        status += "• Application version and startup/shutdown times\n"
        status += "• Feature usage (e.g., export formats, AI chat)\n"
        status += "• Performance metrics (document size, render time)\n"
        status += "• Error events and stack traces\n\n"

        status += "Privacy:\n"
        status += "• No document content is collected\n"
        status += "• No personal information is collected\n"
        status += "• Data is stored locally only\n"
        status += "• No data is sent to external servers\n\n"

        status += "To disable telemetry:\n"
        status += "Go to Tools → Telemetry (toggle off)\n"

        return status

    def _build_disabled_status_message(self, telemetry_file: "Path | None", telemetry_dir: "Path | None") -> str:
        """
        Build status message for disabled telemetry.

        MA principle: Extracted from show_telemetry_status (24 lines).

        Args:
            telemetry_file: Telemetry file path
            telemetry_dir: Telemetry directory path

        Returns:
            Formatted status message string
        """
        status = "⚠️ Telemetry: Disabled\n\n"

        # Show storage location even when disabled
        if telemetry_file:
            status += "Storage Location:\n"
            status += f"  File: {telemetry_file}\n"
            status += f"  Directory: {telemetry_dir}\n\n"

        status += "Telemetry helps improve the application by collecting:\n"
        status += "• Anonymous usage statistics\n"
        status += "• Performance metrics\n"
        status += "• Error reports\n\n"

        status += "Privacy guarantees:\n"
        status += "• No document content is collected\n"
        status += "• No personal information is collected\n"
        status += "• Data is stored locally only\n"
        status += "• No data is sent to external servers\n\n"

        status += "To enable telemetry:\n"
        status += "Go to Tools → Telemetry (toggle on)\n"

        return status

    def _create_telemetry_status_dialog(
        self, status: str, telemetry_file: "Path | None", telemetry_dir: "Path | None"
    ) -> None:
        """
        Create and display telemetry status dialog with action buttons.

        MA principle: Extracted from show_telemetry_status (20 lines).

        Args:
            status: Formatted status message
            telemetry_file: Telemetry file path
            telemetry_dir: Telemetry directory path
        """
        msg_box = QMessageBox(self.editor)
        msg_box.setWindowTitle("Telemetry Status")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(status)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Add "Open File" button if telemetry file exists
        if telemetry_file and telemetry_file.exists():
            open_file_button = msg_box.addButton("Open File", QMessageBox.ButtonRole.ActionRole)
            open_file_button.clicked.connect(lambda: self._open_telemetry_file(telemetry_file))

        # Add "Change Directory" button
        change_dir_button = msg_box.addButton("Change Directory", QMessageBox.ButtonRole.ActionRole)
        change_dir_button.clicked.connect(
            lambda: self._change_telemetry_directory(telemetry_file, telemetry_dir, msg_box)
        )

        msg_box.exec()

    def show_telemetry_status(self) -> None:
        """
        Show telemetry configuration and data collection status.

        MA principle: Reduced from 86→18 lines by extracting 4 message-building helpers.
        """
        # Get file information
        telemetry_file, telemetry_dir = self._get_telemetry_file_info()

        # Build status message
        status = "Telemetry Status:\n\n"
        if self.editor._settings.telemetry_enabled:
            status += self._build_enabled_status_message(telemetry_file, telemetry_dir)
        else:
            status += self._build_disabled_status_message(telemetry_file, telemetry_dir)

        # Create and show dialog
        self._create_telemetry_status_dialog(status, telemetry_file, telemetry_dir)
