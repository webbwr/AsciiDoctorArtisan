"""
Menu Builder - Constructs application menu bar structure.

Extracted from ActionManager to reduce class size (MA principle).
Organizes QAction objects into File, Edit, View, Git, Tools, Help menus.
"""

from typing import Any, Protocol


class ActionSource(Protocol):
    """Protocol for accessing action objects (avoid circular imports)."""

    # File actions
    new_act: Any
    new_from_template_act: Any
    open_act: Any
    save_act: Any
    save_as_act: Any
    save_as_adoc_act: Any
    save_as_md_act: Any
    save_as_docx_act: Any
    save_as_html_act: Any
    save_as_pdf_act: Any
    exit_act: Any

    # Edit actions
    undo_act: Any
    redo_act: Any
    cut_act: Any
    copy_act: Any
    paste_act: Any
    convert_paste_act: Any

    # Find actions
    find_act: Any
    replace_act: Any
    find_next_act: Any
    find_previous_act: Any

    # View actions
    zoom_in_act: Any
    zoom_out_act: Any
    dark_mode_act: Any
    sync_scrolling_act: Any
    maximize_window_act: Any
    maximize_editor_act: Any
    maximize_preview_act: Any

    # Git actions
    set_repo_act: Any
    git_status_act: Any
    git_commit_act: Any
    quick_commit_act: Any
    git_pull_act: Any
    git_push_act: Any

    # GitHub actions
    github_create_pr_act: Any
    github_list_prs_act: Any
    github_create_issue_act: Any
    github_list_issues_act: Any
    github_repo_info_act: Any

    # Tools actions
    validate_install_act: Any
    ollama_settings_act: Any
    anthropic_settings_act: Any
    app_settings_act: Any
    autocomplete_settings_act: Any
    toggle_chat_pane_act: Any
    font_settings_act: Any
    toggle_spell_check_act: Any
    syntax_check_settings_act: Any
    toggle_telemetry_act: Any
    toggle_theme_act: Any

    # Help actions
    about_act: Any
    anthropic_status_act: Any
    ollama_status_act: Any
    pandoc_formats_act: Any
    pandoc_status_act: Any
    telemetry_status_act: Any


class MenuBuilder:
    """
    Constructs application menu bar structure from QAction objects.

    This class was extracted from ActionManager to reduce class size
    per MA principle (590→~494 lines).

    Organizes 50+ actions into hierarchical menu structure:
    - File menu: New, Open, Save, Export submenu, Exit
    - Edit menu: Undo, Redo, Cut, Copy, Paste, Find/Replace
    - View menu: Zoom, Dark mode, Sync scroll, Maximize
    - Git menu: Repo, Commit, Pull, Push, GitHub submenu
    - Tools menu: Settings, AI submenu, Validation, UI toggles
    - Help menu: About, Service status checks
    """

    def __init__(self, action_source: ActionSource) -> None:
        """
        Initialize menu builder.

        Args:
            action_source: Source of QAction objects (ActionManager)
        """
        self.actions = action_source

    def create_file_menu(self, menubar: Any) -> None:
        """Create and populate File menu."""
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.actions.new_act)
        file_menu.addAction(self.actions.new_from_template_act)
        file_menu.addAction(self.actions.open_act)
        file_menu.addSeparator()
        file_menu.addAction(self.actions.save_act)
        file_menu.addAction(self.actions.save_as_act)
        export_menu = file_menu.addMenu("&Export As")
        export_menu.addAction(self.actions.save_as_adoc_act)
        export_menu.addAction(self.actions.save_as_md_act)
        export_menu.addAction(self.actions.save_as_docx_act)
        export_menu.addAction(self.actions.save_as_html_act)
        export_menu.addAction(self.actions.save_as_pdf_act)
        file_menu.addSeparator()
        file_menu.addAction(self.actions.exit_act)

    def create_edit_menu(self, menubar: Any) -> None:
        """Create and populate Edit menu."""
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.actions.undo_act)
        edit_menu.addAction(self.actions.redo_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions.cut_act)
        edit_menu.addAction(self.actions.copy_act)
        edit_menu.addAction(self.actions.paste_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions.convert_paste_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.actions.find_act)
        edit_menu.addAction(self.actions.replace_act)
        edit_menu.addAction(self.actions.find_next_act)
        edit_menu.addAction(self.actions.find_previous_act)

    def create_view_menu(self, menubar: Any) -> None:
        """Create and populate View menu."""
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.actions.zoom_in_act)
        view_menu.addAction(self.actions.zoom_out_act)
        view_menu.addSeparator()
        view_menu.addAction(self.actions.dark_mode_act)
        view_menu.addAction(self.actions.sync_scrolling_act)
        view_menu.addSeparator()
        view_menu.addAction(self.actions.maximize_window_act)
        view_menu.addAction(self.actions.maximize_editor_act)
        view_menu.addAction(self.actions.maximize_preview_act)

    def create_git_menu(self, menubar: Any) -> None:
        """Create and populate Git menu with GitHub submenu."""
        git_menu = menubar.addMenu("&Git")
        git_menu.addAction(self.actions.set_repo_act)
        git_menu.addAction(self.actions.git_status_act)
        git_menu.addSeparator()
        git_menu.addAction(self.actions.git_commit_act)
        git_menu.addAction(self.actions.quick_commit_act)
        git_menu.addAction(self.actions.git_pull_act)
        git_menu.addAction(self.actions.git_push_act)
        git_menu.addSeparator()
        github_submenu = git_menu.addMenu("Git&Hub")
        github_submenu.addAction(self.actions.github_create_pr_act)
        github_submenu.addAction(self.actions.github_list_prs_act)
        github_submenu.addSeparator()
        github_submenu.addAction(self.actions.github_create_issue_act)
        github_submenu.addAction(self.actions.github_list_issues_act)
        github_submenu.addSeparator()
        github_submenu.addAction(self.actions.github_repo_info_act)

    def create_tools_menu(self, menubar: Any) -> None:
        """Create and populate Tools menu with AI Settings submenu."""
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction(self.actions.validate_install_act)
        tools_menu.addSeparator()
        ai_settings_menu = tools_menu.addMenu("&AI Settings")
        ai_settings_menu.addAction(self.actions.ollama_settings_act)
        ai_settings_menu.addAction(self.actions.ollama_model_browser_act)
        ai_settings_menu.addAction(self.actions.anthropic_settings_act)
        tools_menu.addAction(self.actions.app_settings_act)
        tools_menu.addAction(self.actions.autocomplete_settings_act)
        tools_menu.addAction(self.actions.toggle_chat_pane_act)
        tools_menu.addAction(self.actions.font_settings_act)
        tools_menu.addAction(self.actions.toggle_spell_check_act)
        tools_menu.addAction(self.actions.syntax_check_settings_act)
        tools_menu.addAction(self.actions.toggle_telemetry_act)
        tools_menu.addAction(self.actions.toggle_theme_act)

    def create_help_menu(self, menubar: Any) -> None:
        """Create and populate Help menu."""
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.actions.about_act)
        help_menu.addSeparator()
        help_menu.addAction(self.actions.anthropic_status_act)
        help_menu.addAction(self.actions.ollama_status_act)
        help_menu.addAction(self.actions.pandoc_formats_act)
        help_menu.addAction(self.actions.pandoc_status_act)
        help_menu.addAction(self.actions.telemetry_status_act)
