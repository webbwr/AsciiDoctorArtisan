"""
Pandoc Result Handler - Handles Pandoc conversion results and errors.

Implements:
- Success result processing for imports and exports
- Error result processing with user-friendly messages
- State management for pending file operations

Extracted from main_window.py as part of Phase 6 refactoring to reduce
main window complexity and improve modularity.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer, Slot

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class PandocResultHandler:
    """Manages Pandoc conversion result and error handling.

    This class encapsulates logic for processing successful Pandoc conversions
    and handling conversion errors with user-friendly error messages.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the PandocResultHandler with a reference to the main editor."""
        self.editor = editor

    def _handle_file_load_request(self, result: str, pending_path: Path, context: str) -> None:
        """Handle file load request in main thread.

        Args:
            result: Converted content
            pending_path: Path to the file being loaded
            context: Context description
        """
        self.editor.file_load_manager.load_content_into_editor(result, pending_path)
        logger.info(f"Successfully converted {context}")
        QTimer.singleShot(100, self.editor.update_preview)

    @Slot(str, str)
    def handle_pandoc_result(self, result: str, context: str) -> None:
        """Handle successful Pandoc conversion result.

        Args:
            result: Converted content
            context: Context description of the conversion operation
        """
        self.editor.file_operations_manager._is_processing_pandoc = False
        self.editor._update_ui_state()

        # Delegate to ExportManager
        self.editor.export_manager.handle_pandoc_result(result, context)

        # Handle file import operations
        if self.editor.file_operations_manager._pending_file_path:
            # Capture variables and emit signal to load in main thread
            pending_path = self.editor.file_operations_manager._pending_file_path
            self.editor.file_operations_manager._pending_file_path = None

            # Emit signal to request file load in main thread
            self.editor.request_load_file_content.emit(result, pending_path, context)

    @Slot(str, str)
    def handle_pandoc_error_result(self, error: str, context: str) -> None:
        """Handle Pandoc conversion error result.

        Args:
            error: Error message from Pandoc
            context: Context description of the conversion operation
        """
        self.editor.file_operations_manager._is_processing_pandoc = False
        file_path = self.editor.file_operations_manager._pending_file_path
        self.editor.file_operations_manager._pending_file_path = None
        export_path = self.editor.export_manager.pending_export_path
        self.editor.export_manager.pending_export_path = None
        self.editor.export_manager.pending_export_format = None
        self.editor._update_ui_state()
        self.editor.status_bar.showMessage(f"Conversion failed: {context}")

        if export_path and "Exporting to" in context:

            if "PDF" in context and (
                "pdflatex" in error
                or "pdf-engine" in error
                or "No such file or directory" in error
            ):
                error_msg = (
                    f"Failed to export to PDF:\n\n"
                    f"Pandoc could not find a PDF engine on your system.\n\n"
                    f"Solution: Export to HTML instead\n"
                    f"1. File → Save As → Select 'HTML Files (*.html)'\n"
                    f"2. Open the HTML file in your browser\n"
                    f"3. Press Ctrl+P and select 'Save as PDF'\n\n"
                    f"Technical details:\n{error}"
                )
            else:
                error_msg = (
                    f"Failed to export to {export_path.suffix[1:].upper()}:\n{error}"
                )

            self.editor.status_manager.show_message(
                "critical", "Export Error", error_msg
            )
            return

        self.editor.editor.clear()
        self.editor.preview.setHtml(
            "<h3>Conversion Failed</h3><p>Unable to convert the document.</p>"
        )

        error_msg = f"{context} failed:\n\n{error}"
        if file_path:
            error_msg += f"\n\nFile: {file_path}"

        self.editor.status_manager.show_message(
            "critical", "Conversion Error", error_msg
        )
