"""
Performance Benchmark Suite - Test performance metrics and optimization.

This module provides comprehensive performance testing for AsciiDoc Artisan:
- Document rendering benchmarks (small, medium, large)
- Preview update latency measurements
- Resource monitor accuracy tests
- Adaptive debouncing validation
- Memory usage tracking

Phase 4 Testing (v1.1.0-beta):
Validates performance improvements from adaptive debouncing and resource monitoring.

Usage:
    pytest tests/test_performance.py -v
    pytest tests/test_performance.py::test_adaptive_debouncing -v
"""

import time

import pytest

from asciidoc_artisan.core import ResourceMonitor

# Sample documents of varying sizes for benchmarking
SMALL_DOC = """= Small Document

This is a small test document with minimal content.

== Section 1

Some basic text here.
"""

MEDIUM_DOC = """= Medium Document

This is a medium-sized document for testing.

== Introduction

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
""" + "\n\n".join(
    [f"=== Subsection {i}\n\nMore content here." for i in range(50)]
)

LARGE_DOC = """= Large Document

This is a large document for performance testing.

== Chapter 1
""" + "\n\n".join(
    [
        f"=== Section {i}\n\n"
        + "\n".join([f"Paragraph {j} with some content here." for j in range(50)])
        for i in range(200)
    ]
)


@pytest.mark.integration
class TestResourceMonitor:
    """Test ResourceMonitor functionality and performance."""

    def test_monitor_initialization(self):
        """Test ResourceMonitor initializes correctly."""
        monitor = ResourceMonitor()
        assert monitor is not None
        # is_available() returns True if psutil is installed
        assert isinstance(monitor.is_available(), bool)

    def test_document_metrics_small(self):
        """Test document metrics calculation for small document."""
        monitor = ResourceMonitor()
        metrics = monitor.get_document_metrics(SMALL_DOC)

        assert metrics.size_bytes > 0
        assert metrics.line_count > 0
        assert metrics.char_count == len(SMALL_DOC)
        assert metrics.is_large is False  # Small doc should not be classified as large

    def test_document_metrics_large(self):
        """Test document metrics calculation for large document."""
        monitor = ResourceMonitor()
        metrics = monitor.get_document_metrics(LARGE_DOC)

        assert metrics.size_bytes > 100_000  # Should be substantial size
        assert metrics.line_count > 5000  # Should exceed large line threshold
        assert metrics.is_large is True  # Should be classified as large

    def test_adaptive_debouncing_small_doc(self):
        """Test adaptive debouncing returns fast interval for small documents."""
        monitor = ResourceMonitor()
        debounce_ms = monitor.calculate_debounce_interval(SMALL_DOC)

        # Small documents should use minimum debounce (200ms)
        assert debounce_ms == monitor.MIN_DEBOUNCE_MS

    def test_adaptive_debouncing_medium_doc(self):
        """Test adaptive debouncing returns normal interval for medium documents."""
        monitor = ResourceMonitor()
        debounce_ms = monitor.calculate_debounce_interval(MEDIUM_DOC)

        # Medium documents should use normal or medium debounce
        assert debounce_ms in (
            monitor.NORMAL_DEBOUNCE_MS,
            monitor.MEDIUM_DEBOUNCE_MS,
        )

    def test_adaptive_debouncing_large_doc(self):
        """Test adaptive debouncing returns long interval for large documents."""
        monitor = ResourceMonitor()
        debounce_ms = monitor.calculate_debounce_interval(LARGE_DOC)

        # Large documents should use large debounce (750ms or 1000ms)
        assert debounce_ms >= monitor.LARGE_DEBOUNCE_MS

    def test_get_metrics_comprehensive(self):
        """Test comprehensive metrics gathering."""
        monitor = ResourceMonitor()
        metrics = monitor.get_metrics(MEDIUM_DOC)

        # Verify all metrics are present
        assert hasattr(metrics, "memory_used_mb")
        assert hasattr(metrics, "memory_percent")
        assert hasattr(metrics, "cpu_percent")
        assert hasattr(metrics, "document_size_bytes")
        assert hasattr(metrics, "document_line_count")
        assert hasattr(metrics, "recommended_debounce_ms")

        # Verify metric values are reasonable
        assert metrics.document_size_bytes > 0
        assert metrics.document_line_count > 0
        assert metrics.recommended_debounce_ms > 0

        # Memory/CPU may be 0 if psutil not available
        assert metrics.memory_used_mb >= 0.0
        assert metrics.memory_percent >= 0.0
        assert metrics.cpu_percent >= 0.0

    def test_platform_info(self):
        """Test platform information retrieval."""
        monitor = ResourceMonitor()
        info = monitor.get_platform_info()

        assert "system" in info
        assert "python_version" in info
        assert "psutil_available" in info
        assert len(info["system"]) > 0


