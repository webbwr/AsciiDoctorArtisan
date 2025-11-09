"""
===============================================================================
CORE MODULE - Fundamental Building Blocks Entry Point
===============================================================================

FILE PURPOSE:
This is the __init__.py file for the core subpackage. It contains the
"behind-the-scenes" code that makes the application work - like the engine
and wiring in a car.

WHAT THIS MODULE CONTAINS:
The core module has all the fundamental building blocks:
- Settings (saves user preferences like theme, font size)
- Data models (GitResult, GitHubResult - structures for Git data)
- File operations (safe file reading/writing to prevent corruption)
- Constants (APP_NAME, EDITOR_FONT_SIZE - values used everywhere)
- Security (SecureCredentials - stores API keys safely)
- Resource monitoring (tracks memory usage, file sizes)
- Memory profiling (finds memory leaks for developers)

FOR BEGINNERS - WHAT IS THE CORE MODULE?:
Think of building a car:
- The ui module (../ui/) = the car's body, seats, steering wheel (what you see)
- The core module (this one) = the engine, transmission, wiring (what makes it work)
- The workers module (../workers/) = the factory robots building the car (background tasks)

You don't see the core module when using the app, but everything depends on it!

ARCHITECTURE - HYBRID IMPORT STRATEGY:
This file uses a smart two-tier import system for performance:

┌─────────────────────────────────────────────────────────────┐
│                    HYBRID IMPORT STRATEGY                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  EAGER IMPORTS (loaded immediately at startup):            │
│  - Settings           (needed by main window)              │
│  - GitResult          (needed by Git operations)           │
│  - GitHubResult       (needed by GitHub operations)        │
│  - sanitize_path      (security - used everywhere)         │
│  - atomic_save_*      (security - used everywhere)         │
│                                                             │
│  LAZY IMPORTS (loaded only when first accessed):           │
│  - 50+ constants      (APP_NAME, EDITOR_FONT_SIZE, etc.)   │
│  - Memory profiler    (only used in debug mode)            │
│  - Resource monitor   (only used for performance tracking) │
│  - SecureCredentials  (only used if API keys configured)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘

WHY HYBRID IMPORTS?:
- Eager imports: Things we KNOW we'll use immediately (Settings, GitResult)
- Lazy imports: Things we MIGHT use later (constants, profiler, monitor)
- Result: Fast startup (1.05s) without loading 50+ constants at once!

CACHING MECHANISM:
When you import a lazy item for the first time, we cache it. Second access
is instant (no re-import needed). This is like bookmarking a page you visit
often - first visit requires searching, later visits are instant.

USAGE EXAMPLES:

    # === COMMON IMPORTS (Eager - Fast) ===
    from asciidoc_artisan.core import Settings, GitResult
    from asciidoc_artisan.core import sanitize_path, atomic_save_text

    # Use settings
    settings = Settings()
    settings.theme = "dark"

    # Safe file write (atomic - no corruption)
    atomic_save_text("/path/to/file.txt", "content")

    # === ADVANCED IMPORTS (Lazy - Loaded on First Use) ===
    from asciidoc_artisan.core import APP_NAME  # Lazy (first time loads constants.py)
    from asciidoc_artisan.core import APP_NAME  # Instant (cached from first time!)

    # Memory profiling (developers only)
    from asciidoc_artisan.core import get_profiler
    profiler = get_profiler()
    profiler.start()

VERSION HISTORY:
- v1.0: Basic settings and constants
- v1.1: Added SecureCredentials (OS keyring), ResourceMonitor (metrics)
- v1.2: Added Ollama AI integration support
- v1.4.0: Added GPU detection and memory profiling
- v1.5.0: Optimized with hybrid import strategy (3x faster startup)
- v1.6.0: Added GitHub CLI integration (GitHubResult model)
"""

from typing import Any

# Fast JSON utilities (v1.9.1 - 3-5x faster with orjson, used for settings at startup)
from . import json_utils

