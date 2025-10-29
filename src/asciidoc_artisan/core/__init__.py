"""
Core module - Application constants, settings, models, and file operations.

This module contains the fundamental building blocks used throughout
the application:
- constants: Application-wide configuration values
- settings: Settings dataclass and persistence
- models: Core data structures (GitResult, etc.)
- file_operations: Secure file I/O utilities
- secure_credentials: OS keyring integration for API keys (v1.1 security feature)
- resource_monitor: System resource and document metrics tracking (v1.1 Phase 4)

Public API exports allow importing directly from asciidoc_artisan.core:
    from asciidoc_artisan.core import Settings, sanitize_path, EDITOR_FONT_SIZE
    from asciidoc_artisan.core import SecureCredentials
"""

# Eagerly import only the most commonly used items for best performance
from .file_operations import atomic_save_json, atomic_save_text, sanitize_path
from .models import GitHubResult, GitResult
from .settings import Settings

# Lazy load everything else via __getattr__
_CONSTANTS_CACHE = {}
_MODULE_CACHE = {}


def __getattr__(name: str):
    """Lazy import for core module exports to improve startup time."""
    # Check if it's a constant
    if name in (
        "ADOC_FILTER", "ALL_FILES_FILTER", "ALL_FORMATS", "APP_NAME", "APP_VERSION",
        "AUTO_SAVE_INTERVAL_MS", "COMMON_FORMATS", "DEFAULT_FILENAME",
        "DIALOG_CONVERSION_ERROR", "DIALOG_OPEN_FILE", "DIALOG_SAVE_ERROR",
        "DIALOG_SAVE_FILE", "DOCX_FILTER", "EDITOR_FONT_FAMILY", "EDITOR_FONT_SIZE",
        "ERR_ASCIIDOC_NOT_INITIALIZED", "ERR_ATOMIC_SAVE_FAILED", "ERR_FAILED_CREATE_TEMP",
        "ERR_FAILED_SAVE_HTML", "HTML_FILTER", "LARGE_FILE_THRESHOLD_BYTES",
        "LATEX_FILTER", "MAX_FILE_SIZE_MB", "MD_FILTER", "MENU_FILE", "MIN_FONT_SIZE",
        "MIN_WINDOW_HEIGHT", "MIN_WINDOW_WIDTH", "MSG_LOADING_LARGE_FILE", "MSG_PDF_IMPORTED",
        "MSG_SAVED_ASCIIDOC", "MSG_SAVED_HTML", "MSG_SAVED_HTML_PDF_READY",
        "ORG_FILTER", "PDF_FILTER", "PREVIEW_FAST_INTERVAL_MS",
        "PREVIEW_NORMAL_INTERVAL_MS", "PREVIEW_SLOW_INTERVAL_MS",
        "PREVIEW_UPDATE_INTERVAL_MS", "RST_FILTER", "SETTINGS_FILENAME",
        "STATUS_MESSAGE_DURATION_MS", "STATUS_TIP_EXPORT_OFFICE365",
        "SUPPORTED_OPEN_FILTER", "SUPPORTED_SAVE_FILTER", "TEXTILE_FILTER", "ZOOM_STEP"
    ):
        if name not in _CONSTANTS_CACHE:
            from . import constants
            _CONSTANTS_CACHE[name] = getattr(constants, name)
        return _CONSTANTS_CACHE[name]

    # Memory profiler exports
    if name in ("MemoryProfiler", "MemorySnapshot", "get_profiler", "profile_memory"):
        if name not in _MODULE_CACHE:
            from . import memory_profiler
            _MODULE_CACHE[name] = getattr(memory_profiler, name)
        return _MODULE_CACHE[name]

    # Resource monitor exports
    if name in ("DocumentMetrics", "ResourceMetrics", "ResourceMonitor"):
        if name not in _MODULE_CACHE:
            from . import resource_monitor
            _MODULE_CACHE[name] = getattr(resource_monitor, name)
        return _MODULE_CACHE[name]

    # Security exports
    if name == "SecureCredentials":
        if name not in _MODULE_CACHE:
            from .secure_credentials import SecureCredentials
            _MODULE_CACHE[name] = SecureCredentials
        return _MODULE_CACHE[name]

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Settings
    "Settings",
    # Models
    "GitResult",
    "GitHubResult",
    # Security
    "SecureCredentials",
    # Performance Monitoring
    "ResourceMonitor",
    "ResourceMetrics",
    "DocumentMetrics",
    # Memory Profiling
    "MemoryProfiler",
    "MemorySnapshot",
    "get_profiler",
    "profile_memory",
    # File Operations
    "sanitize_path",
    "atomic_save_text",
    "atomic_save_json",
    # Constants - Application
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_FILENAME",
    "SETTINGS_FILENAME",
    # Constants - UI
    "PREVIEW_UPDATE_INTERVAL_MS",
    "EDITOR_FONT_FAMILY",
    "EDITOR_FONT_SIZE",
    "MIN_FONT_SIZE",
    "ZOOM_STEP",
    "MIN_WINDOW_WIDTH",
    "MIN_WINDOW_HEIGHT",
    # Constants - Timing
    "AUTO_SAVE_INTERVAL_MS",
    "PREVIEW_FAST_INTERVAL_MS",
    "PREVIEW_NORMAL_INTERVAL_MS",
    "PREVIEW_SLOW_INTERVAL_MS",
    "STATUS_MESSAGE_DURATION_MS",
    # Constants - File Sizes
    "LARGE_FILE_THRESHOLD_BYTES",
    "MAX_FILE_SIZE_MB",
    # Constants - File Filters
    "ADOC_FILTER",
    "DOCX_FILTER",
    "PDF_FILTER",
    "MD_FILTER",
    "HTML_FILTER",
    "LATEX_FILTER",
    "RST_FILTER",
    "ORG_FILTER",
    "TEXTILE_FILTER",
    "ALL_FILES_FILTER",
    "COMMON_FORMATS",
    "ALL_FORMATS",
    "SUPPORTED_OPEN_FILTER",
    "SUPPORTED_SAVE_FILTER",
    # Constants - Messages
    "MSG_SAVED_ASCIIDOC",
    "MSG_SAVED_HTML",
    "MSG_SAVED_HTML_PDF_READY",
    "MSG_PDF_IMPORTED",
    "MSG_LOADING_LARGE_FILE",
    # Constants - Errors
    "ERR_ASCIIDOC_NOT_INITIALIZED",
    "ERR_ATOMIC_SAVE_FAILED",
    "ERR_FAILED_SAVE_HTML",
    "ERR_FAILED_CREATE_TEMP",
    # Constants - Dialogs
    "DIALOG_OPEN_FILE",
    "DIALOG_SAVE_FILE",
    "DIALOG_SAVE_ERROR",
    "DIALOG_CONVERSION_ERROR",
    # Constants - Menus
    "MENU_FILE",
    # Constants - Status Tips
    "STATUS_TIP_EXPORT_OFFICE365",
]
