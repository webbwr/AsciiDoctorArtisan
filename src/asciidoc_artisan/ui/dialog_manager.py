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
import platform
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFileDialog, QMessageBox

from asciidoc_artisan.core.constants import is_pandoc_available

# Optional imports - may not be installed
try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import ollama
except ImportError:
    ollama = None

# Claude client (optional)
try:
    from asciidoc_artisan.claude import ClaudeClient
except ImportError:
    ClaudeClient = None

# Application dialogs
# Note: Previously imported locally to avoid circular imports, but moved to module
# level to support @patch decorators in tests. Circular imports are handled via
# lazy initialization in the dialogs themselves.
from asciidoc_artisan.ui.api_key_dialog import APIKeySetupDialog
from asciidoc_artisan.ui.dialogs import (
    FontSettingsDialog,
    OllamaSettingsDialog,
    SettingsEditorDialog,
)
from asciidoc_artisan.ui.installation_validator_dialog import (
    InstallationValidatorDialog,
)
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
        self._telemetry_handler = TelemetryDialogHandler(editor)

    def show_installation_validator(self) -> None:
        """Show installation validator dialog."""
        dialog = InstallationValidatorDialog(self.editor)
        dialog.exec()

    def show_pandoc_status(self) -> None:
        """Show detailed pandoc installation status."""
        status = "Pandoc Status:\n\n"
        pandoc_available = is_pandoc_available()
        status += f"PANDOC_AVAILABLE: {pandoc_available}\n"

        # Lazy import pypandoc only if needed
        pypandoc_module: Any = None
        if pandoc_available:
            try:
                import pypandoc

                pypandoc_module = pypandoc
            except ImportError:
                pass

        status += f"pypandoc module: {'Imported' if pypandoc_module else 'Not found'}\n"

        if pandoc_available and pypandoc_module:
            try:
                # Query pandoc version from system.
                version = pypandoc_module.get_pandoc_version()
                status += f"Pandoc version: {version}\n"
                # Show where binary is installed.
                path = pypandoc_module.get_pandoc_path()
                status += f"Pandoc path: {path}\n"
            except Exception as e:
                # Pypandoc exists but cannot talk to pandoc.
                status += f"Error getting pandoc info: {e}\n"

        if not pandoc_available:
            # Show install instructions if missing.
            status += "\nTo enable document conversion:\n"
            status += "1. Install pandoc from https://pandoc.org\n"
            status += "2. Run: pip install pypandoc"

        self.editor.status_manager.show_message("info", "Pandoc Status", status)

    def show_supported_formats(self) -> None:
        """Show supported input and output formats."""
        if is_pandoc_available():
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
            self.editor.status_manager.show_message("info", "Supported Formats", message)
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

    def _build_disabled_ollama_status(self) -> str:
        """
        Build status message for disabled Ollama.

        MA principle: Extracted from show_ollama_status (8 lines).

        Returns:
            Status message string
        """
        return (
            "⚠️ Ollama AI: Disabled in settings\n\n"
            "Current conversion method: Pandoc (standard)\n\n"
            "To enable Ollama AI:\n"
            "1. Go to Tools → AI Status → Settings...\n"
            "2. Check 'Enable Ollama AI integration'\n"
            "3. Select an AI model\n"
            "4. Click OK\n"
        )

    def _detect_gpu_status(self) -> str:
        """
        Detect GPU availability for Ollama.

        MA principle: Extracted from show_ollama_status (15 lines).

        Returns:
            GPU status message
        """
        try:
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                text=True,
                timeout=2,  # Quick timeout to avoid hanging
            )
            if result.returncode == 0:
                return "GPU: ✅ NVIDIA GPU detected\n"
            else:
                return "GPU: ⚠️ Not detected (CPU mode)\n"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return "GPU: ⚠️ Not detected (CPU mode)\n"

    def _check_ollama_service(self) -> str:
        """
        Check Ollama service status and build message.

        MA principle: Extracted from show_ollama_status (20 lines).

        Returns:
            Service status message

        Raises:
            Exception: If service check fails
        """
        try:
            # List models to test connection
            models = ollama.list()
            status = "✅ Ollama service: Running\n"
            status += "API endpoint: http://127.0.0.1:11434\n"
            status += f"Models installed: {len(models.get('models', []))}\n"
            status += self._detect_gpu_status()
            return status
        except Exception as e:
            # Library exists but service not running
            return (
                "❌ Ollama service: Not running\n"
                f"Error: {str(e)}\n\n"
                "To start Ollama:\n"
                "  Linux/Mac: systemctl start ollama\n"
                "  Windows: Start Ollama application\n"
            )

    def _build_ollama_import_error(self) -> str:
        """
        Build message for missing Ollama library.

        MA principle: Extracted from show_ollama_status (7 lines).

        Returns:
            Import error message
        """
        return (
            "❌ Ollama Python library not installed\n\n"
            "To install:\n"
            "  pip install ollama>=0.4.0\n\n"
            "To install Ollama itself:\n"
            "  Visit: https://ollama.com/download\n"
        )

    def show_ollama_status(self) -> None:
        """
        Show Ollama service and installation status.

        MA principle: Reduced from 73→23 lines by extracting 4 message builders (68% reduction).
        """
        status = "Ollama Status:\n\n"

        # Exit early if user disabled AI in settings
        if not self.editor._settings.ollama_enabled:
            status += self._build_disabled_ollama_status()
            self.editor.status_manager.show_message("info", "Ollama Status", status)
            return

        # AI is enabled - show model selection
        status += "✅ Ollama AI: Enabled\n"
        if self.editor._settings.ollama_model:
            status += f"Selected model: {self.editor._settings.ollama_model}\n\n"
        else:
            status += "⚠️ No model selected\n\n"

        # Check service status
        try:
            if ollama is None:
                raise ImportError("ollama library not installed")
            status += self._check_ollama_service()
        except ImportError:
            status += self._build_ollama_import_error()

        self.editor.status_manager.show_message("info", "Ollama Status", status)

    def _build_sdk_version_status(self) -> str:
        """
        Build SDK version status message.

        MA principle: Extracted from show_anthropic_status (8 lines).

        Returns:
            SDK version status string
        """
        try:
            if anthropic:
                sdk_version = anthropic.__version__
                return f"SDK Version: {sdk_version}\n\n"
            else:
                return "SDK: Not installed\n\n"
        except AttributeError:
            return "SDK Version: Unknown\n\n"

    def _build_no_api_key_message(self) -> str:
        """
        Build message for missing API key configuration.

        MA principle: Extracted from show_anthropic_status (13 lines).

        Returns:
            Configuration instructions string
        """
        message = "⚠️ Anthropic API: No API key configured\n\n"
        message += "To configure Anthropic API key:\n"
        message += "1. Go to Tools → API Key Setup\n"
        message += "2. Enter your Anthropic API key\n"
        message += "3. Click Save\n\n"
        message += "To get an API key:\n"
        message += "  Visit: https://console.anthropic.com/settings/keys\n"
        return message

    def _build_backend_status(self) -> str:
        """
        Build Claude backend status message.

        MA principle: Extracted from show_anthropic_status (8 lines).

        Returns:
            Backend status string
        """
        if self.editor._settings.ai_backend == "claude":
            return "✅ Active backend: Claude (remote)\n"
        else:
            message = "⚠️ Active backend: Ollama (local)\n"
            message += "\nTo switch to Claude:\n"
            message += "1. Disable Ollama in Tools → AI Status → Settings\n"
            message += "2. Chat will automatically use Claude\n"
            return message

    def _test_anthropic_connection(self) -> str:
        """
        Test Anthropic API connection and build status message.

        MA principle: Extracted from show_anthropic_status (19 lines).

        Returns:
            Connection test result string
        """
        status = "\nTesting connection...\n"
        try:
            if ClaudeClient is None:
                raise ImportError("Claude client not available")

            client = ClaudeClient()
            result = client.test_connection()

            if result.success:
                status += "✅ Connection test: Success\n"
                status += f"Model: {result.model}\n"
                status += f"Tokens used: {result.tokens_used}\n"
            else:
                status += "❌ Connection test: Failed\n"
                status += f"Error: {result.error}\n"
        except Exception as e:
            status += "❌ Connection test: Failed\n"
            status += f"Error: {str(e)}\n"
        return status

    def show_anthropic_status(self) -> None:
        """
        Show Anthropic API key and service status.

        MA principle: Reduced from 71→28 lines by extracting 4 message builders (61% reduction).
        """
        from asciidoc_artisan.core import SecureCredentials

        status = "Anthropic Status:\n\n"

        # Show SDK version
        status += self._build_sdk_version_status()

        # Check if API key is configured
        try:
            creds = SecureCredentials()
            has_key = creds.has_anthropic_key()
        except Exception as e:
            logger.warning(f"Error checking Anthropic API key: {e}")
            has_key = False

        # Exit early if no API key
        if not has_key:
            status += self._build_no_api_key_message()
            self.editor.status_manager.show_message("info", "Anthropic Status", status)
            return

        # API key is configured - show model selection
        status += "✅ Anthropic API: Key configured\n"
        if self.editor._settings.claude_model:
            status += f"Selected model: {self.editor._settings.claude_model}\n\n"
        else:
            status += "⚠️ No model selected\n\n"

        # Show backend status
        status += self._build_backend_status()

        # Test connection
        status += self._test_anthropic_connection()

        self.editor.status_manager.show_message("info", "Anthropic Status", status)

    def show_telemetry_status(self) -> None:
        """Show telemetry status (delegates to telemetry_dialog_handler)."""
        self._telemetry_handler.show_telemetry_status()

    def show_ollama_settings(self) -> None:
        """Show Ollama AI settings dialog with model selection."""
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
        # Show API key configuration dialog.
        dialog = APIKeySetupDialog(self.editor)
        dialog.exec()  # Modal dialog - wait for user to close it

    def show_app_settings(self) -> None:
        """Show application settings editor dialog."""
        dialog = SettingsEditorDialog(self.editor._settings, self.editor._settings_manager, self.editor)
        if dialog.exec():
            # Settings are saved automatically in the dialog
            # Just refresh the UI from the updated settings
            self.editor._refresh_from_settings()
            logger.info("Application settings updated via settings editor")

    def show_font_settings(self) -> None:
        """Show font settings dialog."""
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
