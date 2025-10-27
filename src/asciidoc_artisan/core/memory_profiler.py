"""
Memory Profiler - Track application memory usage.

Provides detailed memory profiling using tracemalloc and psutil to identify
optimization opportunities and memory leaks.

Usage:
    profiler = get_profiler()
    profiler.start()

    # ... application code ...

    snapshot = profiler.take_snapshot("operation_name")
    print(snapshot)

    profiler.stop()

Or use as decorator:
    @profile_memory("render_preview")
    def render_preview(text):
        # ... function code ...
        pass
"""

import logging
import time
import tracemalloc
from dataclasses import dataclass
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Try to import psutil for system memory monitoring
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - system memory monitoring disabled")


@dataclass
class MemorySnapshot:
    """Memory usage snapshot."""

    timestamp: float
    current_mb: float
    peak_mb: float
    top_allocations: List[Tuple[str, int]]  # [(location, size_bytes)]
    description: str = ""

    def __str__(self) -> str:
        desc = f" ({self.description})" if self.description else ""
        return (
            f"Memory{desc}: {self.current_mb:.1f}MB current, "
            f"{self.peak_mb:.1f}MB peak"
        )


class MemoryProfiler:
    """
    Application memory profiler.

    Tracks memory usage using tracemalloc and psutil to identify:
    - Memory leaks
    - High memory consumers
    - Memory growth over time
    - Peak memory usage

    Features:
    - Take snapshots at any point
    - Compare snapshots to see memory deltas
    - Log top memory allocations
    - Get statistics over time
    - Minimal performance overhead when disabled

    Example:
        profiler = MemoryProfiler()
        profiler.start()

        snap1 = profiler.take_snapshot("before operation")
        do_operation()
        snap2 = profiler.take_snapshot("after operation")

        profiler.compare_snapshots(0, 1)
        profiler.stop()
    """

    def __init__(self, top_n: int = 10):
        """
        Initialize profiler.

        Args:
            top_n: Number of top allocations to track
        """
        self.top_n = top_n
        self.is_running = False
        self.snapshots: List[MemorySnapshot] = []
        self.process = None

        if PSUTIL_AVAILABLE:
            try:
                self.process = psutil.Process()
            except Exception as e:
                logger.warning(f"Failed to initialize psutil process: {e}")

    def start(self) -> None:
        """Start memory profiling."""
        if self.is_running:
            logger.warning("Memory profiler already running")
            return

        tracemalloc.start()
        self.is_running = True
        logger.info("Memory profiler started")

    def stop(self) -> None:
        """Stop memory profiling."""
        if not self.is_running:
            return

        tracemalloc.stop()
        self.is_running = False
        logger.info("Memory profiler stopped")

    def take_snapshot(self, description: str = "") -> Optional[MemorySnapshot]:
        """
        Take memory snapshot.

        Args:
            description: Optional description for this snapshot

        Returns:
            MemorySnapshot with current memory state, or None if not running
        """
        if not self.is_running:
            logger.warning("Memory profiler not running - call start() first")
            return None

        # Get tracemalloc statistics
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        # Get current and peak memory from tracemalloc
        current, peak = tracemalloc.get_traced_memory()
        current_mb = current / 1024 / 1024
        peak_mb = peak / 1024 / 1024

        # Get top allocations
        top_allocations = []
        for stat in top_stats[:self.top_n]:
            # Get first traceback frame for location
            if stat.traceback:
                frame = stat.traceback[0]
                location = f"{frame.filename}:{frame.lineno}"
            else:
                location = "unknown"
            size_bytes = stat.size
            top_allocations.append((location, size_bytes))

        mem_snapshot = MemorySnapshot(
            timestamp=time.time(),
            current_mb=current_mb,
            peak_mb=peak_mb,
            top_allocations=top_allocations,
            description=description
        )

        self.snapshots.append(mem_snapshot)

        if description:
            logger.info(f"Memory snapshot ({description}): {mem_snapshot}")
        else:
            logger.debug(f"Memory snapshot: {mem_snapshot}")

        return mem_snapshot

    def get_memory_usage(self) -> Tuple[float, float]:
        """
        Get current memory usage from OS (via psutil).

        Returns:
            Tuple of (memory_mb, memory_percent)
            Returns (0.0, 0.0) if psutil unavailable
        """
        if not PSUTIL_AVAILABLE or not self.process:
            return (0.0, 0.0)

        try:
            mem_info = self.process.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            mem_percent = self.process.memory_percent()
            return (mem_mb, mem_percent)
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return (0.0, 0.0)

    def log_top_allocations(self, n: int = 10) -> None:
        """
        Log top N memory allocations.

        Args:
            n: Number of top allocations to log
        """
        if not self.is_running:
            logger.warning("Memory profiler not running")
            return

        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        logger.info(f"Top {n} memory allocations:")
        for index, stat in enumerate(top_stats[:n], 1):
            size_kb = stat.size / 1024
            if stat.traceback:
                frame = stat.traceback[0]
                location = f"{frame.filename}:{frame.lineno}"
            else:
                location = "unknown"
            logger.info(
                f"  {index}. {location} - {size_kb:.1f} KB"
            )

    def compare_snapshots(self, index1: int, index2: int) -> None:
        """
        Compare two snapshots and log differences.

        Args:
            index1: Index of first snapshot
            index2: Index of second snapshot
        """
        if index1 >= len(self.snapshots) or index2 >= len(self.snapshots):
            logger.error("Invalid snapshot indices")
            return

        snap1 = self.snapshots[index1]
        snap2 = self.snapshots[index2]

        diff_mb = snap2.current_mb - snap1.current_mb
        time_diff = snap2.timestamp - snap1.timestamp

        logger.info(
            f"Memory change: {diff_mb:+.1f}MB "
            f"({snap1.current_mb:.1f}MB → {snap2.current_mb:.1f}MB) "
            f"over {time_diff:.1f}s"
        )

        if snap1.description and snap2.description:
            logger.info(f"  From: {snap1.description}")
            logger.info(f"  To: {snap2.description}")

    def get_statistics(self) -> dict:
        """
        Get profiler statistics.

        Returns:
            Dictionary with memory statistics
        """
        if not self.snapshots:
            return {
                "snapshots_count": 0,
                "profiler_running": self.is_running
            }

        current_mbs = [s.current_mb for s in self.snapshots]
        peak_mbs = [s.peak_mb for s in self.snapshots]

        stats = {
            "snapshots_count": len(self.snapshots),
            "profiler_running": self.is_running,
            "current_mb": self.snapshots[-1].current_mb,
            "peak_mb": max(peak_mbs),
            "min_mb": min(current_mbs),
            "avg_mb": sum(current_mbs) / len(current_mbs),
            "total_growth_mb": current_mbs[-1] - current_mbs[0] if len(current_mbs) > 1 else 0,
        }

        # Add psutil stats if available
        if PSUTIL_AVAILABLE and self.process:
            mem_mb, mem_percent = self.get_memory_usage()
            stats["system_memory_mb"] = mem_mb
            stats["system_memory_percent"] = mem_percent

        return stats

    def clear_snapshots(self) -> None:
        """Clear all snapshots."""
        self.snapshots.clear()
        logger.debug("Memory snapshots cleared")

    def get_snapshot_count(self) -> int:
        """Get number of snapshots taken."""
        return len(self.snapshots)

    def get_latest_snapshot(self) -> Optional[MemorySnapshot]:
        """Get the most recent snapshot."""
        if not self.snapshots:
            return None
        return self.snapshots[-1]


