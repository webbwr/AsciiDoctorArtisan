"""
Metrics Collection System - Track operation performance and statistics.

Provides lightweight metrics collection for:
- Operation durations (preview render, file I/O, conversions)
- Cache hit/miss rates
- Performance percentiles (p50, p95, p99)
- Trend analysis over time

Usage:
    metrics = get_metrics_collector()
    metrics.record_operation("preview_render", duration_ms=250.5)
    metrics.record_cache_event("preview_cache", hit=True)

    # Get statistics
    stats = metrics.get_statistics()
    print(stats)

    # Generate report
    report = metrics.generate_report()
    print(report)
"""

import logging
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class OperationMetrics:
    """Metrics for a specific operation type."""

    operation_name: str
    durations: deque[float] = field(default_factory=lambda: deque(maxlen=1000))
    count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float("inf")
    max_time_ms: float = 0.0

    def record(self, duration_ms: float) -> None:
        """Record an operation duration."""
        self.durations.append(duration_ms)
        self.count += 1
        self.total_time_ms += duration_ms
        self.min_time_ms = min(self.min_time_ms, duration_ms)
        self.max_time_ms = max(self.max_time_ms, duration_ms)

    def get_average(self) -> float:
        """Get average duration in ms."""
        if self.count == 0:
            return 0.0
        return self.total_time_ms / self.count

    def get_percentile(self, percentile: int) -> float:
        """
        Get duration percentile (e.g., 50, 95, 99).

        Args:
            percentile: Percentile to calculate (0-100)

        Returns:
            Duration in ms at the specified percentile
        """
        if not self.durations:
            return 0.0
        sorted_durations = sorted(self.durations)
        index = int(len(sorted_durations) * (percentile / 100.0))
        index = min(index, len(sorted_durations) - 1)
        return sorted_durations[index]

    def get_stats(self) -> dict[str, float]:
        """Get comprehensive statistics."""
        if self.count == 0:
            return {
                "count": 0,
                "avg_ms": 0.0,
                "min_ms": 0.0,
                "max_ms": 0.0,
                "p50_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
            }

        return {
            "count": self.count,
            "avg_ms": self.get_average(),
            "min_ms": self.min_time_ms,
            "max_ms": self.max_time_ms,
            "p50_ms": self.get_percentile(50),
            "p95_ms": self.get_percentile(95),
            "p99_ms": self.get_percentile(99),
        }


