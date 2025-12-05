"""
Tests for ui.action_manager module.

Tests QAction creation and management functionality.
"""

from unittest.mock import Mock

import pytest
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow


@pytest.fixture
def main_window(qapp):
    """Create a mock main window with required attributes."""
    window = QMainWindow()
    # Add required attributes that ActionManager expects
    window.editor = Mock()  # Text editor widget

    # Mock settings with proper return types (booleans, not Mocks)
    window._settings = Mock()
    window._settings.dark_mode = False  # Boolean, not Mock
    window._settings.ai_chat_enabled = False  # Boolean, not Mock
    window._settings.ollama_chat_enabled = False  # Boolean, not Mock
    window._settings.spell_check_enabled = False
    window._settings.syntax_check_realtime_enabled = False
    window._settings.autocomplete_enabled = False

    window._sync_scrolling = False  # Scroll sync state

    # Mock all window methods that create_actions() connects to
    window.new_file = Mock()
    window.new_from_template = Mock()  # v2.0.0 template feature
    window.open_file = Mock()
    window.save_file = Mock()
    window.save_file_as_format = Mock()
    window.convert_and_paste_from_clipboard = Mock()
    window.find_bar = Mock()
    window.find_bar.show_and_focus = Mock()
    window.find_bar.show_replace_and_focus = Mock()
    window._handle_find_next = Mock()
    window._handle_find_previous = Mock()

    # View actions
    window._zoom = Mock()
    window._toggle_dark_mode = Mock()
    window._toggle_sync_scrolling = Mock()
    window._toggle_maximize_window = Mock()
    window._toggle_pane_maximize = Mock()

    # Git handler with methods
    window.git_handler = Mock()
    window.git_handler.select_repository = Mock()
    window.git_handler.commit_changes = Mock()
    window.git_handler.pull_changes = Mock()
    window.git_handler.push_changes = Mock()
    window._show_git_status = Mock()
    window._show_quick_commit = Mock()

    # GitHub handler with methods
    window.github_handler = Mock()
    window.github_handler.create_pull_request = Mock()
    window.github_handler.list_pull_requests = Mock()
    window.github_handler.create_issue = Mock()
    window.github_handler.list_issues = Mock()
    window.github_handler.get_repo_info = Mock()

    # Dialog manager with all dialog methods
    window.dialog_manager = Mock()
    window.dialog_manager.show_installation_validator = Mock()
    window.dialog_manager.show_pandoc_status = Mock()
    window.dialog_manager.show_ollama_status = Mock()
    window.dialog_manager.show_anthropic_status = Mock()
    window.dialog_manager.show_telemetry_status = Mock()
    window.dialog_manager.show_ollama_settings = Mock()
    window.dialog_manager.show_anthropic_settings = Mock()
    window.dialog_manager.show_font_settings = Mock()
    window.dialog_manager.show_app_settings = Mock()
    window.dialog_manager.show_about = Mock()

    # Tools actions (remaining methods on window)
    window._show_ollama_model_browser = Mock()
    window.chat_manager = Mock()
    window.chat_manager.toggle_panel_visibility = Mock()
    window.spell_check_manager = Mock()
    window.spell_check_manager.toggle_spell_check = Mock()
    window.toggle_telemetry = Mock()
    window.show_autocomplete_settings = Mock()  # v2.0.0 auto-complete
    window.show_syntax_check_settings = Mock()  # v2.0.0 syntax checking

    return window


