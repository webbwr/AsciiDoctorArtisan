"""
Main window initialization methods.

MA Principle: Extracted from main_window.py to reduce file size.
Contains all _init_* and _setup_* methods for cleaner organization.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QRect, Qt, QTimer

from asciidoc_artisan.core import AUTO_SAVE_INTERVAL_MS, PREVIEW_UPDATE_INTERVAL_MS

if TYPE_CHECKING:
    from asciidoc_artisan.core.settings import Settings
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

logger = logging.getLogger(__name__)

# Check for AsciiDoc3 availability
try:
    from asciidoc3 import asciidoc3
    from asciidoc3.asciidoc3api import AsciiDoc3API

    ASCIIDOC3_AVAILABLE = True
except ImportError:
    asciidoc3 = None
    AsciiDoc3API = None
    ASCIIDOC3_AVAILABLE = False


class MainWindowInitMixin:
    """Mixin providing initialization methods for AsciiDocEditor."""

    # Type hints for attributes set by main class
    _settings: Settings
    _settings_path: Path
    _settings_manager: Any
    _current_file_path: Path | None
    _initial_geometry: QRect | None
    _start_maximized: bool
    _is_opening_file: bool
    _is_processing_git: bool
    _last_git_operation: str
    _pending_commit_message: str | None
    _unsaved_changes: bool
    _sync_scrolling: bool
    _is_syncing_scroll: bool
    _temp_dir: tempfile.TemporaryDirectory[str]
    _asciidoc_api: Any
    _preview_timer: QTimer

    def _init_settings(self: AsciiDocEditor) -> None:
        """Initialize settings manager and load configuration."""
        from asciidoc_artisan.ui.settings_manager import SettingsManager

        self._settings_manager = SettingsManager()
        self._settings_path = self._settings_manager.get_settings_path()
        self._settings = self._settings_manager.load_settings()

    def _init_state_variables(self: AsciiDocEditor) -> None:
        """Initialize state tracking variables."""
        from PySide6.QtWidgets import QProgressDialog

        self._current_file_path = None
        self._initial_geometry = None
        self._start_maximized = self._settings.maximized
        self._is_opening_file = False
        self._is_processing_git = False
        self._last_git_operation = ""
        self._pending_commit_message = None
        self._unsaved_changes = False
        self._sync_scrolling = True
        self._is_syncing_scroll = False
        self._progress_dialog: QProgressDialog | None = None
        self._temp_dir = tempfile.TemporaryDirectory()

        if not self._start_maximized:
            self._initial_geometry = self._settings_manager.parse_window_geometry(self._settings)

        if self._settings.last_file and Path(self._settings.last_file).is_file():
            self._current_file_path = Path(self._settings.last_file)

    def _init_core_managers(self: AsciiDocEditor) -> None:
        """Initialize core managers (status, theme)."""
        from asciidoc_artisan.ui.status_manager import StatusManager
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        self.status_manager = StatusManager(self)
        self.theme_manager = ThemeManager(self)

    def _init_ui_managers(self: AsciiDocEditor) -> None:
        """Initialize UI state and coordination managers."""
        from asciidoc_artisan.ui.dialog_manager import DialogManager
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        self.dialog_manager = DialogManager(self)
        self.scroll_manager = ScrollManager(self)

    def _init_file_managers(self: AsciiDocEditor) -> None:
        """Initialize file and operations managers."""
        from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
        from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

        self.file_operations_manager = FileOperationsManager(self)
        self.pandoc_result_handler = PandocResultHandler(self)

    def _init_resource_monitoring(self: AsciiDocEditor) -> None:
        """Initialize resource monitoring and large file handling."""
        from asciidoc_artisan.core import ResourceMonitor
        from asciidoc_artisan.core.large_file_handler import LargeFileHandler

        self.resource_monitor = ResourceMonitor()
        logger.info(f"ResourceMonitor initialized (psutil available: {self.resource_monitor.is_available()})")

        self.large_file_handler = LargeFileHandler()
        self.large_file_handler.progress_update.connect(self.dialog_manager.on_file_load_progress)

    def _init_worker_management(self: AsciiDocEditor) -> None:
        """Initialize worker thread management."""
        from asciidoc_artisan.ui.worker_manager import WorkerManager

        self.worker_manager = WorkerManager(self)

    def _init_asciidoc_and_preview(self: AsciiDocEditor) -> None:
        """Initialize AsciiDoc API and preview timer."""
        self._asciidoc_api = self._initialize_asciidoc()
        self._preview_timer = self._setup_preview_timer()

    def _configure_window(self: AsciiDocEditor) -> None:
        """Configure window title and flags."""
        import platform

        from asciidoc_artisan.core import APP_NAME

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

    def _setup_ui_components(self: AsciiDocEditor) -> None:
        """Setup UI components via UISetupManager."""
        from asciidoc_artisan.ui.ui_setup_manager import UISetupManager

        self.ui_setup = UISetupManager(self)
        self.ui_setup.setup_ui()

    def _setup_file_operations(self: AsciiDocEditor) -> None:
        """Setup file operations and auto-save."""
        from asciidoc_artisan.ui.file_handler import FileHandler

        self.file_handler = FileHandler(self.editor, self, self._settings_manager, self.status_manager)
        self.file_handler.start_auto_save(AUTO_SAVE_INTERVAL_MS)

    def _setup_preview_system(self: AsciiDocEditor) -> None:
        """Setup preview handler and start updates."""
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_handler

        self.preview_handler = create_preview_handler(self.editor, self.preview, self)
        self.preview_handler.start_preview_updates()

    def _setup_git_integration(self: AsciiDocEditor) -> None:
        """Setup Git and GitHub integration."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        from asciidoc_artisan.ui.github_handler import GitHubHandler

        self.git_handler = GitHandler(self, self._settings_manager, self.status_manager)
        self.git_handler.initialize()
        self.github_handler = GitHubHandler(self, self._settings_manager, self.status_manager, self.git_handler)

    def _setup_editor_features(self: AsciiDocEditor) -> None:
        """Setup editor features (spell check, autocomplete, syntax, templates)."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        self.spell_check_manager = SpellCheckManager(self)
        self.editor.spell_check_manager = self.spell_check_manager
        logger.info("SpellCheckManager initialized")

        self._setup_autocomplete()
        self._setup_syntax_checker()
        self._setup_template_system()

    def _setup_actions_and_export(self: AsciiDocEditor) -> None:
        """Setup actions, menus, and export system."""
        from asciidoc_artisan.ui.action_manager import ActionManager
        from asciidoc_artisan.ui.export_manager import ExportManager

        self.action_manager = ActionManager(self)
        self.action_manager.create_actions()
        self.action_manager.create_menus()
        self.spell_check_manager._update_menu_text()
        self.export_manager = ExportManager(self)

    def _setup_chat_and_search(self: AsciiDocEditor) -> None:
        """Setup chat, find, and quick commit systems."""
        from asciidoc_artisan.ui.chat_manager import ChatManager
        from asciidoc_artisan.ui.chat_worker_router import ChatWorkerRouter
        from asciidoc_artisan.ui.editor_state import EditorState

        self.editor_state = EditorState(self)
        self.chat_manager = ChatManager(self.chat_bar, self.chat_panel, self._settings, parent=self)
        self.chat_worker_router = ChatWorkerRouter(self)
        self._setup_find_system()
        self._setup_quick_commit()

    def _finalize_initialization(self: AsciiDocEditor) -> None:
        """Finalize initialization (telemetry, restore settings, apply theme, UX)."""
        from asciidoc_artisan.ui.telemetry_manager import TelemetryManager
        from asciidoc_artisan.ui.ux_manager import create_ux_manager

        self.telemetry_manager = TelemetryManager(self)
        self.telemetry_collector = self.telemetry_manager.initialize(getattr(self, "_app_start_time", None))
        self.telemetry_manager._update_menu_text()

        self._settings_manager.restore_ui_settings(self, self.splitter, self._settings)
        self.theme_manager.apply_theme()
        self._setup_workers_and_threads()
        self._update_ui_state()
        self._update_ai_backend_checkmarks()

        # Initialize S-tier UX features
        self.ux_manager = create_ux_manager(self)
        logger.info("S-tier UX features initialized")

    def _initialize_asciidoc(self: AsciiDocEditor) -> Any:
        """Initialize AsciiDoc3 API."""
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

    def _setup_preview_timer(self: AsciiDocEditor) -> QTimer:
        """Setup preview update timer."""
        timer = QTimer(self)
        timer.setInterval(PREVIEW_UPDATE_INTERVAL_MS)
        timer.setSingleShot(True)
        timer.timeout.connect(self.update_preview)
        return timer

    def _setup_find_system(self: AsciiDocEditor) -> None:
        """Initialize Find & Replace system."""
        from asciidoc_artisan.core.search_engine import SearchEngine
        from asciidoc_artisan.ui.search_handler import SearchContext, SearchHandler

        self.search_engine = SearchEngine(self.editor.toPlainText())
        self.search_handler = SearchHandler(cast(SearchContext, self))

        self.find_bar.search_requested.connect(self.search_handler.handle_search_requested)
        self.find_bar.find_next_requested.connect(self.search_handler.handle_find_next)
        self.find_bar.find_previous_requested.connect(self.search_handler.handle_find_previous)
        self.find_bar.closed.connect(self.search_handler.handle_find_closed)
        self.find_bar.replace_requested.connect(self.search_handler.handle_replace)
        self.find_bar.replace_all_requested.connect(self.search_handler.handle_replace_all)
        self.editor.textChanged.connect(lambda: self.search_engine.set_text(self.editor.toPlainText()))

        logger.info("Find & Replace system initialized")

    def _setup_quick_commit(self: AsciiDocEditor) -> None:
        """Initialize Quick Commit system."""
        self.quick_commit_widget.commit_requested.connect(self._handle_quick_commit)
        self.quick_commit_widget.cancelled.connect(lambda: logger.debug("Quick commit cancelled"))
        logger.info("Quick Commit system initialized")

    def _setup_autocomplete(self: AsciiDocEditor) -> None:
        """Initialize Auto-Complete System."""
        from asciidoc_artisan.core.autocomplete_engine import AutoCompleteEngine
        from asciidoc_artisan.ui.autocomplete_manager import AutoCompleteManager

        engine = AutoCompleteEngine()
        self.autocomplete_manager = AutoCompleteManager(self.editor, engine)
        self.autocomplete_manager.enabled = self._settings.autocomplete_enabled
        self.autocomplete_manager.auto_delay = self._settings.autocomplete_delay
        logger.info("AutoCompleteManager initialized")

    def _setup_syntax_checker(self: AsciiDocEditor) -> None:
        """Initialize Syntax Checking System."""
        from asciidoc_artisan.core.syntax_checker import SyntaxChecker
        from asciidoc_artisan.ui.settings_dialog_helper import SettingsContext, SettingsDialogHelper
        from asciidoc_artisan.ui.syntax_checker_manager import SyntaxCheckerManager

        checker = SyntaxChecker()
        self.syntax_checker_manager = SyntaxCheckerManager(self.editor, checker)
        self.syntax_checker_manager.enabled = self._settings.syntax_check_realtime_enabled
        self.syntax_checker_manager.check_delay = self._settings.syntax_check_delay
        self.settings_dialog_helper = SettingsDialogHelper(self, cast(SettingsContext, self))
        logger.info("SyntaxCheckerManager initialized")

    def _setup_template_system(self: AsciiDocEditor) -> None:
        """Initialize Template System."""
        from asciidoc_artisan.core.template_engine import TemplateEngine
        from asciidoc_artisan.core.template_manager import TemplateManager

        engine = TemplateEngine()
        self.template_manager = TemplateManager(engine)
        templates = self.template_manager.get_all_templates()
        logger.info(f"TemplateManager initialized with {len(templates)} templates")

    def _setup_workers_and_threads(self: AsciiDocEditor) -> None:
        """Set up worker threads."""
        self.worker_manager.setup_workers_and_threads()

        self.request_load_file_content.connect(
            self.pandoc_result_handler._handle_file_load_request,
            Qt.ConnectionType.QueuedConnection,
        )

        self.chat_manager.message_sent_to_worker.connect(self.chat_worker_router.route_message)
        self.chat_manager.status_message.connect(self.status_manager.show_status)
        self.chat_manager.settings_changed.connect(lambda: self._settings_manager.save_settings(self._settings, self))

        self.ollama_chat_worker.chat_response_ready.connect(self.chat_manager.handle_response_ready)
        self.ollama_chat_worker.chat_response_chunk.connect(self.chat_manager.handle_response_chunk)
        self.ollama_chat_worker.chat_error.connect(self.chat_manager.handle_error)
        self.ollama_chat_worker.operation_cancelled.connect(self.chat_manager.handle_operation_cancelled)

        self.claude_worker.response_ready.connect(self.chat_worker_router.adapt_claude_response)
        self.claude_worker.error_occurred.connect(self.chat_manager.handle_error)

        self.chat_bar.cancel_requested.connect(self.ollama_chat_worker.cancel_operation)

        self.chat_manager.set_document_content_provider(lambda: self.editor.toPlainText())
        self.chat_manager.initialize()
        self.github_handler.initialize()