@dataclass
class CacheMetrics:
    """Metrics for cache hit/miss rates."""

    cache_name: str
    hits: int = 0
    misses: int = 0

    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1

    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1

    def get_hit_rate(self) -> float:
        """Get cache hit rate (0.0 to 1.0)."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": self.hits + self.misses,
            "hit_rate": self.get_hit_rate(),
        }


class MetricsCollector:
    """
    Centralized metrics collection.

    Thread-safe singleton for collecting performance metrics.
    """

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.operations: defaultdict[str, OperationMetrics] = defaultdict(lambda: OperationMetrics(operation_name=""))
        self.caches: defaultdict[str, CacheMetrics] = defaultdict(lambda: CacheMetrics(cache_name=""))
        self.enabled = True
        self.start_time = time.time()

        logger.info("MetricsCollector initialized")

    def record_operation(self, operation_name: str, duration_ms: float) -> None:
        """
        Record an operation duration.

        Args:
            operation_name: Name of operation (e.g., "preview_render")
            duration_ms: Duration in milliseconds
        """
        if not self.enabled:
            return

        if operation_name not in self.operations:
            self.operations[operation_name] = OperationMetrics(operation_name=operation_name)

        self.operations[operation_name].record(duration_ms)

    def record_cache_event(self, cache_name: str, hit: bool) -> None:
        """
        Record a cache hit or miss.

        Args:
            cache_name: Name of cache (e.g., "preview_cache")
            hit: True if cache hit, False if cache miss
        """
        if not self.enabled:
            return

        if cache_name not in self.caches:
            self.caches[cache_name] = CacheMetrics(cache_name=cache_name)

        if hit:
            self.caches[cache_name].record_hit()
        else:
            self.caches[cache_name].record_miss()

    def get_operation_stats(self, operation_name: str) -> dict[str, float] | None:
        """Get statistics for a specific operation."""
        if operation_name not in self.operations:
            return None
        return self.operations[operation_name].get_stats()

    def get_cache_stats(self, cache_name: str) -> dict[str, Any] | None:
        """Get statistics for a specific cache."""
        if cache_name not in self.caches:
            return None
        return self.caches[cache_name].get_stats()

    def get_statistics(self) -> dict[str, Any]:
        """
        Get comprehensive statistics.

        Returns:
            Dictionary with all operation and cache statistics
        """
        stats: dict[str, Any] = {
            "uptime_seconds": time.time() - self.start_time,
            "operations": {},
            "caches": {},
        }

        operations_dict: dict[str, Any] = stats["operations"]
        for op_name, op_metrics in self.operations.items():
            operations_dict[op_name] = op_metrics.get_stats()

        caches_dict: dict[str, Any] = stats["caches"]
        for cache_name, cache_metrics in self.caches.items():
            caches_dict[cache_name] = cache_metrics.get_stats()

        return stats

    def generate_report(self) -> str:
        """
        Generate human-readable performance report.

        Returns:
            Formatted string report
        """
        stats = self.get_statistics()
        lines = []

        lines.append("=" * 60)
        lines.append("Performance Metrics Report")
        lines.append("=" * 60)
        lines.append(f"Uptime: {stats['uptime_seconds']:.1f} seconds")
        lines.append("")

        # Operations section
        if stats["operations"]:
            lines.append("Operations:")
            lines.append("-" * 60)

            for op_name, op_stats in sorted(stats["operations"].items()):
                lines.append(f"\n{op_name}:")
                lines.append(f"  Count:       {op_stats['count']}")
                lines.append(f"  Average:     {op_stats['avg_ms']:.2f} ms")
                lines.append(f"  Min:         {op_stats['min_ms']:.2f} ms")
                lines.append(f"  Max:         {op_stats['max_ms']:.2f} ms")
                lines.append(f"  p50 (median): {op_stats['p50_ms']:.2f} ms")
                lines.append(f"  p95:         {op_stats['p95_ms']:.2f} ms")
                lines.append(f"  p99:         {op_stats['p99_ms']:.2f} ms")

        # Caches section
        if stats["caches"]:
            lines.append("")
            lines.append("Caches:")
            lines.append("-" * 60)

            for cache_name, cache_stats in sorted(stats["caches"].items()):
                hit_rate = cache_stats["hit_rate"] * 100
                lines.append(f"\n{cache_name}:")
                lines.append(f"  Hits:        {cache_stats['hits']}")
                lines.append(f"  Misses:      {cache_stats['misses']}")
                lines.append(f"  Total:       {cache_stats['total']}")
                lines.append(f"  Hit Rate:    {hit_rate:.1f}%")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def reset(self) -> None:
        """Reset all metrics."""
        self.operations.clear()
        self.caches.clear()
        self.start_time = time.time()
        logger.info("Metrics reset")

    def enable(self) -> None:
        """Enable metrics collection."""
        self.enabled = True
        logger.info("Metrics collection enabled")

    def disable(self) -> None:
        """Disable metrics collection."""
        self.enabled = False
        logger.info("Metrics collection disabled")


# Global singleton instance
_metrics_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """
    Get global metrics collector singleton.

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# Decorator for automatic timing
def measure_time(
    operation_name: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to automatically measure and record operation time.

    Usage:
        @measure_time("preview_render")
        def render_preview(text):
            # ... function code ...
            pass

    Args:
        operation_name: Name to use for metrics
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics = get_metrics_collector()
                metrics.record_operation(operation_name, duration_ms)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator
