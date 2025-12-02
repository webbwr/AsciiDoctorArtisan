"""
File Open Handler - Handles file open operations with format conversion.

Extracted from FileOperationsManager to reduce class size (MA principle).
Manages file dialogs, format detection, and conversion routing (PDF/Pandoc/native).
"""

import logging
import platform
from pathlib import Path
from typing import Protocol, cast

from PySide6.QtWidgets import QFileDialog, QWidget

from asciidoc_artisan.core import SUPPORTED_OPEN_FILTER
from asciidoc_artisan.core.large_file_handler import LargeFileHandler

logger = logging.getLogger(__name__)


class FileOpsContext(Protocol):
    """Protocol for file operations context (FileOperationsManager)."""

    _is_processing_pandoc: bool
    _pending_file_path: Path | None
    editor: object  # Reference to main window (AsciiDocEditor)


class FileOpenHandler:
    """
    File open operations handler with format conversion support.

    This class was extracted from FileOperationsManager to reduce class size
    per MA principle (572→~362 lines).

    Handles:
    - File open dialog with unsaved changes prompt
    - Format detection by extension
    - PDF text extraction (PyMuPDF)
    - Pandoc conversion for DOCX/MD/HTML/etc
    - Native AsciiDoc loading with large file optimization
    """

    def __init__(self, file_ops_mgr: FileOpsContext) -> None:
        """
        Initialize file open handler.

        Args:
            file_ops_mgr: File operations manager context
        """
        self.mgr = file_ops_mgr

    def open_file(self) -> None:
        """
        Open file with format conversion support.

        Handles:
        - Reentrancy guard check
        - Unsaved changes prompt
        - File dialog presentation
        - Format detection and routing

        MA principle: Extracted from FileOperationsManager (100 lines).
        """
        # Check reentrancy guard
        if self.mgr._is_processing_pandoc:
            self.mgr.editor.status_manager.show_message("warning", "Busy", "Already processing a file conversion.")
            return

        # Check unsaved changes (access via editor, the main window)
        if hasattr(self.mgr.editor, "_unsaved_changes") and self.mgr.editor._unsaved_changes:
            if not self.mgr.editor.status_manager.prompt_save_before_action("opening a new file"):
                return

        # Show file dialog
        file_path_str, _ = QFileDialog.getOpenFileName(
            cast(QWidget, self.mgr),
            "Open File",
            self.mgr.editor._settings.last_directory,
            SUPPORTED_OPEN_FILTER,
            options=(
                QFileDialog.Option.DontUseNativeDialog if platform.system() != "Windows" else QFileDialog.Option(0)
            ),
        )

        if not file_path_str:
            return

        file_path = Path(file_path_str)
        self.mgr.editor._settings.last_directory = str(file_path.parent)

        # Route to appropriate handler based on extension
        try:
            suffix = file_path.suffix.lower()
            if suffix == ".pdf":
                self.open_pdf_with_extraction(file_path)
            elif suffix in [".docx", ".md", ".markdown", ".html", ".htm", ".tex", ".rst", ".org", ".textile"]:
                self.open_with_pandoc_conversion(file_path, suffix)
            else:
                self.open_native_file(file_path)
        except Exception as e:
            logger.exception(f"Failed to open file: {file_path}")
            self.mgr.editor.status_manager.show_message("critical", "Error", f"Failed to open file:\n{e}")

    def open_pdf_with_extraction(self, file_path: Path) -> None:
        """
        Import PDF file via text extraction.

        Args:
            file_path: Path to PDF file to import

        MA principle: Extracted from FileOperationsManager (35 lines).
        """
        from asciidoc_artisan.document_converter import pdf_extractor

        if not pdf_extractor.is_available():
            self.mgr.editor.status_manager.show_message(
                "warning",
                "PDF Support Unavailable",
                "PDF text extraction requires PyMuPDF.\n\n"
                "To install:\n"
                "  pip install pymupdf\n\n"
                "After installation, restart the application.",
            )
            return

        self.mgr.editor.status_bar.showMessage(f"Extracting text from PDF: {file_path.name}...")

        success, asciidoc_text, error_msg = pdf_extractor.convert_to_asciidoc(file_path)

        if not success:
            self.mgr.editor.status_manager.show_message(
                "critical",
                "PDF Extraction Failed",
                f"Failed to extract text from PDF:\n\n{error_msg}\n\n"
                "The PDF may be encrypted, image-based, or corrupted.",
            )
            return

        # Load extracted content into editor
        self.mgr.editor.file_load_manager.load_content_into_editor(asciidoc_text, file_path)
        self.mgr.editor.status_bar.showMessage(f"PDF imported successfully: {file_path.name}", 5000)

    def open_with_pandoc_conversion(self, file_path: Path, suffix: str) -> None:
        """
        Open file with Pandoc format conversion.

        Args:
            file_path: Path to file to import
            suffix: File extension (e.g., '.docx', '.md')

        MA principle: Extracted from FileOperationsManager (55 lines).
        """
        if not self.mgr.editor.ui_state_manager.check_pandoc_availability(f"Opening {suffix.upper()[1:]}"):
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

        # Use settings preference for AI conversion
        use_ai_for_import = self.mgr.editor._settings_manager.get_ai_conversion_preference(self.mgr.editor._settings)

        self.mgr._is_processing_pandoc = True
        self.mgr._pending_file_path = file_path
        self.mgr.editor._update_ui_state()

        self.mgr.editor.editor.setPlainText(f"// Converting {file_path.name} to AsciiDoc...\n// Please wait...")
        self.mgr.editor.preview.setHtml(
            "<h3>Converting document...</h3><p>The preview will update when conversion is complete.</p>"
        )
        self.mgr.editor.status_bar.showMessage(
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

        self.mgr.editor.request_pandoc_conversion.emit(
            file_content,
            "asciidoc",
            input_format,
            f"converting '{file_path.name}'",
            None,
            use_ai_for_import,
        )

    def open_native_file(self, file_path: Path) -> None:
        """
        Open native AsciiDoc file with large file optimization.

        Args:
            file_path: Path to AsciiDoc file to open

        MA principle: Extracted from FileOperationsManager (19 lines).
        """
        # Use optimized loading for large files
        category = LargeFileHandler.get_file_size_category(file_path)

        if category in ["medium", "large"]:
            logger.info(f"Loading {category} file with optimizations")
            success, content, error = self.mgr.editor.large_file_handler.load_file_optimized(file_path)
            if not success:
                raise Exception(error)
        else:
            content = file_path.read_text(encoding="utf-8")

        self.mgr.editor.file_load_manager.load_content_into_editor(content, file_path)
