"""
Ollama Grammar Worker - AI-powered context-aware grammar checking.

This module provides the OllamaGrammarWorker class which performs
intelligent, context-aware grammar and style checking using local
Ollama LLM models.

Implements:
- FR-073: Ollama AI integration
- FR-074: Context-aware style analysis
- FR-075: AI suggestion parsing
- FR-076: Structured output handling
- NFR-005: Non-blocking background operations

Architecture:
- QObject-based worker for Qt threading
- Structured output with JSON parsing
- Retry logic with exponential backoff
- Timeout handling
- Result validation and sanitization

Thread Safety:
- Designed to run in separate QThread
- All methods are thread-safe
- Uses Qt signals for communication

Author: AsciiDoc Artisan Development Team
Version: 1.3.0
"""

import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, Signal, Slot

# Import Ollama with graceful fallback
try:
    import ollama
    from ollama import ResponseError

    OLLAMA_AVAILABLE = True
except ImportError:
    ollama = None
    ResponseError = Exception
    OLLAMA_AVAILABLE = False

# Import grammar models and config
from asciidoc_artisan.core.grammar_config import (
    ERROR_MESSAGES,
    OLLAMA_API_BASE_URL,
    OLLAMA_DEFAULT_MODEL,
    OLLAMA_MAX_RETRIES,
    OLLAMA_RETRY_DELAY_MS,
    OLLAMA_TIMEOUT_MS,
)
from asciidoc_artisan.core.grammar_models import (
    GrammarCategory,
    GrammarResult,
    GrammarSeverity,
    GrammarSource,
    GrammarSuggestion,
)

logger = logging.getLogger(__name__)


# ============================================================================
# RETRY LOGIC WITH EXPONENTIAL BACKOFF
# ============================================================================

@dataclass
class RetryState:
    """State tracker for retry logic with exponential backoff."""

    attempt: int = 0
    max_attempts: int = OLLAMA_MAX_RETRIES
    base_delay_ms: int = OLLAMA_RETRY_DELAY_MS
    last_error: Optional[str] = None

    def should_retry(self) -> bool:
        """Check if another retry attempt should be made."""
        return self.attempt < self.max_attempts

    def get_delay_ms(self) -> int:
        """Calculate delay for next retry using exponential backoff.

        Returns:
            Delay in milliseconds
        """
        # Exponential backoff: base * 2^attempt
        delay = self.base_delay_ms * (2 ** self.attempt)
        # Cap at 10 seconds
        return min(delay, 10000)

    def record_attempt(self, error: Optional[str] = None):
        """Record a retry attempt."""
        self.attempt += 1
        if error:
            self.last_error = error
        logger.debug(f"Retry attempt {self.attempt}/{self.max_attempts}")

    def reset(self):
        """Reset retry state after success."""
        self.attempt = 0
        self.last_error = None


# ============================================================================
# GRAMMAR PROMPT TEMPLATES
# ============================================================================

class GrammarPromptTemplate:
    """Templates for Ollama grammar checking prompts.

    Different prompt strategies for different use cases.
    """

    # Structured JSON output prompt (most reliable)
    STRUCTURED_JSON = """You are an expert grammar and style checker. Analyze the text below and identify issues.

For each issue found, provide:
1. The exact problematic text (quote it precisely)
2. Clear explanation of why it's an issue
3. A better alternative
4. Severity level: "error" (grammar), "warning" (style), or "info" (suggestion)

Format your response as a JSON array:
[
  {
    "text": "exact problematic text",
    "issue": "explanation of the problem",
    "suggestion": "improved version",
    "severity": "error|warning|info"
  }
]

If no issues are found, return an empty array: []

Text to check:
```
{text}
```

Respond ONLY with the JSON array, no other text:"""

    # Simple correction prompt (faster, less detailed)
    SIMPLE_CORRECTION = """Fix grammar and style issues in the text below.
Keep the original voice and tone.
Only respond with corrected text, nothing else.

Text:
```
{text}
```

Corrected text:"""

    # Detailed analysis prompt (slower, more comprehensive)
    DETAILED_ANALYSIS = """Analyze the following text for:
1. Grammar errors (subject-verb agreement, tenses, articles)
2. Style issues (passive voice, wordiness, cliches)
3. Clarity problems (ambiguous pronouns, unclear antecedents)

Text:
```
{text}
```

Provide specific suggestions in JSON format:
[
  {
    "text": "problem phrase",
    "issue": "what's wrong",
    "suggestion": "better alternative",
    "severity": "error|warning|info",
    "category": "grammar|style|clarity"
  }
]

JSON:"""

    @classmethod
    def get_prompt(cls, text: str, style: str = "structured") -> str:
        """Get formatted prompt for text.

        Args:
            text: Text to check
            style: Prompt style ("structured", "simple", "detailed")

        Returns:
            Formatted prompt string
        """
        templates = {
            "structured": cls.STRUCTURED_JSON,
            "simple": cls.SIMPLE_CORRECTION,
            "detailed": cls.DETAILED_ANALYSIS,
        }

        template = templates.get(style, cls.STRUCTURED_JSON)
        return template.format(text=text)


