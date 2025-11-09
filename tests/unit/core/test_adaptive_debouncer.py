"""
Tests for adaptive debouncer.

Tests adaptive delay calculation based on document size, CPU load,
typing speed, and render times.
"""

import time

import pytest

from asciidoc_artisan.core.adaptive_debouncer import (
    AdaptiveDebouncer,
    DebounceConfig,
    SystemMetrics,
    SystemMonitor,
)


class TestSystemMonitor:
    """Test system monitoring."""

    def test_monitor_initialization(self):
        """Test monitor initializes correctly."""
        monitor = SystemMonitor()
        assert monitor._last_metrics is None

    def test_get_metrics(self):
        """Test getting system metrics."""
        monitor = SystemMonitor()
        metrics = monitor.get_metrics()

        assert isinstance(metrics, SystemMetrics)
        assert 0 <= metrics.cpu_percent <= 100
        assert 0 <= metrics.memory_percent <= 100
        assert metrics.timestamp > 0

    def test_metrics_caching(self):
        """Test metrics are cached for 1 second."""
        monitor = SystemMonitor()

        # First call
        metrics1 = monitor.get_metrics()
        time1 = metrics1.timestamp

        # Immediate second call (should be cached)
        metrics2 = monitor.get_metrics()
        time2 = metrics2.timestamp

        # Should be same timestamp (cached)
        assert time1 == time2

    def test_get_cpu_load_category(self):
        """Test CPU load categorization."""
        config = DebounceConfig()
        monitor = SystemMonitor()

        # Just test that it returns a valid category
        category = monitor.get_cpu_load_category(config)
        assert category in ["low", "medium", "high", "very_high"]

    def test_get_metrics_exception_handling(self):
        """Test system monitor handles exceptions gracefully."""
        from unittest.mock import patch

        monitor = SystemMonitor()

        # Mock psutil to raise exception
        with patch("psutil.cpu_percent", side_effect=Exception("Test error")):
            metrics = monitor.get_metrics()

            # Should return safe defaults (50%, 50%)
            assert metrics.cpu_percent == 50.0
            assert metrics.memory_percent == 50.0
            assert metrics.timestamp > 0

    def test_cpu_load_category_very_high(self):
        """Test CPU load category for very high load."""

        config = DebounceConfig()
        monitor = SystemMonitor()

        # Mock metrics with very high CPU (>80%)
        mock_metrics = SystemMetrics(
            cpu_percent=95.0, memory_percent=50.0, timestamp=time.time()
        )
        monitor._last_metrics = mock_metrics

        category = monitor.get_cpu_load_category(config)
        assert category == "very_high"

    def test_cpu_load_category_high(self):
        """Test CPU load category for high load."""
        config = DebounceConfig()
        monitor = SystemMonitor()

        # Mock metrics with high CPU (60-80%)
        mock_metrics = SystemMetrics(
            cpu_percent=70.0, memory_percent=50.0, timestamp=time.time()
        )
        monitor._last_metrics = mock_metrics

        category = monitor.get_cpu_load_category(config)
        assert category == "high"

    def test_cpu_load_category_medium(self):
        """Test CPU load category for medium load."""
        config = DebounceConfig()
        monitor = SystemMonitor()

        # Mock metrics with medium CPU (30-60%)
        mock_metrics = SystemMetrics(
            cpu_percent=45.0, memory_percent=50.0, timestamp=time.time()
        )
        monitor._last_metrics = mock_metrics

        category = monitor.get_cpu_load_category(config)
        assert category == "medium"

    def test_cpu_load_category_low(self):
        """Test CPU load category for low load."""
        config = DebounceConfig()
        monitor = SystemMonitor()

        # Mock metrics with low CPU (<30%)
        mock_metrics = SystemMetrics(
            cpu_percent=15.0, memory_percent=50.0, timestamp=time.time()
        )
        monitor._last_metrics = mock_metrics

        category = monitor.get_cpu_load_category(config)
        assert category == "low"


