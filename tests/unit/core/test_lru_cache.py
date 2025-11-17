"""
Tests for LRU cache implementations.

Tests basic LRU cache and size-aware variant.
"""

import pytest

from asciidoc_artisan.core.lru_cache import LRUCache, SizeAwareLRUCache


@pytest.mark.fr_084
@pytest.mark.unit
class TestLRUCache:
    """Test basic LRU cache."""

    def test_initialization(self):
        """Test cache initializes correctly."""
        cache = LRUCache(max_size=10)

        assert cache.max_size == 10
        assert len(cache) == 0

    def test_invalid_size(self):
        """Test error on invalid size."""
        with pytest.raises(ValueError):
            LRUCache(max_size=0)

        with pytest.raises(ValueError):
            LRUCache(max_size=-1)

    def test_put_and_get(self):
        """Test basic put and get."""
        cache = LRUCache(max_size=10)

        cache.put("key1", "value1")
        cache.put("key2", "value2")

        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") is None

    def test_get_with_default(self):
        """Test get with default value."""
        cache = LRUCache(max_size=10)

        assert cache.get("missing", "default") == "default"

    def test_lru_eviction(self):
        """Test LRU eviction when full."""
        cache = LRUCache(max_size=3)

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")

        # Cache full
        assert len(cache) == 3

        # Add one more - should evict key1 (oldest)
        cache.put("key4", "value4")

        assert len(cache) == 3
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_lru_access_updates_order(self):
        """Test that accessing an item updates LRU order."""
        cache = LRUCache(max_size=3)

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")

        # Access key1 (moves to end)
        cache.get("key1")

        # Add new item - should evict key2 (now oldest)
        cache.put("key4", "value4")

        assert cache.get("key1") == "value1"  # Still there
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_put_updates_existing_key(self):
        """Test that putting existing key updates value."""
        cache = LRUCache(max_size=10)

        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

        cache.put("key1", "value2")
        assert cache.get("key1") == "value2"

        # Should still be only 1 item
        assert len(cache) == 1

    def test_delete(self):
        """Test deleting items."""
        cache = LRUCache(max_size=10)

        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

        # Delete
        result = cache.delete("key1")
        assert result is True
        assert cache.get("key1") is None

        # Delete again
        result = cache.delete("key1")
        assert result is False

    def test_clear(self):
        """Test clearing cache."""
        cache = LRUCache(max_size=10)

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.get("key1")  # Hit

        assert len(cache) == 2

        cache.clear()

        assert len(cache) == 0

        # Stats are reset by clear()
        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0

        # Verify keys are gone
        assert "key1" not in cache
        assert "key2" not in cache

    def test_contains(self):
        """Test __contains__ (in operator)."""
        cache = LRUCache(max_size=10)

        cache.put("key1", "value1")

        assert "key1" in cache
        assert "key2" not in cache

    def test_bracket_notation(self):
        """Test bracket notation access."""
        cache = LRUCache(max_size=10)

        # Set with brackets
        cache["key1"] = "value1"

        # Get with brackets
        assert cache["key1"] == "value1"

        # Get missing key
        with pytest.raises(KeyError):
            _ = cache["missing"]

        # Delete with brackets
        del cache["key1"]
        assert "key1" not in cache

        # Delete missing key
        with pytest.raises(KeyError):
            del cache["missing"]

    def test_keys_values_items(self):
        """Test keys, values, items methods."""
        cache = LRUCache(max_size=10)

        cache.put("key1", "value1")
        cache.put("key2", "value2")

        assert set(cache.keys()) == {"key1", "key2"}
        assert set(cache.values()) == {"value1", "value2"}
        assert set(cache.items()) == {("key1", "value1"), ("key2", "value2")}

    def test_get_stats(self):
        """Test getting statistics."""
        cache = LRUCache(max_size=10, name="TestCache")

        cache.put("key1", "value1")
        cache.put("key2", "value2")

        # Hits
        cache.get("key1")
        cache.get("key2")

        # Misses
        cache.get("key3")
        cache.get("key4")

        stats = cache.get_stats()

        assert stats["name"] == "TestCache"
        assert stats["size"] == 2
        assert stats["max_size"] == 10
        assert stats["hits"] == 2
        assert stats["misses"] == 2
        assert stats["evictions"] == 0
        assert stats["hit_rate"] == 50.0
        assert stats["fill_rate"] == 20.0

    def test_eviction_count(self):
        """Test eviction counting."""
        cache = LRUCache(max_size=2)

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Evicts key1
        cache.put("key4", "value4")  # Evicts key2

        stats = cache.get_stats()
        assert stats["evictions"] == 2

    def test_resize(self):
        """Test resizing cache."""
        cache = LRUCache(max_size=5)

        # Fill cache
        for i in range(5):
            cache.put(f"key{i}", f"value{i}")

        assert len(cache) == 5

        # Resize smaller - should evict oldest
        cache.resize(3)

        assert cache.max_size == 3
        assert len(cache) == 3

        # key0 and key1 should be evicted (oldest)
        assert cache.get("key0") is None
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_resize_larger(self):
        """Test resizing cache larger."""
        cache = LRUCache(max_size=3)

        cache.put("key1", "value1")
        cache.put("key2", "value2")

        cache.resize(10)

        assert cache.max_size == 10
        assert len(cache) == 2

    def test_resize_invalid(self):
        """Test error on invalid resize."""
        cache = LRUCache(max_size=10)

        with pytest.raises(ValueError):
            cache.resize(0)

        with pytest.raises(ValueError):
            cache.resize(-5)