# === EAGER IMPORTS (Load Immediately) ===
# These are the most commonly used items - we import them RIGHT NOW (not lazily)
# because we know the main window will need them within the first second
# File operations (security-critical - used everywhere in the app)
from .file_operations import (
    atomic_save_json,  # Save JSON files atomically (no corruption risk)
    atomic_save_text,  # Save text files atomically (no corruption risk)
    sanitize_path,  # Clean file paths (prevent directory traversal attacks)
)

# Data models - MOVED TO LAZY LOADING (v1.9.1 optimization, saves 115ms startup time)
# These models import Pydantic (heavy library), so we load them only when first accessed.
# GitResult, GitStatus, GitHubResult are used by worker threads, so 115ms delay is not noticeable.
# Settings (used by main window immediately at startup)
from .settings import Settings  # Application settings (theme, font, recent files)

# === LAZY IMPORT CACHES ===
# These dictionaries store lazily-imported items after first access
# Think of them as "bookmarks" - first visit loads the module, later visits are instant

# Stores constants (APP_NAME, EDITOR_FONT_SIZE, etc.) after first access
_CONSTANTS_CACHE = {}

# Stores classes and functions (MemoryProfiler, ResourceMonitor, etc.) after first access
_MODULE_CACHE = {}


def __getattr__(name: str) -> Any:
    """
    Lazy Import Handler - Load Modules Only When Accessed.

    WHY THIS EXISTS:
    Loading 50+ constants and 3 heavy modules at startup takes time. Instead,
    we load them only when someone actually uses them. This makes startup
    3x faster (1.05s instead of 3-5s).

    HOW IT WORKS:
    1. Someone does: from asciidoc_artisan.core import APP_NAME
    2. Python looks for APP_NAME in this file
    3. APP_NAME doesn't exist yet (not imported)
    4. Python calls __getattr__("APP_NAME")
    5. We check: Is this a constant? Memory profiler? Resource monitor?
    6. Import the appropriate module and cache the result
    7. Return the value to the user
    8. Next time they access APP_NAME: instant (cached)

    CACHING STRATEGY:
    - First access: Import module + cache result (~1-10ms)
    - Second access: Return cached value (~0.001ms - instant!)

    This is like a library:
    - Without caching: Every time you need a book, search the entire library
    - With caching: First search is slow, then you bookmark it for instant access

    PARAMETERS:
        name: The attribute name someone tried to import

    RETURNS:
        The requested constant, class, or function

    RAISES:
        AttributeError: If name is not in our public API
    """
    # === GROUP 1: CONSTANTS (50+ Values) ===
    # These are string and numeric constants used throughout the app
    # All stored in constants.py - we import that file once and cache all accesses
    if name in (
        "ADOC_FILTER",  # File dialog filter: "AsciiDoc Files (*.adoc *.asciidoc)"
        "ALL_FILES_FILTER",  # File dialog filter: "All Files (*)"
        "ALL_FORMATS",  # List of all supported file formats
        "APP_NAME",  # "AsciiDoc Artisan" (application name)
        "APP_VERSION",  # "1.5.0" (current version)
        "AUTO_SAVE_INTERVAL_MS",  # 60000 (auto-save every 60 seconds)
        "COMMON_FORMATS",  # List of common file formats (DOCX, PDF, MD, HTML)
        "DEFAULT_FILENAME",  # "Untitled.adoc" (new file default name)
        "DIALOG_CONVERSION_ERROR",  # "Conversion Error" (dialog title)
        "DIALOG_OPEN_FILE",  # "Open File" (dialog title)
        "DIALOG_SAVE_ERROR",  # "Save Error" (dialog title)
        "DIALOG_SAVE_FILE",  # "Save File" (dialog title)
        "DOCX_FILTER",  # File dialog filter: "Word Documents (*.docx)"
        "EDITOR_FONT_FAMILY",  # "Courier New" (default editor font)
        "EDITOR_FONT_SIZE",  # 12 (default editor font size in points)
        "ERR_ASCIIDOC_NOT_INITIALIZED",  # Error message for uninitialized AsciiDoc
        "ERR_ATOMIC_SAVE_FAILED",  # Error message for failed atomic save
        "ERR_FAILED_CREATE_TEMP",  # Error message for failed temp file creation
        "ERR_FAILED_SAVE_HTML",  # Error message for failed HTML save
        "HTML_FILTER",  # File dialog filter: "HTML Files (*.html *.htm)"
        "LARGE_FILE_THRESHOLD_BYTES",  # 1048576 (1MB - files above this show warning)
        "LATEX_FILTER",  # File dialog filter: "LaTeX Files (*.tex)"
        "MAX_FILE_SIZE_MB",  # 50 (maximum file size in megabytes)
        "MD_FILTER",  # File dialog filter: "Markdown Files (*.md)"
        "MENU_FILE",  # "File" (File menu label)
        "MIN_FONT_SIZE",  # 6 (minimum allowed font size)
        "MIN_WINDOW_HEIGHT",  # 600 (minimum window height in pixels)
        "MIN_WINDOW_WIDTH",  # 800 (minimum window width in pixels)
        "MSG_LOADING_LARGE_FILE",  # "Loading large file..." (status message)
        "MSG_PDF_IMPORTED",  # "PDF imported successfully" (status message)
        "MSG_SAVED_ASCIIDOC",  # "Saved as AsciiDoc" (status message)
        "MSG_SAVED_HTML",  # "Saved as HTML" (status message)
        "MSG_SAVED_HTML_PDF_READY",  # "Saved as HTML (ready for PDF)" (status)
        "ORG_FILTER",  # File dialog filter: "Org-mode Files (*.org)"
        "PDF_FILTER",  # File dialog filter: "PDF Files (*.pdf)"
        "PREVIEW_FAST_INTERVAL_MS",  # 100 (100ms - fast preview update interval)
        "PREVIEW_NORMAL_INTERVAL_MS",  # 500 (500ms - normal preview update interval)
        "PREVIEW_SLOW_INTERVAL_MS",  # 1000 (1000ms - slow preview update interval)
        "PREVIEW_UPDATE_INTERVAL_MS",  # 500 (default preview update interval)
        "RST_FILTER",  # File dialog filter: "reStructuredText Files (*.rst)"
        "SETTINGS_FILENAME",  # "AsciiDocArtisan.json" (settings file name)
        "STATUS_MESSAGE_DURATION_MS",  # 3000 (status messages show for 3 seconds)
        "STATUS_TIP_EXPORT_OFFICE365",  # "Export to Word/Office365" (tooltip)
        "SUPPORTED_OPEN_FILTER",  # Combined filter for Open dialog
        "SUPPORTED_SAVE_FILTER",  # Combined filter for Save dialog
        "TEXTILE_FILTER",  # File dialog filter: "Textile Files (*.textile)"
        "ZOOM_STEP",  # 1 (font size change per zoom step)
    ):
        # Check if we've already imported this constant
        if name not in _CONSTANTS_CACHE:
            # First time accessing this constant - import constants.py now
            from . import constants

            # Get the constant value and cache it
            _CONSTANTS_CACHE[name] = getattr(constants, name)

        # Return the cached value (instant on subsequent accesses)
        return _CONSTANTS_CACHE[name]

    # === GROUP 1B: DATA MODELS (Pydantic-based, lazy to save 115ms startup) ===
    # These models use Pydantic which takes 115ms to import.
    # Since they're used by background worker threads, lazy loading them doesn't affect UI.
    if name in ("GitResult", "GitStatus", "GitHubResult", "ChatMessage"):
        # Check if we've already imported this model
        if name not in _MODULE_CACHE:
            # First time accessing this model - import models.py now
            from . import models

            # Get the model class and cache it
            _MODULE_CACHE[name] = getattr(models, name)

        # Return the cached model class
        return _MODULE_CACHE[name]

    # === GROUP 2: MEMORY PROFILER (Developer Tools) ===
    # Only used when debugging memory leaks - rarely accessed
    if name in ("MemoryProfiler", "MemorySnapshot", "get_profiler", "profile_memory"):
        # Check if we've already imported memory_profiler module
        if name not in _MODULE_CACHE:
            # First time accessing memory profiler - import it now
            from . import memory_profiler

            # Get the class/function and cache it
            _MODULE_CACHE[name] = getattr(memory_profiler, name)

        # Return the cached class/function
        return _MODULE_CACHE[name]

    # === GROUP 2B: CPU PROFILER (Developer Tools - QA-15) ===
    # Only used when profiling CPU performance - rarely accessed
    if name in (
        "CPUProfiler",
        "ProfileResult",
        "get_cpu_profiler",
        "enable_cpu_profiling",
        "disable_cpu_profiling",
    ):
        # Check if we've already imported cpu_profiler module
        if name not in _MODULE_CACHE:
            # First time accessing CPU profiler - import it now
            from . import cpu_profiler

            # Get the class/function and cache it
            _MODULE_CACHE[name] = getattr(cpu_profiler, name)

        # Return the cached class/function
        return _MODULE_CACHE[name]

    # === GROUP 3: RESOURCE MONITOR (Performance Tracking) ===
    # Used for tracking memory usage and document metrics
    if name in ("DocumentMetrics", "ResourceMetrics", "ResourceMonitor"):
        # Check if we've already imported resource_monitor module
        if name not in _MODULE_CACHE:
            # First time accessing resource monitor - import it now
            from . import resource_monitor

            # Get the class and cache it
            _MODULE_CACHE[name] = getattr(resource_monitor, name)

        # Return the cached class
        return _MODULE_CACHE[name]

    # === GROUP 4: SECURITY (Credential Storage) ===
    # Only used if API keys are configured (optional feature)
    if name == "SecureCredentials":
        # Check if we've already imported SecureCredentials
        if name not in _MODULE_CACHE:
            # First time accessing credentials - import it now
            from .secure_credentials import SecureCredentials

            # Cache the class
            _MODULE_CACHE[name] = SecureCredentials

        # Return the cached class
        return _MODULE_CACHE[name]

    # === GROUP 5: ASYNC FILE OPERATIONS (v1.7.0 Task 4) ===
    # Async file I/O with Qt integration and file watching
    if name in (
        "AsyncFileWatcher",
        "QtAsyncFileManager",
        "async_read_text",
        "async_atomic_save_text",
        "async_atomic_save_json",
        "async_read_json",
        "async_copy_file",
        "AsyncFileContext",
    ):
        # Check if we've already imported this async component
        if name not in _MODULE_CACHE:
            # Determine which module to import from
            if name == "AsyncFileWatcher":
                from .async_file_watcher import AsyncFileWatcher

                _MODULE_CACHE[name] = AsyncFileWatcher
            elif name == "QtAsyncFileManager":
                from .qt_async_file_manager import QtAsyncFileManager

                _MODULE_CACHE[name] = QtAsyncFileManager
            else:
                # Import from async_file_ops
                from . import async_file_ops

                _MODULE_CACHE[name] = getattr(async_file_ops, name)

        # Return the cached class/function
        return _MODULE_CACHE[name]

    # === GROUP 6: SPELL CHECKER (v1.8.0) ===
    # Integrated spell checking with custom dictionary support
    if name in ("SpellChecker", "SpellError"):
        # Check if we've already imported spell checker
        if name not in _MODULE_CACHE:
            # First time accessing spell checker - import it now
            from . import spell_checker

            # Get the class and cache it
            _MODULE_CACHE[name] = getattr(spell_checker, name)

        # Return the cached class
        return _MODULE_CACHE[name]

    # === GROUP 7: TELEMETRY (v1.8.0) ===
    # Privacy-first usage analytics (opt-in only)
    if name in ("TelemetryCollector", "TelemetryEvent"):
        # Check if we've already imported telemetry collector
        if name not in _MODULE_CACHE:
            # First time accessing telemetry - import it now
            from . import telemetry_collector

            # Get the class and cache it
            _MODULE_CACHE[name] = getattr(telemetry_collector, name)

        # Return the cached class
        return _MODULE_CACHE[name]

    # === GROUP 8: DEPENDENCY VALIDATOR (v2.0.1) ===
    # Startup dependency validation for system and Python requirements
    if name in (
        "DependencyValidator",
        "validate_dependencies",
        "DependencyType",
        "DependencyStatus",
        "Dependency",
    ):
        # Check if we've already imported dependency validator
        if name not in _MODULE_CACHE:
            # First time accessing validator - import it now
            from . import dependency_validator

            # Get the class/function and cache it
            _MODULE_CACHE[name] = getattr(dependency_validator, name)

        # Return the cached class/function
        return _MODULE_CACHE[name]

    # === UNKNOWN ATTRIBUTE ===
    # If we get here, they asked for something not in our public API
    # Raise AttributeError (same as Python does for missing attributes)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# === PUBLIC API DECLARATION ===
