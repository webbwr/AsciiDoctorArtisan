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
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from asciidoc_artisan.core.constants import is_pandoc_available

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

    def show_installation_validator(self) -> None:
        """Show installation validator dialog."""
        from asciidoc_artisan.ui.installation_validator_dialog import (
            InstallationValidatorDialog,
        )

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

    def show_anthropic_status(self) -> None:
        """Show Anthropic API key and service status."""
        import anthropic

        from asciidoc_artisan.core import SecureCredentials

        status = "Anthropic Status:\n\n"

        # Show SDK version
        try:
            sdk_version = anthropic.__version__
            status += f"SDK Version: {sdk_version}\n\n"
        except AttributeError:
            status += "SDK Version: Unknown\n\n"

        # Check if API key is configured
        creds = SecureCredentials()
        has_key = creds.has_anthropic_key()

        if not has_key:
            status += "⚠️ Anthropic API: No API key configured\n\n"
            status += "To configure Anthropic API key:\n"
            status += "1. Go to Tools → API Key Setup\n"
            status += "2. Enter your Anthropic API key\n"
            status += "3. Click Save\n\n"
            status += "To get an API key:\n"
            status += "  Visit: https://console.anthropic.com/settings/keys\n"
            self.editor.status_manager.show_message("info", "Anthropic Status", status)
            return

        # API key is configured
        status += "✅ Anthropic API: Key configured\n"
        if self.editor._settings.claude_model:
            status += f"Selected model: {self.editor._settings.claude_model}\n\n"
        else:
            status += "⚠️ No model selected\n\n"

        # Check if Claude backend is active
        if self.editor._settings.ai_backend == "claude":
            status += "✅ Active backend: Claude (remote)\n"
        else:
            status += "⚠️ Active backend: Ollama (local)\n"
            status += "\nTo switch to Claude:\n"
            status += "1. Disable Ollama in Tools → AI Status → Settings\n"
            status += "2. Chat will automatically use Claude\n"

        # Test connection
        status += "\nTesting connection...\n"
        try:
            from asciidoc_artisan.claude import ClaudeClient

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

        self.editor.status_manager.show_message("info", "Anthropic Status", status)

    def show_telemetry_status(self) -> None:  # noqa: C901
        """Show telemetry configuration and data collection status."""
        import logging
        import platform
        import subprocess
        from pathlib import Path

        from PySide6.QtWidgets import QFileDialog, QMessageBox

        logger = logging.getLogger(__name__)

        status = "Telemetry Status:\n\n"

        # Get telemetry file path from collector
        telemetry_file = None
        telemetry_dir = None
        if hasattr(self.editor, "telemetry_collector"):
            telemetry_file = self.editor.telemetry_collector.telemetry_file
            telemetry_dir = telemetry_file.parent

        # Check if telemetry is enabled
        if self.editor._settings.telemetry_enabled:
            status += "✅ Telemetry: Enabled\n"

            # Show session ID
            if self.editor._settings.telemetry_session_id:
                session_id = self.editor._settings.telemetry_session_id
                status += f"Session ID: {session_id}\n\n"
            else:
                status += "⚠️ No session ID generated yet\n\n"

            # Show storage location
            if telemetry_file:
                status += "Storage Location:\n"
                status += f"  File: {telemetry_file}\n"
                status += f"  Directory: {telemetry_dir}\n\n"

            # Data collection info
            status += "Data Collected:\n"
            status += "• Application version and startup/shutdown times\n"
            status += "• Feature usage (e.g., export formats, AI chat)\n"
            status += "• Performance metrics (document size, render time)\n"
            status += "• Error events and stack traces\n\n"

            status += "Privacy:\n"
            status += "• No document content is collected\n"
            status += "• No personal information is collected\n"
            status += "• Data is stored locally only\n"
            status += "• No data is sent to external servers\n\n"

            status += "To disable telemetry:\n"
            status += "Go to Tools → Telemetry (toggle off)\n"
        else:
            status += "⚠️ Telemetry: Disabled\n\n"

            # Show storage location even when disabled
            if telemetry_file:
                status += "Storage Location:\n"
                status += f"  File: {telemetry_file}\n"
                status += f"  Directory: {telemetry_dir}\n\n"

            status += "Telemetry helps improve the application by collecting:\n"
            status += "• Anonymous usage statistics\n"
            status += "• Performance metrics\n"
            status += "• Error reports\n\n"

            status += "Privacy guarantees:\n"
            status += "• No document content is collected\n"
            status += "• No personal information is collected\n"
            status += "• Data is stored locally only\n"
            status += "• No data is sent to external servers\n\n"

            status += "To enable telemetry:\n"
            status += "Go to Tools → Telemetry (toggle on)\n"

        # Create custom dialog with "Open Directory" and "Change Directory" buttons
        msg_box = QMessageBox(self.editor)
        msg_box.setWindowTitle("Telemetry Status")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(status)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Add "Open File" button if telemetry file exists
        if telemetry_file and telemetry_file.exists():
            open_file_button = msg_box.addButton(
                "Open File", QMessageBox.ButtonRole.ActionRole
            )

            def open_file() -> None:
                """Open telemetry file in default application."""
                logger.info(f"Opening telemetry file: {telemetry_file}")
                try:
                    system = platform.system()
                    if system == "Windows":
                        # Use default text editor on Windows
                        result = subprocess.run(
                            ["notepad", str(telemetry_file)],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        logger.info(f"Notepad command succeeded: {result}")
                    elif system == "Darwin":  # macOS
                        # Opens with default application
                        result = subprocess.run(
                            ["open", str(telemetry_file)],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        logger.info(f"Open command succeeded: {result}")
                    else:  # Linux/Unix
                        # Check if running in WSL
                        is_wsl = False
                        try:
                            with open("/proc/version", "r") as f:
                                is_wsl = "microsoft" in f.read().lower()
                        except (FileNotFoundError, PermissionError, OSError):
                            pass

                        if is_wsl:
                            # WSL: Use Windows notepad.exe with wslpath conversion
                            try:
                                # Convert Linux path to Windows path
                                win_path_result = subprocess.run(
                                    ["wslpath", "-w", str(telemetry_file)],
                                    capture_output=True,
                                    text=True,
                                    check=True,
                                )
                                win_path = win_path_result.stdout.strip()

                                # Open with Windows notepad
                                result = subprocess.run(
                                    ["/mnt/c/Windows/System32/notepad.exe", win_path],
                                    check=False,  # Don't check return code
                                    capture_output=True,
                                    text=True,
                                )
                                logger.info("WSL notepad.exe command succeeded")
                            except Exception as wsl_error:
                                logger.warning(
                                    f"WSL notepad failed: {wsl_error}, falling back to less"
                                )
                                # Fall back to less (simple viewer)
                                subprocess.run(
                                    [
                                        "x-terminal-emulator",
                                        "-e",
                                        "less",
                                        str(telemetry_file),
                                    ]
                                )
                        else:
                            # Try xdg-open first, fall back to less
                            try:
                                result = subprocess.run(
                                    ["xdg-open", str(telemetry_file)],
                                    check=True,
                                    capture_output=True,
                                    text=True,
                                )
                                logger.info(f"xdg-open command succeeded: {result}")
                            except FileNotFoundError:
                                # xdg-open not available, use less as fallback
                                logger.info("xdg-open not found, using less as viewer")
                                subprocess.run(
                                    [
                                        "x-terminal-emulator",
                                        "-e",
                                        "less",
                                        str(telemetry_file),
                                    ]
                                )

                    # File opened successfully - no status message needed
                    logger.info(
                        f"Successfully opened telemetry file: {telemetry_file.name}"
                    )
                except subprocess.CalledProcessError as e:
                    error_msg = f"Failed to open file: {e}\nStderr: {e.stderr}"
                    logger.error(error_msg)
                    QMessageBox.warning(
                        self.editor,
                        "Open File Failed",
                        f"Could not open telemetry file:\n{telemetry_file}\n\nError: {e.stderr or str(e)}",
                    )
                except Exception as e:
                    error_msg = (
                        f"Unexpected error opening file: {type(e).__name__}: {e}"
                    )
                    logger.error(error_msg, exc_info=True)
                    QMessageBox.warning(
                        self.editor, "Open File Failed", f"Unexpected error:\n{str(e)}"
                    )

            open_file_button.clicked.connect(open_file)

        # Add "Change Directory" button
        change_dir_button = msg_box.addButton(
            "Change Directory", QMessageBox.ButtonRole.ActionRole
        )

        def change_directory() -> None:
            """Allow user to select a new telemetry directory."""
            logger.info("User requested to change telemetry directory")

            # Show directory selection dialog
            new_dir = QFileDialog.getExistingDirectory(
                self.editor,
                "Select Telemetry Directory",
                str(telemetry_dir) if telemetry_dir else str(Path.home()),
                QFileDialog.Option.ShowDirsOnly,
            )

            if not new_dir:
                logger.info("User cancelled directory selection")
                return

            new_dir_path = Path(new_dir)
            logger.info(f"User selected new directory: {new_dir_path}")

            # Confirm change
            reply = QMessageBox.question(
                self.editor,
                "Confirm Directory Change",
                f"Change telemetry directory to:\n{new_dir_path}\n\n"
                "This will move all telemetry data to the new location.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                logger.info("User cancelled directory change confirmation")
                return

            try:
                # Create new directory if it doesn't exist
                new_dir_path.mkdir(parents=True, exist_ok=True)

                # Move existing telemetry file if it exists
                if telemetry_file and telemetry_file.exists():
                    new_file_path = new_dir_path / "telemetry.json"
                    import shutil

                    shutil.copy2(telemetry_file, new_file_path)
                    logger.info(f"Copied telemetry file to: {new_file_path}")

                # Update telemetry collector
                self.editor.telemetry_collector.data_dir = new_dir_path
                self.editor.telemetry_collector.telemetry_file = (
                    new_dir_path / "telemetry.json"
                )

                logger.info("Telemetry directory changed successfully")

                QMessageBox.information(
                    self.editor,
                    "Directory Changed",
                    f"Telemetry directory changed to:\n{new_dir_path}\n\n"
                    "Previous data has been copied to the new location.",
                )

                # Close the dialog and reopen to show updated info
                msg_box.done(QMessageBox.StandardButton.Ok)
                self.show_telemetry_status()

            except Exception as e:
                error_msg = f"Failed to change directory: {type(e).__name__}: {e}"
                logger.error(error_msg, exc_info=True)
                QMessageBox.critical(
                    self.editor,
                    "Change Directory Failed",
                    f"Could not change telemetry directory:\n{str(e)}",
                )

        change_dir_button.clicked.connect(change_directory)

        msg_box.exec()

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
