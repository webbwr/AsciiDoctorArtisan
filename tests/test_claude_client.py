"""
Unit tests for ClaudeClient class.
"""

from unittest.mock import MagicMock, patch

import pytest

# Try to import, but handle if anthropic not installed
try:
    from claude_client import ClaudeClient, ConversionFormat, ConversionResult

    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    pytest.skip("ClaudeClient not available", allow_module_level=True)


@pytest.mark.unit
@pytest.mark.skipif(not CLAUDE_AVAILABLE, reason="Claude client not available")
class TestClaudeClient:
    """Test ClaudeClient for AI-enhanced document conversion."""

    @patch("claude_client.Anthropic")
    def test_client_initialization(self, mock_anthropic):
        """Test ClaudeClient can be instantiated."""
        client = ClaudeClient(api_key="test_key")
        assert client is not None
        assert client.model == ClaudeClient.DEFAULT_MODEL
        assert client.max_retries == ClaudeClient.MAX_RETRIES

    @patch("claude_client.Anthropic")
    def test_client_custom_parameters(self, mock_anthropic):
        """Test ClaudeClient with custom parameters."""
        client = ClaudeClient(
            api_key="test_key",
            model="claude-3-opus-20240229",
            max_retries=5,
            timeout=120,
        )
        assert client.model == "claude-3-opus-20240229"
        assert client.max_retries == 5
        assert client.timeout == 120

    @patch("claude_client.Anthropic")
    def test_successful_conversion(self, mock_anthropic):
        """Test successful document conversion."""
        from anthropic.types import TextBlock

        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_message = MagicMock()
        text_block = TextBlock(text="# Converted Markdown", type="text")
        mock_message.content = [text_block]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test_key")
        client._validated = True  # Skip validation

        result = client.convert_document(
            content="= AsciiDoc Content",
            source_format="asciidoc",
            target_format=ConversionFormat.MARKDOWN,
        )

        assert result.success is True
        assert result.content == "# Converted Markdown"
        assert result.used_ai is True

    @patch("claude_client.Anthropic")
    def test_conversion_with_progress_callback(self, mock_anthropic):
        """Test conversion with progress callback."""
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        from anthropic.types import TextBlock

        mock_message = MagicMock()
        text_block = TextBlock(text="Converted", type="text")
        mock_message.content = [text_block]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test_key")
        client._validated = True

        progress_messages = []

        def progress_callback(message: str):
            progress_messages.append(message)

        result = client.convert_document(
            content="Test content",
            source_format="markdown",
            target_format=ConversionFormat.HTML,
            progress_callback=progress_callback,
        )

        assert result.success is True
        assert len(progress_messages) > 0

    @patch("claude_client.Anthropic")
    def test_api_error_handling(self, mock_anthropic):
        """Test API error handling."""
        from anthropic import APIError

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        # Create APIError with required request parameter
        mock_request = MagicMock()
        mock_client.messages.create.side_effect = APIError(
            "API error", request=mock_request, body=None
        )

        client = ClaudeClient(api_key="test_key")
        client._validated = True

        result = client.convert_document(
            content="Test",
            source_format="markdown",
            target_format=ConversionFormat.HTML,
        )

        assert result.success is False
        assert result.error_message is not None

    @patch("claude_client.Anthropic")
    @patch("claude_client.time.sleep")  # Mock sleep to speed up test
    def test_rate_limit_retry(self, mock_sleep, mock_anthropic):
        """Test rate limit retry logic."""
        from anthropic import RateLimitError

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        # First call raises RateLimitError, second succeeds
        from anthropic.types import TextBlock

        mock_message = MagicMock()
        text_block = TextBlock(text="Success after retry", type="text")
        mock_message.content = [text_block]

        # Create RateLimitError with required parameters
        mock_response = MagicMock()
        mock_response.status_code = 429
        rate_limit_error = RateLimitError(
            "Rate limit", response=mock_response, body=None
        )

        mock_client.messages.create.side_effect = [
            rate_limit_error,
            mock_message,
        ]

        client = ClaudeClient(api_key="test_key", max_retries=2)
        client._validated = True

        result = client.convert_document(
            content="Test",
            source_format="markdown",
            target_format=ConversionFormat.HTML,
        )

        # Should succeed after retry
        assert result.success is True
        assert mock_client.messages.create.call_count == 2
        assert mock_sleep.called  # Verify backoff was attempted


