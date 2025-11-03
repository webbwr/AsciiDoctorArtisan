"""
Claude AI Integration Module for AsciiDoc Artisan.

This module provides integration with Anthropic's Claude AI API for:
- Document analysis and Q&A
- Writing assistance and improvements
- Code explanation and generation
- Markdown/AsciiDoc conversion
- General AI-powered document assistance

The integration follows the same patterns as Ollama integration but uses
cloud-based Claude models via the Anthropic API.

Architecture:
- ClaudeClient: Main API client (synchronous)
- ClaudeWorker: QThread worker for async operations (non-blocking UI)
- Secure credential storage via OS keyring

Example:
    >>> from asciidoc_artisan.claude import ClaudeClient, ClaudeWorker
    >>> client = ClaudeClient()
    >>> if client.is_configured():
    ...     response = client.send_message("Explain AsciiDoc syntax")
    ...     print(response)
"""

from .claude_client import ClaudeClient, ClaudeResult, ClaudeMessage
from .claude_worker import ClaudeWorker

__all__ = [
    "ClaudeClient",
    "ClaudeResult",
    "ClaudeMessage",
    "ClaudeWorker",
]
