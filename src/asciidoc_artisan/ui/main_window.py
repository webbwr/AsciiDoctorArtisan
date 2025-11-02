"""
===============================================================================
MAIN WINDOW - The Heart of the Application
===============================================================================

FILE PURPOSE:
This is the most important UI file in the application. It creates and manages
the main application window that users see and interact with. Think of this
as the "control center" that coordinates everything else.

WHAT THIS FILE CONTAINS:
The AsciiDocEditor class - the main window with:
- Left side: Text editor where you write AsciiDoc
- Right side: Live preview showing how it looks
- Top: Menu bar (File, Edit, View, Git, Tools, Help)
- Bottom: Status bar showing file info and AI status

FOR BEGINNERS - ARCHITECTURE OVERVIEW:
This file uses the "Manager Pattern" - instead of doing everything itself,
it delegates work to specialized manager classes:

┌─────────────────────────────────────────────────────────────┐
│                     AsciiDocEditor                          │
│                   (Main Coordinator)                        │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
│ FileHandler  │    │ActionManager│    │ThemeManager │
│(Save/Open)   │    │(Menu/Actions)    │(Dark/Light) │
└──────────────┘    └─────────────┘    └─────────────┘
        │                   │                   │
┌───────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
│ GitHandler   │    │StatusManager│    │WorkerManager│
│(Git Ops)     │    │(Status Bar) │    │(Threads)    │
└──────────────┘    └─────────────┘    └─────────────┘

WHY THIS ARCHITECTURE?:
1. Single Responsibility: Each manager handles ONE thing
2. Maintainability: Easy to find and fix bugs
3. Testability: Can test each manager independently
4. Modularity: Can replace managers without affecting others

KEY RESPONSIBILITIES:
- Create the main window UI (editor + preview split)
- Initialize all manager classes
- Connect signals between managers (like wiring a circuit)
- Coordinate between UI, workers, and business logic
- Handle window lifecycle (startup, running, shutdown)

DESIGN PATTERN USED:
"Delegation Pattern" - The main window doesn't DO the work, it DELEGATES
work to specialized managers. This follows the principle: "A leader's job
is to coordinate, not to do everything themselves."

THREAD ARCHITECTURE:
- Main Thread: Handles UI (this file runs here)
- Worker Threads: Handle slow operations (Git, file I/O, rendering)
- Communication: Qt Signals/Slots (thread-safe messaging)

REFACTORING HISTORY:
- v1.0: Monolithic design (1000+ lines, everything in one class)
- v1.1: Extracted managers (Phase 1-5 refactoring)
- v1.4: GPU acceleration added
- v1.5: Reduced to 561 lines (67% reduction via delegation)

IMPLEMENTS SPECIFICATIONS:
FR-001 to FR-053 (all functional requirements)
See SPECIFICATIONS.md for complete feature list.
"""

# === PYTHON STANDARD LIBRARY IMPORTS ===
# These are built into Python - no installation needed
import html  # For escaping HTML special characters (< > & " ')
import io  # For in-memory file-like objects (BytesIO, StringIO)
import logging  # For recording program events (debug, info, warning, error)
import platform  # For detecting OS (Windows, Linux, Mac)
import tempfile  # For creating temporary files (deleted automatically)
from pathlib import Path  # Modern way to handle file paths (better than strings)
from typing import Any, Optional  # Type hints to catch bugs early

# === QT CORE IMPORTS ===
# Qt's core functionality (not GUI widgets)
from PySide6.QtCore import (
    QRect,  # Rectangle class (x, y, width, height)
    Qt,  # Enums and constants (e.g., Qt.AlignCenter, Qt.Key_Enter)
    QTimer,  # Timer for delayed/repeated actions (like setInterval in JavaScript)
    Signal,  # For emitting events (publisher in pub/sub pattern)
    Slot,  # Decorator for signal receivers (subscriber in pub/sub pattern)
)

# === GPU-ACCELERATED WEB ENGINE (OPTIONAL) ===
# Try to import QtWebEngine for GPU-accelerated preview
# If not available (e.g., on older systems), fall back to QTextBrowser
# This is called "graceful degradation" - app works even without GPU
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: F401

    WEBENGINE_AVAILABLE = True  # Flag: GPU preview available
except ImportError:
    # ImportError = library not installed or not available on this system
    WEBENGINE_AVAILABLE = False  # Flag: Fall back to CPU preview

