"""
Main Window - AsciiDocEditor application window.

This module contains the AsciiDocEditor class, the main application window
for AsciiDoc Artisan. This is the central UI controller that manages:
- Editor and preview panes
- File operations (open, save, import, export)
- Git integration
- Settings persistence
- Worker thread coordination

The AsciiDocEditor implements the complete application UI per specification
requirements FR-001 to FR-053.

Phase 2 Refactoring (v1.1.0-beta):
The class now delegates menu, theme, and status management to specialized
manager classes for improved modularity:
- MenuManager: Handles menu creation and actions
- ThemeManager: Manages dark/light mode and color palettes
- StatusManager: Coordinates window title, status bar, and message dialogs

This architectural improvement reduces complexity while maintaining full
backward compatibility.
"""

import html
import io
import logging
import os
import platform
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import (
    QRect,
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
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressDialog,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

# Import from refactored modules
from asciidoc_artisan.core import (
    ADOC_FILTER,
    APP_NAME,
    DEFAULT_FILENAME,
    DOCX_FILTER,
    EDITOR_FONT_FAMILY,
    EDITOR_FONT_SIZE,
    HTML_FILTER,
    MD_FILTER,
    MIN_FONT_SIZE,
    PDF_FILTER,
    PREVIEW_UPDATE_INTERVAL_MS,
    SUPPORTED_OPEN_FILTER,
    SUPPORTED_SAVE_FILTER,
    GitResult,
    ResourceMonitor,
    atomic_save_text,
)
from asciidoc_artisan.core.large_file_handler import LargeFileHandler
from asciidoc_artisan.ui.dialogs import (
    PreferencesDialog,
)
from asciidoc_artisan.ui.action_manager import ActionManager
from asciidoc_artisan.ui.editor_state import EditorState
from asciidoc_artisan.ui.export_manager import ExportManager
from asciidoc_artisan.ui.file_handler import FileHandler
from asciidoc_artisan.ui.git_handler import GitHandler
from asciidoc_artisan.ui.line_number_area import LineNumberPlainTextEdit
from asciidoc_artisan.ui.menu_manager import MenuManager
from asciidoc_artisan.ui.preview_handler import PreviewHandler
from asciidoc_artisan.ui.settings_manager import SettingsManager
from asciidoc_artisan.ui.status_manager import StatusManager
from asciidoc_artisan.ui.theme_manager import ThemeManager
from asciidoc_artisan.workers import GitWorker, PandocWorker, PreviewWorker

# Check for AI client availability
try:
    import ai_client  # noqa: F401

    AI_CLIENT_AVAILABLE = True
except ImportError:
    AI_CLIENT_AVAILABLE = False

# Check for AsciiDoc3 availability
try:
    from asciidoc3 import asciidoc3
    from asciidoc3.asciidoc3api import AsciiDoc3API

    ASCIIDOC3_AVAILABLE = True
except ImportError:
    asciidoc3 = None
    AsciiDoc3API = None
    ASCIIDOC3_AVAILABLE = False

# Check for Pandoc availability
try:
    import pypandoc

    PANDOC_AVAILABLE = True
except ImportError:
    pypandoc = None
    PANDOC_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS
# ============================================================================

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

# Color Values
SEPARATOR_BACKGROUND_COLOR = "rgba(128, 128, 128, 0.1)"
SEPARATOR_BORDER_COLOR = "#888"
EDITOR_HIGHLIGHT_COLOR_ADD = "rgba(74, 222, 128, 0.2)"
EDITOR_HIGHLIGHT_HOVER_ADD = "rgba(74, 222, 128, 0.3)"
PREVIEW_HIGHLIGHT_COLOR_ADD = "rgba(74, 158, 255, 0.2)"
PREVIEW_HIGHLIGHT_HOVER_ADD = "rgba(74, 158, 255, 0.3)"
DARK_THEME_LINK_COLOR = QColor(42, 130, 218)
DARK_THEME_HIGHLIGHT_COLOR = QColor(42, 130, 218)

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


class AsciiDocEditor(QMainWindow):
    request_git_command = Signal(list, str)
    request_pandoc_conversion = Signal(object, str, str, str, object, bool)
    request_preview_render = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        # Initialize settings manager
        self._settings_manager = SettingsManager()
        self._settings_path = self._settings_manager.get_settings_path()

        # Load settings
        self._settings = self._settings_manager.load_settings()

        # Initialize Phase 2 managers
        self.menu_manager = MenuManager(self)
        self.theme_manager = ThemeManager(self)
        self.status_manager = StatusManager(self)

        # Initialize Phase 4 resource monitor
        self.resource_monitor = ResourceMonitor()
        logger.info(
            f"ResourceMonitor initialized (psutil available: {self.resource_monitor.is_available()})"
        )

        # Initialize large file handler
        self.large_file_handler = LargeFileHandler()
        self.large_file_handler.progress_update.connect(self._on_file_load_progress)

        # Initialize progress dialog for large file loading
        self._progress_dialog: Optional[QProgressDialog] = None

        # Initialize temporary directory for file conversions
        self._temp_dir = tempfile.TemporaryDirectory()

        # Initialize state variables
        self._current_file_path: Optional[Path] = None
        self._initial_geometry: Optional[QRect] = None
        self._start_maximized = self._settings.maximized
        self._is_opening_file = False
        self._is_processing_git = False
        self._is_processing_pandoc = False
        self._last_git_operation = ""
        self._pending_file_path: Optional[Path] = None
        self._pending_commit_message: Optional[str] = None
        self._unsaved_changes = False
        self._sync_scrolling = True
        self._is_syncing_scroll = False

        # Parse window geometry from settings
        if not self._start_maximized:
            self._initial_geometry = self._settings_manager.parse_window_geometry(
                self._settings
            )

        # Restore last file if exists
        if self._settings.last_file and Path(self._settings.last_file).is_file():
            self._current_file_path = Path(self._settings.last_file)

        # Initialize AsciiDoc API
        self._asciidoc_api = self._initialize_asciidoc()

        # Setup preview timer
        self._preview_timer = self._setup_preview_timer()

        self.setWindowTitle(f"{APP_NAME} · Basic Preview")

        if platform.system() == "Windows":
            self.setWindowFlags(
                Qt.WindowType.Window
                | Qt.WindowType.WindowTitleHint
                | Qt.WindowType.WindowSystemMenuHint
                | Qt.WindowType.WindowMinimizeButtonHint
                | Qt.WindowType.WindowMaximizeButtonHint
                | Qt.WindowType.WindowCloseButtonHint
            )

        self._setup_ui()

        # Initialize FileHandler (Phase 5: Refactoring)
        self.file_handler = FileHandler(
            self.editor,
            self,
            self._settings_manager,
            self.status_manager
        )
        # Start auto-save
        self.file_handler.start_auto_save(AUTO_SAVE_INTERVAL_MS)

        # Initialize PreviewHandler (Phase 5: Refactoring)
        self.preview_handler = PreviewHandler(
            self.editor,
            self.preview,
            self
        )
        self.preview_handler.start_preview_updates()

        # Initialize GitHandler (Phase 5: Refactoring)
        self.git_handler = GitHandler(
            self,
            self._settings_manager,
            self.status_manager
        )

        # Initialize ActionManager (Phase 5: Refactoring)
        self.action_manager = ActionManager(self)
        self.action_manager.create_actions()
        self.action_manager.create_menus()

        # Initialize ExportManager (Phase 5: Refactoring)
        self.export_manager = ExportManager(self)

        # Initialize EditorState (Phase 5: Refactoring)
        self.editor_state = EditorState(self)

        # Restore UI settings using manager
        self._settings_manager.restore_ui_settings(self, self.splitter, self._settings)
        # Phase 2: Use manager classes for theme setup
        self.theme_manager.apply_theme()
        self._setup_workers_and_threads()
        self._update_ui_state()

    def _initialize_asciidoc(self) -> Optional[AsciiDoc3API]:
        if ASCIIDOC3_AVAILABLE and AsciiDoc3API and asciidoc3:
            try:
                instance = AsciiDoc3API(asciidoc3.__file__)

                instance.options("--no-header-footer")

                instance.attributes["icons"] = "font"
                instance.attributes["source-highlighter"] = "highlight.js"
                instance.attributes["toc"] = "left"
                instance.attributes["sectanchors"] = ""
                instance.attributes["sectnums"] = ""
                instance.attributes["imagesdir"] = "."

                logger.info("AsciiDoc3API initialized with enhanced attributes")
                return instance
            except Exception as exc:
                logger.error(f"AsciiDoc3API initialization failed: {exc}")
        return None

    def _setup_preview_timer(self) -> QTimer:
        timer = QTimer(self)
        timer.setInterval(PREVIEW_UPDATE_INTERVAL_MS)
        timer.setSingleShot(True)
        timer.timeout.connect(self.update_preview)
        return timer

    def _setup_ui(self) -> None:

        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.setCentralWidget(self.splitter)

        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        editor_toolbar = QWidget()
        editor_toolbar.setFixedHeight(30)
        editor_toolbar.setStyleSheet(
            f"background-color: {SEPARATOR_BACKGROUND_COLOR}; border-bottom: 1px solid {SEPARATOR_BORDER_COLOR};"
        )
        editor_toolbar_layout = QHBoxLayout(editor_toolbar)
        editor_toolbar_layout.setContentsMargins(5, 2, 5, 2)

        self.editor_label = QLabel("Editor")

        self.editor_label.setStyleSheet("color: #4ade80; font-weight: bold;")
        editor_toolbar_layout.addWidget(self.editor_label)
        editor_toolbar_layout.addStretch()

        self.editor_max_btn = QPushButton("⬜")
        self.editor_max_btn.setFixedSize(24, 24)
        self.editor_max_btn.setToolTip("Maximize editor")
        self.editor_max_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: 1px solid #4ade80;
                border-radius: 3px;
                padding: 2px;
                color: #4ade80;
            }
            QPushButton:hover {
                background-color: {EDITOR_HIGHLIGHT_COLOR_ADD};
                border-color: #4ade80;
            }
            QPushButton:pressed {
                background-color: {EDITOR_HIGHLIGHT_HOVER_ADD};
            }
        """
        )
        self.editor_max_btn.clicked.connect(
            lambda: self._toggle_pane_maximize("editor")
        )
        editor_toolbar_layout.addWidget(self.editor_max_btn)

        editor_layout.addWidget(editor_toolbar)

        self.editor = LineNumberPlainTextEdit(self)
        font = QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE)
        self.editor.setFont(font)
        self.editor.textChanged.connect(self._start_preview_timer)
        editor_layout.addWidget(self.editor)

        self.splitter.addWidget(editor_container)

        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)

        preview_toolbar = QWidget()
        preview_toolbar.setFixedHeight(30)
        preview_toolbar.setStyleSheet(
            f"background-color: {SEPARATOR_BACKGROUND_COLOR}; border-bottom: 1px solid {SEPARATOR_BORDER_COLOR};"
        )
        preview_toolbar_layout = QHBoxLayout(preview_toolbar)
        preview_toolbar_layout.setContentsMargins(5, 2, 5, 2)

        self.preview_label = QLabel("Preview")

        self.preview_label.setStyleSheet("color: #4a9eff; font-weight: bold;")
        preview_toolbar_layout.addWidget(self.preview_label)
        preview_toolbar_layout.addStretch()

        self.preview_max_btn = QPushButton("⬜")
        self.preview_max_btn.setFixedSize(24, 24)
        self.preview_max_btn.setToolTip("Maximize preview")
        self.preview_max_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: 1px solid #4a9eff;
                border-radius: 3px;
                padding: 2px;
                color: #4a9eff;
            }
            QPushButton:hover {
                background-color: {PREVIEW_HIGHLIGHT_COLOR_ADD};
                border-color: #4a9eff;
            }
            QPushButton:pressed {
                background-color: {PREVIEW_HIGHLIGHT_HOVER_ADD};
            }
        """
        )
        self.preview_max_btn.clicked.connect(
            lambda: self._toggle_pane_maximize("preview")
        )
        preview_toolbar_layout.addWidget(self.preview_max_btn)

        preview_layout.addWidget(preview_toolbar)

        self.preview = QTextBrowser(self)
        self.preview.setReadOnly(True)
        self.preview.setOpenExternalLinks(True)
        preview_layout.addWidget(self.preview)

        self.splitter.addWidget(preview_container)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        # Set default 50/50 split - ensure both panes visible
        # This will be overridden by saved settings if they exist
        QTimer.singleShot(0, lambda: self.splitter.setSizes([400, 400]))

        self._setup_synchronized_scrolling()

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self._setup_dynamic_sizing()

    def _setup_dynamic_sizing(self) -> None:
        """Set up window to dynamically resize based on screen size."""
        screen = QGuiApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()

            default_width = int(available.width() * 0.8)
            default_height = int(available.height() * 0.8)

            if self._initial_geometry and available.intersects(self._initial_geometry):
                self.setGeometry(self._initial_geometry)
            else:

                self.resize(default_width, default_height)
                self.move(
                    (available.width() - default_width) // 2 + available.x(),
                    (available.height() - default_height) // 2 + available.y(),
                )

            if self._start_maximized:
                self.showMaximized()

    def _setup_synchronized_scrolling(self) -> None:
        """
        Set up synchronized scrolling between editor and preview.

        Implements FR-043 with scroll loop protection and event coalescing.
        """
        editor_scrollbar = self.editor.verticalScrollBar()
        preview_scrollbar = self.preview.verticalScrollBar()

        editor_scrollbar.valueChanged.connect(self._sync_editor_to_preview)
        preview_scrollbar.valueChanged.connect(self._sync_preview_to_editor)

        # Initialize scroll sync tracking
        self._last_editor_scroll = 0
        self._last_preview_scroll = 0
        self._scroll_sync_count = 0

    def _sync_editor_to_preview(self, value: int) -> None:
        """
        Synchronize preview scroll position with editor.

        Implements FR-043 with loop detection and coalescing.
        """
        if not self._sync_scrolling or self._is_syncing_scroll:
            return

        # Skip if value hasn't changed significantly (coalesce events)
        if abs(value - self._last_editor_scroll) < 2:
            return

        self._last_editor_scroll = value

        # Detect potential scroll loops
        self._scroll_sync_count += 1
        if self._scroll_sync_count > 100:
            logger.warning("Scroll loop detected, resetting")
            self._scroll_sync_count = 0
            return

        self._is_syncing_scroll = True
        try:
            editor_scrollbar = self.editor.verticalScrollBar()
            preview_scrollbar = self.preview.verticalScrollBar()

            editor_max = editor_scrollbar.maximum()
            if editor_max > 0:
                scroll_percentage = value / editor_max
                preview_value = int(preview_scrollbar.maximum() * scroll_percentage)

                # Only update if value actually changed
                if preview_scrollbar.value() != preview_value:
                    preview_scrollbar.setValue(preview_value)

            # Reset counter on successful sync
            self._scroll_sync_count = max(0, self._scroll_sync_count - 1)
        finally:
            self._is_syncing_scroll = False

    def _sync_preview_to_editor(self, value: int) -> None:
        """
        Synchronize editor scroll position with preview.

        Implements FR-043 with loop detection and coalescing.
        """
        if not self._sync_scrolling or self._is_syncing_scroll:
            return

        # Skip if value hasn't changed significantly (coalesce events)
        if abs(value - self._last_preview_scroll) < 2:
            return

        self._last_preview_scroll = value

        # Detect potential scroll loops
        self._scroll_sync_count += 1
        if self._scroll_sync_count > 100:
            logger.warning("Scroll loop detected, resetting")
            self._scroll_sync_count = 0
            return

        self._is_syncing_scroll = True
        try:
            editor_scrollbar = self.editor.verticalScrollBar()
            preview_scrollbar = self.preview.verticalScrollBar()

            preview_max = preview_scrollbar.maximum()
            if preview_max > 0:
                scroll_percentage = value / preview_max
                editor_value = int(editor_scrollbar.maximum() * scroll_percentage)

                # Only update if value actually changed
                if editor_scrollbar.value() != editor_value:
                    editor_scrollbar.setValue(editor_value)

            # Reset counter on successful sync
            self._scroll_sync_count = max(0, self._scroll_sync_count - 1)
        finally:
            self._is_syncing_scroll = False

    def _setup_workers_and_threads(self) -> None:
        logger.info("Setting up worker threads...")

        self.git_thread = QThread(self)
        self.git_worker = GitWorker()
        self.git_worker.moveToThread(self.git_thread)
        self.request_git_command.connect(self.git_worker.run_git_command)
        self.git_worker.command_complete.connect(self._handle_git_result)
        self.git_thread.finished.connect(self.git_worker.deleteLater)
        self.git_thread.start()

        self.pandoc_thread = QThread(self)
        self.pandoc_worker = PandocWorker()
        self.pandoc_worker.moveToThread(self.pandoc_thread)
        self.request_pandoc_conversion.connect(self.pandoc_worker.run_pandoc_conversion)
        self.pandoc_worker.conversion_complete.connect(self._handle_pandoc_result)
        self.pandoc_worker.conversion_error.connect(self._handle_pandoc_error_result)
        self.pandoc_thread.finished.connect(self.pandoc_worker.deleteLater)
        self.pandoc_thread.start()

        self.preview_thread = QThread(self)
        self.preview_worker = PreviewWorker()
        self.preview_worker.moveToThread(self.preview_thread)

        if ASCIIDOC3_AVAILABLE and asciidoc3:
            self.preview_worker.initialize_asciidoc(asciidoc3.__file__)

        self.request_preview_render.connect(self.preview_worker.render_preview)
        self.preview_worker.render_complete.connect(self._handle_preview_complete)
        self.preview_worker.render_error.connect(self._handle_preview_error)
        self.preview_thread.finished.connect(self.preview_worker.deleteLater)
        self.preview_thread.start()

        logger.info("All worker threads started (Git, Pandoc, Preview)")

    def _start_preview_timer(self) -> None:
        """
        Start preview update timer with adaptive debouncing.

        Phase 4 Enhancement: Dynamically adjusts debounce interval based on
        document size. Small documents get fast updates (200ms), while large
        documents use longer intervals (500-1000ms) to maintain responsiveness.
        """
        if self._is_opening_file:
            return
        self._unsaved_changes = True
        self.status_manager.update_window_title()

        # Calculate adaptive debounce interval based on document size
        text = self.editor.toPlainText()
        debounce_ms = self.resource_monitor.calculate_debounce_interval(text)

        # Update timer interval if it has changed
        if self._preview_timer.interval() != debounce_ms:
            self._preview_timer.setInterval(debounce_ms)
            logger.debug(
                f"Adaptive debounce: {debounce_ms}ms for {len(text)} chars, "
                f"{text.count(chr(10)) + 1} lines"
            )

        self._preview_timer.start()

    def _update_window_title(self) -> None:
        title = APP_NAME
        if self._current_file_path:
            title = f"{APP_NAME} - {self._current_file_path.name}"
        else:
            title = f"{APP_NAME} - {DEFAULT_FILENAME}"

        if self._unsaved_changes:
            title += "*"

        self.setWindowTitle(title)

    def _apply_theme(self) -> None:
        if self._settings.dark_mode:
            self._apply_dark_theme()

            if hasattr(self, "editor_label"):
                self.editor_label.setStyleSheet("color: white;")
            if hasattr(self, "preview_label"):
                self.preview_label.setStyleSheet("color: white;")
        else:

            QApplication.setPalette(QApplication.style().standardPalette())

            if hasattr(self, "editor_label"):
                self.editor_label.setStyleSheet("color: black;")
            if hasattr(self, "preview_label"):
                self.preview_label.setStyleSheet("color: black;")

    def _apply_dark_theme(self) -> None:
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, DARK_THEME_LINK_COLOR)
        palette.setColor(QPalette.ColorRole.Highlight, DARK_THEME_HIGHLIGHT_COLOR)
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        QApplication.setPalette(palette)

    def new_file(self) -> None:
        """Create a new file (delegates to FileHandler)."""
        self.file_handler.new_file()

    @Slot()
    def open_file(self) -> None:
        """Open a file with proper Windows dialog."""
        if self._is_processing_pandoc:
            self.status_manager.show_message(
                "warning", "Busy", "Already processing a file conversion."
            )
            return

        if self._unsaved_changes:
            if not self.status_manager.prompt_save_before_action("opening a new file"):
                return

        file_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            self._settings.last_directory,
            SUPPORTED_OPEN_FILTER,
            options=(
                QFileDialog.Option.DontUseNativeDialog
                if platform.system() != "Windows"
                else QFileDialog.Option(0)
            ),
        )

        if not file_path_str:
            return

        file_path = Path(file_path_str)
        self._settings.last_directory = str(file_path.parent)

        try:
            suffix = file_path.suffix.lower()
            if suffix == ".pdf":
                # PDF import via text extraction
                from document_converter import pdf_extractor

                if not pdf_extractor.is_available():
                    self.status_manager.show_message(
                        "warning",
                        "PDF Support Unavailable",
                        "PDF text extraction requires pdfplumber.\n\n"
                        "To install:\n"
                        "  pip install pdfplumber\n\n"
                        "After installation, restart the application.",
                    )
                    return

                self.status_bar.showMessage(
                    f"Extracting text from PDF: {file_path.name}..."
                )

                success, asciidoc_text, error_msg = pdf_extractor.convert_to_asciidoc(
                    file_path
                )

                if not success:
                    self.status_manager.show_message(
                        "critical",
                        "PDF Extraction Failed",
                        f"Failed to extract text from PDF:\n\n{error_msg}\n\n"
                        "The PDF may be encrypted, image-based, or corrupted.",
                    )
                    return

                # Load extracted content into editor
                self._load_content_into_editor(asciidoc_text, file_path)
                self.status_bar.showMessage(
                    f"PDF imported successfully: {file_path.name}", 5000
                )
                return
            elif suffix in [
                ".docx",
                ".md",
                ".markdown",
                ".html",
                ".htm",
                ".tex",
                ".rst",
                ".org",
                ".textile",
            ]:

                if not self._check_pandoc_availability(f"Opening {suffix.upper()[1:]}"):
                    return

                format_map = {
                    ".docx": ("docx", "binary"),
                    ".md": ("markdown", "text"),
                    ".markdown": ("markdown", "text"),
                    ".html": ("html", "text"),
                    ".htm": ("html", "text"),
                    ".tex": ("latex", "text"),
                    ".rst": ("rst", "text"),
                    ".org": ("org", "text"),
                    ".textile": ("textile", "text"),
                }

                input_format, file_type = format_map.get(suffix, ("markdown", "text"))

                # Use settings preference for AI conversion (defaults to Pandoc)
                use_ai_for_import = self._settings_manager.get_ai_conversion_preference(
                    self._settings
                )

                self._is_processing_pandoc = True
                self._pending_file_path = file_path
                self._update_ui_state()

                self.editor.setPlainText(
                    f"// Converting {file_path.name} to AsciiDoc...\n// Please wait..."
                )
                self.preview.setHtml(
                    "<h3>Converting document...</h3><p>The preview will update when conversion is complete.</p>"
                )
                self.status_bar.showMessage(
                    f"Converting '{file_path.name}' from {suffix.upper()[1:]} to AsciiDoc..."
                )

                file_content: str | bytes
                if file_type == "binary":
                    file_content = file_path.read_bytes()
                else:
                    file_content = file_path.read_text(encoding="utf-8")

                logger.info(
                    f"Starting conversion of {file_path.name} from {input_format} to asciidoc (AI: {use_ai_for_import})"
                )

                self.request_pandoc_conversion.emit(
                    file_content,
                    "asciidoc",
                    input_format,
                    f"converting '{file_path.name}'",
                    None,
                    use_ai_for_import,
                )
            else:
                # Use optimized loading for large files
                file_size = file_path.stat().st_size
                category = LargeFileHandler.get_file_size_category(file_path)

                if category in ["medium", "large"]:
                    logger.info(f"Loading {category} file with optimizations")
                    success, content, error = self.large_file_handler.load_file_optimized(
                        file_path
                    )
                    if not success:
                        raise Exception(error)
                else:
                    content = file_path.read_text(encoding="utf-8")

                self._load_content_into_editor(content, file_path)

        except Exception as e:
            logger.exception(f"Failed to open file: {file_path}")
            self.status_manager.show_message(
                "critical", "Error", f"Failed to open file:\n{e}"
            )

    def _load_content_into_editor(self, content: str, file_path: Path) -> None:
        """Load content into editor with lazy loading for large files."""
        self._is_opening_file = True
        try:
            # Disable preview updates temporarily for large files
            content_size = len(content)
            is_large_file = content_size > LARGE_FILE_THRESHOLD_BYTES

            if is_large_file:
                logger.info(
                    MSG_LOADING_LARGE_FILE.format(content_size / 1024)
                )

            # QPlainTextEdit handles large documents efficiently with internal lazy loading
            # It only renders visible blocks, so setPlainText is still fast
            self.editor.setPlainText(content)
            self._current_file_path = file_path
            self._unsaved_changes = False
            self.status_manager.update_window_title()

            if file_path.suffix.lower() in [
                ".md",
                ".markdown",
                ".docx",
                ".html",
                ".htm",
                ".tex",
                ".rst",
                ".org",
                ".textile",
            ]:
                self.status_bar.showMessage(
                    f"Converted and opened: {file_path} → AsciiDoc"
                )
            else:
                self.status_bar.showMessage(f"Opened: {file_path}")

            # Trigger preview update (will be optimized based on file size)
            self.update_preview()

            logger.info(f"Loaded content into editor: {file_path}")
        finally:
            self._is_opening_file = False

    @Slot()
    def save_file(self, save_as: bool = False) -> bool:
        """
        Save file with Windows-friendly dialog.

        Handles both simple AsciiDoc saves and export to other formats.
        Simple .adoc saves delegate to FileHandler.
        """
        if save_as or not self._current_file_path:

            suggested_name = (
                self._current_file_path.name
                if self._current_file_path
                else DEFAULT_FILENAME
            )
            suggested_path = Path(self._settings.last_directory) / suggested_name

            file_path_str, selected_filter = QFileDialog.getSaveFileName(
                self,
                "Save File",
                str(suggested_path),
                SUPPORTED_SAVE_FILTER,
                options=(
                    QFileDialog.Option.DontUseNativeDialog
                    if platform.system() != "Windows"
                    else QFileDialog.Option(0)
                ),
            )

            if not file_path_str:
                return False

            file_path = Path(file_path_str)
            logger.info(
                f"Save As dialog - file_path: {file_path}, selected_filter: {selected_filter}"
            )

            format_type = "adoc"

            if MD_FILTER in selected_filter:
                format_type = "md"
            elif DOCX_FILTER in selected_filter:
                format_type = "docx"
            elif HTML_FILTER in selected_filter:
                format_type = "html"
            elif PDF_FILTER in selected_filter:
                format_type = "pdf"
            elif file_path.suffix:

                ext = file_path.suffix.lower()
                if ext in [".md", ".markdown"]:
                    format_type = "md"
                elif ext == ".docx":
                    format_type = "docx"
                elif ext in [".html", ".htm"]:
                    format_type = "html"
                elif ext == ".pdf":
                    format_type = "pdf"

            if format_type == "md" and not file_path.suffix:
                file_path = file_path.with_suffix(".md")
            elif format_type == "docx" and not file_path.suffix:
                file_path = file_path.with_suffix(".docx")
            elif format_type == "html" and not file_path.suffix:
                file_path = file_path.with_suffix(".html")
            elif format_type == "pdf" and not file_path.suffix:
                file_path = file_path.with_suffix(".pdf")
            elif format_type == "adoc" and not file_path.suffix:
                file_path = file_path.with_suffix(".adoc")

            if format_type != "adoc":

                # Use settings preference for AI conversion (defaults to Pandoc)
                use_ai_for_export = self._settings_manager.get_ai_conversion_preference(
                    self._settings
                )

                logger.info(
                    f"Calling _save_as_format_internal with file_path={file_path}, format_type={format_type}, use_ai={use_ai_for_export}"
                )
                return self._save_as_format_internal(
                    file_path, format_type, use_ai_for_export
                )

        else:
            # We only reach here if _current_file_path is not None (checked at line 1909)
            file_path = self._current_file_path
            assert file_path is not None, "file_path should not be None in save mode"

            if file_path.suffix.lower() not in [".adoc", ".asciidoc"]:

                file_path = file_path.with_suffix(".adoc")
                logger.info(
                    f"Converting save format from {self._current_file_path.suffix} to .adoc"
                )

        content = self.editor.toPlainText()

        if atomic_save_text(file_path, content, encoding="utf-8"):
            self._current_file_path = file_path
            self._settings.last_directory = str(file_path.parent)
            self._unsaved_changes = False
            self.status_manager.update_window_title()
            self.status_bar.showMessage(MSG_SAVED_ASCIIDOC.format(file_path))
            logger.info(f"Saved file: {file_path}")
            return True
        else:
            self.status_manager.show_message(
                "critical",
                "Save Error",
                f"Failed to save file: {file_path}\nThe file may be in use or the directory may be read-only.",
            )
            return False

    def _save_as_format_internal(
        self, file_path: Path, format_type: str, use_ai: Optional[bool] = None
    ) -> bool:
        """Internal method to save file in specified format without showing dialog.

        Args:
            file_path: Target file path
            format_type: Target format (adoc, md, docx, pdf, html)
            use_ai: Whether to use AI conversion (None = use settings default)
        """
        logger.info(
            f"_save_as_format_internal called - file_path: {file_path}, format_type: {format_type}, use_ai: {use_ai}"
        )

        if use_ai is None:
            use_ai = self._settings_manager.get_ai_conversion_preference(self._settings)

        content = self.editor.toPlainText()

        if format_type == "adoc":
            if atomic_save_text(file_path, content, encoding="utf-8"):
                self._current_file_path = file_path
                self._settings.last_directory = str(file_path.parent)
                self._unsaved_changes = False
                self.status_manager.update_window_title()
                self.status_bar.showMessage(MSG_SAVED_ASCIIDOC.format(file_path))
                return True
            else:
                self.status_manager.show_message(
                    "critical",
                    "Save Error",
                    f"Failed to save AsciiDoc file: {file_path}",
                )
                return False

        if format_type == "html":
            self.status_bar.showMessage("Saving as HTML...")
            try:
                if self._asciidoc_api is None:
                    raise RuntimeError(ERR_ASCIIDOC_NOT_INITIALIZED)

                infile = io.StringIO(content)
                outfile = io.StringIO()
                self._asciidoc_api.execute(infile, outfile, backend="html5")
                html_content = outfile.getvalue()

                if atomic_save_text(file_path, html_content, encoding="utf-8"):
                    self.status_bar.showMessage(MSG_SAVED_HTML.format(file_path))
                    logger.info(f"Successfully saved as HTML: {file_path}")
                    return True
                else:
                    raise IOError(f"Atomic save failed for {file_path}")
            except Exception as e:
                logger.exception(f"Failed to save HTML file: {e}")
                self.status_manager.show_message(
                    "critical", "Save Error", f"Failed to save HTML file:\n{e}"
                )
                return False

        if not self._check_pandoc_availability(f"Save as {format_type.upper()}"):
            return False

        self.status_bar.showMessage(f"Saving as {format_type.upper()}...")

        # Determine source format from current file
        source_format = "asciidoc"  # default
        temp_source_file = None

        if self._current_file_path:
            suffix = self._current_file_path.suffix.lower()
            format_map = {
                ".md": "markdown",
                ".markdown": "markdown",
                ".docx": "docx",
                ".pdf": "markdown",  # PDF was converted to text, treat as markdown
                ".html": "html",
                ".htm": "html",
            }
            source_format = format_map.get(suffix, "asciidoc")

        # If source is AsciiDoc, convert to HTML first (legacy path)
        if source_format == "asciidoc":
            try:
                if self._asciidoc_api is None:
                    raise RuntimeError(ERR_ASCIIDOC_NOT_INITIALIZED)

                infile = io.StringIO(content)
                outfile = io.StringIO()
                self._asciidoc_api.execute(infile, outfile, backend="html5")
                html_content = outfile.getvalue()

                temp_source_file = Path(self._temp_dir.name) / f"temp_{uuid.uuid4().hex}.html"
                temp_source_file.write_text(html_content, encoding="utf-8")
                source_format = "html"
            except Exception as e:
                logger.exception(f"Failed to convert AsciiDoc to HTML: {e}")
                self.status_manager.show_message(
                    "critical",
                    "Conversion Error",
                    f"Failed to convert AsciiDoc to HTML:\n{e}",
                )
                return False
        else:
            # For non-AsciiDoc sources, save content to temp file for Pandoc
            ext_map = {"markdown": ".md", "docx": ".docx", "html": ".html"}
            temp_ext = ext_map.get(source_format, ".txt")
            temp_source_file = Path(self._temp_dir.name) / f"temp_{uuid.uuid4().hex}{temp_ext}"
            try:
                temp_source_file.write_text(content, encoding="utf-8")
            except Exception as e:
                self.status_manager.show_message(
                    "critical", "Save Error", f"Failed to create temporary file:\n{e}"
                )
                return False

        self.status_bar.showMessage(f"Saving as {format_type.upper()}...")

        # Set export manager pending paths for result handling
        self.export_manager.pending_export_path = file_path
        self.export_manager.pending_export_format = format_type

        if format_type in ["pdf", "docx"]:
            # Use Pandoc for PDF and DOCX conversion - pass output file directly
            logger.info(
                f"Emitting pandoc conversion request for {format_type} - source: {temp_source_file} ({source_format}), output: {file_path}"
            )
            self.request_pandoc_conversion.emit(
                temp_source_file,
                format_type,
                source_format,
                f"Exporting to {format_type.upper()}",
                file_path,
                use_ai,
            )
        else:
            # For other formats, let worker return the content
            logger.info(
                f"Emitting pandoc conversion request for {format_type} - source: {temp_source_file} ({source_format})"
            )
            self.request_pandoc_conversion.emit(
                temp_source_file,
                format_type,
                source_format,
                f"Exporting to {format_type.upper()}",
                None,
                use_ai,
            )

            self._pending_export_path = file_path
            self._pending_export_format = format_type

        if format_type == "adoc":
            self._current_file_path = file_path
            self._settings.last_directory = str(file_path.parent)
            self._unsaved_changes = False
            self.status_manager.update_window_title()

        return True

    def save_file_as_format(self, format_type: str) -> bool:
        """Save/export file in specified format (delegates to ExportManager)."""
        return self.export_manager.save_file_as_format(format_type)


    def _auto_save(self) -> None:
        """Auto-save current file if there are unsaved changes using atomic write."""
        if self._current_file_path and self._unsaved_changes:
            content = self.editor.toPlainText()
            if atomic_save_text(self._current_file_path, content, encoding="utf-8"):
                self.status_bar.showMessage("Auto-saved", 2000)
                logger.info(f"Auto-saved: {self._current_file_path}")
            else:
                logger.error(f"Auto-save failed: {self._current_file_path}")

    @Slot(int, str)
    def _on_file_load_progress(self, percentage: int, message: str) -> None:
        """Handle file loading progress updates with visual progress dialog."""
        # Create progress dialog on first progress update
        if percentage > 0 and percentage < 100:
            if self._progress_dialog is None:
                self._progress_dialog = QProgressDialog(
                    "Loading file...", "Cancel", 0, 100, self
                )
                self._progress_dialog.setWindowTitle("Loading")
                self._progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
                self._progress_dialog.setMinimumDuration(500)  # Show after 500ms
                self._progress_dialog.setCancelButton(None)  # No cancel button
                self._progress_dialog.setAutoClose(True)
                self._progress_dialog.setAutoReset(True)

            self._progress_dialog.setValue(percentage)
            self._progress_dialog.setLabelText(message)
            logger.debug(f"File load progress: {percentage}% - {message}")

        # Close and cleanup on completion
        elif percentage >= 100:
            if self._progress_dialog is not None:
                self._progress_dialog.setValue(100)
                self._progress_dialog.close()
                self._progress_dialog = None
            self.status_bar.showMessage(message, 3000)
            logger.debug(f"File load complete: {message}")

        # Show in status bar for initial progress
        else:
            self.status_bar.showMessage(message, 2000)

    @Slot()
    def update_preview(self) -> None:
        """Request preview rendering (delegates to PreviewHandler)."""
        self.preview_handler.update_preview()

    @Slot(str)
    def _handle_preview_complete(self, html_body: str) -> None:
        """Handle successful preview rendering (delegates to PreviewHandler)."""
        self.preview_handler.handle_preview_complete(html_body)

    @Slot(str)
    def _handle_preview_error(self, error_html: str) -> None:
        """Handle preview rendering error (delegates to PreviewHandler)."""
        self.preview_handler.handle_preview_error(error_html)

    def _convert_asciidoc_to_html_body(self, source_text: str) -> str:
        """
        DEPRECATED: Rendering now handled by PreviewWorker thread.
        Kept for compatibility with export operations that need synchronous rendering.
        """
        if self._asciidoc_api is None:
            return f"<pre>{html.escape(source_text)}</pre>"

        try:
            infile = io.StringIO(source_text)
            outfile = io.StringIO()
            self._asciidoc_api.execute(infile, outfile, backend="html5")
            return outfile.getvalue()
        except Exception as exc:
            logger.error(f"AsciiDoc rendering failed: {exc}")
            return f"<div style='color:red'>Render Error: {html.escape(str(exc))}</div>"

    def _get_preview_css(self) -> str:

        if self._settings.dark_mode:
            return """
                body {
                    background:#1e1e1e; color:#dcdcdc;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    padding: 20px; line-height: 1.6; max-width: 900px; margin: 0 auto;
                }
                h1,h2,h3,h4,h5,h6 { color:#ececec; margin-top: 1.5em; margin-bottom: 0.5em; }
                h1 { font-size: 2.2em; border-bottom: 2px solid #444; padding-bottom: 0.3em; }
                h2 { font-size: 1.8em; border-bottom: 1px solid #333; padding-bottom: 0.2em; }
                h3 { font-size: 1.4em; }
                a { color:#80d0ff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                code { background:#2a2a2a; color:#f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
                pre { background:#2a2a2a; color:#f0f0f0; padding: 15px; overflow-x: auto; border-radius: 5px; }
                pre code { background: none; padding: 0; }
                blockquote { border-left: 4px solid #666; margin: 1em 0; padding-left: 1em; color: #aaa; }
                table { border-collapse: collapse; width: 100%; margin: 1em 0; }
                th, td { border: 1px solid #444; padding: 8px; text-align: left; }
                th { background: #2a2a2a; font-weight: bold; }
                ul, ol { padding-left: 2em; margin: 1em 0; }
                .admonitionblock { margin: 1em 0; padding: 1em; border-radius: 5px; }
                .admonitionblock.note { background: #1e3a5f; border-left: 4px solid #4a90e2; }
                .admonitionblock.tip { background: #1e4d2b; border-left: 4px solid #5cb85c; }
                .admonitionblock.warning { background: #5d4037; border-left: 4px solid #ff9800; }
                .admonitionblock.caution { background: #5d4037; border-left: 4px solid #f44336; }
                .admonitionblock.important { background: #4a148c; border-left: 4px solid #9c27b0; }
                .imageblock { text-align: center; margin: 1em 0; }
                .imageblock img { max-width: 100%; height: auto; }
            """
        else:
            return """
                body {
                    background:#ffffff; color:#333333;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    padding: 20px; line-height: 1.6; max-width: 900px; margin: 0 auto;
                }
                h1,h2,h3,h4,h5,h6 { color:#111111; margin-top: 1.5em; margin-bottom: 0.5em; }
                h1 { font-size: 2.2em; border-bottom: 2px solid #ddd; padding-bottom: 0.3em; }
                h2 { font-size: 1.8em; border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
                h3 { font-size: 1.4em; }
                a { color:#007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                code { background:#f8f8f8; color:#333; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; border: 1px solid #e1e4e8; }
                pre { background:#f8f8f8; color:#333; padding: 15px; overflow-x: auto; border-radius: 5px; border: 1px solid #e1e4e8; }
                pre code { background: none; padding: 0; border: none; }
                blockquote { border-left: 4px solid #ddd; margin: 1em 0; padding-left: 1em; color: #666; }
                table { border-collapse: collapse; width: 100%; margin: 1em 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background: #f8f8f8; font-weight: bold; }
                ul, ol { padding-left: 2em; margin: 1em 0; }
                .admonitionblock { margin: 1em 0; padding: 1em; border-radius: 5px; }
                .admonitionblock.note { background: #e3f2fd; border-left: 4px solid #2196f3; }
                .admonitionblock.tip { background: #e8f5e9; border-left: 4px solid #4caf50; }
                .admonitionblock.warning { background: #fff3e0; border-left: 4px solid #ff9800; }
                .admonitionblock.caution { background: #ffebee; border-left: 4px solid #f44336; }
                .admonitionblock.important { background: #f3e5f5; border-left: 4px solid #9c27b0; }
                .imageblock { text-align: center; margin: 1em 0; }
                .imageblock img { max-width: 100%; height: auto; }
            """

    def _zoom(self, delta: int) -> None:
        """Zoom editor and preview (delegates to EditorState)."""
        self.editor_state.zoom(delta)

    def _toggle_dark_mode(self) -> None:
        """Toggle dark mode (delegates to EditorState)."""
        self.editor_state.toggle_dark_mode()

    def _toggle_sync_scrolling(self) -> None:
        """Toggle synchronized scrolling (delegates to EditorState)."""
        self.editor_state.toggle_sync_scrolling()

    def _toggle_pane_maximize(self, pane: str) -> None:
        """Toggle maximize/restore for a specific pane (delegates to EditorState)."""
        self.editor_state.toggle_pane_maximize(pane)

    def convert_and_paste_from_clipboard(self) -> None:
        """Convert clipboard content to AsciiDoc (delegates to ExportManager)."""
        self.export_manager.convert_and_paste_from_clipboard()


    def _select_git_repository(self) -> None:
        """Select Git repository (delegates to GitHandler)."""
        self.git_handler.select_repository()

    def _trigger_git_commit(self) -> None:
        """Trigger Git commit (delegates to GitHandler)."""
        self.git_handler.commit_changes()

    def _trigger_git_pull(self) -> None:
        """Trigger Git pull (delegates to GitHandler)."""
        self.git_handler.pull_changes()

    def _trigger_git_push(self) -> None:
        """Trigger Git push (delegates to GitHandler)."""
        self.git_handler.push_changes()

    def _ensure_git_ready(self) -> bool:
        """Ensure Git is ready (delegates to GitHandler)."""
        return self.git_handler._ensure_ready()

    @Slot(GitResult)
    def _handle_git_result(self, result: GitResult) -> None:
        """Handle Git result (delegates to GitHandler)."""
        self.git_handler.handle_git_result(result)

    @Slot(str, str)
    def _handle_pandoc_result(self, result: str, context: str) -> None:
        self._is_processing_pandoc = False
        self._update_ui_state()

        # Delegate to ExportManager
        self.export_manager.handle_pandoc_result(result, context)

        # Handle file import operations
        if self._pending_file_path:

            self._load_content_into_editor(result, self._pending_file_path)
            self._pending_file_path = None

            logger.info(f"Successfully converted {context}")

            QTimer.singleShot(100, self.update_preview)

    @Slot(str, str)
    def _handle_pandoc_error_result(self, error: str, context: str) -> None:
        self._is_processing_pandoc = False
        file_path = self._pending_file_path
        self._pending_file_path = None
        export_path = self.export_manager.pending_export_path
        self.export_manager.pending_export_path = None
        self.export_manager.pending_export_format = None
        self._update_ui_state()
        self.status_bar.showMessage(f"Conversion failed: {context}")

        if export_path and "Exporting to" in context:

            if "PDF" in context and (
                "pdflatex" in error
                or "pdf-engine" in error
                or "No such file or directory" in error
            ):
                error_msg = (
                    f"Failed to export to PDF:\n\n"
                    f"Pandoc could not find a PDF engine on your system.\n\n"
                    f"Solution: Export to HTML instead\n"
                    f"1. File → Save As → Select 'HTML Files (*.html)'\n"
                    f"2. Open the HTML file in your browser\n"
                    f"3. Press Ctrl+P and select 'Save as PDF'\n\n"
                    f"Technical details:\n{error}"
                )
            else:
                error_msg = (
                    f"Failed to export to {export_path.suffix[1:].upper()}:\n{error}"
                )

            self.status_manager.show_message("critical", "Export Error", error_msg)
            return

        self.editor.clear()
        self.preview.setHtml(
            "<h3>Conversion Failed</h3><p>Unable to convert the document.</p>"
        )

        error_msg = f"{context} failed:\n\n{error}"
        if file_path:
            error_msg += f"\n\nFile: {file_path}"

        self.status_manager.show_message("critical", "Conversion Error", error_msg)

    def _update_ui_state(self) -> None:

        self.action_manager.save_act.setEnabled(not self._is_processing_pandoc)
        self.action_manager.save_as_act.setEnabled(not self._is_processing_pandoc)

        export_enabled = not self._is_processing_pandoc
        self.action_manager.save_as_adoc_act.setEnabled(export_enabled)
        self.action_manager.save_as_md_act.setEnabled(export_enabled and PANDOC_AVAILABLE)
        self.action_manager.save_as_docx_act.setEnabled(export_enabled and PANDOC_AVAILABLE)
        self.action_manager.save_as_html_act.setEnabled(export_enabled)
        self.action_manager.save_as_pdf_act.setEnabled(export_enabled and PANDOC_AVAILABLE)

        git_ready = bool(self._settings.git_repo_path) and not self._is_processing_git
        self.action_manager.git_commit_act.setEnabled(git_ready)
        self.action_manager.git_pull_act.setEnabled(git_ready)
        self.action_manager.git_push_act.setEnabled(git_ready)

        self.action_manager.convert_paste_act.setEnabled(
            PANDOC_AVAILABLE and not self._is_processing_pandoc
        )

    def _check_pandoc_availability(self, context: str) -> bool:
        """Check if Pandoc is available for document conversion."""
        if not PANDOC_AVAILABLE:
            self.status_manager.show_message(
                "critical",
                "Pandoc Not Available",
                f"{context} requires Pandoc and pypandoc.\n"
                "Please install them first:\n\n"
                "1. Install pandoc from https://pandoc.org\n"
                "2. Run: pip install pypandoc",
            )
            return False
        return True

    def _show_pandoc_status(self) -> None:
        """Show detailed pandoc installation status."""
        status = "Pandoc Status:\n\n"
        status += f"PANDOC_AVAILABLE: {PANDOC_AVAILABLE}\n"
        status += f"pypandoc module: {'Imported' if pypandoc else 'Not found'}\n"

        if PANDOC_AVAILABLE and pypandoc:
            try:
                version = pypandoc.get_pandoc_version()
                status += f"Pandoc version: {version}\n"
                path = pypandoc.get_pandoc_path()
                status += f"Pandoc path: {path}\n"
            except Exception as e:
                status += f"Error getting pandoc info: {e}\n"

        if not PANDOC_AVAILABLE:
            status += "\nTo enable document conversion:\n"
            status += "1. Install pandoc from https://pandoc.org\n"
            status += "2. Run: pip install pypandoc"

        self.status_manager.show_message("info", "Pandoc Status", status)

    def _show_supported_formats(self) -> None:
        """Show supported input and output formats."""
        if PANDOC_AVAILABLE and pypandoc:
            message = "Supported Conversion Formats:\n\n"
            message += "COMMON INPUT FORMATS:\n"
            message += "  • markdown (.md, .markdown)\n"
            message += "  • docx (Microsoft Word)\n"
            message += "  • html (.html, .htm)\n"
            message += "  • latex (.tex)\n"
            message += "  • rst (reStructuredText)\n"
            message += "  • org (Org Mode)\n"
            message += "\nCOMMON OUTPUT FORMATS:\n"
            message += "  • asciidoc (.adoc)\n"
            message += "  • markdown (.md)\n"
            message += "  • html (.html)\n"
            message += "  • docx (Microsoft Word)\n"
            message += "  • pdf (via PDF engine)\n"
            message += "\nNote: Pandoc supports 40+ formats total.\n"
            message += "See https://pandoc.org for complete list."
            self.status_manager.show_message("info", "Supported Formats", message)
        else:
            self.status_manager.show_message(
                "warning",
                "Format Information Unavailable",
                "Pandoc is not properly configured.\n\n"
                "When configured, you can convert between many formats including:\n"
                "• Markdown to AsciiDoc\n"
                "• DOCX to AsciiDoc\n"
                "• HTML to AsciiDoc\n"
                "• And many more...",
            )

    def _show_message(self, level: str, title: str, text: str) -> None:
        icon_map = {
            "info": QMessageBox.Icon.Information,
            "warning": QMessageBox.Icon.Warning,
            "critical": QMessageBox.Icon.Critical,
        }

        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon_map.get(level, QMessageBox.Icon.Information))
        msg.exec()

    def _prompt_save_before_action(self, action: str) -> bool:
        if not self._unsaved_changes:
            return True

        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            f"Save changes before {action}?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def _show_preferences_dialog(self) -> None:
        """
        Show preferences dialog for configuring application settings.

        FR-055: AI-Enhanced Conversion option configuration UI
        """
        dialog = PreferencesDialog(self._settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._settings = dialog.get_settings()
            self._settings_manager.save_settings(
                self._settings, self, self._current_file_path
            )
            self.status_bar.showMessage("Preferences updated", 3000)
            logger.info(
                f"AI conversion preference updated: {self._settings.ai_conversion_enabled}"
            )

    def _show_ai_setup_help(self) -> None:
        """
        Show help dialog for AI conversion setup.

        FR-055: AI Conversion Setup documentation
        """

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        api_key_status = "✓ Configured" if api_key else "✗ Not Set"
        api_key_color = "green" if api_key else "red"

        client_status = "✓ Available" if AI_CLIENT_AVAILABLE else "✗ Not Available"
        client_color = "green" if AI_CLIENT_AVAILABLE else "red"

        help_text = f"""
        <h2>AI-Enhanced Conversion Setup</h2>

        <h3>Current Status</h3>
        <ul>
            <li><span style="color: {api_key_color}; font-weight: bold;">API Key: {api_key_status}</span></li>
            <li><span style="color: {client_color}; font-weight: bold;">Claude Client: {client_status}</span></li>
        </ul>

        <h3>How to Enable AI Conversion</h3>
        <p>AI-enhanced conversion uses Claude AI to preserve complex formatting like nested lists, tables, and code blocks during document conversion.</p>

        <h4>Step 1: Install the anthropic library</h4>
        <pre style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">pip install anthropic</pre>

        <h4>Step 2: Get an API key from Anthropic</h4>
        <ol>
            <li>Visit <a href="https://console.anthropic.com/">https://console.anthropic.com/</a></li>
            <li>Sign up or log in to your account</li>
            <li>Navigate to API Keys section</li>
            <li>Create a new API key</li>
            <li>Copy the key (it starts with "sk-ant-")</li>
        </ol>

        <h4>Step 3: Set the environment variable</h4>
        <p><b>Windows (PowerShell):</b></p>
        <pre style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">$env:ANTHROPIC_API_KEY = "your-api-key-here"</pre>

        <p><b>Windows (Command Prompt):</b></p>
        <pre style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">set ANTHROPIC_API_KEY=your-api-key-here</pre>

        <p><b>Linux/Mac:</b></p>
        <pre style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">export ANTHROPIC_API_KEY="your-api-key-here"</pre>

        <p><b>Make it permanent:</b> Add the above command to your shell profile (~/.bashrc, ~/.zshrc, or system environment variables on Windows)</p>

        <h4>Step 4: Restart the application</h4>
        <p>After setting the environment variable, restart AsciiDoctor Artisan for the changes to take effect.</p>

        <h4>Step 5: Enable AI conversion</h4>
        <p>Go to <b>Edit → Preferences</b> and check "Enable AI-enhanced conversion by default"</p>

        <h3>Usage Notes</h3>
        <ul>
            <li><b>Cost:</b> AI conversion uses Claude API which may incur usage costs. See <a href="https://www.anthropic.com/pricing">pricing details</a>.</li>
            <li><b>Fallback:</b> If AI conversion fails, the system automatically falls back to Pandoc.</li>
            <li><b>Per-operation override:</b> You can enable/disable AI for individual exports and imports using the conversion dialog.</li>
            <li><b>Supported formats:</b> AI conversion works best for Markdown, HTML, and DOCX conversions.</li>
        </ul>

        <h3>Troubleshooting</h3>
        <ul>
            <li><b>API key not detected:</b> Make sure you set the environment variable and restarted the application.</li>
            <li><b>anthropic library missing:</b> Install it with: <code>pip install anthropic</code></li>
            <li><b>Conversion fails:</b> Check your API key is valid and you have sufficient credits.</li>
        </ul>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle("AI Conversion Setup Guide")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _show_about(self) -> None:
        """Show about dialog."""
        about_text = """
        <h2>AsciiDoctor Artisan</h2>
        <p><b>Version:</b> 1.1.0</p>
        <p><b>Description:</b> A unified, distraction-free environment for AsciiDoc authoring with live preview.</p>

        <h3>Features</h3>
        <ul>
            <li>Real-time AsciiDoc preview</li>
            <li>Git integration for version control</li>
            <li>Multi-format export (Markdown, DOCX, HTML, PDF)</li>
            <li>AI-enhanced document conversion (optional)</li>
            <li>Dark mode support</li>
            <li>Auto-save functionality</li>
        </ul>

        <h3>Technology Stack</h3>
        <ul>
            <li>Python + PySide6 (Qt)</li>
            <li>asciidoc3 for rendering</li>
            <li>Pandoc for format conversion</li>
            <li>Claude AI for enhanced conversions (optional)</li>
        </ul>

        <p><b>License:</b> Open Source</p>
        <p><b>Documentation:</b> See Help menu for AI setup and usage guides</p>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle("About AsciiDoctor Artisan")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def closeEvent(self, event: Any) -> None:
        """Handle window close event (delegates to EditorState)."""
        self.editor_state.handle_close_event(event)
