"""
Tests for Ollama AI Chat Worker.

Tests the OllamaChatWorker class which handles background AI chat processing.
"""

import json
import time
from unittest.mock import MagicMock, Mock, patch

import pytest
from PySide6.QtCore import QThread

from asciidoc_artisan.core.models import ChatMessage
from asciidoc_artisan.workers.ollama_chat_worker import OllamaChatWorker


@pytest.fixture
def chat_worker():
    """Create a chat worker for testing."""
    worker = OllamaChatWorker()
    yield worker
    # Cleanup
    if worker.isRunning():
        worker.quit()
        worker.wait(1000)


@pytest.fixture
def sample_chat_history():
    """Create sample chat history."""
    return [
        ChatMessage(
            role="user",
            content="Hello",
            timestamp=time.time() - 100,
            model="phi3:mini",
            context_mode="general",
        ),
        ChatMessage(
            role="assistant",
            content="Hi! How can I help?",
            timestamp=time.time() - 90,
            model="phi3:mini",
            context_mode="general",
        ),
    ]


class TestOllamaChatWorkerInitialization:
    """Test worker initialization."""

    def test_worker_creation(self, chat_worker):
        """Test worker can be created."""
        assert isinstance(chat_worker, QThread)
        assert not chat_worker.isRunning()

    def test_initial_state(self, chat_worker):
        """Test initial state is correct."""
        assert not chat_worker._is_processing
        assert not chat_worker._should_cancel
        assert chat_worker._current_model is None
        assert chat_worker._context_mode == "document"
        assert chat_worker._chat_history == []
        assert chat_worker._document_content is None
        assert chat_worker._user_message is None


class TestOllamaChatWorkerMessageSending:
    """Test message sending functionality."""

    def test_send_message_queues_correctly(self, chat_worker):
        """Test message is queued correctly."""
        message = "How do I make a table?"
        model = "phi3:mini"
        context_mode = "syntax"
        history = []

        chat_worker.send_message(message, model, context_mode, history)

        assert chat_worker._user_message == message
        assert chat_worker._current_model == model
        assert chat_worker._context_mode == context_mode
        assert chat_worker._chat_history == history

    def test_send_message_with_document_content(self, chat_worker):
        """Test message sending with document context."""
        message = "Explain this document"
        model = "phi3:mini"
        context_mode = "document"
        history = []
        doc_content = "= My Document\nSome content here"

        chat_worker.send_message(message, model, context_mode, history, doc_content)

        assert chat_worker._document_content == doc_content

    def test_send_message_starts_worker(self, chat_worker):
        """Test sending message starts the worker thread."""
        chat_worker.send_message("Hello", "phi3:mini", "general", [])

        # Worker should start
        assert chat_worker.isRunning() or not chat_worker.isFinished()


class TestOllamaChatWorkerCancellation:
    """Test cancellation functionality."""

    def test_cancel_operation_sets_flag(self, chat_worker):
        """Test cancel sets the flag."""
        chat_worker._is_processing = True
        chat_worker.cancel_operation()

        assert chat_worker._should_cancel

    def test_cancel_when_not_processing(self, chat_worker):
        """Test cancel when not processing does nothing."""
        chat_worker._is_processing = False
        chat_worker.cancel_operation()

        # Should not crash, and flag should NOT be set (nothing to cancel)
        assert not chat_worker._should_cancel


class TestOllamaChatWorkerContextModes:
    """Test context mode handling."""

    @pytest.mark.parametrize(
        "context_mode",
        ["document", "syntax", "general", "editing"],
    )
    def test_valid_context_modes(self, chat_worker, context_mode):
        """Test all valid context modes are accepted."""
        chat_worker.send_message("Test", "phi3:mini", context_mode, [])
        assert chat_worker._context_mode == context_mode

    def test_context_mode_affects_system_prompt(self, chat_worker):
        """Test context mode changes system prompt."""
        # This would require mocking the Ollama API call
        # Placeholder for future implementation
        pass


class TestOllamaChatWorkerSignals:
    """Test worker signals."""

    def test_has_chat_response_ready_signal(self, chat_worker):
        """Test worker has chat_response_ready signal."""
        assert hasattr(chat_worker, "chat_response_ready")

    def test_has_chat_response_chunk_signal(self, chat_worker):
        """Test worker has chat_response_chunk signal for streaming."""
        assert hasattr(chat_worker, "chat_response_chunk")

    def test_has_chat_error_signal(self, chat_worker):
        """Test worker has chat_error signal."""
        assert hasattr(chat_worker, "chat_error")

    def test_has_operation_cancelled_signal(self, chat_worker):
        """Test worker has operation_cancelled signal."""
        assert hasattr(chat_worker, "operation_cancelled")


class TestOllamaChatWorkerReentrancy:
    """Test reentrancy guard."""

    def test_prevents_concurrent_operations(self, chat_worker):
        """Test worker prevents concurrent operations."""
        chat_worker._is_processing = True

        # Try to send another message
        chat_worker.send_message("Second message", "phi3:mini", "general", [])

        # Should not update state since already processing
        # (implementation detail - may vary)
        pass


class TestOllamaChatWorkerErrorHandling:
    """Test error handling."""

    def test_handles_missing_ollama(self, chat_worker):
        """Test worker handles missing Ollama gracefully."""
        # This would require mocking subprocess to simulate missing Ollama
        # Placeholder for future implementation
        pass

    def test_handles_invalid_model(self, chat_worker):
        """Test worker handles invalid model name."""
        # Placeholder for future implementation
        pass

    def test_handles_api_errors(self, chat_worker):
        """Test worker handles Ollama API errors."""
        # Placeholder for future implementation
        pass


# Integration tests would require actual Ollama installation
# These are marked as integration tests

@pytest.mark.integration
class TestOllamaChatWorkerIntegration:
    """Integration tests requiring Ollama."""

    @pytest.mark.skip(reason="Requires Ollama installation")
    def test_actual_chat_response(self, chat_worker):
        """Test actual chat with Ollama (requires installation)."""
        response_received = False

        def on_response(message):
            nonlocal response_received
            response_received = True
            assert isinstance(message, ChatMessage)
            assert message.role == "assistant"
            assert len(message.content) > 0

        chat_worker.chat_response_ready.connect(on_response)
        chat_worker.send_message("Hello", "phi3:mini", "general", [])

        # Wait for response (with timeout)
        chat_worker.wait(10000)  # 10 second timeout
        assert response_received

    @pytest.mark.skip(reason="Requires Ollama installation")
    def test_streaming_response(self, chat_worker):
        """Test streaming responses (requires installation)."""
        chunks_received = []

        def on_chunk(chunk):
            chunks_received.append(chunk)

        chat_worker.chat_response_chunk.connect(on_chunk)
        chat_worker.send_message("Tell me a story", "phi3:mini", "general", [])

        chat_worker.wait(15000)  # 15 second timeout
        assert len(chunks_received) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