# === QT WIDGET IMPORTS ===
# Qt's GUI widgets (buttons, windows, etc.)
from PySide6.QtWidgets import (
    QMainWindow,  # Base class for main application windows (has menu bar, status bar)
    QProgressDialog,  # Pop-up showing progress bar for long operations
)

# === CORE MODULE IMPORTS ===
# Constants and utilities used throughout the application
from asciidoc_artisan.core import (
    APP_NAME,  # "AsciiDoc Artisan" - shown in window title
    AUTO_SAVE_INTERVAL_MS,  # How often to auto-save (milliseconds)
    DEFAULT_FILENAME,  # "Untitled.adoc" - default name for new files
    PREVIEW_UPDATE_INTERVAL_MS,  # How often to refresh preview (milliseconds)
    GitResult,  # Data class for Git operation results
    ResourceMonitor,  # Tracks CPU/memory usage
    atomic_save_text,  # Save files atomically (prevents corruption)
)
from asciidoc_artisan.core.large_file_handler import (  # Handles files >10MB
    LargeFileHandler,
)
from asciidoc_artisan.core.search_engine import SearchEngine  # Text search (v1.8.0)

# === UI MANAGER IMPORTS ===
# These "manager" classes handle different parts of the UI
# This is the "Delegation Pattern" - main window delegates to specialists
from asciidoc_artisan.ui.action_manager import ActionManager  # Creates menu actions

# === REMOVED FEATURES (KEPT AS COMMENTS FOR REFERENCE) ===
# MenuManager removed in v1.5.0 - replaced by ActionManager (better architecture)
# from asciidoc_artisan.ui.menu_manager import MenuManager
from asciidoc_artisan.ui.chat_manager import ChatManager  # Manages AI chat (v1.7.0)
from asciidoc_artisan.ui.dialog_manager import DialogManager  # Manages pop-up dialogs
from asciidoc_artisan.ui.editor_state import (  # Tracks editor state (cursor, undo, etc.)
    EditorState,
)
from asciidoc_artisan.ui.export_manager import ExportManager  # Exports to PDF/DOCX/HTML
from asciidoc_artisan.ui.file_handler import FileHandler  # Opens/saves files
from asciidoc_artisan.ui.file_load_manager import (  # Loads files with progress
    FileLoadManager,
)
from asciidoc_artisan.ui.file_operations_manager import (  # File I/O coordinator
    FileOperationsManager,
)
from asciidoc_artisan.ui.git_handler import (  # Git operations (commit/push/pull)
    GitHandler,
)
from asciidoc_artisan.ui.github_handler import (  # GitHub PR/Issue operations
    GitHubHandler,
)
from asciidoc_artisan.ui.pandoc_result_handler import (  # Handles Pandoc results
    PandocResultHandler,
)

# === PREVIEW & RENDERING MANAGERS ===
# GPU-accelerated preview handler - automatically detects GPU and uses it if available
from asciidoc_artisan.ui.preview_handler_gpu import (  # Preview factory
    create_preview_handler,
)
from asciidoc_artisan.ui.scroll_manager import (  # Syncs editor/preview scroll
    ScrollManager,
)
from asciidoc_artisan.ui.settings_manager import SettingsManager  # Loads/saves settings
from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager  # Spell checking
from asciidoc_artisan.ui.status_manager import StatusManager  # Status bar updates
from asciidoc_artisan.ui.theme_manager import ThemeManager  # Dark/light mode switcher
from asciidoc_artisan.ui.ui_setup_manager import UISetupManager  # Sets up UI widgets
from asciidoc_artisan.ui.ui_state_manager import UIStateManager  # Tracks UI state
from asciidoc_artisan.ui.worker_manager import (  # Manages background threads
    WorkerManager,
)

# === OPTIONAL: AI CLIENT ===
# Check if AI client library is installed (for smart document conversion)
# This is optional - app works without it
try:
    import ai_client  # noqa: F401  # AI client for enhanced conversion

    AI_CLIENT_AVAILABLE = True  # Flag: AI features enabled
except ImportError:
    # ImportError = library not installed - that's okay!
    AI_CLIENT_AVAILABLE = False  # Flag: AI features disabled

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
# CONSTANTS (UI-specific color values - other constants imported from core)
# ============================================================================
# Note: UI color constants moved to ui_setup_manager.py (Phase 6b refactoring)


