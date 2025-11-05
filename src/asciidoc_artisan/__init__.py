"""
===============================================================================
PACKAGE ENTRY POINT - The Front Door to asciidoc_artisan Package
===============================================================================

FILE PURPOSE:
This is the __init__.py file for the main asciidoc_artisan package. In Python,
__init__.py files turn folders into "packages" that can be imported. This file
controls what users see when they do: "from asciidoc_artisan import X"

FOR BEGINNERS - WHAT IS __init__.py?:
Think of a Python package as a library. The __init__.py file is like the
library's front desk - it decides which books (classes/functions) are easy
to check out, and which require going deeper into the shelves.

ANALOGY:
  Without __init__.py:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor  # Long path!

  With __init__.py (exports AsciiDocEditor):
    from asciidoc_artisan import AsciiDocEditor  # Short, clean!

The __init__.py file "re-exports" things from deeper modules to make them
easily accessible. This is called "creating a public API."

WHAT THIS FILE DOES:
1. Defines the package version (__version__ = "1.9.0")
2. Re-exports commonly used classes/functions (public API)
3. Uses LAZY IMPORTS for fast startup (1.05s target)
4. Lists all exports in __all__ (for "from X import *")

PACKAGE ARCHITECTURE:
asciidoc_artisan/
├── __init__.py (this file - package entry point)
├── core/ (business logic, utilities, constants)
│   ├── __init__.py
│   ├── settings.py (Settings class)
│   ├── models.py (GitResult, etc.)
│   └── ... (20+ utility files)
├── ui/ (user interface - Qt widgets)
│   ├── __init__.py
│   ├── main_window.py (AsciiDocEditor)
│   ├── dialogs.py (PreferencesDialog)
│   └── ... (30+ UI files)
└── workers/ (background threads)
    ├── __init__.py
    ├── git_worker.py (GitWorker)
    ├── pandoc_worker.py (PandocWorker)
    └── ... (10+ worker files)

LAZY IMPORT PATTERN (Performance Optimization):
Instead of importing everything at package load time (slow startup):
  from .ui import AsciiDocEditor  # Loads entire UI module!

We use __getattr__() to import only when accessed (fast startup):
  def __getattr__(name):
      if name == "AsciiDocEditor":
          from .ui import AsciiDocEditor  # Only loads when used!
          return AsciiDocEditor

This is why startup is 1.05 seconds instead of 3-5 seconds!

PUBLIC API (What Users Can Import):
    from asciidoc_artisan import ...

    # Main Application
    - AsciiDocEditor: Main window (the whole editor)

    # Settings & Data Models
    - Settings: Application settings (save location, theme, etc.)
    - GitResult: Data from Git operations (success/failure, output)

    # Background Workers (Threading)
    - GitWorker: Runs Git commands without freezing UI
    - PandocWorker: Converts documents without freezing UI
    - PreviewWorker: Renders preview without freezing UI

    # UI Components
    - PreferencesDialog: Settings window (Edit → Preferences)

    # Security Functions (Atomic file writes, path sanitization)
    - sanitize_path: Prevent directory traversal attacks
    - atomic_save_text: Save files without corruption risk
    - atomic_save_json: Save JSON files atomically

    # Constants
    - APP_NAME: "AsciiDoc Artisan"
    - DEFAULT_FILENAME: "Untitled.adoc"
    - SETTINGS_FILENAME: "AsciiDocArtisan.json"
    - etc.

VERSION 1.5.0 FEATURES:
Performance:
- ⚡ 1.05s startup (meets 1.5s target)
- 🚀 GPU-accelerated preview (10-50x faster)
- 🧵 Worker pool with task prioritization
- ⏹️ Operation cancellation support

Code Quality:
- 📉 Main window: 1719 → 577 lines (66% reduction)
- ✅ 60%+ test coverage (681+ tests)
- 📊 Metrics collection system
- 🔍 Memory profiling tools
- 🖥️ NPU detection (Intel AI accelerators)

Architecture:
- 🏗️ Modular design (core/ui/workers)
- 🎯 Manager pattern (delegation not monolithic)
- 🔧 Type hints everywhere (NFR-016)
- 📚 Comprehensive docs (NFR-017)

SPECIFICATION COMPLIANCE:
✅ FR-001 to FR-053: All functional requirements
✅ Performance rules: Fast, cancellable, clean
✅ NFR-016: Type hints everywhere
✅ NFR-017: All classes/methods documented
✅ Technical debt: Resolved via refactoring

USAGE EXAMPLES:
"""

