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

    def _check_wsl_environment(self) -> bool:
        """
        Check if running in Windows Subsystem for Linux.

        MA principle: Extracted from _open_telemetry_file (8 lines).

        Returns:
            True if running in WSL, False otherwise
        """
        try:
            with open("/proc/version") as f:
                return "microsoft" in f.read().lower()
        except (FileNotFoundError, PermissionError, OSError):
            return False

    def _open_file_windows(self, file_path: "Path") -> None:
        """
        Open file with Windows notepad.

        MA principle: Extracted from _open_telemetry_file (10 lines).

        Args:
            file_path: Path to file to open
        """
        result = subprocess.run(
            ["notepad", str(file_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"Notepad command succeeded: {result}")

    def _open_file_macos(self, file_path: "Path") -> None:
        """
        Open file with macOS default application.

        MA principle: Extracted from _open_telemetry_file (10 lines).

        Args:
            file_path: Path to file to open
        """
        result = subprocess.run(
            ["open", str(file_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"Open command succeeded: {result}")

    def _open_file_wsl(self, file_path: "Path") -> None:
        """
        Open file in WSL using Windows notepad.

        MA principle: Extracted from _open_telemetry_file (30 lines).

        Args:
            file_path: Path to file to open
        """
        try:
            # Convert Linux path to Windows path
            win_path_result = subprocess.run(
                ["wslpath", "-w", str(file_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            win_path = win_path_result.stdout.strip()

            # Open with Windows notepad
            subprocess.run(
                ["/mnt/c/Windows/System32/notepad.exe", win_path],
                check=False,  # Don't check return code
                capture_output=True,
                text=True,
            )
            logger.info("WSL notepad.exe command succeeded")
        except Exception as wsl_error:
            logger.warning(f"WSL notepad failed: {wsl_error}, falling back to less")
            # Fall back to less (simple viewer)
            subprocess.run(
                [
                    "x-terminal-emulator",
                    "-e",
                    "less",
                    str(file_path),
                ]
            )

    def _open_file_linux(self, file_path: "Path") -> None:
        """
        Open file on Linux with xdg-open or fallback to less.

        MA principle: Extracted from _open_telemetry_file (21 lines).

        Args:
            file_path: Path to file to open
        """
        try:
            result = subprocess.run(
                ["xdg-open", str(file_path)],
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
                    str(file_path),
                ]
            )

    def _handle_file_open_error(self, error: Exception, file_path: "Path") -> None:
        """
        Handle file opening errors with user-friendly dialogs.

        MA principle: Extracted from _open_telemetry_file (13 lines).

        Args:
            error: Exception that occurred
            file_path: Path to file that failed to open
        """
        if isinstance(error, subprocess.CalledProcessError):
            error_msg = f"Failed to open file: {error}\nStderr: {error.stderr}"
            logger.error(error_msg)
            QMessageBox.warning(
                self.editor,
                "Open File Failed",
                f"Could not open telemetry file:\n{file_path}\n\nError: {error.stderr or str(error)}",
            )
        else:
            error_msg = f"Unexpected error opening file: {type(error).__name__}: {error}"
            logger.error(error_msg, exc_info=True)
            QMessageBox.warning(self.editor, "Open File Failed", f"Unexpected error:\n{str(error)}")

    def _open_telemetry_file(self, telemetry_file: "Path") -> None:
        """
        Open telemetry file in default application.

        MA principle: Reduced from 105→35 lines by extracting 6 platform-specific helpers.

        Args:
            telemetry_file: Path to telemetry file to open
        """
        logger.info(f"Opening telemetry file: {telemetry_file}")
        try:
            system = platform.system()
            if system == "Windows":
                self._open_file_windows(telemetry_file)
            elif system == "Darwin":  # macOS
                self._open_file_macos(telemetry_file)
            else:  # Linux/Unix
                if self._check_wsl_environment():
                    self._open_file_wsl(telemetry_file)
                else:
                    self._open_file_linux(telemetry_file)

            # File opened successfully
            logger.info(f"Successfully opened telemetry file: {telemetry_file.name}")
        except (subprocess.CalledProcessError, Exception) as e:
            self._handle_file_open_error(e, telemetry_file)

    def _select_telemetry_directory(self, telemetry_dir: "Path | None") -> "Path | None":
        """
        Show directory selection dialog for telemetry.

        MA principle: Extracted from _change_telemetry_directory (10 lines).

        Args:
            telemetry_dir: Current telemetry directory

        Returns:
            Selected directory path or None if cancelled
        """
        new_dir = QFileDialog.getExistingDirectory(
            self.editor,
            "Select Telemetry Directory",
            str(telemetry_dir) if telemetry_dir else str(Path.home()),
            QFileDialog.Option.ShowDirsOnly,
        )

        if not new_dir:
            logger.info("User cancelled directory selection")
            return None

        new_dir_path = Path(new_dir)
        logger.info(f"User selected new directory: {new_dir_path}")
        return new_dir_path

    def _confirm_directory_change(self, new_dir_path: "Path") -> bool:
        """
        Show confirmation dialog for directory change.

        MA principle: Extracted from _change_telemetry_directory (10 lines).

        Args:
            new_dir_path: New directory path

        Returns:
            True if user confirmed, False otherwise
        """
        reply = QMessageBox.question(
            self.editor,
            "Confirm Directory Change",
            f"Change telemetry directory to:\n{new_dir_path}\n\nThis will move all telemetry data to the new location.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            logger.info("User cancelled directory change confirmation")
            return False

        return True

    def _move_telemetry_data(self, telemetry_file: "Path | None", new_dir_path: "Path") -> None:
        """
        Move telemetry data to new directory and update collector.

        MA principle: Extracted from _change_telemetry_directory (15 lines).

        Args:
            telemetry_file: Current telemetry file path
            new_dir_path: New directory path

        Raises:
            Exception: If file move or directory creation fails
        """
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
        self.editor.telemetry_collector.telemetry_file = new_dir_path / "telemetry.json"

        logger.info("Telemetry directory changed successfully")

    def _show_directory_change_success(self, new_dir_path: "Path", msg_box: QMessageBox) -> None:
        """
        Show success message and reopen telemetry status.

        MA principle: Extracted from _change_telemetry_directory (8 lines).

        Args:
            new_dir_path: New directory path
            msg_box: Parent message box to close
        """
        QMessageBox.information(
            self.editor,
            "Directory Changed",
            f"Telemetry directory changed to:\n{new_dir_path}\n\nPrevious data has been copied to the new location.",
        )

        # Close the dialog and reopen to show updated info
        msg_box.done(QMessageBox.StandardButton.Ok)
        self.show_telemetry_status()

    def _change_telemetry_directory(
        self, telemetry_file: "Path | None", telemetry_dir: "Path | None", msg_box: QMessageBox
    ) -> None:
        """
        Allow user to select a new telemetry directory.

        MA principle: Reduced from 80→28 lines by extracting 4 dialog/operation helpers (65% reduction).

        Args:
            telemetry_file: Current telemetry file path
            telemetry_dir: Current telemetry directory
            msg_box: Parent message box (for closing/reopening)
        """
        logger.info("User requested to change telemetry directory")

        # Show directory selection dialog
        new_dir_path = self._select_telemetry_directory(telemetry_dir)
        if not new_dir_path:
            return

        # Confirm change
        if not self._confirm_directory_change(new_dir_path):
            return

        try:
            # Move data and update collector
            self._move_telemetry_data(telemetry_file, new_dir_path)

            # Show success and reopen dialog
            self._show_directory_change_success(new_dir_path, msg_box)

        except Exception as e:
            error_msg = f"Failed to change directory: {type(e).__name__}: {e}"
            logger.error(error_msg, exc_info=True)
            QMessageBox.critical(
                self.editor,
                "Change Directory Failed",
                f"Could not change telemetry directory:\n{str(e)}",
            )

    def _get_telemetry_file_info(self) -> tuple["Path | None", "Path | None"]:
        """
        Get telemetry file and directory paths.

        MA principle: Extracted from show_telemetry_status (7 lines).

        Returns:
            Tuple of (telemetry_file, telemetry_dir) or (None, None)
        """
        if hasattr(self.editor, "telemetry_collector"):
            telemetry_file = self.editor.telemetry_collector.telemetry_file
            return telemetry_file, telemetry_file.parent
        return None, None

    def _build_enabled_status_message(self, telemetry_file: "Path | None", telemetry_dir: "Path | None") -> str:
        """
        Build status message for enabled telemetry.

        MA principle: Extracted from show_telemetry_status (32 lines).

        Args:
            telemetry_file: Telemetry file path
            telemetry_dir: Telemetry directory path

        Returns:
            Formatted status message string
        """
        status = "✅ Telemetry: Enabled\n"

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

        return status

    def _build_disabled_status_message(self, telemetry_file: "Path | None", telemetry_dir: "Path | None") -> str:
        """
        Build status message for disabled telemetry.

        MA principle: Extracted from show_telemetry_status (24 lines).

        Args:
            telemetry_file: Telemetry file path
            telemetry_dir: Telemetry directory path

        Returns:
            Formatted status message string
        """
        status = "⚠️ Telemetry: Disabled\n\n"

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

        return status

    def _create_telemetry_status_dialog(
        self, status: str, telemetry_file: "Path | None", telemetry_dir: "Path | None"
    ) -> None:
        """
        Create and display telemetry status dialog with action buttons.

        MA principle: Extracted from show_telemetry_status (20 lines).

        Args:
            status: Formatted status message
            telemetry_file: Telemetry file path
            telemetry_dir: Telemetry directory path
        """
        msg_box = QMessageBox(self.editor)
        msg_box.setWindowTitle("Telemetry Status")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(status)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Add "Open File" button if telemetry file exists
        if telemetry_file and telemetry_file.exists():
            open_file_button = msg_box.addButton("Open File", QMessageBox.ButtonRole.ActionRole)
            open_file_button.clicked.connect(lambda: self._open_telemetry_file(telemetry_file))

        # Add "Change Directory" button
        change_dir_button = msg_box.addButton("Change Directory", QMessageBox.ButtonRole.ActionRole)
        change_dir_button.clicked.connect(
            lambda: self._change_telemetry_directory(telemetry_file, telemetry_dir, msg_box)
        )

        msg_box.exec()

    def show_telemetry_status(self) -> None:
        """
        Show telemetry configuration and data collection status.

        MA principle: Reduced from 86→18 lines by extracting 4 message-building helpers.
        """
        # Get file information
        telemetry_file, telemetry_dir = self._get_telemetry_file_info()

        # Build status message
        status = "Telemetry Status:\n\n"
        if self.editor._settings.telemetry_enabled:
            status += self._build_enabled_status_message(telemetry_file, telemetry_dir)
        else:
            status += self._build_disabled_status_message(telemetry_file, telemetry_dir)

        # Create and show dialog
        self._create_telemetry_status_dialog(status, telemetry_file, telemetry_dir)

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