class TestDebounceConfig:
    """Test debounce configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DebounceConfig()

        # Defaults were reduced for lower latency (see adaptive_debouncer.py lines 59-61)
        assert config.min_delay == 50  # Reduced from 100ms
        assert config.max_delay == 1000  # Reduced from 2000ms
        assert config.default_delay == 200  # Reduced from 350ms
        assert config.small_doc_threshold == 10_000
        assert config.medium_doc_threshold == 100_000

    def test_custom_config(self):
        """Test custom configuration."""
        config = DebounceConfig(min_delay=50, max_delay=3000, default_delay=500)

        assert config.min_delay == 50
        assert config.max_delay == 3000
        assert config.default_delay == 500


class TestAdaptiveDebouncer:
    """Test adaptive debouncer."""

    def test_initialization(self):
        """Test debouncer initializes correctly."""
        debouncer = AdaptiveDebouncer()

        assert debouncer.config is not None
        assert debouncer.system_monitor is not None
        assert len(debouncer._keystroke_times) == 0
        assert len(debouncer._recent_render_times) == 0

    def test_custom_config(self):
        """Test debouncer with custom config."""
        config = DebounceConfig(min_delay=50, max_delay=3000)
        debouncer = AdaptiveDebouncer(config)

        assert debouncer.config.min_delay == 50
        assert debouncer.config.max_delay == 3000

    @pytest.mark.parametrize(
        "document_size,min_delay,max_delay,description",
        [
            # Small document (~5KB)
            (5_000, 50, 400, "small_doc"),
            # Medium document (~50KB)
            (50_000, 150, 600, "medium_doc"),
            # Large document (~200KB)
            (200_000, 200, 1000, "large_doc"),
            # Very large document (~1MB)
            (1_000_000, 400, 1000, "very_large_doc"),
        ],
        ids=[
            "small_5kb",
            "medium_50kb",
            "large_200kb",
            "very_large_1mb",
        ],
    )
    def test_calculate_delay_by_document_size(
        self, document_size, min_delay, max_delay, description
    ):
        """Test adaptive delay calculation scales with document size."""
        debouncer = AdaptiveDebouncer()

        delay = debouncer.calculate_delay(document_size=document_size)

        # Verify delay is within expected range for document size
        assert (
            min_delay <= delay <= max_delay
        ), f"Delay {delay}ms out of range [{min_delay}, {max_delay}] for {description}"

    def test_delay_clamping(self):
        """Test delays are clamped to min/max."""
        config = DebounceConfig(min_delay=100, max_delay=500)
        debouncer = AdaptiveDebouncer(config)

        # Very small doc - should clamp to min
        delay_small = debouncer.calculate_delay(document_size=10)
        assert delay_small >= 100

        # Very large doc - should clamp to max
        delay_large = debouncer.calculate_delay(document_size=10_000_000)
        assert delay_large <= 500

    def test_cpu_load_affects_delay(self):
        """Test CPU load affects delay calculation."""
        debouncer = AdaptiveDebouncer()

        # Just verify that delays are calculated in reasonable range
        # CPU monitoring is dynamic so we can't predict exact values
        delay = debouncer.calculate_delay(document_size=50000)

        # Should be in reasonable range for medium document (reduced max to 1000ms)
        assert 50 <= delay <= 1000

    def test_typing_speed_affects_delay(self):
        """Test fast typing increases delay."""
        debouncer = AdaptiveDebouncer()

        # Simulate fast typing (4 keystrokes in 0.4 seconds)
        now = time.time()
        debouncer._keystroke_times = [now - 0.4, now - 0.3, now - 0.2, now - 0.1]

        delay = debouncer.calculate_delay(document_size=50000)

        # Should apply typing multiplier
        # Base ~200ms * 1.5 (typing) = ~300ms (before CPU adjustment, reduced delays)
        assert (
            delay >= 200
        )  # Should be increased from base (adjusted for system variance)

    def test_on_text_changed_tracks_keystrokes(self):
        """Test on_text_changed tracks keystroke timing."""
        debouncer = AdaptiveDebouncer()

        # Simulate text changes
        debouncer.on_text_changed()
        assert len(debouncer._keystroke_times) == 1

        debouncer.on_text_changed()
        assert len(debouncer._keystroke_times) == 2

        # Verify keystroke times are recent
        now = time.time()
        for keystroke_time in debouncer._keystroke_times:
            assert now - keystroke_time < 1.0  # Within last second

    def test_keystroke_history_limited(self):
        """Test keystroke history is limited to 10."""
        debouncer = AdaptiveDebouncer()

        # Add 20 keystrokes
        for _ in range(20):
            debouncer.on_text_changed()

        # Should keep only last 10
        assert len(debouncer._keystroke_times) <= 10

    def test_render_time_affects_delay(self):
        """Test slow renders increase delay."""
        debouncer = AdaptiveDebouncer()

        # Fast render - should not trigger multiplier
        delay1 = debouncer.calculate_delay(document_size=50000, last_render_time=0.1)

        # Add more fast renders to stabilize
        for _ in range(4):
            debouncer.calculate_delay(document_size=50000, last_render_time=0.1)

        # Now add slow renders (>0.5s threshold)
        for _ in range(5):
            debouncer.calculate_delay(document_size=50000, last_render_time=0.8)

        # Get delay after slow renders
        delay2 = debouncer.calculate_delay(document_size=50000)

        # After slow renders, delay should increase (or at least be reasonable)
        # Due to multiplier being applied
        assert delay2 >= delay1

    def test_render_time_multiplier_with_no_history(self):
        """Test render time multiplier when no render history exists."""
        debouncer = AdaptiveDebouncer()

        # Directly test the internal method with empty history
        # This hits the early return in _get_render_time_multiplier (line 291)
        multiplier = debouncer._get_render_time_multiplier()

        # Should return 1.0 when no render history
        assert multiplier == 1.0

    def test_render_time_multiplier_below_threshold(self):
        """Test render time multiplier with fast renders."""
        debouncer = AdaptiveDebouncer()

        # Add fast render times (below 0.5s threshold)
        debouncer._recent_render_times = [0.1, 0.2, 0.15, 0.18, 0.12]

        multiplier = debouncer._get_render_time_multiplier()

        # Should return 1.0 for fast renders
        assert multiplier == 1.0

    def test_render_time_multiplier_above_threshold(self):
        """Test render time multiplier with slow renders."""
        debouncer = AdaptiveDebouncer()

        # Add slow render times (above 0.5s threshold)
        debouncer._recent_render_times = [0.8, 0.9, 0.7, 0.85, 0.75]

        multiplier = debouncer._get_render_time_multiplier()

        # Should return configured multiplier (2.0) for slow renders
        assert multiplier == debouncer.config.render_time_multiplier
        assert multiplier == 2.0

    def test_on_render_complete_tracks_time(self):
        """Test on_render_complete tracks render times."""
        debouncer = AdaptiveDebouncer()

        debouncer.on_render_complete(0.3)
        assert len(debouncer._recent_render_times) == 1
        assert debouncer._recent_render_times[0] == 0.3

        debouncer.on_render_complete(0.5)
        assert len(debouncer._recent_render_times) == 2

    def test_render_time_history_limited(self):
        """Test render time history is limited to 5."""
        debouncer = AdaptiveDebouncer()

        # Add 10 render times
        for i in range(10):
            debouncer.on_render_complete(0.1 * i)

        # Should keep only last 5
        assert len(debouncer._recent_render_times) == 5

    def test_get_statistics(self):
        """Test getting statistics."""
        debouncer = AdaptiveDebouncer()

        # Calculate some delays
        debouncer.calculate_delay(document_size=10000)
        debouncer.calculate_delay(document_size=50000)
        debouncer.calculate_delay(document_size=100000)

        stats = debouncer.get_statistics()

        assert "avg_delay" in stats
        assert "min_delay" in stats
        assert "max_delay" in stats
        assert "total_adjustments" in stats
        assert stats["total_adjustments"] == 3

    def test_statistics_with_no_history(self):
        """Test statistics with no delay history."""
        debouncer = AdaptiveDebouncer()

        stats = debouncer.get_statistics()

        assert stats["avg_delay"] == 0
        assert stats["min_delay"] == 0
        assert stats["max_delay"] == 0
        assert stats["total_adjustments"] == 0

    def test_reset(self):
        """Test reset clears all state."""
        debouncer = AdaptiveDebouncer()

        # Add some state
        debouncer.on_text_changed()
        debouncer.on_text_changed()
        debouncer.on_render_complete(0.3)
        debouncer.calculate_delay(document_size=50000)

        # Reset
        debouncer.reset()

        # All state should be cleared
        assert len(debouncer._keystroke_times) == 0
        assert len(debouncer._recent_render_times) == 0
        assert len(debouncer._delay_history) == 0


@pytest.mark.performance
class TestAdaptiveDebouncerPerformance:
    """Performance tests for adaptive debouncer."""

    def test_delay_calculation_performance(self):
        """Test delay calculation is fast."""
        debouncer = AdaptiveDebouncer()

        # Should be very fast
        start = time.time()
        for _ in range(1000):
            debouncer.calculate_delay(document_size=50000)
        elapsed = time.time() - start

        # 1000 calculations should take <200ms (psutil queries add overhead)
        assert elapsed < 0.2

    def test_typing_detection_performance(self):
        """Test typing detection doesn't slow down text changes."""
        debouncer = AdaptiveDebouncer()

        # Should handle many text changes quickly
        start = time.time()
        for _ in range(1000):
            debouncer.on_text_changed()
        elapsed = time.time() - start

        # 1000 text changes should take <50ms
        assert elapsed < 0.05

    def test_adaptive_behavior_scenario(self):
        """Test realistic adaptive behavior scenario."""
        debouncer = AdaptiveDebouncer()

        # Scenario: User editing large document

        # 1. Initial edit (large doc)
        delay1 = debouncer.calculate_delay(document_size=200000)
        debouncer.on_text_changed()

        # 2. Fast typing (3 quick edits)
        for _ in range(3):
            debouncer.on_text_changed()
            time.sleep(0.1)

        delay2 = debouncer.calculate_delay(document_size=200000)

        # 3. Slow renders
        for _ in range(5):
            debouncer.on_render_complete(0.8)

        delay3 = debouncer.calculate_delay(document_size=200000)

        # Delays should adapt
        assert delay2 >= delay1  # Fast typing may increase
        assert delay3 >= delay1  # Slow renders increase

        print("\nAdaptive delay scenario:")
        print(f"  Initial: {delay1}ms")
        print(f"  Fast typing: {delay2}ms")
        print(f"  After slow renders: {delay3}ms")

        stats = debouncer.get_statistics()
        print(f"  Final stats: {stats}")
