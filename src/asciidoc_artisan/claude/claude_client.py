"""
Claude AI Client - Main API client for Anthropic Claude integration.

This module provides a high-level interface to the Anthropic Claude API with:
- Secure API key management via OS keyring
- Configurable models and parameters
- Error handling and validation
- Token usage tracking
- Streaming support for real-time responses

Security:
- API keys never stored in plain text
- Credentials managed via secure_credentials module
- API key validation before requests

Example:
    >>> client = ClaudeClient()
    >>> if client.is_configured():
    ...     result = client.send_message("Hello Claude!")
    ...     if result.success:
    ...         print(result.content)
"""

import logging
from dataclasses import dataclass

from anthropic import Anthropic, APIConnectionError, APIError
from pydantic import BaseModel, Field

from asciidoc_artisan.core import SecureCredentials

logger = logging.getLogger(__name__)


@dataclass
class ClaudeResult:
    """
    Result of a Claude API operation.

    Attributes:
        success: True if operation succeeded
        content: Response text from Claude
        model: Model used for the response
        tokens_used: Total tokens consumed (prompt + completion)
        error: Error message if operation failed
        stop_reason: Reason Claude stopped generating (e.g., "end_turn", "max_tokens")
    """

    success: bool
    content: str = ""
    model: str = ""
    tokens_used: int = 0
    error: str = ""
    stop_reason: str = ""


class ClaudeMessage(BaseModel):
    """
    Single message in Claude conversation history.

    Attributes:
        role: Message sender ("user" or "assistant")
        content: Message text content
    """

    role: str = Field(..., description='Message role: "user" or "assistant"')
    content: str = Field(..., description="Message text content")


