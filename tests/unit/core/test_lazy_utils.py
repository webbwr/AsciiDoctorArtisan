"""
Tests for lazy loading utilities.

Tests lazy property, lazy imports, and deferred initialization.
"""

import time

import pytest

from asciidoc_artisan.core.lazy_utils import (
    LazyImport,
    LazyInitializer,
    cached_property,
    lazy_property,
)


class TestLazyProperty:
    """Test lazy_property decorator."""

    def test_lazy_computation(self):
        """Test property is computed lazily."""
        call_count = 0

        class MyClass:
            @lazy_property
            def expensive(self):
                nonlocal call_count
                call_count += 1
                return "computed"

        obj = MyClass()

        # Not computed yet
        assert call_count == 0

        # First access computes
        result = obj.expensive
        assert result == "computed"
        assert call_count == 1

        # Second access uses cache
        result = obj.expensive
        assert result == "computed"
        assert call_count == 1  # Not called again

    def test_lazy_property_per_instance(self):
        """Test each instance has own cache."""

        class MyClass:
            def __init__(self, value):
                self.value = value

            @lazy_property
            def doubled(self):
                return self.value * 2

        obj1 = MyClass(5)
        obj2 = MyClass(10)

        assert obj1.doubled == 10
        assert obj2.doubled == 20

    def test_lazy_property_delete(self):
        """Test deleting cached value."""
        call_count = 0

        class MyClass:
            @lazy_property
            def data(self):
                nonlocal call_count
                call_count += 1
                return f"call_{call_count}"

        obj = MyClass()

        result1 = obj.data
        assert result1 == "call_1"
        assert call_count == 1

        # Delete cache
        del obj.data

        # Next access recomputes
        result2 = obj.data
        assert result2 == "call_2"
        assert call_count == 2

    def test_lazy_property_set(self):
        """Test manually setting property value."""

        class MyClass:
            @lazy_property
            def value(self):
                return "computed"

        obj = MyClass()

        # Set manually
        obj.value = "manual"

        # Returns manual value
        assert obj.value == "manual"


class TestLazyImport:
    """Test LazyImport."""

    def test_deferred_import(self):
        """Test module import is deferred."""
        # Create lazy import (shouldn't import yet)
        lazy_os = LazyImport("os")

        # Module not imported yet
        assert lazy_os._module is None

        # First use triggers import
        result = lazy_os.path.exists("/")

        # Module now imported
        assert lazy_os._module is not None
        assert result is True

    def test_multiple_access(self):
        """Test multiple accesses use same module."""
        lazy_os = LazyImport("os")

        # Multiple accesses
        lazy_os.path.exists("/")
        lazy_os.path.isdir("/")
        lazy_os.getcwd()

        # Module imported only once
        assert lazy_os._module is not None

    def test_nonexistent_module(self):
        """Test error on nonexistent module."""
        lazy_bad = LazyImport("nonexistent_module_xyz")

        with pytest.raises(ModuleNotFoundError):
            lazy_bad.some_function()


class TestLazyInitializer:
    """Test LazyInitializer."""

    def test_register_and_initialize(self):
        """Test registering and initializing components."""
        initialized = []

        def init_component_a():
            initialized.append("a")

        def init_component_b():
            initialized.append("b")

        initializer = LazyInitializer()
        initializer.register("a", init_component_a)
        initializer.register("b", init_component_b)

        # Nothing initialized yet
        assert len(initialized) == 0

        # Initialize component a
        initializer.initialize("a")
        assert initialized == ["a"]

        # Initialize component b
        initializer.initialize("b")
        assert initialized == ["a", "b"]

    def test_initialize_only_once(self):
        """Test component only initialized once."""
        call_count = 0

        def init_component():
            nonlocal call_count
            call_count += 1

        initializer = LazyInitializer()
        initializer.register("test", init_component)

        # Initialize multiple times
        initializer.initialize("test")
        initializer.initialize("test")
        initializer.initialize("test")

        # Only called once
        assert call_count == 1

    def test_initialize_remaining(self):
        """Test initializing all remaining components."""
        initialized = []

        initializer = LazyInitializer()
        initializer.register("a", lambda: initialized.append("a"))
        initializer.register("b", lambda: initialized.append("b"))
        initializer.register("c", lambda: initialized.append("c"))

        # Initialize one manually
        initializer.initialize("a")
        assert initialized == ["a"]

        # Initialize remaining
        initializer.initialize_remaining()
        assert set(initialized) == {"a", "b", "c"}

    def test_is_initialized(self):
        """Test checking initialization status."""
        initializer = LazyInitializer()
        initializer.register("test", lambda: None)

        assert initializer.is_initialized("test") is False

        initializer.initialize("test")

        assert initializer.is_initialized("test") is True

    def test_get_statistics(self):
        """Test getting statistics."""
        initializer = LazyInitializer()
        initializer.register("a", lambda: None)
        initializer.register("b", lambda: None)
        initializer.register("c", lambda: None)

        initializer.initialize("a")

        stats = initializer.get_statistics()

        assert stats["total"] == 3
        assert stats["initialized"] == 1
        assert stats["pending"] == 2
        assert stats["components"]["a"] is True
        assert stats["components"]["b"] is False
        assert stats["components"]["c"] is False

    def test_initialize_nonexistent(self):
        """Test error on nonexistent component."""
        initializer = LazyInitializer()

        with pytest.raises(ValueError):
            initializer.initialize("nonexistent")


