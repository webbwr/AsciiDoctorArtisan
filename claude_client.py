"""
Claude AI Client for AsciiDoc Artisan

Provides integration with Anthropic's Claude API for AI-enhanced document conversion.
Handles API key validation, retries, rate limiting, and error recovery.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Callable, Optional

try:
    from anthropic import Anthropic, APIConnectionError, APIError, RateLimitError
    from anthropic.types import TextBlock

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    TextBlock = None  # type: ignore
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
    High-performance Claude API client for document conversion.

    Features:
    - Lazy API key validation
    - Exponential backoff retry logic
    - Token estimation and document size checks
    - Progress callbacks for UX
    - Comprehensive error handling
    """

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    MAX_RETRIES = 3
    DEFAULT_TIMEOUT = 60
    MAX_TOKENS = 50000
    CHARS_PER_TOKEN = 4

    __slots__ = ("client", "model", "max_retries", "timeout", "_validated")

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_retries: int = MAX_RETRIES,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic SDK not installed. Install with: pip install anthropic>=0.40.0"
            )

        self.client = Anthropic(api_key=api_key, timeout=timeout)
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        self._validated = False

    def _validate_api_key(self) -> None:
        """Validate API key with minimal API call. Cached after first success."""
        if self._validated:
            return

        try:
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}],
            )
            self._validated = True
            logger.info("API key validated")
        except APIError as e:
            logger.error(f"API key validation failed: {e}")
            raise ValueError(f"Invalid API key: {e}") from e

    def convert_document(
        self,
        content: str,
        source_format: str,
        target_format: ConversionFormat,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ConversionResult:
        """
        Convert document using Claude AI with intelligent formatting preservation.

        Args:
            content: Source document content
            source_format: Source format identifier
            target_format: Target format from ConversionFormat enum
            progress_callback: Optional progress update callback

        Returns:
            ConversionResult with conversion outcome and metadata
        """
        start_time = time.time()

        if not self._validated:
            try:
                self._validate_api_key()
            except ValueError as e:
                return ConversionResult(
                    success=False,
                    error_message=str(e),
                    used_ai=True,
                    processing_time=time.time() - start_time,
                )

        if progress_callback:
            progress_callback("Preparing AI conversion request...")

        prompt = self._build_prompt(content, source_format, target_format)

        for attempt in range(1, self.max_retries + 1):
            try:
                if progress_callback:
                    progress_callback(
                        f"Claude API request (attempt {attempt}/{self.max_retries})..."
                    )

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8192,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}],
                )

                # Extract text from response, filtering for TextBlock
                text_blocks = [block for block in response.content if isinstance(block, TextBlock)]
                if not text_blocks:
                    return self._error_result("No text content in API response", start_time)

                converted_content = text_blocks[0].text
                processing_time = time.time() - start_time

                logger.info(f"AI conversion successful in {processing_time:.2f}s")

                if progress_callback:
                    progress_callback("Conversion completed!")

                return ConversionResult(
                    success=True,
                    content=converted_content,
                    used_ai=True,
                    processing_time=processing_time,
                )

            except RateLimitError:
                if attempt < self.max_retries:
                    wait_time = 2**attempt
                    logger.warning(f"Rate limit hit, retrying in {wait_time}s")
                    if progress_callback:
                        progress_callback(f"Rate limited. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    return self._error_result(
                        f"Rate limit exceeded after {self.max_retries} attempts",
                        start_time,
                    )

            except APIConnectionError as e:
                if attempt < self.max_retries:
                    wait_time = 2**attempt
                    logger.warning(f"Connection error, retrying in {wait_time}s")
                    if progress_callback:
                        progress_callback(
                            f"Connection error. Retrying in {wait_time}s..."
                        )
                    time.sleep(wait_time)
                else:
                    return self._error_result(
                        f"Connection failed after {self.max_retries} attempts: {e}",
                        start_time,
                    )

            except APIError as e:
                logger.error(f"API error: {e}")
                return self._error_result(f"API error: {e}", start_time)

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return self._error_result(f"Unexpected error: {e}", start_time)

        return self._error_result("Max retries exceeded", start_time)

    @staticmethod
    def _error_result(error_message: str, start_time: float) -> ConversionResult:
        """Create standardized error result."""
        return ConversionResult(
            success=False,
            error_message=error_message,
            used_ai=True,
            processing_time=time.time() - start_time,
        )

    @staticmethod
    @lru_cache(maxsize=32)
    def _build_prompt(
        content: str, source_format: str, target_format: ConversionFormat
    ) -> str:
        """Build optimized conversion prompt. Cached for repeated formats."""
        return f"""Expert document converter. Convert {source_format.upper()} to {target_format.value.upper()}.

REQUIREMENTS:
1. Preserve ALL structure (headings, lists, tables, code blocks)
2. Maintain heading hierarchy exactly
3. Convert cross-references and links appropriately
4. Preserve code blocks with language annotations
5. Handle nested lists correctly
6. Maintain table structure
7. Convert inline formatting accurately (bold, italic, monospace)
8. Output ONLY converted document - no explanations or markdown fences

SOURCE:
{content}

OUTPUT FORMAT: {target_format.value.upper()}

CONVERTED:"""

    @staticmethod
    def is_available() -> bool:
        """Check if Anthropic SDK is available."""
        return ANTHROPIC_AVAILABLE

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count (Claude: ~4 chars/token)."""
        return len(text) // ClaudeClient.CHARS_PER_TOKEN

    def can_handle_document(self, content: str, max_tokens: int = MAX_TOKENS) -> bool:
        """Check if document size is within API limits."""
        return self.estimate_tokens(content) <= max_tokens


def create_client(api_key: Optional[str] = None) -> Optional[ClaudeClient]:
    """
    Factory function to create ClaudeClient instance.

    Args:
        api_key: Optional API key (reads from environment if None)

    Returns:
        ClaudeClient instance or None if creation fails
    """
    try:
        return ClaudeClient(api_key=api_key)
    except (ImportError, ValueError) as e:
        logger.error(f"Failed to create ClaudeClient: {e}")
        return None
