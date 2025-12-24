"""Action Manager - Coordinates menu actions and keyboard shortcuts via delegation."""

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QThread, QTimer
from PySide6.QtGui import QAction

from asciidoc_artisan.core.constants import is_pandoc_available
from asciidoc_artisan.ui.action_creators import ActionCreators
from asciidoc_artisan.ui.action_factory import ActionFactory
from asciidoc_artisan.ui.menu_builder import MenuBuilder

if TYPE_CHECKING:  # pragma: no cover
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class ActionManager:
    """Central controller coordinating 50+ menu actions and keyboard shortcuts."""

    def __init__(self, main_window: "AsciiDocEditor"):
        """Initialize with references to main window and helper instances."""
        self._setup_references(main_window)
        self._declare_all_actions()

    def _setup_references(self, main_window: "AsciiDocEditor") -> None:
        """
        Setup references to main window components.

        MA principle: Extracted helper (8 lines) - focused reference initialization.
        """
        self.window = main_window
        self.editor = main_window.editor
        self._settings = main_window._settings
        self._sync_scrolling = main_window._sync_scrolling
        self._factory = ActionFactory(main_window)
        self._creators = ActionCreators(self)
        self._menu_builder = MenuBuilder(self)

    def _declare_file_actions(self) -> None:
        """Declare File menu action type hints."""
        self.new_act: QAction
        self.new_from_template_act: QAction
        self.open_act: QAction
        self.save_act: QAction
        self.save_as_act: QAction
        self.save_as_adoc_act: QAction
        self.save_as_md_act: QAction
        self.save_as_docx_act: QAction
        self.save_as_html_act: QAction
        self.save_as_pdf_act: QAction
        self.exit_act: QAction

    def _declare_edit_actions(self) -> None:
        """Declare Edit menu action type hints."""
        self.undo_act: QAction
        self.redo_act: QAction
        self.cut_act: QAction
        self.copy_act: QAction
        self.paste_act: QAction
        self.convert_paste_act: QAction
        self.find_act: QAction
        self.replace_act: QAction
        self.find_next_act: QAction
        self.find_previous_act: QAction

    def _declare_view_actions(self) -> None:
        """Declare View menu action type hints."""
        self.zoom_in_act: QAction
        self.zoom_out_act: QAction
        self.dark_mode_act: QAction
        self.sync_scrolling_act: QAction
        self.maximize_window_act: QAction
        self.maximize_editor_act: QAction
        self.maximize_preview_act: QAction

    def _declare_git_actions(self) -> None:
        """Declare Git menu action type hints."""
        self.set_repo_act: QAction
        self.git_status_act: QAction
        self.git_commit_act: QAction
        self.git_pull_act: QAction
        self.git_push_act: QAction
        self.quick_commit_act: QAction

    def _declare_github_actions(self) -> None:
        """Declare GitHub submenu action type hints."""
        self.github_create_pr_act: QAction
        self.github_list_prs_act: QAction
        self.github_create_issue_act: QAction
        self.github_list_issues_act: QAction
        self.github_repo_info_act: QAction

    def _declare_tools_actions(self) -> None:
        """Declare Tools menu action type hints."""
        self.validate_install_act: QAction
        self.performance_dashboard_act: QAction
        self.autocomplete_settings_act: QAction
        self.syntax_check_settings_act: QAction
        self.toggle_chat_pane_act: QAction
        self.toggle_spell_check_act: QAction
        self.toggle_telemetry_act: QAction
        self.toggle_theme_act: QAction
        self.pandoc_status_act: QAction
        self.pandoc_formats_act: QAction
        self.ollama_status_act: QAction
        self.anthropic_status_act: QAction
        self.telemetry_status_act: QAction
        self.ollama_settings_act: QAction
        self.anthropic_settings_act: QAction
        self.font_settings_act: QAction
        self.app_settings_act: QAction

    def _declare_help_actions(self) -> None:
        """Declare Help menu action type hints."""
        self.welcome_guide_act: QAction
        self.about_act: QAction

    def _declare_all_actions(self) -> None:
        """
        Declare all action type hints for IDE/mypy support.

        MA principle: Reduced from 67→11 lines by extracting menu-specific helpers (84% reduction).

        These are declared (but not created yet - that happens in create_actions()).
        Declaring them here helps type checkers and IDEs.
        """
        self._declare_file_actions()
        self._declare_edit_actions()
        self._declare_view_actions()
        self._declare_git_actions()
        self._declare_github_actions()
        self._declare_tools_actions()
        self._declare_help_actions()

    # === HELPER METHODS ===
    # These methods reduce code duplication (DRY principle)

    def _create_action(
        self,
        text: str,
        status_tip: str,
        triggered: Any,
        shortcut: Any | None = None,
        checkable: bool = False,
        checked: bool = False,
    ) -> QAction:
        """Create QAction with common parameters (delegates to action_factory)."""
        return self._factory.create_action_internal(text, status_tip, triggered, shortcut, checkable, checked)

    def create_action(
        self,
        text: str,
        triggered: Any,
        shortcut: Any | None = None,
        icon: Any | None = None,
        tooltip: str | None = None,
        enabled: bool = True,
        checkable: bool = False,
        checked: bool = False,
    ) -> QAction:
        """Public API to create a single QAction (delegates to action_factory)."""
        return self._factory.create_action(text, triggered, shortcut, icon, tooltip, enabled, checkable, checked)

    def _create_file_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_file_actions()

    def _create_edit_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_edit_actions()

    def _create_find_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_find_actions()

    def _create_view_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_view_actions()

    def _create_git_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_git_actions()

    def _create_github_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_github_actions()

    def _create_tools_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_tools_actions()

    def _create_validation_settings_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_validation_settings_actions()

    def _create_service_status_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_service_status_actions()

    def _create_service_settings_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_service_settings_actions()

    def _create_ui_toggle_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_ui_toggle_actions()

    def _create_general_settings_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_general_settings_actions()

    def _create_help_actions(self) -> None:
        """Create actions (delegates to action_creators)."""
        self._creators.create_help_actions()

    def create_actions(self) -> None:
        """
        Create all 50+ QAction objects by delegating to ActionCreators.

        Called during startup to instantiate File, Edit, View, Git, GitHub,
        Tools, and Help menu actions with shortcuts and handlers.

        MA principle: Delegates to ActionCreators (338 lines extracted).
        """
        logger.debug("Creating actions...")
        self._create_file_actions()
        self._create_edit_actions()
        self._create_find_actions()
        self._create_view_actions()
        self._create_git_actions()
        self._create_github_actions()
        # Tools menu has multiple action creator methods
        self._create_tools_actions()
        self._create_validation_settings_actions()
        self._create_service_status_actions()
        self._create_service_settings_actions()
        self._create_ui_toggle_actions()
        self._create_general_settings_actions()
        self._create_help_actions()
        logger.debug("Actions created successfully")

    def _create_file_menu(self, menubar: Any) -> None:
        """Create menu (delegates to menu_builder)."""
        self._menu_builder.create_file_menu(menubar)

    def _create_edit_menu(self, menubar: Any) -> None:
        """Create menu (delegates to menu_builder)."""
        self._menu_builder.create_edit_menu(menubar)

    def _create_view_menu(self, menubar: Any) -> None:
        """Create menu (delegates to menu_builder)."""
        self._menu_builder.create_view_menu(menubar)

    def _create_git_menu(self, menubar: Any) -> None:
        """Create menu (delegates to menu_builder)."""
        self._menu_builder.create_git_menu(menubar)

    def _create_tools_menu(self, menubar: Any) -> None:
        """Create menu (delegates to menu_builder)."""
        self._menu_builder.create_tools_menu(menubar)

    def _create_help_menu(self, menubar: Any) -> None:
        """Create menu (delegates to menu_builder)."""
        self._menu_builder.create_help_menu(menubar)

    def create_menus(self) -> None:
        """
        Build application menu bar by delegating to MenuBuilder.

        Constructs File, Edit, View, Git, Tools, Help menus with separators
        and submenus (Export formats, GitHub actions, AI Settings).

        MA principle: Delegates to MenuBuilder (222 lines extracted).
        """
        logger.debug("Creating menus...")
        menubar = self.window.menuBar()
        self._create_file_menu(menubar)
        self._create_edit_menu(menubar)
        self._create_view_menu(menubar)
        self._create_git_menu(menubar)
        self._create_tools_menu(menubar)
        self._create_help_menu(menubar)
        logger.debug("Menus created successfully")

    # === UI STATE MANAGEMENT (merged from UIStateManager) ===

    def update_ui_state(self) -> None:
        """Update UI element states based on current processing state.

        Enables/disables actions based on:
        - Pandoc processing state
        - Git processing state
        - Git repository availability
        - Pandoc availability

        MA principle: Merged from UIStateManager for consolidated action management.
        """
        # Ensure this runs on the main thread (Qt requirement for UI updates)
        if QThread.currentThread() != self.window.thread():  # pragma: no cover
            QTimer.singleShot(0, self.update_ui_state)
            return

        # Save/Save As actions - disabled during Pandoc processing
        is_processing_pandoc = self.window.file_operations_manager._is_processing_pandoc
        self.save_act.setEnabled(not is_processing_pandoc)
        self.save_as_act.setEnabled(not is_processing_pandoc)

        # Export actions - disabled during Pandoc processing
        export_enabled = not is_processing_pandoc
        self.save_as_adoc_act.setEnabled(export_enabled)
        self.save_as_md_act.setEnabled(export_enabled and is_pandoc_available())
        self.save_as_docx_act.setEnabled(export_enabled and is_pandoc_available())
        self.save_as_html_act.setEnabled(export_enabled)
        self.save_as_pdf_act.setEnabled(export_enabled and is_pandoc_available())

        # Git actions - disabled during Git processing or if no repo
        git_ready = bool(self._settings.git_repo_path) and not self.window._is_processing_git
        self.git_commit_act.setEnabled(git_ready)
        self.git_pull_act.setEnabled(git_ready)
        self.git_push_act.setEnabled(git_ready)

        # Convert and paste - requires Pandoc and not processing
        self.convert_paste_act.setEnabled(is_pandoc_available() and not is_processing_pandoc)

        # Update AI status bar
        self.update_ai_status_bar()

    def update_ai_status_bar(self) -> None:
        """Update AI model name in status bar based on settings."""
        if self._settings.ollama_enabled and self._settings.ollama_model:
            # Show selected Ollama model
            self.window.status_manager.set_ai_model(self._settings.ollama_model)
        else:
            # Show Pandoc as fallback conversion method
            self.window.status_manager.set_ai_model("Pandoc")

    def check_pandoc_availability(self, context: str) -> bool:
        """Check if Pandoc is available for document conversion.

        Args:
            context: Context string describing the operation requiring Pandoc

        Returns:
            True if Pandoc is available, False otherwise (shows error dialog)
        """
        if not is_pandoc_available():
            self.window.status_manager.show_message(
                "critical",
                "Pandoc Not Available",
                f"{context} requires Pandoc and pypandoc.\n"
                "Please install them first:\n\n"
                "1. Install pandoc from https://pandoc.org\n"
                "2. Run: pip install pypandoc",
            )
            return False
        return True