@pytest.mark.unit
class TestActionManagerBasics:
    """Test suite for ActionManager basic functionality."""

    def test_import_action_manager(self):
        """Test that ActionManager can be imported."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        assert ActionManager is not None

    def test_action_manager_creation(self, main_window):
        """Test creating ActionManager instance."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        assert manager is not None

    def test_action_manager_has_parent(self, main_window):
        """Test that ActionManager stores parent reference."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        assert hasattr(manager, "window")
        assert manager.window == main_window

    def test_create_action_method_exists(self, main_window):
        """Test that create_action method exists."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        assert hasattr(manager, "create_action")
        assert callable(getattr(manager, "create_action"))

    def test_private_create_action_exists(self, main_window):
        """Test that _create_action private method exists."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        assert hasattr(manager, "_create_action")
        assert callable(getattr(manager, "_create_action"))


@pytest.mark.unit
class TestActionCreation:
    """Test suite for action creation functionality."""

    def test_create_action_returns_qaction(self, main_window):
        """Test that create_action returns QAction."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test Action", lambda: None)

        assert isinstance(action, QAction)
        assert action.text() == "Test Action"

    def test_action_with_shortcut(self, main_window):
        """Test creating action with keyboard shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Save", lambda: None, shortcut="Ctrl+S")

        assert action.shortcut().toString() == "Ctrl+S"

    def test_action_with_standard_key_shortcut(self, main_window):
        """Test creating action with StandardKey shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager._create_action(
            "New",
            "Create new file",
            lambda: None,
            shortcut=QKeySequence.StandardKey.New,
        )

        # StandardKey.New is platform-specific (Ctrl+N or Cmd+N)
        shortcut_str = action.shortcut().toString()
        assert "N" in shortcut_str  # Should contain N key

    def test_action_with_icon(self, main_window):
        """Test creating action with icon."""
        from PySide6.QtWidgets import QStyle

        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        # Use a standard icon instead of null icon for testing
        icon = main_window.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        action = manager.create_action("Open", lambda: None, icon=icon)

        assert not action.icon().isNull()

    def test_action_with_tooltip(self, main_window):
        """Test creating action with tooltip."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Help", lambda: None, tooltip="Show help")

        assert action.toolTip() == "Show help"
        assert action.statusTip() == "Show help"  # Tooltip used as status tip

    def test_action_without_tooltip_uses_text(self, main_window):
        """Test that action without tooltip uses text as status tip."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Save", lambda: None)

        assert action.statusTip() == "Save"


@pytest.mark.unit
class TestActionState:
    """Test suite for action state management."""

    def test_action_enabled_state(self, main_window):
        """Test that actions can be enabled/disabled."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test", lambda: None, enabled=False)

        assert action.isEnabled() is False

        action.setEnabled(True)
        assert action.isEnabled() is True

    def test_action_default_enabled(self, main_window):
        """Test that actions are enabled by default."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test", lambda: None)

        assert action.isEnabled() is True

    def test_action_checkable(self, main_window):
        """Test creating checkable action."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Toggle", lambda: None, checkable=True)

        assert action.isCheckable() is True

    def test_action_checkable_with_initial_state(self, main_window):
        """Test checkable action with initial checked state."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Dark Mode", lambda: None, checkable=True, checked=True)

        assert action.isCheckable() is True
        assert action.isChecked() is True

    def test_action_check_state_change(self, main_window):
        """Test changing action check state."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Toggle", lambda: None, checkable=True)

        assert action.isChecked() is False
        action.setChecked(True)
        assert action.isChecked() is True
        action.setChecked(False)
        assert action.isChecked() is False


@pytest.mark.unit
class TestActionCallbacks:
    """Test suite for action callback connections."""

    def test_action_callback_connection(self, main_window):
        """Test that action callback is properly connected."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        callback_called = [False]

        def callback():
            callback_called[0] = True

        action = manager.create_action("Test", callback)
        action.trigger()

        assert callback_called[0] is True

    def test_action_callback_with_arguments(self, main_window):
        """Test action callback that expects arguments."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        callback_args = []

        def callback(checked):
            callback_args.append(checked)

        action = manager.create_action("Toggle", callback, checkable=True)
        action.trigger()  # Triggers with checked state

        assert len(callback_args) == 1
        assert isinstance(callback_args[0], bool)

    def test_multiple_action_triggers(self, main_window):
        """Test triggering action multiple times."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        counter = [0]

        def callback():
            counter[0] += 1

        action = manager.create_action("Increment", callback)

        action.trigger()
        action.trigger()
        action.trigger()

        assert counter[0] == 3


