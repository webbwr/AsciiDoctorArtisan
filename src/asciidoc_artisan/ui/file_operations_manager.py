"""
File Operations Manager - Coordinates file open/save with format conversion.

Manages file operations by delegating to specialized handlers:
- FileOpenHandler: File dialogs, PDF/Pandoc/native loading
- FileSaveHandler: Save dialogs, AsciiDoc/HTML direct saves
- FormatConversionHelper: Pandoc integration, temp file management
- PathFormatUtils: Format detection, path resolution

Architecture:
- Thin coordination layer with delegation pattern
- Reentrancy guards prevent concurrent Pandoc operations
- Worker threads for format conversion (non-blocking UI)
- Large file optimization (streaming for 50MB+ files)

Format Support:
- Input: AsciiDoc, PDF, DOCX, Markdown, HTML, LaTeX, RST, Org, Textile
- Output: AsciiDoc, HTML, DOCX, PDF, Markdown, LaTeX
- PDF import via PyMuPDF text extraction
- DOCX/Markdown/HTML via Pandoc conversion

Key Features:
- Atomic file writes (prevents corruption)
- Windows-compatible dialogs
- Unsaved changes prompts
- Format auto-detection by extension
- AI-enhanced conversion support (Ollama)

Specifications:
- FR-001 to FR-010: File operations (New, Open, Save, Save As)
- FR-011: Multi-format support
- FR-012: PDF import
- FR-025 to FR-027: Pandoc integration
- NFR-011: Large file support (50MB+)

MA Compliance: Reduced from 865→306 lines via 4 class extractions (65% reduction).
"""

# === STANDARD LIBRARY IMPORTS ===
import logging  # For recording what the program does
from pathlib import Path  # Modern file path handling (better than strings)
from typing import TYPE_CHECKING, cast  # Type hints

# === QT FRAMEWORK IMPORTS ===
# === CORE IMPORTS (Constants and Utilities) ===
from asciidoc_artisan.ui.file_open_handler import FileOpenHandler, FileOpsContext
from asciidoc_artisan.ui.file_save_handler import EditorContext, FileSaveHandler
from asciidoc_artisan.ui.format_conversion_helper import (
    EditorContext as FormatEditorContext,
)
from asciidoc_artisan.ui.format_conversion_helper import (
    FormatConversionHelper,
)
from asciidoc_artisan.ui.path_format_utils import PathFormatUtils

# === TYPE CHECKING (Avoid Circular Imports) ===
if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

# === LOGGING SETUP ===
logger = logging.getLogger(__name__)