@pytest.mark.integration
class TestPerformanceBenchmarks:
    """Performance benchmarking tests."""

    @pytest.mark.benchmark
    def test_resource_monitor_overhead(self):
        """Benchmark ResourceMonitor calculation overhead."""
        monitor = ResourceMonitor()

        # Measure time for 100 debounce calculations
        start = time.perf_counter()
        for _ in range(100):
            monitor.calculate_debounce_interval(MEDIUM_DOC)
        elapsed = time.perf_counter() - start

        # Should complete 100 calculations in < 100ms (avg < 1ms per call)
        assert elapsed < 0.1, f"ResourceMonitor too slow: {elapsed:.3f}s for 100 calls"

    @pytest.mark.benchmark
    def test_document_metrics_performance(self):
        """Benchmark document metrics calculation speed."""
        monitor = ResourceMonitor()

        # Measure time for 100 metric calculations
        start = time.perf_counter()
        for _ in range(100):
            monitor.get_document_metrics(LARGE_DOC)
        elapsed = time.perf_counter() - start

        # Should complete 100 calculations in < 200ms (avg < 2ms per call)
        assert elapsed < 0.2, f"Document metrics too slow: {elapsed:.3f}s for 100 calls"

    @pytest.mark.benchmark
    def test_comprehensive_metrics_performance(self):
        """Benchmark comprehensive metrics gathering speed."""
        monitor = ResourceMonitor()

        # Measure time for 50 comprehensive metric calculations
        start = time.perf_counter()
        for _ in range(50):
            monitor.get_metrics(MEDIUM_DOC)
        elapsed = time.perf_counter() - start

        # Should complete 50 calculations in < 10s (avg < 200ms per call)
        # Relaxed timing for CI/slow systems - includes psutil system calls
        assert (
            elapsed < 10.0
        ), f"Comprehensive metrics too slow: {elapsed:.3f}s for 50 calls"


@pytest.mark.integration
class TestDebounceIntervalAccuracy:
    """Test adaptive debounce interval calculation accuracy."""

    def test_empty_document(self):
        """Test debounce calculation for empty document."""
        monitor = ResourceMonitor()
        debounce_ms = monitor.calculate_debounce_interval("")

        # Empty doc should use minimum debounce
        assert debounce_ms == monitor.MIN_DEBOUNCE_MS

    def test_single_line_document(self):
        """Test debounce calculation for single line."""
        monitor = ResourceMonitor()
        debounce_ms = monitor.calculate_debounce_interval("= Title")

        # Single line should use minimum debounce
        assert debounce_ms == monitor.MIN_DEBOUNCE_MS

    def test_threshold_boundaries(self):
        """Test debounce calculation at size thresholds."""
        monitor = ResourceMonitor()

        # Just under small threshold (9 KB)
        small_text = "x" * 9_000
        assert (
            monitor.calculate_debounce_interval(small_text) == monitor.MIN_DEBOUNCE_MS
        )

        # Just over small threshold (11 KB)
        medium_text = "x" * 11_000
        assert (
            monitor.calculate_debounce_interval(medium_text)
            == monitor.NORMAL_DEBOUNCE_MS
        )

        # Just over large threshold (501 KB)
        large_text = "x" * 501_000
        assert (
            monitor.calculate_debounce_interval(large_text) >= monitor.LARGE_DEBOUNCE_MS
        )

    def test_debounce_consistency(self):
        """Test debounce calculation is consistent for same input."""
        monitor = ResourceMonitor()

        # Same input should always return same debounce interval
        interval1 = monitor.calculate_debounce_interval(MEDIUM_DOC)
        interval2 = monitor.calculate_debounce_interval(MEDIUM_DOC)
        interval3 = monitor.calculate_debounce_interval(MEDIUM_DOC)

        assert interval1 == interval2 == interval3


