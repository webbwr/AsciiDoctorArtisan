"""
Unit tests for Claude AI Client.

Tests the ClaudeClient class for Anthropic Claude API integration.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock

from asciidoc_artisan.claude import ClaudeClient, ClaudeResult, ClaudeMessage


@pytest.mark.unit
class TestClaudeClient:
    """Test ClaudeClient for Claude API operations."""

    def test_claude_client_initialization(self):
        """Test ClaudeClient can be instantiated."""
        client = ClaudeClient()
        assert client is not None
        assert client.model == ClaudeClient.DEFAULT_MODEL
        assert client.max_tokens == 4096
        assert client.temperature == 1.0

    def test_claude_client_custom_params(self):
        """Test ClaudeClient with custom parameters."""
        client = ClaudeClient(
            model="claude-3-5-haiku-20241022", max_tokens=2048, temperature=0.7
        )
        assert client.model == "claude-3-5-haiku-20241022"
        assert client.max_tokens == 2048
        assert client.temperature == 0.7

    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_is_configured_returns_true_when_key_exists(self, mock_credentials):
        """Test is_configured returns True when API key exists."""
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = True
        mock_credentials.return_value = mock_creds

        client = ClaudeClient()
        assert client.is_configured() is True

    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_is_configured_returns_false_when_no_key(self, mock_credentials):
        """Test is_configured returns False when no API key."""
        mock_creds = Mock()
        mock_creds.has_anthropic_key.return_value = False
        mock_credentials.return_value = mock_creds

        client = ClaudeClient()
        assert client.is_configured() is False

    def test_send_message_with_empty_message(self):
        """Test send_message rejects empty messages."""
        client = ClaudeClient()

        result = client.send_message("")
        assert result.success is False
        assert "empty" in result.error.lower()

    def test_send_message_with_whitespace_only(self):
        """Test send_message rejects whitespace-only messages."""
        client = ClaudeClient()

        result = client.send_message("   \n\t   ")
        assert result.success is False
        assert "empty" in result.error.lower()

    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_without_api_key(self, mock_credentials):
        """Test send_message without API key configured."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = None
        mock_credentials.return_value = mock_creds

        client = ClaudeClient()
        result = client.send_message("Hello")

        assert result.success is False
        assert "not configured" in result.error.lower()

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_successful(self, mock_credentials, mock_anthropic):
        """Test successful message send."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        # Mock Anthropic client response
        mock_response = Mock()
        mock_response.content = [Mock(text="Hello! I'm Claude.")]
        mock_response.model = "claude-3-5-sonnet-20240620"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = Mock(input_tokens=10, output_tokens=15)

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Execute
        client = ClaudeClient()
        result = client.send_message("Hello Claude!")

        # Verify
        assert result.success is True
        assert result.content == "Hello! I'm Claude."
        assert result.model == "claude-3-5-sonnet-20240620"
        assert result.tokens_used == 25  # 10 + 15
        assert result.stop_reason == "end_turn"

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_with_system_prompt(self, mock_credentials, mock_anthropic):
        """Test message send with system prompt."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_response.model = "claude-3-5-sonnet-20240620"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = Mock(input_tokens=10, output_tokens=5)

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Execute
        client = ClaudeClient()
        result = client.send_message(
            "Hello", system="You are a helpful assistant"
        )

        # Verify system prompt was passed
        assert result.success is True
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["system"] == "You are a helpful assistant"

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_with_conversation_history(
        self, mock_credentials, mock_anthropic
    ):
        """Test message send with conversation history."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_response.model = "claude-3-5-sonnet-20240620"
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
        client = ClaudeClient()
        result = client.send_message("Second message", conversation_history=history)

        # Verify history was included
        assert result.success is True
        call_kwargs = mock_client.messages.create.call_args[1]
        messages = call_kwargs["messages"]
        assert len(messages) == 3  # 2 from history + 1 current
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "First message"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "First response"
        assert messages[2]["role"] == "user"
        assert messages[2]["content"] == "Second message"

    def test_get_available_models(self):
        """Test get_available_models returns list of models."""
        client = ClaudeClient()
        models = client.get_available_models()

        assert isinstance(models, list)
        assert len(models) > 0
        # Check for current model IDs (as of Nov 2025)
        assert "claude-sonnet-4-20250514" in models or "claude-3-5-sonnet-20240620" in models
        assert "claude-haiku-4-5" in models or "claude-3-5-haiku-20241022" in models

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_test_connection_successful(self, mock_credentials, mock_anthropic):
        """Test successful connection test."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_response = Mock()
        mock_response.content = [Mock(text="Connection OK")]
        mock_response.model = "claude-3-5-sonnet-20240620"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = Mock(input_tokens=5, output_tokens=3)

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Execute
        client = ClaudeClient()
        result = client.test_connection()

        # Verify
        assert result.success is True
        assert "Connection OK" in result.content


@pytest.mark.unit
class TestClaudeResult:
    """Test ClaudeResult dataclass."""

    def test_claude_result_success(self):
        """Test ClaudeResult for successful operation."""
        result = ClaudeResult(
            success=True,
            content="Test response",
            model="claude-3-5-sonnet-20240620",
            tokens_used=100,
            stop_reason="end_turn",
        )

        assert result.success is True
        assert result.content == "Test response"
        assert result.model == "claude-3-5-sonnet-20240620"
        assert result.tokens_used == 100
        assert result.stop_reason == "end_turn"
        assert result.error == ""

    def test_claude_result_failure(self):
        """Test ClaudeResult for failed operation."""
        result = ClaudeResult(success=False, error="API error")

        assert result.success is False
        assert result.error == "API error"
        assert result.content == ""
        assert result.tokens_used == 0
