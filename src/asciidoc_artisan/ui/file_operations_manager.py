"""
File Operations Manager - Handles complex file operations with format conversion.

Implements:
- File opening with PDF import and format conversion
- File saving with multi-format export support
- Format conversion via Pandoc/Ollama
- Integration with worker threads for async operations

Extracted from main_window.py as part of Phase 7 refactoring to consolidate
all file operations and reach well under 1,000 lines.
"""

import io
import logging
import platform
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFileDialog

from asciidoc_artisan.core import (
    DEFAULT_FILENAME,
    DOCX_FILTER,
    ERR_ASCIIDOC_NOT_INITIALIZED,
    HTML_FILTER,
    MD_FILTER,
    MSG_SAVED_ASCIIDOC,
    MSG_SAVED_HTML,
    PDF_FILTER,
    SUPPORTED_OPEN_FILTER,
    SUPPORTED_SAVE_FILTER,
    atomic_save_text,
)
from asciidoc_artisan.core.large_file_handler import LargeFileHandler

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class FileOperationsManager:
    """Manages file operations including format conversion and export.

    This class encapsulates all complex file operations that involve
    format conversion, PDF import, Pandoc integration, and worker threads.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the FileOperationsManager with a reference to the main editor."""
        self.editor = editor
        self._is_processing_pandoc = False
        self._pending_file_path: Optional[Path] = None

    def open_file(self) -> None:
        """Open a file with proper Windows dialog and format conversion support."""
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
                # PDF import via text extraction
                from document_converter import pdf_extractor

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

                success, asciidoc_text, error_msg = pdf_extractor.convert_to_asciidoc(
                    file_path
                )

                if not success:
                    self.editor.status_manager.show_message(
                        "critical",
                        "PDF Extraction Failed",
                        f"Failed to extract text from PDF:\n\n{error_msg}\n\n"
                        "The PDF may be encrypted, image-based, or corrupted.",
                    )
                    return

                # Load extracted content into editor
                self.editor.file_load_manager.load_content_into_editor(
                    asciidoc_text, file_path
                )
                self.editor.status_bar.showMessage(
                    f"PDF imported successfully: {file_path.name}", 5000
                )
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
                use_ai_for_import = (
                    self.editor._settings_manager.get_ai_conversion_preference(
                        self.editor._settings
                    )
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
            else:
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

                self.editor.file_load_manager.load_content_into_editor(
                    content, file_path
                )

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
