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
_CONSTANTS_CACHE: dict[str, Any] = {}

# Stores classes and functions (MemoryProfiler, ResourceMonitor, etc.) after first access
_MODULE_CACHE: dict[str, Any] = {}

# === LAZY IMPORT CONFIGURATION ===
# Maps attribute names to their source modules for lazy loading
_LAZY_IMPORT_MAP = {
    # Constants module (50+ values)
    "constants": (
        "ADOC_FILTER",
        "ALL_FILES_FILTER",
        "ALL_FORMATS",
        "APP_NAME",
        "APP_VERSION",
        "AUTO_SAVE_INTERVAL_MS",
        "COMMON_FORMATS",
        "DEFAULT_FILENAME",
        "DIALOG_CONVERSION_ERROR",
        "DIALOG_OPEN_FILE",
        "DIALOG_SAVE_ERROR",
        "DIALOG_SAVE_FILE",
        "DOCX_FILTER",
        "EDITOR_FONT_FAMILY",
        "EDITOR_FONT_SIZE",
        "ERR_ASCIIDOC_NOT_INITIALIZED",
        "ERR_ATOMIC_SAVE_FAILED",
        "ERR_FAILED_CREATE_TEMP",
        "ERR_FAILED_SAVE_HTML",
        "HTML_FILTER",
        "LARGE_FILE_THRESHOLD_BYTES",
        "LATEX_FILTER",
        "MAX_FILE_SIZE_MB",
        "MD_FILTER",
        "MENU_FILE",
        "MIN_FONT_SIZE",
        "MIN_WINDOW_HEIGHT",
        "MIN_WINDOW_WIDTH",
        "MSG_LOADING_LARGE_FILE",
        "MSG_PDF_IMPORTED",
        "MSG_SAVED_ASCIIDOC",
        "MSG_SAVED_HTML",
        "MSG_SAVED_HTML_PDF_READY",
        "ORG_FILTER",
        "PDF_FILTER",
        "PREVIEW_FAST_INTERVAL_MS",
        "PREVIEW_NORMAL_INTERVAL_MS",
        "PREVIEW_SLOW_INTERVAL_MS",
        "PREVIEW_UPDATE_INTERVAL_MS",
        "RST_FILTER",
        "SETTINGS_FILENAME",
        "STATUS_MESSAGE_DURATION_MS",
        "STATUS_TIP_EXPORT_OFFICE365",
        "SUPPORTED_OPEN_FILTER",
        "SUPPORTED_SAVE_FILTER",
        "TEXTILE_FILTER",
        "ZOOM_STEP",
    ),
    # Data models (Pydantic-based)
    "models": ("GitResult", "GitStatus", "GitHubResult", "ChatMessage"),
    # Memory profiler (developer tools)
    "memory_profiler": ("MemoryProfiler", "MemorySnapshot", "get_profiler", "profile_memory"),
    # CPU profiler (developer tools)
    "cpu_profiler": (
        "CPUProfiler",
        "ProfileResult",
        "get_cpu_profiler",
        "enable_cpu_profiling",
        "disable_cpu_profiling",
    ),
    # Resource monitor (performance tracking)
    "resource_monitor": ("ResourceMonitor", "get_resource_monitor", "monitor_memory"),
    # Security (credential storage)
    "security": ("SecureCredentials",),
    # Async file operations
    "async_file_watcher": ("AsyncFileWatcher", "get_file_watcher", "monitor_file"),
    # Spell checker
    "spell_checker": ("SpellChecker", "get_spell_checker", "check_spelling"),
    # Telemetry
    "telemetry_collector": ("TelemetryCollector", "get_telemetry", "record_event"),
    # Dependency validator
    "dependency_validator": ("DependencyValidator", "validate_dependencies", "check_dependency"),
    # Qt async file manager (v1.7.0)
    "qt_async_file_manager": ("QtAsyncFileManager",),
}


