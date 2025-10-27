"""
Adaptive Debouncer - Smart timing for preview updates.

Implements:
- NFR-001: Preview update latency optimization (<350ms target)
- NFR-004: Memory usage optimization (adaptive resource management)

This module provides adaptive debouncing that adjusts preview delays based on:
- Document size (larger docs = longer delays)
- System CPU load (high load = longer delays)
- Recent render times (slow renders = longer delays)
- User typing speed (fast typing = longer delays)

Implements Phase 3.3 of Performance Optimization Plan:
- Adaptive timing based on system state
- Reduced CPU usage during heavy load
- Better user experience with smart delays

Design Goals:
- Responsive for small documents
- Efficient for large documents
- Adaptive to system load
- No preview lag during fast typing
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SystemMetrics:
    """
    System performance metrics.

    Uses __slots__ for memory efficiency.
    Created frequently during system monitoring.
    """

    cpu_percent: float
    memory_percent: float
    timestamp: float


@dataclass(slots=True)
class DebounceConfig:
    """
    Configuration for adaptive debouncing.

    Uses __slots__ for memory efficiency.
    """

    # Base delays (milliseconds)
    min_delay: int = 100
    max_delay: int = 2000
    default_delay: int = 350

    # Document size thresholds (characters)
    small_doc_threshold: int = 10_000
    medium_doc_threshold: int = 100_000
    large_doc_threshold: int = 500_000

    # CPU load thresholds (percent)
    low_cpu_threshold: float = 30.0
    medium_cpu_threshold: float = 60.0
    high_cpu_threshold: float = 80.0

    # Typing detection
    fast_typing_interval: float = 0.5  # seconds
    typing_multiplier: float = 1.5

    # Render time tracking
    slow_render_threshold: float = 0.5  # seconds
    render_time_multiplier: float = 2.0


class SystemMonitor:
    """
    Monitor system resources (CPU, memory).

    Tracks system performance and provides metrics for adaptive delays.
    Uses psutil for cross-platform system monitoring.
    """

    def __init__(self):
        """Initialize system monitor."""
        self._last_metrics: Optional[SystemMetrics] = None
        self._metrics_cache_duration = 1.0  # Cache for 1 second

    def get_metrics(self) -> SystemMetrics:
        """
        Get current system metrics.

        Returns:
            SystemMetrics with CPU and memory usage
        """
        now = time.time()

        # Return cached metrics if recent enough
        if self._last_metrics:
            age = now - self._last_metrics.timestamp
            if age < self._metrics_cache_duration:
                return self._last_metrics

        # Get fresh metrics
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent

            metrics = SystemMetrics(
                cpu_percent=cpu_percent, memory_percent=memory_percent, timestamp=now
            )

            self._last_metrics = metrics
            return metrics

        except Exception as exc:
            logger.warning(f"Failed to get system metrics: {exc}")
            # Return safe defaults
            return SystemMetrics(cpu_percent=50.0, memory_percent=50.0, timestamp=now)

    def get_cpu_load_category(self, config: DebounceConfig) -> str:
        """
        Get CPU load category (low/medium/high).

        Args:
            config: Debounce configuration

        Returns:
            'low', 'medium', or 'high'
        """
        metrics = self.get_metrics()
        cpu = metrics.cpu_percent

        if cpu < config.low_cpu_threshold:
            return "low"
        elif cpu < config.medium_cpu_threshold:
            return "medium"
        elif cpu < config.high_cpu_threshold:
            return "high"
        else:
            return "very_high"


class AdaptiveDebouncer:
    """
    Adaptive debouncer for preview updates.

    Calculates optimal preview delay based on:
    - Document size
    - System CPU load
    - Recent render times
    - User typing speed

    Example:
        debouncer = AdaptiveDebouncer()

        # On text change
        delay = debouncer.calculate_delay(
            document_size=50000,
            last_render_time=0.3
        )
        # delay = 450 (adjusted for medium doc + CPU)

        # Start timer with calculated delay
        timer.start(delay)
    """

    def __init__(self, config: Optional[DebounceConfig] = None):
        """
        Initialize adaptive debouncer.

        Args:
            config: Optional configuration (uses defaults if None)
        """
        self.config = config or DebounceConfig()
        self.system_monitor = SystemMonitor()

        # Tracking state
        self._last_change_time = 0.0
        self._keystroke_times: list[float] = []
        self._recent_render_times: list[float] = []
        self._max_recent_renders = 5

        # Statistics
        self._delay_history: list[int] = []
        self._max_history = 100

    def calculate_delay(
        self, document_size: int, last_render_time: Optional[float] = None
    ) -> int:
        """
        Calculate adaptive delay for preview update.

        Args:
            document_size: Document size in characters
            last_render_time: Last render time in seconds (optional)

        Returns:
            Delay in milliseconds
        """
        # Start with base delay from document size
        base_delay = self._get_delay_for_size(document_size)

        # Adjust for CPU load
        cpu_multiplier = self._get_cpu_multiplier()
        delay = base_delay * cpu_multiplier

        # Adjust for typing speed
        typing_multiplier = self._get_typing_multiplier()
        delay *= typing_multiplier

        # Adjust for render time
        if last_render_time is not None:
            self._recent_render_times.append(last_render_time)
            if len(self._recent_render_times) > self._max_recent_renders:
                self._recent_render_times.pop(0)

            render_multiplier = self._get_render_time_multiplier()
            delay *= render_multiplier

        # Clamp to min/max
        delay = max(self.config.min_delay, min(delay, self.config.max_delay))
        delay = int(delay)

        # Track for statistics
        self._delay_history.append(delay)
        if len(self._delay_history) > self._max_history:
            self._delay_history.pop(0)

        logger.debug(
            f"Adaptive delay: {delay}ms "
            f"(size={document_size}, cpu={cpu_multiplier:.2f}x, "
            f"typing={typing_multiplier:.2f}x)"
        )

        return delay

    def _get_delay_for_size(self, size: int) -> float:
        """Get base delay for document size."""
        if size < self.config.small_doc_threshold:
            return 200
        elif size < self.config.medium_doc_threshold:
            return 350
        elif size < self.config.large_doc_threshold:
            return 500
        else:
            return 800

    def _get_cpu_multiplier(self) -> float:
        """Get CPU load multiplier."""
        cpu_category = self.system_monitor.get_cpu_load_category(self.config)

        multipliers = {
            "low": 0.8,  # Faster when CPU available
            "medium": 1.0,  # Normal
            "high": 1.5,  # Slower when busy
            "very_high": 2.0,  # Much slower when very busy
        }

        return multipliers.get(cpu_category, 1.0)

    def _get_typing_multiplier(self) -> float:
        """Get typing speed multiplier."""
        now = time.time()

        # Clean old keystrokes (older than 2 seconds)
        self._keystroke_times = [t for t in self._keystroke_times if now - t < 2.0]

        # Fast typing = more than 2 keystrokes in last 0.5s
        recent = [
            t
            for t in self._keystroke_times
            if now - t < self.config.fast_typing_interval
        ]

        if len(recent) >= 3:
            # User typing fast - increase delay
            return self.config.typing_multiplier

        return 1.0

    def _get_render_time_multiplier(self) -> float:
        """Get render time multiplier based on recent renders."""
        if not self._recent_render_times:
            return 1.0

        # Average recent render times
        avg_render_time = sum(self._recent_render_times) / len(
            self._recent_render_times
        )

        # If renders are slow, increase delay
        if avg_render_time > self.config.slow_render_threshold:
            return self.config.render_time_multiplier

        return 1.0

    def on_text_changed(self) -> None:
        """
        Call this when text changes (for typing detection).

        Tracks keystroke timing for typing speed detection.
        """
        now = time.time()
        self._last_change_time = now
        self._keystroke_times.append(now)

        # Keep only recent keystrokes
        if len(self._keystroke_times) > 10:
            self._keystroke_times.pop(0)

    def on_render_complete(self, render_time: float) -> None:
        """
        Call this when render completes.

        Args:
            render_time: Render time in seconds
        """
        self._recent_render_times.append(render_time)
        if len(self._recent_render_times) > self._max_recent_renders:
            self._recent_render_times.pop(0)

    def get_statistics(self) -> dict:
        """
        Get debouncer statistics.

        Returns:
            Dictionary with stats
        """
        if not self._delay_history:
            return {
                "avg_delay": 0,
                "min_delay": 0,
                "max_delay": 0,
                "total_adjustments": 0,
            }

        return {
            "avg_delay": sum(self._delay_history) / len(self._delay_history),
            "min_delay": min(self._delay_history),
            "max_delay": max(self._delay_history),
            "total_adjustments": len(self._delay_history),
            "current_cpu": self.system_monitor.get_metrics().cpu_percent,
            "avg_render_time": (
                sum(self._recent_render_times) / len(self._recent_render_times)
                if self._recent_render_times
                else 0
            ),
        }

    def reset(self) -> None:
        """Reset tracking state."""
        self._last_change_time = 0.0
        self._keystroke_times = []
        self._recent_render_times = []
        self._delay_history = []
        logger.debug("Adaptive debouncer reset")