# The __all__ list defines the "public API" - what users can import
# This controls "from asciidoc_artisan.core import *" behavior
#
# WHY SO MANY ITEMS? (78 items)
# The core module is the "toolbox" for the entire application. It contains
# all the fundamental values, classes, and functions that every part of the
# app needs. Think of it like a hardware store - lots of tools!
#
# ORGANIZATION:
# Items are grouped by category:
# 1. Core Classes (Settings, Models, Security, Monitoring)
# 2. File Operations (Security functions)
# 3. Constants - Application (name, version, filenames)
# 4. Constants - UI (fonts, window sizes, timing)
# 5. Constants - File Filters (for Open/Save dialogs)
# 6. Constants - Messages/Errors/Dialogs (user-facing text)
#
# IMPORT STYLE:
# Most users should import specific items (not use "*"):
#   from asciidoc_artisan.core import Settings, APP_NAME  # ✓ Good (explicit)
#   from asciidoc_artisan.core import *                    # ✗ Avoid (imports 78 items!)
#
__all__ = [
    # === CORE CLASSES - SETTINGS ===
    # Settings class for saving/loading user preferences
    "Settings",  # Main settings class (theme, font, recent files, window size)
    # === CORE CLASSES - DATA MODELS ===
    # Data structures for Git and GitHub operations
    "GitResult",  # Result from Git commands (success/failure, output, error)
    "GitStatus",  # Git repository status (branch, changes, conflicts, v1.9.0+)
    "GitHubResult",  # Result from GitHub CLI operations (PR/Issue management)
    "ChatMessage",  # Chat message data (Ollama AI chat, v1.7.0+)
    # === CORE CLASSES - SECURITY ===
    # Secure credential storage using OS keyring
    "SecureCredentials",  # Stores API keys safely in OS keyring (not plain text!)
    # === CORE CLASSES - PERFORMANCE MONITORING ===
    # Classes for tracking resource usage and document metrics
    "ResourceMonitor",  # Monitors memory usage, CPU, file sizes
    "ResourceMetrics",  # Data structure for resource measurements
    "DocumentMetrics",  # Data structure for document statistics
    # === CORE CLASSES - MEMORY PROFILING (Developer Tools) ===
    # Tools for finding memory leaks and optimization opportunities
    "MemoryProfiler",  # Main profiler class (start/stop, take snapshots)
    "MemorySnapshot",  # Snapshot of memory state at a point in time
    "get_profiler",  # Function to get singleton profiler instance
    "profile_memory",  # Decorator for profiling function memory usage
    # === CORE CLASSES - CPU PROFILING (Developer Tools - QA-15) ===
    # Tools for CPU performance analysis and hotspot detection
    "CPUProfiler",  # Main CPU profiler class (profile code blocks)
    "ProfileResult",  # CPU profile result data (time, hotspots)
    "get_cpu_profiler",  # Function to get singleton CPU profiler instance
    "enable_cpu_profiling",  # Enable global CPU profiling
    "disable_cpu_profiling",  # Disable global CPU profiling
    # === FILE OPERATIONS (Security Functions) ===
    # Safe file I/O to prevent corruption and security vulnerabilities
    "sanitize_path",  # Clean file paths (prevent directory traversal attacks)
    "atomic_save_text",  # Save text files atomically (no corruption if crash)
    "atomic_save_json",  # Save JSON files atomically (no corruption if crash)
    # === FAST JSON UTILITIES (v1.9.1 Performance Optimization) ===
    # High-performance JSON serialization (3-5x faster with orjson)
    "json_utils",  # Fast JSON module (loads, dumps, load, dump with orjson backend)
    # === ASYNC FILE OPERATIONS (v1.7.0 Task 4) ===
    # Non-blocking file I/O with Qt integration and file watching
    "AsyncFileWatcher",  # Monitor files for external changes (polling-based)
    "QtAsyncFileManager",  # Qt-integrated async file manager with signals
    "async_read_text",  # Read text file asynchronously (non-blocking)
    "async_atomic_save_text",  # Save text file asynchronously (atomic)
    "async_atomic_save_json",  # Save JSON file asynchronously (atomic)
    "async_read_json",  # Read JSON file asynchronously
    "async_copy_file",  # Copy file asynchronously (chunked for large files)
    "AsyncFileContext",  # Async context manager for file operations
    # === SPELL CHECKER (v1.8.0) ===
    # Integrated spell checking with custom dictionary support
    "SpellChecker",  # Main spell checker class (word checking, suggestions)
    "SpellError",  # Data structure for spelling errors (word, position, suggestions)
    # === TELEMETRY (v1.8.0) ===
    # Privacy-first usage analytics (opt-in only, local storage)
    "TelemetryCollector",  # Telemetry collector (event tracking, performance metrics)
    "TelemetryEvent",  # Data structure for telemetry events (type, timestamp, data)
    # === DEPENDENCY VALIDATOR (v2.0.1) ===
    # Startup dependency validation for system and Python requirements
    "DependencyValidator",  # Main validator class (checks all dependencies)
    "validate_dependencies",  # Convenience function for quick validation
    "DependencyType",  # Enum for dependency types (REQUIRED, OPTIONAL, PYTHON, SYSTEM)
    "DependencyStatus",  # Enum for validation status (INSTALLED, MISSING, etc.)
    "Dependency",  # Data structure for dependency information
    # === CONSTANTS - APPLICATION METADATA ===
    # Basic application information
    "APP_NAME",  # "AsciiDoc Artisan" (shown in title bar, about dialog)
    "APP_VERSION",  # "1.5.0" (current version number)
    "DEFAULT_FILENAME",  # "Untitled.adoc" (default name for new files)
    "SETTINGS_FILENAME",  # "AsciiDocArtisan.json" (settings file name)
    # === CONSTANTS - UI SETTINGS ===
    # User interface configuration values
    "PREVIEW_UPDATE_INTERVAL_MS",  # 500ms (how often preview refreshes)
    "EDITOR_FONT_FAMILY",  # "Courier New" (monospace font for editor)
    "EDITOR_FONT_SIZE",  # 12 (default font size in points)
    "MIN_FONT_SIZE",  # 6 (minimum allowed font size)
    "ZOOM_STEP",  # 1 (font size change per zoom in/out)
    "MIN_WINDOW_WIDTH",  # 800 (minimum window width in pixels)
    "MIN_WINDOW_HEIGHT",  # 600 (minimum window height in pixels)
    # === CONSTANTS - TIMING ===
    # Time intervals for various operations (all in milliseconds)
    "AUTO_SAVE_INTERVAL_MS",  # 60000 (auto-save every 60 seconds)
    "PREVIEW_FAST_INTERVAL_MS",  # 100 (fast preview updates - 100ms)
    "PREVIEW_NORMAL_INTERVAL_MS",  # 500 (normal preview updates - 500ms)
    "PREVIEW_SLOW_INTERVAL_MS",  # 1000 (slow preview updates - 1 second)
    "STATUS_MESSAGE_DURATION_MS",  # 3000 (status messages show for 3 seconds)
    # === CONSTANTS - FILE SIZE LIMITS ===
    # Thresholds for large files and size limits
    "LARGE_FILE_THRESHOLD_BYTES",  # 1048576 (1MB - show warning for larger)
    "MAX_FILE_SIZE_MB",  # 50 (maximum file size in megabytes)
    # === CONSTANTS - FILE FILTERS (For Open/Save Dialogs) ===
    # These strings are used in Qt file dialogs to filter file types
    # Format: "Description (*.extension *.ext2)"
    "ADOC_FILTER",  # "AsciiDoc Files (*.adoc *.asciidoc)"
    "DOCX_FILTER",  # "Word Documents (*.docx)"
    "PDF_FILTER",  # "PDF Files (*.pdf)"
    "MD_FILTER",  # "Markdown Files (*.md)"
    "HTML_FILTER",  # "HTML Files (*.html *.htm)"
    "LATEX_FILTER",  # "LaTeX Files (*.tex)"
    "RST_FILTER",  # "reStructuredText Files (*.rst)"
    "ORG_FILTER",  # "Org-mode Files (*.org)"
    "TEXTILE_FILTER",  # "Textile Files (*.textile)"
    "ALL_FILES_FILTER",  # "All Files (*)" (no filter)
    # Grouped filters (lists of formats)
    "COMMON_FORMATS",  # ["DOCX", "PDF", "MD", "HTML"] (most-used formats)
    "ALL_FORMATS",  # All supported formats (for advanced users)
    # Combined filters (multiple formats in one filter string)
    "SUPPORTED_OPEN_FILTER",  # All formats the app can open
    "SUPPORTED_SAVE_FILTER",  # All formats the app can save to
    # === CONSTANTS - USER MESSAGES ===
    # Messages shown in the status bar after operations
    "MSG_SAVED_ASCIIDOC",  # "Saved as AsciiDoc"
    "MSG_SAVED_HTML",  # "Saved as HTML"
    "MSG_SAVED_HTML_PDF_READY",  # "Saved as HTML (ready for PDF conversion)"
    "MSG_PDF_IMPORTED",  # "PDF imported successfully"
    "MSG_LOADING_LARGE_FILE",  # "Loading large file... this may take a moment"
    # === CONSTANTS - ERROR MESSAGES ===
    # Error messages for common failure cases
    "ERR_ASCIIDOC_NOT_INITIALIZED",  # "AsciiDoc converter not initialized"
    "ERR_ATOMIC_SAVE_FAILED",  # "Failed to save file atomically"
    "ERR_FAILED_SAVE_HTML",  # "Failed to save HTML file"
    "ERR_FAILED_CREATE_TEMP",  # "Failed to create temporary file"
    # === CONSTANTS - DIALOG TITLES ===
    # Titles for various dialogs (shown in dialog title bar)
    "DIALOG_OPEN_FILE",  # "Open File"
    "DIALOG_SAVE_FILE",  # "Save File"
    "DIALOG_SAVE_ERROR",  # "Save Error"
    "DIALOG_CONVERSION_ERROR",  # "Conversion Error"
    # === CONSTANTS - MENU LABELS ===
    # Labels for menu items
    "MENU_FILE",  # "File" (File menu label)
    # === CONSTANTS - STATUS TIPS ===
    # Tooltips shown in status bar when hovering over menu items
    "STATUS_TIP_EXPORT_OFFICE365",  # "Export to Word/Office365 format"
]
