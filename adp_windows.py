"""
AsciiDoc Artisan - Windows-Optimized Version
============================================

Enhanced for Windows with proper window management, dynamic screen sizing,
and improved file navigation.
"""

import html
import io
import json
import logging
import os
import platform
import subprocess
import sys
import tempfile
import uuid
import warnings
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Union

try:
    from claude_client import ConversionFormat, ConversionResult, create_client

    CLAUDE_CLIENT_AVAILABLE = True
except ImportError:
    CLAUDE_CLIENT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.info("Claude client not available. AI-enhanced conversion disabled.")


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import from refactored core module
from asciidoc_artisan.core import (
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
    GitResult,
    Settings,
    atomic_save_json,
    atomic_save_text,
    sanitize_path,
)

# Import from refactored workers module
from asciidoc_artisan.workers import GitWorker, PandocWorker, PreviewWorker

# Import from refactored UI module
from asciidoc_artisan.ui import (
    AsciiDocEditor,
    ExportOptionsDialog,
    ImportOptionsDialog,
    PreferencesDialog,
)

from PySide6.QtCore import (
    QObject,
    QRect,
    QStandardPaths,
    Qt,
    QThread,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
    QGuiApplication,
    QKeySequence,
    QPalette,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

try:
    import pypandoc

    PANDOC_AVAILABLE = True
except ImportError:
    logger.warning("pypandoc not found. Document conversion limited.")
    pypandoc = None
    PANDOC_AVAILABLE = False


try:
    from pandoc_integration import ensure_pandoc_available, pandoc

    ENHANCED_PANDOC = True
except ImportError:
    logger.warning("Enhanced pandoc integration not available")
    pandoc = None  # type: ignore[assignment]
    ensure_pandoc_available = None  # type: ignore[assignment]
    ENHANCED_PANDOC = False

try:
    from asciidoc3 import asciidoc3
    from asciidoc3.asciidoc3api import AsciiDoc3API

    ASCIIDOC3_AVAILABLE = True
except ImportError:
    logger.warning("asciidoc3 not found. Live preview will use plain text.")
    asciidoc3 = None
    AsciiDoc3API = None
    ASCIIDOC3_AVAILABLE = False

# ============================================================================
# REFACTORING NOTE: Constants, Settings, GitResult, and file operations
# have been extracted to asciidoc_artisan.core module (Phase 1 of architectural
# refactoring to resolve technical debt per specification line 1197).
# These are now imported above from asciidoc_artisan.core.
# ============================================================================


# ============================================================================
# REFACTORING NOTE: Dialog classes (ImportOptionsDialog, ExportOptionsDialog,
# PreferencesDialog) have been extracted to asciidoc_artisan.ui.dialogs module
# (Phase 3 of architectural refactoring to resolve technical debt per
# specification line 1197). These are now imported above from asciidoc_artisan.ui.dialogs.
# ============================================================================

# ============================================================================
# REFACTORING NOTE: Worker classes (GitWorker, PandocWorker, PreviewWorker)
# have been extracted to asciidoc_artisan.workers module (Phase 2 of
# architectural refactoring to resolve technical debt per specification line 1197).
# These are now imported above from asciidoc_artisan.workers.
# ============================================================================

# ============================================================================
# REFACTORING NOTE: AsciiDocEditor class has been extracted to
# asciidoc_artisan.ui.main_window module (Phase 4 of architectural
# refactoring to resolve technical debt per specification line 1197).
# The class is now imported above from asciidoc_artisan.ui.
# ============================================================================


def main() -> None:

    warnings.filterwarnings("ignore", category=SyntaxWarning)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("AsciiDoc Artisan")

    if platform.system() == "Windows":
        app.setStyle("windowsvista")
    else:
        app.setStyle("Fusion")

    window = AsciiDocEditor()
    window.show()

    window.update_preview()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
