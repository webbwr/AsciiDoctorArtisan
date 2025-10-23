"""
Claude AI Client for AsciiDoc Artisan

This module provides integration with Anthropic's Claude API for AI-enhanced
document format conversion.

Requirements Addressed:
- FR-054: Claude API integration for format conversion
- FR-056: Complex document handling with AI
- FR-057: Fallback to Pandoc on AI failure
- FR-058: API key validation
- FR-060: Error handling for API failures
- FR-062: Rate limiting and retry logic
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Callable

try:
    from anthropic import Anthropic, APIError, RateLimitError, APIConnectionError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("Anthropic SDK not installed. AI-enhanced conversion unavailable.")


logger = logging.getLogger(__name__)


class ConversionFormat(Enum):
    """Supported output formats for document conversion."""
    MARKDOWN = "markdown"
    DOCX = "docx"
    HTML = "html"
    PDF = "pdf"
    LATEX = "latex"


@dataclass
class ConversionResult:
    """Result of a document conversion operation."""
    success: bool
    content: Optional[str] = None
    error_message: Optional[str] = None
    used_ai: bool = False
    fallback_used: bool = False
    processing_time: float = 0.0


class ClaudeClient:
    """
    Client for interacting with Claude API for document conversion.

    This client handles:
    - API key validation
    - Document conversion with Claude AI
    - Rate limiting and retry logic
    - Error handling and fallback to Pandoc
    - Progress callbacks for long operations

    Attributes:
        api_key: Anthropic API key (from environment or direct)
        model: Claude model to use (default: claude-3-5-sonnet-20241022)
        max_retries: Maximum retry attempts for transient failures
        timeout: API request timeout in seconds
    """

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    MAX_RETRIES = 3
    DEFAULT_TIMEOUT = 60  # seconds

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_retries: int = MAX_RETRIES,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key. If None, will attempt to read from
                    ANTHROPIC_API_KEY environment variable.
            model: Claude model identifier
            max_retries: Maximum retry attempts for transient failures
            timeout: Request timeout in seconds

        Raises:
            ImportError: If anthropic SDK is not installed
            ValueError: If API key is not provided and not in environment
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic SDK not installed. Install with: pip install anthropic>=0.40.0"
            )

        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout

        # Initialize client (will auto-read ANTHROPIC_API_KEY from env if api_key is None)
        try:
            self.client = Anthropic(api_key=api_key, timeout=timeout)
            self._validate_api_key()
        except Exception as e:
            raise ValueError(f"Failed to initialize Anthropic client: {e}")

    def _validate_api_key(self) -> bool:
        """
        Validate that the API key is valid by making a minimal API call.

        Returns:
            True if API key is valid

        Raises:
            ValueError: If API key is invalid
        """
        try:
            # Make a minimal request to validate the API key
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            logger.info("API key validated successfully")
            return True
        except APIError as e:
            logger.error(f"API key validation failed: {e}")
            raise ValueError(f"Invalid API key: {e}")

    def convert_document(
        self,
        content: str,
        source_format: str,
        target_format: ConversionFormat,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> ConversionResult:
        """
        Convert document using Claude AI with intelligent formatting.

        This method uses Claude to intelligently convert documents, preserving
        complex formatting like nested lists, tables, code blocks, and semantic
        structure that simple converters might lose.

        Args:
            content: Source document content
            source_format: Source format (e.g., "asciidoc", "markdown")
            target_format: Target format from ConversionFormat enum
            progress_callback: Optional callback for progress updates

        Returns:
            ConversionResult with conversion outcome
        """
        start_time = time.time()

        if progress_callback:
            progress_callback("Preparing AI conversion request...")

        # Build conversion prompt
        prompt = self._build_conversion_prompt(content, source_format, target_format)

        # Attempt conversion with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                if progress_callback:
                    progress_callback(f"Sending request to Claude API (attempt {attempt}/{self.max_retries})...")

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8192,  # Sufficient for most documents
                    temperature=0.3,  # Lower temperature for more consistent conversions
                    messages=[{"role": "user", "content": prompt}]
                )

                # Extract converted content
                converted_content = response.content[0].text

                processing_time = time.time() - start_time
                logger.info(f"AI conversion successful in {processing_time:.2f}s")

                if progress_callback:
                    progress_callback("AI conversion completed successfully!")

                return ConversionResult(
                    success=True,
                    content=converted_content,
                    used_ai=True,
                    fallback_used=False,
                    processing_time=processing_time
                )

            except RateLimitError as e:
                logger.warning(f"Rate limit hit on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    if progress_callback:
                        progress_callback(f"Rate limited. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    processing_time = time.time() - start_time
                    return ConversionResult(
                        success=False,
                        error_message=f"Rate limit exceeded after {self.max_retries} attempts",
                        used_ai=True,
                        fallback_used=False,
                        processing_time=processing_time
                    )

            except APIConnectionError as e:
                logger.warning(f"API connection error on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    if progress_callback:
                        progress_callback(f"Connection error. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    processing_time = time.time() - start_time
                    return ConversionResult(
                        success=False,
                        error_message=f"Connection failed after {self.max_retries} attempts: {e}",
                        used_ai=True,
                        fallback_used=False,
                        processing_time=processing_time
                    )

            except APIError as e:
                # Non-retryable API errors
                logger.error(f"API error during conversion: {e}")
                processing_time = time.time() - start_time
                return ConversionResult(
                    success=False,
                    error_message=f"API error: {e}",
                    used_ai=True,
                    fallback_used=False,
                    processing_time=processing_time
                )

            except Exception as e:
                # Unexpected errors
                logger.error(f"Unexpected error during AI conversion: {e}")
                processing_time = time.time() - start_time
                return ConversionResult(
                    success=False,
                    error_message=f"Unexpected error: {e}",
                    used_ai=True,
                    fallback_used=False,
                    processing_time=processing_time
                )

        # Should not reach here, but handle gracefully
        processing_time = time.time() - start_time
        return ConversionResult(
            success=False,
            error_message="Max retries exceeded",
            used_ai=True,
            fallback_used=False,
            processing_time=processing_time
        )

    def _build_conversion_prompt(
        self,
        content: str,
        source_format: str,
        target_format: ConversionFormat
    ) -> str:
        """
        Build a detailed prompt for Claude to perform document conversion.

        Args:
            content: Source document content
            source_format: Source format name
            target_format: Target format

        Returns:
            Formatted prompt for Claude
        """
        prompt = f"""You are an expert technical writer and document conversion specialist.
