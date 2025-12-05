"""
Core module - fundamental building blocks for AsciiDoc Artisan.

Contains settings, data models, file operations, constants, and utilities.
Uses hybrid import strategy: eager imports for commonly-used items,
lazy imports for constants and optional modules (3x faster startup).

Usage:
    from asciidoc_artisan.core import Settings, GitResult
    from asciidoc_artisan.core import sanitize_path, atomic_save_text
    from asciidoc_artisan.core import APP_NAME  # Lazy-loaded on first access
"""

from typing import Any

from . import json_utils, toon_utils
from .file_operations import atomic_save_json, atomic_save_text, atomic_save_toon, sanitize_path
from .settings import Settings

_CONSTANTS_CACHE: dict[str, Any] = {}
_MODULE_CACHE: dict[str, Any] = {}

_LAZY_IMPORT_MAP = {
    "constants": (
        "ADOC_FILTER",
        "ALL_FILES_FILTER",
        "ALL_FORMATS",
        "APP_NAME",
        "APP_VERSION",
        "AUTO_SAVE_INTERVAL_MS",
        "COMMON_FORMATS",
        "DEFAULT_FILENAME",
        "SETTINGS_FILENAME_JSON",
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
    "models": ("GitResult", "GitStatus", "GitHubResult", "ChatMessage"),
    "memory_profiler": ("MemoryProfiler", "MemorySnapshot", "get_profiler", "profile_memory"),
    "cpu_profiler": (
        "CPUProfiler",
        "ProfileResult",
        "get_cpu_profiler",
        "enable_cpu_profiling",
        "disable_cpu_profiling",
    ),
    "resource_monitor": ("ResourceMonitor", "get_resource_monitor", "monitor_memory"),
    "security": ("SecureCredentials",),
    "async_file_watcher": ("AsyncFileWatcher", "get_file_watcher", "monitor_file"),
    "spell_checker": ("SpellChecker", "get_spell_checker", "check_spelling"),
    "telemetry_collector": ("TelemetryCollector", "get_telemetry", "record_event"),
    "dependency_validator": ("DependencyValidator", "validate_dependencies", "check_dependency"),
    "qt_async_file_manager": ("QtAsyncFileManager",),
}


def _lazy_import(name: str, module_name: str, cache: dict[str, Any]) -> Any:
    """Lazily import an attribute from a module with caching."""
    if name not in cache:
        module = __import__(f"asciidoc_artisan.core.{module_name}", fromlist=[name])
        cache[name] = getattr(module, name)
    return cache[name]


def __getattr__(name: str) -> Any:
    """Lazy import handler - loads modules only when accessed."""
    if name in _LAZY_IMPORT_MAP["constants"]:
        return _lazy_import(name, "constants", _CONSTANTS_CACHE)

    for module_name, attr_names in _LAZY_IMPORT_MAP.items():
        if module_name == "constants":
            continue
        if name in attr_names:
            return _handle_module_import(name, module_name)

    result = _try_additional_attributes(name)
    if result is not None:
        return result

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def _handle_module_import(name: str, module_name: str) -> Any:
    """Handle import with special case handling for certain modules."""
    if name == "AsyncFileWatcher":
        return _lazy_import_special(name, "async_file_watcher")
    if name == "QtAsyncFileManager":
        return _lazy_import_special(name, "qt_async_file_manager")
    if name == "SecureCredentials":
        return _lazy_import_special(name, "secure_credentials")
    return _lazy_import(name, module_name, _MODULE_CACHE)


def _try_additional_attributes(name: str) -> Any | None:
    """Try importing additional attributes not in main lazy import map."""
    if name in ("DocumentMetrics", "ResourceMetrics"):
        return _lazy_import(name, "resource_monitor", _MODULE_CACHE)

    if name in (
        "async_read_text",
        "async_atomic_save_text",
        "async_atomic_save_json",
        "async_read_json",
        "async_copy_file",
        "AsyncFileContext",
    ):
        return _lazy_import(name, "async_file_ops", _MODULE_CACHE)

    if name in ("DependencyType", "DependencyStatus", "Dependency"):
        return _lazy_import(name, "dependency_validator", _MODULE_CACHE)

    if name == "SpellError":
        return _lazy_import(name, "spell_checker", _MODULE_CACHE)

    if name == "TelemetryEvent":
        return _lazy_import(name, "telemetry_collector", _MODULE_CACHE)

    return None


def _lazy_import_special(name: str, module_name: str) -> Any:
    """Special lazy import for single-class modules."""
    if name not in _MODULE_CACHE:
        module = __import__(f"asciidoc_artisan.core.{module_name}", fromlist=[name])
        _MODULE_CACHE[name] = getattr(module, name)
    return _MODULE_CACHE[name]


__all__ = [
    # Settings and models
    "Settings",
    "GitResult",
    "GitStatus",
    "GitHubResult",
    "ChatMessage",
    # Security
    "SecureCredentials",
    # Monitoring
    "ResourceMonitor",
    "ResourceMetrics",
    "DocumentMetrics",
    # Memory profiling
    "MemoryProfiler",
    "MemorySnapshot",
    "get_profiler",
    "profile_memory",
    # CPU profiling
    "CPUProfiler",
    "ProfileResult",
    "get_cpu_profiler",
    "enable_cpu_profiling",
    "disable_cpu_profiling",
    # File operations
    "sanitize_path",
    "atomic_save_text",
    "atomic_save_json",
    "atomic_save_toon",
    "json_utils",
    "toon_utils",
    # Async file operations
    "AsyncFileWatcher",
    "QtAsyncFileManager",
    "async_read_text",
    "async_atomic_save_text",
    "async_atomic_save_json",
    "async_read_json",
    "async_copy_file",
    "AsyncFileContext",
    # Spell checker
    "SpellChecker",
    "SpellError",
    # Telemetry
    "TelemetryCollector",
    "TelemetryEvent",
    # Dependency validator
    "DependencyValidator",
    "validate_dependencies",
    "DependencyType",
    "DependencyStatus",
    "Dependency",
    # Constants - Application
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_FILENAME",
    "SETTINGS_FILENAME",
    "SETTINGS_FILENAME_JSON",
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
    # Constants - File limits
    "LARGE_FILE_THRESHOLD_BYTES",
    "MAX_FILE_SIZE_MB",
    # Constants - File filters
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
    # Constants - Menu
    "MENU_FILE",
    "STATUS_TIP_EXPORT_OFFICE365",
]
