"""
Menu Manager - Handles menu and action creation for AsciiDoc Artisan.

This module manages all QAction creation and menu bar setup, extracted from
main_window.py as part of Phase 2 architectural refactoring.

The MenuManager separates UI menu concerns from the main window logic,
making the codebase more modular and maintainable.
"""

from typing import TYPE_CHECKING

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenu

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor


class MenuManager:
    """Manages menu bar and actions for AsciiDoc Artisan.

    This class encapsulates all menu and action creation logic, reducing
    the size and complexity of the main AsciiDocEditor class.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the MenuManager with a reference to the main editor."""
        self.editor = editor

    def create_actions(self) -> None:
        """Create all QAction instances for the application."""
        # File actions
        self.editor.new_act = QAction(  # type: ignore[call-overload]
            "&New",
            self.editor,
            shortcut=QKeySequence.StandardKey.New,
            statusTip="Create a new file",
            triggered=self.editor.new_file,
        )

        self.editor.open_act = QAction(  # type: ignore[call-overload]
            "&Open...",
            self.editor,
            shortcut=QKeySequence.StandardKey.Open,
            statusTip="Open a file",
            triggered=self.editor.open_file,
        )

        self.editor.save_act = QAction(  # type: ignore[call-overload]
            "&Save",
            self.editor,
            shortcut=QKeySequence(QKeySequence.StandardKey.Save),
            statusTip="Save the document as AsciiDoc format (.adoc)",
            triggered=self.editor.save_file,
        )

        self.editor.save_as_act = QAction(  # type: ignore[call-overload]
            "Save &As...",
            self.editor,
            shortcut=QKeySequence(QKeySequence.StandardKey.SaveAs),
            statusTip="Save with a new name",
            triggered=lambda: self.editor.save_file(save_as=True),
        )

        self.editor.save_as_adoc_act = QAction(  # type: ignore[call-overload]
            "AsciiDoc (*.adoc)",
            self.editor,
            statusTip="Save as AsciiDoc file",
            triggered=lambda: self.editor.save_file_as_format("adoc"),
        )

        self.editor.save_as_md_act = QAction(  # type: ignore[call-overload]
            "GitHub Markdown (*.md)",
            self.editor,
            statusTip="Export to GitHub Markdown format",
            triggered=lambda: self.editor.save_file_as_format("md"),
        )

        self.editor.save_as_docx_act = QAction(  # type: ignore[call-overload]
            "Microsoft Word (*.docx)",
            self.editor,
            statusTip="Export to Microsoft Office 365 Word format",
            triggered=lambda: self.editor.save_file_as_format("docx"),
        )

        self.editor.save_as_html_act = QAction(  # type: ignore[call-overload]
            "HTML Web Page (*.html)",
            self.editor,
            statusTip="Export to HTML format (can print to PDF from browser)",
            triggered=lambda: self.editor.save_file_as_format("html"),
        )

        self.editor.save_as_pdf_act = QAction(  # type: ignore[call-overload]
            "Adobe PDF (*.pdf)",
            self.editor,
            statusTip="Export to Adobe Acrobat PDF format",
            triggered=lambda: self.editor.save_file_as_format("pdf"),
        )

        self.editor.exit_act = QAction(  # type: ignore[call-overload]
            "E&xit",
            self.editor,
            shortcut=QKeySequence.StandardKey.Quit,
            statusTip="Exit the application",
            triggered=self.editor.close,
        )

        # Edit actions
        self.editor.undo_act = QAction(  # type: ignore[call-overload]
            "&Undo",
            self.editor,
            shortcut=QKeySequence.StandardKey.Undo,
            statusTip="Undo last action",
            triggered=self.editor.editor.undo,
        )

        self.editor.redo_act = QAction(  # type: ignore[call-overload]
            "&Redo",
            self.editor,
            shortcut=QKeySequence.StandardKey.Redo,
            statusTip="Redo last action",
            triggered=self.editor.editor.redo,
        )

        self.editor.cut_act = QAction(  # type: ignore[call-overload]
            "Cu&t",
            self.editor,
            shortcut=QKeySequence.StandardKey.Cut,
            statusTip="Cut selection",
            triggered=self.editor.editor.cut,
        )

        self.editor.copy_act = QAction(  # type: ignore[call-overload]
            "&Copy",
            self.editor,
            shortcut=QKeySequence.StandardKey.Copy,
            statusTip="Copy selection",
            triggered=self.editor.editor.copy,
        )

        self.editor.paste_act = QAction(  # type: ignore[call-overload]
            "&Paste",
            self.editor,
            shortcut=QKeySequence.StandardKey.Paste,
            statusTip="Paste from clipboard",
            triggered=self.editor.editor.paste,
        )

        self.editor.convert_paste_act = QAction(  # type: ignore[call-overload]
            "Convert && Paste",
            self.editor,
            shortcut="Ctrl+Shift+V",
            statusTip="Convert clipboard content to AsciiDoc",
            triggered=self.editor.convert_and_paste_from_clipboard,
        )

        self.editor.preferences_act = QAction(  # type: ignore[call-overload]
            "&Preferences...",
            self.editor,
            shortcut="Ctrl+,",
            statusTip="Configure application preferences",
            triggered=self.editor._show_preferences_dialog,
        )

        # View actions
        self.editor.zoom_in_act = QAction(  # type: ignore[call-overload]
            "Zoom &In",
            self.editor,
            shortcut=QKeySequence.StandardKey.ZoomIn,
            statusTip="Increase font size",
            triggered=lambda: self.editor._zoom(1),
        )

        self.editor.zoom_out_act = QAction(  # type: ignore[call-overload]
            "Zoom &Out",
            self.editor,
            shortcut=QKeySequence.StandardKey.ZoomOut,
            statusTip="Decrease font size",
            triggered=lambda: self.editor._zoom(-1),
        )

        self.editor.dark_mode_act = QAction(  # type: ignore[call-overload]
            "&Dark Mode",
            self.editor,
            checkable=True,
            checked=self.editor._settings.dark_mode,
            statusTip="Toggle dark mode",
            triggered=self.editor._toggle_dark_mode,
        )

        self.editor.sync_scrolling_act = QAction(  # type: ignore[call-overload]
            "&Synchronized Scrolling",
            self.editor,
            checkable=True,
            checked=self.editor._sync_scrolling,
            statusTip="Toggle synchronized scrolling between editor and preview",
            triggered=self.editor._toggle_sync_scrolling,
        )

        self.editor.maximize_editor_act = QAction(  # type: ignore[call-overload]
            "Maximize &Editor",
            self.editor,
            shortcut="Ctrl+Shift+E",
            statusTip="Toggle maximize editor pane",
            triggered=lambda: self.editor._toggle_pane_maximize("editor"),
        )

        self.editor.maximize_preview_act = QAction(  # type: ignore[call-overload]
            "Maximize &Preview",
            self.editor,
            shortcut="Ctrl+Shift+R",
            statusTip="Toggle maximize preview pane",
            triggered=lambda: self.editor._toggle_pane_maximize("preview"),
        )

        # Git actions
        self.editor.set_repo_act = QAction(  # type: ignore[call-overload]
            "Set &Repository...",
            self.editor,
            statusTip="Select Git repository",
            triggered=self.editor._select_git_repository,
        )

        self.editor.git_commit_act = QAction(  # type: ignore[call-overload]
            "&Commit...",
            self.editor,
            shortcut="Ctrl+Shift+C",
            statusTip="Commit changes",
            triggered=self.editor._trigger_git_commit,
        )

        self.editor.git_pull_act = QAction(  # type: ignore[call-overload]
            "&Pull",
            self.editor,
            shortcut="Ctrl+Shift+P",
            statusTip="Pull from remote",
            triggered=self.editor._trigger_git_pull,
        )

        self.editor.git_push_act = QAction(  # type: ignore[call-overload]
            "P&ush",
            self.editor,
            shortcut="Ctrl+Shift+U",
            statusTip="Push to remote",
            triggered=self.editor._trigger_git_push,
        )

        # Tools actions
        self.editor.pandoc_status_act = QAction(  # type: ignore[call-overload]
            "&Pandoc Status",
            self.editor,
            statusTip="Check Pandoc installation status",
            triggered=self.editor._show_pandoc_status,
        )

        self.editor.pandoc_formats_act = QAction(  # type: ignore[call-overload]
            "Supported &Formats",
            self.editor,
            statusTip="Show supported conversion formats",
            triggered=self.editor._show_supported_formats,
        )

        self.editor.ai_setup_help_act = QAction(  # type: ignore[call-overload]
            "&AI Conversion Setup",
            self.editor,
            statusTip="How to set up AI-enhanced conversion",
            triggered=self.editor._show_ai_setup_help,
        )

        # Help actions
        self.editor.about_act = QAction(  # type: ignore[call-overload]
            "&About",
            self.editor,
            statusTip="About AsciiDoctor Artisan",
            triggered=self.editor._show_about,
        )

    def create_menus(self) -> None:
        """Create and populate the menu bar."""
        menubar = self.editor.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.editor.new_act)
        file_menu.addAction(self.editor.open_act)
        file_menu.addSeparator()
        file_menu.addAction(self.editor.save_act)
        file_menu.addAction(self.editor.save_as_act)

        # Export submenu
        export_menu = QMenu("E&xport As", self.editor)
        export_menu.addAction(self.editor.save_as_adoc_act)
        export_menu.addAction(self.editor.save_as_md_act)
        export_menu.addAction(self.editor.save_as_docx_act)
        export_menu.addAction(self.editor.save_as_html_act)
        export_menu.addAction(self.editor.save_as_pdf_act)
        file_menu.addMenu(export_menu)

        file_menu.addSeparator()
        file_menu.addAction(self.editor.preferences_act)
        file_menu.addSeparator()
        file_menu.addAction(self.editor.exit_act)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.editor.undo_act)
        edit_menu.addAction(self.editor.redo_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.editor.cut_act)
        edit_menu.addAction(self.editor.copy_act)
        edit_menu.addAction(self.editor.paste_act)
        edit_menu.addAction(self.editor.convert_paste_act)

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.editor.zoom_in_act)
        view_menu.addAction(self.editor.zoom_out_act)
        view_menu.addSeparator()
        view_menu.addAction(self.editor.dark_mode_act)
        view_menu.addAction(self.editor.sync_scrolling_act)
        view_menu.addSeparator()
        view_menu.addAction(self.editor.maximize_editor_act)
        view_menu.addAction(self.editor.maximize_preview_act)

        # Git menu
        git_menu = menubar.addMenu("&Git")
        git_menu.addAction(self.editor.set_repo_act)
        git_menu.addSeparator()
        git_menu.addAction(self.editor.git_commit_act)
        git_menu.addAction(self.editor.git_pull_act)
        git_menu.addAction(self.editor.git_push_act)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction(self.editor.pandoc_status_act)
        tools_menu.addAction(self.editor.pandoc_formats_act)
        tools_menu.addSeparator()
        tools_menu.addAction(self.editor.ai_setup_help_act)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.editor.about_act)
