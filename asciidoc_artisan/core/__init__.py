"""
Core module - Application constants, settings, models, and file operations.

This module contains the fundamental building blocks used throughout
the application:
- constants: Application-wide configuration values
- settings: Settings dataclass and persistence
- models: Core data structures (GitResult, etc.)
- file_operations: Secure file I/O utilities

Public API exports allow importing directly from asciidoc_artisan.core:
    from asciidoc_artisan.core import Settings, sanitize_path, EDITOR_FONT_SIZE
"""

# Settings
from .settings import Settings

# Models
from .models import GitResult

# File Operations
from .file_operations import atomic_save_json, atomic_save_text, sanitize_path

# Constants - import commonly used ones
from .constants import (
    ADOC_FILTER,
    ALL_FILES_FILTER,
    ALL_FORMATS,
    APP_NAME,
    COMMON_FORMATS,
    DEFAULT_FILENAME,
    DOCX_FILTER,
    EDITOR_FONT_FAMILY,
    EDITOR_FONT_SIZE,
    HTML_FILTER,
    LATEX_FILTER,
    MD_FILTER,
    MIN_FONT_SIZE,
    ORG_FILTER,
    PDF_FILTER,
    PREVIEW_UPDATE_INTERVAL_MS,
    RST_FILTER,
    SETTINGS_FILENAME,
    SUPPORTED_OPEN_FILTER,
    SUPPORTED_SAVE_FILTER,
    TEXTILE_FILTER,
    ZOOM_STEP,
)

__all__ = [
    # Settings
    "Settings",
    # Models
    "GitResult",
    # File Operations
    "sanitize_path",
    "atomic_save_text",
    "atomic_save_json",
    # Constants
    "APP_NAME",
    "DEFAULT_FILENAME",
    "SETTINGS_FILENAME",
    "PREVIEW_UPDATE_INTERVAL_MS",
    "EDITOR_FONT_FAMILY",
    "EDITOR_FONT_SIZE",
    "MIN_FONT_SIZE",
    "ZOOM_STEP",
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
]