class FileOperationsManager:
    """
    File Operations Manager - Handles File Open/Save with Format Conversion.

    FOR BEGINNERS - WHAT IS THIS CLASS?:
    This class is like a "file translator" that can:
    - Open files in different formats and convert them to AsciiDoc
    - Save AsciiDoc files in different formats (Word, PDF, Markdown, HTML)
    - Handle large files (50MB+) without freezing the app
    - Work in the background (uses worker threads)

    KEY RESPONSIBILITIES:
    1. Open files with format conversion (open_file method)
    2. Save files in multiple formats (save_file_as_format method)
    3. PDF text extraction (using PyMuPDF library)
    4. Pandoc integration for format conversion
    5. Reentrancy guard to prevent concurrent operations

    WHY IT EXISTS:
    Before this class, all file operations were in main_window.py. This made
    main_window.py huge (1,700+ lines) and hard to maintain. By extracting
    file operations into this manager, we:
    - Reduced main_window.py by 67% (to 561 lines)
    - Made file operations testable independently
    - Separated concerns (main window doesn't need to know about Pandoc)

    USAGE:
    Called by main_window.py for all file operations:
        file_mgr = FileOperationsManager(self)
        file_mgr.open_file()  # Opens file with format conversion
        file_mgr.save_file_as_format("docx")  # Exports to Word

    PARAMETERS:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """
        Initialize File Operations Manager.

        WHAT THIS DOES:
        1. Stores reference to main editor window
        2. Sets up reentrancy guard (_is_processing_pandoc)
        3. Initializes pending file path storage
        4. Creates helper instances for format conversion

        PARAMETERS:
            editor: The main application window (AsciiDocEditor)

        CREATES:
            self.editor: Reference to main window
            self._is_processing_pandoc: Guard flag (prevents concurrent operations)
            self._pending_file_path: Stores file path during async operations
            self._format_helper: Format conversion helper (MA principle extraction)
        """
        # Store reference to main editor window
        self.editor = editor

        # Reentrancy guard - prevents concurrent Pandoc operations
        # If True, another operation is in progress (don't start a new one!)
        self._is_processing_pandoc = False

        # Storage for file path during async operations
        # When Pandoc worker finishes, we need to know which file we were working on
        self._pending_file_path: Path | None = None

        # Helper instances (MA principle: delegate logic to focused classes)
        # Use cast() to satisfy mypy - editor has all required protocol attributes
        self._format_helper = FormatConversionHelper(cast(FormatEditorContext, editor))
        self._save_handler = FileSaveHandler(cast(EditorContext, editor), PathFormatUtils)
        self._open_handler = FileOpenHandler(cast(FileOpsContext, self))

    def open_file(self) -> None:
        """Open file with format conversion support (delegates to open_handler)."""
        return self._open_handler.open_file()

    def save_file(self, save_as: bool = False) -> bool:
        """
        Save file with Windows-friendly dialog.

        MA principle: Reduced from 72→23 lines by extracting 4 helpers (68% reduction).

        Handles both simple AsciiDoc saves and export to other formats.
        Simple .adoc saves delegate to atomic file write.

        Args:
            save_as: If True, always show save dialog

        Returns:
            True if saved successfully, False otherwise
        """
        # Determine file path
        if save_as or not self.editor._current_file_path:
            # Show save dialog for Save As or new files
            result = self._show_save_dialog()
            if not result:
                return False
            file_path, format_type = result

            # Handle export to non-adoc formats
            if format_type != "adoc":
                return self._handle_export_format(file_path, format_type)
        else:
            # Regular save with existing path
            file_path = self._prepare_regular_save_path()

        # Execute atomic save and update state
        return self._execute_save_and_update(file_path)

    def _show_save_dialog(self) -> tuple[Path, str] | None:
        """Show save dialog and return selected path and format (delegates to save_handler)."""
        return self._save_handler.show_save_dialog()

    def _handle_export_format(self, file_path: Path, format_type: str) -> bool:
        """
        Handle export to non-adoc format.

        MA principle: Extracted from save_file (10 lines).

        Args:
            file_path: Target file path
            format_type: Format type (md, docx, html, pdf)

        Returns:
            True if export succeeded, False otherwise
        """
        use_ai_for_export = self.editor._settings_manager.get_ai_conversion_preference(self.editor._settings)

        logger.info(
            f"Calling _save_as_format_internal with "
            f"file_path={file_path}, format_type={format_type}, "
            f"use_ai={use_ai_for_export}"
        )
        return self.save_as_format_internal(file_path, format_type, use_ai_for_export)

    def _prepare_regular_save_path(self) -> Path:
        """Prepare file path for regular save operation (delegates to save_handler)."""
        return self._save_handler.prepare_regular_save_path()

    def _execute_save_and_update(self, file_path: Path) -> bool:
        """Execute atomic save and update editor state (delegates to save_handler)."""
        return self._save_handler.execute_save_and_update(file_path)

    def _save_as_adoc(self, file_path: Path, content: str) -> bool:
        """Save content as AsciiDoc format (delegates to save_handler)."""
        return self._save_handler.save_as_adoc(file_path, content)

    def _save_as_html(self, file_path: Path, content: str) -> bool:
        """Save content as HTML format (delegates to save_handler)."""
        return self._save_handler.save_as_html(file_path, content)

    def _determine_source_format(self) -> str:
        """Determine source format from current file extension (delegates to format_helper)."""
        return self._format_helper.determine_source_format()

    def _convert_asciidoc_to_html_temp(self, content: str) -> Path | None:
        """Convert AsciiDoc to HTML and save to temp file (delegates to format_helper)."""
        return self._format_helper.convert_asciidoc_to_html_temp(content)

    def _save_to_temp_file(self, content: str, source_format: str) -> Path | None:
        """Save content to temporary file for Pandoc processing (delegates to format_helper)."""
        return self._format_helper.save_to_temp_file(content, source_format)

    def _emit_pandoc_conversion(
        self,
        temp_source_file: Path,
        format_type: str,
        source_format: str,
        file_path: Path,
        use_ai: bool,
    ) -> None:
        """Emit Pandoc conversion request signal (delegates to format_helper)."""
        return self._format_helper.emit_pandoc_conversion(
            temp_source_file, format_type, source_format, file_path, use_ai
        )

    def save_as_format_internal(self, file_path: Path, format_type: str, use_ai: bool | None = None) -> bool:
        """
        Internal method to save file in specified format without showing dialog.

        Args:
            file_path: Target file path
            format_type: Target format (adoc, md, docx, pdf, html)
            use_ai: Whether to use AI conversion (None = use settings default)

        Returns:
            True if export started successfully, False otherwise

        MA principle: Reduced from 161→48 lines by extracting 6 helper methods.
        """
        logger.info(
            f"_save_as_format_internal called - file_path: {file_path}, format_type: {format_type}, use_ai: {use_ai}"
        )

        # Determine AI preference if not specified
        if use_ai is None:
            use_ai = self.editor._settings_manager.get_ai_conversion_preference(self.editor._settings)

        content = self.editor.editor.toPlainText()

        # Handle direct saves (no Pandoc needed)
        if format_type == "adoc":
            return self._save_as_adoc(file_path, content)

        if format_type == "html":
            return self._save_as_html(file_path, content)

        # For other formats, check Pandoc availability
        if not self.editor.ui_state_manager.check_pandoc_availability(f"Save as {format_type.upper()}"):
            return False

        # Determine source format and create temp file
        source_format = self._determine_source_format()
        temp_source_file = None

        if source_format == "asciidoc":
            temp_source_file = self._convert_asciidoc_to_html_temp(content)
            if temp_source_file is None:
                return False
            source_format = "html"
        else:
            temp_source_file = self._save_to_temp_file(content, source_format)
            if temp_source_file is None:
                return False

        # Emit Pandoc conversion request
        self._emit_pandoc_conversion(temp_source_file, format_type, source_format, file_path, use_ai)

        # Update state for ADOC format
        if format_type == "adoc":
            self.editor._current_file_path = file_path
            self.editor._settings.last_directory = str(file_path.parent)
            self.editor._unsaved_changes = False
            self.editor.status_manager.update_window_title()

        return True

    # Helper methods for file opening (delegate to open_handler)

    def _open_pdf_with_extraction(self, file_path: Path) -> None:
        """Import PDF file via text extraction (delegates to open_handler)."""
        return self._open_handler.open_pdf_with_extraction(file_path)

    def _open_with_pandoc_conversion(self, file_path: Path, suffix: str) -> None:
        """Open file with Pandoc format conversion (delegates to open_handler)."""
        return self._open_handler.open_with_pandoc_conversion(file_path, suffix)

    def _open_native_file(self, file_path: Path) -> None:
        """Open native AsciiDoc file with large file optimization (delegates to open_handler)."""
        return self._open_handler.open_native_file(file_path)

    # Helper methods for file saving (delegate to PathFormatUtils)

    def _determine_save_format(self, file_path: Path, selected_filter: str) -> tuple[str, Path]:
        """Determine save format and ensure file path has correct extension (delegates to PathFormatUtils)."""
        return PathFormatUtils.determine_save_format(file_path, selected_filter)

    def _get_format_from_filter_or_extension(self, selected_filter: str, file_path: Path) -> str:
        """Determine format type from filter string or file extension (delegates to PathFormatUtils)."""
        return PathFormatUtils.get_format_from_filter_or_extension(selected_filter, file_path)

    def _ensure_file_extension(self, file_path: Path, format_type: str) -> Path:
        """Add file extension if missing (delegates to PathFormatUtils)."""
        return PathFormatUtils.ensure_file_extension(file_path, format_type)
