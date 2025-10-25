"""
Action Manager - Manage application menu actions.

This module creates and manages all QAction objects for the application:
- File actions (New, Open, Save, Export)
- Edit actions (Undo, Redo, Cut, Copy, Paste)
- View actions (Zoom, Dark Mode, Sync Scrolling)
- Git actions (Commit, Pull, Push)
- Help actions (About, Formats, AI Setup)

Extracted from main_window.py to improve maintainability.
Splits the massive 240-line _create_actions() function into focused methods.
"""

import logging
from typing import Dict

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow

logger = logging.getLogger(__name__)


class ActionManager:
    """Manage all application actions."""

    def __init__(self, main_window: QMainWindow):
        """
        Initialize ActionManager.

        Args:
            main_window: Main window for action creation and connections
        """
        self.window = main_window
        self.actions: Dict[str, QAction] = {}

    def create_all_actions(self) -> None:
        """
        Create all application actions.

        Splits the original 240-line function into focused methods by category.
        """
        self._create_file_actions()
        self._create_edit_actions()
        self._create_view_actions()
        self._create_git_actions()
        self._create_help_actions()

        logger.info(f"Created {len(self.actions)} actions")

    def get_action(self, name: str) -> QAction:
        """
        Get action by name.

        Args:
            name: Action name (without _act suffix)

        Returns:
            QAction object
        """
        return self.actions.get(name)

    def _create_file_actions(self) -> None:
        """Create File menu actions."""
        # New
        self.window.new_act = QAction(
            "&New",
            self.window,
            shortcut=QKeySequence.StandardKey.New,
            statusTip="Create a new file",
            triggered=self.window.new_file,
        )
        self.actions['new'] = self.window.new_act

        # Open
        self.window.open_act = QAction(
            "&Open...",
            self.window,
            shortcut=QKeySequence.StandardKey.Open,
            statusTip="Open a file",
            triggered=self.window.open_file,
        )
        self.actions['open'] = self.window.open_act

        # Save
        self.window.save_act = QAction(
            "&Save",
            self.window,
            shortcut=QKeySequence(QKeySequence.StandardKey.Save),
            statusTip="Save the document as AsciiDoc format (.adoc)",
            triggered=self.window.save_file,
        )
        self.actions['save'] = self.window.save_act

        # Save As
        self.window.save_as_act = QAction(
            "Save &As...",
            self.window,
            shortcut=QKeySequence(QKeySequence.StandardKey.SaveAs),
            statusTip="Save with a new name",
            triggered=lambda: self.window.save_file(save_as=True),
        )
        self.actions['save_as'] = self.window.save_as_act

        # Export submenu actions
        self.window.save_as_adoc_act = QAction(
            "AsciiDoc (*.adoc)",
            self.window,
            statusTip="Save as AsciiDoc file",
            triggered=lambda: self.window.save_file_as_format("adoc"),
        )
        self.actions['save_as_adoc'] = self.window.save_as_adoc_act

        self.window.save_as_md_act = QAction(
            "GitHub Markdown (*.md)",
            self.window,
            statusTip="Export to GitHub Markdown format",
            triggered=lambda: self.window.save_file_as_format("md"),
        )
        self.actions['save_as_md'] = self.window.save_as_md_act

        self.window.save_as_docx_act = QAction(
            "Microsoft Word (*.docx)",
            self.window,
            statusTip="Export to Microsoft Office 365 Word format",
            triggered=lambda: self.window.save_file_as_format("docx"),
        )
        self.actions['save_as_docx'] = self.window.save_as_docx_act

        self.window.save_as_html_act = QAction(
            "HTML Web Page (*.html)",
            self.window,
            statusTip="Export to HTML format (can print to PDF from browser)",
            triggered=lambda: self.window.save_file_as_format("html"),
        )
        self.actions['save_as_html'] = self.window.save_as_html_act

        self.window.save_as_pdf_act = QAction(
            "Adobe PDF (*.pdf)",
            self.window,
            statusTip="Export to Adobe Acrobat PDF format",
            triggered=lambda: self.window.save_file_as_format("pdf"),
        )
        self.actions['save_as_pdf'] = self.window.save_as_pdf_act

        # Exit
        self.window.exit_act = QAction(
            "E&xit",
            self.window,
            shortcut=QKeySequence.StandardKey.Quit,
            statusTip="Exit the application",
            triggered=self.window.close,
        )
        self.actions['exit'] = self.window.exit_act

        logger.debug("Created File actions (10 actions)")

    def _create_edit_actions(self) -> None:
        """Create Edit menu actions."""
        # Undo
        self.window.undo_act = QAction(
            "&Undo",
            self.window,
            shortcut=QKeySequence.StandardKey.Undo,
            statusTip="Undo last action",
            triggered=self.window.editor.undo,
        )
        self.actions['undo'] = self.window.undo_act

        # Redo
        self.window.redo_act = QAction(
            "&Redo",
            self.window,
            shortcut=QKeySequence.StandardKey.Redo,
            statusTip="Redo last action",
            triggered=self.window.editor.redo,
        )
        self.actions['redo'] = self.window.redo_act

        # Cut
        self.window.cut_act = QAction(
            "Cu&t",
            self.window,
            shortcut=QKeySequence.StandardKey.Cut,
            statusTip="Cut selection",
            triggered=self.window.editor.cut,
        )
        self.actions['cut'] = self.window.cut_act

        # Copy
        self.window.copy_act = QAction(
            "&Copy",
            self.window,
            shortcut=QKeySequence.StandardKey.Copy,
            statusTip="Copy selection",
            triggered=self.window.editor.copy,
        )
        self.actions['copy'] = self.window.copy_act

        # Paste
        self.window.paste_act = QAction(
            "&Paste",
            self.window,
            shortcut=QKeySequence.StandardKey.Paste,
            statusTip="Paste from clipboard",
            triggered=self.window.editor.paste,
        )
        self.actions['paste'] = self.window.paste_act

        # Convert and Paste
        self.window.convert_paste_act = QAction(
            "Convert && Paste",
            self.window,
            shortcut="Ctrl+Shift+V",
            statusTip="Convert clipboard content to AsciiDoc and paste",
            triggered=self.window.convert_and_paste_from_clipboard,
        )
        self.actions['convert_paste'] = self.window.convert_paste_act

        logger.debug("Created Edit actions (6 actions)")

    def _create_view_actions(self) -> None:
        """Create View menu actions."""
        # Zoom In
        self.window.zoom_in_act = QAction(
            "Zoom &In",
            self.window,
            shortcut=QKeySequence.StandardKey.ZoomIn,
            statusTip="Increase font size",
            triggered=lambda: self.window._zoom(1),
        )
        self.actions['zoom_in'] = self.window.zoom_in_act

        # Zoom Out
        self.window.zoom_out_act = QAction(
            "Zoom &Out",
            self.window,
            shortcut=QKeySequence.StandardKey.ZoomOut,
            statusTip="Decrease font size",
            triggered=lambda: self.window._zoom(-1),
        )
        self.actions['zoom_out'] = self.window.zoom_out_act

        # Toggle Dark Mode
        self.window.dark_mode_act = QAction(
            "Dark &Mode",
            self.window,
            statusTip="Toggle dark mode",
            triggered=self.window._toggle_dark_mode,
            checkable=True,
        )
        self.actions['dark_mode'] = self.window.dark_mode_act

        # Toggle Sync Scrolling
        self.window.sync_scrolling_act = QAction(
            "&Sync Scrolling",
            self.window,
            statusTip="Toggle synchronized scrolling between editor and preview",
            triggered=self.window._toggle_sync_scrolling,
            checkable=True,
        )
        self.window.sync_scrolling_act.setChecked(True)
        self.actions['sync_scrolling'] = self.window.sync_scrolling_act

        # Maximize Editor
        self.window.maximize_editor_act = QAction(
            "Maximize &Editor",
            self.window,
            shortcut="Ctrl+E",
            statusTip="Maximize editor pane",
            triggered=lambda: self.window._maximize_pane("editor"),
        )
        self.actions['maximize_editor'] = self.window.maximize_editor_act

        # Maximize Preview
        self.window.maximize_preview_act = QAction(
            "Maximize &Preview",
            self.window,
            shortcut="Ctrl+P",
            statusTip="Maximize preview pane",
            triggered=lambda: self.window._maximize_pane("preview"),
        )
        self.actions['maximize_preview'] = self.window.maximize_preview_act

        logger.debug("Created View actions (6 actions)")

    def _create_git_actions(self) -> None:
        """Create Git menu actions."""
        # Git Commit
        self.window.git_commit_act = QAction(
            "&Commit...",
            self.window,
            shortcut="Ctrl+G",
            statusTip="Commit changes to Git",
            triggered=self.window._trigger_git_commit,
        )
        self.actions['git_commit'] = self.window.git_commit_act

        # Git Pull
        self.window.git_pull_act = QAction(
            "&Pull",
            self.window,
            statusTip="Pull from remote repository",
            triggered=self.window._trigger_git_pull,
        )
        self.actions['git_pull'] = self.window.git_pull_act

        # Git Push
        self.window.git_push_act = QAction(
            "P&ush",
            self.window,
            statusTip="Push to remote repository",
            triggered=self.window._trigger_git_push,
        )
        self.actions['git_push'] = self.window.git_push_act

        logger.debug("Created Git actions (3 actions)")

    def _create_help_actions(self) -> None:
        """Create Help menu actions."""
        # Supported Formats
        self.window.pandoc_formats_act = QAction(
            "Supported &Formats",
            self.window,
            statusTip="Show supported import/export formats",
            triggered=self.window._show_supported_formats,
        )
        self.actions['pandoc_formats'] = self.window.pandoc_formats_act

        # AI Setup Help
        self.window.ai_setup_help_act = QAction(
            "&AI Setup Help",
            self.window,
            statusTip="Show help for setting up AI assistant",
            triggered=self.window._show_ai_setup_help,
        )
        self.actions['ai_setup_help'] = self.window.ai_setup_help_act

        # About
        self.window.about_act = QAction(
            "&About",
            self.window,
            statusTip="About AsciiDoc Artisan",
            triggered=self.window._show_about,
        )
        self.actions['about'] = self.window.about_act

        logger.debug("Created Help actions (3 actions)")

    def enable_action(self, name: str, enabled: bool) -> None:
        """
        Enable or disable an action.

        Args:
            name: Action name (without _act suffix)
            enabled: True to enable, False to disable
        """
        action = self.get_action(name)
        if action:
            action.setEnabled(enabled)

    def get_all_actions(self) -> Dict[str, QAction]:
        """Get all actions as a dictionary."""
        return self.actions.copy()
