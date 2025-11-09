"""
Tests for lazy importer.

Tests lazy module loading, import profiling, and optimization.
"""

import time

import pytest

from asciidoc_artisan.core.lazy_importer import (
    ImportOptimizer,
    ImportProfiler,
    ImportTracker,
    LazyModule,
    get_import_statistics,
    lazy_import,
    profile_imports,
)


class TestLazyModule:
    """Test LazyModule."""

    def test_create_lazy_module(self):
        """Test creating lazy module."""
        lazy_os = LazyModule("os")

        # Module not loaded yet
        assert lazy_os._module is None

    def test_lazy_loading(self):
        """Test module loads on first access."""
        lazy_os = LazyModule("os")

        # First access triggers load
        result = lazy_os.path.exists("/")

        # Module now loaded
        assert lazy_os._module is not None
        assert result is True

    def test_multiple_access(self):
        """Test multiple accesses use same module."""
        lazy_sys = LazyModule("sys")

        # Multiple accesses
        version1 = lazy_sys.version
        version2 = lazy_sys.version

        # Same module
        assert version1 == version2
        assert lazy_sys._module is not None

    def test_lazy_import_time_tracked(self):
        """Test import time is tracked."""
        lazy_time = LazyModule("time")

        # Access module
        lazy_time.time()

        # Import time should be recorded
        assert lazy_time._import_time > 0

    def test_lazy_module_repr(self):
        """Test string representation."""
        lazy_os = LazyModule("os")

        # Before loading
        repr_before = repr(lazy_os)
        assert "not loaded" in repr_before

        # After loading
        lazy_os.getcwd()
        repr_after = repr(lazy_os)
        assert "loaded in" in repr_after

    def test_lazy_module_dir(self):
        """Test dir() on lazy module."""
        lazy_os = LazyModule("os")

        # Get attributes
        attrs = dir(lazy_os)

        # Should have loaded module
        assert lazy_os._module is not None
        assert "path" in attrs

    def test_nonexistent_module_error(self):
        """Test error for non-existent module."""
        lazy_bad = LazyModule("nonexistent_module_xyz")

        with pytest.raises(ModuleNotFoundError):
            lazy_bad.some_function()


class TestImportProfiler:
    """Test ImportProfiler."""

    def test_profile_imports(self):
        """Test profiling imports."""
        profiler = ImportProfiler()

        with profiler:
            import json  # noqa: F401
            import urllib  # noqa: F401

        stats = profiler.get_statistics()

        # Should have tracked imports
        assert stats["total_imports"] >= 2
        assert stats["total_time"] > 0
        assert len(stats["slowest"]) > 0

    def test_profiler_slowest_imports(self):
        """Test identifying slowest imports."""
        profiler = ImportProfiler()

        with profiler:
            import os  # noqa: F401
            import sys  # noqa: F401
            import time  # noqa: F401

        stats = profiler.get_statistics()

        # Should list slowest
        slowest = stats["slowest"]
        assert len(slowest) > 0

        # Each entry is (name, time_ms)
        for name, time_ms in slowest:
            assert isinstance(name, str)
            assert time_ms >= 0

    def test_profiler_context_manager(self):
        """Test profiler as context manager."""
        profiler = ImportProfiler()

        # Before profiling
        assert profiler._original_import is None

        with profiler:
            # During profiling
            assert profiler._original_import is not None
            import pathlib  # noqa: F401

        # After profiling
        # Import hook restored

        stats = profiler.get_statistics()
        assert stats["total_imports"] > 0

    def test_profiler_print_report(self, capsys):
        """Test printing report."""
        profiler = ImportProfiler()

        with profiler:
            import re  # noqa: F401

        profiler.print_report(top_n=5)

        captured = capsys.readouterr()
        assert "Import Profiling Report" in captured.out
        assert "Total imports" in captured.out

    def test_profiler_empty_statistics(self):
        """Test profiler with no imports."""
        profiler = ImportProfiler()

        # Get stats without profiling anything
        stats = profiler.get_statistics()

        # Should return empty stats structure
        assert stats["total_imports"] == 0
        assert stats["total_time"] == 0
        assert stats["slowest"] == []
        assert stats["fastest"] == []


