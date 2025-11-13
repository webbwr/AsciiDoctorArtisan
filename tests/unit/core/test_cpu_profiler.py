"""
Tests for CPU Profiler - Runtime CPU profiling.

Tests the CPU profiling system for performance analysis:
- Context manager for profiling code blocks
- cProfile integration
- Hotspot detection
- Statistics collection
- Report generation

QA-15: CPU Profiling Integration
"""

import time

from asciidoc_artisan.core.cpu_profiler import (
    CPUProfiler,
    ProfileResult,
    disable_cpu_profiling,
    enable_cpu_profiling,
    get_cpu_profiler,
)


class TestCPUProfiler:
    """Test CPU profiler functionality."""

    def test_profiler_initialization(self):
        """Test CPU profiler initializes correctly."""
        profiler = CPUProfiler(enabled=True)

        assert profiler.enabled is True
        assert profiler.max_results == 100
        assert len(profiler._results) == 0

    def test_profiler_disabled_no_op(self):
        """Test disabled profiler is no-op."""
        profiler = CPUProfiler(enabled=False)

        with profiler.profile("test_op"):
            time.sleep(0.01)

        # Should not have any results
        assert len(profiler._results) == 0

    def test_profile_context_manager(self):
        """Test profiling with context manager."""
        profiler = CPUProfiler(enabled=True)

        def expensive_operation():
            # Simulate some work
            total = 0
            for i in range(10000):
                total += i * i
            return total

        with profiler.profile("expensive_op"):
            expensive_operation()

        # Should have results
        assert "expensive_op" in profiler._results
        results = profiler._results["expensive_op"]
        assert len(results) == 1

        result = results[0]
        assert result.name == "expensive_op"
        assert result.total_time > 0
        assert result.call_count == 1
        assert len(result.hotspots) > 0  # Should detect some hotspots

    def test_multiple_profiles(self):
        """Test multiple profiling sessions."""
        profiler = CPUProfiler(enabled=True)

        for i in range(5):
            with profiler.profile("repeated_op"):
                time.sleep(0.001)

        results = profiler._results["repeated_op"]
        assert len(results) == 5

    def test_get_results(self):
        """Test getting profile results."""
        profiler = CPUProfiler(enabled=True)

        with profiler.profile("test_op"):
            time.sleep(0.001)

        results = profiler.get_results("test_op")
        assert len(results) == 1
        assert results[0].name == "test_op"

        # Non-existent operation
        empty = profiler.get_results("nonexistent")
        assert len(empty) == 0

    def test_get_hotspots(self):
        """Test getting hotspots."""
        profiler = CPUProfiler(enabled=True)

        def work_function():
            # Create some CPU-intensive work
            result = 0
            for i in range(10000):
                result += i**2
            return result

        with profiler.profile("work_op"):
            work_function()

        hotspots = profiler.get_hotspots("work_op", limit=3)
        assert len(hotspots) <= 3

        # Each hotspot should have required fields
        if hotspots:
            hotspot = hotspots[0]
            assert "function" in hotspot
            assert "cumtime" in hotspot
            assert "ncalls" in hotspot

    def test_get_statistics(self):
        """Test getting aggregated statistics."""
        profiler = CPUProfiler(enabled=True)

        # Profile multiple times
        for i in range(3):
            with profiler.profile("stat_op"):
                time.sleep(0.001)

        stats = profiler.get_statistics("stat_op")

        assert stats is not None
        assert stats["operation"] == "stat_op"
        assert stats["total_calls"] == 3
        assert stats["num_profiles"] == 3
        assert stats["avg_time"] > 0
        assert stats["total_time"] > 0

        # Non-existent operation
        assert profiler.get_statistics("nonexistent") is None

    def test_get_report(self):
        """Test generating comprehensive report."""
        profiler = CPUProfiler(enabled=True)

        with profiler.profile("op1"):
            time.sleep(0.001)

        with profiler.profile("op2"):
            time.sleep(0.001)

        report = profiler.get_report()

        assert "operations" in report
        assert "summary" in report
        assert "op1" in report["operations"]
        assert "op2" in report["operations"]

        # Check summary
        assert report["summary"]["total_operations"] == 2
        assert report["summary"]["total_profiles"] == 2
        assert report["summary"]["total_time"] > 0

    def test_reset(self):
        """Test resetting profiler."""
        profiler = CPUProfiler(enabled=True)

        with profiler.profile("test_op"):
            time.sleep(0.001)

        assert len(profiler._results) > 0

        profiler.reset()

        assert len(profiler._results) == 0
        assert len(profiler._profilers) == 0
        assert len(profiler._active_profiles) == 0

    def test_is_profiling(self):
        """Test checking if operation is being profiled."""
        profiler = CPUProfiler(enabled=True)

        assert not profiler.is_profiling("test_op")

        # Note: This is tricky because we're inside the context manager
        # Just verify the method exists and works
        with profiler.profile("test_op"):
            pass  # Can't check inside context due to cleanup

        # After context exits, should not be profiling
        assert not profiler.is_profiling("test_op")

    def test_max_results_limit(self):
        """Test max results limiting."""
        profiler = CPUProfiler(enabled=True, max_results=5)

        # Profile more than max
        for i in range(10):
            with profiler.profile("limited_op"):
                pass

        results = profiler._results["limited_op"]
        assert len(results) <= 5  # Should be limited

    def test_hotspot_parsing(self):
        """Test hotspot parsing from cProfile output."""
        profiler = CPUProfiler(enabled=True)

        # Simple operation to generate hotspots
        def nested_work():
            def inner1():
                return sum(range(1000))

            def inner2():
                return sum(range(1000))

            return inner1() + inner2()

        with profiler.profile("nested_op"):
            nested_work()

        hotspots = profiler.get_hotspots("nested_op")

        # Should have detected some hotspots
        assert len(hotspots) > 0

        # Verify hotspot structure
        for hotspot in hotspots:
            assert isinstance(hotspot, dict)
            assert "function" in hotspot
            assert "cumtime" in hotspot
            assert "ncalls" in hotspot
            assert isinstance(hotspot["cumtime"], float)
            assert isinstance(hotspot["ncalls"], int)


