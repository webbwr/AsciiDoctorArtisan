"""
Unit tests for Claude Worker.

Tests the ClaudeWorker class for asynchronous Claude API operations.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from PySide6.QtCore import QThread

from asciidoc_artisan.claude import ClaudeWorker, ClaudeClient, ClaudeResult, ClaudeMessage


@pytest.mark.unit
class TestClaudeWorker:
    """Test ClaudeWorker for async Claude API operations."""

    def test_claude_worker_initialization(self):
        """Test ClaudeWorker can be instantiated."""
        worker = ClaudeWorker()

        assert worker is not None
        assert isinstance(worker, QThread)
        assert worker.client is not None
        assert isinstance(worker.client, ClaudeClient)
        assert worker.client.model == ClaudeClient.DEFAULT_MODEL

    def test_claude_worker_custom_params(self):
        """Test ClaudeWorker with custom parameters."""
        worker = ClaudeWorker(
            model="claude-3-5-haiku-20241022", max_tokens=2048, temperature=0.7
        )

        assert worker.client.model == "claude-3-5-haiku-20241022"
        assert worker.client.max_tokens == 2048
        assert worker.client.temperature == 0.7

    def test_is_configured_delegates_to_client(self):
        """Test is_configured delegates to ClaudeClient."""
        worker = ClaudeWorker()

        with patch.object(worker.client, "is_configured", return_value=True):
            assert worker.is_configured() is True

        with patch.object(worker.client, "is_configured", return_value=False):
            assert worker.is_configured() is False

    def test_get_available_models_delegates_to_client(self):
        """Test get_available_models delegates to ClaudeClient."""
        worker = ClaudeWorker()

        models = worker.get_available_models()
        assert isinstance(models, list)
        assert "claude-3-5-sonnet-20241022" in models

    def test_set_model(self):
        """Test set_model updates client model."""
        worker = ClaudeWorker()

        worker.set_model("claude-3-5-haiku-20241022")
        assert worker.client.model == "claude-3-5-haiku-20241022"

    def test_set_max_tokens(self):
        """Test set_max_tokens updates client max_tokens."""
        worker = ClaudeWorker()

        worker.set_max_tokens(8192)
        assert worker.client.max_tokens == 8192

    def test_set_temperature(self):
        """Test set_temperature updates client temperature."""
        worker = ClaudeWorker()

        worker.set_temperature(0.5)
        assert worker.client.temperature == 0.5

    def test_send_message_starts_worker_thread(self):
        """Test send_message starts the worker thread."""
        worker = ClaudeWorker()

        with patch.object(worker, "start") as mock_start:
            worker.send_message("Hello")
            mock_start.assert_called_once()

    def test_send_message_while_running_emits_error(self, qtbot):
        """Test send_message while running emits error."""
        worker = ClaudeWorker()

        # Mock worker as running
        with patch.object(worker, "isRunning", return_value=True):
            with qtbot.waitSignal(worker.error_occurred, timeout=1000) as blocker:
                worker.send_message("Hello")

            assert "busy" in blocker.args[0].lower()

    def test_send_message_sets_operation_state(self):
        """Test send_message sets internal state correctly."""
        worker = ClaudeWorker()

        with patch.object(worker, "start"):
            worker.send_message(
                "Test message", system="System prompt", conversation_history=[]
            )

            assert worker._operation == "send_message"
            assert worker._current_message == "Test message"
            assert worker._current_system == "System prompt"
            assert worker._current_history == []

    def test_test_connection_starts_worker_thread(self):
        """Test test_connection starts the worker thread."""
        worker = ClaudeWorker()

        with patch.object(worker, "start") as mock_start:
            worker.test_connection()
            mock_start.assert_called_once()

    def test_test_connection_while_running_emits_error(self, qtbot):
        """Test test_connection while running emits error."""
        worker = ClaudeWorker()

        # Mock worker as running
        with patch.object(worker, "isRunning", return_value=True):
            with qtbot.waitSignal(worker.error_occurred, timeout=1000) as blocker:
                worker.test_connection()

            assert "busy" in blocker.args[0].lower()

    def test_test_connection_sets_operation_state(self):
        """Test test_connection sets internal state correctly."""
        worker = ClaudeWorker()

        with patch.object(worker, "start"):
            worker.test_connection()
            assert worker._operation == "test_connection"

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_emits_response_ready(
        self, mock_credentials, mock_anthropic, qtbot
    ):
        """Test successful message send emits response_ready."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_response = Mock()
        mock_response.content = [Mock(text="Hello! I'm Claude.")]
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = Mock(input_tokens=10, output_tokens=15)

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Execute
        worker = ClaudeWorker()

        with qtbot.waitSignal(worker.response_ready, timeout=5000) as blocker:
            worker.send_message("Hello Claude!")

        # Verify
        result = blocker.args[0]
        assert isinstance(result, ClaudeResult)
        assert result.success is True
        assert result.content == "Hello! I'm Claude."
        assert result.model == "claude-3-5-sonnet-20241022"
        assert result.tokens_used == 25

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_test_connection_emits_connection_tested(
        self, mock_credentials, mock_anthropic, qtbot
    ):
        """Test successful connection test emits connection_tested."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_response = Mock()
        mock_response.content = [Mock(text="Connection OK")]
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = Mock(input_tokens=5, output_tokens=3)

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Execute
        worker = ClaudeWorker()

        with qtbot.waitSignal(worker.connection_tested, timeout=5000) as blocker:
            worker.test_connection()

        # Verify
        result = blocker.args[0]
        assert isinstance(result, ClaudeResult)
        assert result.success is True
        assert "Connection OK" in result.content

    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_without_api_key_emits_response(
        self, mock_credentials, qtbot
    ):
        """Test send_message without API key emits error response."""
        # Setup mock
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = None
        mock_credentials.return_value = mock_creds

        # Execute
        worker = ClaudeWorker()

        with qtbot.waitSignal(worker.response_ready, timeout=5000) as blocker:
            worker.send_message("Hello")

        # Verify
        result = blocker.args[0]
        assert isinstance(result, ClaudeResult)
        assert result.success is False
        assert "not configured" in result.error.lower()

    def test_unknown_operation_emits_error(self, qtbot):
        """Test unknown operation emits error."""
        worker = ClaudeWorker()

        # Set invalid operation
        worker._operation = "invalid_operation"

        with qtbot.waitSignal(worker.error_occurred, timeout=5000) as blocker:
            worker.start()
            worker.wait()  # Wait for thread to finish

        assert "unknown operation" in blocker.args[0].lower()

    def test_exception_in_run_emits_error(self, qtbot):
        """Test exception in run() emits error."""
        worker = ClaudeWorker()

        # Patch _execute_send_message to raise exception
        with patch.object(
            worker, "_execute_send_message", side_effect=Exception("Test error")
        ):
            worker._operation = "send_message"

            with qtbot.waitSignal(worker.error_occurred, timeout=5000) as blocker:
                worker.start()
                worker.wait()

            assert "worker error" in blocker.args[0].lower()

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_with_conversation_history(
        self, mock_credentials, mock_anthropic, qtbot
    ):
        """Test send_message with conversation history."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = Mock(input_tokens=20, output_tokens=10)

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Execute
        history = [
            ClaudeMessage(role="user", content="First message"),
            ClaudeMessage(role="assistant", content="First response"),
        ]

        worker = ClaudeWorker()

        with qtbot.waitSignal(worker.response_ready, timeout=5000) as blocker:
            worker.send_message("Second message", conversation_history=history)

        # Verify
        result = blocker.args[0]
        assert result.success is True

        # Verify history was passed to API
        call_kwargs = mock_client.messages.create.call_args[1]
        messages = call_kwargs["messages"]
        assert len(messages) == 3  # 2 from history + 1 current
        assert messages[0]["content"] == "First message"
        assert messages[1]["content"] == "First response"
        assert messages[2]["content"] == "Second message"