class TestCachedProperty:
    """Test cached_property decorator."""

    def test_cached_computation(self):
        """Test property is computed once and cached."""
        call_count = 0

        class MyClass:
            @cached_property
            def expensive(self):
                nonlocal call_count
                call_count += 1
                return "computed"

        obj = MyClass()

        # First access
        result = obj.expensive
        assert result == "computed"
        assert call_count == 1

        # Second access (cached)
        result = obj.expensive
        assert result == "computed"
        assert call_count == 1

    def test_cached_property_per_instance(self):
        """Test each instance has own cache."""

        class MyClass:
            def __init__(self, value):
                self.value = value

            @cached_property
            def doubled(self):
                return self.value * 2

        obj1 = MyClass(5)
        obj2 = MyClass(10)

        assert obj1.doubled == 10
        assert obj2.doubled == 20


class TestMemoryEfficiency:
    """Test memory efficiency of lazy loading."""

    def test_lazy_property_memory(self):
        """Test lazy property reduces initial memory."""

        class HeavyClass:
            @lazy_property
            def heavy_data(self):
                # Simulate heavy data
                return list(range(10000))

        # Create many instances
        objects = [HeavyClass() for _ in range(100)]

        # Heavy data not allocated yet
        # (In real app, this would show significant memory savings)

        # Access first object's data
        data = objects[0].heavy_data

        assert len(data) == 10000

    def test_deferred_initialization_order(self):
        """Test deferred initialization controls order."""
        order = []

        class Application:
            def __init__(self):
                self.initializer = LazyInitializer()

                # Register in one order
                self.initializer.register("slow", lambda: order.append("slow"))
                self.initializer.register("fast", lambda: order.append("fast"))
                self.initializer.register("medium", lambda: order.append("medium"))

            def initialize_critical_first(self):
                # Initialize in priority order
                self.initializer.initialize("fast")
                self.initializer.initialize("medium")
                self.initializer.initialize("slow")

        app = Application()
        app.initialize_critical_first()

        # Order controlled by initialization calls
        assert order == ["fast", "medium", "slow"]


@pytest.mark.performance
class TestLazyLoadingPerformance:
    """Test performance benefits of lazy loading."""

    def test_startup_time_reduction(self):
        """Test lazy loading reduces startup time."""

        class EagerApp:
            def __init__(self):
                self.data1 = self._load_data()
                self.data2 = self._load_data()
                self.data3 = self._load_data()

            def _load_data(self):
                time.sleep(0.01)  # Simulate slow loading
                return list(range(1000))

        class LazyApp:
            def __init__(self):
                pass  # Nothing loaded

            @lazy_property
            def data1(self):
                time.sleep(0.01)
                return list(range(1000))

            @lazy_property
            def data2(self):
                time.sleep(0.01)
                return list(range(1000))

            @lazy_property
            def data3(self):
                time.sleep(0.01)
                return list(range(1000))

        # Measure eager loading
        start = time.time()
        eager = EagerApp()
        eager_time = time.time() - start

        # Measure lazy loading (just creation)
        start = time.time()
        lazy = LazyApp()
        lazy_time = time.time() - start

        # Lazy should be much faster to create
        assert lazy_time < eager_time / 10

        # But data available when needed
        lazy.data1
        lazy.data2
        lazy.data3

    def test_lazy_import_performance(self):
        """Test lazy import reduces startup overhead."""
        # Lazy import (creation only)
        start = time.time()
        lazy_os = LazyImport("os")
        lazy_sys = LazyImport("sys")
        lazy_pathlib = LazyImport("pathlib")
        lazy_time = time.time() - start

        # Lazy creation should be extremely fast (< 50 microseconds)
        # No actual import happens until attribute access
        # Relaxed threshold to accommodate varying system loads
        assert (
            lazy_time < 0.00005
        ), f"LazyImport creation took {lazy_time * 1000000:.2f}µs (expected < 50µs)"
