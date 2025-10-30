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
APP_VERSION = "1.5.0"  # Current release version
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

# Window Settings
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# Auto-save Settings
AUTO_SAVE_INTERVAL_MS = 300000  # 5 minutes

# Preview Timer Settings
PREVIEW_FAST_INTERVAL_MS = 200  # For small documents
PREVIEW_NORMAL_INTERVAL_MS = 500  # For medium documents
PREVIEW_SLOW_INTERVAL_MS = 1000  # For large documents

# File Size Thresholds
LARGE_FILE_THRESHOLD_BYTES = 100000  # 100 KB
MAX_FILE_SIZE_MB = 500  # Maximum file size for opening (Security: DoS prevention)

# Status Messages
MSG_SAVED_ASCIIDOC = "Saved as AsciiDoc: {}"
MSG_SAVED_HTML = "Saved as HTML: {}"
MSG_SAVED_HTML_PDF_READY = "Saved as HTML (PDF-ready): {}"
MSG_PDF_IMPORTED = "PDF imported successfully: {}"
MSG_LOADING_LARGE_FILE = "Loading large file ({:.1f} KB) - preview will be deferred"

# Error Messages
ERR_ASCIIDOC_NOT_INITIALIZED = "AsciiDoc API not initialized"
ERR_ATOMIC_SAVE_FAILED = "Atomic save failed for {}"
ERR_FAILED_SAVE_HTML = "Failed to save HTML file: {}"
ERR_FAILED_CREATE_TEMP = "Failed to create temporary file:\n{}"

# Dialog Titles
DIALOG_OPEN_FILE = "Open File"
DIALOG_SAVE_FILE = "Save File"
DIALOG_SAVE_ERROR = "Save Error"
DIALOG_CONVERSION_ERROR = "Conversion Error"

# Menu Labels
MENU_FILE = "&File"

# Status Tip Text
STATUS_TIP_EXPORT_OFFICE365 = "Export to Microsoft Office 365 Word format"

# Message Display Duration
STATUS_MESSAGE_DURATION_MS = 5000

# ============================================================================
# Module Availability Checks (v1.5.0-D)
# ============================================================================
# Check if optional modules are available.
# Note: These checks import the modules, so they should be deferred by importing
# constants.py only when needed, not at main.py startup.

try:
    import pypandoc  # noqa: F401

    PANDOC_AVAILABLE = True
except ImportError:
    PANDOC_AVAILABLE = False
