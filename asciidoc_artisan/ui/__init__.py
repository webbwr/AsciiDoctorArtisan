"""
UI module - User interface components for AsciiDoc Artisan.

This module contains QWidget-based UI classes:
- dialogs: Import/Export/Preferences dialogs
- main_window: AsciiDocEditor main window (pending extraction)

All UI components use PySide6 (Qt for Python) and implement the
application's graphical interface per the specification requirements.

Public API exports allow importing directly from asciidoc_artisan.ui:
    from asciidoc_artisan.ui import ImportOptionsDialog, PreferencesDialog
"""

from .dialogs import ExportOptionsDialog, ImportOptionsDialog, PreferencesDialog

__all__ = [
    "ImportOptionsDialog",
    "ExportOptionsDialog",
    "PreferencesDialog",
]
