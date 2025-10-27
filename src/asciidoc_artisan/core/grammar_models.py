"""
Grammar Models - Type-safe data models for grammar checking system.

This module provides enterprise-grade data models for the hybrid grammar
checking system (LanguageTool + Ollama AI).

Implements:
- FR-063: Grammar checking data structures
- FR-064: Type-safe suggestion models
- FR-065: Result aggregation models

Architecture:
- Immutable dataclasses for thread safety
- Enum types for categorical data
- Comprehensive validation
- JSON serialization support

Author: AsciiDoc Artisan Development Team
Version: 1.3.0
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class GrammarSource(Enum):
    """Source of grammar suggestion.

    Distinguishes between rules-based and AI-based checking.
    """

    LANGUAGETOOL = "languagetool"  # Rules-based grammar checker
    OLLAMA = "ollama"  # AI-powered style analyzer
    HYBRID = "hybrid"  # Combined analysis

    def __str__(self) -> str:
        """Human-readable source name."""
        return self.value.title()


class GrammarCategory(Enum):
    """Category of grammar issue.

    Maps to visual indicators (underline colors) in the editor.
    """

    GRAMMAR = "grammar"  # Red underline - Grammar errors
    STYLE = "style"  # Blue underline - Style issues
    SPELLING = "spelling"  # Orange underline - Spelling mistakes
    AI_SUGGESTION = "ai"  # Green underline - AI improvements
    PUNCTUATION = "punctuation"  # Purple underline - Punctuation
    READABILITY = "readability"  # Yellow underline - Readability

    def __str__(self) -> str:
        """Human-readable category name."""
        return self.value.title()

    def get_color_rgb(self) -> tuple[int, int, int]:
        """Get RGB color for this category.

        Returns:
            Tuple of (red, green, blue) values (0-255)
        """
        color_map = {
            GrammarCategory.GRAMMAR: (255, 0, 0),  # Red
            GrammarCategory.STYLE: (0, 0, 255),  # Blue
            GrammarCategory.SPELLING: (255, 165, 0),  # Orange
            GrammarCategory.AI_SUGGESTION: (0, 200, 0),  # Green
            GrammarCategory.PUNCTUATION: (128, 0, 128),  # Purple
            GrammarCategory.READABILITY: (255, 215, 0),  # Gold
        }
        return color_map.get(self, (128, 128, 128))  # Gray default


class GrammarSeverity(Enum):
    """Severity level of grammar issue."""

    ERROR = "error"  # Critical grammar error
    WARNING = "warning"  # Style or minor grammar issue
    INFO = "info"  # Informational suggestion
    HINT = "hint"  # Subtle improvement hint

    def __str__(self) -> str:
        """Human-readable severity name."""
        return self.value.title()

    def get_priority(self) -> int:
        """Get numeric priority for sorting.

        Returns:
            Priority value (higher = more important)
        """
        priority_map = {
            GrammarSeverity.ERROR: 4,
            GrammarSeverity.WARNING: 3,
            GrammarSeverity.INFO: 2,
            GrammarSeverity.HINT: 1,
        }
        return priority_map.get(self, 0)


@dataclass(frozen=True)
class GrammarSuggestion:
    """Single grammar/style suggestion.

    Immutable data structure representing one grammar issue detected
    by either LanguageTool or Ollama AI.

    Attributes:
        start: Character offset in document (0-indexed)
        end: Character offset in document (exclusive)
        category: Type of issue (grammar, style, spelling, etc.)
        source: Which engine detected this (LanguageTool or Ollama)
        message: Human-readable explanation of the issue
        replacements: List of suggested fixes (ordered by confidence)
        rule_id: Unique identifier for this rule (for ignoring)
        context: Surrounding text for display
        severity: Severity level of the issue
        url: Optional URL to documentation/explanation
        metadata: Additional metadata (confidence scores, etc.)

    Thread Safety:
        This is a frozen dataclass, making it immutable and thread-safe.
    """

    start: int
    end: int
    category: GrammarCategory
    source: GrammarSource
    message: str
    replacements: List[str] = field(default_factory=list)
    rule_id: str = ""
    context: str = ""
    severity: GrammarSeverity = GrammarSeverity.WARNING
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate suggestion data."""
        if self.start < 0:
            raise ValueError(f"start must be >= 0, got {self.start}")
        if self.end <= self.start:
            raise ValueError(f"end ({self.end}) must be > start ({self.start})")
        if not self.message:
            raise ValueError("message cannot be empty")

    @property
    def length(self) -> int:
        """Length of the flagged text."""
        return self.end - self.start

    @property
    def has_replacements(self) -> bool:
        """Whether this suggestion has replacement options."""
        return len(self.replacements) > 0

    @property
    def primary_replacement(self) -> Optional[str]:
        """Primary (most confident) replacement suggestion."""
        return self.replacements[0] if self.replacements else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "start": self.start,
            "end": self.end,
            "category": self.category.value,
            "source": self.source.value,
            "message": self.message,
            "replacements": self.replacements,
            "rule_id": self.rule_id,
            "context": self.context,
            "severity": self.severity.value,
            "url": self.url,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GrammarSuggestion":
        """Create suggestion from dictionary."""
        return cls(
            start=data["start"],
            end=data["end"],
            category=GrammarCategory(data["category"]),
            source=GrammarSource(data["source"]),
            message=data["message"],
            replacements=data.get("replacements", []),
            rule_id=data.get("rule_id", ""),
            context=data.get("context", ""),
            severity=GrammarSeverity(data.get("severity", "warning")),
            url=data.get("url"),
            metadata=data.get("metadata", {}),
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.category} at [{self.start}:{self.end}]: {self.message}"