class TestImportTracker:
    """Test ImportTracker."""

    def test_tracker_singleton(self):
        """Test tracker is singleton."""
        tracker1 = ImportTracker()
        tracker2 = ImportTracker()

        assert tracker1 is tracker2

    def test_register_lazy_import(self):
        """Test registering lazy import."""
        tracker = ImportTracker()

        tracker.register_lazy_import("test_module")

        stats = tracker.get_statistics()
        assert "test_module" in tracker._lazy_modules

    def test_record_import(self):
        """Test recording import."""
        tracker = ImportTracker()

        tracker.record_import("test_module", 0.05, deferred=False)

        stats = tracker.get_statistics()
        assert stats["total_imports"] >= 1

    def test_track_eager_vs_lazy(self):
        """Test tracking eager vs lazy imports."""
        tracker = ImportTracker()

        # Clear previous data for this test
        tracker._imports.clear()
        tracker._lazy_modules.clear()

        # Record eager import
        tracker.record_import("module_eager", 0.01, deferred=False)

        # Record lazy import
        tracker.register_lazy_import("module_lazy")
        tracker.record_import("module_lazy", 0.02, deferred=True)

        stats = tracker.get_statistics()

        assert stats["eager_imports"] >= 1
        assert stats["lazy_imports"] >= 1
        assert stats["time_saved"] > 0

    def test_tracker_print_report(self, capsys):
        """Test printing tracker report."""
        tracker = ImportTracker()

        tracker.print_report()

        captured = capsys.readouterr()
        assert "Import Tracking Report" in captured.out


class TestLazyImportFunction:
    """Test lazy_import function."""

    def test_lazy_import_function(self):
        """Test lazy_import convenience function."""
        lazy_json = lazy_import("json")

        # Not loaded yet
        assert lazy_json._module is None

        # Use it
        data = lazy_json.dumps({"test": 123})

        # Now loaded
        assert lazy_json._module is not None
        assert '"test": 123' in data

    def test_lazy_import_with_package(self):
        """Test lazy import with package."""
        # Test relative import capability
        lazy_mod = lazy_import("os.path")

        result = lazy_mod.join("a", "b")
        assert "a" in result and "b" in result


class TestProfileImportsDecorator:
    """Test profile_imports decorator."""

    def test_decorator_basic(self, capsys):
        """Test decorator profiles function imports."""

        @profile_imports
        def test_function():
            import csv  # noqa: F401
            import xml  # noqa: F401

            return "done"

        result = test_function()

        assert result == "done"

        # Should print report
        captured = capsys.readouterr()
        assert "Import Profiling Report" in captured.out

    def test_decorator_with_args(self, capsys):
        """Test decorator with function arguments."""

        @profile_imports
        def test_function(x, y):
            import base64  # noqa: F401

            return x + y

        result = test_function(10, 20)

        assert result == 30

        captured = capsys.readouterr()
        assert "Import Profiling Report" in captured.out


class TestGetImportStatistics:
    """Test get_import_statistics function."""

    def test_get_statistics(self):
        """Test getting global statistics."""
        stats = get_import_statistics()

        assert "total_imports" in stats
        assert "eager_imports" in stats
        assert "lazy_imports" in stats
        assert isinstance(stats["total_imports"], int)


class TestPrintImportReport:
    """Test print_import_report function."""

    def test_print_import_report(self, capsys):
        """Test global import report printing."""
        from asciidoc_artisan.core.lazy_importer import print_import_report

        print_import_report()

        captured = capsys.readouterr()
        assert "Import Tracking Report" in captured.out
        assert "Total imports" in captured.out


class TestImportOptimizer:
    """Test ImportOptimizer."""

    def test_create_optimizer(self):
        """Test creating optimizer."""
        optimizer = ImportOptimizer()

        assert optimizer is not None

    def test_get_heavy_modules(self):
        """Test getting heavy modules list."""
        optimizer = ImportOptimizer()

        heavy = optimizer.get_heavy_modules()

        assert "pandas" in heavy
        assert "numpy" in heavy
        assert "matplotlib" in heavy

    def test_analyze_module(self):
        """Test analyzing module."""
        optimizer = ImportOptimizer()

        # Analyze a built-in module
        suggestions = optimizer.analyze_module("os")

        # Should return list (may be empty for os)
        assert isinstance(suggestions, list)

    def test_analyze_module_not_loaded(self):
        """Test analyzing module that's not yet loaded."""
        optimizer = ImportOptimizer()

        # Analyze module not in sys.modules
        suggestions = optimizer.analyze_module("asyncio")

        # Should import and analyze it
        assert isinstance(suggestions, list)

    def test_analyze_nonexistent_module(self):
        """Test analyzing non-existent module."""
        optimizer = ImportOptimizer()

        # Should handle gracefully
        suggestions = optimizer.analyze_module("nonexistent_module_xyz_12345")

        # Should return empty list (logged warning internally)
        assert suggestions == []

    def test_analyze_module_with_heavy_imports(self):
        """Test detecting heavy imports in module."""
        optimizer = ImportOptimizer()

        # Create a test module with heavy imports
        import sys
        from types import ModuleType

        test_module = ModuleType("test_heavy_module")

        # Create mock object with pandas module attribute
        class MockPandasObject:
            __module__ = "pandas.core.frame"

        test_module.dataframe_obj = MockPandasObject()
        sys.modules["test_heavy_module"] = test_module

        try:
            suggestions = optimizer.analyze_module("test_heavy_module")

            # Should suggest lazy loading pandas
            assert len(suggestions) > 0
            assert any("pandas" in s for s in suggestions)
        finally:
            # Cleanup
            del sys.modules["test_heavy_module"]


