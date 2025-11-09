"""
CPU Profiler - Runtime CPU profiling for performance analysis.

Provides integrated CPU profiling capabilities:
- Context manager for profiling code blocks
- cProfile integration with statistics
- Hotspot detection and analysis
- Performance report generation

Design Goals:
- Zero overhead when disabled
- Minimal overhead when enabled (~2-5%)
- Easy integration into existing code
- Actionable performance insights

QA-15: CPU Profiling Integration

Usage:
    from asciidoc_artisan.core.cpu_profiler import CPUProfiler

    profiler = CPUProfiler()

    # Profile a code block
    with profiler.profile("operation_name"):
        # Code to profile
        pass

    # Get report
    report = profiler.get_report()
"""

import cProfile
import io
import logging
import pstats
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProfileResult:
    """
    Result of a profiling session.

    Attributes:
        name: Name of the profiled operation
        total_time: Total CPU time (seconds)
        call_count: Number of times operation was called
        hotspots: Top CPU hotspots (function, time, calls)
        timestamp: When profiling occurred
    """

    name: str
    total_time: float
    call_count: int
    hotspots: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class CPUProfiler:
    """
    CPU profiler for runtime performance analysis.

    Features:
    - Context manager for profiling code blocks
    - cProfile integration with statistics collection
    - Hotspot detection (top 10 time-consuming functions)
    - Performance report generation
    - Low overhead (~2-5% when enabled)

    Example:
        profiler = CPUProfiler(enabled=True)

        with profiler.profile("render_preview"):
            # Code to profile
            pass

        # Get statistics
        report = profiler.get_report()
        hotspots = profiler.get_hotspots("render_preview", limit=5)
    """

    def __init__(self, enabled: bool = True, max_results: int = 100):
        """
        Initialize CPU profiler.

        Args:
            enabled: Enable profiling (default True)
            max_results: Maximum number of profile results to keep
        """
        self.enabled = enabled
        self.max_results = max_results

        self._results: Dict[str, List[ProfileResult]] = {}
        self._profilers: Dict[str, cProfile.Profile] = {}
        self._active_profiles: Dict[str, float] = {}  # name -> start_time

        logger.debug(f"CPUProfiler initialized (enabled={enabled})")

    @contextmanager
    def profile(self, name: str) -> Generator[None, None, None]:
        """
        Context manager for profiling a code block.

        Args:
            name: Name of the operation to profile

        Example:
            with profiler.profile("expensive_operation"):
                # Code to profile
                pass
        """
        if not self.enabled:
            yield  # No-op when disabled
            return

        # Create profiler for this operation
        profiler = cProfile.Profile()
        start_time = time.perf_counter()

        self._active_profiles[name] = start_time

        try:
            profiler.enable()
            yield
        finally:
            profiler.disable()

            # Calculate elapsed time
            elapsed = time.perf_counter() - start_time
            self._active_profiles.pop(name, None)

            # Extract statistics
            stats = pstats.Stats(profiler)

            # Get hotspots (top 10 functions by cumulative time)
            stream = io.StringIO()
            stats.stream = stream  # type: ignore[attr-defined]  # pstats.Stats.stream is writable
            stats.sort_stats("cumulative")
            stats.print_stats(10)

            hotspots = self._parse_hotspots(stream.getvalue())

            # Store result
            result = ProfileResult(
                name=name, total_time=elapsed, call_count=1, hotspots=hotspots
            )

            if name not in self._results:
                self._results[name] = []

            self._results[name].append(result)

            # Limit stored results
            if len(self._results[name]) > self.max_results:
                self._results[name] = self._results[name][-self.max_results :]

            logger.debug(
                f"Profile complete: {name} took {elapsed * 1000:.2f}ms, {len(hotspots)} hotspots detected"
            )

    def _parse_hotspots(self, stats_output: str) -> List[Dict[str, Any]]:
        """
        Parse cProfile stats output to extract hotspots.

        Args:
            stats_output: Output from pstats.print_stats()

        Returns:
            List of hotspot dicts with function, cumtime, ncalls
        """
        hotspots = []
        lines = stats_output.split("\n")

        # Skip header lines
        data_start = False
        for line in lines:
            if "ncalls" in line and "tottime" in line:
                data_start = True
                continue

            if not data_start or not line.strip():
                continue

            # Parse stats line
            # Format: ncalls tottime percall cumtime percall filename:lineno(function)
            parts = line.split()
            if len(parts) >= 6:
                try:
                    ncalls = parts[0].split("/")[0]  # Handle "x/y" format
                    cumtime = float(parts[3])
                    func_info = " ".join(parts[5:])

                    hotspots.append(
                        {
                            "function": func_info,
                            "cumtime": cumtime,
                            "ncalls": int(ncalls),
                        }
                    )
                except (ValueError, IndexError):
                    continue

        return hotspots[:10]  # Top 10 only

    def get_results(self, name: str) -> List[ProfileResult]:
        """
        Get all profile results for an operation.

        Args:
            name: Operation name

        Returns:
            List of ProfileResult objects
        """
        return self._results.get(name, [])

    def get_hotspots(self, name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get hotspots for an operation (most recent profiling).

        Args:
            name: Operation name
            limit: Number of hotspots to return

        Returns:
            List of hotspot dicts
        """
        results = self._results.get(name, [])
        if not results:
            return []

        # Get most recent result
        latest = results[-1]
        return latest.hotspots[:limit]

    def get_statistics(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get aggregated statistics for an operation.

        Args:
            name: Operation name

        Returns:
            Dict with stats (avg_time, total_calls, etc.) or None
        """
        results = self._results.get(name, [])
        if not results:
            return None

        total_time = sum(r.total_time for r in results)
        total_calls = sum(r.call_count for r in results)
        avg_time = total_time / total_calls if total_calls > 0 else 0

        return {
            "operation": name,
            "total_time": total_time,
            "total_calls": total_calls,
            "avg_time": avg_time,
            "num_profiles": len(results),
        }

    def get_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive profiling report.

        Returns:
            Dict with profiling results for all operations
        """
        report: dict[str, dict[str, Any]] = {"operations": {}, "summary": {}}

        for name in self._results:
            stats = self.get_statistics(name)
            hotspots = self.get_hotspots(name, limit=5)

            report["operations"][name] = {"stats": stats, "hotspots": hotspots}

        # Summary statistics
        all_results = [r for results in self._results.values() for r in results]
        if all_results:
            report["summary"] = {
                "total_operations": len(self._results),
                "total_profiles": len(all_results),
                "total_time": sum(r.total_time for r in all_results),
            }

        return report

    def reset(self) -> None:
        """Clear all profiling results."""
        self._results.clear()
        self._profilers.clear()
        self._active_profiles.clear()
        logger.debug("CPU profiler reset")

    def is_profiling(self, name: str) -> bool:
        """
        Check if an operation is currently being profiled.

        Args:
            name: Operation name

        Returns:
            True if operation is being profiled
        """
        return name in self._active_profiles


# Global profiler instance
_cpu_profiler: Optional[CPUProfiler] = None


def get_cpu_profiler() -> CPUProfiler:
    """
    Get global CPU profiler instance (singleton).

    Returns:
        Global CPUProfiler instance
    """
    global _cpu_profiler
    if _cpu_profiler is None:
        _cpu_profiler = CPUProfiler(enabled=False)  # Disabled by default
    return _cpu_profiler


def enable_cpu_profiling() -> None:
    """Enable global CPU profiling."""
    profiler = get_cpu_profiler()
    profiler.enabled = True
    logger.info("CPU profiling enabled")


def disable_cpu_profiling() -> None:
    """Disable global CPU profiling."""
    profiler = get_cpu_profiler()
    profiler.enabled = False
    logger.info("CPU profiling disabled")
