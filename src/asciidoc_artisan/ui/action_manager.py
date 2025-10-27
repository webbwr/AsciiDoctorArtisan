"""
Action Manager - Manage all QAction objects for menu and toolbar integration.

Implements:
- FR-048: Keyboard shortcuts (platform-appropriate)
- FR-053: Complete keyboard shortcut list

This module handles:
- Creating all QAction objects for File, Edit, View, Git, Tools, and Help menus
- Managing action state (enabled/disabled, checked/unchecked)
- Connecting actions to their handler methods
- Creating menu structures

Extracted from main_window.py to improve maintainability and testability.
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtGui import QAction, QKeySequence

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class ActionManager:
    """Handle all QAction creation and menu building."""

    def __init__(self, main_window: "AsciiDocEditor"):
        """
        Initialize ActionManager.

        Args:
            main_window: Main window instance (for signals and methods)
        """
        self.window = main_window
        self.editor = main_window.editor
        self._settings = main_window._settings
        self._sync_scrolling = main_window._sync_scrolling

        # Store all actions as instance variables
        self.new_act: QAction
        self.open_act: QAction
        self.save_act: QAction
        self.save_as_act: QAction
        self.save_as_adoc_act: QAction
        self.save_as_md_act: QAction
        self.save_as_docx_act: QAction
        self.save_as_html_act: QAction
        self.save_as_pdf_act: QAction
        self.exit_act: QAction
        self.undo_act: QAction
        self.redo_act: QAction
        self.cut_act: QAction
        self.copy_act: QAction
        self.paste_act: QAction
        self.convert_paste_act: QAction
        self.preferences_act: QAction
        self.zoom_in_act: QAction
        self.zoom_out_act: QAction
        self.dark_mode_act: QAction
        self.sync_scrolling_act: QAction
        self.maximize_editor_act: QAction
        self.maximize_preview_act: QAction
        self.set_repo_act: QAction
        self.git_commit_act: QAction
        self.git_pull_act: QAction
        self.git_push_act: QAction
        self.pandoc_status_act: QAction
        self.pandoc_formats_act: QAction
        self.ollama_status_act: QAction
        self.ollama_settings_act: QAction
        self.about_act: QAction
        # Grammar actions (v1.3)
        self.grammar_check_act: QAction
        self.grammar_toggle_act: QAction
        self.grammar_next_act: QAction
        self.grammar_ignore_act: QAction

    def create_actions(self) -> None:
        """Create all QAction objects."""
        logger.debug("Creating actions...")

        # File menu actions
        self.new_act = QAction(  # type: ignore[call-overload]
            "&New",
            self.window,
            shortcut=QKeySequence.StandardKey.New,
            statusTip="Create a new file",
            triggered=self.window.new_file,
        )

        self.open_act = QAction(  # type: ignore[call-overload]
            "&Open...",
            self.window,
            shortcut=QKeySequence.StandardKey.Open,
            statusTip="Open a file",
            triggered=self.window.open_file,
        )

        self.save_act = QAction(  # type: ignore[call-overload]
            "&Save",
            self.window,
            shortcut=QKeySequence(QKeySequence.StandardKey.Save),
            statusTip="Save the document as AsciiDoc format (.adoc)",
            triggered=self.window.save_file,
        )

        self.save_as_act = QAction(  # type: ignore[call-overload]
            "Save &As...",
            self.window,
            shortcut=QKeySequence(QKeySequence.StandardKey.SaveAs),
            statusTip="Save with a new name",
            triggered=lambda: self.window.save_file(save_as=True),
        )

        self.save_as_adoc_act = QAction(  # type: ignore[call-overload]
            "AsciiDoc (*.adoc)",
            self.window,
            statusTip="Save as AsciiDoc file",
            triggered=lambda: self.window.save_file_as_format("adoc"),
        )

        self.save_as_md_act = QAction(  # type: ignore[call-overload]
            "GitHub Markdown (*.md)",
            self.window,
            statusTip="Export to GitHub Markdown format",
            triggered=lambda: self.window.save_file_as_format("md"),
        )

        self.save_as_docx_act = QAction(  # type: ignore[call-overload]
            "Microsoft Word (*.docx)",
            self.window,
            statusTip="Export to Microsoft Office 365 Word format",
            triggered=lambda: self.window.save_file_as_format("docx"),
        )

        self.save_as_html_act = QAction(  # type: ignore[call-overload]
            "HTML Web Page (*.html)",
            self.window,
            statusTip="Export to HTML format (can print to PDF from browser)",
            triggered=lambda: self.window.save_file_as_format("html"),
        )

        self.save_as_pdf_act = QAction(  # type: ignore[call-overload]
            "Adobe PDF (*.pdf)",
            self.window,
            statusTip="Export to Adobe Acrobat PDF format",
            triggered=lambda: self.window.save_file_as_format("pdf"),
        )

        self.exit_act = QAction(  # type: ignore[call-overload]
            "E&xit",
            self.window,
            shortcut=QKeySequence.StandardKey.Quit,
            statusTip="Exit the application",
            triggered=self.window.close,
        )

        # Edit menu actions
        self.undo_act = QAction(  # type: ignore[call-overload]
            "&Undo",
            self.window,
            shortcut=QKeySequence.StandardKey.Undo,
            statusTip="Undo last action",
            triggered=self.editor.undo,
        )

        self.redo_act = QAction(  # type: ignore[call-overload]
            "&Redo",
            self.window,
            shortcut=QKeySequence.StandardKey.Redo,
            statusTip="Redo last action",
            triggered=self.editor.redo,
        )

        self.cut_act = QAction(  # type: ignore[call-overload]
            "Cu&t",
            self.window,
            shortcut=QKeySequence.StandardKey.Cut,
            statusTip="Cut selection",
            triggered=self.editor.cut,
        )

        self.copy_act = QAction(  # type: ignore[call-overload]
            "&Copy",
            self.window,
            shortcut=QKeySequence.StandardKey.Copy,
            statusTip="Copy selection",
            triggered=self.editor.copy,
        )

        self.paste_act = QAction(  # type: ignore[call-overload]
            "&Paste",
            self.window,
            shortcut=QKeySequence.StandardKey.Paste,
            statusTip="Paste from clipboard",
            triggered=self.editor.paste,
        )

        self.convert_paste_act = QAction(  # type: ignore[call-overload]
            "Convert && Paste",
            self.window,
            shortcut="Ctrl+Shift+V",
            statusTip="Convert clipboard content to AsciiDoc",
            triggered=self.window.convert_and_paste_from_clipboard,
        )

        self.preferences_act = QAction(  # type: ignore[call-overload]
            "&Preferences...",
            self.window,
            shortcut="Ctrl+,",
            statusTip="Configure application preferences",
            triggered=self.window._show_preferences_dialog,
        )

        # View menu actions
        self.zoom_in_act = QAction(  # type: ignore[call-overload]
            "Zoom &In",
            self.window,
            shortcut=QKeySequence.StandardKey.ZoomIn,
            statusTip="Increase font size",
            triggered=lambda: self.window._zoom(1),
        )

        self.zoom_out_act = QAction(  # type: ignore[call-overload]
            "Zoom &Out",
            self.window,
            shortcut=QKeySequence.StandardKey.ZoomOut,
            statusTip="Decrease font size",
            triggered=lambda: self.window._zoom(-1),
        )

        self.dark_mode_act = QAction(  # type: ignore[call-overload]
            "&Dark Mode",
            self.window,
            checkable=True,
            checked=self._settings.dark_mode,
            statusTip="Toggle dark mode",
            triggered=self.window._toggle_dark_mode,
        )

        self.sync_scrolling_act = QAction(  # type: ignore[call-overload]
            "&Synchronized Scrolling",
            self.window,
            checkable=True,
            checked=self._sync_scrolling,
            statusTip="Toggle synchronized scrolling between editor and preview",
            triggered=self.window._toggle_sync_scrolling,
        )

        self.maximize_editor_act = QAction(  # type: ignore[call-overload]
            "Maximize &Editor",
            self.window,
            shortcut="Ctrl+Shift+E",
            statusTip="Toggle maximize editor pane",
            triggered=lambda: self.window._toggle_pane_maximize("editor"),
        )

        self.maximize_preview_act = QAction(  # type: ignore[call-overload]
            "Maximize &Preview",
            self.window,
            shortcut="Ctrl+Shift+R",
            statusTip="Toggle maximize preview pane",
            triggered=lambda: self.window._toggle_pane_maximize("preview"),
        )

        # Git menu actions
        self.set_repo_act = QAction(  # type: ignore[call-overload]
            "Set &Repository...",
            self.window,
            statusTip="Select Git repository",
            triggered=self.window._select_git_repository,
        )

        self.git_commit_act = QAction(  # type: ignore[call-overload]
            "&Commit...",
            self.window,
            shortcut="Ctrl+Shift+C",
            statusTip="Commit changes",
            triggered=self.window._trigger_git_commit,
        )

        self.git_pull_act = QAction(  # type: ignore[call-overload]
            "&Pull",
            self.window,
            shortcut="Ctrl+Shift+P",
            statusTip="Pull from remote",
            triggered=self.window._trigger_git_pull,
        )

        self.git_push_act = QAction(  # type: ignore[call-overload]
            "P&ush",
            self.window,
            shortcut="Ctrl+Shift+U",
            statusTip="Push to remote",
            triggered=self.window._trigger_git_push,
        )

        # Tools menu actions
        self.pandoc_status_act = QAction(  # type: ignore[call-overload]
            "&Pandoc Status",
            self.window,
            statusTip="Check Pandoc installation status",
            triggered=self.window._show_pandoc_status,
        )

        self.pandoc_formats_act = QAction(  # type: ignore[call-overload]
            "Supported &Formats",
            self.window,
            statusTip="Show supported conversion formats",
            triggered=self.window._show_supported_formats,
        )

        self.ollama_status_act = QAction(  # type: ignore[call-overload]
            "&Ollama Status",
            self.window,
            statusTip="Check Ollama service and installation status",
            triggered=self.window._show_ollama_status,
        )

        self.ollama_settings_act = QAction(  # type: ignore[call-overload]
            "&Settings...",
            self.window,
            statusTip="Configure Ollama AI integration and select model",
            triggered=self.window._show_ollama_settings,
        )

        # Grammar menu actions (v1.3: Legendary Grammar System)
        self.grammar_check_act = QAction(  # type: ignore[call-overload]
            "&Check Grammar Now",
            self.window,
            shortcut="F7",
            statusTip="Run grammar check on current document",
            triggered=self.window.grammar_manager.check_now,
        )

        self.grammar_toggle_act = QAction(  # type: ignore[call-overload]
            "&Auto-Check",
            self.window,
            statusTip="Toggle automatic grammar checking",
            checkable=True,
            checked=True,
            triggered=self.window.grammar_manager.toggle_auto_check,
        )

        self.grammar_next_act = QAction(  # type: ignore[call-overload]
            "&Next Issue",
            self.window,
            shortcut="Ctrl+.",
            statusTip="Navigate to next grammar issue",
            triggered=self.window.grammar_manager.navigate_to_next_issue,
        )

        self.grammar_ignore_act = QAction(  # type: ignore[call-overload]
            "&Ignore Suggestion",
            self.window,
            shortcut="Ctrl+I",
            statusTip="Ignore current grammar suggestion",
            triggered=self.window.grammar_manager.ignore_current_suggestion,
        )

        # Help menu actions
        self.about_act = QAction(  # type: ignore[call-overload]
            "&About",
            self.window,
            statusTip="About AsciiDoctor Artisan",
            triggered=self.window._show_about,
        )

        logger.debug("Actions created successfully")

    def create_menus(self) -> None:
        """Build menu structure with all actions."""
        logger.debug("Creating menus...")
        menubar = self.window.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_act)
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

        # Edit menu
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
        edit_menu.addAction(self.preferences_act)

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.zoom_in_act)
        view_menu.addAction(self.zoom_out_act)
        view_menu.addSeparator()
        view_menu.addAction(self.dark_mode_act)
        view_menu.addAction(self.sync_scrolling_act)
        view_menu.addSeparator()
        view_menu.addAction(self.maximize_editor_act)
        view_menu.addAction(self.maximize_preview_act)

        # Git menu
        git_menu = menubar.addMenu("&Git")
        git_menu.addAction(self.set_repo_act)
        git_menu.addSeparator()
        git_menu.addAction(self.git_commit_act)
        git_menu.addAction(self.git_pull_act)
        git_menu.addAction(self.git_push_act)

        # Grammar menu (v1.3: Legendary Grammar System)
        grammar_menu = menubar.addMenu("&Grammar")
        grammar_menu.addAction(self.grammar_check_act)
        grammar_menu.addAction(self.grammar_toggle_act)
        grammar_menu.addSeparator()
        grammar_menu.addAction(self.grammar_next_act)
        grammar_menu.addAction(self.grammar_ignore_act)

        # Tools menu (sorted alphabetically)
        tools_menu = menubar.addMenu("&Tools")

        # AI Status submenu
        ai_status_menu = tools_menu.addMenu("&AI Status")
        ai_status_menu.addAction(self.ollama_status_act)
        ai_status_menu.addAction(self.ollama_settings_act)

        # Pandoc items
        tools_menu.addAction(self.pandoc_status_act)
        tools_menu.addAction(self.pandoc_formats_act)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.about_act)

        logger.debug("Menus created successfully")
