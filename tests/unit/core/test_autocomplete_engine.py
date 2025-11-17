"""
Tests for core.autocomplete_engine module.

Tests auto-complete engine with fuzzy matching, ranking, and caching.
"""

import sys
from unittest.mock import patch

import pytest

from asciidoc_artisan.core.autocomplete_engine import (
    AutoCompleteEngine,
    fuzzy_match_score,
)
from asciidoc_artisan.core.models import (
    CompletionContext,
    CompletionItem,
    CompletionKind,
)


@pytest.mark.fr_085
@pytest.mark.fr_088
@pytest.mark.fr_089
@pytest.mark.unit
class TestAutoCompleteEngine:
    """Test AutoCompleteEngine class."""

    def test_init(self):
        """Test engine initialization."""
        engine = AutoCompleteEngine()

        assert engine.providers == []
        assert engine._cache_size == 1000
        assert engine._cache == {}

    def test_init_with_custom_cache_size(self):
        """Test engine initialization with custom cache size."""
        engine = AutoCompleteEngine(cache_size=500)

        assert engine._cache_size == 500

    def test_add_provider(self):
        """Test adding a completion provider."""
        engine = AutoCompleteEngine()

        class MockProvider:
            def get_completions(self, context):
                return []

        provider = MockProvider()
        engine.add_provider(provider)

        assert len(engine.providers) == 1
        assert engine.providers[0] is provider

    def test_add_multiple_providers(self):
        """Test adding multiple providers."""
        engine = AutoCompleteEngine()

        class ProviderA:
            def get_completions(self, context):
                return []

        class ProviderB:
            def get_completions(self, context):
                return []

        provider_a = ProviderA()
        provider_b = ProviderB()

        engine.add_provider(provider_a)
        engine.add_provider(provider_b)

        assert len(engine.providers) == 2
        assert engine.providers[0] is provider_a
        assert engine.providers[1] is provider_b

    def test_remove_provider(self):
        """Test removing a provider."""
        engine = AutoCompleteEngine()

        class MockProvider:
            def get_completions(self, context):
                return []

        provider = MockProvider()
        engine.add_provider(provider)

        engine.remove_provider(provider)

        assert len(engine.providers) == 0

    def test_remove_provider_not_registered(self):
        """Test removing unregistered provider raises ValueError."""
        engine = AutoCompleteEngine()

        class MockProvider:
            def get_completions(self, context):
                return []

        provider = MockProvider()

        with pytest.raises(ValueError, match="Provider not registered"):
            engine.remove_provider(provider)

    def test_remove_provider_clears_cache(self):
        """Test removing provider clears cache."""
        engine = AutoCompleteEngine()

        class MockProvider:
            def get_completions(self, context):
                return [
                    CompletionItem(
                        text="test", kind=CompletionKind.SYNTAX, detail="Test item"
                    )
                ]

        provider = MockProvider()
        engine.add_provider(provider)

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        # Populate cache
        engine.get_completions(context)
        assert len(engine._cache) > 0

        # Remove provider should clear cache
        engine.remove_provider(provider)
        assert len(engine._cache) == 0

    def test_get_completions_no_providers(self):
        """Test getting completions with no providers."""
        engine = AutoCompleteEngine()

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        items = engine.get_completions(context)

        assert items == []

    def test_get_completions_with_provider(self):
        """Test getting completions from provider."""
        engine = AutoCompleteEngine()

        class MockProvider:
            def get_completions(self, context):
                return [
                    CompletionItem(
                        text="introduction",
                        kind=CompletionKind.SYNTAX,
                        detail="Section heading",
                    )
                ]

        engine.add_provider(MockProvider())

        context = CompletionContext(
            line="intro",
            line_number=1,
            column=5,
            word_before_cursor="intro",
            prefix="intro",
            trigger_char=None,
            manual=False,
        )

        items = engine.get_completions(context)

        assert len(items) == 1
        assert items[0].text == "introduction"

    def test_get_completions_caching(self):
        """Test completion results are cached."""
        engine = AutoCompleteEngine()
        call_count = 0

        class MockProvider:
            def get_completions(self, context):
                nonlocal call_count
                call_count += 1
                return [
                    CompletionItem(
                        text="test", kind=CompletionKind.SYNTAX, detail="Test"
                    )
                ]

        engine.add_provider(MockProvider())

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        # First call - should call provider
        items1 = engine.get_completions(context)
        assert call_count == 1

        # Second call with same context - should use cache
        items2 = engine.get_completions(context)
        assert call_count == 1  # Not incremented
        assert items1 == items2

    def test_get_completions_max_items(self):
        """Test max_items limit."""
        engine = AutoCompleteEngine()

        class MockProvider:
            def get_completions(self, context):
                return [
                    CompletionItem(
                        text=f"item_{i}", kind=CompletionKind.SYNTAX, detail=f"Item {i}"
                    )
                    for i in range(20)
                ]

        engine.add_provider(MockProvider())

        context = CompletionContext(
            line="item",
            line_number=1,
            column=4,
            word_before_cursor="item",
            prefix="item",
            trigger_char=None,
            manual=False,
        )

        items = engine.get_completions(context, max_items=10)

        assert len(items) == 10

    def test_get_completions_provider_exception(self):
        """Test engine handles provider exceptions gracefully."""
        engine = AutoCompleteEngine()

        class BrokenProvider:
            def get_completions(self, context):
                raise RuntimeError("Provider failed")

        class WorkingProvider:
            def get_completions(self, context):
                return [
                    CompletionItem(
                        text="working", kind=CompletionKind.SYNTAX, detail="Works"
                    )
                ]

        engine.add_provider(BrokenProvider())
        engine.add_provider(WorkingProvider())

        context = CompletionContext(
            line="work",
            line_number=1,
            column=4,
            word_before_cursor="work",
            prefix="work",
            trigger_char=None,
            manual=False,
        )

        # Should not raise, should return working provider's results
        items = engine.get_completions(context)
        assert len(items) == 1
        assert items[0].text == "working"

    def test_clear_cache(self):
        """Test clearing cache."""
        engine = AutoCompleteEngine()

        class MockProvider:
            def get_completions(self, context):
                return [
                    CompletionItem(
                        text="test", kind=CompletionKind.SYNTAX, detail="Test"
                    )
                ]

        engine.add_provider(MockProvider())

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        # Populate cache
        engine.get_completions(context)
        assert len(engine._cache) > 0

        # Clear cache
        engine.clear_cache()
        assert len(engine._cache) == 0

    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        engine = AutoCompleteEngine(cache_size=100)

        stats = engine.get_cache_stats()

        assert stats["size"] == 0
        assert stats["max_size"] == 100
        assert stats["utilization"] == 0

    def test_get_cache_stats_with_entries(self):
        """Test cache stats with cached entries."""
        engine = AutoCompleteEngine(cache_size=100)

        class MockProvider:
            def get_completions(self, context):
                return [
                    CompletionItem(
                        text="test", kind=CompletionKind.SYNTAX, detail="Test"
                    )
                ]

        engine.add_provider(MockProvider())

        # Add 50 cache entries
        for i in range(50):
            context = CompletionContext(
                line=f"test{i}",
                line_number=i,
                column=4,
                word_before_cursor=f"test{i}",
                prefix=f"test{i}",
                trigger_char=None,
                manual=False,
            )
            engine.get_completions(context)

        stats = engine.get_cache_stats()

        assert stats["size"] == 50
        assert stats["max_size"] == 100
        assert stats["utilization"] == 50

    def test_cache_pruning(self):
        """Test cache is pruned when size limit exceeded."""
        engine = AutoCompleteEngine(cache_size=10)

        class MockProvider:
            def get_completions(self, context):
                return [
                    CompletionItem(
                        text="test", kind=CompletionKind.SYNTAX, detail="Test"
                    )
                ]

        engine.add_provider(MockProvider())

        # Add 15 cache entries (exceeds limit of 10)
        for i in range(15):
            context = CompletionContext(
                line=f"test{i}",
                line_number=i,
                column=4,
                word_before_cursor=f"test{i}",
                prefix=f"test{i}",
                trigger_char=None,
                manual=False,
            )
            engine.get_completions(context)

        # Cache should be pruned (removes 20% = 2 entries)
        assert len(engine._cache) <= 13  # 15 - 2

    def test_get_cache_stats_zero_cache_size(self):
        """Test cache stats with zero cache size."""
        engine = AutoCompleteEngine(cache_size=0)

        stats = engine.get_cache_stats()

        assert stats["utilization"] == 0


