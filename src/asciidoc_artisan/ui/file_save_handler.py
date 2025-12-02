"""
File Save Handler - Handles file save operations and dialog management.

Extracted from FileOperationsManager to reduce class size (MA principle).
Manages save dialogs, format selection, and direct save operations.
"""

import io
import logging
import platform
from pathlib import Path
from typing import Protocol, cast

from PySide6.QtWidgets import QFileDialog, QWidget

from asciidoc_artisan.core import (
    DEFAULT_FILENAME,
    ERR_ASCIIDOC_NOT_INITIALIZED,
    MSG_SAVED_ASCIIDOC,
    MSG_SAVED_HTML,
    SUPPORTED_SAVE_FILTER,
    atomic_save_text,
)

logger = logging.getLogger(__name__)


class EditorContext(Protocol):
    """Protocol for editor context access (avoid circular imports)."""

    _current_file_path: Path | None
    _settings: object
    _asciidoc_api: object | None
    status_manager: object
    status_bar: object
    editor: object
    _unsaved_changes: bool

    def __getattr__(self, name: str) -> object:  # pragma: no cover
        """Allow access to any editor attribute."""
        ...


class PathFormatResolver(Protocol):
    """Protocol for path/format resolution."""

    @staticmethod
    def determine_save_format(file_path: Path, selected_filter: str) -> tuple[str, Path]:  # pragma: no cover
        """Determine save format and correct file path."""
        ...


class FileSaveHandler:
    """
    File save operations handler.

    This class was extracted from FileOperationsManager to reduce class size
    per MA principle (689→~538 lines).

    Handles:
    - Save dialog presentation and format selection
    - Regular save path preparation
    - Atomic save execution and state updates
    - Direct AsciiDoc and HTML saves
    """

    def __init__(self, editor: EditorContext, path_resolver: PathFormatResolver) -> None:
        """
        Initialize file save handler.

        Args:
            editor: Editor context for accessing state and UI
            path_resolver: Path format resolver (PathFormatUtils)
        """
        self.editor = editor
        self.path_resolver = path_resolver

    def show_save_dialog(self) -> tuple[Path, str] | None:
        """
        Show save dialog and return selected path and format.

        Returns:
            Tuple of (file_path, format_type) if user selected, None if cancelled

        MA principle: Extracted from save_file (19 lines).
        """
        suggested_name = self.editor._current_file_path.name if self.editor._current_file_path else DEFAULT_FILENAME
        suggested_path = Path(self.editor._settings.last_directory) / suggested_name

        file_path_str, selected_filter = QFileDialog.getSaveFileName(
            cast(QWidget, self.editor),
            "Save File",
            str(suggested_path),
            SUPPORTED_SAVE_FILTER,
            options=(
                QFileDialog.Option.DontUseNativeDialog if platform.system() != "Windows" else QFileDialog.Option(0)
            ),
        )

        if not file_path_str:
            return None

        file_path = Path(file_path_str)
        logger.info(f"Save As dialog - file_path: {file_path}, selected_filter: {selected_filter}")

        format_type, file_path = self.path_resolver.determine_save_format(file_path, selected_filter)
        return file_path, format_type

    def prepare_regular_save_path(self) -> Path:
        """
        Prepare file path for regular save operation.

        Returns:
            File path with .adoc extension

        MA principle: Extracted from save_file (8 lines).
        """
        file_path = self.editor._current_file_path
        assert file_path is not None, "file_path should not be None in save mode"

        if file_path.suffix.lower() not in [".adoc", ".asciidoc"]:
            file_path = file_path.with_suffix(".adoc")
            logger.info(f"Converting save format from {self.editor._current_file_path.suffix} to .adoc")

        return file_path

    def execute_save_and_update(self, file_path: Path) -> bool:
        """
        Execute atomic save and update editor state.

        Args:
            file_path: Target file path

        Returns:
            True if saved successfully, False otherwise

        MA principle: Extracted from save_file (17 lines).
        """
        content = self.editor.editor.toPlainText()

        if atomic_save_text(file_path, content, encoding="utf-8"):
            self.editor._current_file_path = file_path
            self.editor._settings.last_directory = str(file_path.parent)
            self.editor._unsaved_changes = False
            self.editor.status_manager.update_window_title()
            self.editor.status_bar.showMessage(MSG_SAVED_ASCIIDOC.format(file_path))
            logger.info(f"Saved file: {file_path}")
            return True
        else:
            self.editor.status_manager.show_message(
                "critical",
                "Save Error",
                f"Failed to save file: {file_path}\nThe file may be in use or the directory may be read-only.",
            )
            return False

    def save_as_adoc(self, file_path: Path, content: str) -> bool:
        """
        Save content as AsciiDoc format.

        Args:
            file_path: Target file path
            content: Content to save

        Returns:
            True if saved successfully, False otherwise

        MA principle: Extracted from save_as_format_internal (14 lines).
        """
        if atomic_save_text(file_path, content, encoding="utf-8"):
            self.editor._current_file_path = file_path
            self.editor._settings.last_directory = str(file_path.parent)
            self.editor._unsaved_changes = False
            self.editor.status_manager.update_window_title()
            self.editor.status_bar.showMessage(MSG_SAVED_ASCIIDOC.format(file_path))
            return True
        else:
            self.editor.status_manager.show_message(
                "critical", "Save Error", f"Failed to save AsciiDoc file: {file_path}"
            )
            return False

    def save_as_html(self, file_path: Path, content: str) -> bool:
        """
        Save content as HTML format.

        Args:
            file_path: Target file path
            content: AsciiDoc content to convert and save

        Returns:
            True if saved successfully, False otherwise

        MA principle: Extracted from save_as_format_internal (20 lines).
        """
        self.editor.status_bar.showMessage("Saving as HTML...")
        try:
            if self.editor._asciidoc_api is None:
                raise RuntimeError(ERR_ASCIIDOC_NOT_INITIALIZED)

            infile = io.StringIO(content)
            outfile = io.StringIO()
            self.editor._asciidoc_api.execute(infile, outfile, backend="html5")
            html_content = outfile.getvalue()

            if atomic_save_text(file_path, html_content, encoding="utf-8"):
                self.editor.status_bar.showMessage(MSG_SAVED_HTML.format(file_path))
                logger.info(f"Successfully saved as HTML: {file_path}")
                return True
            else:
                raise OSError(f"Atomic save failed for {file_path}")
        except Exception as e:
            logger.exception(f"Failed to save HTML file: {e}")
            self.editor.status_manager.show_message("critical", "Save Error", f"Failed to save HTML file:\n{e}")
            return False
