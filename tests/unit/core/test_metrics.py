"""Tests for metrics collection system."""

import pytest
import time
from asciidoc_artisan.core.metrics import (
    MetricsCollector,
    OperationMetrics,
    CacheMetrics,
    get_metrics_collector,
    measure_time,
)


def test_operation_metrics_record():
    """Test recording operation metrics."""
    metrics = OperationMetrics(operation_name="test_op")

    metrics.record(100.0)
    metrics.record(200.0)
    metrics.record(150.0)

    assert metrics.count == 3
    assert metrics.total_time_ms == 450.0
    assert metrics.min_time_ms == 100.0
    assert metrics.max_time_ms == 200.0
    assert metrics.get_average() == 150.0


def test_operation_metrics_percentiles():
    """Test percentile calculations."""
    metrics = OperationMetrics(operation_name="test_op")

    # Add 100 values from 1 to 100
    for i in range(1, 101):
        metrics.record(float(i))

    assert metrics.get_percentile(50) == pytest.approx(50.0, rel=5)
    assert metrics.get_percentile(95) == pytest.approx(95.0, rel=5)
    assert metrics.get_percentile(99) == pytest.approx(99.0, rel=5)


def test_operation_metrics_stats():
    """Test getting operation statistics."""
    metrics = OperationMetrics(operation_name="test_op")

    metrics.record(100.0)
    metrics.record(200.0)
    metrics.record(300.0)

    stats = metrics.get_stats()

    assert stats["count"] == 3
    assert stats["avg_ms"] == 200.0
    assert stats["min_ms"] == 100.0
    assert stats["max_ms"] == 300.0
    assert "p50_ms" in stats
    assert "p95_ms" in stats
    assert "p99_ms" in stats


def test_cache_metrics():
    """Test cache hit/miss tracking."""
    cache = CacheMetrics(cache_name="test_cache")

    cache.record_hit()
    cache.record_hit()
    cache.record_hit()
    cache.record_miss()

    assert cache.hits == 3
    assert cache.misses == 1
    assert cache.get_hit_rate() == 0.75


def test_cache_metrics_stats():
    """Test getting cache statistics."""
    cache = CacheMetrics(cache_name="test_cache")

    cache.record_hit()
    cache.record_hit()
    cache.record_miss()

    stats = cache.get_stats()

    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["total"] == 3
    assert stats["hit_rate"] == pytest.approx(0.666, rel=0.01)


def test_metrics_collector_record_operation():
    """Test recording operations in collector."""
    collector = MetricsCollector()

    collector.record_operation("render", 100.0)
    collector.record_operation("render", 200.0)
    collector.record_operation("save", 50.0)

    stats = collector.get_operation_stats("render")
    assert stats["count"] == 2
    assert stats["avg_ms"] == 150.0

    stats = collector.get_operation_stats("save")
    assert stats["count"] == 1
    assert stats["avg_ms"] == 50.0


def test_metrics_collector_record_cache():
    """Test recording cache events."""
    collector = MetricsCollector()

    collector.record_cache_event("preview", hit=True)
    collector.record_cache_event("preview", hit=True)
    collector.record_cache_event("preview", hit=False)

    stats = collector.get_cache_stats("preview")
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["hit_rate"] == pytest.approx(0.666, rel=0.01)


def test_metrics_collector_statistics():
    """Test getting comprehensive statistics."""
    collector = MetricsCollector()

    collector.record_operation("render", 100.0)
    collector.record_cache_event("preview", hit=True)

    stats = collector.get_statistics()

    assert "uptime_seconds" in stats
    assert "operations" in stats
    assert "caches" in stats
    assert "render" in stats["operations"]
    assert "preview" in stats["caches"]


def test_metrics_collector_generate_report():
    """Test generating performance report."""
    collector = MetricsCollector()

    collector.record_operation("render", 100.0)
    collector.record_operation("render", 200.0)
    collector.record_cache_event("preview", hit=True)
    collector.record_cache_event("preview", hit=False)

    report = collector.generate_report()

    assert "Performance Metrics Report" in report
    assert "render" in report
    assert "preview" in report
    assert "Count:" in report
    assert "Hit Rate:" in report


def test_metrics_collector_reset():
    """Test resetting metrics."""
    collector = MetricsCollector()

    collector.record_operation("render", 100.0)
    collector.record_cache_event("preview", hit=True)

    collector.reset()

    stats = collector.get_statistics()
    assert len(stats["operations"]) == 0
    assert len(stats["caches"]) == 0


def test_metrics_collector_enable_disable():
    """Test enabling/disabling metrics collection."""
    collector = MetricsCollector()

    # Disable and record
    collector.disable()
    collector.record_operation("render", 100.0)

    stats = collector.get_statistics()
    assert len(stats["operations"]) == 0

    # Enable and record
    collector.enable()
    collector.record_operation("render", 100.0)

    stats = collector.get_statistics()
    assert len(stats["operations"]) == 1


def test_get_metrics_collector_singleton():
    """Test global metrics collector singleton."""
    collector1 = get_metrics_collector()
    collector2 = get_metrics_collector()

    assert collector1 is collector2


def test_measure_time_decorator():
    """Test automatic timing decorator."""
    collector = get_metrics_collector()
    collector.reset()

    @measure_time("test_function")
    def slow_function():
        time.sleep(0.1)  # Sleep 100ms
        return "done"

    result = slow_function()

    assert result == "done"

    stats = collector.get_operation_stats("test_function")
    assert stats is not None
    assert stats["count"] == 1
    assert stats["avg_ms"] >= 100.0  # At least 100ms


def test_measure_time_decorator_multiple_calls():
    """Test decorator with multiple calls."""
    collector = get_metrics_collector()
    collector.reset()

    @measure_time("fast_function")
    def fast_function(value):
        return value * 2

    for i in range(10):
        fast_function(i)

    stats = collector.get_operation_stats("fast_function")
    assert stats["count"] == 10


def test_operation_metrics_empty():
    """Test metrics with no data."""
    metrics = OperationMetrics(operation_name="empty")

    stats = metrics.get_stats()
    assert stats["count"] == 0
    assert stats["avg_ms"] == 0.0


def test_cache_metrics_empty():
    """Test cache metrics with no data."""
    cache = CacheMetrics(cache_name="empty")

    assert cache.get_hit_rate() == 0.0

    stats = cache.get_stats()
    assert stats["total"] == 0


def test_metrics_collector_nonexistent_operation():
    """Test getting stats for non-existent operation."""
    collector = MetricsCollector()

    stats = collector.get_operation_stats("nonexistent")
    assert stats is None


def test_metrics_collector_nonexistent_cache():
    """Test getting stats for non-existent cache."""
    collector = MetricsCollector()

    stats = collector.get_cache_stats("nonexistent")
    assert stats is None


def test_operation_metrics_max_buffer():
    """Test that operation metrics buffer is limited."""
    metrics = OperationMetrics(operation_name="test")

    # Record more than buffer size (1000)
    for i in range(1500):
        metrics.record(float(i))

    # Should have exactly 1000 durations (buffer size)
    assert len(metrics.durations) == 1000
    # But count should be 1500
    assert metrics.count == 1500
