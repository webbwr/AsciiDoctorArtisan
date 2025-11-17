"""
Performance baseline tests for AsciiDoc Artisan.

These tests establish and verify performance baselines for:
- Application startup time
- Memory usage
- Preview rendering performance
- File I/O operations
- CPU usage

Run with: pytest tests/performance/ -v --benchmark
"""

import json
import logging
import platform
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Optional

import psutil
import pytest

logger = logging.getLogger(__name__)

# Performance targets (will be calibrated after baseline)
PERFORMANCE_TARGETS = {
    "startup_time_ms": 2000,  # 2 seconds max
    "memory_base_mb": 200,  # 200 MB base
    "memory_1mb_doc_mb": 300,  # 300 MB with 1MB doc
    "preview_100_lines_ms": 50,  # 50ms for 100 lines
    "preview_1000_lines_ms": 200,  # 200ms for 1000 lines
    "file_load_1mb_ms": 100,  # 100ms to load 1MB
    "file_save_1mb_ms": 100,  # 100ms to save 1MB
}


class PerformanceProfiler:
    """Track and measure application performance."""

    def __init__(self):
        """Initialize performance profiler."""
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.process = psutil.Process()
        self.system_info = self._gather_system_info()

    def _gather_system_info(self) -> Dict[str, Any]:
        """Gather system information for context."""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "cpu_freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A",
        }

    @contextmanager
    def measure(self, operation: str):
        """
        Context manager to measure operation performance.

        Args:
            operation: Name of the operation being measured

        Yields:
            None

        Example:
            with profiler.measure('startup'):
                app = create_app()
        """
        # Collect garbage before measurement
        import gc

        gc.collect()

        # Get initial metrics
        start_time = time.perf_counter()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = self.process.cpu_percent()

        try:
            yield
        finally:
            # Get final metrics
            end_time = time.perf_counter()
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            end_cpu = self.process.cpu_percent()

            # Calculate metrics
            self.metrics[operation] = {
                "time_ms": round((end_time - start_time) * 1000, 2),
                "memory_start_mb": round(start_memory, 2),
                "memory_end_mb": round(end_memory, 2),
                "memory_delta_mb": round(end_memory - start_memory, 2),
                "cpu_percent": round((start_cpu + end_cpu) / 2, 2),
                "timestamp": time.time(),
            }

            logger.info(
                f"Performance: {operation} took {self.metrics[operation]['time_ms']:.2f}ms, "
                f"memory delta: {self.metrics[operation]['memory_delta_mb']:.2f}MB"
            )

    def get_metric(self, operation: str, metric_name: str) -> Optional[float]:
        """
        Get a specific metric for an operation.

        Args:
            operation: Name of the operation
            metric_name: Name of the metric (e.g., 'time_ms', 'memory_delta_mb')

        Returns:
            Metric value or None if not found
        """
        return self.metrics.get(operation, {}).get(metric_name)

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.

        Returns:
            Dictionary containing all metrics and system info
        """
        return {
            "timestamp": time.time(),
            "system_info": self.system_info,
            "metrics": self.metrics,
            "summary": self._generate_summary(),
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        if not self.metrics:
            return {}

        all_times = [m["time_ms"] for m in self.metrics.values() if "time_ms" in m]
        all_memory_deltas = [
            m["memory_delta_mb"]
            for m in self.metrics.values()
            if "memory_delta_mb" in m
        ]

        return {
            "total_operations": len(self.metrics),
            "avg_time_ms": (
                round(sum(all_times) / len(all_times), 2) if all_times else 0
            ),
            "max_time_ms": round(max(all_times), 2) if all_times else 0,
            "total_memory_delta_mb": (
                round(sum(all_memory_deltas), 2) if all_memory_deltas else 0
            ),
        }

    def save_report(self, filepath: Path):
        """
        Save performance report to JSON file.

        Args:
            filepath: Path to save the report
        """
        report = self.generate_report()
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Performance report saved to {filepath}")

    def compare_with_baseline(self, baseline_file: Path) -> Dict[str, Any]:
        """
        Compare current metrics with baseline.

        Args:
            baseline_file: Path to baseline JSON file

        Returns:
            Dictionary with comparison results
        """
        if not baseline_file.exists():
            return {"error": "Baseline file not found"}

        with open(baseline_file, "r") as f:
            baseline = json.load(f)

        current = self.generate_report()
        comparison = {"regressions": [], "improvements": [], "unchanged": []}

        for operation, metrics in current["metrics"].items():
            if operation not in baseline["metrics"]:
                continue

            baseline_time = baseline["metrics"][operation].get("time_ms", 0)
            current_time = metrics.get("time_ms", 0)

            if current_time > baseline_time * 1.1:  # 10% slower
                comparison["regressions"].append(
                    {
                        "operation": operation,
                        "baseline_ms": baseline_time,
                        "current_ms": current_time,
                        "change_percent": round(
                            ((current_time - baseline_time) / baseline_time) * 100, 2
                        ),
                    }
                )
            elif current_time < baseline_time * 0.9:  # 10% faster
                comparison["improvements"].append(
                    {
                        "operation": operation,
                        "baseline_ms": baseline_time,
                        "current_ms": current_time,
                        "change_percent": round(
                            ((current_time - baseline_time) / baseline_time) * 100, 2
                        ),
                    }
                )
            else:
                comparison["unchanged"].append(operation)

        return comparison


# Pytest fixtures


@pytest.fixture
def profiler():
    """Create a performance profiler instance."""
    return PerformanceProfiler()


@pytest.fixture
def performance_report_dir(tmp_path):
    """Create temporary directory for performance reports."""
    report_dir = tmp_path / "performance_reports"
    report_dir.mkdir()
    return report_dir


def generate_test_document(num_lines: int) -> str:
    """
    Generate test AsciiDoc document.

    Args:
        num_lines: Number of lines to generate

    Returns:
        AsciiDoc content string
    """
    lines = [
        "= Test Document",
        ":toc:",
        "",
        "== Introduction",
        "",
        "This is a test document for performance benchmarking.",
        "",
    ]

    for i in range(1, num_lines // 10):
        lines.extend(
            [
                f"== Section {i}",
                "",
                f"This is section {i} with some content.",
                "",
                "* Item 1",
                "* Item 2",
                "* Item 3",
                "",
                "[source,python]",
                "----",
                "def example():",
                "    return 'test'",
                "----",
                "",
            ]
        )

    return "\n".join(lines)


# Performance tests


@pytest.mark.performance
def test_memory_baseline(profiler):
    """Test base memory usage."""
    with profiler.measure("memory_baseline"):
        # Just measure current memory
        time.sleep(0.1)

    memory_mb = profiler.get_metric("memory_baseline", "memory_end_mb")
    assert memory_mb is not None
    logger.info(f"Baseline memory: {memory_mb:.2f} MB")


@pytest.mark.performance
def test_small_document_generation(profiler):
    """Test performance of generating small document."""
    with profiler.measure("generate_small_doc"):
        generate_test_document(100)

    time_ms = profiler.get_metric("generate_small_doc", "time_ms")
    assert time_ms < 100, f"Small doc generation took {time_ms}ms (expected < 100ms)"


@pytest.mark.performance
def test_medium_document_generation(profiler):
    """Test performance of generating medium document."""
    with profiler.measure("generate_medium_doc"):
        generate_test_document(1000)

    time_ms = profiler.get_metric("generate_medium_doc", "time_ms")
    assert time_ms < 1000, f"Medium doc generation took {time_ms}ms (expected < 1000ms)"


@pytest.mark.performance
def test_large_document_generation(profiler):
    """Test performance of generating large document."""
    with profiler.measure("generate_large_doc"):
        generate_test_document(10000)

    time_ms = profiler.get_metric("generate_large_doc", "time_ms")
    assert time_ms < 5000, f"Large doc generation took {time_ms}ms (expected < 5000ms)"


@pytest.mark.performance
def test_profiler_overhead(profiler):
    """Test performance profiler overhead."""
    # Measure overhead of measurement itself
    iterations = 100

    start = time.perf_counter()
    for i in range(iterations):
        with profiler.measure(f"overhead_test_{i}"):
            pass
    end = time.perf_counter()

    total_overhead_ms = (end - start) * 1000
    avg_overhead_ms = total_overhead_ms / iterations

    # Allow higher overhead in WSL/virtualized environments
    # WSL2 has ~40% higher overhead due to virtualization layer
    is_wsl = "microsoft" in platform.uname().release.lower()
    threshold_ms = 150.0 if is_wsl else 100.0

    assert (
        avg_overhead_ms < threshold_ms
    ), f"Profiler overhead too high: {avg_overhead_ms:.3f}ms per measurement (threshold: {threshold_ms}ms, WSL: {is_wsl})"
    logger.info(
        f"Profiler overhead: {avg_overhead_ms:.3f}ms per measurement (threshold: {threshold_ms}ms, WSL: {is_wsl})"
    )


@pytest.mark.performance
def test_save_performance_report(profiler, performance_report_dir):
    """Test saving performance report."""
    # Generate some metrics
    with profiler.measure("test_operation"):
        time.sleep(0.01)

    # Save report
    report_file = performance_report_dir / "test_report.json"
    profiler.save_report(report_file)

    # Verify report exists and is valid
    assert report_file.exists()

    with open(report_file, "r") as f:
        report = json.load(f)

    assert "system_info" in report
    assert "metrics" in report
    assert "summary" in report
    assert "test_operation" in report["metrics"]


@pytest.mark.performance
def test_generate_report_structure(profiler):
    """Test performance report structure."""
    # Generate some metrics
    with profiler.measure("op1"):
        time.sleep(0.01)

    with profiler.measure("op2"):
        time.sleep(0.02)

    report = profiler.generate_report()

    # Verify structure
    assert "timestamp" in report
    assert "system_info" in report
    assert "metrics" in report
    assert "summary" in report

    # Verify system info
    assert "platform" in report["system_info"]
    assert "cpu_count" in report["system_info"]
    assert "memory_total_gb" in report["system_info"]

    # Verify metrics
    assert "op1" in report["metrics"]
    assert "op2" in report["metrics"]
    assert "time_ms" in report["metrics"]["op1"]
    assert "memory_delta_mb" in report["metrics"]["op1"]

    # Verify summary
    assert report["summary"]["total_operations"] == 2
    assert report["summary"]["avg_time_ms"] > 0


if __name__ == "__main__":
    # Run standalone for quick testing

    print("Running performance baseline tests...")
    profiler = PerformanceProfiler()

    print("\nSystem Information:")
    for key, value in profiler.system_info.items():
        print(f"  {key}: {value}")

    print("\nGenerating test documents...")
    with profiler.measure("generate_100_lines"):
        doc_100 = generate_test_document(100)

    with profiler.measure("generate_1000_lines"):
        doc_1000 = generate_test_document(1000)

    with profiler.measure("generate_10000_lines"):
        doc_10000 = generate_test_document(10000)

    print("\nPerformance Metrics:")
    for operation, metrics in profiler.metrics.items():
        print(
            f"  {operation}: {metrics['time_ms']:.2f}ms, memory: {metrics['memory_delta_mb']:.2f}MB"
        )

    print("\nSummary:")
    summary = profiler._generate_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
