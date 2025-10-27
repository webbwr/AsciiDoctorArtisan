"""
Unit tests for grammar system data models.
"""

import pytest

from asciidoc_artisan.core import GrammarResult, GrammarSuggestion
from asciidoc_artisan.core.grammar_models import GrammarCategory, GrammarSeverity


@pytest.mark.unit
class TestGrammarSuggestion:
    """Test GrammarSuggestion dataclass."""

    def test_create_suggestion(self):
        """Test creating a grammar suggestion."""
        sugg = GrammarSuggestion(
            start=10,
            end=20,
            message="Test message",
            category=GrammarCategory.GRAMMAR,
            replacements=["fix1", "fix2"],
            rule_id="TEST_RULE",
        )

        assert sugg.start == 10
        assert sugg.end == 20
        assert sugg.message == "Test message"
        assert sugg.category == GrammarCategory.GRAMMAR
        assert sugg.replacements == ["fix1", "fix2"]
        assert sugg.rule_id == "TEST_RULE"
        assert sugg.context == ""

    def test_suggestion_with_context(self):
        """Test suggestion with context."""
        sugg = GrammarSuggestion(
            start=5,
            end=10,
            message="Error",
            category=GrammarCategory.SPELLING,
            context="this is a test context",
        )

        assert sugg.context == "this is a test context"
        assert len(sugg.replacements) == 0

    def test_suggestion_categories(self):
        """Test all suggestion categories are valid."""
        assert GrammarCategory.GRAMMAR.value == "grammar"
        assert GrammarCategory.STYLE.value == "style"
        assert GrammarCategory.SPELLING.value == "spelling"
        assert GrammarCategory.AI_SUGGESTION.value == "ai"


@pytest.mark.unit
class TestGrammarResult:
    """Test GrammarResult dataclass."""

    def test_successful_result(self):
        """Test creating successful grammar result."""
        suggestions = [
            GrammarSuggestion(
                start=0, end=5, message="Test", suggestion_type=SuggestionType.GRAMMAR
            )
        ]

        result = GrammarResult(
            success=True,
            suggestions=suggestions,
            error_message="",
            processing_time_ms=150.5,
            word_count=100,
            suggestion_count=1,
            cached=False,
        )

        assert result.success is True
        assert len(result.suggestions) == 1
        assert result.error_message == ""
        assert result.processing_time_ms == 150.5
        assert result.word_count == 100
        assert result.suggestion_count == 1
        assert result.cached is False

    def test_failed_result(self):
        """Test creating failed grammar result."""
        result = GrammarResult(
            success=False,
            suggestions=[],
            error_message="Connection failed",
            processing_time_ms=0,
            word_count=0,
            suggestion_count=0,
            cached=False,
        )

        assert result.success is False
        assert len(result.suggestions) == 0
        assert result.error_message == "Connection failed"

    def test_cached_result(self):
        """Test cached result flag."""
        result = GrammarResult(
            success=True,
            suggestions=[],
            error_message="",
            processing_time_ms=5.0,
            word_count=50,
            suggestion_count=0,
            cached=True,
        )

        assert result.cached is True
        assert result.processing_time_ms < 10  # Should be fast


@pytest.mark.unit
class TestGrammarConfig:
    """Test GrammarConfig dataclass."""

    def test_default_config(self):
        """Test default grammar configuration."""
        config = GrammarConfig()

        assert config.enabled is False
        assert config.auto_check is False
        assert config.ai_suggestions_enabled is False
        assert config.checking_mode == CheckingMode.HYBRID
        assert config.performance_profile == PerformanceProfile.BALANCED
        assert config.language == "en-US"
        assert config.check_delay_ms == 500

    def test_custom_config(self):
        """Test custom grammar configuration."""
        config = GrammarConfig(
            enabled=True,
            auto_check=True,
            ai_suggestions_enabled=True,
            checking_mode=CheckingMode.LANGUAGETOOL_ONLY,
            performance_profile=PerformanceProfile.REAL_TIME,
            language="en-GB",
            check_delay_ms=1000,
        )

        assert config.enabled is True
        assert config.auto_check is True
        assert config.ai_suggestions_enabled is True
        assert config.checking_mode == CheckingMode.LANGUAGETOOL_ONLY
        assert config.performance_profile == PerformanceProfile.REAL_TIME
        assert config.language == "en-GB"
        assert config.check_delay_ms == 1000

    def test_checking_modes(self):
        """Test all checking modes are valid."""
        assert CheckingMode.HYBRID.value == "hybrid"
        assert CheckingMode.LANGUAGETOOL_ONLY.value == "languagetool_only"
        assert CheckingMode.OLLAMA_ONLY.value == "ollama_only"
        assert CheckingMode.DISABLED.value == "disabled"

    def test_performance_profiles(self):
        """Test all performance profiles are valid."""
        assert PerformanceProfile.BALANCED.value == "balanced"
        assert PerformanceProfile.REAL_TIME.value == "real_time"
        assert PerformanceProfile.THOROUGH.value == "thorough"


@pytest.mark.unit
class TestGrammarStatistics:
    """Test grammar checking statistics tracking."""

    def test_suggestion_counts(self):
        """Test counting suggestions by type."""
        suggestions = [
            GrammarSuggestion(
                start=0, end=5, message="G1", category=GrammarCategory.GRAMMAR
            ),
            GrammarSuggestion(
                start=10, end=15, message="G2", category=GrammarCategory.GRAMMAR
            ),
            GrammarSuggestion(
                start=20, end=25, message="S1", category=GrammarCategory.STYLE
            ),
            GrammarSuggestion(
                start=30, end=35, message="SP1", category=GrammarCategory.SPELLING
            ),
        ]

        grammar_count = sum(
            1 for s in suggestions if s.category == GrammarCategory.GRAMMAR
        )
        style_count = sum(1 for s in suggestions if s.category == GrammarCategory.STYLE)
        spelling_count = sum(
            1 for s in suggestions if s.category == GrammarCategory.SPELLING
        )

        assert grammar_count == 2
        assert style_count == 1
        assert spelling_count == 1
        assert len(suggestions) == 4

    def test_result_statistics(self):
        """Test result provides correct statistics."""
        suggestions = [
            GrammarSuggestion(
                start=i * 10,
                end=(i + 1) * 10,
                message=f"Issue {i}",
                category=GrammarCategory.GRAMMAR,
            )
            for i in range(5)
        ]

        result = GrammarResult(
            success=True,
            suggestions=suggestions,
            error_message="",
            processing_time_ms=200.0,
            word_count=150,
            cached=False,
        )

        assert len(result.suggestions) == 5
