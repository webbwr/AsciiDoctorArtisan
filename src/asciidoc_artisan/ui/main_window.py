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
import platform
import tempfile
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import (
    QRect,
    Qt,
    QTimer,
    Signal,
    Slot,
)

# QWebEngine with GPU acceleration - auto-detected by preview_handler_gpu
try:
    from PySide6.QtWebEngineCore import QWebEngineSettings
    from PySide6.QtWebEngineWidgets import QWebEngineView

    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
from PySide6.QtWidgets import (
    QMainWindow,
    QProgressDialog,
)

# Import from refactored modules
from asciidoc_artisan.core import (
    APP_NAME,
    AUTO_SAVE_INTERVAL_MS,
    DEFAULT_FILENAME,
    PREVIEW_UPDATE_INTERVAL_MS,
    GitResult,
    ResourceMonitor,
    atomic_save_text,
)
from asciidoc_artisan.core.large_file_handler import LargeFileHandler
from asciidoc_artisan.ui.action_manager import ActionManager
from asciidoc_artisan.ui.dialog_manager import DialogManager
from asciidoc_artisan.ui.editor_state import EditorState
from asciidoc_artisan.ui.export_manager import ExportManager
from asciidoc_artisan.ui.file_handler import FileHandler
from asciidoc_artisan.ui.file_load_manager import FileLoadManager
from asciidoc_artisan.ui.file_operations_manager import FileOperationsManager
from asciidoc_artisan.ui.git_handler import GitHandler
from asciidoc_artisan.ui.github_handler import GitHubHandler

# Grammar functionality removed - no longer needed
# from asciidoc_artisan.ui.grammar_manager import GrammarManager
from asciidoc_artisan.ui.menu_manager import MenuManager
from asciidoc_artisan.ui.pandoc_result_handler import PandocResultHandler

# GPU-accelerated preview handler (auto-detects and uses GPU when available)
from asciidoc_artisan.ui.preview_handler_gpu import PreviewHandler
from asciidoc_artisan.ui.scroll_manager import ScrollManager
from asciidoc_artisan.ui.settings_manager import SettingsManager
from asciidoc_artisan.ui.status_manager import StatusManager
from asciidoc_artisan.ui.theme_manager import ThemeManager
from asciidoc_artisan.ui.ui_setup_manager import UISetupManager
from asciidoc_artisan.ui.ui_state_manager import UIStateManager
from asciidoc_artisan.ui.worker_manager import WorkerManager

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
# CONSTANTS (UI-specific color values - other constants imported from core)
# ============================================================================
# Note: UI color constants moved to ui_setup_manager.py (Phase 6b refactoring)


class AsciiDocEditor(QMainWindow):
    request_git_command = Signal(list, str)
    request_github_command = Signal(str, dict)  # operation_type, kwargs
    request_pandoc_conversion = Signal(object, str, str, str, object, bool)
    request_preview_render = Signal(str)

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
        # MenuManager initialization deferred until after UI setup
        self.menu_manager = MenuManager(self)

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
        self.preview_handler = PreviewHandler(self.editor, self.preview, self)
        self.preview_handler.start_preview_updates()

        # === Git Integration ===
        self.git_handler = GitHandler(self, self._settings_manager, self.status_manager)

        # === GitHub Integration ===
        self.github_handler = GitHubHandler(
            self, self._settings_manager, self.status_manager, self.git_handler
        )

        # === Grammar (Removed in v1.4.0) ===
        self.grammar_manager = None  # Placeholder for compatibility

        # === Actions & Menus ===
        self.action_manager = ActionManager(self)
        self.action_manager.create_actions()
        self.action_manager.create_menus()

        # === Export System ===
        self.export_manager = ExportManager(self)

        # === Editor State ===
        self.editor_state = EditorState(self)

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
    def _handle_github_result(self, result) -> None:
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

    def closeEvent(self, event: Any) -> None:
        """Handle window close event (delegates to EditorState)."""
        self.editor_state.handle_close_event(event)