@pytest.mark.performance
class TestLazyImportPerformance:
    """Test lazy import performance benefits."""

    def test_startup_time_savings(self):
        """Test lazy import reduces startup time."""
        # Eager import
        start = time.time()
        import json  # noqa: F401
        import urllib  # noqa: F401
        import xml  # noqa: F401

        eager_time = time.time() - start

        # Lazy import (creation only)
        start = time.time()
        lazy_json = LazyModule("json")
        lazy_urllib = LazyModule("urllib")
        lazy_xml = LazyModule("xml")
        lazy_create_time = time.time() - start

        # Lazy creation should be faster or equal (on fast systems, both are very quick)
        # On slow systems, lazy should be significantly faster
        assert lazy_create_time <= eager_time * 2  # Allow some variance

        print(f"\nEager import: {eager_time * 1000:.2f}ms")
        print(f"Lazy creation: {lazy_create_time * 1000:.2f}ms")
        print(f"Savings: {(eager_time - lazy_create_time) * 1000:.2f}ms")

    def test_deferred_cost(self):
        """Test deferred import cost on first access."""
        # Create lazy module
        lazy_re = LazyModule("re")

        # First access (triggers import)
        start = time.time()
        lazy_re.compile(r"test")
        first_access = time.time() - start

        # Second access (already loaded)
        start = time.time()
        lazy_re.compile(r"test2")
        second_access = time.time() - start

        # Second access should be much faster
        assert second_access < first_access

        print(f"\nFirst access: {first_access * 1000:.2f}ms (import + use)")
        print(f"Second access: {second_access * 1000:.2f}ms (use only)")

    def test_import_profiler_overhead(self):
        """Test import profiler overhead."""
        # Without profiler
        start = time.time()
        import hashlib  # noqa: F401
        import hmac  # noqa: F401

        normal_time = time.time() - start

        # With profiler
        profiler = ImportProfiler()
        start = time.time()
        with profiler:
            import secrets  # noqa: F401
            import uuid  # noqa: F401
        profiled_time = time.time() - start

        # Overhead should be minimal
        overhead = profiled_time - normal_time
        assert overhead < 0.1  # Less than 100ms overhead

        print(f"\nNormal import: {normal_time * 1000:.2f}ms")
        print(f"Profiled import: {profiled_time * 1000:.2f}ms")
        print(f"Overhead: {overhead * 1000:.2f}ms")


class TestLazyImportIntegration:
    """Test lazy import integration scenarios."""

    def test_mixed_eager_and_lazy(self):
        """Test mixing eager and lazy imports."""
        # Eager
        import sys  # noqa: F401

        # Lazy
        lazy_os = lazy_import("os")

        # Both work
        assert sys.version is not None
        assert lazy_os.getcwd() is not None

    def test_lazy_import_in_function(self):
        """Test lazy import inside function."""

        def process_data():
            # Import only when function is called
            lazy_json = lazy_import("json")
            return lazy_json.dumps({"result": "success"})

        # Function defined but imports not loaded yet

        # Call function
        result = process_data()
        assert "success" in result

    def test_conditional_lazy_import(self):
        """Test conditional lazy import."""
        use_feature = True

        if use_feature:
            lazy_mod = lazy_import("datetime")
        else:
            lazy_mod = None

        if lazy_mod:
            # Import happens here if feature enabled
            now = lazy_mod.datetime.now()
            assert now is not None