def _lazy_import(name: str, module_name: str, cache: dict[str, Any]) -> Any:
    """
    Helper to lazily import an attribute from a module.

    Args:
        name: Attribute name to import
        module_name: Module name to import from
        cache: Cache dictionary to use

    Returns:
        The requested attribute value
    """
    if name not in cache:
        # Import module and cache the attribute
        module = __import__(f"asciidoc_artisan.core.{module_name}", fromlist=[name])
        cache[name] = getattr(module, name)

    return cache[name]


def __getattr__(name: str) -> Any:
    """
    Lazy Import Handler - Load Modules Only When Accessed.

    Makes startup 3x faster (1.05s instead of 3-5s) by loading modules
    only when first accessed. Subsequent accesses are instant (cached).

    MA principle: Reduced from 66→25 lines by extracting 2 helper methods.

    Args:
        name: The attribute name to import

    Returns:
        The requested constant, class, or function

    Raises:
        AttributeError: If name is not in our public API
    """
    # Check constants first (most common case)
    if name in _LAZY_IMPORT_MAP["constants"]:
        return _lazy_import(name, "constants", _CONSTANTS_CACHE)

    # Check each module group
    for module_name, attr_names in _LAZY_IMPORT_MAP.items():
        if module_name == "constants":
            continue  # Already checked above

        if name in attr_names:
            return _handle_module_import(name, module_name)

    # Try additional attributes not in main map
    result = _try_additional_attributes(name)
    if result is not None:
        return result

    # Unknown attribute - raise error
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def _handle_module_import(name: str, module_name: str) -> Any:
    """
    Handle import for a specific module with special case handling.

    MA principle: Extracted from __getattr__ (18 lines).

    Args:
        name: Attribute name to import
        module_name: Module name containing the attribute

    Returns:
        The requested attribute
    """
    # Handle special cases for async file operations
    if name == "AsyncFileWatcher":
        return _lazy_import_special(name, "async_file_watcher")
    if name == "QtAsyncFileManager":
        return _lazy_import_special(name, "qt_async_file_manager")
    if name == "SecureCredentials":
        return _lazy_import_special(name, "secure_credentials")

    # Standard lazy import
    return _lazy_import(name, module_name, _MODULE_CACHE)


def _try_additional_attributes(name: str) -> Any | None:
    """
    Try importing additional attributes not in main lazy import map.

    MA principle: Extracted from __getattr__ (24 lines).

    Args:
        name: Attribute name to import

    Returns:
        The requested attribute, or None if not found
    """
    # Handle additional resource monitor attributes
    if name in ("DocumentMetrics", "ResourceMetrics"):
        return _lazy_import(name, "resource_monitor", _MODULE_CACHE)

    # Handle async file operations (multi-module group)
    if name in (
        "async_read_text",
        "async_atomic_save_text",
        "async_atomic_save_json",
        "async_read_json",
        "async_copy_file",
        "AsyncFileContext",
    ):
        return _lazy_import(name, "async_file_ops", _MODULE_CACHE)

    # Handle dependency validator additional attributes
    if name in ("DependencyType", "DependencyStatus", "Dependency"):
        return _lazy_import(name, "dependency_validator", _MODULE_CACHE)

    # Handle spell checker additional attributes
    if name == "SpellError":
        return _lazy_import(name, "spell_checker", _MODULE_CACHE)

    # Handle telemetry additional attributes
    if name == "TelemetryEvent":
        return _lazy_import(name, "telemetry_collector", _MODULE_CACHE)

    return None


def _lazy_import_special(name: str, module_name: str) -> Any:
    """
    Special lazy import for single-class modules.

    Args:
        name: Class name to import
        module_name: Module name to import from

    Returns:
        The requested class
    """
    if name not in _MODULE_CACHE:
        module = __import__(f"asciidoc_artisan.core.{module_name}", fromlist=[name])
        _MODULE_CACHE[name] = getattr(module, name)

    return _MODULE_CACHE[name]


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