# ============================================================================
# SUGGESTION PARSER
# ============================================================================

class OllamaSuggestionParser:
    """Parses Ollama AI responses into GrammarSuggestion objects.

    Handles multiple response formats and sanitizes/validates results.
    """

    @staticmethod
    def parse_structured_json(
        response: str,
        original_text: str
    ) -> List[GrammarSuggestion]:
        """Parse structured JSON response from Ollama.

        Args:
            response: AI response text
            original_text: Original document text

        Returns:
            List of GrammarSuggestion objects
        """
        suggestions = []

        try:
            # Extract JSON from response (handle extra text)
            json_match = re.search(r'\[[\s\S]*\]', response)
            if not json_match:
                logger.warning("No JSON array found in Ollama response")
                return suggestions

            json_str = json_match.group(0)
            issues = json.loads(json_str)

            if not isinstance(issues, list):
                logger.warning(f"Expected JSON array, got {type(issues)}")
                return suggestions

            logger.debug(f"Parsed {len(issues)} issues from Ollama response")

            for issue in issues:
                try:
                    suggestion = OllamaSuggestionParser._parse_single_issue(
                        issue, original_text
                    )
                    if suggestion:
                        suggestions.append(suggestion)
                except Exception as e:
                    logger.warning(f"Failed to parse issue: {e}")
                    continue

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.debug(f"Response was: {response[:200]}")
        except Exception as e:
            logger.error(f"Unexpected parsing error: {e}", exc_info=True)

        return suggestions

    @staticmethod
    def _parse_single_issue(
        issue: Dict[str, Any],
        original_text: str
    ) -> Optional[GrammarSuggestion]:
        """Parse single issue dict into GrammarSuggestion.

        Args:
            issue: Issue dictionary from AI response
            original_text: Original document text

        Returns:
            GrammarSuggestion if valid, None otherwise
        """
        # Extract fields with defaults
        problem_text = issue.get('text', '').strip()
        issue_explanation = issue.get('issue', '').strip()
        suggestion_text = issue.get('suggestion', '').strip()
        severity_str = issue.get('severity', 'info').lower()
        category_str = issue.get('category', 'ai').lower()

        # Validate required fields
        if not problem_text or not issue_explanation:
            logger.debug("Skipping issue: missing text or explanation")
            return None

        # Find problem text in original document
        start = original_text.find(problem_text)
        if start == -1:
            # Try case-insensitive search
            start = original_text.lower().find(problem_text.lower())

        if start == -1:
            logger.debug(f"Could not locate text in document: {problem_text[:50]}")
            return None

        end = start + len(problem_text)

        # Map severity
        severity_map = {
            'error': GrammarSeverity.ERROR,
            'warning': GrammarSeverity.WARNING,
            'info': GrammarSeverity.INFO,
            'hint': GrammarSeverity.HINT,
        }
        severity = severity_map.get(severity_str, GrammarSeverity.INFO)

        # Map category
        category_map = {
            'grammar': GrammarCategory.GRAMMAR,
            'style': GrammarCategory.STYLE,
            'spelling': GrammarCategory.SPELLING,
            'clarity': GrammarCategory.READABILITY,
            'ai': GrammarCategory.AI_SUGGESTION,
        }
        category = category_map.get(category_str, GrammarCategory.AI_SUGGESTION)

        # Build suggestion
        return GrammarSuggestion(
            start=start,
            end=end,
            category=category,
            source=GrammarSource.OLLAMA,
            message=issue_explanation,
            replacements=[suggestion_text] if suggestion_text else [],
            rule_id='ollama_ai',
            context=problem_text,
            severity=severity,
            metadata={
                'ai_category': category_str,
                'original_severity': severity_str,
            }
        )

    @staticmethod
    def parse_simple_correction(
        response: str,
        original_text: str
    ) -> List[GrammarSuggestion]:
        """Parse simple correction response (diff-based).

        Args:
            response: Corrected text from AI
            original_text: Original document text

        Returns:
            List of GrammarSuggestion objects (one overall suggestion)
        """
        # For simple corrections, we create a single suggestion
        # representing the entire corrected text
        if response.strip() == original_text.strip():
            return []  # No changes

        suggestion = GrammarSuggestion(
            start=0,
            end=len(original_text),
            category=GrammarCategory.AI_SUGGESTION,
            source=GrammarSource.OLLAMA,
            message="AI suggests improvements to this text",
            replacements=[response.strip()],
            rule_id='ollama_overall',
            context=original_text[:100],
            severity=GrammarSeverity.INFO,
        )

        return [suggestion]


