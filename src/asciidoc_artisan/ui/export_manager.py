"""
===============================================================================
EXPORT MANAGER - Document Export and Format Conversion
===============================================================================

FILE PURPOSE:
This file manages exporting documents to different formats: AsciiDoc, Markdown,
Word (DOCX), HTML, and PDF.

WHAT THIS FILE DOES:
1. Exports AsciiDoc documents to multiple formats (5 formats total)
2. Uses Pandoc for format conversion (AsciiDoc → Markdown/Word/HTML/PDF)
3. Handles clipboard content conversion (paste and convert)
4. Detects PDF engines and chooses best one (wkhtmltopdf or xhtml2pdf)
5. Manages export state (prevents concurrent exports)

FOR BEGINNERS - WHAT IS EXPORTING?:
Exporting means saving your document in a different format:
- You write in AsciiDoc (easy to read and write)
- You export to Word (DOCX) to send to colleagues
- You export to PDF to share a finished document
- You export to HTML to publish on a website

ANALOGY:
Think of a translator:
- You speak English (AsciiDoc)
- Translator converts to Spanish (Word/PDF/HTML)
- Same content, different language (format)

WHY THIS FILE WAS EXTRACTED:
Before v1.5.0, export logic was in main_window.py (making it 1,700+ lines!).
We extracted it to:
- Reduce main_window.py size (part of 67% reduction to 561 lines)
- Group related functionality (all exports in one place)
- Make testing easier (can test exports separately)
- Separate concerns (main window doesn't need to know about Pandoc)

KEY CONCEPTS:

1. FORMAT CONVERSION:
   - Pandoc is the "Swiss Army knife" of document conversion
   - It converts between 40+ formats
   - We use it for: Markdown, Word, HTML, PDF

2. PDF ENGINES:
   - wkhtmltopdf: Fast, high quality (requires external program)
   - xhtml2pdf: Pure Python, slower (fallback if wkhtmltopdf missing)
   - We auto-detect which is available

3. EXPORT STATE MANAGEMENT:
   - _is_exporting flag prevents concurrent exports
   - Can't start new export while one is running
   - Prevents file corruption and UI confusion

4. CLIPBOARD CONVERSION:
   - Copy Word/HTML content to clipboard
   - Paste in AsciiDoc Artisan
   - Automatically converts to AsciiDoc!

SPECIFICATIONS IMPLEMENTED:
- FR-021 to FR-024: Multi-format export (Markdown, DOCX, HTML, PDF)
- FR-028: Clipboard content conversion
- NFR-010: Export operation status indication

REFACTORING HISTORY:
- v1.0: All export code in main_window.py
- v1.5.0: Extracted to export_manager.py (455 lines)
- Result: Main window reduced by 67%

VERSION: 1.5.0 (Major refactoring)
"""

# === STANDARD LIBRARY IMPORTS ===
import logging  # For recording what the program does
import platform  # For detecting Windows/Linux/Mac
import tempfile  # For creating temporary files during export
import uuid  # For generating unique IDs
from pathlib import Path  # Modern file path handling
from typing import TYPE_CHECKING, Optional  # Type hints

# === QT FRAMEWORK IMPORTS ===
from PySide6.QtCore import QObject, Signal  # Signal/slot support, Qt base class
from PySide6.QtGui import QGuiApplication  # For clipboard access
from PySide6.QtWidgets import QFileDialog  # File save dialogs

# === CORE IMPORTS (Constants and Utilities) ===
from asciidoc_artisan.core import (
    ADOC_FILTER,  # "AsciiDoc Files (*.adoc *.asciidoc)"
    DOCX_FILTER,  # "Word Documents (*.docx)"
    HTML_FILTER,  # "HTML Files (*.html *.htm)"
    MD_FILTER,  # "Markdown Files (*.md)"
    PDF_FILTER,  # "PDF Files (*.pdf)"
    atomic_save_text,  # Safe file write (prevents corruption)
)

# === EXPORT HELPER IMPORTS ===
from asciidoc_artisan.ui.export_helpers import (
    ClipboardHelper,  # Clipboard content conversion utilities
    HTMLConverter,  # HTML generation for export
    PDFHelper,  # PDF engine detection and conversion
)

# === TYPE CHECKING (Avoid Circular Imports) ===
if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

# === LOGGING SETUP ===
logger = logging.getLogger(__name__)

# === MESSAGE CONSTANTS ===
# Status messages shown to user after export operations
MSG_SAVED_ASCIIDOC = "Saved as AsciiDoc: {}"  # Success message with file path
ERR_ASCIIDOC_NOT_INITIALIZED = "AsciiDoc renderer not initialized"  # Error message


