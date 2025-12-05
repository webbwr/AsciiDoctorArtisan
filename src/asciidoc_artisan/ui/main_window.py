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
import os  # For environment variables and file operations
import platform  # For detecting OS (Windows, Linux, Mac)
import tempfile  # For creating temporary files (deleted automatically)
from pathlib import Path  # Modern way to handle file paths (better than strings)
from typing import Any, cast  # Type hints to catch bugs early

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
from asciidoc_artisan.core.autocomplete_engine import (
    AutoCompleteEngine,
)  # Auto-complete engine (v2.0.0)
from asciidoc_artisan.core.large_file_handler import (  # Handles files >10MB
    LargeFileHandler,
)
from asciidoc_artisan.core.search_engine import (
    SearchEngine,
)  # Text search (v1.8.0)
from asciidoc_artisan.core.syntax_checker import (
    SyntaxChecker,
)  # Syntax checker core (v2.0.0)
from asciidoc_artisan.core.template_engine import (
    TemplateEngine,
)  # Template rendering (v2.0.0)
from asciidoc_artisan.core.template_manager import (
    TemplateManager,
)  # Template management (v2.0.0)

# === UI MANAGER IMPORTS ===
# These "manager" classes handle different parts of the UI
# This is the "Delegation Pattern" - main window delegates to specialists
from asciidoc_artisan.ui.action_manager import ActionManager  # Creates menu actions

# === V2.0.0 FEATURE MANAGERS ===
from asciidoc_artisan.ui.autocomplete_manager import (
    AutoCompleteManager,
)  # Auto-complete (v2.0.0)

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
from asciidoc_artisan.ui.search_handler import SearchHandler  # Find/Replace operations (MA)
from asciidoc_artisan.ui.settings_dialog_helper import SettingsDialogHelper  # Settings dialogs (MA)
from asciidoc_artisan.ui.settings_manager import SettingsManager  # Loads/saves settings
from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager  # Spell checking
from asciidoc_artisan.ui.status_manager import StatusManager  # Status bar updates
from asciidoc_artisan.ui.syntax_checker_manager import (
    SyntaxCheckerManager,
)  # Syntax checking (v2.0.0)
from asciidoc_artisan.ui.template_browser import (  # Template browsing dialog (v2.0.0)
    TemplateBrowser,
)
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

# Lazy import check for Pandoc (deferred until first use for faster startup)
# Note: is_pandoc_available() is called dynamically, not imported directly

logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS (UI-specific color values - other constants imported from core)
# ============================================================================
# Note: UI color constants moved to ui_setup_manager.py (Phase 6b refactoring)