@dataclass(frozen=True)
class GrammarResult:
    """Complete grammar check result from one engine.

    Represents the output of a single grammar checking pass
    (either LanguageTool or Ollama AI).

    Attributes:
        suggestions: List of detected issues
        success: Whether the check completed successfully
        source: Which engine produced this result
        error_message: Error details if check failed
        processing_time_ms: Time taken to process (milliseconds)
        word_count: Number of words analyzed
        character_count: Number of characters analyzed
        cached: Whether result came from cache
        model_name: Name of model used (for Ollama)
        language: Language code (for LanguageTool)

    Thread Safety:
        This is a frozen dataclass, making it immutable and thread-safe.
    """

    suggestions: List[GrammarSuggestion] = field(default_factory=list)
    success: bool = True
    source: GrammarSource = GrammarSource.LANGUAGETOOL
    error_message: Optional[str] = None
    processing_time_ms: int = 0
    word_count: int = 0
    character_count: int = 0
    cached: bool = False
    model_name: Optional[str] = None
    language: str = "en-US"

    @property
    def suggestion_count(self) -> int:
        """Total number of suggestions."""
        return len(self.suggestions)

    @property
    def has_errors(self) -> bool:
        """Whether any ERROR-level issues were found."""
        return any(s.severity == GrammarSeverity.ERROR for s in self.suggestions)

    @property
    def has_warnings(self) -> bool:
        """Whether any WARNING-level issues were found."""
        return any(s.severity == GrammarSeverity.WARNING for s in self.suggestions)

    def get_suggestions_by_category(
        self, category: GrammarCategory
    ) -> List[GrammarSuggestion]:
        """Get all suggestions of a specific category."""
        return [s for s in self.suggestions if s.category == category]

    def get_suggestions_by_severity(
        self, severity: GrammarSeverity
    ) -> List[GrammarSuggestion]:
        """Get all suggestions of a specific severity."""
        return [s for s in self.suggestions if s.severity == severity]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "suggestions": [s.to_dict() for s in self.suggestions],
            "success": self.success,
            "source": self.source.value,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "cached": self.cached,
            "model_name": self.model_name,
            "language": self.language,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GrammarResult":
        """Create result from dictionary."""
        return cls(
            suggestions=[
                GrammarSuggestion.from_dict(s) for s in data.get("suggestions", [])
            ],
            success=data.get("success", True),
            source=GrammarSource(data.get("source", "languagetool")),
            error_message=data.get("error_message"),
            processing_time_ms=data.get("processing_time_ms", 0),
            word_count=data.get("word_count", 0),
            character_count=data.get("character_count", 0),
            cached=data.get("cached", False),
            model_name=data.get("model_name"),
            language=data.get("language", "en-US"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "GrammarResult":
        """Create result from JSON string."""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def create_error(
        cls,
        source: GrammarSource,
        error_message: str,
    ) -> "GrammarResult":
        """Create an error result.

        Args:
            source: Which engine failed
            error_message: Error details

        Returns:
            GrammarResult with success=False
        """
        return cls(
            suggestions=[],
            success=False,
            source=source,
            error_message=error_message,
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        if not self.success:
            return f"GrammarResult(ERROR: {self.error_message})"
        return f"GrammarResult({self.source}: {self.suggestion_count} suggestions, {self.processing_time_ms}ms)"


@dataclass(frozen=True)
class AggregatedGrammarResult:
    """Aggregated result from multiple grammar engines.

    Combines results from both LanguageTool and Ollama AI,
    with deduplication and merging logic.

    Attributes:
        languagetool_result: Result from LanguageTool (if available)
        ollama_result: Result from Ollama AI (if available)
        merged_suggestions: Deduplicated list of all suggestions
        total_processing_time_ms: Combined processing time
    """

    languagetool_result: Optional[GrammarResult] = None
    ollama_result: Optional[GrammarResult] = None
    merged_suggestions: List[GrammarSuggestion] = field(default_factory=list)
    total_processing_time_ms: int = 0

    @property
    def success(self) -> bool:
        """Whether at least one engine succeeded."""
        lt_success = (
            self.languagetool_result.success if self.languagetool_result else False
        )
        ollama_success = self.ollama_result.success if self.ollama_result else False
        return lt_success or ollama_success

    @property
    def suggestion_count(self) -> int:
        """Total number of merged suggestions."""
        return len(self.merged_suggestions)

    @property
    def languagetool_count(self) -> int:
        """Number of suggestions from LanguageTool."""
        return sum(
            1 for s in self.merged_suggestions if s.source == GrammarSource.LANGUAGETOOL
        )

    @property
    def ollama_count(self) -> int:
        """Number of suggestions from Ollama."""
        return sum(
            1 for s in self.merged_suggestions if s.source == GrammarSource.OLLAMA
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about the results."""
        stats: Dict[str, Any] = {
            "total_suggestions": self.suggestion_count,
            "languagetool_suggestions": self.languagetool_count,
            "ollama_suggestions": self.ollama_count,
            "processing_time_ms": self.total_processing_time_ms,
            "by_category": {},
            "by_severity": {},
        }

        # Count by category
        for category in GrammarCategory:
            count = sum(1 for s in self.merged_suggestions if s.category == category)
            if count > 0:
                stats["by_category"][category.value] = count

        # Count by severity
        for severity in GrammarSeverity:
            count = sum(1 for s in self.merged_suggestions if s.severity == severity)
            if count > 0:
                stats["by_severity"][severity.value] = count

        return stats

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"AggregatedResult({self.suggestion_count} suggestions: LT={self.languagetool_count}, Ollama={self.ollama_count})"


# Type aliases for convenience
SuggestionList = List[GrammarSuggestion]
ResultCallback = Any  # Qt Signal type (can't be properly typed here)
