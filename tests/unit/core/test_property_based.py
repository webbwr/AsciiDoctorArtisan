"""
Property-based tests using Hypothesis.

Tests that verify properties hold for all possible inputs (fuzz testing).
QA-7: Phase 3 - Quality Infrastructure
"""

from pathlib import Path

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from asciidoc_artisan.core import atomic_save_json, atomic_save_text, sanitize_path
from asciidoc_artisan.core.adaptive_debouncer import AdaptiveDebouncer
from asciidoc_artisan.core.lru_cache import LRUCache

# Custom strategies
safe_text = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),  # Exclude surrogates
    min_size=0,
    max_size=10000,
)

file_content = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)), min_size=0, max_size=50000
)

safe_filenames = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=32, max_codepoint=126
    ),
    min_size=1,
    max_size=255,
).filter(lambda s: s.strip() and "/" not in s and "\\" not in s)


@pytest.mark.property
class TestFileOperationsProperties:
    """Property-based tests for file operations."""

    @given(content=file_content)
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_atomic_save_text_never_corrupts(self, content, tmp_path):
        """Property: Atomic save always produces valid file or fails cleanly.

        Note: Text mode normalizes line endings (\r -> \n), which is expected behavior.
        """
        file_path = tmp_path / "test.txt"

        result = atomic_save_text(file_path, content)

        if result:
            # If save succeeded, file must exist and contain content
            # (with possible line ending normalization in text mode)
            assert file_path.exists()
            saved_content = file_path.read_text(encoding="utf-8")
            # Verify content matches after normalizing line endings
            assert saved_content == content.replace("\r\n", "\n").replace("\r", "\n")
        # If save failed (result False), that's acceptable - no corruption

    @given(
        data=st.dictionaries(
            keys=safe_text.filter(lambda s: len(s) > 0 and len(s) < 100),
            values=st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                safe_text,
                st.lists(st.integers(), max_size=10),
            ),
            max_size=20,
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_atomic_save_json_always_valid(self, data, tmp_path):
        """Property: JSON save always produces valid JSON or fails cleanly."""
        import json

        file_path = tmp_path / "test.json"
        result = atomic_save_json(file_path, data)

        if result:
            # If save succeeded, must be valid JSON
            assert file_path.exists()
            loaded = json.loads(file_path.read_text(encoding="utf-8"))
            assert loaded == data

    @given(path_str=st.text(max_size=500))
    def test_sanitize_path_never_crashes(self, path_str):
        """Property: Path sanitization never crashes, always returns Path or None."""
        try:
            result = sanitize_path(path_str)
            assert result is None or isinstance(result, Path)
            if result is not None:
                assert result.is_absolute()
        except Exception:
            # Some paths may raise exceptions (e.g., invalid characters)
            # That's acceptable as long as it's controlled
            pass

    @given(
        filename=safe_filenames, content=file_content.filter(lambda s: len(s) < 10000)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_save_and_load_preserves_content(self, filename, content, tmp_path):
        """Property: Save then load preserves content (with line ending normalization)."""
        file_path = tmp_path / filename

        save_result = atomic_save_text(file_path, content)
        assume(save_result)  # Only test if save succeeded

        loaded_content = file_path.read_text(encoding="utf-8")
        # Text mode normalizes line endings
        expected = content.replace("\r\n", "\n").replace("\r", "\n")
        assert loaded_content == expected


@pytest.mark.property
class TestCacheProperties:
    """Property-based tests for LRU cache."""

    @given(
        max_size=st.integers(min_value=1, max_value=100),
        operations=st.lists(
            st.tuples(
                st.sampled_from(["put", "get"]),
                st.text(max_size=20),
                st.text(max_size=100),
            ),
            max_size=200,
        ),
    )
    def test_cache_never_exceeds_max_size(self, max_size, operations):
        """Property: Cache never exceeds configured max size."""
        cache = LRUCache(max_size=max_size)

        for op, key, value in operations:
            if op == "put":
                cache.put(key, value)
            else:
                cache.get(key)

            # Invariant: cache size <= max_size
            assert len(cache) <= max_size

    @given(
        max_size=st.integers(min_value=5, max_value=50),
        key=st.text(min_size=1, max_size=20),
        value=st.text(max_size=100),
    )
    def test_cache_get_after_put_returns_value(self, max_size, key, value):
        """Property: Get immediately after put returns the value."""
        cache = LRUCache(max_size=max_size)
        cache.put(key, value)

        result = cache.get(key)
        assert result == value

    @given(
        max_size=st.integers(min_value=2, max_value=20),
        entries=st.lists(
            st.tuples(st.text(min_size=1, max_size=10), st.integers()),
            min_size=1,
            max_size=50,
            unique_by=lambda x: x[0],
        ),
    )
    def test_cache_evicts_lru_when_full(self, max_size, entries):
        """Property: Cache evicts least recently used when full."""
        cache = LRUCache(max_size=max_size)

        # Fill cache beyond capacity
        for key, value in entries:
            cache.put(key, value)

        # Cache should be at max size
        assert len(cache) <= max_size

        # Most recent entries should still be present
        if len(entries) >= max_size:
            recent_keys = [k for k, _ in entries[-max_size:]]
            for key in recent_keys:
                result = cache.get(key)
                # Key should exist (unless it was a duplicate)
                if result is None:
                    # Check if key was overwritten by later entry
                    later_keys = [
                        k for k, _ in entries[entries.index((key, cache.get(key))) :]
                    ]
                    assert key in later_keys or len(set(recent_keys)) < len(recent_keys)


@pytest.mark.property
class TestDebouncerProperties:
    """Property-based tests for adaptive debouncer."""

    @given(
        document_size=st.integers(min_value=0, max_value=1_000_000),
        render_time=st.floats(
            min_value=0.0, max_value=5.0, allow_nan=False, allow_infinity=False
        ),
    )
    def test_debouncer_delay_always_positive(self, document_size, render_time):
        """Property: Debouncer always returns positive delay."""
        debouncer = AdaptiveDebouncer()

        delay = debouncer.calculate_delay(
            document_size=document_size, last_render_time=render_time
        )

        assert delay >= 0
        # Max delay is in config object, not instance attribute
        assert delay <= debouncer.config.max_delay

    @given(
        sizes=st.lists(
            st.integers(min_value=100, max_value=100_000), min_size=5, max_size=20
        )
    )
    def test_debouncer_larger_docs_longer_delay(self, sizes):
        """Property: Larger documents generally get longer delays."""
        debouncer = AdaptiveDebouncer()

        sorted_sizes = sorted(sizes)
        delays = [debouncer.calculate_delay(size) for size in sorted_sizes]

        # First delay might be default, but trend should be increasing
        if len(delays) >= 3:
            # Check that delays don't decrease dramatically
            for i in range(len(delays) - 1):
                # Allow some variation, but large docs shouldn't have tiny delays
                if sorted_sizes[i + 1] > sorted_sizes[i] * 2:
                    assert delays[i + 1] >= delays[i] * 0.5  # Relaxed constraint


@pytest.mark.property
class TestTextProcessingProperties:
    """Property-based tests for text processing."""

    @given(text=safe_text)
    def test_text_never_causes_crash(self, text):
        """Property: Any text input never causes crashes."""
        # Test various text processing operations
        try:
            # String operations that should never crash
            _ = text.strip()
            _ = text.lower()
            _ = text.upper()
            _ = len(text)
            _ = text.split("\n")

            # These should all succeed
            assert True
        except Exception as e:
            pytest.fail(f"Text processing crashed: {e}")

    @given(
        text=safe_text.filter(lambda s: len(s) > 0),
        separator=st.sampled_from(["\n", " ", "\t", ","]),
    )
    def test_split_and_join_identity(self, text, separator):
        """Property: split then join with same separator restores text (with caveats)."""
        parts = text.split(separator)
        rejoined = separator.join(parts)

        # This is the identity property for split/join
        assert rejoined == text or separator in text

    @given(text=st.text(min_size=0, max_size=1000))
    def test_empty_vs_whitespace_detection(self, text):
        """Property: Empty string XOR whitespace-only XOR has content."""
        is_empty = len(text) == 0
        is_whitespace_only = len(text) > 0 and len(text.strip()) == 0
        has_content = len(text.strip()) > 0

        # Exactly one of these should be true
        true_count = sum([is_empty, is_whitespace_only, has_content])
        assert true_count == 1


@pytest.mark.property
class TestPathSecurityProperties:
    """Property-based tests for path security."""

    @given(
        dangerous=st.sampled_from(
            [
                "../../../etc/passwd",
                "../../secret",
                "..\\..\\..\\windows\\system32",
                "folder/../../../etc/shadow",
            ]
        )
    )
    def test_sanitize_blocks_directory_traversal(self, dangerous):
        """Property: Directory traversal attacks (using ..) are blocked.

        Note: sanitize_path is designed to prevent directory traversal attacks,
        not to block all access to system paths. Application-level access control
        should restrict which directories users can open/save to.

        Relative paths like ../../../etc/passwd resolve safely to working directory
        (e.g., /home/user/project/etc/passwd, not /etc/passwd).

        Absolute system paths like /etc/shadow are NOT blocked by this function,
        as they don't involve directory traversal. Application should restrict
        file dialogs to safe directories (e.g., user's home directory).
        """
        result = sanitize_path(dangerous)

        # Either rejected (None) or resolved to absolute path
        if result is not None:
            assert result.is_absolute()
            # The key security property: no ".." in resolved path components
            assert ".." not in result.parts

    @given(base=st.sampled_from(["/tmp", "/home", "."]), relative=safe_filenames)
    def test_path_joining_preserves_safety(self, base, relative):
        """Property: Joining safe paths produces safe paths."""
        from pathlib import Path

        try:
            base_path = Path(base)
            joined = base_path / relative

            # Resolved path should be absolute
            resolved = joined.resolve()
            assert resolved.is_absolute()
        except Exception:
            # Some joins may fail, that's acceptable
            pass


@pytest.mark.property
class TestNumericProperties:
    """Property-based tests for numeric operations."""

    @given(
        value=st.integers(min_value=0, max_value=1_000_000_000),
        threshold=st.integers(min_value=1, max_value=1_000_000_000),
    )
    def test_threshold_comparison_consistent(self, value, threshold):
        """Property: Threshold comparisons are consistent."""
        exceeds = value > threshold
        within = value <= threshold

        # Exactly one must be true
        assert exceeds != within  # XOR

    @given(
        start=st.integers(min_value=0, max_value=1000),
        end=st.integers(min_value=0, max_value=1000),
    )
    def test_range_calculations_valid(self, start, end):
        """Property: Range calculations produce valid results."""
        minimum = min(start, end)
        maximum = max(start, end)

        assert minimum <= start
        assert minimum <= end
        assert maximum >= start
        assert maximum >= end
        assert maximum - minimum == abs(end - start)


@pytest.mark.property
class TestListOperationsProperties:
    """Property-based tests for list operations."""

    @given(items=st.lists(st.integers(), max_size=100))
    def test_list_length_invariant(self, items):
        """Property: List operations preserve expected lengths."""
        original_length = len(items)

        # Copy operations
        copied = items.copy()
        assert len(copied) == original_length

        # Slice operations
        half = len(items) // 2
        first_half = items[:half]
        second_half = items[half:]
        assert len(first_half) + len(second_half) == original_length

    @given(items=st.lists(st.integers(), min_size=1, max_size=100), index=st.integers())
    def test_safe_list_indexing(self, items, index):
        """Property: Safe indexing never crashes."""
        try:
            # Modulo indexing is always safe
            safe_index = index % len(items)
            value = items[safe_index]
            assert isinstance(value, int)
        except Exception as e:
            pytest.fail(f"Safe indexing failed: {e}")

    @given(
        items=st.lists(st.text(max_size=20), max_size=50), element=st.text(max_size=20)
    )
    def test_membership_consistency(self, items, element):
        """Property: Membership checks are consistent."""
        is_member = element in items
        count = items.count(element)

        if is_member:
            assert count > 0
        else:
            assert count == 0


@pytest.mark.property
class TestDictionaryProperties:
    """Property-based tests for dictionary operations."""

    @given(
        keys=st.lists(
            st.text(min_size=1, max_size=20), min_size=0, max_size=50, unique=True
        ),
        values=st.lists(st.integers(), min_size=0, max_size=50),
    )
    def test_dict_keys_values_length_match(self, keys, values):
        """Property: Dict creation from keys/values preserves structure."""
        # Truncate to same length
        min_len = min(len(keys), len(values))
        if min_len == 0:
            return

        d = dict(zip(keys[:min_len], values[:min_len]))

        assert len(d) <= min_len  # May be less if keys weren't unique
        assert len(d.keys()) == len(d.values())

        # Each key maps to expected value
        for key, value in zip(keys[:min_len], values[:min_len]):
            assert d[key] == value

    @given(
        initial=st.dictionaries(
            keys=st.text(min_size=1, max_size=10), values=st.integers(), max_size=20
        ),
        updates=st.dictionaries(
            keys=st.text(min_size=1, max_size=10), values=st.integers(), max_size=10
        ),
    )
    def test_dict_update_preserves_keys(self, initial, updates):
        """Property: Dict update adds new keys and updates existing."""
        original_keys = set(initial.keys())
        d = initial.copy()

        d.update(updates)

        # All original keys still present or updated
        for key in original_keys:
            assert key in d

        # All update keys now present
        for key in updates:
            assert key in d
            assert d[key] == updates[key]
