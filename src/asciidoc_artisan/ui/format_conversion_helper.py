"""
Format Conversion Helper - Handles format detection and Pandoc conversion requests.

Extracted from FileOperationsManager to reduce class size (MA principle).
Manages source format detection, temp file creation, and Pandoc signal emission.
"""

import io
import logging
import uuid
from pathlib import Path
from typing import Protocol

from asciidoc_artisan.core import ERR_ASCIIDOC_NOT_INITIALIZED

logger = logging.getLogger(__name__)


class EditorContext(Protocol):
    """Protocol for editor context access (avoid circular imports)."""

    _current_file_path: Path | None
    _asciidoc_api: object | None
    _temp_dir: object
    status_manager: object
    export_manager: object
    _pending_export_path: Path | None
    _pending_export_format: str | None
    request_pandoc_conversion: object

    def __getattr__(self, name: str) -> object:  # pragma: no cover
        """Allow access to any editor attribute."""
        ...


class FormatConversionHelper:
    """
    Format conversion and Pandoc integration helper.

    This class was extracted from FileOperationsManager to reduce class size
    per MA principle (797→~664 lines).

    Handles:
    - Source format detection from file extensions
    - AsciiDoc to HTML temp file conversion
    - Temp file creation for Pandoc processing
    - Pandoc conversion signal emission
    """

    def __init__(self, editor: EditorContext) -> None:
        """
        Initialize format conversion helper.

        Args:
            editor: Editor context for accessing state and signals
        """
        self.editor = editor

    def determine_source_format(self) -> str:
        """
        Determine source format from current file extension.

        Returns:
            Source format string ("asciidoc", "markdown", "docx", "html")

        MA principle: Extracted from save_as_format_internal (15 lines).
        """
        source_format = "asciidoc"  # default

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

        return source_format

    def convert_asciidoc_to_html_temp(self, content: str) -> Path | None:
        """
        Convert AsciiDoc to HTML and save to temp file.

        Args:
            content: AsciiDoc content to convert

        Returns:
            Path to temp HTML file or None if conversion failed

        MA principle: Extracted from save_as_format_internal (21 lines).
        """
        try:
            if self.editor._asciidoc_api is None:
                raise RuntimeError(ERR_ASCIIDOC_NOT_INITIALIZED)

            infile = io.StringIO(content)
            outfile = io.StringIO()
            self.editor._asciidoc_api.execute(infile, outfile, backend="html5")
            html_content = outfile.getvalue()

            temp_source_file = Path(self.editor._temp_dir.name) / f"temp_{uuid.uuid4().hex}.html"
            temp_source_file.write_text(html_content, encoding="utf-8")
            return temp_source_file
        except Exception as e:
            logger.exception(f"Failed to convert AsciiDoc to HTML: {e}")
            self.editor.status_manager.show_message(
                "critical", "Conversion Error", f"Failed to convert AsciiDoc to HTML:\n{e}"
            )
            return None

    def save_to_temp_file(self, content: str, source_format: str) -> Path | None:
        """
        Save content to temporary file for Pandoc processing.

        Args:
            content: Content to save
            source_format: Format type ("markdown", "docx", "html")

        Returns:
            Path to temp file or None if save failed

        MA principle: Extracted from save_as_format_internal (12 lines).
        """
        ext_map = {"markdown": ".md", "docx": ".docx", "html": ".html"}
        temp_ext = ext_map.get(source_format, ".txt")
        temp_source_file = Path(self.editor._temp_dir.name) / f"temp_{uuid.uuid4().hex}{temp_ext}"
        try:
            temp_source_file.write_text(content, encoding="utf-8")
            return temp_source_file
        except Exception as e:
            self.editor.status_manager.show_message("critical", "Save Error", f"Failed to create temporary file:\n{e}")
            return None

    def emit_pandoc_conversion(
        self,
        temp_source_file: Path,
        format_type: str,
        source_format: str,
        file_path: Path,
        use_ai: bool,
    ) -> None:
        """
        Emit Pandoc conversion request signal.

        Args:
            temp_source_file: Temporary source file path
            format_type: Target format type
            source_format: Source format type
            file_path: Final output file path
            use_ai: Whether to use AI conversion

        MA principle: Extracted from save_as_format_internal (32 lines).
        """
        self.editor.status_bar.showMessage(f"Saving as {format_type.upper()}...")

        # Set export manager pending paths for result handling
        self.editor.export_manager.pending_export_path = file_path
        self.editor.export_manager.pending_export_format = format_type

        if format_type in ["pdf", "docx"]:
            # Use Pandoc for PDF and DOCX conversion - pass output file directly
            logger.info(
                f"Emitting pandoc conversion request for {format_type} - "
                f"source: {temp_source_file} ({source_format}), "
                f"output: {file_path}"
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
