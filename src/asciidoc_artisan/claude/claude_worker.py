"""
Claude Worker - QThread worker for asynchronous Claude API operations.

This module provides a worker thread for non-blocking Claude API calls,
following the same pattern as GitWorker and OllamaChatWorker.

The worker runs API calls in a background thread to prevent UI freezing
and emits signals when results are ready.

Example:
    >>> worker = ClaudeWorker()
    >>> worker.response_ready.connect(handle_response)
    >>> worker.send_message("Hello Claude!")
"""

import logging
from typing import List, Optional

from PySide6.QtCore import QThread, Signal, Slot

from .claude_client import ClaudeClient, ClaudeMessage, ClaudeResult

logger = logging.getLogger(__name__)


class ClaudeWorker(QThread):
    """
    Worker thread for asynchronous Claude API operations.

    This worker handles Claude API calls in a background thread to avoid
    blocking the UI. It follows the same pattern as other workers in the
    application (GitWorker, OllamaChatWorker, etc.).

    Signals:
        response_ready: Emitted when Claude response is ready (ClaudeResult)
        connection_tested: Emitted when connection test completes (ClaudeResult)
        error_occurred: Emitted when an error occurs (str)

    Example:
        >>> worker = ClaudeWorker(model="claude-3-5-sonnet-20241022")
        >>> worker.response_ready.connect(lambda result: print(result.content))
        >>> worker.send_message("Explain AsciiDoc syntax")
    """

    # Signals
    response_ready = Signal(object)  # ClaudeResult
    connection_tested = Signal(object)  # ClaudeResult
    error_occurred = Signal(str)  # Error message

    def __init__(
        self,
        model: str = ClaudeClient.DEFAULT_MODEL,
        max_tokens: int = 4096,
        temperature: float = 1.0,
    ) -> None:
        """
        Initialize Claude worker.

        Args:
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
        """
        super().__init__()

        self.client = ClaudeClient(
            model=model, max_tokens=max_tokens, temperature=temperature
        )

        # Operation state
        self._current_message: str = ""
        self._current_system: Optional[str] = None
        self._current_history: Optional[List[ClaudeMessage]] = None
        self._operation: str = ""  # "send_message" or "test_connection"

        logger.debug("Claude worker initialized")

    def run(self) -> None:
        """
        Execute the current operation.

        This method runs in the worker thread and should not be called directly.
        Use send_message() or test_connection() instead.
        """
        try:
            if self._operation == "send_message":
                self._execute_send_message()
            elif self._operation == "test_connection":
                self._execute_test_connection()
            else:
                logger.warning(f"Unknown operation: {self._operation}")
                self.error_occurred.emit(f"Unknown operation: {self._operation}")

        except Exception as e:
            logger.exception(f"Claude worker error: {e}")
            self.error_occurred.emit(f"Worker error: {str(e)}")

    def _execute_send_message(self) -> None:
        """Execute send_message operation (runs in worker thread)."""
        logger.debug("Executing send_message in worker thread")

        result = self.client.send_message(
            message=self._current_message,
            system=self._current_system,
            conversation_history=self._current_history,
        )

        self.response_ready.emit(result)
        logger.debug("send_message complete, result emitted")

    def _execute_test_connection(self) -> None:
        """Execute test_connection operation (runs in worker thread)."""
        logger.debug("Executing test_connection in worker thread")

        result = self.client.test_connection()

        self.connection_tested.emit(result)
        logger.debug("test_connection complete, result emitted")

    @Slot(str, str, list)
    def send_message(
        self,
        message: str,
        system: Optional[str] = None,
        conversation_history: Optional[List[ClaudeMessage]] = None,
    ) -> None:
        """
        Send a message to Claude (non-blocking).

        This method sets up the operation and starts the worker thread.
        The result will be emitted via the response_ready signal.

        Args:
            message: User message to send
            system: System prompt for context (optional)
            conversation_history: Previous messages for context (optional)

        Example:
            >>> worker.send_message(
            ...     "Explain AsciiDoc",
            ...     system="You are an AsciiDoc expert"
            ... )
            >>> # Result will be emitted via response_ready signal
        """
        if self.isRunning():
            logger.warning("Worker is already running, operation ignored")
            self.error_occurred.emit("Worker is busy. Please wait.")
            return

        self._operation = "send_message"
        self._current_message = message
        self._current_system = system
        self._current_history = conversation_history

        logger.debug(f"Starting send_message operation: '{message[:50]}...'")
        self.start()

    @Slot()
    def test_connection(self) -> None:
        """
        Test Claude API connection (non-blocking).

        This method starts a connection test in the worker thread.
        The result will be emitted via the connection_tested signal.

        Example:
            >>> worker.test_connection()
            >>> # Result will be emitted via connection_tested signal
        """
        if self.isRunning():
            logger.warning("Worker is already running, operation ignored")
            self.error_occurred.emit("Worker is busy. Please wait.")
            return

        self._operation = "test_connection"
        logger.debug("Starting test_connection operation")
        self.start()

    def is_configured(self) -> bool:
        """
        Check if Claude API key is configured.

        Returns:
            True if API key is available

        Example:
            >>> worker = ClaudeWorker()
            >>> if worker.is_configured():
            ...     worker.send_message("Hello!")
        """
        return self.client.is_configured()

    def get_available_models(self) -> List[str]:
        """
        Get list of available Claude models.

        Returns:
            List of model identifiers

        Example:
            >>> worker = ClaudeWorker()
            >>> models = worker.get_available_models()
        """
        return self.client.get_available_models()

    def set_model(self, model: str) -> None:
        """
        Set the Claude model to use.

        Args:
            model: Model identifier (e.g., "claude-3-5-sonnet-20241022")

        Example:
            >>> worker.set_model("claude-3-5-haiku-20241022")
        """
        self.client.model = model
        logger.debug(f"Claude model changed to: {model}")

    def set_max_tokens(self, max_tokens: int) -> None:
        """
        Set maximum tokens in response.

        Args:
            max_tokens: Maximum number of tokens

        Example:
            >>> worker.set_max_tokens(8192)
        """
        self.client.max_tokens = max_tokens
        logger.debug(f"Max tokens changed to: {max_tokens}")

    def set_temperature(self, temperature: float) -> None:
        """
        Set sampling temperature.

        Args:
            temperature: Temperature value (0-1)

        Example:
            >>> worker.set_temperature(0.7)
        """
        self.client.temperature = temperature
        logger.debug(f"Temperature changed to: {temperature}")
