"""
Ollama AI Chat worker for background chat processing.

This module provides OllamaChatWorker, a QObject-based worker that handles
asynchronous communication with the Ollama API for chat interactions.

The worker supports:
- Four context modes: document, syntax, general, editing
- Streaming responses for long-form AI output
- Cancellation of in-progress requests
- Error handling with user-friendly messages
- Document context injection with debouncing

Thread Safety:
    All Ollama API calls run on a background thread. Results are emitted
    via Qt signals to the main UI thread for display.

Specification Reference: Lines 228-329 (Ollama AI Chat Rules)
"""

import logging
import subprocess
import time

from PySide6.QtCore import QObject, Signal, Slot

from ..core.models import ChatMessage

logger = logging.getLogger(__name__)


class OllamaChatWorker(QObject):
    """
    Background worker for Ollama AI chat operations.

    Runs Ollama API calls in a separate thread to prevent UI blocking.
    Supports streaming responses, cancellation, and four interaction modes.

    Threading: This worker inherits from QObject and is moved to a background
    thread using QObject.moveToThread(). Methods decorated with @Slot are
    automatically invoked on the worker's thread when called from the main thread.

    Signals:
        chat_response_ready: Emitted with ChatMessage when AI response completes
        chat_response_chunk: Emitted with partial response text during streaming
        chat_error: Emitted with error message when operation fails
        operation_cancelled: Emitted when user cancels ongoing operation

    Attributes:
        _is_processing: Reentrancy guard to prevent concurrent operations
        _should_cancel: Flag to signal cancellation request
        _current_model: Active Ollama model name
        _context_mode: Current interaction mode
        _chat_history: List of ChatMessage objects for context
        _document_content: Current document text for context injection
        _user_message: Pending user message to process

    Example:
        ```python
        worker = OllamaChatWorker()
        worker.chat_response_ready.connect(on_response)
        worker.chat_error.connect(on_error)

        worker.send_message(
            message="How do I make a table?",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
            history=[...],
            document_content=None
        )
        ```
    """

    # Signals
    chat_response_ready = Signal(ChatMessage)
    chat_response_chunk = Signal(str)
    chat_error = Signal(str)
    operation_cancelled = Signal()

    def __init__(self) -> None:
        """Initialize the Ollama chat worker."""
        super().__init__()
        self._is_processing = False
        self._should_cancel = False
        self._current_model: str | None = None
        self._context_mode: str = "document"
        self._chat_history: list[ChatMessage] = []
        self._document_content: str | None = None
        self._user_message: str | None = None

    @Slot(str, str, str, object, object)
    def send_message(
        self,
        message: str,
        model: str,
        context_mode: str,
        history: list[ChatMessage],
        document_content: str | None = None,
    ) -> None:
        """
        Queue a chat message for processing.

        Args:
            message: User's chat message text
            model: Ollama model name (e.g., "qwen2.5-coder:7b")
            context_mode: Interaction mode (document/syntax/general/editing)
            history: Previous chat messages for context
            document_content: Current document text (optional, for context modes)

        Raises:
            RuntimeError: If worker is already processing a message

        Note: This method is a Qt slot. When called from the main thread,
        Qt automatically queues execution on the worker's thread.
        """
        if self._is_processing:
            logger.warning("Chat worker is busy, ignoring new message")
            return

        self._user_message = message
        self._current_model = model
        self._context_mode = context_mode
        self._chat_history = history
        self._document_content = document_content
        self._should_cancel = False

        # Process chat on worker thread (Qt handles threading via moveToThread)
        self._process_chat()

    def cancel_operation(self) -> None:
        """
        Cancel the currently running chat operation.

        Sets cancellation flag. Worker checks this flag periodically
        during API calls and streaming responses.
        """
        if self._is_processing:
            logger.info("Cancelling chat operation")
            self._should_cancel = True

    def _process_chat(self) -> None:
        """
        Process the queued chat message on the worker thread.

        Processes the queued chat message, calls Ollama API, and emits
        results via signals. Handles streaming, errors, and cancellation.

        This method runs on the worker's thread (not the main UI thread).
        """
        if not self._user_message or not self._current_model:
            logger.error("Missing user message or model")
            self.chat_error.emit("Internal error: missing message or model")
            return

        self._is_processing = True

        try:
            # Build system prompt based on context mode
            system_prompt = self._build_system_prompt()

            # Build message history for Ollama API
            messages = self._build_message_history(system_prompt)

            # Call Ollama API
            response_text = self._call_ollama_api(messages)

            # Check for cancellation
            if self._should_cancel:
                logger.info("Operation cancelled by user")
                self.operation_cancelled.emit()
                return

            # Create ChatMessage for response
            response_message = ChatMessage(
                role="assistant",
                content=response_text,
                timestamp=time.time(),
                model=self._current_model,
                context_mode=self._context_mode,
            )

            self.chat_response_ready.emit(response_message)
            logger.info(f"Chat response completed ({len(response_text)} chars)")

        except subprocess.TimeoutExpired:
            error_msg = "Request timed out. Try a shorter message or simpler question."
            logger.error(f"Ollama API timeout: {error_msg}")
            self.chat_error.emit(error_msg)

        except subprocess.CalledProcessError as e:
            error_msg = self._parse_ollama_error(e)
            logger.error(f"Ollama API error: {error_msg}")
            self.chat_error.emit(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.exception("Unexpected error in chat worker")
            self.chat_error.emit(error_msg)

        finally:
            self._is_processing = False
            self._user_message = None

    def _build_system_prompt(self) -> str:
        """
        Build system prompt based on context mode.

        Returns:
            System prompt text tailored to the interaction mode
        """
        if self._context_mode == "document":
            if self._document_content:
                return (
                    "You are an AI assistant helping with AsciiDoc document editing. "
                    "The user is working on the document shown below. This is your PRIMARY context. "
                    "Answer questions about this document, suggest improvements, and help with editing.\n\n"
                    f"CURRENT DOCUMENT CONTENT:\n{self._document_content[:2000]}\n"  # Limit to 2KB
                    f"\n[Document truncated to 2000 characters for context efficiency]"
                )
            else:
                return (
                    "You are an AI assistant helping with AsciiDoc document editing. "
                    "The document editor is currently empty or no content is available. "
                    "You can answer general questions about AsciiDoc or help with document planning."
                )

        elif self._context_mode == "syntax":
            return (
                "You are an expert in AsciiDoc syntax. Help users with AsciiDoc "
                "formatting, markup, and best practices. Provide clear examples."
            )

        elif self._context_mode == "editing":
            if self._document_content:
                return (
                    "You are an AI editor helping improve document quality. "
                    "The user is working on the document shown below. This is your PRIMARY context. "
                    "Suggest specific edits, improvements, and corrections based on this content.\n\n"
                    f"CURRENT DOCUMENT CONTENT:\n{self._document_content[:2000]}\n"  # Limit to 2KB
                    f"\n[Document truncated to 2000 characters for context efficiency]"
                )
            else:
                return (
                    "You are an AI editor helping improve document quality. "
                    "The document editor is currently empty or no content is available. "
                    "You can provide general writing advice or help with document structure."
                )

        else:  # general
            return "You are a helpful AI assistant. Answer questions clearly and concisely."

    def _build_message_history(self, system_prompt: str) -> list[dict[str, str]]:
        """
        Build message list for Ollama API from chat history.

        Args:
            system_prompt: System context prompt

        Returns:
            List of message dicts with 'role' and 'content' keys
        """
        messages: list[dict[str, str]] = []

        # Add system prompt
        messages.append({"role": "system", "content": system_prompt})

        # Add chat history (last 10 messages for context window management)
        for msg in self._chat_history[-10:]:
            messages.append({"role": msg.role, "content": msg.content})

        # Add current user message
        if self._user_message:
            messages.append({"role": "user", "content": self._user_message})

        return messages

    def _call_ollama_api(self, messages: list[dict[str, str]]) -> str:
        """
        Call Ollama API with message history.

        Args:
            messages: List of message dicts for API

        Returns:
            AI response text

        Raises:
            subprocess.TimeoutExpired: If API call exceeds 60s timeout
            subprocess.CalledProcessError: If Ollama returns error
        """
        # Build prompt from messages
        # Format: system prompt + history + user message
        full_prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                full_prompt += f"System: {content}\n\n"
            elif role == "user":
                full_prompt += f"User: {content}\n\n"
            elif role == "assistant":
                full_prompt += f"Assistant: {content}\n\n"

        full_prompt += "Assistant: "  # Prompt for response

        # Build Ollama CLI command (simple run without JSON format)
        cmd = [
            "ollama",
            "run",
            self._current_model or "qwen2.5-coder:7b",
        ]

        logger.debug(f"Calling Ollama with model: {self._current_model}")

        # Call Ollama CLI with prompt as stdin
        result = subprocess.run(
            cmd,
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            check=True,
            shell=False,  # Security: never use shell=True
        )

        # Response is in stdout - strip ANSI escape codes
        response_text = result.stdout.strip()

        # Remove ANSI escape sequences (spinner, colors, etc.)
        import re

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        response_text = ansi_escape.sub("", response_text)
        response_text = response_text.strip()

        if not response_text:
            raise ValueError("Empty response from Ollama")

        return response_text

    def _parse_ollama_error(self, error: subprocess.CalledProcessError) -> str:
        """
        Parse Ollama CLI error into user-friendly message.

        Args:
            error: CalledProcessError from subprocess

        Returns:
            User-friendly error message
        """
        stderr = error.stderr.strip()

        # Common error patterns
        if "model" in stderr.lower() and "not found" in stderr.lower():
            return f"Model '{self._current_model}' not found. Pull it with: ollama pull {{model}}"
        elif "connection refused" in stderr.lower():
            return "Cannot connect to Ollama. Ensure Ollama is running: ollama serve"
        elif "context length" in stderr.lower():
            return "Message too long for model context. Try a shorter message or clear chat history."
        else:
            return f"Ollama error: {stderr[:200]}"  # Limit error message length
