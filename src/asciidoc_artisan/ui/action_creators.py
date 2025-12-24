"""Action Creators - Creates all QAction instances for menus (13 methods)."""

from typing import Any, Protocol

from PySide6.QtGui import QAction, QKeySequence


class ActionManagerContext(Protocol):
    """Protocol for ActionManager context (avoid circular imports)."""

    window: Any
    editor: Any
    _settings: Any
    _sync_scrolling: Any

    def _create_action(
        self,
        text: str,
        status_tip: str,
        triggered: Any,
        shortcut: Any | None = None,
        checkable: bool = False,
        checked: bool = False,
    ) -> QAction:  # pragma: no cover
        """Create action helper."""
        ...


class ActionCreators:
    """
    Creates all QAction instances for application menus.

    This class was extracted from ActionManager to reduce class size
    per MA principle (833→~536 lines).

    Contains 13 action creator methods:
    - File actions (11): New, Open, Save, Save As, Export formats, Exit
    - Edit actions (6): Undo, Redo, Cut, Copy, Paste, Convert Paste
    - Find actions (4): Find, Replace, Find Next, Find Previous
    - View actions (7): Zoom in/out/reset, Dark mode, Sync scroll, Maximize
    - Git actions (4): Set repo, Commit, Pull, Push
    - GitHub actions (5): Create PR/Issue, List PRs/Issues, View repo
    - Tools actions (12): Spell check, validation, service settings, etc.
    - Help actions (1): About
    """

    def __init__(self, parent: ActionManagerContext) -> None:
        """
        Initialize action creators.

        Args:
            parent: ActionManager instance for accessing window/editor/factory
        """
        self.parent = parent

    def create_file_actions(self) -> None:
        """Create File menu actions (11 actions)."""
        self.parent.new_act = self.parent._create_action(
            "&New", "Create a new file", self.parent.window.new_file, shortcut=QKeySequence.StandardKey.New
        )
        self.parent.new_from_template_act = self.parent._create_action(
            "New from &Template...", "Create a new document from a template", self.parent.window.new_from_template
        )
        self.parent.open_act = self.parent._create_action(
            "&Open...", "Open a file", self.parent.window.open_file, shortcut=QKeySequence.StandardKey.Open
        )
        self.parent.save_act = self.parent._create_action(
            "&Save",
            "Save the document as AsciiDoc format (.adoc)",
            self.parent.window.save_file,
            shortcut=QKeySequence.StandardKey.Save,
        )
        self.parent.save_as_act = self.parent._create_action(
            "Save &As...",
            "Save with a new name",
            lambda: self.parent.window.save_file(save_as=True),
            shortcut=QKeySequence.StandardKey.SaveAs,
        )
        self.parent.save_as_adoc_act = self.parent._create_action(
            "AsciiDoc (*.adoc)", "Save as AsciiDoc file", lambda: self.parent.window.save_file_as_format("adoc")
        )
        self.parent.save_as_md_act = self.parent._create_action(
            "GitHub Markdown (*.md)",
            "Export to GitHub Markdown format",
            lambda: self.parent.window.save_file_as_format("md"),
        )
        self.parent.save_as_docx_act = self.parent._create_action(
            "Microsoft Word (*.docx)",
            "Export to Microsoft Office 365 Word format",
            lambda: self.parent.window.save_file_as_format("docx"),
        )
        self.parent.save_as_html_act = self.parent._create_action(
            "HTML Web Page (*.html)",
            "Export to HTML format (can print to PDF from browser)",
            lambda: self.parent.window.save_file_as_format("html"),
        )
        self.parent.save_as_pdf_act = self.parent._create_action(
            "Adobe PDF (*.pdf)",
            "Export to Adobe Acrobat PDF format",
            lambda: self.parent.window.save_file_as_format("pdf"),
        )
        self.parent.exit_act = self.parent._create_action(
            "E&xit", "Exit the application", self.parent.window.close, shortcut=QKeySequence.StandardKey.Quit
        )

    def create_edit_actions(self) -> None:
        """Create Edit menu actions (6 actions)."""
        self.parent.undo_act = self.parent._create_action(
            "&Undo", "Undo last action", self.parent.editor.undo, shortcut=QKeySequence.StandardKey.Undo
        )
        self.parent.redo_act = self.parent._create_action(
            "&Redo", "Redo last action", self.parent.editor.redo, shortcut=QKeySequence.StandardKey.Redo
        )
        self.parent.cut_act = self.parent._create_action(
            "Cu&t", "Cut selection", self.parent.editor.cut, shortcut=QKeySequence.StandardKey.Cut
        )
        self.parent.copy_act = self.parent._create_action(
            "&Copy", "Copy selection", self.parent.editor.copy, shortcut=QKeySequence.StandardKey.Copy
        )
        self.parent.paste_act = self.parent._create_action(
            "&Paste", "Paste from clipboard", self.parent.editor.paste, shortcut=QKeySequence.StandardKey.Paste
        )
        self.parent.convert_paste_act = self.parent._create_action(
            "Convert && Paste",
            "Convert clipboard content to AsciiDoc",
            self.parent.window.convert_and_paste_from_clipboard,
            shortcut="Ctrl+Shift+V",
        )

    def create_find_actions(self) -> None:
        """Create Find & Replace actions (4 actions)."""
        self.parent.find_act = self.parent._create_action(
            "&Find...",
            "Find text in document",
            lambda: self.parent.window.find_bar.show_and_focus(),
            shortcut=QKeySequence.StandardKey.Find,
        )
        self.parent.replace_act = self.parent._create_action(
            "R&eplace...",
            "Find and replace text",
            lambda: self.parent.window.find_bar.show_replace_and_focus(),
            shortcut=QKeySequence.StandardKey.Replace,
        )
        self.parent.find_next_act = self.parent._create_action(
            "Find &Next",
            "Find next occurrence",
            self.parent.window._handle_find_next,
            shortcut=QKeySequence.StandardKey.FindNext,
        )
        self.parent.find_previous_act = self.parent._create_action(
            "Find &Previous",
            "Find previous occurrence",
            self.parent.window._handle_find_previous,
            shortcut=QKeySequence.StandardKey.FindPrevious,
        )

    def create_view_actions(self) -> None:
        """Create View menu actions (8 actions)."""
        self.parent.zoom_in_act = self.parent._create_action(
            "Zoom &In",
            "Zoom in editor and preview (make text larger)",
            lambda: self.parent.window._zoom(1),
            shortcut=QKeySequence.StandardKey.ZoomIn,
        )
        self.parent.zoom_out_act = self.parent._create_action(
            "Zoom &Out",
            "Zoom out editor and preview (make text smaller)",
            lambda: self.parent.window._zoom(-1),
            shortcut=QKeySequence.StandardKey.ZoomOut,
        )
        self.parent.zoom_reset_act = self.parent._create_action(
            "&Reset Zoom", "Reset zoom to 100% (normal size)", lambda: self.parent.window._zoom(0)
        )
        self.parent.dark_mode_act = self.parent._create_action(
            "&Toggle Dark Mode",
            "Switch between light and dark themes",
            self.parent.window._toggle_dark_mode,
            shortcut="F11",
        )
        self.parent.sync_scrolling_act = self.parent._create_action(
            "Sync &Scrolling",
            "Synchronize scrolling between editor and preview",
            self.parent.window._toggle_sync_scrolling,
            checkable=True,
            checked=self.parent._sync_scrolling,
        )
        self.parent.maximize_window_act = self.parent._create_action(
            "Ma&ximize Window",
            "Maximize the application window",
            self.parent.window._toggle_maximize_window,
        )
        self.parent.maximize_editor_act = self.parent._create_action(
            "&Maximize Editor",
            "Maximize editor pane (hide preview and sidebar)",
            lambda: self.parent.window._toggle_pane_maximize("editor"),
        )
        self.parent.maximize_preview_act = self.parent._create_action(
            "Maximize &Preview",
            "Maximize preview pane (hide editor and sidebar)",
            lambda: self.parent.window._toggle_pane_maximize("preview"),
        )

    def create_git_actions(self) -> None:
        """Create Git menu actions (6 actions)."""
        self.parent.set_repo_act = self.parent._create_action(
            "&Set Repository...",
            "Set the Git repository for version control",
            self.parent.window.git_handler.select_repository,
        )
        self.parent.git_status_act = self.parent._create_action(
            "Git &Status",
            "View current Git repository status",
            self.parent.window._show_git_status,
        )
        self.parent.git_commit_act = self.parent._create_action(
            "&Commit Changes...",
            "Commit changes to Git repository (Ctrl+Shift+G shows dialog)",
            self.parent.window.git_handler.commit_changes,
            shortcut="Ctrl+Shift+G",
        )
        self.parent.quick_commit_act = self.parent._create_action(
            "&Quick Commit...",
            "Quick commit with inline message entry (Ctrl+G)",
            self.parent.window._show_quick_commit,
            shortcut="Ctrl+G",
        )
        self.parent.git_pull_act = self.parent._create_action(
            "&Pull", "Pull latest changes from remote repository", self.parent.window.git_handler.pull_changes
        )
        self.parent.git_push_act = self.parent._create_action(
            "P&ush", "Push local commits to remote repository", self.parent.window.git_handler.push_changes
        )

    def create_github_actions(self) -> None:
        """Create GitHub CLI actions (5 actions)."""
        self.parent.github_create_pr_act = self.parent._create_action(
            "Create &Pull Request...",
            "Create a new GitHub pull request",
            self.parent.window.github_handler.create_pull_request,
        )
        self.parent.github_list_prs_act = self.parent._create_action(
            "&List Pull Requests...",
            "View all GitHub pull requests",
            self.parent.window.github_handler.list_pull_requests,
        )
        self.parent.github_create_issue_act = self.parent._create_action(
            "Create &Issue...", "Create a new GitHub issue", self.parent.window.github_handler.create_issue
        )
        self.parent.github_list_issues_act = self.parent._create_action(
            "List &Issues...", "View all GitHub issues", self.parent.window.github_handler.list_issues
        )
        self.parent.github_repo_info_act = self.parent._create_action(
            "View &Repository...",
            "Open GitHub repository in browser",
            self.parent.window.github_handler.get_repo_info,
        )

    def create_tools_actions(self) -> None:
        """Create Tools menu actions - validation toggle."""
        self.parent.toggle_spell_check_act = self.parent._create_action(
            "&Spell Check (F7)",
            "Toggle spell check highlighting",
            self.parent.window.spell_check_manager.toggle_spell_check,
            shortcut="F7",
            checkable=True,
            checked=self.parent._settings.spell_check_enabled,
        )
        self.parent.validate_install_act = self.parent._create_action(
            "&Validate Installation...",
            "Check all dependencies are properly installed",
            self.parent.window.dialog_manager.show_installation_validator,
        )
        self.parent.performance_dashboard_act = self.parent._create_action(
            "&Performance Dashboard...",
            "View real-time performance metrics and benchmarks",
            self.parent.window.dialog_manager.show_performance_dashboard,
        )
        self.parent.toggle_theme_act = self.parent._create_action(
            "&Toggle Theme",
            "Switch between light and dark themes",
            self.parent.window._toggle_dark_mode,
        )

    def create_validation_settings_actions(self) -> None:
        """
        Create validation settings actions.

        MA principle: Extracted helper (23 lines) - validation configuration actions.
        """
        self.parent.syntax_check_settings_act = self.parent._create_action(
            "Ena&ble Syntax Checking",
            "Enable live AsciiDoc validation (F8 to jump to errors)",
            self.parent.window.show_syntax_check_settings,
            checkable=True,
            checked=self.parent._settings.syntax_check_realtime_enabled,
        )
        self.parent.autocomplete_settings_act = self.parent._create_action(
            "Enable &Auto-complete",
            "Enable syntax auto-completion (Ctrl+Space)",
            self.parent.window.show_autocomplete_settings,
            checkable=True,
            checked=self.parent._settings.autocomplete_enabled,
        )

    def create_service_status_actions(self) -> None:
        """
        Create service status check actions.

        MA principle: Extracted helper (22 lines) - service availability actions.
        """
        self.parent.pandoc_status_act = self.parent._create_action(
            "Check &Pandoc Installation",
            "Verify Pandoc is installed and working (required for format conversion)",
            self.parent.window.dialog_manager.show_pandoc_status,
        )
        self.parent.pandoc_formats_act = self.parent._create_action(
            "Pandoc &Formats...",
            "View supported Pandoc conversion formats",
            self.parent.window.dialog_manager.show_pandoc_status,  # Same dialog shows formats
        )
        self.parent.ollama_status_act = self.parent._create_action(
            "Check &Ollama Service",
            "Verify Ollama AI service is running (optional for AI features)",
            self.parent.window.dialog_manager.show_ollama_status,
        )
        self.parent.anthropic_status_act = self.parent._create_action(
            "Check &Anthropic API",
            "Verify Anthropic Claude API is accessible",
            self.parent.window.dialog_manager.show_anthropic_status,
        )
        self.parent.telemetry_status_act = self.parent._create_action(
            "&Telemetry Status...",
            "View telemetry data collection status",
            self.parent.window.dialog_manager.show_telemetry_status,
        )

    def create_service_settings_actions(self) -> None:
        """
        Create service settings actions.

        MA principle: Extracted helper (13 lines) - service configuration actions.
        """
        self.parent.ollama_settings_act = self.parent._create_action(
            "Ollama &AI Settings...",
            "Configure Ollama AI models for document conversion",
            self.parent.window.dialog_manager.show_ollama_settings,
        )
        # Model browser moved into Ollama Settings dialog (Browse All Models... button)
        self.parent.anthropic_settings_act = self.parent._create_action(
            "&Anthropic AI Settings...",
            "Configure Anthropic Claude API settings",
            self.parent.window.dialog_manager.show_anthropic_settings,
        )

    def create_ui_toggle_actions(self) -> None:
        """
        Create UI toggle actions.

        MA principle: Extracted helper (21 lines) - UI visibility actions.
        Uses lambda to defer chat_manager access (not created during action creation).
        """
        self.parent.toggle_chat_pane_act = self.parent._create_action(
            "Show/Hide &Chat Pane",
            "Toggle visibility of AI chat sidebar",
            lambda: self.parent.window.chat_manager.toggle_panel_visibility(),
            checkable=True,
            checked=self.parent._settings.ai_chat_enabled,
        )
        self.parent.toggle_telemetry_act = self.parent._create_action(
            "&Usage Analytics...",
            "Enable/disable anonymous usage statistics (no personal data)",
            self.parent.window.toggle_telemetry,
        )

    def create_general_settings_actions(self) -> None:
        """
        Create general settings actions.

        MA principle: Extracted helper (11 lines) - general application settings actions.
        """
        self.parent.font_settings_act = self.parent._create_action(
            "&Font Settings...",
            "Customize fonts for editor, preview, and chat panes",
            self.parent.window.dialog_manager.show_font_settings,
        )
        self.parent.app_settings_act = self.parent._create_action(
            "Application &Settings...",
            "View and edit all application settings",
            self.parent.window.dialog_manager.show_app_settings,
        )

    def create_help_actions(self) -> None:
        """Create Help menu actions (2 actions)."""
        self.parent.welcome_guide_act = self.parent._create_action(
            "&Welcome Guide", "Show welcome guide with features and shortcuts", self._show_welcome_guide
        )
        self.parent.about_act = self.parent._create_action(
            "&About", "About AsciiDoctor Artisan", self.parent.window.dialog_manager.show_about
        )

    def _show_welcome_guide(self) -> None:
        """Show welcome guide dialog (Help > Welcome Guide)."""
        if hasattr(self.parent.window, "welcome_manager"):
            self.parent.window.welcome_manager.show_welcome_guide()
