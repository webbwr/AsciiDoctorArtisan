"""
Unit tests for OllamaChatWorker class.

Tests Ollama AI chat worker for background chat processing with four
context modes: document, syntax, general, and editing.
"""

from unittest.mock import MagicMock, patch
import subprocess

import pytest

from asciidoc_artisan.workers.ollama_chat_worker import OllamaChatWorker
from asciidoc_artisan.core.models import ChatMessage


@pytest.mark.unit
class TestOllamaChatWorkerInitialization:
    """Test worker initialization."""

    def test_worker_initialization(self):
        """Test worker initializes with correct default state."""
        worker = OllamaChatWorker()

        assert worker is not None
        assert worker._is_processing is False
        assert worker._should_cancel is False
        assert worker._current_model is None
        assert worker._context_mode == "document"
        assert worker._chat_history == []
        assert worker._document_content is None
        assert worker._user_message is None

    def test_worker_has_required_signals(self):
        """Test worker defines all required signals."""
        worker = OllamaChatWorker()

        assert hasattr(worker, "chat_response_ready")
        assert hasattr(worker, "chat_response_chunk")
        assert hasattr(worker, "chat_error")
        assert hasattr(worker, "operation_cancelled")


@pytest.mark.unit
class TestSendMessage:
    """Test send_message method."""

    def test_send_message_sets_state(self):
        """Test send_message sets internal state correctly."""
        worker = OllamaChatWorker()
        history = [
            ChatMessage(
                role="user",
                content="Hello",
                timestamp=1.0,
                model="llama2",
                context_mode="document",
            ),
            ChatMessage(
                role="assistant",
                content="Hi",
                timestamp=2.0,
                model="llama2",
                context_mode="document",
            ),
        ]

        # Prevent worker from actually starting thread
        worker.start = MagicMock()

        worker.send_message(
            message="Test message",
            model="qwen2.5-coder:7b",
            context_mode="syntax",
            history=history,
            document_content="= Doc\n\nContent",
        )

        assert worker._user_message == "Test message"
        assert worker._current_model == "qwen2.5-coder:7b"
        assert worker._context_mode == "syntax"
        assert worker._chat_history == history
        assert worker._document_content == "= Doc\n\nContent"
        assert worker._should_cancel is False
        worker.start.assert_called_once()

    def test_send_message_when_busy_ignores_request(self):
        """Test send_message ignores request when already processing."""
        worker = OllamaChatWorker()
        worker._is_processing = True
        worker.start = MagicMock()

        worker.send_message(
            message="Test",
            model="llama2",
            context_mode="general",
            history=[],
            document_content=None,
        )

        # Should not start thread when busy
        worker.start.assert_not_called()
        # Should not update state
        assert worker._user_message is None


@pytest.mark.unit
class TestCancelOperation:
    """Test cancel_operation method."""

    def test_cancel_sets_flag_when_processing(self):
        """Test cancel sets cancellation flag when processing."""
        worker = OllamaChatWorker()
        worker._is_processing = True

        worker.cancel_operation()

        assert worker._should_cancel is True

    def test_cancel_when_not_processing_does_nothing(self):
        """Test cancel when not processing is safe."""
        worker = OllamaChatWorker()
        worker._is_processing = False
        worker._should_cancel = False

        worker.cancel_operation()

        # Should remain False (no side effects)
        assert worker._should_cancel is False


