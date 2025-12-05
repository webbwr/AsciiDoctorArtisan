"""
Main window signal definitions.

MA Principle: Extracted from main_window.py to reduce file size.
Signals are defined as a mixin class for clean separation.
"""

from PySide6.QtCore import Signal


class MainWindowSignalsMixin:
    """Mixin providing signal definitions for AsciiDocEditor."""

    # Git operations
    request_git_command = Signal(list, str)
    request_git_status = Signal(str)
    request_detailed_git_status = Signal(str)

    # GitHub operations
    request_github_command = Signal(str, dict)

    # Pandoc conversion
    request_pandoc_conversion = Signal(object, str, str, str, object, bool)

    # Preview rendering
    request_preview_render = Signal(str)

    # File loading
    request_load_file_content = Signal(str, object, str)
