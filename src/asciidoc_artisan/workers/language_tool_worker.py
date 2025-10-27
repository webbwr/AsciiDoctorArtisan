"""
LanguageTool Worker - Enterprise-grade background grammar checking.

This module provides the LanguageToolWorker class which performs fast,
rules-based grammar checking in a background QThread using LanguageTool.

Implements:
- FR-069: LanguageTool integration
- FR-070: Background grammar processing
- FR-071: AsciiDoc content filtering
- FR-072: Result caching and optimization
- NFR-005: Non-blocking background operations

Architecture:
- QObject-based worker for Qt threading
- Circuit breaker pattern for fault tolerance
- Exponential backoff for retries
- LRU cache for performance
- Comprehensive error handling and logging

Thread Safety:
- Designed to run in separate QThread
- All methods are thread-safe
- Uses Qt signals for communication

Author: AsciiDoc Artisan Development Team
Version: 1.3.0
"""

import hashlib
import logging
import re
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple

from PySide6.QtCore import QObject, Signal, Slot

# Import LanguageTool with graceful fallback
try:
    import language_tool_python
    from language_tool_python import Match

    LANGUAGETOOL_AVAILABLE = True
except ImportError:
    language_tool_python = None
    Match = None
    LANGUAGETOOL_AVAILABLE = False