@pytest.mark.integration
class TestMemoryMonitoring:
    """Test memory usage monitoring capabilities."""

    def test_memory_usage_retrieval(self):
        """Test memory usage can be retrieved."""
        monitor = ResourceMonitor()
        mem_mb, mem_percent = monitor.get_memory_usage()

        # Values should be non-negative
        assert mem_mb >= 0.0
        assert mem_percent >= 0.0

        # If psutil available, memory should be positive
        if monitor.is_available():
            assert mem_mb > 0.0
            assert 0.0 <= mem_percent <= 100.0

    def test_cpu_usage_retrieval(self):
        """Test CPU usage can be retrieved."""
        monitor = ResourceMonitor()
        cpu_percent = monitor.get_cpu_usage()

        # CPU should be non-negative
        assert cpu_percent >= 0.0

        # If psutil available, CPU percentage should be reasonable
        if monitor.is_available():
            import psutil

            assert 0.0 <= cpu_percent <= 100.0 * psutil.cpu_count()


@pytest.mark.integration
class TestDocumentSizeClassification:
    """Test document size classification logic."""

    def test_classification_thresholds(self):
        """Test documents are classified correctly by size."""
        monitor = ResourceMonitor()

        # Test at each threshold
        test_cases = [
            ("", False),  # Empty
            ("x" * 5_000, False),  # 5KB - small
            ("x" * 50_000, False),  # 50KB - medium
            ("x" * 600_000, True),  # 600KB - large
        ]

        for text, expected_large in test_cases:
            metrics = monitor.get_document_metrics(text)
            assert (
                metrics.is_large == expected_large
            ), f"Failed for {len(text)} bytes: expected {expected_large}, got {metrics.is_large}"

    def test_line_count_classification(self):
        """Test documents are classified correctly by line count."""
        monitor = ResourceMonitor()

        # Create documents with specific line counts
        small_lines = "\n".join(["x"] * 50)  # 50 lines
        large_lines = "\n".join(["x"] * 6000)  # 6000 lines

        small_metrics = monitor.get_document_metrics(small_lines)
        large_metrics = monitor.get_document_metrics(large_lines)

        assert small_metrics.is_large is False
        assert large_metrics.is_large is True


# Performance regression tests
@pytest.mark.integration
class TestPerformanceRegression:
    """Test for performance regressions."""

    @pytest.mark.benchmark
    def test_no_regression_small_doc(self):
        """Ensure small document processing stays fast."""
        monitor = ResourceMonitor()

        start = time.perf_counter()
        for _ in range(1000):
            monitor.calculate_debounce_interval(SMALL_DOC)
        elapsed = time.perf_counter() - start

        # 1000 calls should complete in < 100ms
        assert elapsed < 0.1, f"Performance regression: {elapsed:.3f}s for 1000 calls"

    @pytest.mark.benchmark
    def test_no_regression_large_doc(self):
        """Ensure large document processing stays reasonable."""
        monitor = ResourceMonitor()

        start = time.perf_counter()
        for _ in range(100):
            monitor.calculate_debounce_interval(LARGE_DOC)
        elapsed = time.perf_counter() - start

        # 100 calls should complete in < 500ms
        assert elapsed < 0.5, f"Performance regression: {elapsed:.3f}s for 100 calls"