# ============================================================================
# OLLAMA GRAMMAR WORKER
# ============================================================================

class OllamaGrammarWorker(QObject):
    """Background worker for Ollama AI grammar checking.

    This worker runs in a separate QThread and performs AI-powered
    grammar and style analysis. Features:
    - Structured JSON output parsing
    - Retry logic with exponential backoff
    - Timeout handling
    - Result validation
    - Multiple prompt strategies

    Signals:
        grammar_result_ready(GrammarResult): Emitted when check completes
        progress_update(str): Emitted with status messages
    """

    # Qt Signals
    grammar_result_ready = Signal(GrammarResult)
    progress_update = Signal(str)

    def __init__(self):
        """Initialize OllamaGrammarWorker."""
        super().__init__()

        # Configuration
        self._enabled: bool = False
        self._model: str = OLLAMA_DEFAULT_MODEL
        self._prompt_style: str = "structured"  # structured, simple, detailed

        # State
        self._retry_state = RetryState()

        # Statistics
        self._total_checks = 0
        self._total_suggestions = 0
        self._total_processing_time_ms = 0
        self._failed_checks = 0

        logger.info("OllamaGrammarWorker created")

    # ========================================================================
    # CONFIGURATION
    # ========================================================================

    @Slot(bool, str)
    def set_config(self, enabled: bool, model: str):
        """Configure Ollama settings.

        Args:
            enabled: Whether Ollama checking is enabled
            model: Name of Ollama model to use
        """
        self._enabled = enabled
        self._model = model
        logger.info(f"Ollama config: enabled={enabled}, model={model}")

    @Slot(str)
    def set_prompt_style(self, style: str):
        """Set prompt style.

        Args:
            style: Prompt style ("structured", "simple", "detailed")
        """
        if style in ["structured", "simple", "detailed"]:
            self._prompt_style = style
            logger.info(f"Prompt style set to: {style}")

    # ========================================================================
    # GRAMMAR CHECKING
    # ========================================================================

    @Slot(str)
    def check_text(self, text: str):
        """Check text with Ollama AI.

        Args:
            text: Document content to check
        """
        # Check if enabled
        if not self._enabled or not self._model:
            logger.debug("Ollama checking disabled or no model set")
            return

        # Check availability
        if not OLLAMA_AVAILABLE:
            result = GrammarResult.create_error(
                GrammarSource.OLLAMA,
                ERROR_MESSAGES["ollama_not_installed"]
            )
            self.grammar_result_ready.emit(result)
            return

        # Validate input
        if not text or not text.strip():
            result = GrammarResult(
                suggestions=[],
                success=True,
                source=GrammarSource.OLLAMA,
                word_count=0,
                character_count=0,
                model_name=self._model,
            )
            self.grammar_result_ready.emit(result)
            return

        # Perform check with retries
        self._retry_state.reset()
        self._check_with_retry(text)

    def _check_with_retry(self, text: str):
        """Perform grammar check with retry logic.

        Args:
            text: Text to check
        """
        start_time = time.time()

        try:
            # Create prompt
            prompt = GrammarPromptTemplate.get_prompt(text, self._prompt_style)

            # Show progress
            self.progress_update.emit(f"Analyzing with AI ({self._model})...")

            logger.debug(f"Calling Ollama: model={self._model}, text_length={len(text)}")

            # Call Ollama API
            response = ollama.generate(
                model=self._model,
                prompt=prompt,
                options={
                    'temperature': 0.3,  # Lower temperature for more consistent output
                    'top_p': 0.9,
                    'num_predict': 2000,  # Max tokens to generate
                }
            )

            if not response or 'response' not in response:
                raise ValueError("Empty response from Ollama")

            response_text = response['response']
            logger.debug(f"Ollama response length: {len(response_text)} chars")

            # Parse response
            if self._prompt_style == "simple":
                suggestions = OllamaSuggestionParser.parse_simple_correction(
                    response_text, text
                )
            else:
                suggestions = OllamaSuggestionParser.parse_structured_json(
                    response_text, text
                )

            # Calculate metrics
            elapsed_ms = int((time.time() - start_time) * 1000)
            word_count = len(text.split())

            # Create result
            result = GrammarResult(
                suggestions=suggestions,
                success=True,
                source=GrammarSource.OLLAMA,
                processing_time_ms=elapsed_ms,
                word_count=word_count,
                character_count=len(text),
                model_name=self._model,
            )

            # Update statistics
            self._total_checks += 1
            self._total_suggestions += len(suggestions)
            self._total_processing_time_ms += elapsed_ms

            logger.info(
                f"Ollama check complete: {len(suggestions)} suggestions, "
                f"{elapsed_ms}ms, model={self._model}"
            )

            self.grammar_result_ready.emit(result)

        except ResponseError as e:
            # Ollama-specific error
            self._handle_ollama_error(e, text, start_time)

        except Exception as e:
            # Generic error
            self._handle_generic_error(e, text, start_time)

    def _handle_ollama_error(self, error: ResponseError, text: str, start_time: float):
        """Handle Ollama-specific errors with retry logic.

        Args:
            error: Ollama ResponseError
            text: Original text
            start_time: Check start time
        """
        error_msg = str(error)
        logger.warning(f"Ollama error: {error_msg}")

        # Check if we should retry
        if self._retry_state.should_retry():
            self._retry_state.record_attempt(error_msg)
            delay_ms = self._retry_state.get_delay_ms()

            logger.info(f"Retrying in {delay_ms}ms...")
            self.progress_update.emit(
                f"Retrying ({self._retry_state.attempt}/{self._retry_state.max_attempts})..."
            )

            # Schedule retry (using QTimer would be better, but sleep works for now)
            time.sleep(delay_ms / 1000.0)
            self._check_with_retry(text)
            return

        # Max retries exhausted
        elapsed_ms = int((time.time() - start_time) * 1000)
        self._failed_checks += 1

        # Determine specific error message
        if "model" in error_msg.lower() and "not found" in error_msg.lower():
            final_error = ERROR_MESSAGES["ollama_model_not_found"].format(
                model=self._model
            )
        elif "connection" in error_msg.lower():
            final_error = ERROR_MESSAGES["ollama_service_down"]
        else:
            final_error = f"Ollama error: {error_msg}"

        result = GrammarResult.create_error(
            GrammarSource.OLLAMA,
            final_error
        )
        self.grammar_result_ready.emit(result)

    def _handle_generic_error(self, error: Exception, text: str, start_time: float):
        """Handle generic errors.

        Args:
            error: Exception that occurred
            text: Original text
            start_time: Check start time
        """
        elapsed_ms = int((time.time() - start_time) * 1000)
        self._failed_checks += 1

        logger.error(f"Ollama check failed: {error}", exc_info=True)

        result = GrammarResult.create_error(
            GrammarSource.OLLAMA,
            f"AI check failed: {str(error)}"
        )
        self.grammar_result_ready.emit(result)

    # ========================================================================
    # VALIDATION
    # ========================================================================

    @Slot()
    def test_connection(self) -> bool:
        """Test connection to Ollama service.

        Returns:
            True if connection successful
        """
        if not OLLAMA_AVAILABLE:
            logger.error("Ollama library not available")
            return False

        try:
            # Try to list models
            result = ollama.list()
            logger.info("Ollama connection test: SUCCESS")
            return True

        except Exception as e:
            logger.error(f"Ollama connection test: FAILED - {e}")
            return False

    @Slot()
    def check_model_available(self) -> bool:
        """Check if configured model is available.

        Returns:
            True if model is available
        """
        if not OLLAMA_AVAILABLE:
            return False

        try:
            result = ollama.list()
            models = result.get('models', [])
            available_models = [m.get('name', '') for m in models]

            is_available = self._model in available_models
            logger.info(
                f"Model {self._model} available: {is_available}"
            )
            return is_available

        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False

    # ========================================================================
    # UTILITIES
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get worker statistics.

        Returns:
            Dictionary of statistics
        """
        avg_time = (
            self._total_processing_time_ms / self._total_checks
            if self._total_checks > 0
            else 0
        )

        success_rate = (
            (self._total_checks - self._failed_checks) / self._total_checks
            if self._total_checks > 0
            else 0
        )

        return {
            "total_checks": self._total_checks,
            "total_suggestions": self._total_suggestions,
            "avg_processing_time_ms": avg_time,
            "failed_checks": self._failed_checks,
            "success_rate": success_rate,
            "current_model": self._model,
            "enabled": self._enabled,
        }

    # ========================================================================
    # CLEANUP
    # ========================================================================

    @Slot()
    def cleanup(self):
        """Clean up resources before shutdown."""
        logger.info("OllamaGrammarWorker cleanup started")

        try:
            # Log final statistics
            stats = self.get_statistics()
            logger.info(f"Final statistics: {stats}")

        except Exception as e:
            logger.error(f"Cleanup error: {e}", exc_info=True)

        logger.info("OllamaGrammarWorker cleanup complete")
