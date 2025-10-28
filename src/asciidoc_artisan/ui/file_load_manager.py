"""
File Load Manager - Handles file loading progress and content loading.

Implements:
- Content loading into editor with lazy loading for large files
- File load progress tracking with visual progress dialog
- Large file optimization

Extracted from main_window.py as part of Phase 6 refactoring to reduce
main window complexity and improve modularity.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QProgressDialog

from asciidoc_artisan.core import LARGE_FILE_THRESHOLD_BYTES, MSG_LOADING_LARGE_FILE

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class FileLoadManager:
    """Manages file loading operations with progress tracking and optimization.

    This class encapsulates logic for loading file content into the editor,
    handling progress updates, and optimizing for large files.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the FileLoadManager with a reference to the main editor."""
        self.editor = editor

    def load_content_into_editor(self, content: str, file_path: Path) -> None:
        """Load content into editor with lazy loading for large files.

        Args:
            content: File content to load
            file_path: Path to the file being loaded
        """
        self.editor._is_opening_file = True
        try:
            # Disable preview updates temporarily for large files
            content_size = len(content)
            is_large_file = content_size > LARGE_FILE_THRESHOLD_BYTES

            if is_large_file:
                logger.info(MSG_LOADING_LARGE_FILE.format(content_size / 1024))

            # QPlainTextEdit handles large documents efficiently with internal lazy loading
            # It only renders visible blocks, so setPlainText is still fast
            self.editor.editor.setPlainText(content)
            self.editor._current_file_path = file_path
            self.editor._unsaved_changes = False
            self.editor.status_manager.update_window_title()

            # Update document metrics after loading content
            self.editor.status_manager.update_document_metrics()

            if file_path.suffix.lower() in [
                ".md",
                ".markdown",
                ".docx",
                ".html",
                ".htm",
                ".tex",
                ".rst",
                ".org",
                ".textile",
            ]:
                self.editor.status_bar.showMessage(
                    f"Converted and opened: {file_path} → AsciiDoc"
                )
            else:
                self.editor.status_bar.showMessage(f"Opened: {file_path}")

            # Trigger preview update (will be optimized based on file size)
            self.editor.update_preview()

            logger.info(f"Loaded content into editor: {file_path}")
        finally:
            self.editor._is_opening_file = False

    @Slot(int, str)
    def on_file_load_progress(self, percentage: int, message: str) -> None:
        """Handle file loading progress updates with visual progress dialog.

        Args:
            percentage: Load progress percentage (0-100)
            message: Progress message to display
        """
        # Create progress dialog on first progress update
        if percentage > 0 and percentage < 100:
            if self.editor._progress_dialog is None:
                self.editor._progress_dialog = QProgressDialog(
                    "Loading file...", "Cancel", 0, 100, self.editor
                )
                self.editor._progress_dialog.setWindowTitle("Loading")
                self.editor._progress_dialog.setWindowModality(
                    Qt.WindowModality.WindowModal
                )
                self.editor._progress_dialog.setMinimumDuration(500)  # Show after 500ms
                self.editor._progress_dialog.setCancelButton(None)  # No cancel button
                self.editor._progress_dialog.setAutoClose(True)
                self.editor._progress_dialog.setAutoReset(True)

            self.editor._progress_dialog.setValue(percentage)
            self.editor._progress_dialog.setLabelText(message)
            logger.debug(f"File load progress: {percentage}% - {message}")

        # Close and cleanup on completion
        elif percentage >= 100:
            if self.editor._progress_dialog is not None:
                self.editor._progress_dialog.setValue(100)
                self.editor._progress_dialog.close()
                self.editor._progress_dialog = None
            self.editor.status_bar.showMessage(message, 3000)
            logger.debug(f"File load complete: {message}")

        # Show in status bar for initial progress
        else:
            self.editor.status_bar.showMessage(message, 2000)