from typing import Any

"""

    # === SIMPLE USAGE (Most Common) ===
    # Just import and run the editor
    from asciidoc_artisan import AsciiDocEditor
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    editor = AsciiDocEditor()
    editor.show()
    sys.exit(app.exec())

    # === ADVANCED USAGE (Custom Integration) ===
    # Import workers and utilities for custom apps
    from asciidoc_artisan import (
        Settings,           # Application settings
        GitWorker,          # Git operations in background
        PandocWorker,       # Document conversion
        sanitize_path,      # Security function
        atomic_save_text,   # Safe file writes
    )

    # Use workers in your own app
    worker = GitWorker()
    worker.request_git_command.connect(my_handler)
    worker.run_command(["git", "status"], "/path/to/repo")

KEY LEARNING POINTS FOR BEGINNERS:
1. __init__.py makes folders into importable packages
2. Lazy imports improve startup performance
3. __getattr__() is Python magic method for dynamic attribute access
4. __all__ lists the "public API" (what users should import)
5. Re-exporting creates convenient shortcuts
"""

# === PACKAGE VERSION ===
# Semantic versioning: MAJOR.MINOR.PATCH
# 1.9.1 = Version 1, Release 9, Patch 1
__version__ = "1.9.1"


# === LAZY IMPORT MAGIC METHOD ===
# This is a Python "magic method" (special method with __ prefix and suffix)
# __getattr__ is called when someone tries to access an attribute that doesn't exist yet
def __getattr__(name: str) -> Any:
    """
    Lazy Import Handler - Only Load Modules When Actually Used.

    WHY THIS EXISTS:
    Normal imports happen immediately when Python loads this file:
        from .ui import AsciiDocEditor  # Loads ALL of ui module RIGHT NOW (slow!)

    Lazy imports wait until something is actually used:
        # Nothing loads yet...
        from asciidoc_artisan import AsciiDocEditor  # Still nothing!
        editor = AsciiDocEditor()  # NOW we load it!

    This makes startup 3x faster (1.05s vs 3-5s)!

    HOW IT WORKS:
    1. Someone does: from asciidoc_artisan import X
    2. Python looks for X in this file
    3. X doesn't exist yet (not imported)
    4. Python calls __getattr__("X")
    5. We import X now and return it
    6. User gets X, but only after they asked for it!

    This is called "lazy loading" or "deferred imports"

    PARAMETERS:
        name: The attribute name someone tried to import

    RETURNS:
        The requested class/function/constant

    RAISES:
        AttributeError: If name is not in our public API
    """
    # === CORE CONSTANTS (String values) ===
    if name in (
        "APP_NAME",  # "AsciiDoc Artisan"
        "DEFAULT_FILENAME",  # "Untitled.adoc"
        "EDITOR_FONT_SIZE",  # 12
        "SETTINGS_FILENAME",  # "AsciiDocArtisan.json"
        "SUPPORTED_OPEN_FILTER",  # File dialog filter string
        "SUPPORTED_SAVE_FILTER",  # File dialog filter string
    ):
        # Import ALL constants at once (they're in same file)
        from .core import (  # noqa: F401
            APP_NAME,
            DEFAULT_FILENAME,
            EDITOR_FONT_SIZE,
            SETTINGS_FILENAME,
            SUPPORTED_OPEN_FILTER,
            SUPPORTED_SAVE_FILTER,
        )

        # Return the one they asked for
        # locals() = dictionary of local variables
        # locals()[name] = get variable with this name
        return locals()[name]

    # === CORE DATA MODELS (Classes) ===
    if name in ("GitResult", "Settings"):
        from .core import GitResult, Settings  # noqa: F401

        return locals()[name]

    # === CORE SECURITY FUNCTIONS ===
    if name in ("atomic_save_json", "atomic_save_text", "sanitize_path"):
        from .core import (  # Save JSON files atomically (no corruption)  # noqa: F401  # Save text files atomically (no corruption)  # noqa: F401  # Clean file paths (prevent attacks); noqa: F401
            atomic_save_json,
            atomic_save_text,
            sanitize_path,
        )

        return locals()[name]

    # === UI COMPONENTS (Main Application Window) ===
    if name == "AsciiDocEditor":
        from .ui import AsciiDocEditor  # The main window class

        return AsciiDocEditor

    # === UI COMPONENTS (Dialogs) ===
    if name == "PreferencesDialog":
        from .ui import PreferencesDialog  # Settings dialog

        return PreferencesDialog

    # === WORKER CLASSES (Background Threads) ===
    if name in ("GitWorker", "PandocWorker", "PreviewWorker"):
        from .workers import GitWorker, PandocWorker, PreviewWorker  # noqa: F401

        return locals()[name]

    # === UNKNOWN ATTRIBUTE ===
    # If we get here, they asked for something not in our public API
    # Raise AttributeError (same as Python does for missing attributes)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# === PUBLIC API DECLARATION ===
