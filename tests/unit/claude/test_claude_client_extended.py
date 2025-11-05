"""
Extended unit tests for Claude AI Client - Error handling and edge cases.

This test suite covers the remaining uncovered code paths in claude_client.py
to achieve 100% coverage (Phase 2.1 of test coverage push).
"""

import pytest
from unittest.mock import Mock, patch
import httpx

from asciidoc_artisan.claude import ClaudeClient, ClaudeResult, ClaudeMessage


def create_mock_api_error(message: str):
    """Helper to create properly initialized APIError."""
    from anthropic import APIError
    mock_request = Mock(spec=httpx.Request)
    return APIError(message, request=mock_request, body=None)


def create_mock_connection_error(message: str = "Network error"):
    """Helper to create properly initialized APIConnectionError."""
    from anthropic import APIConnectionError
    mock_request = Mock(spec=httpx.Request)
    return APIConnectionError(message=message, request=mock_request)


@pytest.mark.unit
class TestClaudeClientErrorHandling:
    """Test error handling in ClaudeClient."""

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_api_connection_error(self, mock_credentials, mock_anthropic):
        """Test send_message handles APIConnectionError."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_client = Mock()
        mock_client.messages.create.side_effect = create_mock_connection_error()
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.send_message("Hello")

        assert result.success is False
        assert "connection error" in result.error.lower()

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_invalid_api_key_error(self, mock_credentials, mock_anthropic):
        """Test send_message handles invalid API key error."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-invalid-key"
        mock_credentials.return_value = mock_creds

        mock_client = Mock()
        mock_client.messages.create.side_effect = create_mock_api_error("invalid_api_key: Invalid")
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.send_message("Hello")

        assert result.success is False
        assert "invalid api key" in result.error.lower()
        assert "tools" in result.error.lower()

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_rate_limit_error(self, mock_credentials, mock_anthropic):
        """Test send_message handles rate limit error."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_client = Mock()
        mock_client.messages.create.side_effect = create_mock_api_error("rate_limit exceeded")
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.send_message("Hello")

        assert result.success is False
        assert "rate limit" in result.error.lower()
        assert "wait" in result.error.lower()

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_insufficient_quota_error(self, mock_credentials, mock_anthropic):
        """Test send_message handles insufficient quota error."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_client = Mock()
        mock_client.messages.create.side_effect = create_mock_api_error("insufficient_quota: Out of credits")
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.send_message("Hello")

        assert result.success is False
        assert ("insufficient" in result.error.lower() or "credits" in result.error.lower())
        assert "console.anthropic.com" in result.error

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_credit_balance_low_error(self, mock_credentials, mock_anthropic):
        """Test send_message handles credit balance too low error."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_client = Mock()
        mock_client.messages.create.side_effect = create_mock_api_error("credit balance is too low")
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.send_message("Hello")

        assert result.success is False
        assert "credits" in result.error.lower()
        assert "console.anthropic.com" in result.error

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_overloaded_error(self, mock_credentials, mock_anthropic):
        """Test send_message handles overloaded API error."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_client = Mock()
        mock_client.messages.create.side_effect = create_mock_api_error("API is overloaded")
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.send_message("Hello")

        assert result.success is False
        assert "overloaded" in result.error.lower()
        assert "try again" in result.error.lower()

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_generic_api_error(self, mock_credentials, mock_anthropic):
        """Test send_message handles generic APIError."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_client = Mock()
        mock_client.messages.create.side_effect = create_mock_api_error("Some other API error")
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.send_message("Hello")

        assert result.success is False
        assert "some other api error" in result.error.lower()

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_unexpected_exception(self, mock_credentials, mock_anthropic):
        """Test send_message handles unexpected exceptions."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_client = Mock()
        mock_client.messages.create.side_effect = RuntimeError("Unexpected error")
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.send_message("Hello")

        assert result.success is False
        assert "unexpected error" in result.error.lower()


