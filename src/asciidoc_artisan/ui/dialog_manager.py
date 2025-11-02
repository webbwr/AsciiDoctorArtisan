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
import subprocess
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QMessageBox

if TYPE_CHECKING:

    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)

# Check for Pandoc availability
try:
    import pypandoc

    PANDOC_AVAILABLE = True
except ImportError:
    pypandoc = None
    PANDOC_AVAILABLE = False


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

    def show_pandoc_status(self) -> None:
        """Show detailed pandoc installation status."""
        status = "Pandoc Status:\n\n"
        status += f"PANDOC_AVAILABLE: {PANDOC_AVAILABLE}\n"
        status += f"pypandoc module: {'Imported' if pypandoc else 'Not found'}\n"

        if PANDOC_AVAILABLE and pypandoc:
            try:
                # Query pandoc version from system.
                version = pypandoc.get_pandoc_version()
                status += f"Pandoc version: {version}\n"
                # Show where binary is installed.
                path = pypandoc.get_pandoc_path()
                status += f"Pandoc path: {path}\n"
            except Exception as e:
                # Pypandoc exists but cannot talk to pandoc.
                status += f"Error getting pandoc info: {e}\n"

        if not PANDOC_AVAILABLE:
            # Show install instructions if missing.
            status += "\nTo enable document conversion:\n"
            status += "1. Install pandoc from https://pandoc.org\n"
            status += "2. Run: pip install pypandoc"

        self.editor.status_manager.show_message("info", "Pandoc Status", status)

    def show_supported_formats(self) -> None:
        """Show supported input and output formats."""
        if PANDOC_AVAILABLE and pypandoc:
            message = "Supported Conversion Formats:\n\n"
            message += "COMMON INPUT FORMATS:\n"
            message += "  • markdown (.md, .markdown)\n"
            message += "  • docx (Microsoft Word)\n"
            message += "  • html (.html, .htm)\n"
            message += "  • latex (.tex)\n"
            message += "  • rst (reStructuredText)\n"
            message += "  • org (Org Mode)\n"
            message += "\nCOMMON OUTPUT FORMATS:\n"
            message += "  • asciidoc (.adoc)\n"
            message += "  • markdown (.md)\n"
            message += "  • html (.html)\n"
            message += "  • docx (Microsoft Word)\n"
            message += "  • pdf (via PDF engine)\n"
            message += "\nNote: Pandoc supports 40+ formats total.\n"
            message += "See https://pandoc.org for complete list."
            self.editor.status_manager.show_message(
                "info", "Supported Formats", message
            )
        else:
            self.editor.status_manager.show_message(
                "warning",
                "Format Information Unavailable",
                "Pandoc is not properly configured.\n\n"
                "When configured, you can convert between many formats including:\n"
                "• Markdown to AsciiDoc\n"
                "• DOCX to AsciiDoc\n"
                "• HTML to AsciiDoc\n"
                "• And many more...",
            )

    def show_ollama_status(self) -> None:
        """Show Ollama service and installation status."""
        status = "Ollama Status:\n\n"

        # Exit early if user disabled AI in settings.
        if not self.editor._settings.ollama_enabled:
            status += "⚠️ Ollama AI: Disabled in settings\n\n"
            status += "Current conversion method: Pandoc (standard)\n\n"
            status += "To enable Ollama AI:\n"
            status += "1. Go to Tools → AI Status → Settings...\n"
            status += "2. Check 'Enable Ollama AI integration'\n"
            status += "3. Select an AI model\n"
            status += "4. Click OK\n"
            self.editor.status_manager.show_message("info", "Ollama Status", status)
            return

        # AI is enabled so check if service is running.
        status += "✅ Ollama AI: Enabled\n"
        if self.editor._settings.ollama_model:
            status += f"Selected model: {self.editor._settings.ollama_model}\n\n"
        else:
            # Enabled but no model chosen yet.
            status += "⚠️ No model selected\n\n"

        try:
            # Try to import Python client library.
            import ollama

            # Check if service is running.
            try:
                # List models to test connection.
                models = ollama.list()
                status += "✅ Ollama service: Running\n"
                status += "API endpoint: http://127.0.0.1:11434\n"
                status += f"Models installed: {len(models.get('models', []))}\n"

                # Detect GPU for faster inference.
                try:
                    result = subprocess.run(
                        ["nvidia-smi"],
                        capture_output=True,
                        text=True,
                        # Quick timeout to avoid hanging.
                        timeout=2,
                    )
                    if result.returncode == 0:
                        status += "GPU: ✅ NVIDIA GPU detected\n"
                    else:
                        # nvidia-smi failed so no GPU.
                        status += "GPU: ⚠️ Not detected (CPU mode)\n"
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    # nvidia-smi not found or too slow.
                    status += "GPU: ⚠️ Not detected (CPU mode)\n"

            except Exception as e:
                # Library exists but service not running.
                status += "❌ Ollama service: Not running\n"
                status += f"Error: {str(e)}\n\n"
                status += "To start Ollama:\n"
                status += "  Linux/Mac: systemctl start ollama\n"
                status += "  Windows: Start Ollama application\n"

        except ImportError:
            # Python library not installed.
            status += "❌ Ollama Python library not installed\n\n"
            status += "To install:\n"
            status += "  pip install ollama>=0.4.0\n\n"
            status += "To install Ollama itself:\n"
            status += "  Visit: https://ollama.com/download\n"

        self.editor.status_manager.show_message("info", "Ollama Status", status)

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

    def show_app_settings(self) -> None:
        """Show application settings editor dialog."""
        from asciidoc_artisan.ui.dialogs import SettingsEditorDialog

        dialog = SettingsEditorDialog(
            self.editor._settings, self.editor._settings_manager, self.editor
        )
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
        from PySide6.QtGui import QFont

        settings = self.editor._settings

        # Set font for editor widget.
        editor_font = QFont(settings.editor_font_family, settings.editor_font_size)
        self.editor.editor.setFont(editor_font)
        logger.debug(
            f"Applied editor font: {settings.editor_font_family} {settings.editor_font_size}pt"
        )

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
            logger.debug(
                f"Applied preview font: {settings.preview_font_family} {settings.preview_font_size}pt"
            )

        # Set font for chat panel if AI is enabled.
        if hasattr(self.editor, "chat_manager") and self.editor.chat_manager:
            chat_font = QFont(settings.chat_font_family, settings.chat_font_size)
            # Check if chat panel exists before setting font.
            if (
                hasattr(self.editor.chat_manager, "chat_panel")
                and self.editor.chat_manager.chat_panel
            ):
                self.editor.chat_manager.chat_panel.setFont(chat_font)
                logger.debug(
                    f"Applied chat font: {settings.chat_font_family} {settings.chat_font_size}pt"
                )

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
        import os

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
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
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

    def show_preferences_dialog(self) -> None:
        """
        Show preferences dialog for configuring application settings.

        FR-055: AI-Enhanced Conversion option configuration UI
        """
        from asciidoc_artisan.ui.dialogs import PreferencesDialog

        dialog = PreferencesDialog(self.editor._settings, self.editor)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.editor._settings = dialog.get_settings()
            self.editor._settings_manager.save_settings(
                self.editor._settings, self.editor, self.editor._current_file_path
            )
            self.editor.status_bar.showMessage("Preferences updated", 3000)
            logger.info(
                f"AI conversion preference updated: {self.editor._settings.ai_conversion_enabled}"
            )

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
