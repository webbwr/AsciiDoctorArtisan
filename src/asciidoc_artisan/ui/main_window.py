"""
Main window coordinator for AsciiDoc Artisan.

MA Principle: Core coordinator reduced to <400 lines via mixin pattern.
Initialization, signals, and slots extracted to separate modules.

Architecture:
- MainWindowSignalsMixin: Signal definitions
- MainWindowInitMixin: _init_* and _setup_* methods
- MainWindowSlotsMixin: @Slot handlers and events
- AsciiDocEditor: Core coordinator (this class)
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import QMainWindow

from asciidoc_artisan.core.template_engine import TemplateEngine
from asciidoc_artisan.ui.main_window_init import MainWindowInitMixin
from asciidoc_artisan.ui.main_window_signals import MainWindowSignalsMixin
from asciidoc_artisan.ui.main_window_slots import MainWindowSlotsMixin
from asciidoc_artisan.ui.template_browser import TemplateBrowser

logger = logging.getLogger(__name__)


class AsciiDocEditor(
    MainWindowSignalsMixin,
    MainWindowInitMixin,
    MainWindowSlotsMixin,
    QMainWindow,
):
    """
    Main application window coordinating all UI managers.

    Uses Manager Pattern - delegates to specialized handlers:
    - FileHandler: Save/Open operations
    - GitHandler: Git operations
    - ThemeManager: Dark/Light mode
    - StatusManager: Status bar updates
    - ActionManager: Menu actions
    - WorkerManager: Background threads
    """

    def __init__(self) -> None:
        """Initialize the main window."""
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

    # ========================================================================
    # Delegation Methods - Thin wrappers to handlers
    # ========================================================================

    def _apply_theme(self) -> None:
        """Apply theme (delegates to ThemeManager)."""
        self.theme_manager.apply_theme()

    def new_file(self) -> None:
        """Create a new file (delegates to FileHandler)."""
        self.file_handler.new_file()

    def new_from_template(self) -> None:
        """Create a new document from a template."""
        browser = TemplateBrowser(self.template_manager, self)
        if browser.exec():
            template = browser.selected_template
            variables = browser.variable_values
            if template:
                engine = TemplateEngine()
                content = engine.instantiate(template, variables)
                self.file_handler.new_file()
                self.editor.setPlainText(content)
                self.has_unsaved_changes = True
                logger.info(f"Created new document from template: {template.name}")

    def _load_content_into_editor(self, content: str, file_path: Path) -> None:
        """Load content into editor (delegates to DialogManager)."""
        self.dialog_manager.load_content_into_editor(content, file_path)

    def save_file_as_format(self, format_type: str) -> bool:
        """Save/export file in specified format (delegates to ExportManager)."""
        return self.export_manager.save_file_as_format(format_type)

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
        """Toggle maximize/restore for a specific pane."""
        self.editor_state.toggle_pane_maximize(pane)

    def _toggle_maximize_window(self) -> None:
        """Toggle maximize/restore application window."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def convert_and_paste_from_clipboard(self) -> None:
        """Convert clipboard content to AsciiDoc."""
        self.export_manager.convert_and_paste_from_clipboard()

    def toggle_telemetry(self) -> None:
        """Toggle telemetry on/off."""
        self.telemetry_manager.toggle()
        self.telemetry_collector = self.telemetry_manager.collector

    # ========================================================================
    # Git Operations
    # ========================================================================

    def _select_git_repository(self) -> None:
        """Select Git repository."""
        self.git_handler.select_repository()

    def _trigger_git_commit(self) -> None:
        """Trigger Git commit."""
        self.git_handler.commit_changes()

    def _trigger_git_pull(self) -> None:
        """Trigger Git pull."""
        self.git_handler.pull_changes()

    def _trigger_git_push(self) -> None:
        """Trigger Git push."""
        self.git_handler.push_changes()

    def _show_git_status(self) -> None:
        """Show Git status dialog with detailed file-level information."""
        if not self._ensure_git_ready():
            return

        if not hasattr(self, "_git_status_dialog"):
            from asciidoc_artisan.ui.git_status_dialog import GitStatusDialog

            self._git_status_dialog = GitStatusDialog(self)
            self._git_status_dialog.refresh_requested.connect(self._refresh_git_status_dialog)

        repo_path = self.git_handler.get_repository_path()
        if repo_path and hasattr(self, "request_detailed_git_status"):
            self.request_detailed_git_status.emit(repo_path)

        self._git_status_dialog.show()
        self._git_status_dialog.raise_()
        self._git_status_dialog.activateWindow()

    def _refresh_git_status_dialog(self) -> None:
        """Refresh Git status dialog data."""
        repo_path = self.git_handler.get_repository_path()
        if repo_path and hasattr(self, "request_detailed_git_status"):
            self.request_detailed_git_status.emit(repo_path)

    def _show_quick_commit(self) -> None:
        """Show quick commit widget for inline Git commits."""
        if not self._ensure_git_ready():
            return
        self.quick_commit_widget.show_and_focus()
        logger.debug("Quick commit widget shown")

    def _ensure_git_ready(self) -> bool:
        """Ensure Git is ready."""
        return self.git_handler._ensure_ready()

    # ========================================================================
    # GitHub Operations
    # ========================================================================

    def _trigger_github_create_pr(self) -> None:
        """Create GitHub pull request."""
        if hasattr(self, "github_handler"):
            self.github_handler.create_pull_request()

    def _trigger_github_list_prs(self) -> None:
        """List GitHub pull requests."""
        if hasattr(self, "github_handler"):
            self.github_handler.list_pull_requests()

    def _trigger_github_create_issue(self) -> None:
        """Create GitHub issue."""
        if hasattr(self, "github_handler"):
            self.github_handler.create_issue()

    def _trigger_github_list_issues(self) -> None:
        """List GitHub issues."""
        if hasattr(self, "github_handler"):
            self.github_handler.list_issues()

    def _trigger_github_repo_info(self) -> None:
        """Show GitHub repository info."""
        if hasattr(self, "github_handler"):
            self.github_handler.get_repo_info()

    # ========================================================================
    # Scroll Management
    # ========================================================================

    def _setup_synchronized_scrolling(self) -> None:
        """Set up synchronized scrolling."""
        self.scroll_manager.setup_synchronized_scrolling()

    def _sync_editor_to_preview(self, value: int) -> None:
        """Synchronize preview scroll."""
        self.scroll_manager.sync_editor_to_preview(value)

    def _sync_preview_to_editor(self, value: int) -> None:
        """Synchronize editor scroll."""
        self.scroll_manager.sync_preview_to_editor(value)

    # ========================================================================
    # Search Operations
    # ========================================================================

    def _handle_find_next(self) -> None:
        """Navigate to next search match."""
        self.search_handler.handle_find_next()

    def _handle_find_previous(self) -> None:
        """Navigate to previous search match."""
        self.search_handler.handle_find_previous()

    def _clear_search_highlighting(self) -> None:
        """Clear all search highlighting."""
        self.search_handler.clear_search_highlighting()

    def _apply_combined_selections(self) -> None:
        """Combine search and spell check selections."""
        self.search_handler.apply_combined_selections()

    # ========================================================================
    # UI State Management
    # ========================================================================

    def _update_ui_state(self) -> None:
        """Update UI element states."""
        self.action_manager.update_ui_state()

    def _update_ai_status_bar(self) -> None:
        """Update AI model name in status bar."""
        self.action_manager.update_ai_status_bar()

    def _update_ai_backend_checkmarks(self) -> None:
        """Update checkmarks on AI backend menu items."""
        is_ollama = self._settings.ai_backend == "ollama"
        is_claude = self._settings.ai_backend == "claude"

        ollama_text = "✓ &Ollama Status" if is_ollama else "&Ollama Status"
        claude_text = "✓ &Anthropic Status" if is_claude else "&Anthropic Status"

        self.action_manager.ollama_status_act.setText(ollama_text)
        self.action_manager.anthropic_status_act.setText(claude_text)

        logger.debug(f"Updated AI backend checkmarks: ollama={is_ollama}, claude={is_claude}")

    def _check_pandoc_availability(self, context: str) -> bool:
        """Check if Pandoc is available."""
        return self.action_manager.check_pandoc_availability(context)

    # ========================================================================
    # Dialog Methods
    # ========================================================================

    def refresh_ollama_models(self, message: str = "") -> None:
        """Refresh Ollama models in chat manager after download/delete."""
        if hasattr(self, "chat_manager") and self.chat_manager:
            self.chat_manager._load_available_models()
        if message:
            self.show_status_message(message)

    def show_autocomplete_settings(self) -> None:
        """Show auto-complete settings dialog."""
        self.settings_dialog_helper.show_autocomplete_settings()

    def show_syntax_check_settings(self) -> None:
        """Show syntax checking settings dialog."""
        self.settings_dialog_helper.show_syntax_check_settings()

    def _show_message(self, level: str, title: str, text: str) -> None:
        """Show message box."""
        self.dialog_manager.show_message(level, title, text)

    def _prompt_save_before_action(self, action: str) -> bool:
        """Prompt to save before action."""
        return self.dialog_manager.prompt_save_before_action(action)

    def show_status_message(self, message: str, timeout: int = 3000) -> None:
        """Show status bar message."""
        if hasattr(self, "status_bar"):
            self.status_bar.showMessage(message, timeout)