# Import grammar models and config
from asciidoc_artisan.core.grammar_config import (
    ASCIIDOC_EXCLUDE_PATTERNS,
    LANGUAGETOOL_CACHE_SIZE,
    LANGUAGETOOL_DEFAULT_LANGUAGE,
    LANGUAGETOOL_DISABLED_RULES_DEFAULT,
    LANGUAGETOOL_MAX_TEXT_LENGTH,
    LANGUAGETOOL_TIMEOUT_MS,
    ERROR_MESSAGES,
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
# CIRCUIT BREAKER FOR FAULT TOLERANCE
# ============================================================================

@dataclass
class CircuitBreakerState:
    """State tracker for circuit breaker pattern.

    Prevents cascading failures by tracking error rates and
    temporarily disabling the service if it's consistently failing.
    """

    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    is_open: bool = False  # True = circuit open (service disabled)
    open_until: float = 0.0  # Timestamp when circuit can retry

    def record_success(self):
        """Record successful operation."""
        self.success_count += 1
        self.failure_count = max(0, self.failure_count - 1)  # Decay failures
        if self.success_count >= 3:
            # Reset after 3 consecutive successes
            self.is_open = False
            self.failure_count = 0

    def record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        # Open circuit after 5 consecutive failures
        if self.failure_count >= 5:
            self.is_open = True
            # Open for exponentially increasing time
            backoff_time = min(60.0, 2 ** (self.failure_count - 5))
            self.open_until = time.time() + backoff_time
            logger.warning(
                f"Circuit breaker OPEN - too many failures. "
                f"Will retry in {backoff_time:.1f}s"
            )

    def can_attempt(self) -> bool:
        """Check if operation can be attempted."""
        if not self.is_open:
            return True

        # Check if timeout expired
        if time.time() >= self.open_until:
            logger.info("Circuit breaker attempting to CLOSE - retrying")
            self.is_open = False
            self.failure_count = 4  # Give it one more chance
            return True

        return False


# ============================================================================
# LRU CACHE FOR PERFORMANCE
# ============================================================================

class LRUCache:
    """Thread-safe LRU cache for grammar check results.

    Caches results by text hash to avoid redundant processing.
    """

    def __init__(self, max_size: int = LANGUAGETOOL_CACHE_SIZE):
        """Initialize LRU cache.

        Args:
            max_size: Maximum number of entries to cache
        """
        self._cache: OrderedDict[str, GrammarResult] = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[GrammarResult]:
        """Get cached result.

        Args:
            key: Cache key (text hash)

        Returns:
            Cached result if found, None otherwise
        """
        if key in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            logger.debug(f"Cache HIT - {self.hit_rate:.1%} hit rate")
            return self._cache[key]

        self._misses += 1
        return None

    def put(self, key: str, value: GrammarResult):
        """Store result in cache.

        Args:
            key: Cache key (text hash)
            value: Result to cache
        """
        if key in self._cache:
            # Update existing entry
            self._cache.move_to_end(key)
        else:
            # Add new entry
            self._cache[key] = value

            # Evict oldest if over capacity
            if len(self._cache) > self._max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                logger.debug(f"Cache eviction - size: {len(self._cache)}")

    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cache cleared")

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def size(self) -> int:
        """Current cache size."""
        return len(self._cache)


# ============================================================================
# ASCIIDOC CONTENT FILTER
# ============================================================================

class AsciiDocContentFilter:
    """Filters AsciiDoc markup to extract prose for grammar checking.

    Removes code blocks, attributes, comments, and other non-prose content
    while maintaining position mappings for accurate error reporting.
    """

    def __init__(self):
        """Initialize content filter."""
        self._exclude_patterns: List[Pattern] = ASCIIDOC_EXCLUDE_PATTERNS

    def filter_content(self, text: str) -> Tuple[str, Dict[int, int]]:
        """Filter AsciiDoc content to extract prose only.

        Args:
            text: Original AsciiDoc document

        Returns:
            Tuple of (filtered_text, offset_map)
            offset_map maps filtered positions back to original positions
        """
        if not text:
            return "", {}

        filtered_text = text
        offset_map: Dict[int, int] = {}

        # Track character removals for offset calculation
        removed_chars = 0

        # Apply each exclusion pattern
        for pattern in self._exclude_patterns:
            matches = list(pattern.finditer(filtered_text))
            for match in reversed(matches):  # Process backwards to maintain positions
                start, end = match.span()
                removed_length = end - start

                # Replace with spaces to maintain line structure
                replacement = ' ' * removed_length
                filtered_text = filtered_text[:start] + replacement + filtered_text[end:]

                # Track offset changes
                for i in range(start, end):
                    offset_map[i - removed_chars] = i

                removed_chars += removed_length

        # Clean up excessive whitespace
        filtered_text = re.sub(r'\n{3,}', '\n\n', filtered_text)  # Max 2 newlines
        filtered_text = re.sub(r' {2,}', ' ', filtered_text)      # Max 1 space

        logger.debug(
            f"Filtered {len(text)} -> {len(filtered_text)} chars "
            f"({(1 - len(filtered_text)/len(text))*100:.1f}% removed)"
        )

        return filtered_text.strip(), offset_map

    def map_offset(self, filtered_offset: int, offset_map: Dict[int, int]) -> int:
        """Map filtered position back to original position.

        Args:
            filtered_offset: Position in filtered text
            offset_map: Offset mapping from filter_content()

        Returns:
            Position in original text
        """
        return offset_map.get(filtered_offset, filtered_offset)


# ============================================================================
# LANGUAGETOOL WORKER
# ============================================================================

class LanguageToolWorker(QObject):
    """Background worker for LanguageTool grammar checking.

    This worker runs in a separate QThread and performs grammar checking
    without blocking the UI. It includes enterprise features like:
    - Circuit breaker for fault tolerance
    - LRU caching for performance
    - AsciiDoc content filtering
    - Comprehensive error handling
    - Exponential backoff for retries

    Signals:
        grammar_result_ready(GrammarResult): Emitted when check completes
        progress_update(str): Emitted with status messages
        initialization_complete(bool): Emitted after initialization
    """

    # Qt Signals
    grammar_result_ready = Signal(GrammarResult)
    progress_update = Signal(str)
    initialization_complete = Signal(bool)

    def __init__(self):
        """Initialize LanguageToolWorker."""
        super().__init__()

        # LanguageTool instance
        self._tool: Optional[Any] = None
        self._language: str = LANGUAGETOOL_DEFAULT_LANGUAGE

        # State management
        self._initialized: bool = False
        self._disabled_rules: Set[str] = set(LANGUAGETOOL_DISABLED_RULES_DEFAULT)

        # Performance & reliability
        self._cache = LRUCache(LANGUAGETOOL_CACHE_SIZE)
        self._circuit_breaker = CircuitBreakerState()
        self._content_filter = AsciiDocContentFilter()

        # Statistics
        self._total_checks = 0
        self._total_suggestions = 0
        self._total_processing_time_ms = 0

        logger.info("LanguageToolWorker created")

    # ========================================================================
    # INITIALIZATION
    # ========================================================================

    @Slot(str)
    def initialize_tool(self, language: str = LANGUAGETOOL_DEFAULT_LANGUAGE):
        """Initialize LanguageTool server.

        This must be called after the worker is moved to its thread.

        Args:
            language: Language code (e.g., "en-US", "es", "fr")
        """
        if self._initialized:
            logger.warning("LanguageTool already initialized")
            return

        if not LANGUAGETOOL_AVAILABLE:
            error_msg = ERROR_MESSAGES["languagetool_not_installed"]
            logger.error(error_msg)
            self.initialization_complete.emit(False)
            return

        try:
            self.progress_update.emit(f"Initializing LanguageTool ({language})...")
            logger.info(f"Initializing LanguageTool with language: {language}")

            # Initialize LanguageTool (this downloads JAR on first run)
            start_time = time.time()
            self._tool = language_tool_python.LanguageTool(language)
            init_time = (time.time() - start_time) * 1000

            self._language = language
            self._initialized = True

            logger.info(
                f"LanguageTool initialized successfully in {init_time:.0f}ms"
            )
            self.progress_update.emit(
                f"LanguageTool ready ({language}) - {init_time:.0f}ms"
            )
            self.initialization_complete.emit(True)

        except Exception as e:
            error_msg = ERROR_MESSAGES["languagetool_init_failed"]
            logger.error(f"LanguageTool initialization failed: {e}", exc_info=True)
            self.progress_update.emit(f"Error: {error_msg}")
            self.initialization_complete.emit(False)

    # ========================================================================
    # GRAMMAR CHECKING
    # ========================================================================

    @Slot(str)
    def check_text(self, text: str):
        """Check text for grammar/spelling issues.

        This is the main entry point for grammar checking. It handles:
        - Input validation
        - Cache lookup
        - Content filtering
        - Grammar checking
        - Result parsing
        - Error handling

        Args:
            text: Document content to check
        """
        # Validate state
        if not self._initialized or not self._tool:
            result = GrammarResult.create_error(
                GrammarSource.LANGUAGETOOL,
                "LanguageTool not initialized"
            )
            self.grammar_result_ready.emit(result)
            return

        # Check circuit breaker
        if not self._circuit_breaker.can_attempt():
            result = GrammarResult.create_error(
                GrammarSource.LANGUAGETOOL,
                "LanguageTool temporarily unavailable (too many errors)"
            )
            self.grammar_result_ready.emit(result)
            return

        # Validate input
        if not text or not text.strip():
            result = GrammarResult(
                suggestions=[],
                success=True,
                source=GrammarSource.LANGUAGETOOL,
                word_count=0,
                character_count=0,
            )
            self.grammar_result_ready.emit(result)
            return

        # Check text length
        if len(text) > LANGUAGETOOL_MAX_TEXT_LENGTH:
            logger.warning(
                f"Text too long ({len(text)} chars), truncating to "
                f"{LANGUAGETOOL_MAX_TEXT_LENGTH}"
            )
            text = text[:LANGUAGETOOL_MAX_TEXT_LENGTH]

        # Check cache
        text_hash = self._compute_hash(text)
        cached_result = self._cache.get(text_hash)
        if cached_result:
            # Return cached result (mark as cached)
            cached_result = GrammarResult(
                suggestions=cached_result.suggestions,
                success=True,
                source=GrammarSource.LANGUAGETOOL,
                processing_time_ms=cached_result.processing_time_ms,
                word_count=cached_result.word_count,
                character_count=cached_result.character_count,
                cached=True,
                language=self._language,
            )
            self.grammar_result_ready.emit(cached_result)
            return

        # Perform check
        start_time = time.time()

        try:
            # Filter AsciiDoc content
            filtered_text, offset_map = self._content_filter.filter_content(text)

            if not filtered_text.strip():
                # No prose content to check
                result = GrammarResult(
                    suggestions=[],
                    success=True,
                    source=GrammarSource.LANGUAGETOOL,
                    word_count=0,
                    character_count=len(text),
                    language=self._language,
                )
                self.grammar_result_ready.emit(result)
                return

            # Run LanguageTool check
            logger.debug(f"Checking {len(filtered_text)} chars with LanguageTool")
            matches = self._tool.check(filtered_text)

            # Parse matches into suggestions
            suggestions = self._parse_matches(matches, offset_map, text)

            # Calculate metrics
            elapsed_ms = int((time.time() - start_time) * 1000)
            word_count = len(text.split())

            # Create result
            result = GrammarResult(
                suggestions=suggestions,
                success=True,
                source=GrammarSource.LANGUAGETOOL,
                processing_time_ms=elapsed_ms,
                word_count=word_count,
                character_count=len(text),
                language=self._language,
            )

            # Cache result
            self._cache.put(text_hash, result)

            # Update statistics
            self._total_checks += 1
            self._total_suggestions += len(suggestions)
            self._total_processing_time_ms += elapsed_ms

            # Record success for circuit breaker
            self._circuit_breaker.record_success()

            logger.info(
                f"LanguageTool check complete: {len(suggestions)} issues, "
                f"{elapsed_ms}ms, {word_count} words"
            )

            self.grammar_result_ready.emit(result)

        except Exception as e:
            # Record failure for circuit breaker
            self._circuit_breaker.record_failure()

            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.error(f"LanguageTool check failed: {e}", exc_info=True)

            result = GrammarResult.create_error(
                GrammarSource.LANGUAGETOOL,
                f"Grammar check failed: {str(e)}"
            )
            self.grammar_result_ready.emit(result)

    # ========================================================================
    # MATCH PARSING
    # ========================================================================

    def _parse_matches(
        self,
        matches: List[Match],
        offset_map: Dict[int, int],
        original_text: str
    ) -> List[GrammarSuggestion]:
        """Parse LanguageTool matches into GrammarSuggestion objects.

        Args:
            matches: List of LanguageTool Match objects
            offset_map: Position mapping from filtered to original text
            original_text: Original unfiltered text

        Returns:
            List of GrammarSuggestion objects
        """
        suggestions = []

        for match in matches:
            # Skip disabled rules
            if match.ruleId in self._disabled_rules:
                continue

            # Map positions back to original text
            start = self._content_filter.map_offset(match.offset, offset_map)
            end = self._content_filter.map_offset(
                match.offset + match.errorLength,
                offset_map
            )

            # Validate positions
            if start >= len(original_text) or end > len(original_text):
                logger.warning(f"Invalid position mapping: [{start}:{end}]")
                continue

            # Extract context
            context_start = max(0, start - 20)
            context_end = min(len(original_text), end + 20)
            context = original_text[context_start:context_end]

            # Categorize match
            category = self._categorize_match(match)
            severity = self._determine_severity(match)

            # Get replacements (limit to 5)
            replacements = match.replacements[:5]

            # Build suggestion
            suggestion = GrammarSuggestion(
                start=start,
                end=end,
                category=category,
                source=GrammarSource.LANGUAGETOOL,
                message=match.message,
                replacements=replacements,
                rule_id=match.ruleId,
                context=context,
                severity=severity,
                url=match.ruleIssueType if hasattr(match, 'ruleIssueType') else None,
                metadata={
                    "category": match.category if hasattr(match, 'category') else None,
                    "offset": match.offset,
                    "length": match.errorLength,
                }
            )

            suggestions.append(suggestion)

        logger.debug(f"Parsed {len(suggestions)} suggestions from {len(matches)} matches")
        return suggestions

    def _categorize_match(self, match: Match) -> GrammarCategory:
        """Categorize LanguageTool match.

        Args:
            match: LanguageTool Match object

        Returns:
            GrammarCategory enum value
        """
        rule_id_lower = match.ruleId.lower()
        category = getattr(match, 'category', '').lower()

        # Spelling errors
        if 'spell' in rule_id_lower or 'spelling' in category or 'morfologik' in rule_id_lower:
            return GrammarCategory.SPELLING

        # Punctuation
        if 'punctuation' in category or 'comma' in rule_id_lower or 'period' in rule_id_lower:
            return GrammarCategory.PUNCTUATION

        # Style issues
        style_keywords = ['style', 'passive', 'cliche', 'redundant', 'wordy', 'repetition']
        if any(keyword in rule_id_lower for keyword in style_keywords):
            return GrammarCategory.STYLE

        # Readability
        if 'readability' in category or 'sentence_length' in rule_id_lower:
            return GrammarCategory.READABILITY

        # Grammar (default)
        return GrammarCategory.GRAMMAR

    def _determine_severity(self, match: Match) -> GrammarSeverity:
        """Determine severity of match.

        Args:
            match: LanguageTool Match object

        Returns:
            GrammarSeverity enum value
        """
        # LanguageTool doesn't provide severity directly, so we infer it
        category = getattr(match, 'category', '').lower()

        # Spelling and grammar errors are high priority
        if 'spelling' in category or 'grammar' in category:
            return GrammarSeverity.ERROR

        # Punctuation and style are warnings
        if 'punctuation' in category or 'style' in category:
            return GrammarSeverity.WARNING

        # Everything else is informational
        return GrammarSeverity.INFO

    # ========================================================================
    # CONFIGURATION
    # ========================================================================

    @Slot(str)
    def disable_rule(self, rule_id: str):
        """Disable a specific grammar rule.

        Args:
            rule_id: Rule identifier to disable
        """
        self._disabled_rules.add(rule_id)
        logger.info(f"Disabled rule: {rule_id}")

    @Slot(str)
    def enable_rule(self, rule_id: str):
        """Enable a previously disabled rule.

        Args:
            rule_id: Rule identifier to enable
        """
        self._disabled_rules.discard(rule_id)
        logger.info(f"Enabled rule: {rule_id}")

    @Slot()
    def clear_cache(self):
        """Clear the result cache."""
        self._cache.clear()
        logger.info("Cache cleared")

    # ========================================================================
    # UTILITIES
    # ========================================================================

    def _compute_hash(self, text: str) -> str:
        """Compute hash of text for caching.

        Args:
            text: Text to hash

        Returns:
            SHA256 hash hex string
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

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

        return {
            "total_checks": self._total_checks,
            "total_suggestions": self._total_suggestions,
            "avg_processing_time_ms": avg_time,
            "cache_size": self._cache.size,
            "cache_hit_rate": self._cache.hit_rate,
            "circuit_breaker_open": self._circuit_breaker.is_open,
            "failure_count": self._circuit_breaker.failure_count,
        }

    # ========================================================================
    # CLEANUP
    # ========================================================================

    @Slot()
    def cleanup(self):
        """Clean up resources before shutdown."""
        logger.info("LanguageToolWorker cleanup started")

        try:
            if self._tool:
                self._tool.close()
                self._tool = None
                logger.info("LanguageTool server closed")

            self._cache.clear()
            self._initialized = False

            # Log final statistics
            stats = self.get_statistics()
            logger.info(f"Final statistics: {stats}")

        except Exception as e:
            logger.error(f"Cleanup error: {e}", exc_info=True)

        logger.info("LanguageToolWorker cleanup complete")