@pytest.mark.unit
class TestBuildSystemPrompt:
    """Test _build_system_prompt method for all context modes."""

    @pytest.mark.parametrize(
        "context_mode,document_content,expected_strings,not_expected_strings",
        [
            # Document mode with content
            (
                "document",
                "= My Document\n\nParagraph content here.",
                ["AsciiDoc document editing", "CURRENT DOCUMENT CONTENT", "My Document", "Paragraph content"],
                [],
            ),
            # Document mode without content
            (
                "document",
                None,
                ["AsciiDoc document editing", "empty or no content"],
                ["CURRENT DOCUMENT CONTENT"],
            ),
            # Syntax mode
            (
                "syntax",
                None,
                ["expert in AsciiDoc syntax"],
                [],
            ),
            # Editing mode with content
            (
                "editing",
                "= Draft\n\nNeeds improvement.",
                ["AI editor", "CURRENT DOCUMENT CONTENT", "Draft", "Needs improvement"],
                [],
            ),
            # Editing mode without content
            (
                "editing",
                None,
                ["AI editor", "empty or no content"],
                ["CURRENT DOCUMENT CONTENT"],
            ),
            # General mode
            (
                "general",
                None,
                ["helpful AI assistant", "clearly and concisely"],
                [],
            ),
        ],
        ids=[
            "document_with_content",
            "document_without_content",
            "syntax",
            "editing_with_content",
            "editing_without_content",
            "general",
        ],
    )
    def test_context_modes(
        self, context_mode, document_content, expected_strings, not_expected_strings
    ):
        """Test system prompts for all context modes with/without content."""
        worker = OllamaChatWorker()
        worker._context_mode = context_mode
        worker._document_content = document_content

        prompt = worker._build_system_prompt()

        # Check all expected strings are present
        for expected in expected_strings:
            assert expected in prompt, f"Expected '{expected}' in prompt for mode '{context_mode}'"

        # Check strings that should NOT be present
        for not_expected in not_expected_strings:
            assert (
                not_expected not in prompt
            ), f"Unexpected '{not_expected}' in prompt for mode '{context_mode}'"

        # Additional check for syntax mode (formatting OR markup)
        if context_mode == "syntax":
            assert "formatting" in prompt or "markup" in prompt

    def test_document_truncation_at_2000_chars(self):
        """Test document content is truncated to 2000 characters."""
        worker = OllamaChatWorker()
        worker._context_mode = "document"
        # Create >2000 char document
        worker._document_content = "= Title\n\n" + ("Content paragraph.\n" * 200)

        prompt = worker._build_system_prompt()

        # Should include truncation notice
        assert "truncated to 2000 characters" in prompt


@pytest.mark.unit
class TestBuildMessageHistory:
    """Test _build_message_history method."""

    def test_build_history_with_empty_history(self):
        """Test building message history with no prior messages."""
        worker = OllamaChatWorker()
        worker._user_message = "Hello"
        worker._chat_history = []

        messages = worker._build_message_history("System prompt here")

        # Should have system message + user message
        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "System prompt here"
        # Last message should be current user message
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "Hello"

    def test_build_history_with_existing_messages(self):
        """Test building message history with prior chat history."""
        worker = OllamaChatWorker()
        worker._user_message = "Follow-up question"
        worker._chat_history = [
            ChatMessage(
                role="user",
                content="First",
                timestamp=1.0,
                model="llama2",
                context_mode="general",
            ),
            ChatMessage(
                role="assistant",
                content="Response",
                timestamp=2.0,
                model="llama2",
                context_mode="general",
            ),
        ]

        messages = worker._build_message_history("System")

        # Should have: system + history (2) + current (1) = 4 messages
        assert len(messages) >= 4
        assert messages[0]["role"] == "system"
        # History messages should be included
        assert any(msg["content"] == "First" for msg in messages)
        assert any(msg["content"] == "Response" for msg in messages)
        # Current message should be last
        assert messages[-1]["content"] == "Follow-up question"


