"""
LRU Cache - Least Recently Used cache implementation.

This module provides a reusable LRU cache for memory-bounded caching
throughout the application.

Implements Phase 2.2 of Performance Optimization Plan:
- Bounded cache sizes
- Automatic eviction
- Cache statistics
- Memory-efficient storage

Features:
- Configurable size limit
- Automatic LRU eviction
- Hit/miss tracking
- Memory usage estimation
- Thread-safe operations
"""

import logging
from collections import OrderedDict
from typing import Any, TypeVar

logger = logging.getLogger(__name__)


K = TypeVar("K")  # Key type
V = TypeVar("V")  # Value type


class LRUCache[K, V]:
    """
    Least Recently Used (LRU) cache.

    Stores key-value pairs with automatic eviction of least recently
    used items when the cache size limit is reached.

    Example:
        # Create cache with max 100 items
        cache = LRUCache(max_size=100)

        # Add items
        cache.put('key1', 'value1')
        cache.put('key2', 'value2')

        # Get items (moves to end - most recent)
        value = cache.get('key1')  # Returns 'value1'

        # Check existence
        if 'key1' in cache:
            print("Key exists")

        # Get statistics
        stats = cache.get_stats()
        print(f"Hit rate: {stats['hit_rate']}%")

        # Clear cache
        cache.clear()
    """

    def __init__(self, max_size: int = 100, name: str = "LRUCache"):
        """
        Initialize LRU cache.

        Args:
            max_size: Maximum number of items
            name: Cache name for logging
        """
        if max_size <= 0:
            raise ValueError("max_size must be positive")

        self.max_size = max_size
        self.name = name
        self._cache: OrderedDict[K, V] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

        logger.debug(f"{self.name}: Initialized with max_size={max_size}")

    def get(self, key: K, default: V | None = None) -> V | None:
        """
        Get value from cache.

        Args:
            key: Key to lookup
            default: Default value if key not found

        Returns:
            Value if found, default otherwise
        """
        if key in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]

        self._misses += 1
        return default

    def put(self, key: K, value: V) -> None:
        """
        Put value in cache.

        Args:
            key: Key
            value: Value

        If cache is full, evicts least recently used item.
        """
        # If key exists, remove it (will re-add at end)
        if key in self._cache:
            del self._cache[key]

        # Add to end (most recently used)
        self._cache[key] = value

        # Evict oldest if over size limit
        while len(self._cache) > self.max_size:
            evicted_key, evicted_value = self._cache.popitem(last=False)
            self._evictions += 1
            logger.debug(f"{self.name}: Evicted {evicted_key} (size={len(self._cache)})")

    def delete(self, key: K) -> bool:
        """
        Delete key from cache.

        Args:
            key: Key to delete

        Returns:
            True if key was deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        size_before = len(self._cache)
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        logger.debug(f"{self.name}: Cleared {size_before} entries")

    def __contains__(self, key: K) -> bool:
        """Check if key exists in cache."""
        return key in self._cache

    def __len__(self) -> int:
        """Get number of items in cache."""
        return len(self._cache)

    def __getitem__(self, key: K) -> V:
        """Get item using bracket notation."""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key: K, value: V) -> None:
        """Set item using bracket notation."""
        self.put(key, value)

    def __delitem__(self, key: K) -> None:
        """Delete item using bracket notation."""
        if not self.delete(key):
            raise KeyError(key)

    def keys(self) -> Any:  # OrderedDict keys view
        """Get cache keys."""
        return self._cache.keys()

    def values(self) -> Any:  # OrderedDict values view
        """Get cache values."""
        return self._cache.values()

    def items(self) -> Any:  # OrderedDict items view
        """Get cache items."""
        return self._cache.items()

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        return {
            "name": self.name,
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": round(hit_rate, 2),
            "fill_rate": round(len(self._cache) / self.max_size * 100, 2),
        }

    def resize(self, new_max_size: int) -> None:
        """
        Resize cache.

        Args:
            new_max_size: New maximum size

        If new size is smaller, evicts oldest items.
        """
        if new_max_size <= 0:
            raise ValueError("new_max_size must be positive")

        old_size = self.max_size
        self.max_size = new_max_size

        # Evict oldest items if needed
        while len(self._cache) > self.max_size:
            evicted_key, _ = self._cache.popitem(last=False)
            self._evictions += 1

        logger.debug(f"{self.name}: Resized from {old_size} to {new_max_size} (current size={len(self._cache)})")


class SizeAwareLRUCache(LRUCache[K, V]):
    """
    LRU cache with size/memory awareness.

    Similar to LRUCache but also tracks total size of cached items,
    useful for caching strings or objects where memory usage matters.

    Example:
        # Create cache with max 1MB total size
        cache = SizeAwareLRUCache(
            max_size=100,
            max_total_size=1024 * 1024
        )

        # Add items (automatically tracks size)
        cache.put('key1', 'small value')
        cache.put('key2', 'x' * 1000000)  # 1MB value

        # Get memory usage
        stats = cache.get_stats()
        print(f"Memory used: {stats['total_size']} bytes")
    """

    def __init__(
        self,
        max_size: int = 100,
        max_total_size: int | None = None,
        name: str = "SizeAwareLRUCache",
    ):
        """
        Initialize size-aware LRU cache.

        Args:
            max_size: Maximum number of items
            max_total_size: Maximum total size in bytes (None = no limit)
            name: Cache name
        """
        super().__init__(max_size, name)
        self.max_total_size = max_total_size
        self._item_sizes: OrderedDict[K, int] = OrderedDict()
        self._total_size = 0

    def put(self, key: K, value: V, size: int | None = None) -> None:
        """
        Put value in cache.

        Args:
            key: Key
            value: Value
            size: Size in bytes (auto-calculated if None)

        Evicts items to make room if needed.
        """
        # Calculate size if not provided
        if size is None:
            try:
                # Try to get size for common types
                if isinstance(value, str):
                    size = len(value.encode("utf-8"))
                elif isinstance(value, bytes):
                    size = len(value)
                elif isinstance(value, (int, float, bool)):
                    size = 8  # Approximate
                else:
                    size = 100  # Default estimate
            except Exception:
                size = 100  # Fallback

        # If key exists, remove old size
        if key in self._cache:
            old_size = self._item_sizes.get(key, 0)
            self._total_size -= old_size
            del self._cache[key]
            del self._item_sizes[key]

        # Evict items if needed to make room
        # (either by count or by total size)
        while len(self._cache) >= self.max_size or (
            self.max_total_size and self._total_size + size > self.max_total_size
        ):
            if len(self._cache) == 0:
                break

            evicted_key, _ = self._cache.popitem(last=False)
            evicted_size = self._item_sizes.pop(evicted_key, 0)
            self._total_size -= evicted_size
            self._evictions += 1

        # Add item
        self._cache[key] = value
        self._item_sizes[key] = size
        self._total_size += size

    def delete(self, key: K) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            size = self._item_sizes.pop(key, 0)
            self._total_size -= size
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        super().clear()
        self._item_sizes.clear()
        self._total_size = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics including size info."""
        stats = super().get_stats()
        stats["total_size"] = self._total_size
        stats["max_total_size"] = self.max_total_size

        if self.max_total_size:
            stats["size_fill_rate"] = round(self._total_size / self.max_total_size * 100, 2)
        else:
            stats["size_fill_rate"] = 0

        return stats