# The __all__ list defines the "public API" - what users can import
# This controls "from asciidoc_artisan import *" behavior
#
# WHY __all__ EXISTS:
# Without __all__, "import *" imports EVERYTHING (messy, confusing)
# With __all__, only these items are imported (clean, intentional)
#
# EXAMPLE:
#   from asciidoc_artisan import *  # Only imports items in __all__
#   print(AsciiDocEditor)            # ✓ Works (in __all__)
#   print(_some_internal_function)   # ✗ Error (not in __all__)
#
# BEST PRACTICE:
# Most users should import specific items, not use "*":
#   from asciidoc_artisan import AsciiDocEditor  # ✓ Better (explicit)
#   from asciidoc_artisan import *                # ✗ Avoid (implicit)
#
__all__ = [
    # === VERSION STRING ===
    "__version__",  # Package version number (e.g., "1.7.0")
    # === MAIN APPLICATION ===
    "AsciiDocEditor",  # The main window - the entire editor application
    # === SETTINGS & DATA MODELS ===
    "Settings",  # Application settings (theme, font, recent files, etc.)
    "GitResult",  # Data from Git operations (success/failure, output, error)
    # === BACKGROUND WORKERS (Threading) ===
    "GitWorker",  # Runs Git commands without freezing the UI
    "PandocWorker",  # Converts documents without freezing the UI
    "PreviewWorker",  # Renders preview without freezing the UI
    # === UI DIALOGS ===
    "PreferencesDialog",  # Settings window (Edit → Preferences menu)
    # === FILE OPERATIONS (Security Functions) ===
    "sanitize_path",  # Clean file paths (prevent directory traversal attacks)
    "atomic_save_text",  # Save text files atomically (no corruption risk)
    "atomic_save_json",  # Save JSON files atomically (no corruption risk)
    # === CONSTANTS (Application-Wide Values) ===
    "APP_NAME",  # "AsciiDoc Artisan" (shown in title bar, taskbar)
    "DEFAULT_FILENAME",  # "Untitled.adoc" (new document name)
    "SETTINGS_FILENAME",  # "AsciiDocArtisan.json" (settings file name)
    "EDITOR_FONT_SIZE",  # 12 (default editor font size in points)
    "SUPPORTED_OPEN_FILTER",  # File dialog filter for opening files
    "SUPPORTED_SAVE_FILTER",  # File dialog filter for saving files
]
