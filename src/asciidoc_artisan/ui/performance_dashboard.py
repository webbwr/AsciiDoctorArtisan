"""Performance Benchmarking Dashboard - Real-time performance metrics display."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Single performance metric with history."""

    name: str
    value: float = 0.0
    unit: str = "ms"
    target: float = 0.0
    history: list[float] = field(default_factory=list)
    max_history: int = 100

    def record(self, value: float) -> None:
        """Record a new metric value."""
        self.value = value
        self.history.append(value)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    @property
    def average(self) -> float:
        """Get average of recorded values."""
        return sum(self.history) / len(self.history) if self.history else 0.0

    @property
    def meets_target(self) -> bool:
        """Check if current value meets target."""
        return self.value <= self.target if self.target > 0 else True


class PerformanceCollector:
    """Collects and manages performance metrics."""

    def __init__(self) -> None:
        """Initialize performance collector."""
        self.metrics: dict[str, PerformanceMetric] = {}
        self._start_times: dict[str, float] = {}
        self._init_default_metrics()

    def _init_default_metrics(self) -> None:
        """Initialize default metrics with targets."""
        defaults = [
            ("startup_time", "ms", 500.0),
            ("preview_render", "ms", 100.0),
            ("file_open", "ms", 200.0),
            ("file_save", "ms", 150.0),
            ("search_query", "ms", 50.0),
            ("memory_usage", "MB", 512.0),
            ("gpu_render", "ms", 50.0),
            ("incremental_render", "ms", 30.0),
        ]
        for name, unit, target in defaults:
            self.metrics[name] = PerformanceMetric(name=name, unit=unit, target=target)

    def start_timer(self, metric_name: str) -> None:
        """Start timing a metric."""
        self._start_times[metric_name] = time.perf_counter()

    def stop_timer(self, metric_name: str) -> float:
        """Stop timing and record metric. Returns elapsed time in ms."""
        if metric_name not in self._start_times:
            return 0.0

        elapsed = (time.perf_counter() - self._start_times[metric_name]) * 1000
        del self._start_times[metric_name]

        if metric_name not in self.metrics:
            self.metrics[metric_name] = PerformanceMetric(name=metric_name)

        self.metrics[metric_name].record(elapsed)
        return elapsed

    def record_metric(self, name: str, value: float, unit: str = "ms") -> None:
        """Record a metric value directly."""
        if name not in self.metrics:
            self.metrics[name] = PerformanceMetric(name=name, unit=unit)
        self.metrics[name].record(value)

    def get_summary(self) -> dict[str, dict[str, Any]]:
        """Get summary of all metrics."""
        return {
            name: {
                "current": metric.value,
                "average": metric.average,
                "target": metric.target,
                "unit": metric.unit,
                "meets_target": metric.meets_target,
                "samples": len(metric.history),
            }
            for name, metric in self.metrics.items()
        }


# Global collector instance
_collector: PerformanceCollector | None = None


def get_performance_collector() -> PerformanceCollector:
    """Get or create global performance collector."""
    global _collector
    if _collector is None:
        _collector = PerformanceCollector()
    return _collector


