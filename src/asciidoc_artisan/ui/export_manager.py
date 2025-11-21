"""
Export Manager - Document export and format conversion.

Exports AsciiDoc to: Markdown (.md), DOCX (.docx), HTML (.html), PDF (.pdf).
Uses Pandoc for conversion, supports AI-enhanced exports (optional).
Handles clipboard content conversion (Word/HTML → AsciiDoc).

Architecture (delegation pattern):
- PandocExporter: Pandoc operations
- HTMLConverter: AsciiDoc → HTML
- PDFHelper: PDF engine detection
- ClipboardHelper: Clipboard conversion

Security: Atomic file writes, temp cleanup, path validation, shell=False.
Performance: Lazy imports, background PandocWorker, responsive UI.

Implements: FR-021 to FR-024 (multi-format export), FR-028 (clipboard).
MA principle: Reduced from 648→572 lines (11.7% reduction, partial work).
"""

# === STANDARD LIBRARY IMPORTS ===
import logging  # For recording what the program does
import platform  # For detecting Windows/Linux/Mac
import tempfile  # For creating temporary files during export
import uuid  # For generating unique IDs
from pathlib import Path  # Modern file path handling
from typing import TYPE_CHECKING  # Type hints

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
from asciidoc_artisan.ui.pandoc_exporter import PandocExporter

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
    Export Manager - Document export and format conversion.

    Exports AsciiDoc to multiple formats (Markdown, DOCX, HTML, PDF).
    Uses Pandoc for conversion, handles clipboard content conversion.

    Signals: export_started(str), export_completed(Path), export_failed(str)
    """

    # === QT SIGNALS ===
    # These are "events" that other parts of the app can listen to
    export_started = Signal(str)  # Emits format name when export starts
    export_completed = Signal(Path)  # Emits file path when export completes
    export_failed = Signal(str)  # Emits error message when export fails

    def __init__(self, main_window: "AsciiDocEditor"):
        """Initialize Export Manager with main window reference and helpers."""
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
        self.pending_export_path: Path | None = None
        self.pending_export_format: str | None = None

        # Temporary directory for export operations
        self.temp_dir = tempfile.TemporaryDirectory()

    def cleanup(self) -> None:
        """Clean up temporary directory."""
        try:
            self.temp_dir.cleanup()
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")

    @property
    def _pandoc_exporter(self) -> PandocExporter:
        """Lazy-initialized Pandoc exporter (MA principle: delegates to PandocExporter)."""
        if not hasattr(self, "_exporter_instance"):
            self._exporter_instance = PandocExporter(self)
        return self._exporter_instance

    def _save_file_atomic(self, file_path: Path, content: str, encoding: str = "utf-8") -> bool:
        """Save file atomically (test wrapper for PandocExporter)."""
        return atomic_save_text(file_path, content, encoding=encoding)

    def _get_format_filter_and_extension(self, format_type: str) -> tuple[str, str] | None:
        """Get file filter and extension for format (MA: extracted 12 lines)."""
        format_filters = {
            "adoc": (ADOC_FILTER, ".adoc"),
            "md": (MD_FILTER, ".md"),
            "docx": (DOCX_FILTER, ".docx"),
            "html": (HTML_FILTER, ".html"),
            "pdf": (PDF_FILTER, ".pdf"),
        }

        if format_type not in format_filters:
            self.status_manager.show_message("warning", "Export Error", f"Unsupported format: {format_type}")
            return None

        return format_filters[format_type]

    def _get_suggested_export_path(self, suggested_ext: str) -> Path:
        """Generate suggested file path for export (MA: extracted 6 lines)."""
        if self.window._current_file_path:
            suggested_name = self.window._current_file_path.stem + suggested_ext
        else:
            suggested_name = "document" + suggested_ext
        return Path(self._settings.last_directory) / suggested_name

    def _show_export_dialog(self, format_type: str, suggested_path: Path, file_filter: str) -> Path | None:
        """Show save dialog for export (MA: extracted 13 lines)."""
        file_path_str, _ = QFileDialog.getSaveFileName(
            self.window,
            f"Export as {format_type.upper()}",
            str(suggested_path),
            file_filter,
            options=(
                QFileDialog.Option.DontUseNativeDialog if platform.system() != "Windows" else QFileDialog.Option(0)
            ),
        )

        if not file_path_str:
            return None

        return Path(file_path_str)

    def _save_asciidoc_directly(self, file_path: Path, content: str) -> bool:
        """Save as AsciiDoc file, no conversion (MA: extracted 14 lines)."""
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

    def save_file_as_format(self, format_type: str) -> bool:
        """Save/export file in format (MA: 78→27 lines, 4 helpers, 65% reduction)."""
        # Get format filter and extension
        result = self._get_format_filter_and_extension(format_type)
        if not result:
            return False
        file_filter, suggested_ext = result

        # Get suggested file path
        suggested_path = self._get_suggested_export_path(suggested_ext)

        # Show save dialog
        file_path = self._show_export_dialog(format_type, suggested_path, file_filter)
        if not file_path:
            return False

        # Ensure proper extension
        if not file_path.suffix:
            file_path = file_path.with_suffix(suggested_ext)

        content = self.editor.toPlainText()

        # Handle direct AsciiDoc save
        if format_type == "adoc":
            return self._save_asciidoc_directly(file_path, content)

        # Handle HTML export (synchronous)
        if format_type == "html":
            return self._export_html(file_path, content)

        # Handle Pandoc-based exports (asynchronous)
        use_ai_for_export = self.settings_manager.get_ai_conversion_preference(self._settings)
        return self._export_via_pandoc(file_path, format_type, content, use_ai_for_export)

    def _export_html(self, file_path: Path, content: str) -> bool:
        """Export to HTML format (synchronous)."""
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
                raise OSError(f"Atomic save failed for {file_path}")
        except Exception as e:
            logger.exception(f"Failed to export HTML file: {e}")
            self.status_manager.show_message("critical", "Export Error", f"Failed to export HTML file:\n{e}")
            self.export_failed.emit(str(e))
            return False

    def _convert_to_html_for_export(self, content: str) -> str | None:
        """Convert AsciiDoc to HTML for export (MA: extracted 12 lines)."""
        try:
            return self.html_converter.asciidoc_to_html(content)
        except Exception as e:
            logger.exception(f"Failed to convert AsciiDoc to HTML: {e}")
            self.status_manager.show_message(
                "critical",
                "Conversion Error",
                f"Failed to convert AsciiDoc to HTML:\n{e}",
            )
            self.export_failed.emit(str(e))
            return None

    def _create_temp_html_file(self, html_content: str) -> Path | None:
        """Create temp HTML file for Pandoc (MA: extracted 8 lines)."""
        temp_html = Path(self.temp_dir.name) / f"temp_{uuid.uuid4().hex}.html"
        try:
            temp_html.write_text(html_content, encoding="utf-8")
            return temp_html
        except Exception as e:
            self.status_manager.show_message("critical", "Export Error", f"Failed to create temporary file:\n{e}")
            self.export_failed.emit(str(e))
            return None

    def _export_via_pandoc(self, file_path: Path, format_type: str, content: str, use_ai: bool) -> bool:
        """Export via Pandoc (delegates to pandoc_exporter)."""
        return self._pandoc_exporter.export_via_pandoc(file_path, format_type, content, use_ai)

    def _export_pdf_fallback(self, file_path: Path, html_content: str) -> bool:
        """Export PDF fallback (delegates to pandoc_exporter)."""
        return self._pandoc_exporter.export_pdf_fallback(file_path, html_content)

    def convert_and_paste_from_clipboard(self) -> None:
        """Convert clipboard (HTML/text) to AsciiDoc and paste at cursor."""
        # Check Pandoc availability (lazy import for fast startup)
        from asciidoc_artisan.core.constants import is_pandoc_available

        if not is_pandoc_available():
            self.status_manager.show_message(
                "warning",
                "Pandoc Not Available",
                "Pandoc is required for clipboard conversion.\n\nPlease install Pandoc to use this feature.",
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
            self.status_manager.show_message("info", "Empty Clipboard", "No text or HTML found in clipboard.")
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
        """Handle Pandoc conversion result."""
        # Handle clipboard conversion
        if context == "clipboard conversion":
            self.editor.insertPlainText(result)
            self.status_bar.showMessage("Pasted converted content")
            return

        # Handle export operations
        if "Exporting to" in context and ("File saved to:" in result or self.pending_export_path):
            self._handle_export_result(result, context)

    def _handle_export_result(self, result: str, context: str) -> None:
        """Handle export operation result."""
        if self.pending_export_path is None or self.pending_export_format is None:
            logger.error("Export paths not set despite being in export context")
            return

        try:
            if "File saved to:" in result:
                # Direct file save
                self.status_bar.showMessage(f"Exported successfully: {result.split(': ', 1)[1]}")
                self.export_completed.emit(self.pending_export_path)
            elif self.pending_export_format == "pdf":
                # PDF export
                if self.pending_export_path.exists():
                    self.status_bar.showMessage(f"Exported to PDF: {self.pending_export_path}")
                    self.export_completed.emit(self.pending_export_path)
                else:
                    # Save result to file
                    if atomic_save_text(self.pending_export_path, result, encoding="utf-8"):
                        self.status_bar.showMessage(
                            f"Exported to {self.pending_export_format.upper()}: {self.pending_export_path}"
                        )
                        self.export_completed.emit(self.pending_export_path)
                    else:
                        raise OSError(f"Failed to save: {self.pending_export_path}")
            else:
                # Other formats
                if atomic_save_text(self.pending_export_path, result, encoding="utf-8"):
                    self.status_bar.showMessage(
                        f"Exported to {self.pending_export_format.upper()}: {self.pending_export_path}"
                    )
                    self.export_completed.emit(self.pending_export_path)
                else:
                    raise OSError(f"Failed to save: {self.pending_export_path}")

            # Update last directory
            self._settings.last_directory = str(self.pending_export_path.parent)
            logger.info(f"Export completed: {self.pending_export_format} -> {self.pending_export_path}")
        except Exception as e:
            logger.exception(f"Failed to handle export result: {e}")
            self.status_manager.show_message("critical", "Export Error", f"Failed to save exported file:\n{e}")
            self.export_failed.emit(str(e))
        finally:
            self.pending_export_path = None
            self.pending_export_format = None
