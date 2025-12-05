"""
Action Manager - Coordinates menu actions and keyboard shortcuts.

Manages application menu bar by delegating to specialized components:
- ActionFactory: QAction creation with DRY pattern (97% code reduction)
- ActionCreators: Instantiates 50+ actions organized by menu
- MenuBuilder: Constructs menu hierarchy (File, Edit, View, Git, Tools, Help)

Architecture:
- Thin coordination layer with delegation pattern
- Platform-aware shortcuts (Ctrl/Cmd auto-adaptation)
- Action state management (enabled/disabled, checked/unchecked)
- Type-safe action declarations for IDE autocomplete

Menu Structure:
- File: New, Open, Save, Export (5 formats), Exit
- Edit: Undo, Redo, Cut, Copy, Paste, Find/Replace
- View: Zoom, Dark mode, Sync scroll, Maximize
- Git: Repo, Commit, Pull, Push, GitHub submenu (5 actions)
- Tools: AI Settings, Validation, UI toggles
- Help: About, Service status checks

Keyboard Shortcuts:
- Standard: Ctrl+N/O/S (New/Open/Save), Ctrl+Z/Y (Undo/Redo), Ctrl+X/C/V
- Custom: F7 (Spell check), F11 (Dark mode), Ctrl+Shift+V (Convert paste)

Specifications:
- FR-048: Platform-appropriate keyboard shortcuts
- FR-053: Complete keyboard shortcut coverage

MA Compliance: Reduced from 971→335 lines via 3 extractions + docstring condensation (65.5% reduction).
"""

# === STANDARD LIBRARY IMPORTS ===
import logging  # For recording what the program does (debug messages)
from typing import (  # For type hints without circular imports
    TYPE_CHECKING,
    Any,
)

# === QT FRAMEWORK IMPORTS ===
from PySide6.QtGui import (
    QAction,  # Menu item class (represents one menu action like "New" or "Save")
)

# === LOCAL IMPORTS ===
from asciidoc_artisan.ui.action_creators import ActionCreators
from asciidoc_artisan.ui.action_factory import ActionFactory
from asciidoc_artisan.ui.menu_builder import MenuBuilder

# === TYPE CHECKING (Avoid Circular Imports) ===
# This is a trick to avoid importing main_window at runtime (would cause circular import)
# We only need the type for type hints, not the actual class
if TYPE_CHECKING:  # pragma: no cover
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

# === LOGGING SETUP ===
# Create a logger for this file (messages show as "action_manager: ...")
logger = logging.getLogger(__name__)


class ActionManager:
    """
    Central controller coordinating menu actions and keyboard shortcuts.

    Manages 50+ QAction objects by delegating to specialized components:
    - ActionFactory: Creates actions with DRY pattern
    - ActionCreators: Instantiates all menu actions
    - MenuBuilder: Constructs menu bar hierarchy

    Usage: action_mgr = ActionManager(window); action_mgr.create_actions(); action_mgr.create_menus()
    """

    def __init__(self, main_window: "AsciiDocEditor"):
        """
        Initialize ActionManager with references and helper instances.

        Sets up references to main window components, creates factory/creator/builder
        instances, and declares type hints for 50+ action variables.
        """
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
