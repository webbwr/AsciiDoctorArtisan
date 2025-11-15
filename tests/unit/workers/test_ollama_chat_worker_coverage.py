"""
Extended tests for ollama_chat_worker to achieve 100% coverage.

Tests for missing lines:
- Lines 303-304: Assistant role in message formatting
- Line 339: ValueError for empty Ollama response
- Line 363: Generic error message in _parse_ollama_error
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.core.models import ChatMessage
from asciidoc_artisan.workers.ollama_chat_worker import OllamaChatWorker


@pytest.mark.fr_039
@pytest.mark.fr_040
@pytest.mark.fr_041
@pytest.mark.fr_042
@pytest.mark.fr_043
@pytest.mark.fr_044
@pytest.mark.fr_076
@pytest.mark.unit
class TestOllamaChatWorkerCoverage:
    """Tests to achieve 100% coverage for OllamaChatWorker."""

    @patch("asciidoc_artisan.workers.ollama_chat_worker.subprocess.run")
    def test_assistant_role_in_messages(self, mock_run):
        """Test assistant role in message formatting (lines 303-304)."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="This is the assistant response",
            stderr="",
        )

        worker = OllamaChatWorker()
        result = None

        def capture_result(msg):
            nonlocal result
            result = msg

        worker.chat_response_ready.connect(capture_result)

        # Set up worker state with assistant message in history
        worker._user_message = "How are you?"
        worker._current_model = "llama2"
        worker._context_mode = "general"
        worker._document_content = ""
        worker._chat_history = [
            ChatMessage(
                role="user",
                content="Hello",
                timestamp=1.0,
                model="llama2",
                context_mode="document",
            ),
            ChatMessage(
                role="assistant",  # This will trigger lines 303-304
                content="Hi there! How can I help?",
                timestamp=2.0,
                model="llama2",
                context_mode="document",
            ),
        ]

        # Call _process_chat directly to test message formatting
        worker._process_chat()

        assert result is not None
        assert isinstance(result, ChatMessage)
        assert result.role == "assistant"

    @patch("asciidoc_artisan.workers.ollama_chat_worker.subprocess.run")
    def test_empty_response_from_ollama(self, mock_run):
        """Test ValueError when Ollama returns empty response (line 339)."""
        # Mock Ollama to return empty output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="   ",  # Whitespace only - will be empty after strip
            stderr="",
        )

        worker = OllamaChatWorker()
        error_msg = None

        def capture_error(msg):
            nonlocal error_msg
            error_msg = msg

        worker.chat_error.connect(capture_error)

        # Set up worker state
        worker._user_message = "Hello"
        worker._current_model = "llama2"
        worker._context_mode = "general"
        worker._document_content = ""
        worker._chat_history = []

        # Call _process_chat - should raise ValueError and emit error
        worker._process_chat()

        assert error_msg is not None
        assert "empty" in error_msg.lower()

    @patch("asciidoc_artisan.workers.ollama_chat_worker.subprocess.run")
    def test_parse_ollama_error_generic(self, mock_run):
        """Test generic error message parsing (line 363)."""
        # Create subprocess error with unknown error message
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd=["ollama", "run", "llama2"],
            stderr="Some weird unknown error message",
        )
        mock_run.side_effect = error

        worker = OllamaChatWorker()
        error_msg = None

        def capture_error(msg):
            nonlocal error_msg
            error_msg = msg

        worker.chat_error.connect(capture_error)

        # Set up worker state
        worker._user_message = "Hello"
        worker._current_model = "llama2"
        worker._context_mode = "general"
        worker._document_content = ""
        worker._chat_history = []

        # Call _process_chat - should trigger generic error (line 363)
        worker._process_chat()

        assert error_msg is not None
        assert "ollama error" in error_msg.lower()
        assert "weird unknown" in error_msg.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
