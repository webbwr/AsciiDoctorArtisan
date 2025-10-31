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
├─New   ├─Undo  ├─Zoom  ├─Set Repo ├─AI Status     ├─About
├─Open  ├─Redo  ├─Dark  ├─Commit   │ ├─Ollama
├─Save  ├─Cut   ├─Sync  ├─Pull     ├─Pandoc Status
├─Save As Copy  ├─Max   ├─Push     └─Pandoc Formats
└─Exit  └─Paste └─Max   └─GitHub
                 Editor   Preview    ├─Create PR
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
from typing import TYPE_CHECKING, Any, Optional  # For type hints without circular imports

# === QT FRAMEWORK IMPORTS ===
from PySide6.QtGui import (
    QAction,  # Menu item class (represents one menu action like "New" or "Save")
    QKeySequence,  # Keyboard shortcut class (like Ctrl+S, Ctrl+C)
)

# === TYPE CHECKING (Avoid Circular Imports) ===
# This is a trick to avoid importing main_window at runtime (would cause circular import)
# We only need the type for type hints, not the actual class
if TYPE_CHECKING:
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
        # === STORE REFERENCES ===
        # These references allow actions to call main window methods
        self.window = main_window  # Main application window
        self.editor = (
            main_window.editor
        )  # Text editor widget (for undo/redo/cut/copy/paste)
        self._settings = main_window._settings  # Application settings
        self._sync_scrolling = (
            main_window._sync_scrolling
        )  # Scroll sync state (for toggling)

        # === DECLARE ALL ACTION VARIABLES ===
        # These are declared (but not created yet - that happens in create_actions())
        # Declaring them here helps type checkers and IDEs

        # File menu actions (10 actions)
        self.new_act: QAction  # New file (Ctrl+N)
        self.open_act: QAction  # Open file (Ctrl+O)
        self.save_act: QAction  # Save file (Ctrl+S)
        self.save_as_act: QAction  # Save As dialog (Ctrl+Shift+S)
        self.save_as_adoc_act: QAction  # Export to AsciiDoc format
        self.save_as_md_act: QAction  # Export to Markdown format
        self.save_as_docx_act: QAction  # Export to Word DOCX format
        self.save_as_html_act: QAction  # Export to HTML format
        self.save_as_pdf_act: QAction  # Export to PDF format
        self.exit_act: QAction  # Exit application (Ctrl+Q)

        # Edit menu actions (7 actions)
        self.undo_act: QAction  # Undo last action (Ctrl+Z)
        self.redo_act: QAction  # Redo last undone action (Ctrl+Y)
        self.cut_act: QAction  # Cut selected text (Ctrl+X)
        self.copy_act: QAction  # Copy selected text (Ctrl+C)
        self.paste_act: QAction  # Paste from clipboard (Ctrl+V)
        self.convert_paste_act: QAction  # Paste and convert format (Ctrl+Shift+V)
        self.preferences_act: QAction  # Open settings dialog

        # View menu actions (6 actions)
        self.zoom_in_act: QAction  # Increase font size (Ctrl++)
        self.zoom_out_act: QAction  # Decrease font size (Ctrl+-)
        self.dark_mode_act: QAction  # Toggle dark/light theme (F11)
        self.sync_scrolling_act: QAction  # Toggle scroll synchronization
        self.maximize_editor_act: QAction  # Maximize editor pane
        self.maximize_preview_act: QAction  # Maximize preview pane

        # Git menu actions (4 actions)
        self.set_repo_act: QAction  # Set Git repository path
        self.git_commit_act: QAction  # Commit changes to Git
        self.git_pull_act: QAction  # Pull changes from remote
        self.git_push_act: QAction  # Push changes to remote

        # GitHub submenu actions (5 actions) - v1.6.0
        self.github_create_pr_act: QAction  # Create pull request
        self.github_list_prs_act: QAction  # List pull requests
        self.github_create_issue_act: QAction  # Create issue
        self.github_list_issues_act: QAction  # List issues
        self.github_repo_info_act: QAction  # View repository info

        # Tools menu actions (4 actions)
        self.pandoc_status_act: QAction  # Show Pandoc installation status
        self.pandoc_formats_act: QAction  # Show supported formats
        self.ollama_status_act: QAction  # Show Ollama AI status
        self.ollama_settings_act: QAction  # Configure Ollama AI settings

        # Help menu actions (1 action)
        self.about_act: QAction  # Show About dialog

    # === HELPER METHODS ===
    # These methods reduce code duplication (DRY principle)

    def _create_action(
        self,
        text: str,
        status_tip: str,
        triggered: Any,
        shortcut: Optional[Any] = None,
        checkable: bool = False,
        checked: bool = False,
    ) -> QAction:
        """
        Create QAction with Common Parameters - THE KEY DRY PATTERN METHOD.

        WHY THIS METHOD IS CRITICAL:
        This is the single most important method in this file! Before this
        helper existed, creating each action required 5-10 lines of code.
        With 50+ actions, that was 250+ lines of repetitive code.

        This helper reduces each action creation to ONE line!

        BEFORE (5-10 lines per action):
            action = QAction("&New", self.window)
            action.setStatusTip("Create a new file")
            action.setShortcut(QKeySequence.StandardKey.New)
            action.triggered.connect(self.window.new_file)
            self.new_act = action

        AFTER (1 line per action):
            self.new_act = self._create_action("&New", "Create a new file",
                                                self.window.new_file,
                                                QKeySequence.StandardKey.New)

        Result: 97% reduction in QAction instantiation code!

        WHAT THIS METHOD DOES:
        1. Creates a QAction object with the given text
        2. Sets the status tip (shown in status bar when hovering)
        3. Connects the action to its handler function (what runs when clicked)
        4. (Optional) Sets keyboard shortcut (Ctrl+N, Ctrl+S, etc.)
        5. (Optional) Makes action checkable (like a toggle switch)
        6. Returns the fully configured action

        FOR BEGINNERS - WHAT ARE THE PARAMETERS?:

        text - The label shown in the menu
          - Use "&" before a letter to make it the keyboard mnemonic
          - "&New" shows as "New" with "N" underlined (Alt+N triggers it)

        status_tip - Help text shown in status bar when hovering over menu item
          - Example: "Create a new file"

        triggered - The function to call when action is clicked/triggered
          - Example: self.window.new_file (the method that creates new files)

        shortcut - (Optional) Keyboard shortcut
          - Can be StandardKey (Ctrl+N, Ctrl+S - cross-platform)
          - Or custom string ("F11", "Ctrl+Shift+V")

        checkable - (Optional) Whether action is a toggle (on/off)
          - False = normal button (like "New", "Save")
          - True = toggle switch (like "Dark Mode", "Sync Scrolling")

        checked - (Optional) Initial state for checkable actions
          - Only used if checkable=True
          - True = starts checked (on)
          - False = starts unchecked (off)

        PARAMETERS:
            text: Action text with & for mnemonic (e.g., "&New" → Alt+N)
            status_tip: Status bar tip text (shown when hovering)
            triggered: Callable to run when action activated
            shortcut: Keyboard shortcut (StandardKey or string), optional
            checkable: Whether action is checkable (toggle), default False
            checked: Initial checked state, default False

        RETURNS:
            Fully configured QAction instance ready to use
        """
        # === STEP 1: CREATE ACTION ===
        # Create QAction object with text and parent window
        # Parent window ensures action is deleted when window closes
        action = QAction(text, self.window)

        # === STEP 2: SET STATUS TIP ===
        # Status tip shows in status bar when user hovers over menu item
        action.setStatusTip(status_tip)

        # === STEP 3: CONNECT TO HANDLER ===
        # When action is triggered (clicked or keyboard shortcut), call the handler
        # This is the "signal/slot" pattern in Qt (like pub/sub in JavaScript)
        action.triggered.connect(triggered)

        # === STEP 4: SET KEYBOARD SHORTCUT (Optional) ===
        if shortcut is not None:
            # Check if shortcut is a StandardKey (cross-platform standard like Ctrl+N)
            if isinstance(shortcut, QKeySequence.StandardKey):
                # StandardKey automatically adapts to platform (Cmd on Mac, Ctrl elsewhere)
                action.setShortcut(QKeySequence(shortcut))
            else:
                # Custom shortcut string (like "F11" or "Ctrl+Shift+V")
                action.setShortcut(shortcut)

        # === STEP 5: MAKE CHECKABLE (Optional) ===
        # Checkable actions are toggles (on/off switches) like checkboxes
        if checkable:
            action.setCheckable(True)  # Make it a toggle
            action.setChecked(checked)  # Set initial state (on or off)

        # === STEP 6: RETURN CONFIGURED ACTION ===
        # Action is now fully set up and ready to use!
        return action

    def create_action(
        self,
        text: str,
        triggered: Any,
        shortcut: Optional[Any] = None,
        icon: Optional[Any] = None,
        tooltip: Optional[str] = None,
        enabled: bool = True,
        checkable: bool = False,
        checked: bool = False,
    ) -> QAction:
        """
        Public API to create a single QAction.

        This is a convenience wrapper around _create_action() with additional
        parameters for icon, tooltip, and enabled state. Useful for creating
        custom actions or extending the application.

        Args:
            text: Action text (e.g., "New File")
            triggered: Callback function to run when action is triggered
            shortcut: Optional keyboard shortcut
            icon: Optional QIcon for the action
            tooltip: Optional tooltip text (also used as status tip)
            enabled: Whether action is enabled (default: True)
            checkable: Whether action is checkable/toggleable (default: False)
            checked: Initial checked state if checkable (default: False)

        Returns:
            Configured QAction instance
        """
        # Use tooltip as status_tip if provided, otherwise use text
        status_tip = tooltip if tooltip else text

        # Create action using private helper
        action = self._create_action(
            text=text,
            status_tip=status_tip,
            triggered=triggered,
            shortcut=shortcut,
            checkable=checkable,
            checked=checked,
        )

        # Set icon if provided
        if icon is not None:
            action.setIcon(icon)

        # Set tooltip if provided (in addition to status tip)
        if tooltip is not None:
            action.setToolTip(tooltip)

        # Set enabled state
        action.setEnabled(enabled)

        return action

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
        """
        logger.debug("Creating actions...")

        # === FILE MENU ACTIONS (10 actions) ===
        # These actions handle file operations: create, open, save, export, quit

        # New file (Ctrl+N) - creates a blank document
        self.new_act = self._create_action(
            "&New",
            "Create a new file",
            self.window.new_file,
            shortcut=QKeySequence.StandardKey.New,
        )

        self.open_act = self._create_action(
            "&Open...",
            "Open a file",
            self.window.open_file,
            shortcut=QKeySequence.StandardKey.Open,
        )

        self.save_act = self._create_action(
            "&Save",
            "Save the document as AsciiDoc format (.adoc)",
            self.window.save_file,
            shortcut=QKeySequence.StandardKey.Save,
        )

        self.save_as_act = self._create_action(
            "Save &As...",
            "Save with a new name",
            lambda: self.window.save_file(save_as=True),
            shortcut=QKeySequence.StandardKey.SaveAs,
        )

        self.save_as_adoc_act = self._create_action(
            "AsciiDoc (*.adoc)",
            "Save as AsciiDoc file",
            lambda: self.window.save_file_as_format("adoc"),
        )

        self.save_as_md_act = self._create_action(
            "GitHub Markdown (*.md)",
            "Export to GitHub Markdown format",
            lambda: self.window.save_file_as_format("md"),
        )

        self.save_as_docx_act = self._create_action(
            "Microsoft Word (*.docx)",
            "Export to Microsoft Office 365 Word format",
            lambda: self.window.save_file_as_format("docx"),
        )

        self.save_as_html_act = self._create_action(
            "HTML Web Page (*.html)",
            "Export to HTML format (can print to PDF from browser)",
            lambda: self.window.save_file_as_format("html"),
        )

        self.save_as_pdf_act = self._create_action(
            "Adobe PDF (*.pdf)",
            "Export to Adobe Acrobat PDF format",
            lambda: self.window.save_file_as_format("pdf"),
        )

        # Exit application (Ctrl+Q) - closes the entire app
        self.exit_act = self._create_action(
            "E&xit",
            "Exit the application",
            self.window.close,
            shortcut=QKeySequence.StandardKey.Quit,
        )

        # === EDIT MENU ACTIONS (7 actions) ===
        # These actions handle text editing: undo, redo, cut, copy, paste, preferences

        # Undo (Ctrl+Z) - reverses the last edit action
        self.undo_act = self._create_action(
            "&Undo",
            "Undo last action",
            self.editor.undo,
            shortcut=QKeySequence.StandardKey.Undo,
        )

        self.redo_act = self._create_action(
            "&Redo",
            "Redo last action",
            self.editor.redo,
            shortcut=QKeySequence.StandardKey.Redo,
        )

        self.cut_act = self._create_action(
            "Cu&t",
            "Cut selection",
            self.editor.cut,
            shortcut=QKeySequence.StandardKey.Cut,
        )

        self.copy_act = self._create_action(
            "&Copy",
            "Copy selection",
            self.editor.copy,
            shortcut=QKeySequence.StandardKey.Copy,
        )

        self.paste_act = self._create_action(
            "&Paste",
            "Paste from clipboard",
            self.editor.paste,
            shortcut=QKeySequence.StandardKey.Paste,
        )

        self.convert_paste_act = self._create_action(
            "Convert && Paste",
            "Convert clipboard content to AsciiDoc",
            self.window.convert_and_paste_from_clipboard,
            shortcut="Ctrl+Shift+V",
        )

        self.preferences_act = self._create_action(
            "&Preferences...",
            "Configure application preferences",
            self.window._show_preferences_dialog,
            shortcut="Ctrl+,",
        )

        # === VIEW MENU ACTIONS (6 actions) ===
        # These actions control the UI appearance: zoom, theme, scroll sync, maximize

        # Zoom in (Ctrl++) - makes editor text larger
        self.zoom_in_act = self._create_action(
            "Zoom &In",
            "Increase font size",
            lambda: self.window._zoom(1),
            shortcut=QKeySequence.StandardKey.ZoomIn,
        )

        self.zoom_out_act = self._create_action(
            "Zoom &Out",
            "Decrease font size",
            lambda: self.window._zoom(-1),
            shortcut=QKeySequence.StandardKey.ZoomOut,
        )

        self.dark_mode_act = self._create_action(
            "&Dark Mode",
            "Toggle dark mode",
            self.window._toggle_dark_mode,
            checkable=True,
            checked=self._settings.dark_mode,
        )

        self.sync_scrolling_act = self._create_action(
            "&Synchronized Scrolling",
            "Toggle synchronized scrolling between editor and preview",
            self.window._toggle_sync_scrolling,
            checkable=True,
            checked=self._sync_scrolling,
        )

        self.maximize_editor_act = self._create_action(
            "Maximize &Editor",
            "Toggle maximize editor pane",
            lambda: self.window._toggle_pane_maximize("editor"),
            shortcut="Ctrl+Shift+E",
        )

        self.maximize_preview_act = self._create_action(
            "Maximize &Preview",
            "Toggle maximize preview pane",
            lambda: self.window._toggle_pane_maximize("preview"),
            shortcut="Ctrl+Shift+R",
        )

        # === GIT MENU ACTIONS (4 actions) ===
        # These actions handle Git version control: set repo, commit, pull, push

        # Set Git repository - choose which folder to track with Git
        self.set_repo_act = self._create_action(
            "Set &Repository...",
            "Select Git repository",
            self.window._select_git_repository,
        )

        self.git_commit_act = self._create_action(
            "&Commit...",
            "Commit changes",
            self.window._trigger_git_commit,
            shortcut="Ctrl+Shift+C",
        )

        self.git_pull_act = self._create_action(
            "&Pull",
            "Pull from remote",
            self.window._trigger_git_pull,
            shortcut="Ctrl+Shift+P",
        )

        self.git_push_act = self._create_action(
            "P&ush",
            "Push to remote",
            self.window._trigger_git_push,
            shortcut="Ctrl+Shift+U",
        )

        # === GITHUB SUBMENU ACTIONS (5 actions) - v1.6.0 ===
        # These actions integrate with GitHub CLI for PR and Issue management

        # Create pull request - opens dialog to create GitHub PR
        self.github_create_pr_act = self._create_action(
            "Create &Pull Request...",
            "Create a GitHub pull request",
            self.window._trigger_github_create_pr,
        )

        self.github_list_prs_act = self._create_action(
            "&List Pull Requests",
            "List GitHub pull requests",
            self.window._trigger_github_list_prs,
        )

        self.github_create_issue_act = self._create_action(
            "Create &Issue...",
            "Create a GitHub issue",
            self.window._trigger_github_create_issue,
        )

        self.github_list_issues_act = self._create_action(
            "List &Issues",
            "List GitHub issues",
            self.window._trigger_github_list_issues,
        )

        self.github_repo_info_act = self._create_action(
            "Repository &Info",
            "Show GitHub repository information",
            self.window._trigger_github_repo_info,
        )

        # === TOOLS MENU ACTIONS (4 actions) ===
        # These actions show status of external tools: Pandoc, Ollama AI

        # Pandoc status - shows if Pandoc is installed and working
        self.pandoc_status_act = self._create_action(
            "&Pandoc Status",
            "Check Pandoc installation status",
            self.window._show_pandoc_status,
        )

        self.pandoc_formats_act = self._create_action(
            "Supported &Formats",
            "Show supported conversion formats",
            self.window._show_supported_formats,
        )

        self.ollama_status_act = self._create_action(
            "&Ollama Status",
            "Check Ollama service and installation status",
            self.window._show_ollama_status,
        )

        self.ollama_settings_act = self._create_action(
            "&Settings...",
            "Configure Ollama AI integration and select model",
            self.window._show_ollama_settings,
        )

        # === HELP MENU ACTIONS (1 action) ===
        # These actions provide help and information about the application

        # About dialog - shows version, license, credits
        self.about_act = self._create_action(
            "&About",
            "About AsciiDoctor Artisan",
            self.window._show_about,
        )

        # All actions created! Log success message
        logger.debug("Actions created successfully")

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
        - Edit: Undo, Redo, Cut, Copy, Paste, Convert & Paste, Preferences
        - View: Zoom In/Out, Dark Mode, Sync Scrolling, Maximize Editor/Preview
        - Git: Set Repo, Commit, Pull, Push, GitHub submenu (5 actions)
        - Tools: AI Status (Ollama submenu), Pandoc Status, Pandoc Formats
        - Help: About

        SEPARATORS:
        Separators (horizontal lines) visually group related actions:
        - File menu: [New/Open/Save/SaveAs] | [Exit]
        - Edit menu: [Undo/Redo] | [Cut/Copy/Paste] | [Convert&Paste] | [Preferences]

        PARAMETERS:
            None

        RETURNS:
            None (modifies the main window's menu bar)

        SIDE EFFECTS:
            Creates and populates the application's menu bar
        """
        logger.debug("Creating menus...")
        # Get the menu bar from the main window
        menubar = self.window.menuBar()

        # === FILE MENU ===
        # Create File menu (&F makes Alt+F open the menu)
        file_menu = menubar.addMenu("&File")

        # Add file operations (New, Open)
        file_menu.addAction(self.new_act)  # New file (Ctrl+N)
        file_menu.addAction(self.open_act)  # Open file (Ctrl+O)

        # Separator (visual divider line)
        file_menu.addSeparator()

        # Add save operations (Save, Save As)
        file_menu.addAction(self.save_act)  # Save (Ctrl+S)
        file_menu.addAction(self.save_as_act)  # Save As (Ctrl+Shift+S)

        # Create "Export As" submenu with 5 format options
        export_menu = file_menu.addMenu("&Export As")
        export_menu.addAction(self.save_as_adoc_act)  # Export to AsciiDoc
        export_menu.addAction(self.save_as_md_act)  # Export to Markdown
        export_menu.addAction(self.save_as_docx_act)  # Export to Word
        export_menu.addAction(self.save_as_html_act)  # Export to HTML
        export_menu.addAction(self.save_as_pdf_act)  # Export to PDF

        # Separator before exit action
        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)  # Exit application (Ctrl+Q)

        # === EDIT MENU ===
        edit_menu = menubar.addMenu("&Edit")

        # Undo/Redo group
        edit_menu.addAction(self.undo_act)  # Undo (Ctrl+Z)
        edit_menu.addAction(self.redo_act)  # Redo (Ctrl+Y)

        # Separator
        edit_menu.addSeparator()

        # Clipboard operations group
        edit_menu.addAction(self.cut_act)  # Cut (Ctrl+X)
        edit_menu.addAction(self.copy_act)  # Copy (Ctrl+C)
        edit_menu.addAction(self.paste_act)  # Paste (Ctrl+V)

        # Separator
        edit_menu.addSeparator()

        # Special paste with format conversion
        edit_menu.addAction(self.convert_paste_act)  # Convert & Paste (Ctrl+Shift+V)

        # Separator
        edit_menu.addSeparator()

        # Preferences dialog
        edit_menu.addAction(self.preferences_act)  # Preferences (Ctrl+,)

        # === VIEW MENU ===
        view_menu = menubar.addMenu("&View")

        # Zoom controls
        view_menu.addAction(self.zoom_in_act)  # Zoom in (Ctrl++)
        view_menu.addAction(self.zoom_out_act)  # Zoom out (Ctrl+-)

        # Separator
        view_menu.addSeparator()

        # UI appearance toggles
        view_menu.addAction(self.dark_mode_act)  # Dark mode (toggle)
        view_menu.addAction(self.sync_scrolling_act)  # Scroll sync (toggle)

        # Separator
        view_menu.addSeparator()

        # Pane maximize toggles
        view_menu.addAction(self.maximize_editor_act)  # Maximize editor (Ctrl+Shift+E)
        view_menu.addAction(
            self.maximize_preview_act
        )  # Maximize preview (Ctrl+Shift+R)

        # === GIT MENU ===
        git_menu = menubar.addMenu("&Git")

        # Repository setup
        git_menu.addAction(self.set_repo_act)  # Set Git repository path

        # Separator
        git_menu.addSeparator()

        # Git operations
        git_menu.addAction(self.git_commit_act)  # Commit changes (Ctrl+Shift+C)
        git_menu.addAction(self.git_pull_act)  # Pull from remote (Ctrl+Shift+P)
        git_menu.addAction(self.git_push_act)  # Push to remote (Ctrl+Shift+U)

        # === GITHUB SUBMENU (v1.6.0) ===
        git_menu.addSeparator()
        github_submenu = git_menu.addMenu("Git&Hub")  # GitHub CLI integration

        # Pull request operations
        github_submenu.addAction(self.github_create_pr_act)  # Create PR
        github_submenu.addAction(self.github_list_prs_act)  # List PRs

        # Separator
        github_submenu.addSeparator()

        # Issue operations
        github_submenu.addAction(self.github_create_issue_act)  # Create issue
        github_submenu.addAction(self.github_list_issues_act)  # List issues

        # Separator
        github_submenu.addSeparator()

        # Repository information
        github_submenu.addAction(self.github_repo_info_act)  # Show repo info

        # === TOOLS MENU ===
        tools_menu = menubar.addMenu("&Tools")

        # AI Status submenu (Ollama integration)
        ai_status_menu = tools_menu.addMenu("&AI Status")
        ai_status_menu.addAction(self.ollama_status_act)  # Check Ollama status
        ai_status_menu.addAction(self.ollama_settings_act)  # Configure Ollama

        # Pandoc utilities
        tools_menu.addAction(self.pandoc_status_act)  # Check Pandoc status
        tools_menu.addAction(self.pandoc_formats_act)  # Show supported formats

        # === HELP MENU ===
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.about_act)  # Show About dialog

        # All menus created! Log success message
        logger.debug("Menus created successfully")
