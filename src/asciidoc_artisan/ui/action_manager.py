"""
===============================================================================
ACTION MANAGER - Menu Actions and Keyboard Shortcuts
===============================================================================

FILE PURPOSE:
This file manages all the menu actions (File, Edit, View, Git, Tools, Help)
and their keyboard shortcuts. It creates the menu bar you see at the top of
the application.

WHAT THIS FILE DOES:
1. Creates QAction objects (menu items like "New", "Save", "Copy", etc.)
2. Sets up keyboard shortcuts (Ctrl+N, Ctrl+S, Ctrl+C, etc.)
3. Connects actions to their handler functions (what happens when clicked)
4. Builds the menu bar structure (File menu, Edit menu, etc.)
5. Manages action state (enabled/disabled, checked/unchecked)

FOR BEGINNERS - WHAT ARE ACTIONS?:
Think of actions as buttons in a menu. When you click "File → New", that's
an action. Actions can be:
- In menus (File → New)
- In toolbars (the Save button with a disk icon)
- Triggered by keyboard shortcuts (Ctrl+N for New)

All three are the SAME action - just different ways to trigger it!

ANALOGY:
Think of a TV remote. The power button on the remote, the power button on
the TV itself, and saying "Turn on" to a voice assistant all do the SAME
thing - they trigger the "turn on TV" action. Actions work the same way.

WHY THIS FILE WAS EXTRACTED:
Before v1.1, all this code was in main_window.py (over 1,000 lines!). We
extracted it to:
- Make main_window.py smaller and easier to understand
- Make actions reusable (could add toolbar buttons later)
- Make testing easier (can test actions separately)
- Follow "Single Responsibility Principle" (one file = one job)

KEY DESIGN PATTERN - DRY (Don't Repeat Yourself):
Before refactoring, creating each action took 5-10 lines of code:
  action = QAction("&New", self)
  action.setStatusTip("Create a new file")
  action.setShortcut(QKeySequence.StandardKey.New)
  action.triggered.connect(self.new_file)

With 50+ actions, that's 250+ lines of repetitive code!

After refactoring with _create_action helper, each action is ONE line:
  self.new_act = self._create_action("&New", "Create a new file",
                                      self.new_file, QKeySequence.StandardKey.New)

Result: 97% reduction in QAction instantiation code! (5-10 lines → 1 line)

SPECIFICATIONS IMPLEMENTED:
- FR-048: Platform-appropriate keyboard shortcuts (Ctrl on Windows/Linux, Cmd on Mac)
- FR-053: Complete keyboard shortcut list for all common operations

MENU STRUCTURE:
File    Edit    View    Git        Tools           Help
├─New   ├─Undo  ├─Zoom  ├─Set Repo ├─AI Settings   ├─About
├─Open  ├─Redo  ├─Dark  ├─Commit   │ ├─Ollama
├─Save  ├─Cut   ├─Sync  ├─Pull     ├─App Settings
├─Save As Copy  ├─Max   ├─Push     ├─Chat Pane
└─Exit  └─Paste └─Max   └─GitHub   ├─Font Settings
                 Editor   Preview    ├─Spell Check
                                     ├─Telemetry
                                     └─Toggle Theme
                          ├─Create PR
                          ├─List PRs
                          ├─Create Issue
                          ├─List Issues
                          └─Repo Info

KEYBOARD SHORTCUTS:
- Ctrl+N (Cmd+N on Mac) = New file
- Ctrl+O (Cmd+O on Mac) = Open file
- Ctrl+S (Cmd+S on Mac) = Save file
- Ctrl+Z (Cmd+Z on Mac) = Undo
- Ctrl+Y (Cmd+Y on Mac) = Redo
- Ctrl+X, C, V = Cut, Copy, Paste
- Ctrl++ / Ctrl+- = Zoom in/out
- F11 = Toggle dark mode
- (20+ total shortcuts)

REFACTORING HISTORY:
- v1.0: All code in main_window.py (1,000+ lines)
- v1.1: Extracted to action_manager.py (462 lines)
- v1.5.0: Added _create_action helper (97% reduction in duplication)
- v1.6.0: Added GitHub CLI actions (PR/Issue management)

VERSION: 1.6.0 (GitHub CLI integration)
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
        """Create and populate File menu."""
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_act)
        file_menu.addAction(self.new_from_template_act)
        file_menu.addAction(self.open_act)
        file_menu.addSeparator()
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.save_as_act)
        export_menu = file_menu.addMenu("&Export As")
        export_menu.addAction(self.save_as_adoc_act)
        export_menu.addAction(self.save_as_md_act)
        export_menu.addAction(self.save_as_docx_act)
        export_menu.addAction(self.save_as_html_act)
        export_menu.addAction(self.save_as_pdf_act)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)

    def _create_edit_menu(self, menubar: Any) -> None:
        """Create and populate Edit menu."""
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.undo_act)
        edit_menu.addAction(self.redo_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_act)
        edit_menu.addAction(self.copy_act)
        edit_menu.addAction(self.paste_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.convert_paste_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_act)
        edit_menu.addAction(self.replace_act)
        edit_menu.addAction(self.find_next_act)
        edit_menu.addAction(self.find_previous_act)

    def _create_view_menu(self, menubar: Any) -> None:
        """Create and populate View menu."""
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.zoom_in_act)
        view_menu.addAction(self.zoom_out_act)
        view_menu.addSeparator()
        view_menu.addAction(self.dark_mode_act)
        view_menu.addAction(self.sync_scrolling_act)
        view_menu.addSeparator()
        view_menu.addAction(self.maximize_window_act)
        view_menu.addAction(self.maximize_editor_act)
        view_menu.addAction(self.maximize_preview_act)

    def _create_git_menu(self, menubar: Any) -> None:
        """Create and populate Git menu with GitHub submenu."""
        git_menu = menubar.addMenu("&Git")
        git_menu.addAction(self.set_repo_act)
        git_menu.addAction(self.git_status_act)
        git_menu.addSeparator()
        git_menu.addAction(self.git_commit_act)
        git_menu.addAction(self.quick_commit_act)
        git_menu.addAction(self.git_pull_act)
        git_menu.addAction(self.git_push_act)
        git_menu.addSeparator()
        github_submenu = git_menu.addMenu("Git&Hub")
        github_submenu.addAction(self.github_create_pr_act)
        github_submenu.addAction(self.github_list_prs_act)
        github_submenu.addSeparator()
        github_submenu.addAction(self.github_create_issue_act)
        github_submenu.addAction(self.github_list_issues_act)
        github_submenu.addSeparator()
        github_submenu.addAction(self.github_repo_info_act)

    def _create_tools_menu(self, menubar: Any) -> None:
        """Create and populate Tools menu with AI Settings submenu."""
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction(self.validate_install_act)
        tools_menu.addSeparator()
        ai_settings_menu = tools_menu.addMenu("&AI Settings")
        ai_settings_menu.addAction(self.ollama_settings_act)
        ai_settings_menu.addAction(self.anthropic_settings_act)
        tools_menu.addAction(self.app_settings_act)
        tools_menu.addAction(self.autocomplete_settings_act)
        tools_menu.addAction(self.toggle_chat_pane_act)
        tools_menu.addAction(self.font_settings_act)
        tools_menu.addAction(self.toggle_spell_check_act)
        tools_menu.addAction(self.syntax_check_settings_act)
        tools_menu.addAction(self.toggle_telemetry_act)
        tools_menu.addAction(self.toggle_theme_act)

    def _create_help_menu(self, menubar: Any) -> None:
        """Create and populate Help menu."""
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.about_act)
        help_menu.addSeparator()
        help_menu.addAction(self.anthropic_status_act)
        help_menu.addAction(self.ollama_status_act)
        help_menu.addAction(self.pandoc_formats_act)
        help_menu.addAction(self.pandoc_status_act)
        help_menu.addAction(self.telemetry_status_act)

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