class PerformanceDashboard(QDialog):
    """Dialog showing real-time performance metrics."""

    refresh_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize performance dashboard."""
        super().__init__(parent)
        self.collector = get_performance_collector()
        self._init_ui()
        self._start_auto_refresh()

    def _init_ui(self) -> None:
        """Initialize the UI."""
        self.setWindowTitle("Performance Dashboard")
        self.setMinimumSize(700, 500)
        layout = QVBoxLayout(self)

        # Header with refresh button
        header = QHBoxLayout()
        header.addWidget(QLabel("<b>Performance Metrics</b>"))
        header.addStretch()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_metrics)
        header.addWidget(self.refresh_btn)
        layout.addLayout(header)

        # Overall health indicator
        self.health_group = QGroupBox("System Health")
        health_layout = QHBoxLayout()
        self.health_bar = QProgressBar()
        self.health_bar.setRange(0, 100)
        self.health_bar.setValue(100)
        self.health_label = QLabel("Excellent")
        health_layout.addWidget(self.health_bar)
        health_layout.addWidget(self.health_label)
        self.health_group.setLayout(health_layout)
        layout.addWidget(self.health_group)

        # Metrics table
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(6)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Current", "Average", "Target", "Status", "Samples"])
        self.metrics_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.metrics_table)

        # Quick stats
        stats_group = QGroupBox("Quick Stats")
        stats_layout = QHBoxLayout()
        self.startup_label = QLabel("Startup: --")
        self.render_label = QLabel("Render: --")
        self.memory_label = QLabel("Memory: --")
        stats_layout.addWidget(self.startup_label)
        stats_layout.addWidget(self.render_label)
        stats_layout.addWidget(self.memory_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.run_benchmark_btn = QPushButton("Run Benchmark")
        self.run_benchmark_btn.clicked.connect(self._run_benchmark)
        btn_layout.addWidget(self.run_benchmark_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self._refresh_metrics()

    def _start_auto_refresh(self) -> None:
        """Start auto-refresh timer."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_metrics)
        self.refresh_timer.start(2000)

    def _refresh_metrics(self) -> None:
        """Refresh metrics display."""
        summary = self.collector.get_summary()

        # Update table
        self.metrics_table.setRowCount(len(summary))
        row = 0
        passing = 0
        total = 0

        for name, data in summary.items():
            self.metrics_table.setItem(row, 0, QTableWidgetItem(name.replace("_", " ").title()))
            self.metrics_table.setItem(row, 1, QTableWidgetItem(f"{data['current']:.1f} {data['unit']}"))
            self.metrics_table.setItem(row, 2, QTableWidgetItem(f"{data['average']:.1f} {data['unit']}"))
            self.metrics_table.setItem(row, 3, QTableWidgetItem(f"{data['target']:.0f} {data['unit']}"))

            status = "✓ Pass" if data["meets_target"] else "✗ Slow"
            status_item = QTableWidgetItem(status)
            if data["meets_target"]:
                passing += 1
            total += 1

            self.metrics_table.setItem(row, 4, status_item)
            self.metrics_table.setItem(row, 5, QTableWidgetItem(str(data["samples"])))
            row += 1

        # Update health bar
        health_pct = int((passing / total) * 100) if total > 0 else 100
        self.health_bar.setValue(health_pct)
        if health_pct >= 90:
            self.health_label.setText("Excellent")
            self.health_bar.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
        elif health_pct >= 70:
            self.health_label.setText("Good")
            self.health_bar.setStyleSheet("QProgressBar::chunk { background-color: #FFC107; }")
        else:
            self.health_label.setText("Needs Attention")
            self.health_bar.setStyleSheet("QProgressBar::chunk { background-color: #F44336; }")

        # Update quick stats
        if "startup_time" in summary:
            self.startup_label.setText(f"Startup: {summary['startup_time']['current']:.0f}ms")
        if "preview_render" in summary:
            self.render_label.setText(f"Render: {summary['preview_render']['average']:.0f}ms")
        if "memory_usage" in summary:
            self.memory_label.setText(f"Memory: {summary['memory_usage']['current']:.0f}MB")

    def _run_benchmark(self) -> None:
        """Run a quick benchmark."""
        self.run_benchmark_btn.setEnabled(False)
        self.run_benchmark_btn.setText("Running...")

        # Simple benchmarks
        import gc

        # Memory benchmark
        import psutil

        process = psutil.Process()
        mem_mb = process.memory_info().rss / (1024 * 1024)
        self.collector.record_metric("memory_usage", mem_mb, "MB")

        # GC benchmark
        self.collector.start_timer("gc_collect")
        gc.collect()
        self.collector.stop_timer("gc_collect")

        self._refresh_metrics()
        self.run_benchmark_btn.setText("Run Benchmark")
        self.run_benchmark_btn.setEnabled(True)

    def closeEvent(self, event: Any) -> None:
        """Handle close event."""
        self.refresh_timer.stop()
        super().closeEvent(event)
