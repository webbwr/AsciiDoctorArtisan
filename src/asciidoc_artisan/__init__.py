"""
AsciiDoc Artisan - Cross-platform AsciiDoc editor with live preview.

This package provides a modular, well-structured implementation of the
AsciiDoc Artisan application per specification v1.5.0.

Architecture:
- core: Constants, settings, models, secure file operations, metrics, profiling
- workers: Background QThread workers (Git, Pandoc, Preview) + Worker Pool
- ui: User interface components (main window, managers, dialogs)

Public API exports the most commonly used classes and functions:
    from asciidoc_artisan import AsciiDocEditor, Settings, GitWorker

Complete Public API:
    # Main Application
    - AsciiDocEditor: Main application window (QMainWindow)

    # Settings & Models
    - Settings: Application settings dataclass
    - GitResult: Git operation result model

    # Workers (Background Threads)
    - GitWorker: Git version control operations
    - PandocWorker: Document format conversion (+ AI)
    - PreviewWorker: AsciiDoc HTML rendering

    # UI Components
    - PreferencesDialog: Application preferences

    # File Operations (Security Features)
    - sanitize_path: Path traversal prevention (FR-016)
    - atomic_save_text: Atomic file writes (FR-015)
    - atomic_save_json: Atomic JSON saves

    # Constants
    - APP_NAME, SETTINGS_FILENAME, etc.

v1.5.0 Features:
- Fast startup (1.05s) with lazy module loading
- Main window refactored to 577 lines (66% reduction)
- Worker pool system with task prioritization
- Operation cancellation support
- Metrics collection and memory profiling
- 60%+ test coverage with 681+ tests
- GPU-accelerated preview (10-50x faster)
- NPU detection and configuration

Specification Compliance:
- FR-001 to FR-053: All functional requirements implemented
- Performance Rules: Fast startup, cancellation, clean code, good tests
- NFR-016: Comprehensive type hints
- NFR-017: All classes/methods documented
- Technical Debt Resolved: Modular architecture

Usage:
    # Simple usage
    from asciidoc_artisan import AsciiDocEditor
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    editor = AsciiDocEditor()
    editor.show()
    sys.exit(app.exec())

    # Advanced usage
    from asciidoc_artisan import Settings, GitWorker, PandocWorker
    from asciidoc_artisan.core import atomic_save_text, sanitize_path
"""

__version__ = "1.5.0"


def __getattr__(name: str):
    """Lazy import for package exports to improve startup time."""
    # Core exports
    if name in ("APP_NAME", "DEFAULT_FILENAME", "EDITOR_FONT_SIZE",
                "SETTINGS_FILENAME", "SUPPORTED_OPEN_FILTER", "SUPPORTED_SAVE_FILTER"):
        from .core import (  # noqa: F401
            APP_NAME,
            DEFAULT_FILENAME,
            EDITOR_FONT_SIZE,
            SETTINGS_FILENAME,
            SUPPORTED_OPEN_FILTER,
            SUPPORTED_SAVE_FILTER,
        )
        return locals()[name]

    if name in ("GitResult", "Settings"):
        from .core import GitResult, Settings  # noqa: F401
        return locals()[name]

    if name in ("atomic_save_json", "atomic_save_text", "sanitize_path"):
        from .core import atomic_save_json, atomic_save_text, sanitize_path  # noqa: F401
        return locals()[name]

    # UI exports
    if name == "AsciiDocEditor":
        from .ui import AsciiDocEditor
        return AsciiDocEditor

    if name == "PreferencesDialog":
        from .ui import PreferencesDialog
        return PreferencesDialog

    # Worker exports
    if name in ("GitWorker", "PandocWorker", "PreviewWorker"):
        from .workers import GitWorker, PandocWorker, PreviewWorker  # noqa: F401
        return locals()[name]

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    # Version
    "__version__",
    # Main Application
    "AsciiDocEditor",
    # Settings & Models
    "Settings",
    "GitResult",
    # Workers
    "GitWorker",
    "PandocWorker",
    "PreviewWorker",
    # UI Dialogs
    "PreferencesDialog",
    # File Operations
    "sanitize_path",
    "atomic_save_text",
    "atomic_save_json",
    # Constants
    "APP_NAME",
    "DEFAULT_FILENAME",
    "SETTINGS_FILENAME",
    "EDITOR_FONT_SIZE",
    "SUPPORTED_OPEN_FILTER",
    "SUPPORTED_SAVE_FILTER",
]