class ExportManager(QObject):
    """
    Export Manager - Handles Document Export and Format Conversion.

    FOR BEGINNERS - WHAT IS THIS CLASS?:
    This class is like a "document translator" that converts your AsciiDoc
    document to other formats (Word, PDF, HTML, Markdown). Think of it as
    having multiple "save as" options.

    RESPONSIBILITIES:
    1. Export to multiple formats (AsciiDoc, Markdown, Word, HTML, PDF)
    2. Use Pandoc for format conversion (background thread)
    3. Detect and use best PDF engine (wkhtmltopdf or fallback)
    4. Handle clipboard content conversion (paste Word/HTML → AsciiDoc)
    5. Manage export state (prevent concurrent exports)

    WHY IT EXISTS:
    Before this class, export logic was in main_window.py. By extracting it,
    we reduced main_window.py by 67% and made exports testable independently.

    USAGE:
    Called by main_window.py:
        export_mgr = ExportManager(self)
        export_mgr.export_as_docx()  # Export to Word
        export_mgr.export_as_pdf()   # Export to PDF

    SIGNALS (Events):
    - export_started: Fired when export begins (emits format name)
    - export_completed: Fired when export succeeds (emits file path)
    - export_failed: Fired when export fails (emits error message)
    """

    # === QT SIGNALS ===
    # These are "events" that other parts of the app can listen to
    export_started = Signal(str)  # Emits format name when export starts
    export_completed = Signal(Path)  # Emits file path when export completes
    export_failed = Signal(str)  # Emits error message when export fails

    def __init__(self, main_window: "AsciiDocEditor"):
        """
        Initialize Export Manager.

        WHAT THIS DOES:
        1. Calls parent QObject.__init__ for signal/slot support
        2. Stores reference to main window
        3. Initializes export state flag

        PARAMETERS:
            main_window: The main AsciiDocEditor window

        CREATES:
            self.main_window: Reference to main window
            self._is_exporting: Guard flag (prevents concurrent exports)

        Args:
            main_window: Main window instance (for signals, editor access, etc.)
        """
        super().__init__(main_window)
        self.window = main_window
        self.editor = main_window.editor
        self.status_bar = main_window.status_bar
        self.status_manager = main_window.status_manager
        self.settings_manager = main_window._settings_manager
        self._settings = main_window._settings
        self._asciidoc_api = main_window._asciidoc_api

        # Export helpers
        self.html_converter = HTMLConverter(self._asciidoc_api)
        self.pdf_helper = PDFHelper()
        self.clipboard_helper = ClipboardHelper()

        # Export state
        self.pending_export_path: Optional[Path] = None
        self.pending_export_format: Optional[str] = None

        # Temporary directory for export operations
        self.temp_dir = tempfile.TemporaryDirectory()

    def cleanup(self) -> None:
        """Clean up temporary directory."""
        try:
            self.temp_dir.cleanup()
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")

    def save_file_as_format(self, format_type: str) -> bool:
        """
        Save/export file in specified format using background conversion.

        Args:
            format_type: Target format (adoc, md, docx, html, pdf)

        Returns:
            True if export initiated successfully, False otherwise
        """
        format_filters = {
            "adoc": (ADOC_FILTER, ".adoc"),
            "md": (MD_FILTER, ".md"),
            "docx": (DOCX_FILTER, ".docx"),
            "html": (HTML_FILTER, ".html"),
            "pdf": (PDF_FILTER, ".pdf"),
        }

        if format_type not in format_filters:
            self.status_manager.show_message(
                "warning", "Export Error", f"Unsupported format: {format_type}"
            )
            return False

        file_filter, suggested_ext = format_filters[format_type]

        # Determine suggested file name
        if self.window._current_file_path:
            suggested_name = self.window._current_file_path.stem + suggested_ext
        else:
            suggested_name = "document" + suggested_ext

        suggested_path = Path(self._settings.last_directory) / suggested_name

        # Show save dialog
        file_path_str, _ = QFileDialog.getSaveFileName(
            self.window,
            f"Export as {format_type.upper()}",
            str(suggested_path),
            file_filter,
            options=(
                QFileDialog.Option.DontUseNativeDialog
                if platform.system() != "Windows"
                else QFileDialog.Option(0)
            ),
        )

        if not file_path_str:
            return False

        file_path = Path(file_path_str)

        # Ensure proper extension
        if not file_path.suffix:
            file_path = file_path.with_suffix(suggested_ext)

        content = self.editor.toPlainText()

        # Use settings preference for AI conversion (defaults to Pandoc)
        use_ai_for_export = self.settings_manager.get_ai_conversion_preference(
            self._settings
        )

        # Handle direct AsciiDoc save
        if format_type == "adoc":
            if atomic_save_text(file_path, content, encoding="utf-8"):
                self.status_bar.showMessage(MSG_SAVED_ASCIIDOC.format(file_path))
                self.export_completed.emit(file_path)
                return True
            else:
                self.status_manager.show_message(
                    "critical",
                    "Export Error",
                    f"Failed to save AsciiDoc file: {file_path}",
                )
                self.export_failed.emit(f"Failed to save: {file_path}")
                return False

        # Handle HTML export (synchronous)
        if format_type == "html":
            return self._export_html(file_path, content)

        # Handle Pandoc-based exports (asynchronous)
        return self._export_via_pandoc(
            file_path, format_type, content, use_ai_for_export
        )

    def _export_html(self, file_path: Path, content: str) -> bool:
        """
        Export to HTML format (synchronous).

        Args:
            file_path: Target file path
            content: AsciiDoc content to export

        Returns:
            True if successful, False otherwise
        """
        self.status_bar.showMessage("Exporting to HTML...")
        try:
            # Convert AsciiDoc to HTML using helper
            html_content = self.html_converter.asciidoc_to_html(content)

            if atomic_save_text(file_path, html_content, encoding="utf-8"):
                self.status_bar.showMessage(f"Exported to HTML: {file_path}")
                logger.info(f"Successfully exported to HTML: {file_path}")
                self.export_completed.emit(file_path)
                return True
            else:
                raise IOError(f"Atomic save failed for {file_path}")
        except Exception as e:
            logger.exception(f"Failed to export HTML file: {e}")
            self.status_manager.show_message(
                "critical", "Export Error", f"Failed to export HTML file:\n{e}"
            )
            self.export_failed.emit(str(e))
            return False

    def _export_via_pandoc(
        self, file_path: Path, format_type: str, content: str, use_ai: bool
    ) -> bool:
        """
        Export via Pandoc (asynchronous).

        Args:
            file_path: Target file path
            format_type: Target format (md, docx, pdf)
            content: AsciiDoc content to export
            use_ai: Whether to use AI-enhanced conversion

        Returns:
            True if export initiated successfully, False otherwise
        """
        self.status_bar.showMessage(f"Exporting to {format_type.upper()}...")

        # Convert AsciiDoc to HTML first using helper
        try:
            html_content = self.html_converter.asciidoc_to_html(content)
        except Exception as e:
            logger.exception(f"Failed to convert AsciiDoc to HTML: {e}")
            self.status_manager.show_message(
                "critical",
                "Conversion Error",
                f"Failed to convert AsciiDoc to HTML:\n{e}",
            )
            self.export_failed.emit(str(e))
            return False

        # Create temporary HTML file
        temp_html = Path(self.temp_dir.name) / f"temp_{uuid.uuid4().hex}.html"
        try:
            temp_html.write_text(html_content, encoding="utf-8")
        except Exception as e:
            self.status_manager.show_message(
                "critical", "Export Error", f"Failed to create temporary file:\n{e}"
            )
            self.export_failed.emit(str(e))
            return False

        # Handle PDF engine fallback
        if format_type == "pdf" and not self.pdf_helper.check_pdf_engine_available():
            return self._export_pdf_fallback(file_path, html_content)

        # Emit Pandoc conversion request
        if format_type in ["pdf", "docx"]:
            # Direct file path conversion
            self.window.request_pandoc_conversion.emit(
                temp_html,
                format_type,
                "html",
                f"Exporting to {format_type.upper()}",
                file_path,
                use_ai,
            )
            self.pending_export_path = None
            self.pending_export_format = None
        else:
            # Indirect conversion (result comes back via signal)
            self.window.request_pandoc_conversion.emit(
                temp_html,
                format_type,
                "html",
                f"Exporting to {format_type.upper()}",
                None,
                use_ai,
            )
            self.pending_export_path = file_path
            self.pending_export_format = format_type

        self.export_started.emit(format_type)
        return True

    def _export_pdf_fallback(self, file_path: Path, html_content: str) -> bool:
        """
        Export PDF fallback when no PDF engine is available.

        Creates an HTML file with print styling for manual PDF creation.

        Args:
            file_path: Target PDF file path
            html_content: HTML content to save

        Returns:
            True if fallback successful, False otherwise
        """
        try:
            styled_html = self.pdf_helper.add_print_css_to_html(html_content)
            html_path = file_path.with_suffix(".html")

            if not atomic_save_text(html_path, styled_html, encoding="utf-8"):
                raise IOError(f"Failed to save HTML file: {html_path}")

            self.status_bar.showMessage(f"Exported as HTML (PDF-ready): {html_path}")
            self.status_manager.show_message(
                "information",
                "PDF Export Alternative",
                f"Exported as HTML with print styling: {html_path}\n\n"
                f"To create PDF:\n"
                f"1. Open this file in your browser\n"
                f"2. Press Ctrl+P (or Cmd+P on Mac)\n"
                f"3. Select 'Save as PDF'\n\n"
                f"The HTML includes print-friendly styling for optimal PDF output.",
            )
            self.export_completed.emit(html_path)
            return True
        except Exception as e:
            logger.exception(f"Failed to save HTML for PDF: {e}")
            self.export_failed.emit(str(e))
            return False

    def convert_and_paste_from_clipboard(self) -> None:
        """
        Convert clipboard content to AsciiDoc and paste at cursor.

        Supports HTML and plain text clipboard content.
        """
        # Check Pandoc availability (lazy import for fast startup)
        from asciidoc_artisan.core.constants import is_pandoc_available

        if not is_pandoc_available():
            self.status_manager.show_message(
                "warning",
                "Pandoc Not Available",
                "Pandoc is required for clipboard conversion.\n\n"
                "Please install Pandoc to use this feature.",
            )
            return

        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData()

        source_text = None
        source_format = "markdown"

        # Check for HTML content first (higher quality)
        if mime_data.hasHtml():
            source_text = mime_data.html()
            source_format = "html"
        elif mime_data.hasText():
            source_text = mime_data.text()

        if not source_text:
            self.status_manager.show_message(
                "info", "Empty Clipboard", "No text or HTML found in clipboard."
            )
            return

        # Update UI state
        self.window._is_processing_pandoc = True
        self.window._update_ui_state()
        self.status_bar.showMessage("Converting clipboard content...")

        # Request conversion
        use_ai = self.settings_manager.get_ai_conversion_preference(self._settings)
        self.window.request_pandoc_conversion.emit(
            source_text,
            "asciidoc",
            source_format,
            "clipboard conversion",
            None,
            use_ai,
        )

    def handle_pandoc_result(self, result: str, context: str) -> None:
        """
        Handle Pandoc conversion result.

        Args:
            result: Conversion result text
            context: Context string identifying the operation
        """
        # Handle clipboard conversion
        if context == "clipboard conversion":
            self.editor.insertPlainText(result)
            self.status_bar.showMessage("Pasted converted content")
            return

        # Handle export operations
        if "Exporting to" in context and (
            "File saved to:" in result or self.pending_export_path
        ):
            self._handle_export_result(result, context)

    def _handle_export_result(self, result: str, context: str) -> None:
        """
        Handle export operation result.

        Args:
            result: Export result text
            context: Context string identifying the operation
        """
        if self.pending_export_path is None or self.pending_export_format is None:
            logger.error("Export paths not set despite being in export context")
            return

        try:
            if "File saved to:" in result:
                # Direct file save
                self.status_bar.showMessage(
                    f"Exported successfully: {result.split(': ', 1)[1]}"
                )
                self.export_completed.emit(self.pending_export_path)
            elif self.pending_export_format == "pdf":
                # PDF export
                if self.pending_export_path.exists():
                    self.status_bar.showMessage(
                        f"Exported to PDF: {self.pending_export_path}"
                    )
                    self.export_completed.emit(self.pending_export_path)
                else:
                    # Save result to file
                    if atomic_save_text(
                        self.pending_export_path, result, encoding="utf-8"
                    ):
                        self.status_bar.showMessage(
                            f"Exported to {self.pending_export_format.upper()}: {self.pending_export_path}"
                        )
                        self.export_completed.emit(self.pending_export_path)
                    else:
                        raise IOError(f"Failed to save: {self.pending_export_path}")
            else:
                # Other formats
                if atomic_save_text(self.pending_export_path, result, encoding="utf-8"):
                    self.status_bar.showMessage(
                        f"Exported to {self.pending_export_format.upper()}: {self.pending_export_path}"
                    )
                    self.export_completed.emit(self.pending_export_path)
                else:
                    raise IOError(f"Failed to save: {self.pending_export_path}")

            # Update last directory
            self._settings.last_directory = str(self.pending_export_path.parent)
            logger.info(
                f"Export completed: {self.pending_export_format} -> {self.pending_export_path}"
            )
        except Exception as e:
            logger.exception(f"Failed to handle export result: {e}")
            self.status_manager.show_message(
                "critical", "Export Error", f"Failed to save exported file:\n{e}"
            )
            self.export_failed.emit(str(e))
        finally:
            self.pending_export_path = None
            self.pending_export_format = None