@pytest.mark.unit
class TestRunMethod:
    """Test run method (thread entry point)."""

    def test_run_without_message_emits_error(self):
        """Test run emits error when user message is None."""
        worker = OllamaChatWorker()
        worker._user_message = None
        worker._current_model = "llama2"
        error = None

        def capture_error(err):
            nonlocal error
            error = err

        worker.chat_error.connect(capture_error)
        worker.run()

        assert error is not None
        assert "missing message" in error.lower()

    def test_run_without_model_emits_error(self):
        """Test run emits error when model is None."""
        worker = OllamaChatWorker()
        worker._user_message = "Test"
        worker._current_model = None
        error = None

        def capture_error(err):
            nonlocal error
            error = err

        worker.chat_error.connect(capture_error)
        worker.run()

        assert error is not None
        assert "missing" in error.lower() and "model" in error.lower()

    @patch("asciidoc_artisan.workers.ollama_chat_worker.subprocess.run")
    def test_run_successful_response(self, mock_run):
        """Test run with successful Ollama API call."""
        # Mock successful API response
        mock_run.return_value = MagicMock(
            stdout='{"message":{"content":"AI response here"}}',
            returncode=0,
        )

        worker = OllamaChatWorker()
        worker._user_message = "Test question"
        worker._current_model = "llama2"
        worker._context_mode = "general"
        worker._chat_history = []

        result = None

        def capture_result(msg):
            nonlocal result
            result = msg

        worker.chat_response_ready.connect(capture_result)
        worker.run()

        assert result is not None
        assert isinstance(result, ChatMessage)
        assert result.role == "assistant"
        assert "AI response" in result.content

    @patch("asciidoc_artisan.workers.ollama_chat_worker.subprocess.run")
    def test_run_timeout_error(self, mock_run):
        """Test run handles timeout error."""
        mock_run.side_effect = subprocess.TimeoutExpired("ollama", 60)

        worker = OllamaChatWorker()
        worker._user_message = "Test"
        worker._current_model = "llama2"
        worker._context_mode = "general"
        worker._chat_history = []

        error = None

        def capture_error(err):
            nonlocal error
            error = err

        worker.chat_error.connect(capture_error)
        worker.run()

        assert error is not None
        assert "timed out" in error.lower() or "timeout" in error.lower()

    @patch("asciidoc_artisan.workers.ollama_chat_worker.subprocess.run")
    def test_run_api_error(self, mock_run):
        """Test run handles API error."""
        # Create mock error with proper stderr attribute
        error = subprocess.CalledProcessError(1, "ollama")
        error.stderr = "Model not found"  # Use string, not bytes
        mock_run.side_effect = error

        worker = OllamaChatWorker()
        worker._user_message = "Test"
        worker._current_model = "invalid-model"
        worker._context_mode = "general"
        worker._chat_history = []

        error_msg = None

        def capture_error(err):
            nonlocal error_msg
            error_msg = err

        worker.chat_error.connect(capture_error)
        worker.run()

        assert error_msg is not None

    @patch("asciidoc_artisan.workers.ollama_chat_worker.subprocess.run")
    def test_run_clears_state_after_completion(self, mock_run):
        """Test run clears processing state after completion."""
        mock_run.return_value = MagicMock(
            stdout='{"message":{"content":"Response"}}',
            returncode=0,
        )

        worker = OllamaChatWorker()
        worker._user_message = "Test"
        worker._current_model = "llama2"
        worker._context_mode = "general"
        worker._chat_history = []

        worker.run()

        # State should be cleared
        assert worker._is_processing is False
        assert worker._user_message is None

    @patch("asciidoc_artisan.workers.ollama_chat_worker.subprocess.run")
    def test_run_respects_cancellation(self, mock_run):
        """Test run respects cancellation flag."""
        mock_run.return_value = MagicMock(
            stdout='{"message":{"content":"Response"}}',
            returncode=0,
        )

        worker = OllamaChatWorker()
        worker._user_message = "Test"
        worker._current_model = "llama2"
        worker._context_mode = "general"
        worker._chat_history = []
        worker._should_cancel = True  # Set cancellation flag

        cancelled = False

        def capture_cancel():
            nonlocal cancelled
            cancelled = True

        worker.operation_cancelled.connect(capture_cancel)
        worker.run()

        # Should emit cancellation signal
        assert cancelled is True


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in various scenarios."""

    @patch("asciidoc_artisan.workers.ollama_chat_worker.subprocess.run")
    def test_unexpected_exception(self, mock_run):
        """Test handling of unexpected exceptions."""
        mock_run.side_effect = Exception("Unexpected error")

        worker = OllamaChatWorker()
        worker._user_message = "Test"
        worker._current_model = "llama2"
        worker._context_mode = "general"
        worker._chat_history = []

        error = None

        def capture_error(err):
            nonlocal error
            error = err

        worker.chat_error.connect(capture_error)
        worker.run()

        assert error is not None
        assert "unexpected" in error.lower() or "error" in error.lower()
