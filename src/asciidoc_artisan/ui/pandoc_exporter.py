"""
Pandoc Exporter - Handles Pandoc-based export operations.

Extracted from ExportManager to reduce class size (MA principle).
Handles Pandoc conversion requests and PDF fallback logic.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from asciidoc_artisan.ui.export_manager import ExportManager

logger = logging.getLogger(__name__)


class PandocExporter:
    """
    Pandoc-based export operations handler.

    This class was extracted from ExportManager to reduce class size
    per MA principle (533→425 lines).

    Handles:
    - Pandoc conversion request emission
    - PDF fallback when no PDF engine available
    - Export via Pandoc workflow
    """

    def __init__(self, export_manager: "ExportManager") -> None:
        """
        Initialize the Pandoc exporter.

        Args:
            export_manager: ExportManager instance to delegate to
        """
        self.export_manager = export_manager

    def emit_pandoc_request(self, temp_html: Path, file_path: Path, format_type: str, use_ai: bool) -> None:
        """
        Emit Pandoc conversion request.

        MA principle: Extracted from _export_via_pandoc (25 lines).

        Args:
            temp_html: Temporary HTML file path
            file_path: Target file path
            format_type: Target format
            use_ai: Whether to use AI conversion
        """
        if format_type in ["pdf", "docx"]:
            # Direct file path conversion
            self.export_manager.window.request_pandoc_conversion.emit(
                temp_html,
                format_type,
                "html",
                f"Exporting to {format_type.upper()}",
                file_path,
                use_ai,
            )
            self.export_manager.pending_export_path = None
            self.export_manager.pending_export_format = None
        else:
            # Indirect conversion (result comes back via signal)
            self.export_manager.window.request_pandoc_conversion.emit(
                temp_html,
                format_type,
                "html",
                f"Exporting to {format_type.upper()}",
                None,
                use_ai,
            )
            self.export_manager.pending_export_path = file_path
            self.export_manager.pending_export_format = format_type

        self.export_manager.export_started.emit(format_type)

    def export_via_pandoc(self, file_path: Path, format_type: str, content: str, use_ai: bool) -> bool:
        """
        Export via Pandoc (asynchronous).

        MA principle: Reduced from 69→23 lines by extracting 3 helpers (67% reduction).

        Args:
            file_path: Target file path
            format_type: Target format (md, docx, pdf)
            content: AsciiDoc content to export
            use_ai: Whether to use AI-enhanced conversion

        Returns:
            True if export initiated successfully, False otherwise
        """
        self.export_manager.status_bar.showMessage(f"Exporting to {format_type.upper()}...")

        # Convert AsciiDoc to HTML
        html_content = self.export_manager._convert_to_html_for_export(content)
        if html_content is None:
            return False

        # Create temporary HTML file
        temp_html = self.export_manager._create_temp_html_file(html_content)
        if temp_html is None:
            return False

        # Handle PDF engine fallback
        if format_type == "pdf" and not self.export_manager.pdf_helper.check_pdf_engine_available():
            return self.export_manager._export_pdf_fallback(file_path, html_content)

        # Emit Pandoc conversion request
        self.emit_pandoc_request(temp_html, file_path, format_type, use_ai)
        return True

    def export_pdf_fallback(self, file_path: Path, html_content: str) -> bool:
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
            styled_html = self.export_manager.pdf_helper.add_print_css_to_html(html_content)
            html_path = file_path.with_suffix(".html")

            if not self.export_manager._save_file_atomic(html_path, styled_html, encoding="utf-8"):
                raise OSError(f"Failed to save HTML file: {html_path}")

            self.export_manager.status_bar.showMessage(f"Exported as HTML (PDF-ready): {html_path}")
            self.export_manager.status_manager.show_message(
                "information",
                "PDF Export Alternative",
                f"Exported as HTML with print styling: {html_path}\n\n"
                f"To create PDF:\n"
                f"1. Open this file in your browser\n"
                f"2. Press Ctrl+P (or Cmd+P on Mac)\n"
                f"3. Select 'Save as PDF'\n\n"
                f"The HTML includes print-friendly styling for optimal PDF output.",
            )
            self.export_manager.export_completed.emit(html_path)
            return True
        except Exception as e:
            logger.exception(f"Failed to save HTML for PDF: {e}")
            self.export_manager.export_failed.emit(str(e))
            return False
