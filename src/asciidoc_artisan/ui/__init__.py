"""
===============================================================================
UI MODULE - User Interface Components Entry Point
===============================================================================

FILE PURPOSE:
This is the __init__.py file for the ui subpackage. It controls what users
can import when they do: "from asciidoc_artisan.ui import X"

WHAT THIS MODULE CONTAINS:
The ui module has all the visual components (windows, dialogs, buttons, menus)
that users see and interact with. It's built on PySide6 (Qt for Python).

FOR BEGINNERS - WHAT IS THE UI MODULE?:
Think of building a house. The ui module contains all the things you can see
and touch:
- Windows (main_window.py) = the house itself
- Dialogs (dialogs.py) = pop-up rooms for special tasks
- Managers (theme_manager.py, status_manager.py) = the systems that control
  lights, temperature, and other features

The "core" module (../core/) is like the electrical wiring and plumbing - you
don't see it, but it makes everything work.

ARCHITECTURE PATTERN:
This app uses the "Manager Pattern" - instead of one huge file doing everything,
we split the UI into specialized managers:

┌─────────────────────────────────────────────────────────────┐
│                     AsciiDocEditor                          │
│                   (Main Window - 561 lines)                 │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┬─────────────┐
        │                   │                   │             │
┌───────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐  ┌───▼────┐
│ThemeManager  │    │StatusManager│    │ActionManager│  │ etc... │
│(Dark/Light)  │    │(Status Bar) │    │(Menus)      │  │        │
└──────────────┘    └─────────────┘    └─────────────┘  └────────┘

WHY MANAGERS?:
Before v1.1, the main window was 1,719 lines - too big!
After refactoring into managers: only 561 lines - much cleaner!

KEY COMPONENTS:
- AsciiDocEditor: Main window (the whole app)
- PreferencesDialog: Settings window (Edit → Preferences)
- ThemeManager: Controls dark/light mode and CSS
- StatusManager: Status bar at bottom (shows messages, document version)
- SettingsManager: Saves/loads user settings (window size, theme, etc.)
- APIKeySetupDialog: Dialog for entering API keys (for AI features)
- LineNumberPlainTextEdit: Text editor with line numbers on the left

RE-EXPORT PATTERN:
Instead of forcing users to write long paths:
  from asciidoc_artisan.ui.main_window import AsciiDocEditor  # Long!

We re-export here so they can write:
  from asciidoc_artisan.ui import AsciiDocEditor  # Short, clean!

NOTE - NO LAZY IMPORTS HERE:
Unlike the main package __init__.py, this file uses direct imports (no __getattr__).
Why? The ui module is smaller, and all imports are fast (no heavy dependencies).
The main package uses lazy imports because it includes the entire application.

USAGE EXAMPLES:

    # === IMPORT MAIN WINDOW ===
    from asciidoc_artisan.ui import AsciiDocEditor
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    editor = AsciiDocEditor()
    editor.show()
    sys.exit(app.exec())

    # === IMPORT MANAGERS (Advanced Usage) ===
    from asciidoc_artisan.ui import ThemeManager, StatusManager

    # Use managers in custom Qt widgets
    theme_mgr = ThemeManager(my_widget)
    theme_mgr.apply_theme("dark")

VERSION HISTORY:
- v1.0: Monolithic main_window.py (1,719 lines)
- v1.1: Refactored into managers (561 lines main window)
- v1.2: Added Ollama AI integration
- v1.4.0: GPU hardware acceleration
- v1.5.0: Worker pool system, 67% size reduction
- v1.6.0: GitHub CLI integration (current)
"""

# === IMPORT UI COMPONENTS ===
# These imports bring classes from deeper modules into this namespace
# This is the "re-export pattern" - makes imports shorter and cleaner

# Dialog for entering API keys (for Ollama AI features)
from .api_key_dialog import APIKeySetupDialog

# Settings dialog window (Edit → Preferences menu)
from .dialogs import PreferencesDialog

# Text editor widget with line numbers (like VS Code, Notepad++)
from .line_number_area import LineNumberPlainTextEdit

# Main application window - the entire editor (most important class!)
from .main_window import AsciiDocEditor

# Manages loading/saving settings (window size, theme, recent files)
from .settings_manager import SettingsManager

# Manages status bar at bottom (messages, document version, progress)
from .status_manager import StatusManager

# Manages dark/light themes and CSS generation
from .theme_manager import ThemeManager

# === PUBLIC API DECLARATION ===
# The __all__ list defines what gets exported from this module
# This controls "from asciidoc_artisan.ui import *" behavior
#
# WHY __all__ MATTERS:
# Without __all__, users might import internal helper classes by accident
# With __all__, only these 7 intentional exports are available
#
# ORDER:
# Listed in order of importance (main window first, helpers last)
#
__all__ = [
    # Main application window (most important - the whole editor!)
    "AsciiDocEditor",
    # Dialogs (pop-up windows)
    "PreferencesDialog",  # Settings dialog (Edit → Preferences)
    "APIKeySetupDialog",  # API key entry dialog (for AI features)
    # Managers (coordinate different parts of the UI)
    "SettingsManager",  # Loads/saves user settings
    "ThemeManager",  # Controls dark/light themes and CSS
    "StatusManager",  # Controls status bar (messages, version, progress)
    # Custom widgets (reusable UI components)
    "LineNumberPlainTextEdit",  # Text editor with line numbers
]
