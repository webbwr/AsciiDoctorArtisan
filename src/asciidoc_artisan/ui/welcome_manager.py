"""
Welcome Manager - Handles first-run experience and welcome dialog.

Extracted following the TelemetryManager pattern per MA principle.

First-Run Features:
- Welcome dialog shown on first launch
- Key features overview
- Essential keyboard shortcuts
- Option to open sample document
- "Don't show again" checkbox

Part of TASK-119: First-Run Experience (v2.1.0)
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor
    from asciidoc_artisan.ui.welcome_dialog import WelcomeDialog

logger = logging.getLogger(__name__)


class WelcomeManager:
    """
    Manages first-run welcome dialog and related functionality.

    MA principle: Follows TelemetryManager pattern for consistency.
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize WelcomeManager with reference to main editor.

        Args:
            editor: Main editor window instance
        """
        self.editor = editor

    def initialize(self) -> None:
        """
        Initialize first-run experience.

        Shows welcome dialog on first launch if not already shown.
        """
        settings = self.editor._settings

        # Show welcome dialog on first launch (if not already shown)
        if not settings.welcome_shown:
            # Delay dialog to allow UI to fully initialize (after telemetry)
            QTimer.singleShot(1500, self._show_welcome_dialog)
            logger.info("Welcome dialog scheduled for first-run experience")
        else:
            logger.debug("Welcome dialog already shown, skipping")

    def _show_welcome_dialog(self) -> None:
        """Show welcome dialog (first launch only)."""
        from asciidoc_artisan.ui.welcome_dialog import WelcomeDialog

        dialog = WelcomeDialog(self.editor)
        result = dialog.exec()

        # Handle dialog result
        if result == WelcomeDialog.Result.GET_STARTED:
            self._handle_get_started(dialog)
        else:
            self._handle_closed(dialog)

    def _handle_get_started(self, dialog: "WelcomeDialog") -> None:
        """Handle user clicking 'Get Started'.

        Args:
            dialog: The welcome dialog instance
        """
        from asciidoc_artisan.ui.welcome_dialog import WelcomeDialog

        self._save_dialog_preferences(dialog)

        # Open sample document if requested
        if dialog.open_sample_document():
            sample_path = WelcomeDialog.get_sample_document_path()
            if sample_path and sample_path.is_file():
                self.editor.file_handler.open_file(str(sample_path))
                logger.info(f"Opened sample document: {sample_path}")
            else:
                logger.warning("Sample document not found")

        logger.info("User clicked Get Started in welcome dialog")

    def _handle_closed(self, dialog: "WelcomeDialog") -> None:
        """Handle user closing the dialog.

        Args:
            dialog: The welcome dialog instance
        """
        self._save_dialog_preferences(dialog)
        logger.info("User closed welcome dialog")

    def _save_dialog_preferences(self, dialog: "WelcomeDialog") -> None:
        """Save dialog preferences to settings.

        Args:
            dialog: The welcome dialog instance
        """
        settings = self.editor._settings

        # Always mark as shown after dialog is displayed
        # (unless user unchecked "Don't show again" - but we show by default once)
        if dialog.dont_show_again():
            settings.welcome_shown = True
            logger.info("Welcome dialog marked as 'don't show again'")
        else:
            # Still mark as shown - they saw it once
            # User can re-access via Help > Welcome Guide
            settings.welcome_shown = True
            logger.info("Welcome dialog shown (user can access via Help menu)")

        # Save settings
        self.editor._settings_manager.save_settings(settings, self.editor)

    def show_welcome_guide(self) -> None:
        """Show welcome guide on demand (Help > Welcome Guide).

        This allows users to access the welcome dialog at any time.
        """
        from asciidoc_artisan.ui.welcome_dialog import WelcomeDialog

        dialog = WelcomeDialog(self.editor)
        result = dialog.exec()

        # Handle sample document if requested
        if result == WelcomeDialog.Result.GET_STARTED and dialog.open_sample_document():
            sample_path = WelcomeDialog.get_sample_document_path()
            if sample_path and sample_path.is_file():
                self.editor.file_handler.open_file(str(sample_path))
                logger.info(f"Opened sample document from Help menu: {sample_path}")

        logger.info("Welcome guide shown from Help menu")
