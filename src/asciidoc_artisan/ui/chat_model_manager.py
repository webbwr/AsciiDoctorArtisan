"""
Chat Model Manager - Model loading, validation, and event handling for AI backends.

Extracted from ChatManager to reduce class size (MA principle).
Handles model operations for both Ollama (local) and Claude (remote) backends.
"""

import logging
import subprocess
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from ..core import AppSettings
    from .chat_bar_widget import ChatBarWidget

logger = logging.getLogger(__name__)


class ChatModelManager(QObject):
    """
    Manager for AI model operations (loading, validation, backend-specific logic).

    This class was extracted from ChatManager to reduce class size per MA principle.

    Handles:
    - Model loading for Ollama and Claude backends
    - Model validation via subprocess (Ollama) or API list (Claude)
    - Model change events with validation
    - Model scanning for Claude backend

    Signals:
        status_message: Status update message for user display
        settings_changed: Settings were modified (trigger save)
    """

    status_message = Signal(str)
    settings_changed = Signal()

    def __init__(self, settings: "AppSettings", chat_bar: "ChatBarWidget", current_backend_getter: Any) -> None:
        """
        Initialize ChatModelManager.

        Args:
            settings: Application settings instance
            chat_bar: Chat bar widget for UI updates
            current_backend_getter: Callable that returns current backend name ("ollama" or "claude")
        """
        super().__init__()
        self._settings = settings
        self._chat_bar = chat_bar
        self._get_current_backend = current_backend_getter

    def update_settings(self, settings: "AppSettings") -> None:
        """Update settings reference when main settings object changes."""
        self._settings = settings

    def load_available_models(self) -> None:
        """
        Load available models into chat bar selector based on active backend.

        For Ollama: Detects installed models via `ollama list` command
        For Claude: Uses hardcoded model list from ClaudeClient

        Falls back to defaults if backend is not available.
        """
        current_backend = self._get_current_backend()
        if current_backend == "ollama":
            self._load_ollama_models()
        elif current_backend == "claude":
            self._load_claude_models()
        else:
            logger.error(f"Unknown backend: {current_backend}")
            self.status_message.emit(f"Error: Unknown AI backend '{current_backend}'")

    def _execute_ollama_list_command(self) -> tuple[list[str], bool]:
        """
        Execute 'ollama list' and parse available models.

        MA principle: Extracted from _load_ollama_models (38 lines).

        Returns:
            Tuple of (model_list, ollama_available)
        """
        models: list[str] = []
        ollama_available = False

        try:
            # SECURITY: List form prevents command injection attacks (no shell=True!)
            result = subprocess.run(
                ["ollama", "list"],  # Safe: list form, no shell
                capture_output=True,
                text=True,
                timeout=3,  # Prevent hang if Ollama is frozen
                check=False,  # Don't raise exception on non-zero exit
            )

            if result.returncode == 0:
                ollama_available = True
                # Parse output: skip header line, extract model names
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:  # Skip header
                    for line in lines[1:]:
                        parts = line.split()
                        if parts:
                            models.append(parts[0])  # Model name is first column

                if models:
                    logger.info(f"Ollama detected: {len(models)} model(s) available")
                    self.status_message.emit(f"Ollama: {len(models)} model(s) found")
                else:
                    logger.warning("Ollama running but no models installed")
                    self.status_message.emit("Ollama: No models installed (run 'ollama pull qwen2.5-coder:7b')")
                    self._auto_download_default_model()
            else:
                logger.warning(f"Ollama command failed: {result.stderr.strip()}")

        except FileNotFoundError:
            logger.info("Ollama not found in PATH")
            self.status_message.emit("Ollama not installed (see docs/OLLAMA_CHAT_GUIDE.md)")
        except subprocess.TimeoutExpired:
            logger.warning("Ollama list command timed out")
            self.status_message.emit("Ollama not responding")
        except Exception as e:
            logger.warning(f"Error detecting Ollama models: {e}")

        return models, ollama_available

    def _get_fallback_models(self) -> list[str]:
        """
        Get default Ollama model list.

        MA principle: Extracted from _load_ollama_models (3 lines).

        Returns:
            Default model list
        """
        return ["gnokit/improve-grammer", "deepseek-coder", "codellama"]

    def _ensure_current_model_in_list(self, models: list[str]) -> None:
        """
        Add current model to list if not already present.

        MA principle: Extracted from _load_ollama_models (4 lines).

        Args:
            models: Model list to update
        """
        if self._settings.ollama_model and self._settings.ollama_model not in models:
            models.insert(0, self._settings.ollama_model)

    def _load_ollama_models(self) -> None:
        """
        Load available Ollama models.

        MA principle: Reduced from 67→22 lines by extracting 3 helpers (67% reduction).
        """
        # Execute ollama list command
        models, ollama_available = self._execute_ollama_list_command()

        # Fallback to defaults if detection failed
        if not models:
            models = self._get_fallback_models()
            if not ollama_available:
                logger.info("Using default Ollama model list (Ollama not detected)")

        # Ensure current model is in list
        self._ensure_current_model_in_list(models)

        # Update chat bar
        self._chat_bar.set_models(models)
        logger.debug(f"Loaded {len(models)} Ollama models into chat bar")

    def _load_claude_models(self) -> None:
        """Load available Claude models."""
        try:
            # Import ClaudeClient to get available models
            from ..claude import ClaudeClient

            models = ClaudeClient.AVAILABLE_MODELS.copy()
            logger.info(f"Claude models available: {len(models)}")

            # Check if API key is configured
            from ..core import SecureCredentials

            creds = SecureCredentials()
            if creds.has_anthropic_key():
                self.status_message.emit(f"Claude: {len(models)} model(s) available")
            else:
                self.status_message.emit("Claude: API key required (Tools → API Key Setup)")

        except Exception as e:
            logger.error(f"Error loading Claude models: {e}")
            # Fallback to hardcoded defaults
            models = [
                "claude-sonnet-4-20250514",
                "claude-haiku-4-5",
            ]

        # Add current model if not in list
        if self._settings.claude_model and self._settings.claude_model not in models:
            models.insert(0, self._settings.claude_model)

        self._chat_bar.set_models(models)
        logger.debug(f"Loaded {len(models)} Claude models into chat bar")

    def _validate_claude_model(self, model: str) -> bool:
        """
        Validate Claude model against available models list.

        MA principle: Extracted from _validate_model (10 lines).

        Args:
            model: Model name to validate

        Returns:
            True if model is available, False otherwise
        """
        try:
            from ..claude import ClaudeClient

            is_valid = model in ClaudeClient.AVAILABLE_MODELS
            logger.debug(f"Claude model validation: {model} -> {is_valid}")
            return is_valid
        except Exception as e:
            logger.error(f"Error validating Claude model: {e}")
            return False

    def _validate_ollama_model(self, model: str) -> bool:
        """
        Validate Ollama model via subprocess.

        MA principle: Extracted from _validate_model (41 lines).

        Args:
            model: Model name to validate

        Returns:
            True if model is available, False otherwise
        """
        try:
            # Check if model exists via ollama list
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )

            if result.returncode == 0:
                # Parse output and check if model is in list
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:  # Skip header
                    for line in lines[1:]:
                        parts = line.split()
                        if parts and parts[0] == model:
                            logger.debug(f"Ollama model validated: {model}")
                            return True

                # Model not found in list
                logger.debug(f"Model not found in ollama list: {model}")
                return False
            else:
                logger.warning(f"ollama list failed: {result.stderr.strip()}")
                return False

        except FileNotFoundError:
            logger.warning("Ollama not found in PATH")
            return False
        except subprocess.TimeoutExpired:
            logger.warning("Model validation timed out")
            # Assume valid to avoid blocking
            return True
        except Exception as e:
            logger.warning(f"Error validating Ollama model: {e}")
            # Assume valid to avoid blocking
            return True

    def validate_model(self, model: str) -> bool:
        """
        Validate that a model exists for the active backend.

        MA principle: Reduced from 74→20 lines by extracting 2 backend validators (73% reduction).

        Args:
            model: Model name to validate

        Returns:
            True if model is available, False otherwise
        """
        if not model:
            return False

        current_backend = self._get_current_backend()
        if current_backend == "claude":
            return self._validate_claude_model(model)
        elif current_backend == "ollama":
            return self._validate_ollama_model(model)
        else:
            logger.error(f"Unknown backend: {current_backend}")
            return False

    def handle_model_changed(self, model: str) -> None:
        """
        Handle model selector change with validation.

        Validates that the selected model exists for the active backend.
        Updates status bar with real-time feedback.

        Args:
            model: New model name
        """
        if not model:
            logger.warning("Empty model name provided")
            self.status_message.emit("Error: No model selected")
            return

        # Validate model exists for active backend
        logger.info(f"Validating model selection: {model}")
        self.status_message.emit(f"Validating model: {model}...")

        current_backend = self._get_current_backend()
        if self.validate_model(model):
            # Model is valid - update settings for active backend
            if current_backend == "ollama":
                self._settings.ollama_model = model
            elif current_backend == "claude":
                self._settings.claude_model = model

            self.settings_changed.emit()
            backend_name = current_backend.capitalize()
            self.status_message.emit(f"✓ Switched to {backend_name} model: {model}")
            logger.info(f"Model changed to: {model} (backend: {current_backend})")
        else:
            # Model is invalid - keep current model and show error
            if current_backend == "ollama":
                current_model = self._settings.ollama_model or "none"
            elif current_backend == "claude":
                current_model = self._settings.claude_model or "none"
            else:
                current_model = "none"

            logger.warning(f"Model validation failed: {model} not found")
            self.status_message.emit(f"✗ Model '{model}' not available (keeping {current_model})")

            # Revert selector to current valid model
            if current_model and current_model != "none":
                self._chat_bar.set_model(current_model)

    def handle_scan_models_requested(self, chat_panel: Any) -> None:
        """
        Handle scan models button click.

        Fetches available models from Anthropic API and displays in chat.
        Only works for Claude backend.

        Args:
            chat_panel: Chat panel widget for displaying results
        """
        current_backend = self._get_current_backend()
        if current_backend != "claude":
            logger.warning("Scan models only available for Claude backend")
            self.status_message.emit("⚠️ Model scanning only available for Claude")
            return

        logger.info("Scanning Anthropic API for available models")
        self.status_message.emit("Scanning Anthropic API for models...")

        try:
            from asciidoc_artisan.claude import ClaudeClient

            client = ClaudeClient()
            result = client.fetch_available_models_from_api()

            if result.success:
                # Display models in chat panel as system message
                chat_panel.add_message("system", f"🔍 **Available Models**\n\n{result.content}")
                self.status_message.emit("✓ Model scan complete")
                logger.info("Model scan successful")
            else:
                # Display error in chat
                error_msg = f"❌ **Model Scan Failed**\n\n{result.error}"
                chat_panel.add_message("system", error_msg)
                self.status_message.emit("✗ Model scan failed")
                logger.error(f"Model scan failed: {result.error}")

        except Exception as e:
            logger.exception(f"Error scanning models: {e}")
            error_msg = f"❌ **Error Scanning Models**\n\n{str(e)}"
            chat_panel.add_message("system", error_msg)
            self.status_message.emit("✗ Error scanning models")

    def _auto_download_default_model(self) -> None:
        """
        Trigger auto-download of default Ollama model.

        Note: This method is referenced in _execute_ollama_list_command but not
        implemented in the extracted class. The parent ChatManager should handle
        this or it can be implemented here if needed.
        """
        logger.info("Auto-download default model triggered (not implemented)")
