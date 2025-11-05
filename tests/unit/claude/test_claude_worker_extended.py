"""
Extended unit tests for ClaudeWorker - Coverage completion.

This test suite covers remaining uncovered code paths in claude_worker.py
to achieve 100% coverage (Phase 3 of test coverage push).
"""

import pytest
from unittest.mock import MagicMock, patch, Mock

from asciidoc_artisan.claude import ClaudeWorker, ClaudeResult, ClaudeMessage


@pytest.mark.unit
class TestRunMethodExecution:
    """Test run() method execution paths."""

    def test_run_with_send_message_operation(self, qtbot):
        """Test run() executes send_message operation."""
        worker = ClaudeWorker()

        # Mock client response
        mock_result = ClaudeResult(
            success=True,
            content="Response",
            model="claude-3-5-sonnet-20241022",
            tokens_used=10,
            error=None,
            stop_reason="end_turn",
        )

        with patch.object(worker.client, "send_message", return_value=mock_result):
            # Set operation and start thread
            worker._operation = "send_message"
            worker._current_message = "Test"
            worker._current_system = None
            worker._current_history = None

            with qtbot.waitSignal(worker.response_ready, timeout=5000) as blocker:
                worker.start()
                worker.wait()

            result = blocker.args[0]
            assert result.success is True

    def test_run_with_test_connection_operation(self, qtbot):
        """Test run() executes test_connection operation."""
        worker = ClaudeWorker()

        # Mock client response
        mock_result = ClaudeResult(
            success=True,
            content="OK",
            model="claude-3-5-sonnet-20241022",
            tokens_used=5,
            error=None,
            stop_reason="end_turn",
        )

        with patch.object(worker.client, "test_connection", return_value=mock_result):
            # Set operation and start thread
            worker._operation = "test_connection"

            with qtbot.waitSignal(worker.connection_tested, timeout=5000) as blocker:
                worker.start()
                worker.wait()

            result = blocker.args[0]
            assert result.success is True

    def test_run_with_empty_operation(self, qtbot):
        """Test run() with empty operation string."""
        worker = ClaudeWorker()

        # Set empty operation
        worker._operation = ""

        with qtbot.waitSignal(worker.error_occurred, timeout=5000) as blocker:
            worker.start()
            worker.wait()

        error_msg = blocker.args[0]
        assert "unknown operation" in error_msg.lower()


@pytest.mark.unit
class TestExecuteSendMessage:
    """Test _execute_send_message method."""

    def test_execute_send_message_with_system_prompt(self, qtbot):
        """Test _execute_send_message with system prompt."""
        worker = ClaudeWorker()

        mock_result = ClaudeResult(
            success=True,
            content="Response with system",
            model="claude-3-5-sonnet-20241022",
            tokens_used=15,
            error=None,
            stop_reason="end_turn",
        )

        with patch.object(worker.client, "send_message", return_value=mock_result) as mock_send:
            worker._operation = "send_message"
            worker._current_message = "User message"
            worker._current_system = "System prompt"
            worker._current_history = None

            with qtbot.waitSignal(worker.response_ready, timeout=5000):
                worker.start()
                worker.wait()

            # Verify system prompt was passed
            mock_send.assert_called_once_with(
                message="User message",
                system="System prompt",
                conversation_history=None,
            )

    def test_execute_send_message_with_history(self, qtbot):
        """Test _execute_send_message with conversation history."""
        worker = ClaudeWorker()

        mock_result = ClaudeResult(
            success=True,
            content="Response with history",
            model="claude-3-5-sonnet-20241022",
            tokens_used=20,
            error=None,
            stop_reason="end_turn",
        )

        history = [
            ClaudeMessage(role="user", content="First"),
            ClaudeMessage(role="assistant", content="Response"),
        ]

        with patch.object(worker.client, "send_message", return_value=mock_result) as mock_send:
            worker._operation = "send_message"
            worker._current_message = "Second message"
            worker._current_system = "System"
            worker._current_history = history

            with qtbot.waitSignal(worker.response_ready, timeout=5000):
                worker.start()
                worker.wait()

            # Verify history was passed
            mock_send.assert_called_once_with(
                message="Second message",
                system="System",
                conversation_history=history,
            )

    def test_execute_send_message_error_response(self, qtbot):
        """Test _execute_send_message with error response."""
        worker = ClaudeWorker()

        mock_result = ClaudeResult(
            success=False,
            content="",
            model="",
            tokens_used=0,
            error="API error",
            stop_reason=None,
        )

        with patch.object(worker.client, "send_message", return_value=mock_result):
            worker._operation = "send_message"
            worker._current_message = "Test"
            worker._current_system = None
            worker._current_history = None

            with qtbot.waitSignal(worker.response_ready, timeout=5000) as blocker:
                worker.start()
                worker.wait()

            result = blocker.args[0]
            assert result.success is False
            assert result.error == "API error"


@pytest.mark.unit
class TestExecuteTestConnection:
    """Test _execute_test_connection method."""

    def test_execute_test_connection_success(self, qtbot):
        """Test _execute_test_connection with successful connection."""
        worker = ClaudeWorker()

        mock_result = ClaudeResult(
            success=True,
            content="Connection successful",
            model="claude-3-5-sonnet-20241022",
            tokens_used=8,
            error=None,
            stop_reason="end_turn",
        )

        with patch.object(worker.client, "test_connection", return_value=mock_result) as mock_test:
            worker._operation = "test_connection"

            with qtbot.waitSignal(worker.connection_tested, timeout=5000) as blocker:
                worker.start()
                worker.wait()

            result = blocker.args[0]
            assert result.success is True
            assert "successful" in result.content.lower()

            # Verify test_connection was called
            mock_test.assert_called_once()

    def test_execute_test_connection_failure(self, qtbot):
        """Test _execute_test_connection with connection failure."""
        worker = ClaudeWorker()

        mock_result = ClaudeResult(
            success=False,
            content="",
            model="",
            tokens_used=0,
            error="Connection failed",
            stop_reason=None,
        )

        with patch.object(worker.client, "test_connection", return_value=mock_result):
            worker._operation = "test_connection"

            with qtbot.waitSignal(worker.connection_tested, timeout=5000) as blocker:
                worker.start()
                worker.wait()

            result = blocker.args[0]
            assert result.success is False
            assert "failed" in result.error.lower()


@pytest.mark.unit
class TestExceptionHandlingInRun:
    """Test exception handling in run() method."""

    def test_run_exception_in_execute_send_message(self, qtbot):
        """Test run() handles exception in _execute_send_message."""
        worker = ClaudeWorker()

        with patch.object(
            worker.client, "send_message", side_effect=RuntimeError("Client error")
        ):
            worker._operation = "send_message"
            worker._current_message = "Test"
            worker._current_system = None
            worker._current_history = None

            with qtbot.waitSignal(worker.error_occurred, timeout=5000) as blocker:
                worker.start()
                worker.wait()

            error_msg = blocker.args[0]
            assert "worker error" in error_msg.lower()

    def test_run_exception_in_execute_test_connection(self, qtbot):
        """Test run() handles exception in _execute_test_connection."""
        worker = ClaudeWorker()

        with patch.object(
            worker.client, "test_connection", side_effect=RuntimeError("Connection error")
        ):
            worker._operation = "test_connection"

            with qtbot.waitSignal(worker.error_occurred, timeout=5000) as blocker:
                worker.start()
                worker.wait()

            error_msg = blocker.args[0]
            assert "worker error" in error_msg.lower()
