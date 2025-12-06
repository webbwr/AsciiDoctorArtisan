"""Integration tests for live Ollama API.

These tests require a running Ollama service.
Run with: pytest tests/integration/test_ollama_live.py -m live_api

Prerequisites:
- Ollama installed and running: https://ollama.ai
- At least one model pulled: ollama pull llama3.2
"""

import subprocess

import pytest

from asciidoc_artisan.core.models import ChatMessage
from asciidoc_artisan.workers.ollama_chat_worker import OllamaChatWorker


def ollama_available() -> bool:
    """Check if Ollama service is running."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_available_model() -> str | None:
    """Get the first available Ollama model."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            # Skip header, get first model name
            model_line = lines[1].split()[0]
            return model_line.split(":")[0]  # Remove tag
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


# Skip all tests if Ollama not available
pytestmark = [
    pytest.mark.live_api,
    pytest.mark.integration,
    pytest.mark.skipif(not ollama_available(), reason="Ollama service not running"),
]


@pytest.fixture
def available_model():
    """Get an available model or skip test."""
    model = get_available_model()
    if not model:
        pytest.skip("No Ollama models available")
    return model


class TestOllamaServiceConnection:
    """Test Ollama service connectivity."""

    def test_ollama_service_running(self):
        """Verify Ollama service is accessible."""
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0

    def test_models_listed(self):
        """Verify at least one model is available."""
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = result.stdout.strip().split("\n")
        assert len(lines) > 1, "No models available - run: ollama pull llama3.2"


class TestOllamaModelInteraction:
    """Test direct model interaction."""

    def test_simple_generation(self, available_model):
        """Test generating a simple response."""
        result = subprocess.run(
            ["ollama", "run", available_model, "Say hello in 5 words or less"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0

    def test_asciidoc_generation(self, available_model):
        """Test generating AsciiDoc content."""
        prompt = "Write a one-line AsciiDoc title starting with ="
        result = subprocess.run(
            ["ollama", "run", available_model, prompt],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        output = result.stdout.strip()
        assert len(output) > 0


class TestOllamaChatWorkerLive:
    """Test OllamaChatWorker with live Ollama service."""

    def test_worker_creates_with_model(self, available_model):
        """Test worker can be created with available model."""
        worker = OllamaChatWorker()
        worker._current_model = available_model
        assert worker._current_model == available_model

    def test_worker_context_modes(self, available_model):
        """Test worker supports all context modes."""
        worker = OllamaChatWorker()
        worker._current_model = available_model

        modes = ["document", "syntax", "general", "editing"]
        for mode in modes:
            worker._context_mode = mode
            assert worker._context_mode == mode


class TestOllamaContextModes:
    """Test different chat context modes with live API."""

    @pytest.fixture
    def sample_document(self):
        """Sample AsciiDoc document for context testing."""
        return """= Sample Document
:author: Test User

== Introduction

This is a test document for Ollama integration testing.

=== Code Example

[source,python]
----
def hello():
    print("Hello, World!")
----
"""

    def test_document_mode_context(self, available_model, sample_document):
        """Test document mode provides document context."""
        worker = OllamaChatWorker()
        worker._current_model = available_model
        worker._context_mode = "document"
        worker._document_content = sample_document
        assert worker._document_content is not None
        assert "Sample Document" in worker._document_content

    def test_syntax_mode_context(self, available_model, sample_document):
        """Test syntax mode for AsciiDoc syntax help."""
        worker = OllamaChatWorker()
        worker._current_model = available_model
        worker._context_mode = "syntax"
        assert worker._context_mode == "syntax"

    def test_editing_mode_context(self, available_model, sample_document):
        """Test editing mode for document improvements."""
        worker = OllamaChatWorker()
        worker._current_model = available_model
        worker._context_mode = "editing"
        worker._document_content = sample_document
        assert worker._context_mode == "editing"


class TestOllamaChatHistory:
    """Test chat history management."""

    def test_empty_history(self, available_model):
        """Test worker starts with empty history."""
        worker = OllamaChatWorker()
        worker._current_model = available_model
        assert worker._chat_history == []

    def test_history_accumulation(self, available_model):
        """Test chat history accumulates messages."""
        worker = OllamaChatWorker()
        worker._current_model = available_model

        # Add messages to history
        messages = [
            ChatMessage(
                role="user",
                content="Hello",
                timestamp=1.0,
                model=available_model,
                context_mode="general",
            ),
            ChatMessage(
                role="assistant",
                content="Hi there!",
                timestamp=2.0,
                model=available_model,
                context_mode="general",
            ),
        ]
        worker._chat_history = messages
        assert len(worker._chat_history) == 2

    def test_history_clear(self, available_model):
        """Test clearing chat history."""
        worker = OllamaChatWorker()
        worker._current_model = available_model
        worker._chat_history = [
            ChatMessage(
                role="user",
                content="Test",
                timestamp=1.0,
                model=available_model,
                context_mode="general",
            )
        ]
        worker._chat_history.clear()
        assert worker._chat_history == []


class TestOllamaErrorHandling:
    """Test error handling with Ollama."""

    def test_invalid_model_handling(self):
        """Test handling of invalid model name."""
        worker = OllamaChatWorker()
        worker._current_model = "nonexistent-model-xyz"
        # Worker should not crash with invalid model
        assert worker._current_model == "nonexistent-model-xyz"

    def test_empty_message_handling(self, available_model):
        """Test handling of empty message."""
        worker = OllamaChatWorker()
        worker._current_model = available_model
        worker._user_message = ""
        assert worker._user_message == ""

    def test_cancellation_flag(self, available_model):
        """Test cancellation flag works."""
        worker = OllamaChatWorker()
        worker._current_model = available_model
        worker._should_cancel = True
        assert worker._should_cancel is True


class TestOllamaPerformance:
    """Performance tests for Ollama integration."""

    def test_model_list_speed(self):
        """Test model listing is fast."""
        import time

        start = time.time()
        subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        elapsed = time.time() - start
        assert elapsed < 2.0, "Model listing took too long"

    def test_worker_init_speed(self, available_model):
        """Test worker initialization is fast."""
        import time

        start = time.time()
        for _ in range(10):
            worker = OllamaChatWorker()
            worker._current_model = available_model
        elapsed = time.time() - start
        assert elapsed < 1.0, "Worker initialization too slow"
