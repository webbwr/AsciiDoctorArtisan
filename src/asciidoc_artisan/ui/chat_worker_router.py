"""
Chat Worker Router - Routes chat messages to appropriate AI backends.

Extracted from main_window.py per MA principle (reduce file size).

Handles routing between:
- Ollama backend
- Claude backend

MA Principle: This class (~100 lines) was extracted from main_window.py
to reduce its line count and improve maintainability.
"""

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Slot

if TYPE_CHECKING:
    from asciidoc_artisan.ui.main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class ChatWorkerRouter:
    """
    Routes chat messages to appropriate AI workers based on active backend.

    MA principle: Extracted from main_window.py (~113 lines → dedicated class).
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize ChatWorkerRouter with reference to main editor."""
        self.editor = editor

    @Slot(str, str, str, list, object)
    def route_message(
        self,
        message: str,
        model: str,
        context_mode: str,
        history: list[Any],
        document_content: Any,
    ) -> None:
        """
        Route chat message to appropriate AI worker based on active backend.

        Args:
            message: User message text
            model: Selected model name
            context_mode: Context mode (document, syntax, general, editing)
            history: Chat history (list of ChatMessage objects)
            document_content: Current document content (optional)
        """
        backend = self.editor._settings.ai_backend
        logger.info(f"Routing message to {backend} backend (model: {model})")

        if backend == "ollama":
            # Route to Ollama worker
            self.editor.ollama_chat_worker.send_message(message, model, context_mode, history, document_content)
        elif backend == "claude":
            # Route to Claude worker with context-appropriate system prompt
            self._route_to_claude(message, model, context_mode, history, document_content)
        else:
            logger.error(f"Unknown AI backend: {backend}")
            self.editor.status_manager.show_status(f"Error: Unknown AI backend '{backend}'")

    def _route_to_claude(
        self,
        message: str,
        model: str,
        context_mode: str,
        history: list[Any],
        document_content: Any,
    ) -> None:
        """Route message to Claude worker with proper formatting."""
        from asciidoc_artisan.claude import ClaudeMessage

        system_prompt = self._build_system_prompt(context_mode, model)

        # Convert ChatMessage history to ClaudeMessage format
        claude_history = []
        for msg in history:
            if hasattr(msg, "role") and hasattr(msg, "content"):
                claude_history.append(ClaudeMessage(role=msg.role, content=msg.content))

        # Build full message with document context if needed
        full_message = message
        if context_mode in ("document", "editing") and document_content:
            full_message = f"Document content:\n```\n{document_content}\n```\n\nUser question: {message}"

        # Send to Claude worker
        self.editor.claude_worker.send_message(
            message=full_message,
            system=system_prompt,
            conversation_history=claude_history,
        )

    def _build_system_prompt(self, context_mode: str, model: str) -> str:
        """
        Build system prompt for Claude based on context mode.

        Args:
            context_mode: Context mode (document, syntax, general, editing)
            model: Selected Claude model

        Returns:
            System prompt string
        """
        if context_mode == "document":
            return (
                "You are an expert assistant helping with AsciiDoc document questions. "
                "Analyze the provided document content and answer questions about it. "
                "Be concise and accurate."
            )
        elif context_mode == "syntax":
            return (
                "You are an AsciiDoc syntax expert. Help users with AsciiDoc formatting, "
                "markup, and best practices. Provide clear examples when helpful."
            )
        elif context_mode == "editing":
            return (
                "You are a document editing assistant for AsciiDoc content. Provide "
                "suggestions to improve the document's clarity, structure, and quality. "
                "Focus on content, not just formatting."
            )
        else:  # general
            return "You are a helpful AI assistant. Answer questions clearly and concisely."

    @Slot(object)
    def adapt_claude_response(self, claude_result: object) -> None:
        """
        Adapt ClaudeResult to ChatMessage and pass to ChatManager.

        Args:
            claude_result: ClaudeResult object from ClaudeWorker
        """
        import time

        from asciidoc_artisan.core.models import ChatMessage

        # Check if result is successful
        if not claude_result.success:
            # Handle error
            error_msg = claude_result.error or "Unknown error"
            self.editor.chat_manager.handle_error(error_msg)
            return

        # Convert ClaudeResult to ChatMessage
        chat_message = ChatMessage(
            role="assistant",
            content=claude_result.content,
            timestamp=int(time.time()),
            model=claude_result.model,
            context_mode=self.editor._settings.chat_context_mode,
        )

        # Pass to ChatManager
        self.editor.chat_manager.handle_response_ready(chat_message)
        logger.info(f"Claude response adapted and forwarded to ChatManager ({claude_result.tokens_used} tokens used)")
