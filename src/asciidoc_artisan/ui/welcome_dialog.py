"""
Welcome Dialog - First-Run Experience for New Users.

This module provides a welcome dialog shown on first launch to introduce
users to AsciiDoc Artisan features and help them get started quickly.

First-Run Features:
- Key features overview
- Essential keyboard shortcuts
- Option to open sample document
- Quick start guide link
- "Don't show again" checkbox

Part of TASK-119: First-Run Experience (v2.1.0)
"""

import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)

from asciidoc_artisan.ui.dialog_factory import ButtonStyle, StyledButtonFactory

logger = logging.getLogger(__name__)


class WelcomeDialog(QDialog):
    """Welcome dialog for first-run experience.

    This dialog introduces new users to AsciiDoc Artisan with:
    - Overview of key features
    - Essential keyboard shortcuts
    - Option to open sample document
    - Quick start guide link

    Example:
        >>> dialog = WelcomeDialog(parent)
        >>> result = dialog.exec()
        >>> if dialog.open_sample_document():
        ...     # Open the sample document
        ... if dialog.dont_show_again():
        ...     settings.welcome_shown = True

    TASK-119: First-Run Experience (v2.1.0)
    """

    # Dialog result codes
    class Result:
        """Dialog result codes."""

        GET_STARTED = QDialog.DialogCode.Accepted
        CLOSED = QDialog.DialogCode.Rejected

    def __init__(self, parent: Any | None = None) -> None:
        """Initialize the Welcome Dialog.

        Args:
            parent: Parent widget (typically the main window)
        """
        super().__init__(parent)
        self.setWindowTitle("Welcome to AsciiDoc Artisan")
        self.setModal(True)
        self.setMinimumWidth(650)
        self.setMinimumHeight(550)

        self._open_sample = False
        self._dont_show = False
        self._dont_show_checkbox: QCheckBox | None = None
        self._open_sample_checkbox: QCheckBox | None = None
        self._setup_ui()

    def _create_header(self) -> QLabel:
        """Create header label with welcome message.

        Returns:
            Header QLabel with title and subtitle

        MA principle: Extracted from _setup_ui.
        """
        header = QLabel(
            "<h2>Welcome to AsciiDoc Artisan!</h2>"
            "<p>Your professional AsciiDoc editor with live preview, "
            "Git integration, and AI-powered assistance.</p>"
        )
        header.setWordWrap(True)
        return header

    def _create_features_browser(self) -> QTextBrowser:
        """Create features text browser with overview content.

        MA principle: Reduced by extracting HTML content.

        Returns:
            QTextBrowser with HTML content explaining features
        """
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._get_features_html())
        browser.setMinimumHeight(320)
        return browser

    def _get_features_html(self) -> str:
        """Get HTML content with features and shortcuts.

        MA principle: Extracted helper - focused HTML content.

        Returns:
            HTML string with features and keyboard shortcuts
        """
        return """
            <h3>Key Features</h3>
            <ul>
                <li><b>Live Preview</b> - See your document rendered in real-time</li>
                <li><b>Git Integration</b> - Commit, push, pull directly from the editor</li>
                <li><b>AI Assistant</b> - Grammar check, style suggestions, summarization</li>
                <li><b>Multi-Format Export</b> - PDF, HTML, DOCX, EPUB, Markdown</li>
                <li><b>Syntax Highlighting</b> - AsciiDoc-aware editor with autocomplete</li>
                <li><b>Templates</b> - Quick-start with built-in document templates</li>
            </ul>

            <h3>Essential Keyboard Shortcuts</h3>
            <table style="border-collapse: collapse; width: 100%;">
                <tr><td style="padding: 4px;"><b>Ctrl+N</b></td><td>New document</td></tr>
                <tr><td style="padding: 4px;"><b>Ctrl+O</b></td><td>Open file</td></tr>
                <tr><td style="padding: 4px;"><b>Ctrl+S</b></td><td>Save file</td></tr>
                <tr><td style="padding: 4px;"><b>Ctrl+Shift+E</b></td><td>Export document</td></tr>
                <tr><td style="padding: 4px;"><b>Ctrl+P</b></td><td>Toggle preview pane</td></tr>
                <tr><td style="padding: 4px;"><b>Ctrl+G</b></td><td>Open Git panel</td></tr>
                <tr><td style="padding: 4px;"><b>Ctrl+Space</b></td><td>Trigger autocomplete</td></tr>
                <tr><td style="padding: 4px;"><b>F1</b></td><td>Open help / documentation</td></tr>
            </table>

            <h3>Quick Start</h3>
            <ol>
                <li><b>Open a file</b> - Use <code>File > Open</code> or <code>Ctrl+O</code></li>
                <li><b>Start typing</b> - The preview updates automatically</li>
                <li><b>Export</b> - Use <code>File > Export</code> for PDF, HTML, etc.</li>
            </ol>

            <h3>Documentation</h3>
            <p>For the complete user guide and tutorials, visit:</p>
            <ul>
                <li><a href="https://github.com/webbwr/AsciiDocArtisan#readme">README & Quick Start</a></li>
                <li><a href="https://github.com/webbwr/AsciiDocArtisan/blob/main/docs/USER_GUIDE.md">User Guide</a></li>
                <li><a href="https://github.com/webbwr/AsciiDocArtisan/blob/main/docs/KEYBOARD_SHORTCUTS.md">Keyboard Shortcuts Reference</a></li>
            </ul>

            <p><small><i>Tip: You can access this welcome screen anytime from
            <b>Help > Welcome Guide</b>.</i></small></p>
            """

    def _create_get_started_button(self) -> QPushButton:
        """Create 'Get Started' button with primary styling.

        Returns:
            Styled QPushButton for getting started
        """
        btn = StyledButtonFactory.create_primary_button("Get Started")
        btn.clicked.connect(self._get_started)
        return btn

    def _create_close_button(self) -> QPushButton:
        """Create close button with secondary styling.

        Returns:
            Styled QPushButton for closing dialog
        """
        btn = StyledButtonFactory.create_button("Close", ButtonStyle.SECONDARY)
        btn.clicked.connect(self._close_dialog)
        return btn

    def _create_options_layout(self) -> QHBoxLayout:
        """Create options layout with checkboxes.

        Returns:
            QHBoxLayout with sample document and don't show again checkboxes

        MA principle: Extracted from _setup_ui.
        """
        layout = QHBoxLayout()

        # Sample document checkbox
        self._open_sample_checkbox = QCheckBox("Open sample document")
        self._open_sample_checkbox.setToolTip("Open a sample AsciiDoc file to explore features")
        layout.addWidget(self._open_sample_checkbox)

        layout.addStretch()

        # Don't show again checkbox
        self._dont_show_checkbox = QCheckBox("Don't show this again")
        self._dont_show_checkbox.setToolTip("You can access this from Help > Welcome Guide anytime")
        layout.addWidget(self._dont_show_checkbox)

        return layout

    def _create_footer_note(self) -> QLabel:
        """Create footer note label.

        Returns:
            QLabel with centered footer note

        MA principle: Extracted from _setup_ui.
        """
        footer = QLabel(
            "<small><i>AsciiDoc Artisan v2.1.0 - Professional AsciiDoc editing made easy. "
            "Access this welcome screen anytime from Help > Welcome Guide.</i></small>"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setWordWrap(True)
        return footer

    def _setup_ui(self) -> None:
        """Set up the dialog UI components.

        MA principle: Reduced by extracting helper methods.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Add header and features browser
        layout.addWidget(self._create_header())
        layout.addWidget(self._create_features_browser())

        # Add options (checkboxes)
        layout.addLayout(self._create_options_layout())

        # Create button box
        button_box = QDialogButtonBox()
        button_box.addButton(self._create_get_started_button(), QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(self._create_close_button(), QDialogButtonBox.ButtonRole.RejectRole)
        layout.addWidget(button_box)

        # Add footer note
        layout.addWidget(self._create_footer_note())

    def _get_started(self) -> None:
        """User clicked 'Get Started'."""
        logger.info("User clicked Get Started in welcome dialog")
        self._capture_checkbox_states()
        self.done(self.Result.GET_STARTED)

    def _close_dialog(self) -> None:
        """User closed the dialog."""
        logger.info("User closed welcome dialog")
        self._capture_checkbox_states()
        self.done(self.Result.CLOSED)

    def _capture_checkbox_states(self) -> None:
        """Capture checkbox states before closing.

        MA principle: Extracted from button handlers.
        """
        if self._open_sample_checkbox:
            self._open_sample = self._open_sample_checkbox.isChecked()
        if self._dont_show_checkbox:
            self._dont_show = self._dont_show_checkbox.isChecked()

    def open_sample_document(self) -> bool:
        """Check if user wants to open sample document.

        Returns:
            True if user checked 'Open sample document'
        """
        return self._open_sample

    def dont_show_again(self) -> bool:
        """Check if user wants to hide welcome dialog on future launches.

        Returns:
            True if user checked "Don't show this again"
        """
        return self._dont_show

    @staticmethod
    def get_sample_document_path() -> Path | None:
        """Get the path to the sample document.

        Returns:
            Path to sample.adoc if it exists, None otherwise
        """
        # Try multiple locations for sample document
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / "docs" / "sample.adoc",
            Path(__file__).parent.parent.parent.parent / "templates" / "sample.adoc",
            Path.home() / ".config" / "AsciiDocArtisan" / "sample.adoc",
        ]

        for path in possible_paths:
            if path.is_file():
                logger.info(f"Found sample document at: {path}")
                return path

        logger.warning("Sample document not found")
        return None
