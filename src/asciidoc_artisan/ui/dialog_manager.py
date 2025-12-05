"""
Dialog Manager - Handles all application dialogs.

Implements:
- Pandoc status dialog
- Supported formats dialog
- Ollama status and settings dialogs
- Message boxes (info, warning, critical)
- Preferences dialog
- About dialog
- Save confirmation dialog

Extracted from main_window.py as part of Phase 6 refactoring to reduce
main window complexity and improve modularity.
"""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox, QProgressDialog

from asciidoc_artisan.core import LARGE_FILE_THRESHOLD_BYTES, MSG_LOADING_LARGE_FILE

# Lazy imports for dialogs - improves startup by ~0.4s
# Note: Import inside methods to defer heavy dependencies (anthropic SDK = 0.32s)
from asciidoc_artisan.ui.status_dialog_builder import StatusDialogBuilder
from asciidoc_artisan.ui.telemetry_dialog_handler import TelemetryDialogHandler

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class DialogManager:
    """Manages all application dialogs and message boxes.

    This class encapsulates all dialog-related functionality for the main
    editor window, including status dialogs, settings dialogs, and message boxes.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the DialogManager with a reference to the main editor."""
        self.editor = editor
        self._status_builder = StatusDialogBuilder(editor)
        self._telemetry_handler = TelemetryDialogHandler(editor)

    def show_installation_validator(self) -> None:
        """Show installation validator dialog."""
        from asciidoc_artisan.ui.installation_validator_dialog import InstallationValidatorDialog

        dialog = InstallationValidatorDialog(self.editor)
        dialog.exec()

    def show_performance_dashboard(self) -> None:
        """Show performance benchmarking dashboard."""
        from asciidoc_artisan.ui.performance_dashboard import PerformanceDashboard

        dialog = PerformanceDashboard(self.editor)
        dialog.exec()

    def show_pandoc_status(self) -> None:
        """Show pandoc status (delegates to status_dialog_builder)."""
        self._status_builder.show_pandoc_status()

    def show_supported_formats(self) -> None:
        """Show supported formats (delegates to status_dialog_builder)."""
        self._status_builder.show_supported_formats()

    def show_ollama_status(self) -> None:
        """Show Ollama status (delegates to status_dialog_builder)."""
        self._status_builder.show_ollama_status()

    def show_anthropic_status(self) -> None:
        """Show Anthropic status (delegates to status_dialog_builder)."""
        self._status_builder.show_anthropic_status()

    def show_telemetry_status(self) -> None:
        """Show telemetry status (delegates to telemetry_dialog_handler)."""
        self._telemetry_handler.show_telemetry_status()

    def show_ollama_settings(self) -> None:
        """Show Ollama AI settings dialog with model selection."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        # Show dialog and wait for user response.
        dialog = OllamaSettingsDialog(self.editor._settings, self.editor)
        if dialog.exec():
            # User clicked OK so get updated settings.
            self.editor._settings = dialog.get_settings()
            # Save to disk immediately.
            self.editor._settings_manager.save_settings(
                self.editor._settings, self.editor, self.editor._current_file_path
            )

            # Refresh status bar to show new model.
            self.editor._update_ai_status_bar()

            # Tell worker thread about new config.
            self.editor.pandoc_worker.set_ollama_config(
                self.editor._settings.ollama_enabled, self.editor._settings.ollama_model
            )

            # Keep chat manager in sync with new settings.
            self.editor.chat_manager.update_settings(self.editor._settings)

            logger.info(
                f"Ollama settings updated: enabled={self.editor._settings.ollama_enabled}, "
                f"model={self.editor._settings.ollama_model}, "
                f"chat_enabled={self.editor._settings.ollama_chat_enabled}"
            )

    def show_anthropic_settings(self) -> None:
        """Show Anthropic API key configuration dialog."""
        from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog

        # Show API key configuration dialog.
        dialog = APIKeySetupDialog(self.editor)
        dialog.exec()  # Modal dialog - wait for user to close it

    def show_app_settings(self) -> None:
        """Show application settings editor dialog."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        dialog = SettingsEditorDialog(self.editor._settings, self.editor._settings_manager, self.editor)
        if dialog.exec():
            # Settings are saved automatically in the dialog
            # Just refresh the UI from the updated settings
            self.editor._refresh_from_settings()
            logger.info("Application settings updated via settings editor")

    def show_font_settings(self) -> None:
        """Show font settings dialog."""
        from asciidoc_artisan.ui.dialogs import FontSettingsDialog

        dialog = FontSettingsDialog(self.editor._settings, self.editor)
        if dialog.exec():
            # Get updated settings
            updated_settings = dialog.get_settings()
            self.editor._settings = updated_settings

            # Save settings
            self.editor._settings_manager.save_settings(updated_settings, self.editor)

            # Apply fonts to all panes
            self._apply_font_settings()

            logger.info(
                f"Font settings updated: editor={updated_settings.editor_font_family} "
                f"{updated_settings.editor_font_size}pt, "
                f"preview={updated_settings.preview_font_family} "
                f"{updated_settings.preview_font_size}pt, "
                f"chat={updated_settings.chat_font_family} "
                f"{updated_settings.chat_font_size}pt"
            )

    def _apply_font_settings(self) -> None:
        """Apply font settings to editor, preview, and chat panes."""
        settings = self.editor._settings

        # Set font for editor widget.
        editor_font = QFont(settings.editor_font_family, settings.editor_font_size)
        self.editor.editor.setFont(editor_font)
        logger.debug(f"Applied editor font: {settings.editor_font_family} {settings.editor_font_size}pt")

        # Set font for preview via CSS injection.
        preview_css = f"""
        body {{
            font-family: '{settings.preview_font_family}', sans-serif;
            font-size: {settings.preview_font_size}pt;
        }}
        """
        if hasattr(self.editor, "preview_handler") and self.editor.preview_handler:
            # Inject CSS into preview widget.
            self.editor.preview_handler.set_custom_css(preview_css)
            logger.debug(f"Applied preview font: {settings.preview_font_family} {settings.preview_font_size}pt")

        # Set font for chat panel if AI is enabled.
        if hasattr(self.editor, "chat_manager") and self.editor.chat_manager:
            chat_font = QFont(settings.chat_font_family, settings.chat_font_size)
            # Check if chat panel exists before setting font.
            if hasattr(self.editor.chat_manager, "chat_panel") and self.editor.chat_manager.chat_panel:
                self.editor.chat_manager.chat_panel.setFont(chat_font)
                logger.debug(f"Applied chat font: {settings.chat_font_family} {settings.chat_font_size}pt")

    def show_message(self, level: str, title: str, text: str) -> None:
        """
        Show a message box with the specified level, title, and text.

        Args:
            level: Message level ("info", "warning", "critical")
            title: Dialog title
            text: Message text
        """
        icon_map = {
            "info": QMessageBox.Icon.Information,
            "warning": QMessageBox.Icon.Warning,
            "critical": QMessageBox.Icon.Critical,
        }

        msg = QMessageBox(self.editor)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon_map.get(level, QMessageBox.Icon.Information))
        msg.exec()

    def prompt_save_before_action(self, action: str) -> bool:
        """
        Prompt user to save unsaved changes before performing an action.

        Args:
            action: Description of the action about to be performed

        Returns:
            True if should proceed with action, False if cancelled
        """
        # Auto-continue in tests to prevent blocking.
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return True

        # Nothing to save so just continue.
        if not self.editor._unsaved_changes:
            return True

        # Ask user what to do with unsaved changes.
        reply = QMessageBox.question(
            self.editor,
            "Unsaved Changes",
            f"Save changes before {action}?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
        )

        if reply == QMessageBox.StandardButton.Save:
            # User wants to save first.
            return self.editor.save_file()  # type: ignore[no-any-return]  # save_file returns bool but QMessageBox comparison typed as Any
        elif reply == QMessageBox.StandardButton.Discard:
            # User wants to continue without saving.
            return True
        else:
            # User cancelled the action.
            return False

    def show_about(self) -> None:
        """Show about dialog."""
        about_text = """
        <h2>AsciiDoctor Artisan</h2>
        <p><b>Version:</b> 1.1.0</p>
        <p><b>Description:</b> A unified, distraction-free environment for AsciiDoc authoring with live preview.</p>

        <h3>Features</h3>
        <ul>
            <li>Real-time AsciiDoc preview</li>
            <li>Git integration for version control</li>
            <li>Multi-format export (Markdown, DOCX, HTML, PDF)</li>
            <li>AI-enhanced document conversion (optional)</li>
            <li>Dark mode support</li>
            <li>Auto-save functionality</li>
        </ul>

        <h3>Technology Stack</h3>
        <ul>
            <li>Python + PySide6 (Qt)</li>
            <li>asciidoc3 for rendering</li>
            <li>Pandoc for format conversion</li>
            <li>Claude AI for enhanced conversions (optional)</li>
        </ul>

        <p><b>License:</b> Open Source</p>
        <p><b>Documentation:</b> See Help menu for AI setup and usage guides</p>
        """

        msg = QMessageBox(self.editor)
        msg.setWindowTitle("About AsciiDoctor Artisan")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    # === FILE LOAD OPERATIONS (merged from FileLoadManager) ===

    def load_content_into_editor(self, content: str, file_path: Path) -> None:
        """Load content into editor with lazy loading for large files.

        MA principle: Merged from FileLoadManager for consolidated dialog/progress handling.

        Args:
            content: File content to load
            file_path: Path to the file being loaded
        """
        self.editor._is_opening_file = True
        try:
            # Disable preview updates temporarily for large files
            content_size = len(content)
            is_large_file = content_size > LARGE_FILE_THRESHOLD_BYTES

            if is_large_file:
                logger.info(MSG_LOADING_LARGE_FILE.format(content_size / 1024))

            # QPlainTextEdit handles large documents efficiently with internal lazy loading
            # It only renders visible blocks, so setPlainText is still fast
            self.editor.editor.setPlainText(content)
            self.editor._current_file_path = file_path
            self.editor._unsaved_changes = False
            self.editor.status_manager.update_window_title()

            # Update document metrics after loading content
            self.editor.status_manager.update_document_metrics()

            if file_path.suffix.lower() in [
                ".md",
                ".markdown",
                ".docx",
                ".html",
                ".htm",
                ".tex",
                ".rst",
                ".org",
                ".textile",
            ]:
                self.editor.status_bar.showMessage(f"Converted and opened: {file_path} → AsciiDoc")
            else:
                self.editor.status_bar.showMessage(f"Opened: {file_path}")

            # Trigger preview update (will be optimized based on file size)
            self.editor.update_preview()

            logger.info(f"Loaded content into editor: {file_path}")
        finally:
            self.editor._is_opening_file = False

    @Slot(int, str)
    def on_file_load_progress(self, percentage: int, message: str) -> None:
        """Handle file loading progress updates with visual progress dialog.

        MA principle: Merged from FileLoadManager - progress dialogs belong with other dialogs.

        Args:
            percentage: Load progress percentage (0-100)
            message: Progress message to display
        """
        # Create progress dialog on first progress update
        if percentage > 0 and percentage < 100:
            if self.editor._progress_dialog is None:
                self.editor._progress_dialog = QProgressDialog("Loading file...", "Cancel", 0, 100, self.editor)
                self.editor._progress_dialog.setWindowTitle("Loading")
                self.editor._progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
                self.editor._progress_dialog.setMinimumDuration(500)  # Show after 500ms
                self.editor._progress_dialog.setCancelButton(None)  # No cancel button
                self.editor._progress_dialog.setAutoClose(True)
                self.editor._progress_dialog.setAutoReset(True)

            self.editor._progress_dialog.setValue(percentage)
            self.editor._progress_dialog.setLabelText(message)
            logger.debug(f"File load progress: {percentage}% - {message}")

        # Close and cleanup on completion
        elif percentage >= 100:
            if self.editor._progress_dialog is not None:
                self.editor._progress_dialog.setValue(100)
                self.editor._progress_dialog.close()
                self.editor._progress_dialog = None
            self.editor.status_bar.showMessage(message, 3000)
            logger.debug(f"File load complete: {message}")

        # Show in status bar for initial progress
        else:
            self.editor.status_bar.showMessage(message, 2000)