class ClaudeClient:
    """
    High-level client for Anthropic Claude API.

    Provides a simple interface for sending messages to Claude and managing
    conversation context. Handles API key management, error handling, and
    response parsing.

    Attributes:
        model: Claude model to use (default: claude-sonnet-4-20250514)
        max_tokens: Maximum tokens in response (default: 4096)
        temperature: Sampling temperature 0-1 (default: 1.0)

    Example:
        >>> client = ClaudeClient(model="claude-sonnet-4-20250514")
        >>> result = client.send_message("Explain AsciiDoc")
        >>> if result.success:
        ...     print(result.content)
    """

    # Default Claude model
    # Using Claude Sonnet 4 (current generation, 2025)
    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    # Available models (Claude 4 family - current generation)
    AVAILABLE_MODELS = [
        "claude-sonnet-4-20250514",  # Sonnet 4 (balanced, recommended)
        "claude-haiku-4-5",  # Haiku 4.5 (fast/cheap)
    ]

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 4096,
        temperature: float = 1.0,
    ) -> None:
        """
        Initialize Claude client.

        Args:
            model: Claude model identifier
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.credentials = SecureCredentials()
        self._client: Anthropic | None = None

        logger.debug(f"Claude client initialized with model={model}")

    def is_configured(self) -> bool:
        """
        Check if Claude API key is configured.

        Returns:
            True if API key is available in keyring
        """
        result: bool = self.credentials.has_anthropic_key()
        return result

    def _get_client(self) -> Anthropic | None:
        """
        Get or create Anthropic client instance.

        Returns:
            Anthropic client or None if no API key configured

        Raises:
            ValueError: If API key is invalid
        """
        if self._client is not None:
            return self._client

        api_key = self.credentials.get_anthropic_key()
        if not api_key:
            logger.warning("No Anthropic API key configured")
            return None

        try:
            self._client = Anthropic(api_key=api_key)
            logger.debug("Anthropic client created successfully")
            return self._client
        except Exception as e:
            logger.error(f"Failed to create Anthropic client: {e}")
            return None

    def send_message(  # noqa: C901
        self,
        message: str,
        system: str | None = None,
        conversation_history: list[ClaudeMessage] | None = None,
    ) -> ClaudeResult:
        """
        Send a message to Claude and get a response.

        Args:
            message: User message to send
            system: System prompt for context (optional)
            conversation_history: Previous messages for context (optional)

        Returns:
            ClaudeResult with response or error

        Example:
            >>> client = ClaudeClient()
            >>> result = client.send_message(
            ...     "Explain AsciiDoc syntax",
            ...     system="You are an AsciiDoc expert"
            ... )
            >>> print(result.content)
        """
        if not message or not message.strip():
            logger.warning("Empty message provided")
            return ClaudeResult(success=False, error="Message cannot be empty")

        client = self._get_client()
        if client is None:
            return ClaudeResult(
                success=False,
                error="API key not configured. Set it in Tools → API Key Setup.",
            )

        try:
            # Build messages list
            messages = []

            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    messages.append({"role": msg.role, "content": msg.content})

            # Add current user message
            messages.append({"role": "user", "content": message.strip()})

            # Make API request
            logger.debug(f"Sending message to Claude (model={self.model}, messages={len(messages)})")

            # Build kwargs, only add system if provided
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": messages,
            }
            if system:
                kwargs["system"] = system

            response = client.messages.create(**kwargs)

            # Extract response
            content = ""
            if response.content and len(response.content) > 0:
                # Claude returns a list of content blocks
                first_block = response.content[0]
                if hasattr(first_block, "text"):
                    content = first_block.text

            tokens_used = (
                response.usage.input_tokens + response.usage.output_tokens if hasattr(response, "usage") else 0
            )

            logger.info(f"Claude response received: {len(content)} chars, {tokens_used} tokens")

            return ClaudeResult(
                success=True,
                content=content,
                model=response.model,
                tokens_used=tokens_used,
                stop_reason=response.stop_reason or "",
            )

        except APIConnectionError as e:
            logger.error(f"Claude API connection error: {e}")
            return ClaudeResult(
                success=False,
                error=f"Connection error: {str(e)}. Check your internet connection.",
            )

        except APIError as e:
            logger.error(f"Claude API error: {e}")
            error_msg = str(e)

            # Provide user-friendly error messages
            if "invalid_api_key" in error_msg.lower():
                error_msg = "Invalid API key. Please update your key in Tools → API Key Setup."
            elif "rate_limit" in error_msg.lower():
                error_msg = "Rate limit exceeded. Please wait a moment and try again."
            elif "insufficient_quota" in error_msg.lower() or "credit balance is too low" in error_msg.lower():
                error_msg = "Insufficient API credits. Please add credits at console.anthropic.com/settings/billing"
            elif "overloaded" in error_msg.lower():
                error_msg = "Claude API is temporarily overloaded. Please try again in a moment."

            return ClaudeResult(success=False, error=error_msg)

        except Exception as e:
            logger.exception(f"Unexpected error calling Claude API: {e}")
            return ClaudeResult(success=False, error=f"Unexpected error: {str(e)}")

    def test_connection(self) -> ClaudeResult:
        """
        Test Claude API connection with a simple message.

        Returns:
            ClaudeResult indicating if connection is working

        Example:
            >>> client = ClaudeClient()
            >>> result = client.test_connection()
            >>> if result.success:
            ...     print("Connection OK!")
        """
        logger.debug("Testing Claude API connection")
        return self.send_message(
            "Reply with exactly: 'Connection OK'",
            system="You are a connection test assistant. Reply exactly as requested.",
        )

    def get_available_models(self) -> list[str]:
        """
        Get list of available Claude models (hardcoded list).

        Returns:
            List of model identifiers

        Example:
            >>> client = ClaudeClient()
            >>> models = client.get_available_models()
            >>> print(models)
            ['claude-sonnet-4-20250514', ...]
        """
        return self.AVAILABLE_MODELS.copy()

    def fetch_available_models_from_api(self) -> ClaudeResult:
        """
        Fetch list of available models from Anthropic API.

        Makes a request to the /v1/models endpoint to get the actual list
        of models available to this API key.

        Returns:
            ClaudeResult with models list in content field (JSON formatted)
            or error if request fails

        Example:
            >>> client = ClaudeClient()
            >>> result = client.fetch_available_models_from_api()
            >>> if result.success:
            ...     print(result.content)
        """
        client = self._get_client()
        if client is None:
            return ClaudeResult(
                success=False,
                error="API key not configured. Set it in Tools → API Key Setup.",
            )

        try:
            import json

            # Make request to models endpoint
            logger.debug("Fetching available models from Anthropic API")

            # Use the underlying HTTP client to make the request
            response = client._client.get("/v1/models")

            # Format the response nicely
            models_data = response.json()

            # Extract model IDs
            if "data" in models_data:
                model_ids = [model.get("id", "unknown") for model in models_data["data"]]
                formatted_output = f"Available Models ({len(model_ids)}):\n\n"
                for model_id in model_ids:
                    formatted_output += f"• {model_id}\n"

                logger.info(f"Fetched {len(model_ids)} models from API")
                return ClaudeResult(
                    success=True,
                    content=formatted_output,
                    model="models-api",
                )
            else:
                # Fallback format
                formatted_json = json.dumps(models_data, indent=2)
                return ClaudeResult(
                    success=True,
                    content=f"Models API Response:\n\n{formatted_json}",
                    model="models-api",
                )

        except APIConnectionError as e:
            logger.error(f"API connection error fetching models: {e}")
            return ClaudeResult(
                success=False,
                error=f"Connection error: {str(e)}. Check your internet connection.",
            )

        except APIError as e:
            logger.error(f"API error fetching models: {e}")
            return ClaudeResult(
                success=False,
                error=f"API error: {str(e)}",
            )

        except Exception as e:
            logger.exception(f"Unexpected error fetching models: {e}")
            return ClaudeResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
            )
