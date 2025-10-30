"""
===============================================================================
FILE OPERATIONS MANAGER - File Open/Save with Format Conversion
===============================================================================

FILE PURPOSE:
This file manages all file operations: opening, saving, importing, and
exporting files in different formats (AsciiDoc, Markdown, Word, PDF, HTML).

WHAT THIS FILE DOES:
1. Opens files with automatic format conversion (PDF → AsciiDoc, DOCX → AsciiDoc)
2. Saves files in multiple formats (AsciiDoc, Markdown, Word, PDF, HTML)
3. Integrates with Pandoc for format conversion
4. Uses worker threads for heavy operations (doesn't freeze UI)
5. Handles large files efficiently (streaming for 50MB+ files)

FOR BEGINNERS - WHAT ARE FILE OPERATIONS?:
File operations are actions involving files on your computer:
- Open: Read a file from disk into the editor
- Save: Write the editor content back to disk
- Import: Convert one format to another (PDF → AsciiDoc)
- Export: Save in a different format (AsciiDoc → Word)

ANALOGY:
Think of a translator app:
- Open: Read a document in English
- Import: Translate Japanese document to English (PDF → AsciiDoc)
- Save: Save your English document
- Export: Translate your English to Spanish and save (AsciiDoc → Word)

WHY THIS FILE WAS EXTRACTED:
Before v1.5.0, all this code was in main_window.py (making it 1,700+ lines!).
We extracted file operations to:
- Make main_window.py smaller and easier to understand (now 561 lines)
- Group related functionality together (Single Responsibility Principle)
- Make testing easier (can test file operations separately)
- Reduce coupling (main window doesn't need to know about Pandoc details)

KEY CONCEPTS:

1. FORMAT CONVERSION:
   - PDF → AsciiDoc: Extract text from PDF using PyMuPDF (fast!)
   - DOCX/MD/HTML → AsciiDoc: Use Pandoc to convert
   - AsciiDoc → DOCX/MD/HTML/PDF: Use Pandoc to export

2. WORKER THREADS:
   - File conversion is slow (2-10 seconds for large files)
   - We use PandocWorker (background thread) so UI stays responsive
   - User can cancel long operations

3. LARGE FILE HANDLING:
   - Files over 1MB (LARGE_FILE_THRESHOLD_BYTES) are handled specially
   - We stream data instead of loading everything at once
   - Prevents memory crashes on 50MB+ files

4. REENTRANCY GUARDS:
   - _is_processing_pandoc flag prevents concurrent operations
   - Can't start new conversion while one is running
   - Prevents race conditions and corruption

SPECIFICATIONS IMPLEMENTED:
- FR-001 to FR-010: File operations (New, Open, Save, Save As)
- FR-011: Multi-format support (AsciiDoc, Markdown, DOCX, PDF, HTML)
- FR-012: PDF import via text extraction
- FR-025 to FR-027: Pandoc integration for conversion
- NFR-011: Large file support (50MB+)

REFACTORING HISTORY:
- v1.0: All code in main_window.py (1,700+ lines)
- v1.5.0 Phase 7: Extracted to file_operations_manager.py (556 lines)
- Result: Main window reduced by 67%

VERSION: 1.5.0 (Major refactoring)
"""

# === STANDARD LIBRARY IMPORTS ===
import io  # For in-memory file-like objects (BytesIO, StringIO)
import logging  # For recording what the program does
import platform  # For detecting Windows/Linux/Mac
import uuid  # For generating unique IDs (temp files)
from pathlib import Path  # Modern file path handling (better than strings)
from typing import TYPE_CHECKING, Optional  # Type hints

# === QT FRAMEWORK IMPORTS ===
from PySide6.QtWidgets import QFileDialog  # File open/save dialogs