@pytest.mark.unit
@pytest.mark.skipif(not CLAUDE_AVAILABLE, reason="Claude client not available")
class TestConversionFormat:
    """Test ConversionFormat enum."""

    def test_all_formats_available(self):
        """Test all conversion formats are defined."""
        assert ConversionFormat.MARKDOWN.value == "markdown"
        assert ConversionFormat.DOCX.value == "docx"
        assert ConversionFormat.HTML.value == "html"
        assert ConversionFormat.PDF.value == "pdf"
        assert ConversionFormat.LATEX.value == "latex"


@pytest.mark.unit
@pytest.mark.skipif(not CLAUDE_AVAILABLE, reason="Claude client not available")
class TestConversionResult:
    """Test ConversionResult dataclass."""

    def test_successful_result(self):
        """Test ConversionResult for successful conversion."""
        result = ConversionResult(
            success=True,
            content="Converted content",
            used_ai=True,
            processing_time=1.5,
        )

        assert result.success is True
        assert result.content == "Converted content"
        assert result.used_ai is True
        assert result.processing_time == 1.5
        assert result.error_message is None

    def test_failed_result(self):
        """Test ConversionResult for failed conversion."""
        result = ConversionResult(
            success=False,
            error_message="Conversion failed",
            used_ai=True,
            processing_time=0.5,
        )

        assert result.success is False
        assert result.error_message == "Conversion failed"
        assert result.content is None


@pytest.mark.unit
@pytest.mark.skipif(not CLAUDE_AVAILABLE, reason="Claude client not available")
class TestClaudeClientUtilities:
    """Test utility functions in ClaudeClient."""

    def test_is_available(self):
        """Test is_available static method."""
        assert ClaudeClient.is_available() is True

    def test_estimate_tokens(self):
        """Test token estimation."""
        text = "A" * 400  # 400 characters
        estimated = ClaudeClient.estimate_tokens(text)

        # Should estimate ~100 tokens (4 chars per token)
        assert 90 <= estimated <= 110

    @patch("claude_client.Anthropic")
    def test_can_handle_document(self, mock_anthropic):
        """Test document size validation."""
        client = ClaudeClient(api_key="test_key")

        # Small document should be acceptable
        small_doc = "A" * 1000
        assert client.can_handle_document(small_doc) is True

        # Very large document should be rejected
        large_doc = "A" * (ClaudeClient.MAX_TOKENS * 10)
        assert client.can_handle_document(large_doc) is False

    def test_get_installation_instructions(self):
        """Test installation instructions generation."""
        instructions = ClaudeClient.get_installation_instructions()
        assert "pandoc" in instructions.lower()

    @patch("claude_client.Anthropic")
    def test_prompt_building(self, mock_anthropic):
        """Test conversion prompt building."""
        prompt = ClaudeClient._build_prompt(
            "Test content",
            "markdown",
            ConversionFormat.HTML,
        )

        assert "Test content" in prompt
        assert "MARKDOWN" in prompt
        assert "HTML" in prompt
        assert "REQUIREMENTS" in prompt


@pytest.mark.unit
@pytest.mark.skipif(not CLAUDE_AVAILABLE, reason="Claude client not available")
class TestCreateClient:
    """Test create_client factory function."""

    @patch("claude_client.ClaudeClient")
    def test_create_client_success(self, mock_client_class):
        """Test successful client creation."""
        from claude_client import create_client

        mock_client_class.return_value = MagicMock()

        client = create_client(api_key="test_key")
        assert client is not None

    @patch("claude_client.ClaudeClient")
    def test_create_client_failure(self, mock_client_class):
        """Test client creation handles errors."""
        from claude_client import create_client

        mock_client_class.side_effect = ValueError("Invalid key")

        client = create_client(api_key="bad_key")
        assert client is None