Your task is to convert the following {source_format.upper()} document to {target_format.value.upper()} format.

CRITICAL REQUIREMENTS:
1. Preserve ALL semantic structure (headings, lists, tables, code blocks)
2. Maintain heading hierarchy exactly
3. Convert cross-references and links appropriately
4. Preserve code blocks with language annotations
5. Handle nested lists correctly (convert admonitions if needed)
6. Maintain table structure and formatting
7. Convert inline formatting (bold, italic, monospace) accurately
8. Preserve document metadata where applicable
9. Output ONLY the converted document - no explanations, no markdown fences around the output
10. If the source format contains special directives or includes, note them in comments

SOURCE DOCUMENT:
{content}

OUTPUT FORMAT: {target_format.value.upper()}

CONVERTED DOCUMENT:"""

        return prompt

    @staticmethod
    def is_available() -> bool:
        """
        Check if Anthropic SDK is available.

        Returns:
            True if anthropic package is installed
        """
        return ANTHROPIC_AVAILABLE

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for given text.

        Claude uses ~4 characters per token on average.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def can_handle_document(self, content: str, max_tokens: int = 50000) -> bool:
        """
        Check if document size is within API limits.

        Args:
            content: Document content
            max_tokens: Maximum allowed tokens (default: 50k for safety)

        Returns:
            True if document can be processed
        """
        estimated_tokens = self.estimate_tokens(content)
        return estimated_tokens <= max_tokens


def create_client(api_key: Optional[str] = None) -> Optional[ClaudeClient]:
    """
    Factory function to create a ClaudeClient instance.

    Args:
        api_key: Optional API key. If None, reads from environment.

    Returns:
        ClaudeClient instance, or None if creation fails
    """
    try:
        return ClaudeClient(api_key=api_key)
    except (ImportError, ValueError) as e:
        logger.error(f"Failed to create ClaudeClient: {e}")
        return None
