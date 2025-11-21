"""
Path & Format Utilities - File path and format type resolution.

Extracted from FileOperationsManager to reduce class size (MA principle).
Provides static utility methods for file format detection and path manipulation.
"""

from pathlib import Path

from asciidoc_artisan.core import (
    DOCX_FILTER,
    HTML_FILTER,
    MD_FILTER,
    PDF_FILTER,
)


class PathFormatUtils:
    """
    Static utilities for file path and format type resolution.

    This class was extracted from FileOperationsManager to reduce class size
    per MA principle (865→~789 lines).

    Handles:
    - Format type detection from filter strings or file extensions
    - File extension validation and correction
    - Path manipulation for save operations
    """

    @staticmethod
    def determine_save_format(file_path: Path, selected_filter: str) -> tuple[str, Path]:
        """
        Determine save format and ensure file path has correct extension.

        Args:
            file_path: Initial file path from dialog
            selected_filter: Selected file filter from dialog

        Returns:
            Tuple of (format_type, corrected_file_path)

        MA principle: Reduced from 47→15 lines by extracting 2 helpers (68% reduction).
        """
        format_type = PathFormatUtils.get_format_from_filter_or_extension(selected_filter, file_path)
        corrected_path = PathFormatUtils.ensure_file_extension(file_path, format_type)
        return format_type, corrected_path

    @staticmethod
    def get_format_from_filter_or_extension(selected_filter: str, file_path: Path) -> str:
        """
        Determine format type from filter string or file extension.

        Args:
            selected_filter: Filter string from file dialog
            file_path: File path to check extension

        Returns:
            Format type string ("md", "docx", "html", "pdf", or "adoc")

        MA principle: Extracted helper (18 lines) - uses mapping for O(1) lookup.
        """
        # Map filter strings to format types
        filter_map = {
            MD_FILTER: "md",
            DOCX_FILTER: "docx",
            HTML_FILTER: "html",
            PDF_FILTER: "pdf",
        }

        # Check filter first
        for filter_str, format_type in filter_map.items():
            if filter_str in selected_filter:
                return format_type

        # Fall back to extension mapping
        ext = file_path.suffix.lower()
        ext_map = {
            ".md": "md",
            ".markdown": "md",
            ".docx": "docx",
            ".html": "html",
            ".htm": "html",
            ".pdf": "pdf",
        }

        return ext_map.get(ext, "adoc")

    @staticmethod
    def ensure_file_extension(file_path: Path, format_type: str) -> Path:
        """
        Add file extension if missing.

        Args:
            file_path: Original file path
            format_type: Desired format type

        Returns:
            Path with correct extension

        MA principle: Extracted helper (11 lines) - uses mapping for clean code.
        """
        if file_path.suffix:
            return file_path

        # Map format types to extensions
        ext_map = {
            "md": ".md",
            "docx": ".docx",
            "html": ".html",
            "pdf": ".pdf",
            "adoc": ".adoc",
        }

        extension = ext_map.get(format_type, ".adoc")
        return file_path.with_suffix(extension)