class TestCPUProfilerGlobalInstance:
    """Test global CPU profiler singleton."""

    def test_get_cpu_profiler_singleton(self):
        """Test get_cpu_profiler returns singleton."""
        profiler1 = get_cpu_profiler()
        profiler2 = get_cpu_profiler()

        assert profiler1 is profiler2  # Same instance

    def test_enable_disable_cpu_profiling(self):
        """Test enabling/disabling global CPU profiling."""
        profiler = get_cpu_profiler()

        # Initially disabled by default
        assert profiler.enabled is False

        enable_cpu_profiling()
        assert profiler.enabled is True

        disable_cpu_profiling()
        assert profiler.enabled is False


class TestProfileResult:
    """Test ProfileResult dataclass."""

    def test_profile_result_creation(self):
        """Test creating ProfileResult."""
        result = ProfileResult(
            name="test_op", total_time=1.5, call_count=10, hotspots=[]
        )

        assert result.name == "test_op"
        assert result.total_time == 1.5
        assert result.call_count == 10
        assert result.hotspots == []
        assert result.timestamp > 0  # Auto-generated

    def test_profile_result_with_hotspots(self):
        """Test ProfileResult with hotspots."""
        hotspots = [
            {"function": "foo", "cumtime": 1.0, "ncalls": 5},
            {"function": "bar", "cumtime": 0.5, "ncalls": 3},
        ]

        result = ProfileResult(
            name="op", total_time=2.0, call_count=1, hotspots=hotspots
        )

        assert len(result.hotspots) == 2
        assert result.hotspots[0]["function"] == "foo"


class TestCoverageImprovements:
    """Tests to achieve 100% coverage."""

    def test_parse_hotspots_with_malformed_stats(self):
        """Test _parse_hotspots handles malformed stats gracefully (lines 205-206)."""
        profiler = CPUProfiler(enabled=True)

        # Create malformed stats output that will trigger ValueError/IndexError
        malformed_stats = """
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        5    invalid  0.000    0.001  0.000 test.py:1(func1)
        not_a_number  0.001  0.000  0.001  0.000 test.py:2(func2)
        10  0.001  0.000  BAD  0.000 test.py:3(func3)
        short_line
        """

        # This should not raise exception - malformed lines should be skipped
        hotspots = profiler._parse_hotspots(malformed_stats)

        # Should return empty list or skip malformed entries
        # The continue on lines 205-206 handles these cases
        assert isinstance(hotspots, list)

    def test_get_hotspots_with_no_results(self):
        """Test get_hotspots returns empty list when no results exist (line 235)."""
        profiler = CPUProfiler(enabled=True)

        # Call get_hotspots for non-existent operation
        # This should hit line 235: return []
        hotspots = profiler.get_hotspots("nonexistent_operation", limit=5)

        assert hotspots == []
        assert len(hotspots) == 0


class TestCPUProfilerIntegration:
    """Integration tests for CPU profiler."""

    def test_profile_realistic_operation(self):
        """Test profiling a realistic operation."""
        profiler = CPUProfiler(enabled=True)

        def process_data(data):
            # Simulate data processing
            result = []
            for item in data:
                # Some calculations
                value = item**2 + item**3
                result.append(value)
            return result

        data = list(range(1000))

        with profiler.profile("process_data"):
            result = process_data(data)

        assert len(result) == 1000

        # Verify profiling captured data
        stats = profiler.get_statistics("process_data")
        assert stats is not None
        assert stats["total_calls"] == 1

        hotspots = profiler.get_hotspots("process_data", limit=5)
        assert len(hotspots) > 0

    def test_exception_handling(self):
        """Test profiler handles exceptions gracefully."""
        profiler = CPUProfiler(enabled=True)

        try:
            with profiler.profile("error_op"):
                raise ValueError("Test error")
        except ValueError:
            pass

        # Should still record profiling data despite exception
        results = profiler.get_results("error_op")
        assert len(results) == 1

    def test_zero_overhead_when_disabled(self):
        """Test zero overhead when profiling is disabled."""
        profiler = CPUProfiler(enabled=False)

        start = time.perf_counter()

        for i in range(1000):
            with profiler.profile("noop"):
                pass

        elapsed = time.perf_counter() - start

        # Should be very fast (< 10ms) since profiling is disabled
        assert elapsed < 0.01

        # No results should be recorded
        assert len(profiler._results) == 0
