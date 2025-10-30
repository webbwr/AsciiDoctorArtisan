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
                version = pypandoc.get_pandoc_version()
                status += f"Pandoc version: {version}\n"
                path = pypandoc.get_pandoc_path()
                status += f"Pandoc path: {path}\n"
            except Exception as e:
                status += f"Error getting pandoc info: {e}\n"

        if not PANDOC_AVAILABLE:
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

        # Check if Ollama is enabled in settings
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

        # Ollama is enabled, check service status
        status += "✅ Ollama AI: Enabled\n"
        if self.editor._settings.ollama_model:
            status += f"Selected model: {self.editor._settings.ollama_model}\n\n"
        else:
            status += "⚠️ No model selected\n\n"

        try:
            import ollama

            # Try to connect to Ollama service
            try:
                # Test connection by listing models
                models = ollama.list()
                status += "✅ Ollama service: Running\n"
                status += "API endpoint: http://127.0.0.1:11434\n"
                status += f"Models installed: {len(models.get('models', []))}\n"

                # Check for GPU
                try:
                    result = subprocess.run(
                        ["nvidia-smi"],
                        capture_output=True,
                        text=True,
                        timeout=2,
                    )
                    if result.returncode == 0:
                        status += "GPU: ✅ NVIDIA GPU detected\n"
                    else:
                        status += "GPU: ⚠️ Not detected (CPU mode)\n"
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    status += "GPU: ⚠️ Not detected (CPU mode)\n"

            except Exception as e:
                status += "❌ Ollama service: Not running\n"
                status += f"Error: {str(e)}\n\n"
                status += "To start Ollama:\n"
                status += "  Linux/Mac: systemctl start ollama\n"
                status += "  Windows: Start Ollama application\n"

        except ImportError:
            status += "❌ Ollama Python library not installed\n\n"
            status += "To install:\n"
            status += "  pip install ollama>=0.4.0\n\n"
            status += "To install Ollama itself:\n"
            status += "  Visit: https://ollama.com/download\n"

        self.editor.status_manager.show_message("info", "Ollama Status", status)

    def show_ollama_settings(self) -> None:
        """Show Ollama AI settings dialog with model selection."""
        from asciidoc_artisan.ui.dialogs import OllamaSettingsDialog

        dialog = OllamaSettingsDialog(self.editor._settings, self.editor)
        if dialog.exec():
            self.editor._settings = dialog.get_settings()
            self.editor._settings_manager.save_settings(
                self.editor._settings, self.editor, self.editor._current_file_path
            )

            # Update status bar with model name
            self.editor._update_ai_status_bar()

            # Update PandocWorker with new Ollama configuration
            self.editor.pandoc_worker.set_ollama_config(
                self.editor._settings.ollama_enabled, self.editor._settings.ollama_model
            )

            logger.info(
                f"Ollama settings updated: enabled={self.editor._settings.ollama_enabled}, "
                f"model={self.editor._settings.ollama_model}"
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

        # Skip prompts in test environment to prevent blocking
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return True

        if not self.editor._unsaved_changes:
            return True

        reply = QMessageBox.question(
            self.editor,
            "Unsaved Changes",
            f"Save changes before {action}?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.editor.save_file()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
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