class AsciiDocEditor(QMainWindow):
    request_git_command = Signal(list, str)
    request_github_command = Signal(str, dict)  # operation_type, kwargs
    request_pandoc_conversion = Signal(object, str, str, str, object, bool)
    request_preview_render = Signal(str)
    request_load_file_content = Signal(str, object, str)  # content, file_path, context

    def __init__(self) -> None:
        super().__init__()

        # === Core Configuration ===
        # Settings must be loaded first as other components depend on it
        self._settings_manager = SettingsManager()
        self._settings_path = self._settings_manager.get_settings_path()
        self._settings = self._settings_manager.load_settings()

        # === State Variables ===
        # Initialize state tracking before managers
        self._current_file_path: Optional[Path] = None
        self._initial_geometry: Optional[QRect] = None
        self._start_maximized = self._settings.maximized
        self._is_opening_file = False
        self._is_processing_git = False
        self._last_git_operation = ""
        self._pending_commit_message: Optional[str] = None
        self._unsaved_changes = False
        self._sync_scrolling = True
        self._is_syncing_scroll = False
        self._progress_dialog: Optional[QProgressDialog] = None
        self._temp_dir = tempfile.TemporaryDirectory()

        # Parse window geometry from settings
        if not self._start_maximized:
            self._initial_geometry = self._settings_manager.parse_window_geometry(
                self._settings
            )

        # Restore last file if exists
        if self._settings.last_file and Path(self._settings.last_file).is_file():
            self._current_file_path = Path(self._settings.last_file)

        # === Core Managers (Always Needed) ===
        # These managers are used throughout initialization
        self.status_manager = StatusManager(self)
        self.theme_manager = ThemeManager(self)

        # === UI State & Coordination Managers ===
        self.ui_state_manager = UIStateManager(self)
        self.dialog_manager = DialogManager(self)
        self.scroll_manager = ScrollManager(self)

        # === File & Operations Managers ===
        self.file_load_manager = FileLoadManager(self)
        self.file_operations_manager = FileOperationsManager(self)
        self.pandoc_result_handler = PandocResultHandler(self)

        # === Resource Monitoring ===
        self.resource_monitor = ResourceMonitor()
        logger.info(
            f"ResourceMonitor initialized (psutil available: {self.resource_monitor.is_available()})"
        )

        # Large file handling
        self.large_file_handler = LargeFileHandler()
        self.large_file_handler.progress_update.connect(
            self.file_load_manager.on_file_load_progress
        )

        # === Menu & Actions ===
        # MenuManager removed - replaced by ActionManager (see _setup_actions_and_menus)

        # === Worker Thread Management ===
        self.worker_manager = WorkerManager(self)

        # === AsciiDoc Processing ===
        self._asciidoc_api = self._initialize_asciidoc()
        self._preview_timer = self._setup_preview_timer()

        # === Window Configuration ===
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

        # === UI Setup ===
        self.ui_setup = UISetupManager(self)
        self.ui_setup.setup_ui()

        # === File Operations ===
        self.file_handler = FileHandler(
            self.editor, self, self._settings_manager, self.status_manager
        )
        self.file_handler.start_auto_save(AUTO_SAVE_INTERVAL_MS)

        # === Preview System ===
        self.preview_handler = create_preview_handler(self.editor, self.preview, self)
        self.preview_handler.start_preview_updates()

        # === Git Integration ===
        self.git_handler = GitHandler(self, self._settings_manager, self.status_manager)
        self.git_handler.initialize()  # Load repository from settings

        # === GitHub Integration ===
        self.github_handler = GitHubHandler(
            self, self._settings_manager, self.status_manager, self.git_handler
        )

        # === Actions & Menus ===
        self.action_manager = ActionManager(self)
        self.action_manager.create_actions()
        self.action_manager.create_menus()

        # === Export System ===
        self.export_manager = ExportManager(self)

        # === Editor State ===
        self.editor_state = EditorState(self)

        # === Chat System (v1.7.0) ===
        # ChatManager must be initialized AFTER UISetupManager creates chat_bar and chat_panel
        self.chat_manager = ChatManager(
            self.chat_bar, self.chat_panel, self._settings, parent=self
        )

        # === Find & Search System (v1.8.0) ===
        # SearchEngine must be initialized AFTER UISetupManager creates find_bar
        self._setup_find_system()

        # === Spell Check System (v1.8.0) ===
        # SpellCheckManager must be initialized AFTER UISetupManager creates editor
        self.spell_check_manager = SpellCheckManager(self)
        # Connect editor to spell check manager for context menu
        self.editor.spell_check_manager = self.spell_check_manager
        logger.info("SpellCheckManager initialized")

        # === Telemetry System (v1.8.0) ===
        # Privacy-first telemetry (opt-in only, local storage)
        self._setup_telemetry()

        # === Finalization ===
        self._settings_manager.restore_ui_settings(self, self.splitter, self._settings)
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

    def _setup_find_system(self) -> None:
        """Initialize Find & Replace system (v1.8.0).

        Sets up SearchEngine and connects FindBarWidget signals for:
        - Live search as you type
        - Find next/previous navigation
        - Match counting and highlighting
        """
        # Initialize search engine with current editor text
        self.search_engine = SearchEngine(self.editor.toPlainText())

        # Connect find bar signals to search handlers
        self.find_bar.search_requested.connect(self._handle_search_requested)
        self.find_bar.find_next_requested.connect(self._handle_find_next)
        self.find_bar.find_previous_requested.connect(self._handle_find_previous)
        self.find_bar.closed.connect(self._handle_find_closed)

        # Connect replace signals (v1.8.0)
        self.find_bar.replace_requested.connect(self._handle_replace)
        self.find_bar.replace_all_requested.connect(self._handle_replace_all)

        # Update search engine text when editor content changes
        self.editor.textChanged.connect(
            lambda: self.search_engine.set_text(self.editor.toPlainText())
        )

        logger.info("Find & Replace system initialized")

    def _setup_telemetry(self) -> None:
        """Initialize Telemetry System (v1.8.0).

        Privacy-first telemetry with:
        - Opt-in only (disabled by default)
        - Local storage only (NO cloud upload)
        - Anonymous session IDs
        - GDPR compliance
        - Easy opt-out anytime
        """
        import time
        import uuid

        from asciidoc_artisan.core import TelemetryCollector

        # Show opt-in dialog on first launch (if not already shown)
        if not self._settings.telemetry_opt_in_shown:
            # Delay dialog to allow UI to fully initialize
            QTimer.singleShot(1000, lambda: self._show_telemetry_opt_in_dialog())
            return

        # Initialize telemetry if enabled
        if self._settings.telemetry_enabled:
            # Generate session ID if not exists
            if not self._settings.telemetry_session_id:
                self._settings.telemetry_session_id = str(uuid.uuid4())
                self._settings_manager.save_settings(self._settings)

            # Initialize collector
            self.telemetry_collector = TelemetryCollector(
                enabled=True, session_id=self._settings.telemetry_session_id
            )

            # Track startup
            startup_time = time.time() - getattr(self, "_app_start_time", time.time())
            self.telemetry_collector.track_startup(startup_time)

            logger.info(
                f"TelemetryCollector initialized (session: {self._settings.telemetry_session_id[:8]}...)"
            )
        else:
            # Telemetry disabled - create inactive collector
            self.telemetry_collector = TelemetryCollector(enabled=False)
            logger.info("TelemetryCollector disabled (opt-in not accepted)")

    def _show_telemetry_opt_in_dialog(self) -> None:
        """Show telemetry opt-in dialog (first launch only)."""
        import uuid

        from asciidoc_artisan.core import TelemetryCollector
        from asciidoc_artisan.ui.telemetry_opt_in_dialog import TelemetryOptInDialog

        dialog = TelemetryOptInDialog(self)
        result = dialog.exec()

        if result == TelemetryOptInDialog.Result.ACCEPTED:
            # User accepted - enable telemetry
            self._settings.telemetry_enabled = True
            self._settings.telemetry_session_id = str(uuid.uuid4())
            self._settings.telemetry_opt_in_shown = True
            self._settings_manager.save_settings(self._settings)

            # Initialize collector
            self.telemetry_collector = TelemetryCollector(
                enabled=True, session_id=self._settings.telemetry_session_id
            )

            logger.info("User accepted telemetry (first launch)")

        elif result == TelemetryOptInDialog.Result.DECLINED:
            # User declined - keep telemetry disabled
            self._settings.telemetry_enabled = False
            self._settings.telemetry_opt_in_shown = True
            self._settings_manager.save_settings(self._settings)

            # Create inactive collector
            self.telemetry_collector = TelemetryCollector(enabled=False)

            logger.info("User declined telemetry (first launch)")

        else:
            # User wants to decide later - don't mark as shown
            # Dialog will show again on next launch
            self.telemetry_collector = TelemetryCollector(enabled=False)
            logger.info("User deferred telemetry decision (first launch)")

    def _setup_synchronized_scrolling(self) -> None:
        """Set up synchronized scrolling (delegates to ScrollManager)."""
        self.scroll_manager.setup_synchronized_scrolling()

    def _sync_editor_to_preview(self, value: int) -> None:
        """Synchronize preview scroll (delegates to ScrollManager)."""
        self.scroll_manager.sync_editor_to_preview(value)

    def _sync_preview_to_editor(self, value: int) -> None:
        """Synchronize editor scroll (delegates to ScrollManager)."""
        self.scroll_manager.sync_preview_to_editor(value)

    def _setup_workers_and_threads(self) -> None:
        """Set up worker threads (delegates to WorkerManager)."""
        self.worker_manager.setup_workers_and_threads()

        # === File Load Signal Connection (threading fix) ===
        # Connect file load request signal to handler in main thread
        self.request_load_file_content.connect(
            self.pandoc_result_handler._handle_file_load_request,
            Qt.ConnectionType.QueuedConnection,  # Force main thread execution
        )

        # === Chat System Signal Connections (v1.7.0) ===
        # Connect ChatManager to OllamaChatWorker
        self.chat_manager.message_sent_to_worker.connect(
            self.ollama_chat_worker.send_message
        )
        self.chat_manager.status_message.connect(self.status_manager.show_status)
        self.chat_manager.settings_changed.connect(
            lambda: self._settings_manager.save_settings(self._settings, self)
        )

        # Connect OllamaChatWorker responses back to ChatManager
        self.ollama_chat_worker.chat_response_ready.connect(
            self.chat_manager.handle_response_ready
        )
        self.ollama_chat_worker.chat_response_chunk.connect(
            self.chat_manager.handle_response_chunk
        )
        self.ollama_chat_worker.chat_error.connect(self.chat_manager.handle_error)
        self.ollama_chat_worker.operation_cancelled.connect(
            self.chat_manager.handle_operation_cancelled
        )

        # Connect chat bar cancel button to worker cancellation
        self.chat_bar.cancel_requested.connect(self.ollama_chat_worker.cancel_operation)

        # Initialize chat manager (loads history, sets visibility)
        self.chat_manager.set_document_content_provider(
            lambda: self.editor.toPlainText()
        )
        self.chat_manager.initialize()

        # Initialize GitHub handler (fetches repo info if Git repository is set)
        self.github_handler.initialize()

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

        # Update document metrics (version, word count, grade level)
        self.status_manager.update_document_metrics()

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
        """Apply theme (delegates to ThemeManager)."""
        self.theme_manager.apply_theme()

    def new_file(self) -> None:
        """Create a new file (delegates to FileHandler)."""
        self.file_handler.new_file()

    @Slot()
    def open_file(self) -> None:
        """Open a file (delegates to FileOperationsManager)."""
        self.file_operations_manager.open_file()

    def _load_content_into_editor(self, content: str, file_path: Path) -> None:
        """Load content into editor (delegates to FileLoadManager)."""
        self.file_load_manager.load_content_into_editor(content, file_path)

    @Slot()
    def save_file(self, save_as: bool = False) -> bool:
        """Save file (delegates to FileOperationsManager)."""
        return self.file_operations_manager.save_file(save_as)

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
        """Handle file loading progress (delegates to FileLoadManager)."""
        self.file_load_manager.on_file_load_progress(percentage, message)

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
        """Get CSS for preview rendering (delegates to ThemeManager)."""
        return self.theme_manager.get_preview_css()

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

    def _toggle_maximize_window(self) -> None:
        """Toggle maximize/restore application window to full screen."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

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

    def _trigger_github_create_pr(self) -> None:
        """Create GitHub pull request (delegates to GitHubHandler)."""
        if hasattr(self, "github_handler"):
            self.github_handler.create_pull_request()

    def _trigger_github_list_prs(self) -> None:
        """List GitHub pull requests (delegates to GitHubHandler)."""
        if hasattr(self, "github_handler"):
            self.github_handler.list_pull_requests()

    def _trigger_github_create_issue(self) -> None:
        """Create GitHub issue (delegates to GitHubHandler)."""
        if hasattr(self, "github_handler"):
            self.github_handler.create_issue()

    def _trigger_github_list_issues(self) -> None:
        """List GitHub issues (delegates to GitHubHandler)."""
        if hasattr(self, "github_handler"):
            self.github_handler.list_issues()

    def _trigger_github_repo_info(self) -> None:
        """Show GitHub repository info (delegates to GitHubHandler)."""
        if hasattr(self, "github_handler"):
            self.github_handler.get_repo_info()

    def _ensure_git_ready(self) -> bool:
        """Ensure Git is ready (delegates to GitHandler)."""
        return self.git_handler._ensure_ready()

    @Slot(GitResult)
    def _handle_git_result(self, result: GitResult) -> None:
        """Handle Git result (delegates to GitHandler)."""
        self.git_handler.handle_git_result(result)

    @Slot(object)
    def _handle_github_result(self, result: Any) -> None:
        """Handle GitHub result (delegates to GitHubHandler)."""
        from asciidoc_artisan.core import GitHubResult

        if isinstance(result, GitHubResult):
            self.github_handler.handle_github_result(result)

    @Slot(str, str)
    def _handle_pandoc_result(self, result: str, context: str) -> None:
        """Handle Pandoc conversion result (delegates to PandocResultHandler)."""
        self.pandoc_result_handler.handle_pandoc_result(result, context)

    @Slot(str, str)
    def _handle_pandoc_error_result(self, error: str, context: str) -> None:
        """Handle Pandoc conversion error (delegates to PandocResultHandler)."""
        self.pandoc_result_handler.handle_pandoc_error_result(error, context)

    # ========================================================================
    # Find & Search Handlers (v1.8.0)
    # ========================================================================

    @Slot(str, bool)
    def _handle_search_requested(self, search_text: str, case_sensitive: bool) -> None:
        """Handle search text changes from find bar (live search).

        Args:
            search_text: Text to search for
            case_sensitive: Whether search is case-sensitive
        """
        if not search_text:
            # Clear highlighting if search is empty
            self._clear_search_highlighting()
            self.find_bar.update_match_count(0, 0)
            return

        try:
            # Find all matches
            matches = self.search_engine.find_all(search_text, case_sensitive=case_sensitive)

            # Update match count in find bar
            if matches:
                # Find which match is closest to current cursor position
                cursor = self.editor.textCursor()
                current_pos = cursor.position()

                # Find first match at or after cursor position
                current_match_index = 0
                for i, match in enumerate(matches):
                    if match.start >= current_pos:
                        current_match_index = i
                        break
                else:
                    # If no match after cursor, use last match (wrapping)
                    current_match_index = len(matches) - 1

                self.find_bar.update_match_count(current_match_index + 1, len(matches))

                # Highlight all matches
                self._highlight_search_matches(matches)

                # Select current match
                if matches:
                    self._select_match(matches[current_match_index])
            else:
                self.find_bar.update_match_count(0, 0)
                self.find_bar.set_not_found_style()
                self._clear_search_highlighting()

        except Exception as e:
            logger.error(f"Search error: {e}")
            self.find_bar.update_match_count(0, 0)

    @Slot()
    def _handle_find_next(self) -> None:
        """Navigate to next search match."""
        search_text = self.find_bar.get_search_text()
        if not search_text:
            return

        try:
            cursor = self.editor.textCursor()
            current_pos = cursor.position()

            # Find next match after current position
            match = self.search_engine.find_next(
                search_text,
                start_offset=current_pos,
                case_sensitive=self.find_bar.is_case_sensitive(),
                wrap_around=True
            )

            if match:
                self._select_match(match)
                # Update counter
                matches = self.search_engine.find_all(search_text, case_sensitive=self.find_bar.is_case_sensitive())
                match_index = matches.index(match) if match in matches else 0
                self.find_bar.update_match_count(match_index + 1, len(matches))

        except Exception as e:
            logger.error(f"Find next error: {e}")

    @Slot()
    def _handle_find_previous(self) -> None:
        """Navigate to previous search match."""
        search_text = self.find_bar.get_search_text()
        if not search_text:
            return

        try:
            cursor = self.editor.textCursor()
            current_pos = cursor.selectionStart()  # Start of current selection

            # Find previous match before current position
            match = self.search_engine.find_previous(
                search_text,
                start_offset=current_pos,
                case_sensitive=self.find_bar.is_case_sensitive(),
                wrap_around=True
            )

            if match:
                self._select_match(match)
                # Update counter
                matches = self.search_engine.find_all(search_text, case_sensitive=self.find_bar.is_case_sensitive())
                match_index = matches.index(match) if match in matches else 0
                self.find_bar.update_match_count(match_index + 1, len(matches))

        except Exception as e:
            logger.error(f"Find previous error: {e}")

    @Slot()
    def _handle_find_closed(self) -> None:
        """Handle find bar being closed."""
        self._clear_search_highlighting()
        self.editor.setFocus()  # Return focus to editor
        logger.debug("Find bar closed, focus returned to editor")

    @Slot(str)
    def _handle_replace(self, replace_text: str) -> None:
        """Replace current match and find next.

        Args:
            replace_text: Text to replace with
        """
        search_text = self.find_bar.get_search_text()
        if not search_text:
            return

        try:
            # Get current selection
            cursor = self.editor.textCursor()
            if not cursor.hasSelection():
                # No selection, find next match first
                self._handle_find_next()
                cursor = self.editor.textCursor()
                if not cursor.hasSelection():
                    return

            # Verify selection matches search text
            selected_text = cursor.selectedText()
            case_sensitive = self.find_bar.is_case_sensitive()

            # Check if selection matches search text
            if case_sensitive:
                matches = selected_text == search_text
            else:
                matches = selected_text.lower() == search_text.lower()

            if matches:
                # Replace the selected text
                cursor.insertText(replace_text)
                self.editor.setTextCursor(cursor)

                # Update search engine with new text
                self.search_engine.set_text(self.editor.toPlainText())

                # Find next occurrence
                self._handle_find_next()

                logger.info(f"Replaced '{search_text}' with '{replace_text}'")
            else:
                # Selection doesn't match, just find next
                self._handle_find_next()

        except Exception as e:
            logger.error(f"Replace error: {e}")

    @Slot(str)
    def _handle_replace_all(self, replace_text: str) -> None:
        """Replace all occurrences after confirmation.

        Args:
            replace_text: Text to replace with
        """
        from PySide6.QtWidgets import QMessageBox

        search_text = self.find_bar.get_search_text()
        if not search_text:
            return

        try:
            # Count matches first
            matches = self.search_engine.find_all(
                search_text, case_sensitive=self.find_bar.is_case_sensitive()
            )
            match_count = len(matches)

            if match_count == 0:
                self.status_manager.show_status("No matches to replace", 2000)
                return

            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Replace All",
                f"Replace {match_count} occurrence(s) of '{search_text}' with '{replace_text}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Perform replace all
                new_text, count = self.search_engine.replace_all(
                    search_text,
                    replace_text,
                    case_sensitive=self.find_bar.is_case_sensitive(),
                )

                # Update editor with new text
                cursor = self.editor.textCursor()
                cursor_pos = cursor.position()  # Save cursor position

                self.editor.setPlainText(new_text)

                # Restore cursor position (approximately)
                cursor.setPosition(min(cursor_pos, len(new_text)))
                self.editor.setTextCursor(cursor)

                # Clear highlights and update status
                self._clear_search_highlighting()
                self.find_bar.update_match_count(0, 0)
                self.status_manager.show_status(
                    f"Replaced {count} occurrence(s)", 3000
                )

                logger.info(
                    f"Replaced all: {count} occurrences of '{search_text}' with '{replace_text}'"
                )

        except Exception as e:
            logger.error(f"Replace all error: {e}")
            self.status_manager.show_status(f"Replace failed: {e}", 3000)

    def _select_match(self, match) -> None:
        """Select a search match in the editor.

        Args:
            match: SearchMatch object with start/end positions
        """
        from PySide6.QtGui import QTextCursor

        cursor = self.editor.textCursor()
        cursor.setPosition(match.start)
        cursor.setPosition(match.end, QTextCursor.MoveMode.KeepAnchor)
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()

    def _highlight_search_matches(self, matches) -> None:
        """Highlight all search matches in the editor.

        Args:
            matches: List of SearchMatch objects
        """
        from PySide6.QtGui import QTextEdit

        # Clear existing highlights
        self._clear_search_highlighting()

        # Create extra selections for each match
        extra_selections = []
        for match in matches:
            selection = QTextEdit.ExtraSelection()
            cursor = self.editor.textCursor()
            cursor.setPosition(match.start)
            cursor.setPosition(match.end, QTextEdit.ExtraSelection.Cursor.KeepAnchor)

            # Yellow highlight for matches
            from PySide6.QtGui import QColor
            selection.format.setBackground(QColor(255, 255, 0, 80))  # Light yellow
            selection.cursor = cursor
            extra_selections.append(selection)

        self.editor.setExtraSelections(extra_selections)

    def _clear_search_highlighting(self) -> None:
        """Clear all search highlighting from the editor."""
        self.editor.setExtraSelections([])
        self.find_bar.clear_not_found_style()

    def _update_ui_state(self) -> None:
        """Update UI element states (delegates to UIStateManager)."""
        self.ui_state_manager.update_ui_state()

    def _update_ai_status_bar(self) -> None:
        """Update AI model name in status bar (delegates to UIStateManager)."""
        self.ui_state_manager.update_ai_status_bar()

    def _check_pandoc_availability(self, context: str) -> bool:
        """Check if Pandoc is available (delegates to UIStateManager)."""
        return self.ui_state_manager.check_pandoc_availability(context)

    # ========================================================================
    # Dialog Methods (Phase 6b: Delegated to DialogManager)
    # ========================================================================

    def _show_installation_validator(self) -> None:
        """Show installation validator dialog (delegates to DialogManager)."""
        self.dialog_manager.show_installation_validator()

    def _show_pandoc_status(self) -> None:
        """Show detailed pandoc installation status (delegates to DialogManager)."""
        self.dialog_manager.show_pandoc_status()

    def _show_supported_formats(self) -> None:
        """Show supported input and output formats (delegates to DialogManager)."""
        self.dialog_manager.show_supported_formats()

    def _show_ollama_status(self) -> None:
        """Show Ollama service and installation status (delegates to DialogManager)."""
        self.dialog_manager.show_ollama_status()

    def _show_ollama_settings(self) -> None:
        """Show Ollama AI settings dialog (delegates to DialogManager)."""
        self.dialog_manager.show_ollama_settings()

    def _show_app_settings(self) -> None:
        """Show application settings editor dialog (delegates to DialogManager)."""
        self.dialog_manager.show_app_settings()

    def _show_font_settings(self) -> None:
        """Show font settings dialog (delegates to DialogManager)."""
        self.dialog_manager.show_font_settings()

    def _show_message(self, level: str, title: str, text: str) -> None:
        """Show message box (delegates to DialogManager)."""
        self.dialog_manager.show_message(level, title, text)

    def _prompt_save_before_action(self, action: str) -> bool:
        """Prompt to save before action (delegates to DialogManager)."""
        return self.dialog_manager.prompt_save_before_action(action)

    def _show_preferences_dialog(self) -> None:
        """Show preferences dialog (delegates to DialogManager)."""
        self.dialog_manager.show_preferences_dialog()

    def _show_about(self) -> None:
        """Show about dialog (delegates to DialogManager)."""
        self.dialog_manager.show_about()

    def _refresh_from_settings(self) -> None:
        """Refresh application state from updated settings."""
        # Reload settings from the updated settings object
        settings = self._settings

        # Apply theme
        if settings.dark_mode:
            self.theme_manager.apply_dark_theme()
        else:
            self.theme_manager.apply_light_theme()

        # Update font size
        from PySide6.QtGui import QFont

        from asciidoc_artisan.core import EDITOR_FONT_FAMILY

        font = QFont(EDITOR_FONT_FAMILY, settings.font_size)
        self.editor.setFont(font)

        # Update AI status bar
        self._update_ai_status_bar()

        # Update PandocWorker with new Ollama configuration
        if hasattr(self, "pandoc_worker"):
            self.pandoc_worker.set_ollama_config(
                settings.ollama_enabled, settings.ollama_model
            )

        # Update ChatManager with new settings
        if hasattr(self, "chat_manager"):
            self.chat_manager.update_settings(settings)

        # Update window geometry if not maximized
        if not settings.maximized and settings.window_geometry:
            geom = settings.window_geometry
            self.setGeometry(geom["x"], geom["y"], geom["width"], geom["height"])

        # Update splitter sizes if available
        if settings.splitter_sizes and hasattr(self, "splitter"):
            self.splitter.setSizes(settings.splitter_sizes)

        # Apply font settings
        if hasattr(self, "dialog_manager"):
            self.dialog_manager._apply_font_settings()

        logger.info("Application refreshed from updated settings")

    def closeEvent(self, event: Any) -> None:
        """Handle window close event (delegates to EditorState)."""
        import os

        # Skip save prompts in test environment to prevent blocking
        if os.environ.get("PYTEST_CURRENT_TEST"):
            event.accept()
            return

        self.editor_state.handle_close_event(event)
