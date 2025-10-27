"""
Application constants and configuration values.

This module contains all application-wide constants including:
- Application metadata
- File format filters and patterns
- UI configuration defaults
- Timing parameters

Extracted from adp_windows.py as part of architectural refactoring
to resolve technical debt per specification line 1197.
"""

import platform

# Application Metadata
APP_NAME = "AsciiDoc Artisan"
APP_VERSION = "1.4.0-beta"  # Updated for GPU cache versioning
DEFAULT_FILENAME = "untitled.adoc"
SETTINGS_FILENAME = "AsciiDocArtisan.json"

# UI Configuration
PREVIEW_UPDATE_INTERVAL_MS = 350  # Preview debounce delay (FR-004)
EDITOR_FONT_FAMILY = "Consolas" if platform.system() == "Windows" else "Courier New"
EDITOR_FONT_SIZE = 12
MIN_FONT_SIZE = 8
ZOOM_STEP = 1

# File Format Filters
ADOC_FILTER = "AsciiDoc Files (*.adoc *.asciidoc)"
DOCX_FILTER = "Microsoft Word 365 Documents (*.docx)"
PDF_FILTER = "Adobe Acrobat PDF Files (*.pdf)"
MD_FILTER = "GitHub Markdown Files (*.md *.markdown)"
HTML_FILTER = "HTML Files (*.html *.htm)"
LATEX_FILTER = "LaTeX Files (*.tex)"
RST_FILTER = "reStructuredText Files (*.rst)"
ORG_FILTER = "Org Mode Files (*.org)"
TEXTILE_FILTER = "Textile Files (*.textile)"
ALL_FILES_FILTER = "All Files (*)"

# Format Patterns
COMMON_FORMATS = "*.adoc *.asciidoc *.docx *.pdf *.md *.markdown *.html *.htm"
ALL_FORMATS = "*.adoc *.asciidoc *.docx *.pdf *.md *.markdown *.html *.htm *.tex *.rst *.org *.textile"

# Combined Filters
SUPPORTED_OPEN_FILTER = (
    f"Common Formats ({COMMON_FORMATS});;"
    f"All Supported ({ALL_FORMATS});;"
    f"{ADOC_FILTER};;{MD_FILTER};;{DOCX_FILTER};;{HTML_FILTER};;"
    f"{LATEX_FILTER};;{RST_FILTER};;{PDF_FILTER};;{ALL_FILES_FILTER}"
)
SUPPORTED_SAVE_FILTER = (
    f"{ADOC_FILTER};;{MD_FILTER};;{DOCX_FILTER};;{HTML_FILTER};;"
    f"{PDF_FILTER};;{ALL_FILES_FILTER}"
)
