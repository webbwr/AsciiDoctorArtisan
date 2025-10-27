"""
Export Manager - Manage document export and format conversion operations.

This module handles:
- Exporting to multiple formats (AsciiDoc, Markdown, DOCX, HTML, PDF)
- Pandoc-based format conversion with AI enhancement support
- Clipboard content conversion
- Export state management
- PDF engine detection and fallback

Extracted from main_window.py to improve maintainability and testability.
"""

import io
import logging
import platform
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QFileDialog

from asciidoc_artisan.core import (
    ADOC_FILTER,
    DOCX_FILTER,
    HTML_FILTER,
    MD_FILTER,
    PDF_FILTER,
    atomic_save_text,
)

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

logger = logging.getLogger(__name__)

# Export messages
MSG_SAVED_ASCIIDOC = "Saved as AsciiDoc: {}"
ERR_ASCIIDOC_NOT_INITIALIZED = "AsciiDoc renderer not initialized"


class ExportManager(QObject):
    """Handle all document export and format conversion operations."""

    # Signals for export operations
    export_started = Signal(str)  # Emitted when export starts (format)
    export_completed = Signal(Path)  # Emitted when export completes (file path)
    export_failed = Signal(str)  # Emitted when export fails (error message)

    def __init__(self, main_window: "AsciiDocEditor"):
        """
        Initialize ExportManager.

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
            if self._asciidoc_api is None:
                raise RuntimeError(ERR_ASCIIDOC_NOT_INITIALIZED)

            infile = io.StringIO(content)
            outfile = io.StringIO()
            self._asciidoc_api.execute(infile, outfile, backend="html5")
            html_content = outfile.getvalue()

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

        # Convert AsciiDoc to HTML first
        try:
            if self._asciidoc_api is None:
                raise RuntimeError(ERR_ASCIIDOC_NOT_INITIALIZED)

            infile = io.StringIO(content)
            outfile = io.StringIO()
            self._asciidoc_api.execute(infile, outfile, backend="html5")
            html_content = outfile.getvalue()
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
        if format_type == "pdf" and not self.check_pdf_engine_available():
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
            styled_html = self.add_print_css_to_html(html_content)
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

    def check_pdf_engine_available(self) -> bool:
        """
        Check if any PDF engine is available.

        Returns:
            True if a PDF engine is found, False otherwise
        """
        pdf_engines = ["wkhtmltopdf", "weasyprint", "pdflatex", "xelatex", "lualatex"]

        for engine in pdf_engines:
            try:
                subprocess.run([engine, "--version"], capture_output=True, check=True)
                logger.debug(f"PDF engine found: {engine}")
                return True
            except (FileNotFoundError, subprocess.CalledProcessError, Exception):
                continue

        logger.warning("No PDF engine available")
        return False

    def add_print_css_to_html(self, html_content: str) -> str:
        """
        Add print-friendly CSS to HTML for better PDF output.

        Args:
            html_content: HTML content to enhance

        Returns:
            HTML content with print CSS added
        """
        print_css = """
        <style type="text/css" media="print">
            @page {
                size: letter;
                margin: 1in;
            }
            body {
                font-family: Georgia, serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #000;
            }
            h1, h2, h3, h4, h5, h6 {
                page-break-after: avoid;
                font-family: Helvetica, Arial, sans-serif;
            }
            pre, code {
                font-family: Consolas, Monaco, monospace;
                font-size: 9pt;
                background-color: #f5f5f5;
                page-break-inside: avoid;
            }
            table {
                border-collapse: collapse;
                page-break-inside: avoid;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            a {
                color: #000;
                text-decoration: underline;
            }
            @media screen {
                body {
                    max-width: 8.5in;
                    margin: 0 auto;
                    padding: 1in;
                }
            }
        </style>
        """

        if "</head>" in html_content:
            html_content = html_content.replace("</head>", print_css + "</head>")
        elif "<html>" in html_content:
            html_content = html_content.replace("<html>", "<html>" + print_css)
        else:
            html_content = print_css + html_content

        return html_content

    def convert_and_paste_from_clipboard(self) -> None:
        """
        Convert clipboard content to AsciiDoc and paste at cursor.

        Supports HTML and plain text clipboard content.
        """
        # Check Pandoc availability
        from asciidoc_artisan.core.constants import PANDOC_AVAILABLE

        if not PANDOC_AVAILABLE:
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