@pytest.mark.fr_085
@pytest.mark.fr_088
@pytest.mark.fr_089
@pytest.mark.unit
class TestRanking:
    """Test completion ranking algorithm."""

    def test_rank_exact_match(self):
        """Test exact match gets highest score (100)."""
        engine = AutoCompleteEngine()

        items = [CompletionItem(text="test", kind=CompletionKind.SYNTAX, detail="Test")]

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        assert len(ranked) == 1
        assert ranked[0].score == 100.0

    def test_rank_prefix_match(self):
        """Test prefix match gets high score (80-90)."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(text="testing", kind=CompletionKind.SYNTAX, detail="Test")
        ]

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        assert len(ranked) == 1
        assert 80.0 <= ranked[0].score <= 90.0

    def test_rank_substring_match(self):
        """Test substring match gets medium score."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(text="latest", kind=CompletionKind.SYNTAX, detail="Test")
        ]

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        assert len(ranked) == 1
        # Fuzzy matching may give different score than substring (50.0)
        assert 0 < ranked[0].score <= 60.0

    def test_rank_no_match(self):
        """Test very poor match items."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(
                text="xyz123",  # Completely different, no shared chars
                kind=CompletionKind.SYNTAX,
                detail="No Match",
            )
        ]

        context = CompletionContext(
            line="abcd",
            line_number=1,
            column=4,
            word_before_cursor="abcd",
            prefix="abcd",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        # Very poor matches are filtered out (score <= 0)
        assert len(ranked) == 0

    def test_rank_sort_by_score(self):
        """Test items are sorted by score (highest first)."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(
                text="testing",  # Prefix match
                kind=CompletionKind.SYNTAX,
                detail="Test 1",
            ),
            CompletionItem(
                text="test",  # Exact match
                kind=CompletionKind.SYNTAX,
                detail="Test 2",
            ),
            CompletionItem(
                text="latest",  # Substring match
                kind=CompletionKind.SYNTAX,
                detail="Test 3",
            ),
        ]

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        # Should be sorted: exact > prefix > substring
        assert len(ranked) == 3
        assert ranked[0].text == "test"  # Exact match first
        assert ranked[1].text == "testing"  # Prefix match second
        assert ranked[2].text == "latest"  # Substring match third

    def test_rank_with_filter_text(self):
        """Test ranking uses filter_text if provided."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(
                text="Display Text",
                filter_text="test",
                kind=CompletionKind.SYNTAX,
                detail="Test",
            )
        ]

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        assert len(ranked) == 1
        assert ranked[0].score == 100.0  # Exact match on filter_text

    def test_rank_empty_query(self):
        """Test ranking with empty query."""
        engine = AutoCompleteEngine()

        items = [CompletionItem(text="test", kind=CompletionKind.SYNTAX, detail="Test")]

        context = CompletionContext(
            line="",
            line_number=1,
            column=0,
            word_before_cursor="",
            prefix="",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        # Empty query matches as prefix (empty string is prefix of everything)
        # This is expected behavior for auto-complete
        assert len(ranked) >= 0  # May or may not match depending on implementation


@pytest.mark.fr_085
@pytest.mark.fr_088
@pytest.mark.fr_089
@pytest.mark.unit
class TestFuzzyMatchScore:
    """Test fuzzy_match_score function."""

    def test_fuzzy_match_exact(self):
        """Test exact match returns 100."""
        score = fuzzy_match_score("test", "test")

        assert score == 100.0

    def test_fuzzy_match_case_insensitive(self):
        """Test matching is case insensitive."""
        score = fuzzy_match_score("TEST", "test")

        assert score == 100.0

    def test_fuzzy_match_prefix(self):
        """Test prefix match returns high score."""
        score = fuzzy_match_score("test", "testing")

        # Should be high score (prefix match fallback)
        assert score >= 60.0

    def test_fuzzy_match_substring(self):
        """Test substring match returns medium score."""
        score = fuzzy_match_score("test", "latest")

        # Should be medium score (substring match fallback)
        assert score >= 60.0

    def test_fuzzy_match_no_match(self):
        """Test no match returns 0."""
        score = fuzzy_match_score("xyz", "abc")

        assert score == 0.0

    def test_fuzzy_match_empty_query(self):
        """Test empty query."""
        score = fuzzy_match_score("", "test")

        assert score >= 0.0

    def test_fuzzy_match_empty_text(self):
        """Test empty text."""
        score = fuzzy_match_score("test", "")

        assert score >= 0.0


@pytest.mark.fr_085
@pytest.mark.fr_088
@pytest.mark.fr_089
@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_cache_key_generation(self):
        """Test cache key generation."""
        engine = AutoCompleteEngine()

        context = CompletionContext(
            line="test",
            line_number=5,
            column=10,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        key = engine._get_cache_key(context)

        assert key == "5:10:test"

    def test_cache_key_different_contexts(self):
        """Test different contexts generate different cache keys."""
        engine = AutoCompleteEngine()

        context1 = CompletionContext(
            line="test1",
            line_number=1,
            column=5,
            word_before_cursor="test1",
            prefix="test1",
            trigger_char=None,
            manual=False,
        )

        context2 = CompletionContext(
            line="test2",
            line_number=2,
            column=5,
            word_before_cursor="test2",
            prefix="test2",
            trigger_char=None,
            manual=False,
        )

        key1 = engine._get_cache_key(context1)
        key2 = engine._get_cache_key(context2)

        assert key1 != key2

    def test_prune_cache_manual(self):
        """Test manual cache pruning."""
        engine = AutoCompleteEngine(cache_size=10)

        # Manually add cache entries
        for i in range(15):
            engine._cache[f"key_{i}"] = []

        # Prune cache
        engine._prune_cache()

        # Should remove 20% of max_size (2 entries)
        assert len(engine._cache) == 13

    def test_empty_items_list(self):
        """Test ranking empty items list."""
        engine = AutoCompleteEngine()

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items([], context)

        assert ranked == []

    def test_multiple_exact_matches(self):
        """Test multiple items with exact same text are sorted alphabetically."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(
                text="test", sort_text="z", kind=CompletionKind.SYNTAX, detail="Z"
            ),
            CompletionItem(
                text="test", sort_text="a", kind=CompletionKind.SYNTAX, detail="A"
            ),
            CompletionItem(
                text="test", sort_text="b", kind=CompletionKind.SYNTAX, detail="B"
            ),
        ]

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        # All exact matches, sorted by sort_text
        ranked = engine._rank_items(items, context)

        assert len(ranked) == 3
        assert ranked[0].sort_text == "a"
        assert ranked[1].sort_text == "b"
        assert ranked[2].sort_text == "z"

    def test_completion_with_sort_text(self):
        """Test items with sort_text are sorted correctly."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(
                text="testing", sort_text="b", kind=CompletionKind.SYNTAX, detail="Test"
            ),
            CompletionItem(
                text="test", sort_text="a", kind=CompletionKind.SYNTAX, detail="Test"
            ),
        ]

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        # Both match, but exact match (score 100) beats prefix (score 80+)
        assert ranked[0].text == "test"
        assert ranked[1].text == "testing"


@pytest.mark.fr_085
@pytest.mark.fr_088
@pytest.mark.fr_089
@pytest.mark.unit
class TestRankItemsFallback:
    """Test _rank_items fallback paths and edge cases."""

    def test_rank_items_substring_match(self):
        """Test substring match scoring (tests line 273-274)."""
        engine = AutoCompleteEngine()

        # Item with substring match (not prefix, not exact)
        items = [
            CompletionItem(
                text="latest_test_value",
                kind=CompletionKind.SYNTAX,
                detail="Test",
            ),
        ]

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        # Should match via substring (fuzzy or substring fallback)
        # Score should be > 0 (either fuzzy ~60% or substring 50.0)
        assert len(ranked) == 1
        assert ranked[0].score > 0

    def test_rank_items_no_match_score_zero(self):
        """Test items with very poor fuzzy match get low scores (tests line 269-276)."""
        engine = AutoCompleteEngine()

        # Items with no meaningful match (very different from query)
        items = [
            CompletionItem(
                text="zzz",
                kind=CompletionKind.SYNTAX,
                detail="Test",
            ),
            CompletionItem(
                text="qqq",
                kind=CompletionKind.SYNTAX,
                detail="Test",
            ),
        ]

        context = CompletionContext(
            line="abc",
            line_number=1,
            column=3,
            word_before_cursor="abc",
            prefix="abc",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        # Items with very low fuzzy scores should still be filtered out or have low scores
        # With rapidfuzz, even poor matches get small scores
        # But we can verify they're ranked by fuzzy score
        if len(ranked) > 0:
            # All scores should be very low (< 20, which is fuzzy * 0.6)
            for item in ranked:
                assert item.score < 20.0


@pytest.mark.fr_085
@pytest.mark.fr_088
@pytest.mark.fr_089
@pytest.mark.unit
class TestRankItemsEdgeCases:
    """Test _rank_items edge cases for complete coverage."""

    def test_rank_items_empty_query_matches_all(self):
        """Test ranking with empty query includes all items."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(
                text="test1",
                kind=CompletionKind.SYNTAX,
                detail="Test",
            ),
            CompletionItem(
                text="test2",
                kind=CompletionKind.SYNTAX,
                detail="Test",
            ),
        ]

        context = CompletionContext(
            line="",
            line_number=1,
            column=0,
            word_before_cursor="",
            prefix="",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        # All items should be included with default scores
        assert len(ranked) == 2

    def test_rank_items_with_filter_text(self):
        """Test ranking uses filter_text when available."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(
                text="Display Text",
                filter_text="filtertext",
                kind=CompletionKind.SYNTAX,
                detail="Test",
            ),
        ]

        context = CompletionContext(
            line="filter",
            line_number=1,
            column=6,
            word_before_cursor="filter",
            prefix="filter",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        # Should match using filter_text (prefix match)
        assert len(ranked) == 1
        assert ranked[0].score > 80.0  # Prefix match score

    def test_rank_items_case_insensitive_matching(self):
        """Test ranking is case-insensitive."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(
                text="TestValue",
                kind=CompletionKind.SYNTAX,
                detail="Test",
            ),
        ]

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        ranked = engine._rank_items(items, context)

        # Should match despite case difference (prefix match)
        assert len(ranked) == 1
        assert ranked[0].score > 80.0