# Global profiler instance
_global_profiler: Optional[MemoryProfiler] = None


def get_profiler() -> MemoryProfiler:
    """
    Get global profiler instance.

    Returns:
        Global MemoryProfiler instance
    """
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = MemoryProfiler()
    return _global_profiler


def profile_memory(description: str = ""):
    """
    Decorator to profile memory usage of a function.

    Takes snapshots before and after function execution.

    Usage:
        @profile_memory("render_preview")
        def render_preview(text):
            # ... function code ...
            pass

    Args:
        description: Description for the profiled function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            profiler = get_profiler()

            # Auto-start if not running
            if not profiler.is_running:
                profiler.start()

            # Take before snapshot
            profiler.take_snapshot(f"{description or func.__name__} - before")

            # Execute function
            result = func(*args, **kwargs)

            # Take after snapshot
            profiler.take_snapshot(f"{description or func.__name__} - after")

            return result
        return wrapper
    return decorator


def main():
    """CLI for memory profiler demonstration."""
    import sys

    print("Memory Profiler Demo")
    print("=" * 50)

    profiler = get_profiler()
    profiler.start()

    print("\n1. Taking initial snapshot...")
    profiler.take_snapshot("Initial state")

    print("\n2. Allocating 10MB...")
    large_list = [0] * (10 * 1024 * 1024 // 8)  # ~10MB
    profiler.take_snapshot("After 10MB allocation")

    print("\n3. Allocating another 5MB...")
    medium_list = [0] * (5 * 1024 * 1024 // 8)  # ~5MB
    profiler.take_snapshot("After 5MB allocation")

    print("\n4. Comparing snapshots...")
    profiler.compare_snapshots(0, 1)
    profiler.compare_snapshots(1, 2)

    print("\n5. Statistics:")
    stats = profiler.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    print("\n6. Top allocations:")
    profiler.log_top_allocations(5)

    profiler.stop()

    print("\nDone!")


if __name__ == "__main__":
    main()
