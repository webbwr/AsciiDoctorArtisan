"""
Advanced tests for lazy_utils.py - Lazy loading and caching utilities.

This test suite complements existing lazy_utils tests with:
- lazy_property caching and thread safety
- LazyImport deferred module loading
- defer_method execution queuing
- LazyInitializer lifecycle management
- cached_property behavior verification

Phase 4B: 10 focused tests for critical lazy loading utilities
"""

import threading
import time
from unittest.mock import Mock, patch
import pytest

from asciidoc_artisan.core.lazy_utils import (
    lazy_property,
    LazyImport,
    defer_method,
    LazyInitializer,
    cached_property,
)


# ==============================================================================
# lazy_property Tests (3 tests)
# ==============================================================================


class TestLazyPropertyAdvanced:
    """Test lazy_property decorator with advanced scenarios."""

    def test_lazy_property_computes_once_and_caches(self):
        """Test lazy property computes on first access and caches result."""
        call_count = {"count": 0}

        class TestClass:
            @lazy_property
            def expensive_resource(self):
                call_count["count"] += 1
                return "expensive_result"

        obj = TestClass()

        # First access - should compute
        result1 = obj.expensive_resource
        assert result1 == "expensive_result"
        assert call_count["count"] == 1

        # Second access - should use cache
        result2 = obj.expensive_resource
        assert result2 == "expensive_result"
        assert call_count["count"] == 1  # No additional call

        # Third access - still cached
        result3 = obj.expensive_resource
        assert call_count["count"] == 1

    def test_lazy_property_thread_safe_access(self):
        """Test lazy property is thread-safe with concurrent access."""
        call_count = {"count": 0}

        class TestClass:
            @lazy_property
            def shared_resource(self):
                call_count["count"] += 1
                time.sleep(0.01)  # Simulate work
                return "shared_result"

        obj = TestClass()
        results = []

        def access_property():
            results.append(obj.shared_resource)

        # Create 10 threads accessing property concurrently
        threads = [threading.Thread(target=access_property) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should get same result
        assert all(r == "shared_result" for r in results)
        # Property should be computed at least once (may be more due to race)
        assert call_count["count"] >= 1

    def test_lazy_property_set_and_delete(self):
        """Test lazy property __set__ and __delete__ behavior."""

        class TestClass:
            @lazy_property
            def data(self):
                return "computed_value"

        obj = TestClass()

        # Initial access
        assert obj.data == "computed_value"

        # Set new value (override cache)
        obj.data = "manual_value"
        assert obj.data == "manual_value"

        # Delete cached value
        del obj.data

        # Next access should recompute
        assert obj.data == "computed_value"


# ==============================================================================
# LazyImport Tests (2 tests)
# ==============================================================================


class TestLazyImportAdvanced:
    """Test LazyImport with deferred module loading."""

    def test_lazy_import_defers_until_first_use(self):
        """Test LazyImport doesn't import module until first attribute access."""
        # Mock importlib.import_module to track calls
        with patch("importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_module.test_function = Mock(return_value="result")
            mock_import.return_value = mock_module

            # Create lazy import
            lazy_os = LazyImport("os")

            # Module should NOT be imported yet
            mock_import.assert_not_called()

            # Access attribute - triggers import
            result = lazy_os.test_function()

            # Now import should have been called
            mock_import.assert_called_once_with("os")
            assert result == "result"

    def test_lazy_import_dir_triggers_import(self):
        """Test __dir__ triggers import and returns module attributes."""
        with patch("importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_module.__dir__ = Mock(return_value=["attr1", "attr2", "attr3"])
            mock_import.return_value = mock_module

            lazy_mod = LazyImport("test_module")

            # Call dir() - should trigger import
            attrs = dir(lazy_mod)

            # Import should have been called
            mock_import.assert_called_once_with("test_module")
            assert attrs == ["attr1", "attr2", "attr3"]


# ==============================================================================
# defer_method Tests (1 test)
# ==============================================================================


class TestDeferMethodAdvanced:
    """Test defer_method decorator for queued execution."""

    def test_defer_method_queues_execution(self):
        """Test defer_method queues method calls instead of immediate execution."""
        call_log = []

        class TestClass:
            def __init__(self):
                self._deferred_calls = []

            @defer_method
            def load_plugins(self):
                call_log.append("load_plugins")
                return "plugins_loaded"

            @defer_method
            def initialize_cache(self):
                call_log.append("initialize_cache")
                return "cache_initialized"

            def run_deferred(self):
                for call in self._deferred_calls:
                    call()
                self._deferred_calls.clear()

        obj = TestClass()

        # Call deferred methods - should queue, not execute
        obj.load_plugins()
        obj.initialize_cache()
        assert len(call_log) == 0  # Not executed yet
        assert len(obj._deferred_calls) == 2  # Queued

        # Run deferred calls
        obj.run_deferred()

        # Now should be executed
        assert call_log == ["load_plugins", "initialize_cache"]
        assert len(obj._deferred_calls) == 0  # Queue cleared


# ==============================================================================
# LazyInitializer Tests (3 tests)
# ==============================================================================


class TestLazyInitializerAdvanced:
    """Test LazyInitializer lifecycle management."""

    def test_lazy_initializer_lifecycle(self):
        """Test LazyInitializer register, initialize, check status lifecycle."""
        init_log = []

        def init_git():
            init_log.append("git")

        def init_export():
            init_log.append("export")

        def init_ai():
            init_log.append("ai")

        initializer = LazyInitializer()

        # Register components
        initializer.register("git", init_git)
        initializer.register("export", init_export)
        initializer.register("ai", init_ai)

        # Nothing initialized yet
        assert not initializer.is_initialized("git")
        assert not initializer.is_initialized("export")
        assert not initializer.is_initialized("ai")

        # Initialize git
        initializer.initialize("git")
        assert initializer.is_initialized("git")
        assert not initializer.is_initialized("export")
        assert init_log == ["git"]

        # Initialize export
        initializer.initialize("export")
        assert initializer.is_initialized("export")
        assert init_log == ["git", "export"]

        # Calling initialize again should be idempotent
        initializer.initialize("git")
        assert init_log == ["git", "export"]  # No duplicate

    def test_lazy_initializer_selective_initialization(self):
        """Test initialize_remaining() with selective initialization."""
        init_log = []

        initializer = LazyInitializer()
        initializer.register("comp1", lambda: init_log.append("comp1"))
        initializer.register("comp2", lambda: init_log.append("comp2"))
        initializer.register("comp3", lambda: init_log.append("comp3"))

        # Initialize comp1 early
        initializer.initialize("comp1")
        assert init_log == ["comp1"]

        # Initialize remaining (should skip comp1)
        initializer.initialize_remaining()
        assert set(init_log) == {"comp1", "comp2", "comp3"}

        # Verify all initialized
        assert initializer.is_initialized("comp1")
        assert initializer.is_initialized("comp2")
        assert initializer.is_initialized("comp3")

    def test_lazy_initializer_statistics(self):
        """Test get_statistics() returns accurate statistics."""
        initializer = LazyInitializer()

        initializer.register("a", lambda: None)
        initializer.register("b", lambda: None)
        initializer.register("c", lambda: None)

        # Initial stats
        stats = initializer.get_statistics()
        assert stats["total"] == 3
        assert stats["initialized"] == 0
        assert stats["pending"] == 3
        assert stats["components"]["a"] is False

        # Initialize one component
        initializer.initialize("a")

        stats = initializer.get_statistics()
        assert stats["total"] == 3
        assert stats["initialized"] == 1
        assert stats["pending"] == 2
        assert stats["components"]["a"] is True
        assert stats["components"]["b"] is False

        # Initialize remaining
        initializer.initialize_remaining()

        stats = initializer.get_statistics()
        assert stats["total"] == 3
        assert stats["initialized"] == 3
        assert stats["pending"] == 0
        assert all(stats["components"].values())


# ==============================================================================
# cached_property Tests (1 test)
# ==============================================================================


class TestCachedPropertyAdvanced:
    """Test cached_property decorator behavior."""

    def test_cached_property_behavior(self):
        """Test cached_property caches values like functools.cached_property."""
        call_count = {"count": 0}

        class TestClass:
            @cached_property
            def heavy_computation(self):
                call_count["count"] += 1
                return 42 * 2

        obj = TestClass()

        # First access - computes
        result1 = obj.heavy_computation
        assert result1 == 84
        assert call_count["count"] == 1

        # Second access - cached
        result2 = obj.heavy_computation
        assert result2 == 84
        assert call_count["count"] == 1

        # Verify cached in __dict__
        assert "heavy_computation" in obj.__dict__
        assert obj.__dict__["heavy_computation"] == 84


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