@pytest.mark.unit
class TestClaudeClientEdgeCases:
    """Test edge cases in ClaudeClient."""

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_get_client_caching(self, mock_credentials, mock_anthropic):
        """Test _get_client caches client instance."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        first_client = client._get_client()
        second_client = client._get_client()

        assert first_client is second_client
        mock_anthropic.assert_called_once()

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_get_client_exception_during_creation(self, mock_credentials, mock_anthropic):
        """Test _get_client handles exception during Anthropic client creation."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_anthropic.side_effect = Exception("Client creation failed")

        client = ClaudeClient()
        result_client = client._get_client()

        assert result_client is None

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_response_without_usage(self, mock_credentials, mock_anthropic):
        """Test send_message handles response without usage attribute."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        # Mock response without usage attribute
        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_response.model = "claude-sonnet-4-20250514"
        mock_response.stop_reason = "end_turn"
        del mock_response.usage  # Remove usage attribute

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.send_message("Hello")

        assert result.success is True
        assert result.tokens_used == 0

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_send_message_empty_content_list(self, mock_credentials, mock_anthropic):
        """Test send_message handles empty content list."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        # Mock response with empty content list
        mock_response = Mock()
        mock_response.content = []  # Empty
        mock_response.model = "claude-sonnet-4-20250514"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = Mock(input_tokens=5, output_tokens=0)

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.send_message("Hello")

        assert result.success is True
        assert result.content == ""


@pytest.mark.unit
class TestFetchAvailableModels:
    """Test fetch_available_models_from_api method."""

    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_fetch_models_without_api_key(self, mock_credentials):
        """Test fetch models without API key configured."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = None
        mock_credentials.return_value = mock_creds

        client = ClaudeClient()
        result = client.fetch_available_models_from_api()

        assert result.success is False
        assert "not configured" in result.error.lower()

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_fetch_models_success_with_data(self, mock_credentials, mock_anthropic):
        """Test fetch models success with 'data' in response."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        # Mock API response with 'data' field
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"id": "claude-sonnet-4-20250514"},
                {"id": "claude-haiku-4-5"},
            ]
        }

        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response

        mock_client = Mock()
        mock_client._client = mock_http_client
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.fetch_available_models_from_api()

        assert result.success is True
        assert "claude-sonnet-4-20250514" in result.content
        assert "claude-haiku-4-5" in result.content
        assert result.model == "models-api"

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_fetch_models_success_without_data(self, mock_credentials, mock_anthropic):
        """Test fetch models success without 'data' field (fallback format)."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        # Mock API response without 'data' field
        mock_response = Mock()
        mock_response.json.return_value = {"models": ["model1", "model2"]}

        mock_http_client = Mock()
        mock_http_client.get.return_value = mock_response

        mock_client = Mock()
        mock_client._client = mock_http_client
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.fetch_available_models_from_api()

        assert result.success is True
        assert "Models API Response" in result.content
        assert result.model == "models-api"

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_fetch_models_connection_error(self, mock_credentials, mock_anthropic):
        """Test fetch models handles connection error."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_http_client = Mock()
        mock_http_client.get.side_effect = create_mock_connection_error()

        mock_client = Mock()
        mock_client._client = mock_http_client
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.fetch_available_models_from_api()

        assert result.success is False
        assert "connection error" in result.error.lower()

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_fetch_models_api_error(self, mock_credentials, mock_anthropic):
        """Test fetch models handles API error."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_http_client = Mock()
        mock_http_client.get.side_effect = create_mock_api_error("API error")

        mock_client = Mock()
        mock_client._client = mock_http_client
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.fetch_available_models_from_api()

        assert result.success is False
        assert "api error" in result.error.lower()

    @patch("asciidoc_artisan.claude.claude_client.Anthropic")
    @patch("asciidoc_artisan.claude.claude_client.SecureCredentials")
    def test_fetch_models_unexpected_exception(self, mock_credentials, mock_anthropic):
        """Test fetch models handles unexpected exception."""
        mock_creds = Mock()
        mock_creds.get_anthropic_key.return_value = "sk-ant-test-key"
        mock_credentials.return_value = mock_creds

        mock_http_client = Mock()
        mock_http_client.get.side_effect = RuntimeError("Unexpected error")

        mock_client = Mock()
        mock_client._client = mock_http_client
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        result = client.fetch_available_models_from_api()

        assert result.success is False
        assert "unexpected error" in result.error.lower()


@pytest.mark.unit
class TestClaudeMessage:
    """Test ClaudeMessage Pydantic model."""

    def test_claude_message_creation(self):
        """Test ClaudeMessage can be created with valid data."""
        msg = ClaudeMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_claude_message_assistant_role(self):
        """Test ClaudeMessage with assistant role."""
        msg = ClaudeMessage(role="assistant", content="Hi there!")
        assert msg.role == "assistant"
        assert msg.content == "Hi there!"

    def test_claude_message_validation(self):
        """Test ClaudeMessage requires role and content."""
        with pytest.raises(Exception):  # Pydantic validation error
            ClaudeMessage()  # Missing required fields
