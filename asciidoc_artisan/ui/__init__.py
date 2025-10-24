"""
UI module - User interface components for AsciiDoc Artisan.

This module contains QWidget-based UI classes:
- dialogs: Import/Export/Preferences dialogs
- main_window: AsciiDocEditor main window (application controller)

All UI components use PySide6 (Qt for Python) and implement the
application's graphical interface per the specification requirements.

Public API exports allow importing directly from asciidoc_artisan.ui:
    from asciidoc_artisan.ui import AsciiDocEditor, ImportOptionsDialog
"""

from .dialogs import ExportOptionsDialog, ImportOptionsDialog, PreferencesDialog
from .main_window import AsciiDocEditor

__all__ = [
    "AsciiDocEditor",
    "ImportOptionsDialog",
    "ExportOptionsDialog",
    "PreferencesDialog",
]