@pytest.mark.fr_084
@pytest.mark.unit
class TestSizeAwareLRUCache:
    """Test size-aware LRU cache."""

    def test_initialization(self):
        """Test initialization."""
        cache = SizeAwareLRUCache(max_size=10, max_total_size=1000)

        assert cache.max_size == 10
        assert cache.max_total_size == 1000
        assert cache._total_size == 0

    def test_put_with_explicit_size(self):
        """Test putting items with explicit size."""
        cache = SizeAwareLRUCache(max_size=10, max_total_size=100)

        cache.put("key1", "value1", size=10)
        cache.put("key2", "value2", size=20)

        assert len(cache) == 2
        assert cache._total_size == 30

    def test_put_with_auto_size_string(self):
        """Test auto-sizing for strings."""
        cache = SizeAwareLRUCache(max_size=10)

        cache.put("key1", "hello")  # Size auto-calculated

        stats = cache.get_stats()
        assert stats["total_size"] > 0

    def test_eviction_by_total_size(self):
        """Test eviction when total size limit reached."""
        cache = SizeAwareLRUCache(max_size=10, max_total_size=50)

        cache.put("key1", "value1", size=30)
        cache.put("key2", "value2", size=25)  # Should evict key1

        assert len(cache) == 1
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache._total_size == 25

    def test_eviction_by_count_and_size(self):
        """Test eviction by both count and size."""
        cache = SizeAwareLRUCache(max_size=3, max_total_size=100)

        cache.put("key1", "value1", size=20)
        cache.put("key2", "value2", size=20)
        cache.put("key3", "value3", size=20)

        # Full by count (3 items)
        assert len(cache) == 3
        assert cache._total_size == 60

        # Add item that exceeds count
        cache.put("key4", "value4", size=20)

        # Should evict by count
        assert len(cache) == 3

    def test_delete_updates_size(self):
        """Test delete updates total size."""
        cache = SizeAwareLRUCache(max_size=10)

        cache.put("key1", "value1", size=50)
        assert cache._total_size == 50

        cache.delete("key1")
        assert cache._total_size == 0

    def test_clear_resets_size(self):
        """Test clear resets total size."""
        cache = SizeAwareLRUCache(max_size=10)

        cache.put("key1", "value1", size=30)
        cache.put("key2", "value2", size=40)

        assert cache._total_size == 70

        cache.clear()

        assert cache._total_size == 0

    def test_get_stats_with_size(self):
        """Test statistics include size info."""
        cache = SizeAwareLRUCache(max_size=10, max_total_size=1000)

        cache.put("key1", "value1", size=300)
        cache.put("key2", "value2", size=200)

        stats = cache.get_stats()

        assert stats["total_size"] == 500
        assert stats["max_total_size"] == 1000
        assert stats["size_fill_rate"] == 50.0

    def test_no_max_total_size(self):
        """Test cache with no total size limit."""
        cache = SizeAwareLRUCache(max_size=3, max_total_size=None)

        # Add items with large sizes
        cache.put("key1", "value1", size=1000)
        cache.put("key2", "value2", size=2000)
        cache.put("key3", "value3", size=3000)

        # Should only evict by count, not size
        assert len(cache) == 3
        assert cache._total_size == 6000

        # Add one more - evicts oldest
        cache.put("key4", "value4", size=4000)

        assert len(cache) == 3
        assert cache._total_size == 9000  # Sum of key2, key3, key4

    def test_auto_size_bytes(self):
        """Test auto-size calculation for bytes type."""
        cache = SizeAwareLRUCache(max_size=10)

        # Test bytes type (line 293-294)
        cache.put("key1", b"hello world")
        assert cache._item_sizes["key1"] == 11  # len(b"hello world")

    def test_auto_size_numeric_types(self):
        """Test auto-size calculation for int, float, bool types."""
        cache = SizeAwareLRUCache(max_size=10)

        # Test int type (line 295-296)
        cache.put("key1", 42)
        assert cache._item_sizes["key1"] == 8

        # Test float type (line 295-296)
        cache.put("key2", 3.14)
        assert cache._item_sizes["key2"] == 8

        # Test bool type (line 295-296)
        cache.put("key3", True)
        assert cache._item_sizes["key3"] == 8

    def test_auto_size_fallback(self):
        """Test auto-size fallback for unknown types."""
        cache = SizeAwareLRUCache(max_size=10)

        # Test unknown type (line 297-298)
        cache.put("key1", {"complex": "object"})
        assert cache._item_sizes["key1"] == 100  # Default estimate

    def test_auto_size_exception_fallback(self):
        """Test exception fallback during size calculation (lines 299-300)."""
        cache = SizeAwareLRUCache(max_size=10)

        # Create a string subclass that raises exception on encode()
        class BadString(str):
            def encode(self, *args, **kwargs):
                raise RuntimeError("Cannot encode!")

        # This should trigger the exception handler fallback (lines 299-300)
        cache.put("key1", BadString("bad_value"))
        assert cache._item_sizes["key1"] == 100  # Fallback on exception

    def test_put_updates_existing_key(self):
        """Test put() updates size when key already exists (lines 304-307)."""
        cache = SizeAwareLRUCache(max_size=10)

        # Put initial value with size 50
        cache.put("key1", "old_value", size=50)
        assert cache._total_size == 50

        # Update same key with different size (lines 304-307)
        cache.put("key1", "new_value", size=75)
        assert cache._total_size == 75  # Old size removed, new size added
        assert cache.get("key1") == "new_value"

    def test_put_single_item_larger_than_max(self):
        """Test adding a single item larger than max_total_size (line 316)."""
        cache = SizeAwareLRUCache(max_size=10, max_total_size=100)

        # Try to add a single item larger than max_total_size
        # This triggers the break on line 316 when cache is empty
        # (prevents infinite eviction loop)
        cache.put("huge_key", "huge_value", size=200)

        # Item still gets added (break just prevents infinite loop)
        assert len(cache) == 1
        assert cache.get("huge_key") == "huge_value"
        assert cache._total_size == 200

    def test_delete_nonexistent_key(self):
        """Test delete() returns False for non-existent key (line 335)."""
        cache = SizeAwareLRUCache(max_size=10)

        cache.put("key1", "value1")

        # Delete existing key returns True
        assert cache.delete("key1") is True

        # Delete non-existent key returns False (line 335)
        assert cache.delete("key2") is False
        assert cache.delete("key1") is False  # Already deleted