class AsciiDocEditor(QMainWindow):
    request_git_command = Signal(list, str)
    request_git_status = Signal(str)  # repository_path (v1.9.0+)
    request_detailed_git_status = Signal(str)  # repository_path (v1.9.0+)
    request_github_command = Signal(str, dict)  # operation_type, kwargs
    request_pandoc_conversion = Signal(object, str, str, str, object, bool)
    request_preview_render = Signal(str)
    request_load_file_content = Signal(str, object, str)  # content, file_path, context

    def _init_settings(self) -> None:
        """
        Initialize settings manager and load configuration.

        MA principle: Extracted from __init__ (5 lines).
        """
        self._settings_manager = SettingsManager()
        self._settings_path = self._settings_manager.get_settings_path()
        self._settings = self._settings_manager.load_settings()

    def _init_state_variables(self) -> None:
        """
        Initialize state tracking variables.

        MA principle: Extracted from __init__ (23 lines).
        """
        self._current_file_path: Path | None = None
        self._initial_geometry: QRect | None = None
        self._start_maximized = self._settings.maximized
        self._is_opening_file = False
        self._is_processing_git = False
        self._last_git_operation = ""
        self._pending_commit_message: str | None = None
        self._unsaved_changes = False
        self._sync_scrolling = True
        self._is_syncing_scroll = False
        self._progress_dialog: QProgressDialog | None = None
        self._temp_dir = tempfile.TemporaryDirectory()

        # Parse window geometry from settings
        if not self._start_maximized:
            self._initial_geometry = self._settings_manager.parse_window_geometry(self._settings)

        # Restore last file if exists
        if self._settings.last_file and Path(self._settings.last_file).is_file():
            self._current_file_path = Path(self._settings.last_file)

    def _init_core_managers(self) -> None:
        """
        Initialize core managers (status, theme).

        MA principle: Extracted from __init__ (3 lines).
        """
        self.status_manager = StatusManager(self)
        self.theme_manager = ThemeManager(self)

    def _init_ui_managers(self) -> None:
        """
        Initialize UI state and coordination managers.

        MA principle: Extracted from __init__ (4 lines).
        """
        self.ui_state_manager = UIStateManager(self)
        self.dialog_manager = DialogManager(self)
        self.scroll_manager = ScrollManager(self)

    def _init_file_managers(self) -> None:
        """
        Initialize file and operations managers.

        MA principle: Extracted from __init__ (4 lines).
        """
        self.file_load_manager = FileLoadManager(self)
        self.file_operations_manager = FileOperationsManager(self)
        self.pandoc_result_handler = PandocResultHandler(self)

    def _init_resource_monitoring(self) -> None:
        """
        Initialize resource monitoring and large file handling.

        MA principle: Extracted from __init__ (7 lines).
        """
        self.resource_monitor = ResourceMonitor()
        logger.info(f"ResourceMonitor initialized (psutil available: {self.resource_monitor.is_available()})")

        self.large_file_handler = LargeFileHandler()
        self.large_file_handler.progress_update.connect(self.file_load_manager.on_file_load_progress)

    def _init_worker_management(self) -> None:
        """
        Initialize worker thread management.

        MA principle: Extracted from __init__ (2 lines).
        """
        self.worker_manager = WorkerManager(self)

    def _init_asciidoc_and_preview(self) -> None:
        """
        Initialize AsciiDoc API and preview timer.

        MA principle: Extracted from __init__ (3 lines).
        """
        self._asciidoc_api = self._initialize_asciidoc()
        self._preview_timer = self._setup_preview_timer()

    def _configure_window(self) -> None:
        """
        Configure window title and flags.

        MA principle: Extracted from __init__ (12 lines).
        """
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

    def _setup_ui_components(self) -> None:
        """
        Setup UI components via UISetupManager.

        MA principle: Extracted from __init__ (3 lines).
        """
        self.ui_setup = UISetupManager(self)
        self.ui_setup.setup_ui()

    def _setup_file_operations(self) -> None:
        """
        Setup file operations and auto-save.

        MA principle: Extracted from __init__ (3 lines).
        """
        self.file_handler = FileHandler(self.editor, self, self._settings_manager, self.status_manager)
        self.file_handler.start_auto_save(AUTO_SAVE_INTERVAL_MS)

    def _setup_preview_system(self) -> None:
        """
        Setup preview handler and start updates.

        MA principle: Extracted from __init__ (3 lines).
        """
        self.preview_handler = create_preview_handler(self.editor, self.preview, self)
        self.preview_handler.start_preview_updates()

    def _setup_git_integration(self) -> None:
        """
        Setup Git and GitHub integration.

        MA principle: Extracted from __init__ (6 lines).
        """
        self.git_handler = GitHandler(self, self._settings_manager, self.status_manager)
        self.git_handler.initialize()

        self.github_handler = GitHubHandler(self, self._settings_manager, self.status_manager, self.git_handler)

    def _setup_editor_features(self) -> None:
        """
        Setup editor features (spell check, autocomplete, syntax, templates).

        MA principle: Extracted from __init__ (19 lines).
        """
        # Spell Check System (v1.8.0)
        self.spell_check_manager = SpellCheckManager(self)
        self.editor.spell_check_manager = self.spell_check_manager
        logger.info("SpellCheckManager initialized")

        # Auto-Complete System (v2.0.0)
        self._setup_autocomplete()

        # Syntax Checking System (v2.0.0)
        self._setup_syntax_checker()

        # Template System (v2.0.0)
        self._setup_template_system()

    def _setup_actions_and_export(self) -> None:
        """
        Setup actions, menus, and export system.

        MA principle: Extracted from __init__ (12 lines).
        """
        self.action_manager = ActionManager(self)
        self.action_manager.create_actions()
        self.action_manager.create_menus()

        # Update spell check menu text to show initial state
        self.spell_check_manager._update_menu_text()

        # Update telemetry menu text to show initial state (deferred until telemetry_manager exists)

        # Export System
        self.export_manager = ExportManager(self)

    def _setup_chat_and_search(self) -> None:
        """
        Setup chat, find, and quick commit systems.

        MA principle: Extracted from __init__ (12 lines).
        """
        # Editor State
        self.editor_state = EditorState(self)

        # Chat System (v1.7.0)
        self.chat_manager = ChatManager(self.chat_bar, self.chat_panel, self._settings, parent=self)

        # Chat Worker Router (MA extraction)
        from asciidoc_artisan.ui.chat_worker_router import ChatWorkerRouter

        self.chat_worker_router = ChatWorkerRouter(self)

        # Find & Search System (v1.8.0)
        self._setup_find_system()

        # Quick Commit System (v1.9.0)
        self._setup_quick_commit()

    def _finalize_initialization(self) -> None:
        """
        Finalize initialization (telemetry, restore settings, apply theme).

        MA principle: Extracted from __init__ (11 lines).
        """
        # Telemetry System (v1.8.0)
        from asciidoc_artisan.ui.telemetry_manager import TelemetryManager

        self.telemetry_manager = TelemetryManager(self)
        self.telemetry_collector = self.telemetry_manager.initialize(getattr(self, "_app_start_time", None))
        # Update telemetry menu text now that manager exists
        self.telemetry_manager._update_menu_text()

        # Restore UI settings and apply theme
        self._settings_manager.restore_ui_settings(self, self.splitter, self._settings)
        self.theme_manager.apply_theme()
        self._setup_workers_and_threads()
        self._update_ui_state()

        # Update AI backend checkmarks
        self._update_ai_backend_checkmarks()

    def __init__(self) -> None:
        """
        Initialize the main window.

        MA principle: Reduced from 159→34 lines by extracting 15 helper methods.

        Initialization phases:
        1. Core configuration (settings, state variables, managers)
        2. Resource monitoring and worker management
        3. AsciiDoc processing and window setup
        4. UI components and file operations
        5. Preview and Git integration
        6. Editor features (spell check, autocomplete, syntax, templates)
        7. Actions, menus, and export system
        8. Chat, search, and finalization
        """
        super().__init__()

        # Phase 1: Core Configuration
        self._init_settings()
        self._init_state_variables()
        self._init_core_managers()
        self._init_ui_managers()
        self._init_file_managers()

        # Phase 2: Resource & Workers
        self._init_resource_monitoring()
        self._init_worker_management()

        # Phase 3: AsciiDoc & Window
        self._init_asciidoc_and_preview()
        self._configure_window()

        # Phase 4: UI & File Operations
        self._setup_ui_components()
        self._setup_file_operations()

        # Phase 5: Preview & Git
        self._setup_preview_system()
        self._setup_git_integration()

        # Phase 6: Editor Features
        self._setup_editor_features()

        # Phase 7: Actions & Export
        self._setup_actions_and_export()

        # Phase 8: Chat, Search & Finalization
        self._setup_chat_and_search()
        self._finalize_initialization()

    def _initialize_asciidoc(self) -> AsciiDoc3API | None:
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

        # Initialize search handler (MA principle: extracted from main_window)
        from asciidoc_artisan.ui.search_handler import SearchContext

        self.search_handler = SearchHandler(cast(SearchContext, self))

        # Connect find bar signals to search handler
        self.find_bar.search_requested.connect(self.search_handler.handle_search_requested)
        self.find_bar.find_next_requested.connect(self.search_handler.handle_find_next)
        self.find_bar.find_previous_requested.connect(self.search_handler.handle_find_previous)
        self.find_bar.closed.connect(self.search_handler.handle_find_closed)

        # Connect replace signals (v1.8.0)
        self.find_bar.replace_requested.connect(self.search_handler.handle_replace)
        self.find_bar.replace_all_requested.connect(self.search_handler.handle_replace_all)

        # Update search engine text when editor content changes
        self.editor.textChanged.connect(lambda: self.search_engine.set_text(self.editor.toPlainText()))

        logger.info("Find & Replace system initialized")

    def _setup_quick_commit(self) -> None:
        """Initialize Quick Commit system (v1.9.0).

        Sets up QuickCommitWidget signals for inline Git commits.
        Enables keyboard-driven workflow (Ctrl+G to show, Enter to commit, Esc to cancel).
        """
        # Connect quick commit widget signals
        self.quick_commit_widget.commit_requested.connect(self._handle_quick_commit)
        self.quick_commit_widget.cancelled.connect(lambda: logger.debug("Quick commit cancelled"))

        logger.info("Quick Commit system initialized")

    def toggle_telemetry(self) -> None:
        """Toggle telemetry on/off (delegates to TelemetryManager)."""
        self.telemetry_manager.toggle()
        self.telemetry_collector = self.telemetry_manager.collector

    def _setup_autocomplete(self) -> None:
        """Initialize Auto-Complete System (v2.0.0).

        Sets up auto-complete with:
        - Automatic completion on typing (300ms debounce)
        - Manual trigger with Ctrl+Space
        - Context-aware suggestions (syntax, snippets, recent)
        - Smart text insertion with word prefix detection
        """
        # Initialize auto-complete engine
        engine = AutoCompleteEngine()

        # Create manager and connect to editor
        self.autocomplete_manager = AutoCompleteManager(self.editor, engine)

        # Load settings
        self.autocomplete_manager.enabled = self._settings.autocomplete_enabled
        self.autocomplete_manager.auto_delay = self._settings.autocomplete_delay

        logger.info("AutoCompleteManager initialized")

    def _setup_syntax_checker(self) -> None:
        """Initialize Syntax Checking System (v2.0.0).

        Sets up syntax checking with:
        - Real-time error detection (500ms debounce)
        - Color-coded underlines (red=error, orange=warning)
        - Jump to next/previous error (F8, Shift+F8)
        - Quick fix suggestions with Ctrl+.
        """
        # Initialize syntax checker engine
        checker = SyntaxChecker()

        # Create manager and connect to editor
        self.syntax_checker_manager = SyntaxCheckerManager(self.editor, checker)

        # Load settings
        self.syntax_checker_manager.enabled = self._settings.syntax_check_realtime_enabled
        self.syntax_checker_manager.check_delay = self._settings.syntax_check_delay

        # Initialize settings dialog helper (MA principle: extracted dialogs)
        from asciidoc_artisan.ui.settings_dialog_helper import SettingsContext

        self.settings_dialog_helper = SettingsDialogHelper(self, cast(SettingsContext, self))

        logger.info("SyntaxCheckerManager initialized")

    def _setup_template_system(self) -> None:
        """Initialize Template System (v2.0.0).

        Sets up template management with:
        - Built-in templates (article, book, manual, etc.)
        - Custom user templates
        - Recent templates tracking
        - Template variable substitution
        """
        # Initialize template engine
        engine = TemplateEngine()

        # Create template manager
        self.template_manager = TemplateManager(engine)

        # Load all templates (built-in + custom)
        templates = self.template_manager.get_all_templates()
        logger.info(f"TemplateManager initialized with {len(templates)} templates")

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

        # === Chat System Signal Connections (v1.7.0, v1.10.0) ===
        # Connect ChatManager to both workers via router
        self.chat_manager.message_sent_to_worker.connect(self.chat_worker_router.route_message)
        self.chat_manager.status_message.connect(self.status_manager.show_status)
        self.chat_manager.settings_changed.connect(lambda: self._settings_manager.save_settings(self._settings, self))

        # Connect OllamaChatWorker responses back to ChatManager
        self.ollama_chat_worker.chat_response_ready.connect(self.chat_manager.handle_response_ready)
        self.ollama_chat_worker.chat_response_chunk.connect(self.chat_manager.handle_response_chunk)
        self.ollama_chat_worker.chat_error.connect(self.chat_manager.handle_error)
        self.ollama_chat_worker.operation_cancelled.connect(self.chat_manager.handle_operation_cancelled)

        # Connect ClaudeWorker responses back to ChatManager (via adapters)
        self.claude_worker.response_ready.connect(self.chat_worker_router.adapt_claude_response)
        self.claude_worker.error_occurred.connect(self.chat_manager.handle_error)

        # Connect chat bar cancel button to worker cancellation
        self.chat_bar.cancel_requested.connect(self.ollama_chat_worker.cancel_operation)
        # Note: ClaudeWorker doesn't support cancellation yet

        # Initialize chat manager (loads history, sets visibility)
        self.chat_manager.set_document_content_provider(lambda: self.editor.toPlainText())
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
            logger.debug(f"Adaptive debounce: {debounce_ms}ms for {len(text)} chars, {text.count(chr(10)) + 1} lines")

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

    def new_from_template(self) -> None:
        """
        Create a new document from a template (v2.0.0).

        Shows the TemplateBrowser dialog with 6 built-in templates.
        If user selects a template and provides variable values,
        creates a new document with the instantiated template content.
        """
        # Show template browser dialog
        browser = TemplateBrowser(self.template_manager, self)

        if browser.exec():
            # User selected a template
            template = browser.selected_template
            variables = browser.variable_values

            if template:
                # Instantiate template with user-provided variables
                engine = TemplateEngine()
                content = engine.instantiate(template, variables)

                # Create new document with template content
                self.file_handler.new_file()
                self.editor.setPlainText(content)
                self.has_unsaved_changes = True

                # Log template usage
                import logging

                logger = logging.getLogger(__name__)
                logger.info(f"Created new document from template: {template.name}")

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

    def _show_git_status(self) -> None:
        """Show Git status dialog with detailed file-level information (v1.9.0+)."""
        if not self._ensure_git_ready():
            return

        # Create dialog if not exists
        if not hasattr(self, "_git_status_dialog"):
            from .git_status_dialog import GitStatusDialog

            self._git_status_dialog = GitStatusDialog(self)

            # Connect dialog signals
            self._git_status_dialog.refresh_requested.connect(self._refresh_git_status_dialog)
            # Note: Stage/Unstage buttons not implemented yet - future enhancement

        # Request detailed status from worker
        repo_path = self.git_handler.get_repository_path()
        if repo_path and hasattr(self, "request_detailed_git_status"):
            self.request_detailed_git_status.emit(repo_path)

        # Show dialog
        self._git_status_dialog.show()
        self._git_status_dialog.raise_()
        self._git_status_dialog.activateWindow()

    def _refresh_git_status_dialog(self) -> None:
        """Refresh Git status dialog data (v1.9.0+)."""
        repo_path = self.git_handler.get_repository_path()
        if repo_path and hasattr(self, "request_detailed_git_status"):
            self.request_detailed_git_status.emit(repo_path)

    def _show_quick_commit(self) -> None:
        """Show quick commit widget for inline Git commits (v1.9.0+)."""
        if not self._ensure_git_ready():
            return

        # Show widget and focus input
        self.quick_commit_widget.show_and_focus()
        logger.debug("Quick commit widget shown")

    @Slot(str)
    def _handle_quick_commit(self, message: str) -> None:
        """Handle quick commit request (v1.9.0+).

        Args:
            message: Commit message from QuickCommitWidget
        """
        if not self._ensure_git_ready():
            return

        logger.info(f"Quick commit requested: '{message[:50]}...'")

        # Delegate to GitHandler
        self.git_handler.quick_commit(message)

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
    def _handle_git_status(self, status: Any) -> None:
        """Handle Git status update (delegates to StatusManager, v1.9.0+)."""
        from asciidoc_artisan.core import GitStatus

        if isinstance(status, GitStatus):
            self.status_manager.update_git_status(status)

    @Slot(dict)
    def _handle_detailed_git_status(self, status_data: dict[str, Any]) -> None:
        """Handle detailed Git status update (populates dialog, v1.9.0+)."""
        if hasattr(self, "_git_status_dialog") and self._git_status_dialog.isVisible():
            branch = status_data.get("branch", "unknown")
            modified = status_data.get("modified", [])
            staged = status_data.get("staged", [])
            untracked = status_data.get("untracked", [])

            self._git_status_dialog.populate_status(branch, modified, staged, untracked)

    @Slot(object)
    def _handle_github_result(self, result: Any) -> None:
        """Handle GitHub result (delegates to GitHubHandler)."""
        from asciidoc_artisan.core import GitHubResult

        if isinstance(result, GitHubResult):
            self.github_handler.handle_github_result(result)

    # Chat routing delegated to ChatWorkerRouter (MA extraction)

    @Slot(str, str)
    def _handle_pandoc_result(self, result: str, context: str) -> None:
        """Handle Pandoc conversion result (delegates to PandocResultHandler)."""
        self.pandoc_result_handler.handle_pandoc_result(result, context)

    @Slot(str, str)
    def _handle_pandoc_error_result(self, error: str, context: str) -> None:
        """Handle Pandoc conversion error (delegates to PandocResultHandler)."""
        self.pandoc_result_handler.handle_pandoc_error_result(error, context)

    # ========================================================================
    # Find & Search Handlers (v1.8.0) - Delegated to SearchHandler (MA)
    # ========================================================================

    def _handle_find_next(self) -> None:
        """Navigate to next search match (delegates to SearchHandler)."""
        self.search_handler.handle_find_next()

    def _handle_find_previous(self) -> None:
        """Navigate to previous search match (delegates to SearchHandler)."""
        self.search_handler.handle_find_previous()

    def _clear_search_highlighting(self) -> None:
        """Clear all search highlighting (delegates to SearchHandler)."""
        self.search_handler.clear_search_highlighting()

    def _apply_combined_selections(self) -> None:
        """Combine search and spell check selections (delegates to SearchHandler)."""
        self.search_handler.apply_combined_selections()

    def _update_ui_state(self) -> None:
        """Update UI element states (delegates to UIStateManager)."""
        self.ui_state_manager.update_ui_state()

    def _update_ai_status_bar(self) -> None:
        """Update AI model name in status bar (delegates to UIStateManager)."""
        self.ui_state_manager.update_ai_status_bar()

    def _update_ai_backend_checkmarks(self) -> None:
        """Update checkmarks on AI backend menu items based on active backend."""
        is_ollama = self._settings.ai_backend == "ollama"
        is_claude = self._settings.ai_backend == "claude"

        # Update menu text with checkmark for active backend
        ollama_text = "✓ &Ollama Status" if is_ollama else "&Ollama Status"
        claude_text = "✓ &Anthropic Status" if is_claude else "&Anthropic Status"

        self.action_manager.ollama_status_act.setText(ollama_text)
        self.action_manager.anthropic_status_act.setText(claude_text)

        logger.debug(f"Updated AI backend checkmarks: ollama={is_ollama}, claude={is_claude}")

    def _check_pandoc_availability(self, context: str) -> bool:
        """Check if Pandoc is available (delegates to UIStateManager)."""
        return self.ui_state_manager.check_pandoc_availability(context)

    # ========================================================================
    # Dialog Methods (Phase 6b: Delegated to DialogManager)
    # ========================================================================

    def _show_ollama_model_browser(self) -> None:
        """Show Ollama model browser to download new models."""
        from asciidoc_artisan.ui.ollama_model_browser import OllamaModelBrowser

        browser = OllamaModelBrowser(self)
        browser.model_downloaded.connect(self._on_ollama_model_downloaded)
        browser.exec()

    def _on_ollama_model_downloaded(self, model_name: str) -> None:
        """Handle when a model is downloaded from the browser."""
        # Reload chat model manager to pick up new model
        if hasattr(self, "chat_manager") and self.chat_manager:
            self.chat_manager._reload_models()
        self.show_status_message(f"Downloaded Ollama model: {model_name}")

    def show_autocomplete_settings(self) -> None:
        """Show auto-complete settings dialog (delegates to SettingsDialogHelper)."""
        self.settings_dialog_helper.show_autocomplete_settings()

    def show_syntax_check_settings(self) -> None:
        """Show syntax checking settings dialog (delegates to SettingsDialogHelper)."""
        self.settings_dialog_helper.show_syntax_check_settings()

    def _show_message(self, level: str, title: str, text: str) -> None:
        """Show message box (delegates to DialogManager)."""
        self.dialog_manager.show_message(level, title, text)

    def _prompt_save_before_action(self, action: str) -> bool:
        """Prompt to save before action (delegates to DialogManager)."""
        return self.dialog_manager.prompt_save_before_action(action)

    def _refresh_from_settings(self) -> None:
        """Refresh application state from updated settings."""
        # Reload settings from the updated settings object
        settings = self._settings

        # Apply theme (theme_manager checks settings.dark_mode internally)
        self.theme_manager.apply_theme()

        # Update font size
        from PySide6.QtGui import QFont

        from asciidoc_artisan.core import EDITOR_FONT_FAMILY

        font = QFont(EDITOR_FONT_FAMILY, settings.font_size)
        self.editor.setFont(font)

        # Update AI status bar
        self._update_ai_status_bar()

        # Update AI backend checkmarks in Help menu
        self._update_ai_backend_checkmarks()

        # Update PandocWorker with new Ollama configuration
        if hasattr(self, "pandoc_worker"):
            self.pandoc_worker.set_ollama_config(settings.ollama_enabled, settings.ollama_model)

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

    def closeEvent(self, event: Any) -> None:  # noqa: N802
        """Handle window close event (delegates to EditorState)."""
        # Skip save prompts in test environment to prevent blocking
        if os.environ.get("PYTEST_CURRENT_TEST"):
            # Still need to shutdown workers in tests to prevent hanging
            logger.info("Test mode: Shutting down worker threads...")
            if hasattr(self, "worker_manager") and self.worker_manager:
                self.worker_manager.shutdown()
            event.accept()
            return

        self.editor_state.handle_close_event(event)