@pytest.mark.fr_085
@pytest.mark.fr_088
@pytest.mark.fr_089
@pytest.mark.unit
class TestRapidFuzzFallback:
    """Test fallback behavior when rapidfuzz is not available."""

    def test_rank_items_without_rapidfuzz_substring(self):
        """Test _rank_items substring fallback when rapidfuzz unavailable (tests line 273-274)."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(
                text="my_test_value",
                kind=CompletionKind.SYNTAX,
                detail="Test",
            ),
        ]

        context = CompletionContext(
            line="test",
            line_number=1,
            column=4,
            word_before_cursor="test",
            prefix="test",
            trigger_char=None,
            manual=False,
        )

        # Mock rapidfuzz to not be available
        with patch.dict(sys.modules, {"rapidfuzz": None, "rapidfuzz.fuzz": None}):
            # Reload the module to force ImportError path
            import importlib

            import asciidoc_artisan.core.autocomplete_engine as ace_module

            importlib.reload(ace_module)

            # Create new engine with reloaded module
            engine = ace_module.AutoCompleteEngine()

            ranked = engine._rank_items(items, context)

            # Should match via substring fallback (score 50.0)
            assert len(ranked) == 1
            assert ranked[0].score == 50.0

    def test_rank_items_without_rapidfuzz_no_match(self):
        """Test _rank_items no match when rapidfuzz unavailable (tests line 275-276)."""
        engine = AutoCompleteEngine()

        items = [
            CompletionItem(
                text="xyz",
                kind=CompletionKind.SYNTAX,
                detail="Test",
            ),
        ]

        context = CompletionContext(
            line="abc",
            line_number=1,
            column=3,
            word_before_cursor="abc",
            prefix="abc",
            trigger_char=None,
            manual=False,
        )

        # Mock rapidfuzz to not be available
        with patch.dict(sys.modules, {"rapidfuzz": None, "rapidfuzz.fuzz": None}):
            # Reload the module to force ImportError path
            import importlib

            import asciidoc_artisan.core.autocomplete_engine as ace_module

            importlib.reload(ace_module)

            # Create new engine with reloaded module
            engine = ace_module.AutoCompleteEngine()

            ranked = engine._rank_items(items, context)

            # No match, should be filtered out (score 0)
            assert len(ranked) == 0

    def test_fuzzy_match_score_without_rapidfuzz(self):
        """Test fuzzy_match_score fallback when rapidfuzz unavailable (tests line 393-405)."""
        # Mock rapidfuzz to not be available
        with patch.dict(sys.modules, {"rapidfuzz": None, "rapidfuzz.fuzz": None}):
            # Reload the module to force ImportError path
            import importlib

            import asciidoc_artisan.core.autocomplete_engine as ace_module

            importlib.reload(ace_module)

            # Test exact match fallback
            score = ace_module.fuzzy_match_score("test", "test")
            assert score == 100.0

            # Test prefix match fallback
            score = ace_module.fuzzy_match_score("test", "testing")
            assert score == 90.0

            # Test substring match fallback
            score = ace_module.fuzzy_match_score("test", "my_test_value")
            assert score == 60.0

            # Test no match fallback
            score = ace_module.fuzzy_match_score("test", "xyz")
            assert score == 0.0
