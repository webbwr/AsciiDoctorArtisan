"""
Status Dialog Builder - Builds status messages for services and integrations.

Extracted from DialogManager to reduce class size (MA principle).
Handles status display for Pandoc, Ollama, and Anthropic services.
"""

import logging
import subprocess
from typing import TYPE_CHECKING, Any

from asciidoc_artisan.core.constants import is_pandoc_available

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class StatusDialogBuilder:
    """
    Builder for service status dialogs.

    This class was extracted from DialogManager to reduce class size per MA principle.

    Handles:
    - Pandoc installation and version status
    - Supported format information
    - Ollama service and GPU status
    - Anthropic API and connection status
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize StatusDialogBuilder with reference to main editor."""
        self.editor = editor

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
        import ollama

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
            import anthropic

            sdk_version = anthropic.__version__
            return f"SDK Version: {sdk_version}\n\n"
        except ImportError:
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
