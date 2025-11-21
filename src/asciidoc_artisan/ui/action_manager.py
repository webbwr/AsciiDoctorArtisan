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

MA Compliance: Reduced from 971→457 lines via 3 class extractions (53% reduction).
"""

# === STANDARD LIBRARY IMPORTS ===
import logging  # For recording what the program does (debug messages)
from typing import (  # For type hints without circular imports
    TYPE_CHECKING,
    Any,
)

# === QT FRAMEWORK IMPORTS ===
from PySide6.QtCore import Qt  # Qt constants and enums (Key codes, etc.)
from PySide6.QtGui import (
    QAction,  # Menu item class (represents one menu action like "New" or "Save")
    QKeySequence,  # Keyboard shortcut class (like Ctrl+S, Ctrl+C)
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
    Action Manager - Central Controller for Menu Actions and Keyboard Shortcuts.

    FOR BEGINNERS - WHAT IS THIS CLASS?:
    This class is like the "button factory" for the application. It creates
    all the menu items you see (New, Save, Copy, etc.) and connects them to
    the code that runs when you click them.

    WHAT IT MANAGES:
    - 50+ QAction objects (one for each menu item)
    - Keyboard shortcuts for each action
    - Menu bar structure (which menus exist, what's in each menu)
    - Action state (which actions are enabled/disabled, checked/unchecked)

    WHY IT EXISTS:
    Before this class, main_window.py had 250+ lines of repetitive code
    creating actions. This class centralizes all that code in one place.

    KEY METHOD - _create_action():
    The DRY pattern helper that reduces 5-10 lines per action to just 1 line.
    This is the most important method in this class!

    RESPONSIBILITIES:
    1. Create all QAction objects (create_actions method)
    2. Build the menu bar structure (create_menus method)
    3. Provide access to actions (via instance variables like self.new_act)

    USAGE:
    Called by main_window.py during initialization:
        action_mgr = ActionManager(self)
        action_mgr.create_actions()   # Creates all 50+ actions
        action_mgr.create_menus()     # Builds File, Edit, View, etc. menus
    """

    def __init__(self, main_window: "AsciiDocEditor"):
        """
        Initialize Action Manager - Set Up References to Main Window.

        MA principle: Reduced from 77→6 lines by extracting reference setup and type declarations (92% reduction).

        WHY THIS INIT EXISTS:
        Actions need to call methods on the main window (like new_file(),
        save_file(), etc.). We store a reference to the main window so
        actions can trigger those methods.

        WHAT THIS DOES:
        1. Stores reference to main window
        2. Stores reference to text editor widget
        3. Stores reference to settings
        4. Declares all 50+ action variables (self.new_act, self.save_act, etc.)

        WHY DECLARE VARIABLES HERE?:
        Python allows adding attributes anywhere, but declaring them in __init__
        helps:
        - Type checkers (mypy) understand what attributes exist
        - IDEs provide autocomplete (type "self." and see all actions)
        - Developers see the full list of actions in one place

        PARAMETERS:
            main_window: The AsciiDocEditor instance (main application window)

        CREATES:
            self.window: Reference to main window (for calling methods)
            self.editor: Reference to text editor widget
            self._settings: Reference to application settings
            self._sync_scrolling: Reference to scroll sync state
            self.new_act, self.save_act, etc.: 50+ QAction variables (created later)
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
        Create All QAction Objects - Build All 50+ Menu Actions.

        WHY THIS METHOD EXISTS:
        This method creates every single menu action in the application using
        the _create_action helper. It's called once during application startup.

        WHAT IT DOES:
        Creates 50+ QAction objects organized by menu:
        - File menu: New, Open, Save, Save As, Export, Exit (10 actions)
        - Edit menu: Undo, Redo, Cut, Copy, Paste, Preferences (7 actions)
        - View menu: Zoom, Dark Mode, Sync Scrolling, Maximize (6 actions)
        - Git menu: Set Repo, Commit, Pull, Push (4 actions)
        - GitHub menu: Create/List PR/Issue, Repo Info (5 actions)
        - Tools menu: Pandoc, Ollama AI (4 actions)
        - Help menu: About (1 action)

        TOTAL: 37 actions (some have sub-actions)

        HOW IT WORKS:
        Each action is created with _create_action helper:
        1. Text (&New) - what shows in menu, & marks keyboard mnemonic
        2. Status tip (Create a new file) - help text in status bar
        3. Handler (self.window.new_file) - function to call when triggered
        4. Shortcut (Ctrl+N) - optional keyboard shortcut

        FOR BEGINNERS - ORDER MATTERS:
        Actions must be created BEFORE create_menus() is called. You can't
        add an action to a menu if the action doesn't exist yet!

        PARAMETERS:
            None

        RETURNS:
            None (stores all actions as instance variables like self.new_act)

        SIDE EFFECTS:
            Sets 50+ instance variables (self.new_act, self.save_act, etc.)

        MA principle: Reduced from 416 lines to ~15 lines by splitting into
        8 focused helper methods (one per menu category).
        """
        logger.debug("Creating actions...")
        self._create_file_actions()
        self._create_edit_actions()
        self._create_find_actions()
        self._create_view_actions()
        self._create_git_actions()
        self._create_github_actions()
        self._create_tools_actions()
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
        Build Menu Structure - Organize Actions into File, Edit, View, etc. Menus.

        WHY THIS METHOD EXISTS:
        Actions exist, but users need a way to access them. This method creates
        the menu bar at the top of the window and organizes actions into menus.

        WHAT IT DOES:
        1. Gets the menu bar from the main window
        2. Creates each menu (File, Edit, View, Git, Tools, Help)
        3. Adds actions to each menu in the correct order
        4. Adds separators between action groups (visual dividers)
        5. Creates submenus (like Git → GitHub with 5 sub-actions)

        FOR BEGINNERS - MENU STRUCTURE:
        Think of a restaurant menu with sections:
        - Appetizers (File menu: New, Open, Save)
        - Main Courses (Edit menu: Undo, Redo, Cut, Copy, Paste)
        - Desserts (View menu: Zoom, Dark Mode)
        - Drinks (Git, Tools, Help menus)

        Each section can have dividers (separators) to group similar items.

        MENU ORGANIZATION:
        - File: New, Open, Save, Save As (with 5 export formats), Exit
        - Edit: Undo, Redo, Cut, Copy, Paste, Convert & Paste, Find & Replace
        - View: Zoom In/Out, Dark Mode, Sync Scrolling, Maximize Editor/Preview
        - Git: Set Repo, Commit, Pull, Push, GitHub submenu (5 actions)
        - Tools: Validation, Theme/Font/Spell, Pandoc/AI Settings, Preferences, Settings
        - Help: About

        SEPARATORS:
        Separators (horizontal lines) visually group related actions:
        - File menu: [New/Open/Save/SaveAs] | [Exit]
        - Edit menu: [Undo/Redo] | [Cut/Copy/Paste] | [Convert&Paste] | [Find/Replace]

        PARAMETERS:
            None

        RETURNS:
            None (modifies the main window's menu bar)

        SIDE EFFECTS:
            Creates and populates the application's menu bar

        MA principle: Reduced from 159 lines to ~12 lines by splitting into
        6 menu-specific helper methods.
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
