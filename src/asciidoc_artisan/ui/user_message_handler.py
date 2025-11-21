"""
User Message Handler - Handles user messages, dialogs, and status bar feedback.

Extracted from StatusManager to reduce class size (MA principle).
Handles message boxes, status bar messages, and save prompts.
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QMessageBox

if TYPE_CHECKING:  # pragma: no cover
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class UserMessageHandler:
    """
    Handles user messages, dialogs, and status bar feedback.

    This class was extracted from StatusManager to reduce class size
    per MA principle (363→~296 lines).

    Handles:
    - Message dialogs (info, warning, critical)
    - Status bar messages
    - Save prompts before actions
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """
        Initialize the message handler.

        Args:
            editor: Reference to the main AsciiDocEditor window
        """
        self.editor = editor

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
        logger.info(f"[STATUS_BAR] Attempting to show: '{message}' (timeout={timeout}ms)")
        if not hasattr(self.editor, "status_bar") or self.editor.status_bar is None:
            logger.error("[STATUS_BAR] ERROR: status_bar not found or is None!")
            return
        logger.info("[STATUS_BAR] status_bar exists, calling showMessage()")
        self.editor.status_bar.showMessage(message, timeout)
        logger.info("[STATUS_BAR] showMessage() completed, checking current message...")
        current_msg = self.editor.status_bar.currentMessage()
        logger.info(f"[STATUS_BAR] Current message in status bar: '{current_msg}'")

    def prompt_save_before_action(self, action: str) -> bool:
        """Prompt user to save unsaved changes before an action.

        Args:
            action: Description of the action about to be performed

        Returns:
            True if user wants to proceed, False if cancelled
        """
        import os

        # Skip prompts in test environment to prevent blocking
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return True

        if not self.editor._unsaved_changes:
            return True

        reply = QMessageBox.question(
            self.editor,
            "Unsaved Changes",
            f"You have unsaved changes. Save before {action}?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.editor.save_file()  # type: ignore[no-any-return]  # save_file returns bool but QMessageBox comparison typed as Any
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False
