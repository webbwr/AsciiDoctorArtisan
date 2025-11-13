"""
Test utilities for performance optimization.

Provides helpers for:
- Reducing sleep times in tests
- Fast mocking patterns
- Performance measurement
"""

import time
from contextlib import contextmanager
from typing import Any, Callable
from unittest.mock import Mock

# Test mode sleep multiplier (reduce sleep times in tests)
TEST_SLEEP_MULTIPLIER = 0.1  # 10x faster


def fast_sleep(seconds: float) -> None:
    """
    Sleep for reduced time in tests.

    Uses TEST_SLEEP_MULTIPLIER to speed up tests while maintaining
    relative timing relationships.

    Args:
        seconds: Intended sleep duration

    Example:
        # Sleeps for 0.05s instead of 0.5s
        fast_sleep(0.5)
    """
    time.sleep(seconds * TEST_SLEEP_MULTIPLIER)


@contextmanager
def timing_context(name: str = "operation"):
    """
    Context manager for timing operations.

    Usage:
        with timing_context("my_operation"):
            # code to time
            pass
    """
    start = time.perf_counter()
    yield
    duration = time.perf_counter() - start
    print(f"{name} took {duration:.4f}s")


def create_mock_worker(
    worker_class: type, result_signal_name: str = "result_ready"
) -> Mock:
    """
    Create a mock worker with proper signal handling.

    Args:
        worker_class: The worker class to mock
        result_signal_name: Name of the result signal

    Returns:
        Mock worker instance with signals

    Example:
        worker = create_mock_worker(GitWorker, "command_result_ready")
        worker.start()
        worker.command_result_ready.emit.assert_called_once()
    """
    mock_worker = Mock(spec=worker_class)
    # Add signal mock
    signal_mock = Mock()
    setattr(mock_worker, result_signal_name, signal_mock)
    signal_mock.emit = Mock()
    signal_mock.connect = Mock()
    signal_mock.disconnect = Mock()
    return mock_worker


def skip_if_slow(test_func: Callable) -> Callable:
    """
    Decorator to skip slow tests based on environment variable.

    Usage:
        @skip_if_slow
        def test_long_running_operation():
            pass

    Run with: pytest  # runs all tests
    Run without slow: pytest -m "not slow"
    """
    import pytest

    return pytest.mark.slow(test_func)


class FastQtBot:
    """
    Wrapper around qtbot with optimized wait times.

    Reduces default timeouts for faster test execution.
    """

    def __init__(self, qtbot):
        self.qtbot = qtbot
        self.default_timeout = 500  # 500ms instead of default 5000ms

    def wait_signal(self, signal, timeout=None, **kwargs):
        """Wait for signal with reduced timeout."""
        timeout = timeout or self.default_timeout
        return self.qtbot.waitSignal(signal, timeout=timeout, **kwargs)

    def wait_until(self, callback, timeout=None, **kwargs):
        """Wait until callback returns True with reduced timeout."""
        timeout = timeout or self.default_timeout
        return self.qtbot.waitUntil(callback, timeout=timeout, **kwargs)

    def __getattr__(self, name):
        """Forward all other methods to qtbot."""
        return getattr(self.qtbot, name)


def assert_performance(duration: float, max_duration: float, operation: str = ""):
    """
    Assert that an operation completed within performance threshold.

    Args:
        duration: Actual duration in seconds
        max_duration: Maximum allowed duration in seconds
        operation: Description of the operation (for error messages)

    Raises:
        AssertionError: If duration exceeds max_duration

    Example:
        start = time.perf_counter()
        # ... do work ...
        duration = time.perf_counter() - start
        assert_performance(duration, 0.1, "file loading")
    """
    if duration > max_duration:
        raise AssertionError(
            f"{operation or 'Operation'} took {duration:.3f}s, expected <{max_duration:.3f}s"
        )


class PerformanceMonitor:
    """
    Monitor and track test performance metrics.

    Usage:
        monitor = PerformanceMonitor()
        monitor.start()
        # ... test code ...
        metrics = monitor.stop()
        assert metrics["duration"] < 1.0
    """

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.metrics = {}

    def start(self):
        """Start monitoring."""
        import psutil

        self.start_time = time.perf_counter()
        process = psutil.Process()
        self.metrics["start_memory_mb"] = process.memory_info().rss / 1024 / 1024

    def stop(self) -> dict[str, Any]:
        """
        Stop monitoring and return metrics.

        Returns:
            Dictionary with:
            - duration: Execution time in seconds
            - start_memory_mb: Memory at start in MB
            - end_memory_mb: Memory at end in MB
            - memory_delta_mb: Memory change in MB
        """
        import psutil

        self.end_time = time.perf_counter()
        process = psutil.Process()
        end_memory = process.memory_info().rss / 1024 / 1024

        self.metrics["end_memory_mb"] = end_memory
        self.metrics["memory_delta_mb"] = end_memory - self.metrics["start_memory_mb"]
        self.metrics["duration"] = self.end_time - self.start_time

        return self.metrics


def create_fast_settings(tmp_path):
    """
    Create test Settings with all slow features disabled.

    Optimized for fast test execution:
    - No telemetry
    - No AI features
    - No Git
    - No network calls

    Args:
        tmp_path: pytest tmp_path fixture

    Returns:
        Settings instance optimized for testing
    """
    from asciidoc_artisan.core import Settings

    settings = Settings()
    # Disable all slow/network features
    settings.telemetry_opt_in_shown = True
    settings.telemetry_enabled = False
    settings.telemetry_session_id = None
    settings.ollama_enabled = False
    settings.ollama_model = None
    settings.ai_conversion_enabled = False
    settings.ai_chat_enabled = False
    settings.claude_api_key = None
    settings.git_repo_path = None
    settings.last_directory = str(tmp_path)
    settings.last_file = None
    # Fast defaults
    settings.auto_save_enabled = False  # Don't trigger auto-save timers
    settings.preview_update_delay = 0  # Instant preview updates
    return settings
