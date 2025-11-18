"""
Unit tests for Claude Worker.

Tests the ClaudeWorker class for asynchronous Claude API operations.
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QThread

from asciidoc_artisan.claude import (
    ClaudeClient,
    ClaudeMessage,
    ClaudeResult,
    ClaudeWorker,
)


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
        worker = ClaudeWorker(model="claude-haiku-4-5", max_tokens=2048, temperature=0.7)

        assert worker.client.model == "claude-haiku-4-5"
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
        assert len(models) > 0  # Should have at least one model
        # Check for any current Claude model (names change with updates)
        assert any("claude" in model.lower() for model in models)

    def test_set_model(self):
        """Test set_model updates client model."""
        worker = ClaudeWorker()

        worker.set_model("claude-haiku-4-5")
        assert worker.client.model == "claude-haiku-4-5"

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
            worker.send_message("Test message", system="System prompt", conversation_history=[])

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

    def test_send_message_emits_response_ready(self, qtbot):
        """Test successful message send emits response_ready."""
        # Create worker
        worker = ClaudeWorker()

        # Mock the ClaudeClient.send_message method directly
        mock_result = ClaudeResult(
            success=True,
            content="Hello! I'm Claude.",
            model="claude-sonnet-4-20250514",
            tokens_used=25,
            error=None,
            stop_reason="end_turn",
        )

        with patch.object(worker.client, "send_message", return_value=mock_result):
            with qtbot.waitSignal(worker.response_ready, timeout=5000) as blocker:
                worker.send_message("Hello Claude!")

        # Verify
        result = blocker.args[0]
        assert isinstance(result, ClaudeResult)
        assert result.success is True
        assert result.content == "Hello! I'm Claude."
        assert result.model == "claude-sonnet-4-20250514"
        assert result.tokens_used == 25

    def test_test_connection_emits_connection_tested(self, qtbot):
        """Test successful connection test emits connection_tested."""
        # Create worker
        worker = ClaudeWorker()

        # Mock the ClaudeClient.test_connection method directly
        mock_result = ClaudeResult(
            success=True,
            content="Connection OK",
            model="claude-sonnet-4-20250514",
            tokens_used=8,
            error=None,
            stop_reason="end_turn",
        )

        with patch.object(worker.client, "test_connection", return_value=mock_result):
            with qtbot.waitSignal(worker.connection_tested, timeout=5000) as blocker:
                worker.test_connection()

        # Verify
        result = blocker.args[0]
        assert isinstance(result, ClaudeResult)
        assert result.success is True
        assert "Connection OK" in result.content

    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_without_api_key_emits_response(self, mock_credentials, qtbot):
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
        with patch.object(worker, "_execute_send_message", side_effect=Exception("Test error")):
            worker._operation = "send_message"

            with qtbot.waitSignal(worker.error_occurred, timeout=5000) as blocker:
                worker.start()
                worker.wait()

            assert "worker error" in blocker.args[0].lower()

    def test_send_message_with_conversation_history(self, qtbot):
        """Test send_message with conversation history."""
        # Create worker
        worker = ClaudeWorker()

        # Mock the ClaudeClient.send_message method directly
        mock_result = ClaudeResult(
            success=True,
            content="Response",
            model="claude-sonnet-4-20250514",
            tokens_used=30,
            error=None,
            stop_reason="end_turn",
        )

        # Execute
        history = [
            ClaudeMessage(role="user", content="First message"),
            ClaudeMessage(role="assistant", content="First response"),
        ]

        with patch.object(worker.client, "send_message", return_value=mock_result) as mock_send:
            with qtbot.waitSignal(worker.response_ready, timeout=5000) as blocker:
                worker.send_message("Second message", conversation_history=history)

        # Verify
        result = blocker.args[0]
        assert result.success is True

        # Verify history was passed to client
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["conversation_history"] == history
        assert call_kwargs["message"] == "Second message"

    def test_execute_send_message_directly(self):
        """Test _execute_send_message method coverage."""
        worker = ClaudeWorker()
        worker._current_message = "Test"
        worker._current_system = None
        worker._current_history = []

        mock_result = ClaudeResult(
            success=True,
            content="Response",
            model="claude-sonnet-4-20250514",
            tokens_used=10,
            error=None,
            stop_reason="end_turn",
        )

        with patch.object(worker.client, "send_message", return_value=mock_result):
            # Directly call the private method to ensure coverage
            worker._execute_send_message()

        # Method should complete without error

    def test_execute_test_connection_directly(self):
        """Test _execute_test_connection method coverage."""
        worker = ClaudeWorker()

        mock_result = ClaudeResult(
            success=True,
            content="OK",
            model="claude-sonnet-4-20250514",
            tokens_used=5,
            error=None,
            stop_reason="end_turn",
        )

        with patch.object(worker.client, "test_connection", return_value=mock_result):
            # Directly call the private method to ensure coverage
            worker._execute_test_connection()

        # Method should complete without error

    def test_run_with_send_message_operation(self):
        """Test run() method with send_message operation."""
        worker = ClaudeWorker()
        worker._operation = "send_message"
        worker._current_message = "Test"
        worker._current_system = None
        worker._current_history = []

        mock_result = ClaudeResult(
            success=True,
            content="Response",
            model="claude-sonnet-4-20250514",
            tokens_used=10,
            error=None,
            stop_reason="end_turn",
        )

        with patch.object(worker.client, "send_message", return_value=mock_result):
            # Call run() directly to cover the if/elif branches
            worker.run()

        # Should complete without raising exception

    def test_run_with_test_connection_operation(self):
        """Test run() method with test_connection operation."""
        worker = ClaudeWorker()
        worker._operation = "test_connection"

        mock_result = ClaudeResult(
            success=True,
            content="OK",
            model="claude-sonnet-4-20250514",
            tokens_used=5,
            error=None,
            stop_reason="end_turn",
        )

        with patch.object(worker.client, "test_connection", return_value=mock_result):
            # Call run() directly to cover the if/elif branches
            worker.run()

        # Should complete without raising exception
