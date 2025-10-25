"""
UI module - User interface components for AsciiDoc Artisan.

This module contains QWidget-based UI classes:
- dialogs: Import/Export/Preferences dialogs
- main_window: AsciiDocEditor main window (application controller)
- settings_manager: Settings persistence and UI state restoration
- menu_manager: Menu and action management (Phase 2 refactoring)
- theme_manager: Theme and appearance management (Phase 2 refactoring)
- status_manager: Status bar and UI feedback (Phase 2 refactoring)
- line_number_area: Line number display for editor (Editor requirement)

All UI components use PySide6 (Qt for Python) and implement the
application's graphical interface per the specification requirements.

Public API exports allow importing directly from asciidoc_artisan.ui:
    from asciidoc_artisan.ui import AsciiDocEditor, ImportOptionsDialog
    from asciidoc_artisan.ui import MenuManager, ThemeManager, StatusManager
"""

from .api_key_dialog import APIKeySetupDialog
from .dialogs import ExportOptionsDialog, ImportOptionsDialog, PreferencesDialog
from .line_number_area import LineNumberPlainTextEdit
from .main_window import AsciiDocEditor
from .menu_manager import MenuManager
from .settings_manager import SettingsManager
from .status_manager import StatusManager
from .theme_manager import ThemeManager

__all__ = [
    "AsciiDocEditor",
    "ImportOptionsDialog",
    "ExportOptionsDialog",
    "PreferencesDialog",
    "SettingsManager",
    "MenuManager",
    "ThemeManager",
    "StatusManager",
    "APIKeySetupDialog",
    "LineNumberPlainTextEdit",
]