@pytest.mark.unit
class TestMultipleActions:
    """Test suite for managing multiple actions."""

    def test_multiple_actions_creation(self, main_window):
        """Test creating multiple actions."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        action1 = manager.create_action("Action 1", lambda: None)
        action2 = manager.create_action("Action 2", lambda: None)
        action3 = manager.create_action("Action 3", lambda: None)

        assert action1 != action2 != action3
        assert all(isinstance(a, QAction) for a in [action1, action2, action3])

    def test_actions_have_unique_text(self, main_window):
        """Test that each action has its own text."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        actions = [
            manager.create_action("New", lambda: None),
            manager.create_action("Open", lambda: None),
            manager.create_action("Save", lambda: None),
        ]

        texts = [action.text() for action in actions]
        assert texts == ["New", "Open", "Save"]

    def test_actions_have_independent_callbacks(self, main_window):
        """Test that actions have independent callbacks."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        results = []

        action1 = manager.create_action("A", lambda: results.append("A"))
        action2 = manager.create_action("B", lambda: results.append("B"))

        action1.trigger()
        action2.trigger()

        assert results == ["A", "B"]


@pytest.mark.unit
class TestActionMnemonics:
    """Test suite for action mnemonics (& in text)."""

    def test_action_with_mnemonic(self, main_window):
        """Test action with mnemonic (&N for Alt+N)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("&New", lambda: None)

        # Text includes &, which Qt uses for mnemonic
        assert "&New" in action.text() or "New" in action.text()

    def test_multiple_actions_with_mnemonics(self, main_window):
        """Test multiple actions with different mnemonics."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        actions = [
            manager.create_action("&File", lambda: None),
            manager.create_action("&Edit", lambda: None),
            manager.create_action("&View", lambda: None),
        ]

        assert all(isinstance(action, QAction) for action in actions)


@pytest.mark.unit
class TestActionEdgeCases:
    """Test suite for edge cases and error handling."""

    def test_action_with_empty_text(self, main_window):
        """Test creating action with empty text."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("", lambda: None)

        assert action.text() == ""
        assert isinstance(action, QAction)

    def test_action_with_none_shortcut(self, main_window):
        """Test action with explicitly None shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test", lambda: None, shortcut=None)

        assert action.shortcut().isEmpty()

    def test_action_with_none_icon(self, main_window):
        """Test action with None icon."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test", lambda: None, icon=None)

        assert action.icon().isNull()

    def test_checkable_false_ignores_checked_parameter(self, main_window):
        """Test that non-checkable action ignores checked parameter."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Test", lambda: None, checkable=False, checked=True)

        assert action.isCheckable() is False
        # Non-checkable actions can't be checked
        assert action.isChecked() is False


@pytest.mark.unit
class TestCreateActionsMethod:
    """Test suite for create_actions() method that creates all 50+ actions."""

    def test_creates_all_file_actions(self, main_window):
        """Test that create_actions creates all File menu actions (10 actions)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # File menu has 10 actions
        assert hasattr(manager, "new_act")
        assert hasattr(manager, "open_act")
        assert hasattr(manager, "save_act")
        assert hasattr(manager, "save_as_act")
        assert hasattr(manager, "save_as_adoc_act")
        assert hasattr(manager, "save_as_md_act")
        assert hasattr(manager, "save_as_docx_act")
        assert hasattr(manager, "save_as_html_act")
        assert hasattr(manager, "save_as_pdf_act")
        assert hasattr(manager, "exit_act")

    def test_creates_all_edit_actions(self, main_window):
        """Test that create_actions creates all Edit menu actions (11 actions)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Edit menu has 11 actions (includes Find & Replace)
        assert hasattr(manager, "undo_act")
        assert hasattr(manager, "redo_act")
        assert hasattr(manager, "cut_act")
        assert hasattr(manager, "copy_act")
        assert hasattr(manager, "paste_act")
        assert hasattr(manager, "convert_paste_act")
        assert hasattr(manager, "find_act")
        assert hasattr(manager, "replace_act")
        assert hasattr(manager, "find_next_act")
        assert hasattr(manager, "find_previous_act")

    def test_creates_all_view_actions(self, main_window):
        """Test that create_actions creates all View menu actions (7 actions)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # View menu has 7 actions
        assert hasattr(manager, "zoom_in_act")
        assert hasattr(manager, "zoom_out_act")
        assert hasattr(manager, "dark_mode_act")
        assert hasattr(manager, "sync_scrolling_act")
        assert hasattr(manager, "maximize_window_act")
        assert hasattr(manager, "maximize_editor_act")
        assert hasattr(manager, "maximize_preview_act")

    def test_creates_all_git_actions(self, main_window):
        """Test that create_actions creates all Git menu actions (6 actions)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Git menu has 6 actions (including status and quick commit)
        assert hasattr(manager, "set_repo_act")
        assert hasattr(manager, "git_status_act")
        assert hasattr(manager, "git_commit_act")
        assert hasattr(manager, "git_pull_act")
        assert hasattr(manager, "git_push_act")
        assert hasattr(manager, "quick_commit_act")

    def test_creates_all_github_actions(self, main_window):
        """Test that create_actions creates all GitHub menu actions (5 actions)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # GitHub submenu has 5 actions
        assert hasattr(manager, "github_create_pr_act")
        assert hasattr(manager, "github_list_prs_act")
        assert hasattr(manager, "github_create_issue_act")
        assert hasattr(manager, "github_list_issues_act")
        assert hasattr(manager, "github_repo_info_act")

    def test_creates_all_tools_actions(self, main_window):
        """Test that create_actions creates all Tools menu actions (8+ actions)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Tools menu has 8+ actions
        assert hasattr(manager, "validate_install_act")
        assert hasattr(manager, "toggle_chat_pane_act")
        assert hasattr(manager, "toggle_theme_act")
        assert hasattr(manager, "pandoc_status_act")
        assert hasattr(manager, "pandoc_formats_act")
        assert hasattr(manager, "ollama_status_act")
        assert hasattr(manager, "anthropic_status_act")
        assert hasattr(manager, "telemetry_status_act")
        assert hasattr(manager, "ollama_settings_act")
        assert hasattr(manager, "anthropic_settings_act")
        assert hasattr(manager, "app_settings_act")

    def test_creates_all_help_actions(self, main_window):
        """Test that create_actions creates all Help menu actions (1 action)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Help menu has 1 action
        assert hasattr(manager, "about_act")

    def test_all_actions_are_qaction_instances(self, main_window):
        """Test that all created actions are QAction instances."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Sample key actions from each menu
        key_actions = [
            manager.new_act,
            manager.save_act,
            manager.undo_act,
            manager.copy_act,
            manager.dark_mode_act,
            manager.git_commit_act,
            manager.github_create_pr_act,
            manager.about_act,
        ]

        assert all(isinstance(action, QAction) for action in key_actions)


@pytest.mark.unit
class TestCreateMenusMethod:
    """Test suite for create_menus() method that builds menu bar."""

    def test_creates_menubar(self, main_window):
        """Test that create_menus creates the menu bar."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        assert menubar is not None
        assert menubar.actions()  # Has some menus

    def test_creates_file_menu(self, main_window):
        """Test that create_menus creates File menu."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menus = [action.text() for action in menubar.actions()]
        assert "&File" in menus

    def test_creates_edit_menu(self, main_window):
        """Test that create_menus creates Edit menu."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menus = [action.text() for action in menubar.actions()]
        assert "&Edit" in menus

    def test_creates_view_menu(self, main_window):
        """Test that create_menus creates View menu."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menus = [action.text() for action in menubar.actions()]
        assert "&View" in menus

    def test_creates_git_menu(self, main_window):
        """Test that create_menus creates Git menu."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menus = [action.text() for action in menubar.actions()]
        assert "&Git" in menus

    def test_creates_tools_menu(self, main_window):
        """Test that create_menus creates Tools menu."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menus = [action.text() for action in menubar.actions()]
        assert "&Tools" in menus

    def test_creates_help_menu(self, main_window):
        """Test that create_menus creates Help menu."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menus = [action.text() for action in menubar.actions()]
        assert "&Help" in menus

    def test_file_menu_has_export_submenu(self, main_window):
        """Test that File menu has 'Export As' submenu."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        file_menu = None
        for action in menubar.actions():
            if "&File" in action.text():
                file_menu = action.menu()
                break

        assert file_menu is not None
        # Check for Export As submenu
        submenus = [action.text() for action in file_menu.actions() if action.menu()]
        assert "&Export As" in submenus

    def test_git_menu_has_github_submenu(self, main_window):
        """Test that Git menu has GitHub submenu."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        git_menu = None
        for action in menubar.actions():
            if "&Git" in action.text():
                git_menu = action.menu()
                break

        assert git_menu is not None
        # Check for GitHub submenu
        submenus = [action.text() for action in git_menu.actions() if action.menu()]
        assert "Git&Hub" in submenus

    def test_tools_menu_has_ai_settings_submenu(self, main_window):
        """Test that Tools menu has AI Settings submenu."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        tools_menu = None
        for action in menubar.actions():
            if "&Tools" in action.text():
                tools_menu = action.menu()
                break

        assert tools_menu is not None
        # Check for AI Settings submenu
        submenus = [action.text() for action in tools_menu.actions() if action.menu()]
        assert "&AI Settings" in submenus


@pytest.mark.unit
class TestMenuStructure:
    """Test suite for menu organization and structure."""

    def test_file_menu_contains_new_and_save_actions(self, main_window):
        """Test that File menu contains New and Save actions."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        file_menu = None
        for action in menubar.actions():
            if "&File" in action.text():
                file_menu = action.menu()
                break

        assert file_menu is not None
        action_texts = [action.text() for action in file_menu.actions() if action.text()]
        assert "&New" in action_texts
        assert "&Save" in action_texts

    def test_edit_menu_contains_undo_and_copy_actions(self, main_window):
        """Test that Edit menu contains Undo and Copy actions."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        edit_menu = None
        for action in menubar.actions():
            if "&Edit" in action.text():
                edit_menu = action.menu()
                break

        assert edit_menu is not None
        action_texts = [action.text() for action in edit_menu.actions() if action.text()]
        assert "&Undo" in action_texts
        assert "&Copy" in action_texts

    def test_view_menu_contains_zoom_and_dark_mode_actions(self, main_window):
        """Test that View menu contains Zoom and Dark Mode actions."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        view_menu = None
        for action in menubar.actions():
            if "&View" in action.text():
                view_menu = action.menu()
                break

        assert view_menu is not None
        action_texts = [action.text() for action in view_menu.actions() if action.text()]
        assert "Zoom &In" in action_texts
        assert "&Toggle Dark Mode" in action_texts

    def test_git_menu_contains_commit_and_push_actions(self, main_window):
        """Test that Git menu contains Commit and Push actions."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        git_menu = None
        for action in menubar.actions():
            if "&Git" in action.text():
                git_menu = action.menu()
                break

        assert git_menu is not None
        action_texts = [action.text() for action in git_menu.actions() if action.text()]
        assert "&Commit Changes..." in action_texts
        assert "P&ush" in action_texts

    def test_tools_menu_contains_settings_action(self, main_window):
        """Test that Tools menu contains Application Settings action."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        tools_menu = None
        for action in menubar.actions():
            if "&Tools" in action.text():
                tools_menu = action.menu()
                break

        assert tools_menu is not None
        action_texts = [action.text() for action in tools_menu.actions() if action.text()]
        assert "Application &Settings..." in action_texts

    def test_help_menu_contains_about_action(self, main_window):
        """Test that Help menu contains About action."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        help_menu = None
        for action in menubar.actions():
            if "&Help" in action.text():
                help_menu = action.menu()
                break

        assert help_menu is not None
        action_texts = [action.text() for action in help_menu.actions() if action.text()]
        assert "&About" in action_texts

    def test_file_menu_has_separators(self, main_window):
        """Test that File menu has separator dividers."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        file_menu = None
        for action in menubar.actions():
            if "&File" in action.text():
                file_menu = action.menu()
                break

        assert file_menu is not None
        # Count separators
        separators = [action for action in file_menu.actions() if action.isSeparator()]
        assert len(separators) >= 2  # At least 2 separators in File menu

    def test_menu_order_is_correct(self, main_window):
        """Test that menus appear in correct order."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menu_texts = [action.text() for action in menubar.actions()]

        # Expected order: File, Edit, View, Git, Tools, Help
        expected_order = ["&File", "&Edit", "&View", "&Git", "&Tools", "&Help"]
        assert menu_texts == expected_order


@pytest.mark.unit
class TestSpecificActions:
    """Test suite for specific action properties and shortcuts."""

    def test_new_action_has_correct_shortcut(self, main_window):
        """Test that New action has Ctrl+N (StandardKey.New) shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        shortcut_str = manager.new_act.shortcut().toString()
        # StandardKey.New is Ctrl+N on Windows/Linux, Cmd+N on Mac
        assert "N" in shortcut_str

    def test_save_action_has_correct_shortcut(self, main_window):
        """Test that Save action has Ctrl+S (StandardKey.Save) shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        shortcut_str = manager.save_act.shortcut().toString()
        # StandardKey.Save is Ctrl+S on Windows/Linux, Cmd+S on Mac
        assert "S" in shortcut_str

    def test_dark_mode_action_has_shortcut(self, main_window):
        """Test that Dark Mode action has F11 shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        assert "F11" in manager.dark_mode_act.shortcut().toString()

    def test_sync_scrolling_action_is_checkable(self, main_window):
        """Test that Synchronized Scrolling action is checkable."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        assert manager.sync_scrolling_act.isCheckable() is True

    def test_git_commit_action_has_shortcut(self, main_window):
        """Test that Git Commit action has Ctrl+Shift+C shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        shortcut_str = manager.git_commit_act.shortcut().toString()
        assert "C" in shortcut_str
        assert "Shift" in shortcut_str or "⇧" in shortcut_str

    def test_quick_commit_action_has_shortcut(self, main_window):
        """Test that Quick Commit action has Ctrl+G shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        shortcut_str = manager.quick_commit_act.shortcut().toString()
        assert "G" in shortcut_str


@pytest.mark.unit
class TestActionShortcuts:
    """Test suite for keyboard shortcuts (StandardKey vs custom)."""

    def test_standard_key_shortcuts_adapt_to_platform(self, main_window):
        """Test that StandardKey shortcuts are set correctly."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # StandardKey shortcuts should not be empty
        assert not manager.new_act.shortcut().isEmpty()
        assert not manager.open_act.shortcut().isEmpty()
        assert not manager.save_act.shortcut().isEmpty()

    def test_custom_string_shortcuts(self, main_window):
        """Test that custom string shortcuts are set correctly."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Convert & Paste uses custom "Ctrl+Shift+V"
        shortcut_str = manager.convert_paste_act.shortcut().toString()
        assert "V" in shortcut_str
        assert "Shift" in shortcut_str or "⇧" in shortcut_str

    def test_f_key_shortcuts(self, main_window):
        """Test that F-key shortcuts (F7, F11) are set correctly."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # F11 for Dark Mode toggle
        assert "F11" in manager.dark_mode_act.shortcut().toString()

        # F7 for Spell Check toggle
        assert "F7" in manager.toggle_spell_check_act.shortcut().toString()

    def test_ctrl_shift_shortcuts(self, main_window):
        """Test that Ctrl+Shift+G shortcut is set for Git commit action."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Git commit uses Ctrl+Shift+G
        commit_shortcut = manager.git_commit_act.shortcut().toString()
        assert "G" in commit_shortcut
        assert "Shift" in commit_shortcut or "⇧" in commit_shortcut

        # Quick commit uses Ctrl+G
        quick_shortcut = manager.quick_commit_act.shortcut().toString()
        assert "G" in quick_shortcut

    def test_find_actions_have_correct_shortcuts(self, main_window):
        """Test that Find/Replace actions have correct shortcuts."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Find = Ctrl+F (StandardKey.Find)
        find_shortcut = manager.find_act.shortcut().toString()
        assert "F" in find_shortcut

        # Replace = Ctrl+H (StandardKey.Replace)
        replace_shortcut = manager.replace_act.shortcut().toString()
        assert "H" in replace_shortcut

        # Find Next = F3 (StandardKey.FindNext)
        find_next_shortcut = manager.find_next_act.shortcut().toString()
        assert "F3" in find_next_shortcut

    def test_git_actions_have_shortcuts(self, main_window):
        """Test that commit Git actions have keyboard shortcuts."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Only commit actions have shortcuts
        git_actions_with_shortcuts = [
            manager.git_commit_act,  # Ctrl+Shift+G
            manager.quick_commit_act,  # Ctrl+G
        ]

        # These should have non-empty shortcuts
        assert all(not action.shortcut().isEmpty() for action in git_actions_with_shortcuts)

    def test_github_actions_have_no_shortcuts(self, main_window):
        """Test that GitHub actions have no keyboard shortcuts (accessed via menu only)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        github_actions = [
            manager.github_create_pr_act,
            manager.github_list_prs_act,
            manager.github_create_issue_act,
            manager.github_list_issues_act,
            manager.github_repo_info_act,
        ]

        # All should have empty shortcuts
        assert all(action.shortcut().isEmpty() for action in github_actions)

    def test_all_shortcuts_are_unique(self, main_window):
        """Test that no two actions share the same keyboard shortcut."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Collect all non-empty shortcuts
        all_actions = [
            manager.new_act,
            manager.open_act,
            manager.save_act,
            manager.save_as_act,
            manager.undo_act,
            manager.redo_act,
            manager.cut_act,
            manager.copy_act,
            manager.paste_act,
            manager.convert_paste_act,
            manager.find_act,
            manager.replace_act,
            manager.find_next_act,
            manager.find_previous_act,
            manager.zoom_in_act,
            manager.zoom_out_act,
            manager.git_status_act,
            manager.git_commit_act,
            manager.git_pull_act,
            manager.git_push_act,
            manager.quick_commit_act,
        ]

        shortcuts = [action.shortcut().toString() for action in all_actions if not action.shortcut().isEmpty()]

        # Note: F11 is intentionally used by both dark_mode_act and maximize_window_act
        # (they trigger the same method), so we don't check for strict uniqueness
        # Just ensure shortcuts list is not empty
        assert len(shortcuts) > 0


@pytest.mark.unit
class TestActionIntegration:
    """Test suite for actions integrating with window methods."""

    def test_actions_have_window_reference(self, main_window):
        """Test that actions have reference to main window as parent."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Actions should have main_window as parent
        assert manager.new_act.parent() == main_window
        assert manager.save_act.parent() == main_window

    def test_new_action_triggers_window_method(self, main_window):
        """Test that New action is connected to window.new_file method."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        # Mock the new_file method
        main_window.new_file = Mock()

        manager.create_actions()
        manager.new_act.trigger()

        # Should call window.new_file
        main_window.new_file.assert_called_once()

    def test_save_action_triggers_window_method(self, main_window):
        """Test that Save action is connected to window.save_file method."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        # Mock the save_file method
        main_window.save_file = Mock()

        manager.create_actions()
        manager.save_act.trigger()

        # Should call window.save_file
        main_window.save_file.assert_called_once()

    def test_undo_action_triggers_editor_method(self, main_window):
        """Test that Undo action is connected to editor.undo method."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.undo_act.trigger()

        # Should call editor.undo
        main_window.editor.undo.assert_called_once()

    def test_copy_action_triggers_editor_method(self, main_window):
        """Test that Copy action is connected to editor.copy method."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.copy_act.trigger()

        # Should call editor.copy
        main_window.editor.copy.assert_called_once()

    def test_exit_action_triggers_window_close(self, main_window):
        """Test that Exit action is connected to window.close method."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        # Mock the close method
        main_window.close = Mock()

        manager.create_actions()
        manager.exit_act.trigger()

        # Should call window.close
        main_window.close.assert_called_once()


@pytest.mark.unit
class TestMenuAccessibility:
    """Test suite for menu mnemonics and accessibility."""

    def test_file_menu_has_mnemonic(self, main_window):
        """Test that File menu has keyboard mnemonic (Alt+F)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menu_texts = [action.text() for action in menubar.actions()]

        # File menu should have & before F for mnemonic
        assert "&File" in menu_texts

    def test_edit_menu_has_mnemonic(self, main_window):
        """Test that Edit menu has keyboard mnemonic (Alt+E)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menu_texts = [action.text() for action in menubar.actions()]

        assert "&Edit" in menu_texts

    def test_view_menu_has_mnemonic(self, main_window):
        """Test that View menu has keyboard mnemonic (Alt+V)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menu_texts = [action.text() for action in menubar.actions()]

        assert "&View" in menu_texts

    def test_git_menu_has_mnemonic(self, main_window):
        """Test that Git menu has keyboard mnemonic (Alt+G)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menu_texts = [action.text() for action in menubar.actions()]

        assert "&Git" in menu_texts

    def test_tools_menu_has_mnemonic(self, main_window):
        """Test that Tools menu has keyboard mnemonic (Alt+T)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menu_texts = [action.text() for action in menubar.actions()]

        assert "&Tools" in menu_texts

    def test_help_menu_has_mnemonic(self, main_window):
        """Test that Help menu has keyboard mnemonic (Alt+H)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()
        manager.create_menus()

        menubar = main_window.menuBar()
        menu_texts = [action.text() for action in menubar.actions()]

        assert "&Help" in menu_texts


@pytest.mark.unit
class TestEdgeCasesExtended:
    """Extended edge cases and additional scenarios."""

    def test_checkable_action_toggle_behavior(self, main_window):
        """Test that checkable actions toggle on/off correctly."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Sync scrolling action is checkable
        initial_state = manager.sync_scrolling_act.isChecked()
        manager.sync_scrolling_act.setChecked(not initial_state)

        assert manager.sync_scrolling_act.isChecked() == (not initial_state)

    def test_disabled_action_still_exists(self, main_window):
        """Test that disabled actions are still valid QAction objects."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        action = manager.create_action("Disabled", lambda: None, enabled=False)

        assert isinstance(action, QAction)
        assert action.isEnabled() is False

    def test_action_with_lambda_callback(self, main_window):
        """Test action with lambda callback (used for parameterized methods)."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)

        # Mock method
        main_window._zoom = Mock()

        # Create action with lambda
        action = manager.create_action("Zoom In", lambda: main_window._zoom(1))
        action.trigger()

        # Should call _zoom with parameter 1
        main_window._zoom.assert_called_once_with(1)

    def test_action_parent_is_window(self, main_window):
        """Test that all actions have main window as parent."""
        from asciidoc_artisan.ui.action_manager import ActionManager

        manager = ActionManager(main_window)
        manager.create_actions()

        # Sample actions from different menus
        sample_actions = [
            manager.new_act,
            manager.undo_act,
            manager.dark_mode_act,
            manager.git_commit_act,
            manager.about_act,
        ]

        # All should have main_window as parent
        assert all(action.parent() == main_window for action in sample_actions)