# === CORE IMPORTS (Constants and Utilities) ===
from asciidoc_artisan.core import (
    DEFAULT_FILENAME,  # "Untitled.adoc"
    DOCX_FILTER,  # "Word Documents (*.docx)"
    ERR_ASCIIDOC_NOT_INITIALIZED,  # Error message
    HTML_FILTER,  # "HTML Files (*.html *.htm)"
    MD_FILTER,  # "Markdown Files (*.md)"
    MSG_SAVED_ASCIIDOC,  # "Saved as AsciiDoc"
    MSG_SAVED_HTML,  # "Saved as HTML"
    PDF_FILTER,  # "PDF Files (*.pdf)"
    SUPPORTED_OPEN_FILTER,  # Combined filter for Open dialog
    SUPPORTED_SAVE_FILTER,  # Combined filter for Save dialog
    atomic_save_text,  # Safe file write (prevents corruption)
)
from asciidoc_artisan.core.large_file_handler import (  # Streaming I/O for large files
    LargeFileHandler,
)

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

        PARAMETERS:
            editor: The main application window (AsciiDocEditor)

        CREATES:
            self.editor: Reference to main window
            self._is_processing_pandoc: Guard flag (prevents concurrent operations)
            self._pending_file_path: Stores file path during async operations
        """
        # Store reference to main editor window
        self.editor = editor

        # Reentrancy guard - prevents concurrent Pandoc operations
        # If True, another operation is in progress (don't start a new one!)
        self._is_processing_pandoc = False

        # Storage for file path during async operations
        # When Pandoc worker finishes, we need to know which file we were working on
        self._pending_file_path: Optional[Path] = None

    def open_file(self) -> None:
        """
        Open File with Format Conversion Support.

        WHY THIS METHOD EXISTS:
        Users need to open files in different formats (PDF, Word, Markdown, HTML)
        and convert them to AsciiDoc. This method handles all the complexity:
        - Shows file dialog (with Windows-specific fixes)
        - Checks for unsaved changes (prompts to save)
        - Detects file format by extension (.pdf, .docx, .md, etc.)
        - Converts non-AsciiDoc files to AsciiDoc format
        - Handles large files (50MB+) without freezing UI

        WHAT IT DOES:
        1. Checks if another operation is in progress (reentrancy guard)
        2. Prompts to save if there are unsaved changes
        3. Shows file open dialog (Windows-native or Qt dialog)
        4. Detects file format by extension
        5. For PDF: Extracts text using PyMuPDF
        6. For DOCX/MD/HTML: Converts using Pandoc worker (background thread)
        7. For AsciiDoc: Loads directly
        8. Updates UI and status bar

        FOR BEGINNERS - FILE FORMATS:
        - .adoc/.asciidoc = AsciiDoc (native format)
        - .pdf = PDF (read-only, extract text)
        - .docx = Microsoft Word
        - .md/.markdown = Markdown
        - .html/.htm = Web page
        - All non-AsciiDoc formats are converted to AsciiDoc

        REENTRANCY GUARD:
        The _is_processing_pandoc flag prevents starting a new operation while
        one is running. This prevents:
        - Race conditions (two operations modifying same data)
        - File corruption
        - UI state confusion

        PARAMETERS:
            None

        RETURNS:
            None

        SIDE EFFECTS:
            - Shows file dialog
            - Loads file into editor
            - Starts Pandoc worker for format conversion (if needed)
            - Updates window title and status bar
        """
        # === STEP 1: CHECK REENTRANCY GUARD ===
        # Don't start new operation if one is already running
        if self._is_processing_pandoc:
            self.editor.status_manager.show_message(
                "warning", "Busy", "Already processing a file conversion."
            )
            return

        if self.editor._unsaved_changes:
            if not self.editor.status_manager.prompt_save_before_action(
                "opening a new file"
            ):
                return

        file_path_str, _ = QFileDialog.getOpenFileName(
            self.editor,
            "Open File",
            self.editor._settings.last_directory,
            SUPPORTED_OPEN_FILTER,
            options=(
                QFileDialog.Option.DontUseNativeDialog
                if platform.system() != "Windows"
                else QFileDialog.Option(0)
            ),
        )

        if not file_path_str:
            return

        file_path = Path(file_path_str)
        self.editor._settings.last_directory = str(file_path.parent)

        try:
            suffix = file_path.suffix.lower()
            if suffix == ".pdf":
                self._open_pdf_with_extraction(file_path)
                return
            elif suffix in [
                ".docx",
                ".md",
                ".markdown",
                ".html",
                ".htm",
                ".tex",
                ".rst",
                ".org",
                ".textile",
            ]:
                self._open_with_pandoc_conversion(file_path, suffix)
                return
            else:
                self._open_native_file(file_path)

        except Exception as e:
            logger.exception(f"Failed to open file: {file_path}")
            self.editor.status_manager.show_message(
                "critical", "Error", f"Failed to open file:\n{e}"
            )

    def save_file(self, save_as: bool = False) -> bool:
        """
        Save file with Windows-friendly dialog.

        Handles both simple AsciiDoc saves and export to other formats.
        Simple .adoc saves delegate to atomic file write.

        Args:
            save_as: If True, always show save dialog

        Returns:
            True if saved successfully, False otherwise
        """
        if save_as or not self.editor._current_file_path:

            suggested_name = (
                self.editor._current_file_path.name
                if self.editor._current_file_path
                else DEFAULT_FILENAME
            )
            suggested_path = Path(self.editor._settings.last_directory) / suggested_name

            file_path_str, selected_filter = QFileDialog.getSaveFileName(
                self.editor,
                "Save File",
                str(suggested_path),
                SUPPORTED_SAVE_FILTER,
                options=(
                    QFileDialog.Option.DontUseNativeDialog
                    if platform.system() != "Windows"
                    else QFileDialog.Option(0)
                ),
            )

            if not file_path_str:
                return False

            file_path = Path(file_path_str)
            logger.info(
                f"Save As dialog - file_path: {file_path}, selected_filter: {selected_filter}"
            )

            format_type, file_path = self._determine_save_format(
                file_path, selected_filter
            )

            if format_type != "adoc":

                # Use settings preference for AI conversion (defaults to Pandoc)
                use_ai_for_export = (
                    self.editor._settings_manager.get_ai_conversion_preference(
                        self.editor._settings
                    )
                )

                logger.info(
                    f"Calling _save_as_format_internal with file_path={file_path}, format_type={format_type}, use_ai={use_ai_for_export}"
                )
                return self.save_as_format_internal(
                    file_path, format_type, use_ai_for_export
                )

        else:
            # We only reach here if _current_file_path is not None
            file_path = self.editor._current_file_path
            assert file_path is not None, "file_path should not be None in save mode"

            if file_path.suffix.lower() not in [".adoc", ".asciidoc"]:

                file_path = file_path.with_suffix(".adoc")
                logger.info(
                    f"Converting save format from {self.editor._current_file_path.suffix} to .adoc"
                )

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

    def save_as_format_internal(
        self, file_path: Path, format_type: str, use_ai: Optional[bool] = None
    ) -> bool:
        """Internal method to save file in specified format without showing dialog.

        Args:
            file_path: Target file path
            format_type: Target format (adoc, md, docx, pdf, html)
            use_ai: Whether to use AI conversion (None = use settings default)

        Returns:
            True if export started successfully, False otherwise
        """
        logger.info(
            f"_save_as_format_internal called - file_path: {file_path}, format_type: {format_type}, use_ai: {use_ai}"
        )

        if use_ai is None:
            use_ai = self.editor._settings_manager.get_ai_conversion_preference(
                self.editor._settings
            )

        content = self.editor.editor.toPlainText()

        if format_type == "adoc":
            if atomic_save_text(file_path, content, encoding="utf-8"):
                self.editor._current_file_path = file_path
                self.editor._settings.last_directory = str(file_path.parent)
                self.editor._unsaved_changes = False
                self.editor.status_manager.update_window_title()
                self.editor.status_bar.showMessage(MSG_SAVED_ASCIIDOC.format(file_path))
                return True
            else:
                self.editor.status_manager.show_message(
                    "critical",
                    "Save Error",
                    f"Failed to save AsciiDoc file: {file_path}",
                )
                return False

        if format_type == "html":
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
                    raise IOError(f"Atomic save failed for {file_path}")
            except Exception as e:
                logger.exception(f"Failed to save HTML file: {e}")
                self.editor.status_manager.show_message(
                    "critical", "Save Error", f"Failed to save HTML file:\n{e}"
                )
                return False

        if not self.editor.ui_state_manager.check_pandoc_availability(
            f"Save as {format_type.upper()}"
        ):
            return False

        self.editor.status_bar.showMessage(f"Saving as {format_type.upper()}...")

        # Determine source format from current file
        source_format = "asciidoc"  # default
        temp_source_file = None

        if self.editor._current_file_path:
            suffix = self.editor._current_file_path.suffix.lower()
            format_map = {
                ".md": "markdown",
                ".markdown": "markdown",
                ".docx": "docx",
                ".pdf": "markdown",  # PDF was converted to text, treat as markdown
                ".html": "html",
                ".htm": "html",
            }
            source_format = format_map.get(suffix, "asciidoc")

        # If source is AsciiDoc, convert to HTML first (legacy path)
        if source_format == "asciidoc":
            try:
                if self.editor._asciidoc_api is None:
                    raise RuntimeError(ERR_ASCIIDOC_NOT_INITIALIZED)

                infile = io.StringIO(content)
                outfile = io.StringIO()
                self.editor._asciidoc_api.execute(infile, outfile, backend="html5")
                html_content = outfile.getvalue()

                temp_source_file = (
                    Path(self.editor._temp_dir.name) / f"temp_{uuid.uuid4().hex}.html"
                )
                temp_source_file.write_text(html_content, encoding="utf-8")
                source_format = "html"
            except Exception as e:
                logger.exception(f"Failed to convert AsciiDoc to HTML: {e}")
                self.editor.status_manager.show_message(
                    "critical",
                    "Conversion Error",
                    f"Failed to convert AsciiDoc to HTML:\n{e}",
                )
                return False
        else:
            # For non-AsciiDoc sources, save content to temp file for Pandoc
            ext_map = {"markdown": ".md", "docx": ".docx", "html": ".html"}
            temp_ext = ext_map.get(source_format, ".txt")
            temp_source_file = (
                Path(self.editor._temp_dir.name) / f"temp_{uuid.uuid4().hex}{temp_ext}"
            )
            try:
                temp_source_file.write_text(content, encoding="utf-8")
            except Exception as e:
                self.editor.status_manager.show_message(
                    "critical", "Save Error", f"Failed to create temporary file:\n{e}"
                )
                return False

        self.editor.status_bar.showMessage(f"Saving as {format_type.upper()}...")

        # Set export manager pending paths for result handling
        self.editor.export_manager.pending_export_path = file_path
        self.editor.export_manager.pending_export_format = format_type

        if format_type in ["pdf", "docx"]:
            # Use Pandoc for PDF and DOCX conversion - pass output file directly
            logger.info(
                f"Emitting pandoc conversion request for {format_type} - source: {temp_source_file} ({source_format}), output: {file_path}"
            )
            self.editor.request_pandoc_conversion.emit(
                temp_source_file,
                format_type,
                source_format,
                f"Exporting to {format_type.upper()}",
                file_path,
                use_ai,
            )
        else:
            # For other formats, let worker return the content
            logger.info(
                f"Emitting pandoc conversion request for {format_type} - source: {temp_source_file} ({source_format})"
            )
            self.editor.request_pandoc_conversion.emit(
                temp_source_file,
                format_type,
                source_format,
                f"Exporting to {format_type.upper()}",
                None,
                use_ai,
            )

            self.editor._pending_export_path = file_path
            self.editor._pending_export_format = format_type

        if format_type == "adoc":
            self.editor._current_file_path = file_path
            self.editor._settings.last_directory = str(file_path.parent)
            self.editor._unsaved_changes = False
            self.editor.status_manager.update_window_title()

        return True

    # Helper methods for file opening

    def _open_pdf_with_extraction(self, file_path: Path) -> None:
        """Import PDF file via text extraction.

        Args:
            file_path: Path to PDF file to import
        """
        from asciidoc_artisan.document_converter import pdf_extractor

        if not pdf_extractor.is_available():
            self.editor.status_manager.show_message(
                "warning",
                "PDF Support Unavailable",
                "PDF text extraction requires PyMuPDF.\n\n"
                "To install:\n"
                "  pip install pymupdf\n\n"
                "After installation, restart the application.",
            )
            return

        self.editor.status_bar.showMessage(
            f"Extracting text from PDF: {file_path.name}..."
        )

        success, asciidoc_text, error_msg = pdf_extractor.convert_to_asciidoc(file_path)

        if not success:
            self.editor.status_manager.show_message(
                "critical",
                "PDF Extraction Failed",
                f"Failed to extract text from PDF:\n\n{error_msg}\n\n"
                "The PDF may be encrypted, image-based, or corrupted.",
            )
            return

        # Load extracted content into editor
        self.editor.file_load_manager.load_content_into_editor(asciidoc_text, file_path)
        self.editor.status_bar.showMessage(
            f"PDF imported successfully: {file_path.name}", 5000
        )

    def _open_with_pandoc_conversion(self, file_path: Path, suffix: str) -> None:
        """Open file with Pandoc format conversion.

        Args:
            file_path: Path to file to import
            suffix: File extension (e.g., '.docx', '.md')
        """
        if not self.editor.ui_state_manager.check_pandoc_availability(
            f"Opening {suffix.upper()[1:]}"
        ):
            return

        format_map = {
            ".docx": ("docx", "binary"),
            ".md": ("markdown", "text"),
            ".markdown": ("markdown", "text"),
            ".html": ("html", "text"),
            ".htm": ("html", "text"),
            ".tex": ("latex", "text"),
            ".rst": ("rst", "text"),
            ".org": ("org", "text"),
            ".textile": ("textile", "text"),
        }

        input_format, file_type = format_map.get(suffix, ("markdown", "text"))

        # Use settings preference for AI conversion (defaults to Pandoc)
        use_ai_for_import = self.editor._settings_manager.get_ai_conversion_preference(
            self.editor._settings
        )

        self._is_processing_pandoc = True
        self._pending_file_path = file_path
        self.editor._update_ui_state()

        self.editor.editor.setPlainText(
            f"// Converting {file_path.name} to AsciiDoc...\n// Please wait..."
        )
        self.editor.preview.setHtml(
            "<h3>Converting document...</h3><p>The preview will update when conversion is complete.</p>"
        )
        self.editor.status_bar.showMessage(
            f"Converting '{file_path.name}' from {suffix.upper()[1:]} to AsciiDoc..."
        )

        file_content: str | bytes
        if file_type == "binary":
            file_content = file_path.read_bytes()
        else:
            file_content = file_path.read_text(encoding="utf-8")

        logger.info(
            f"Starting conversion of {file_path.name} from {input_format} to asciidoc (AI: {use_ai_for_import})"
        )

        self.editor.request_pandoc_conversion.emit(
            file_content,
            "asciidoc",
            input_format,
            f"converting '{file_path.name}'",
            None,
            use_ai_for_import,
        )

    def _open_native_file(self, file_path: Path) -> None:
        """Open native AsciiDoc file with large file optimization.

        Args:
            file_path: Path to AsciiDoc file to open
        """
        # Use optimized loading for large files
        file_path.stat().st_size
        category = LargeFileHandler.get_file_size_category(file_path)

        if category in ["medium", "large"]:
            logger.info(f"Loading {category} file with optimizations")
            success, content, error = (
                self.editor.large_file_handler.load_file_optimized(file_path)
            )
            if not success:
                raise Exception(error)
        else:
            content = file_path.read_text(encoding="utf-8")

        self.editor.file_load_manager.load_content_into_editor(content, file_path)

    # Helper methods for file saving

    def _determine_save_format(
        self, file_path: Path, selected_filter: str
    ) -> tuple[str, Path]:
        """Determine save format and ensure file path has correct extension.

        Args:
            file_path: Initial file path from dialog
            selected_filter: Selected file filter from dialog

        Returns:
            Tuple of (format_type, corrected_file_path)
        """
        format_type = "adoc"

        if MD_FILTER in selected_filter:
            format_type = "md"
        elif DOCX_FILTER in selected_filter:
            format_type = "docx"
        elif HTML_FILTER in selected_filter:
            format_type = "html"
        elif PDF_FILTER in selected_filter:
            format_type = "pdf"
        elif file_path.suffix:
            ext = file_path.suffix.lower()
            if ext in [".md", ".markdown"]:
                format_type = "md"
            elif ext == ".docx":
                format_type = "docx"
            elif ext in [".html", ".htm"]:
                format_type = "html"
            elif ext == ".pdf":
                format_type = "pdf"

        # Ensure proper file extension
        if format_type == "md" and not file_path.suffix:
            file_path = file_path.with_suffix(".md")
        elif format_type == "docx" and not file_path.suffix:
            file_path = file_path.with_suffix(".docx")
        elif format_type == "html" and not file_path.suffix:
            file_path = file_path.with_suffix(".html")
        elif format_type == "pdf" and not file_path.suffix:
            file_path = file_path.with_suffix(".pdf")
        elif format_type == "adoc" and not file_path.suffix:
            file_path = file_path.with_suffix(".adoc")

        return format_type, file_path
