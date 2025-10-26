"""
Status Manager - Handles status bar and UI feedback for AsciiDoc Artisan.

Implements:
- FR-045: Status bar with contextual messages
- FR-051: Window title (filename with unsaved indicator)

This module manages status messages, window titles, and user notifications,
extracted from main_window.py as part of Phase 2 architectural refactoring.

The StatusManager provides centralized UI feedback management.
"""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QMessageBox

from asciidoc_artisan.core import APP_NAME, DEFAULT_FILENAME

if TYPE_CHECKING:

    from .main_window import AsciiDocEditor


class StatusManager:
    """Manages status display and UI feedback for AsciiDoc Artisan.

    This class encapsulates all status bar, window title, and message dialog
    functionality.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the StatusManager with a reference to the main editor."""
        self.editor = editor

    def update_window_title(self) -> None:
        """Update the window title based on current file and save status."""
        title = APP_NAME

        if self.editor._current_file_path:
            title = f"{APP_NAME} - {self.editor._current_file_path.name}"
        else:
            title = f"{APP_NAME} - {DEFAULT_FILENAME}"

        if self.editor._unsaved_changes:
            title += "*"

        self.editor.setWindowTitle(title)

    def show_message(self, level: str, title: str, text: str) -> None:
        """Show a message dialog to the user.

        Args:
            level: Message level ('info', 'warning', 'critical')
            title: Dialog window title
            text: Message text to display
        """
        icon_map = {
            "info": QMessageBox.Icon.Information,
            "warning": QMessageBox.Icon.Warning,
            "critical": QMessageBox.Icon.Critical,
        }

        msg = QMessageBox(self.editor)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon_map.get(level, QMessageBox.Icon.Information))
        msg.exec()

    def show_status(self, message: str, timeout: int = 0) -> None:
        """Show a message in the status bar.

        Args:
            message: Status message to display
            timeout: Duration in milliseconds (0 = permanent)
        """
        self.editor.status_bar.showMessage(message, timeout)

    def prompt_save_before_action(self, action: str) -> bool:
        """Prompt user to save unsaved changes before an action.

        Args:
            action: Description of the action about to be performed

        Returns:
            True if user wants to proceed, False if cancelled
        """
        if not self.editor._unsaved_changes:
            return True

        reply = QMessageBox.question(
            self.editor,
            "Unsaved Changes",
            f"You have unsaved changes. Save before {action}?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.editor.save_file()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False
