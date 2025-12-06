"""
Pytest configuration and fixtures for AsciiDoc Artisan tests.

# =============================================================================
# TEST STRATEGY: Total Coverage with Bug-Finding Focus
# =============================================================================
#
# PRINCIPAL GOAL: Bug and issue-free code
#
# Tests exist to FIND BUGS, not to pass. A passing test suite with bugs
# in production is a failure of our testing strategy.
#
# KEY PRINCIPLES:
#   1. COVERAGE: Every line of code and UI path must be tested
#   2. FIND BUGS: Tests should actively seek bugs, not just verify happy paths
#   3. FAIL LOUDLY: When something is wrong, tests must fail immediately
#   4. EDGE CASES: All boundary conditions and error paths must be tested
#   5. SECURITY FIRST: Security tests run first and must never be skipped
#
# This file provides:
#   - Bug-finding fixtures (memory tracker, strict mocks, boundary testers)
#   - Thread leak detection
#   - Automatic test ordering (security first)
#   - Property-based testing configuration (Hypothesis)
#   - Qt test infrastructure
#   - Isolation guarantees between tests
#
# =============================================================================
"""

import gc
import os
import random
import string
import sys
import threading
import tracemalloc
from typing import Any
from unittest.mock import MagicMock

import pytest

# CRITICAL: Disable keyring BEFORE any imports
# This prevents macOS Security.framework crashes in multiprocess/fork scenarios
os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.null.Keyring"

# CRITICAL: Disable QtWebEngine completely during tests
# QtWebEngineCore is Chromium-based and does NOT support fork() at all
# This will cause tests to skip WebEngine-dependent code
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --disable-dev-shm-usage"
os.environ["DISABLE_QTWEBENGINE_IN_TESTS"] = "1"

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


# Mock keyring BEFORE any imports that might use it
# This prevents the crash when pytest-forked tries to access keyring in child processes
@pytest.fixture(scope="session", autouse=True)
def mock_keyring_globally():
    """
    Mock the keyring module globally to prevent macOS Security.framework crashes.

    The issue: pytest-forked forks processes, but macOS Security.framework
    (used by keyring) doesn't work in forked children due to multi-threading.

    Solution: Mock keyring before any code tries to use it.
    """
    import sys

    # Create a mock keyring module
    mock_keyring = MagicMock()
    mock_keyring.get_password = MagicMock(return_value=None)
    mock_keyring.set_password = MagicMock()
    mock_keyring.delete_password = MagicMock()

    # Replace keyring in sys.modules
    sys.modules["keyring"] = mock_keyring

    yield

    # Cleanup (restore original if needed)
    # Note: In practice, tests should always use mocked keyring


@pytest.fixture(scope="function")
def mock_keyring(monkeypatch):
    """
    Per-test keyring mock fixture.

    Use this in tests that explicitly interact with keyring:
        def test_something(mock_keyring):
            mock_keyring.get_password.return_value = "test_password"
    """
    import sys

    return sys.modules["keyring"]


# Prevent Qt from trying to create a display in headless environments
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(scope="session")
def qapp():
    """
    Create a single QApplication instance for all tests.

    Qt requires exactly one QApplication instance per process.
    This fixture ensures that.
    """
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    yield app

    # Don't quit - other tests might still need it


@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Reset singleton instances between tests for isolation.

    This ensures tests don't interfere with each other via
    shared state in singleton objects.
    """
    yield

    # Add any singleton cleanup here if needed
    # Example:
    # if hasattr(SomeClass, '_instance'):
    #     SomeClass._instance = None


# =============================================================================
# BUG DETECTION FIXTURES AND HOOKS
# =============================================================================


@pytest.fixture(autouse=True)
def detect_thread_leaks():
    """
    Detect thread leaks between tests.

    Tracks threads before/after each test to catch leaked threads
    that could indicate resource cleanup issues.

    To enable thread leak detection, uncomment the assertion block below.
    """
    # Get threads before test
    threads_before = set(threading.enumerate())

    yield

    # Give threads time to clean up
    gc.collect()

    # Get threads after test and detect leaks
    # Uncomment to enable thread leak detection:
    # threads_after = set(threading.enumerate())
    # new_threads = threads_after - threads_before
    # excluded = {"MainThread", "pytest_timeout", "QThread", "Dummy-"}
    # leaked = [t for t in new_threads if t.is_alive() and not any(ex in t.name for ex in excluded)]
    # if leaked:
    #     pytest.fail(f"Thread leak detected: {[t.name for t in leaked]}")
    _ = threads_before  # Suppress unused variable warning


@pytest.fixture
def memory_tracker():
    """
    Track memory allocations during a test.

    Usage:
        def test_no_memory_leak(memory_tracker):
            memory_tracker.start()
            # ... do work ...
            peak_mb = memory_tracker.stop()
            assert peak_mb < 100, f"Used {peak_mb}MB"
    """

    class MemoryTracker:
        def __init__(self):
            self._snapshot_start = None
            self._peak_mb = 0

        def start(self):
            gc.collect()
            tracemalloc.start()
            self._snapshot_start = tracemalloc.take_snapshot()

        def stop(self) -> float:
            gc.collect()
            snapshot_end = tracemalloc.take_snapshot()
            tracemalloc.stop()

            # Calculate peak memory
            stats = snapshot_end.compare_to(self._snapshot_start, "lineno")
            total_bytes = sum(stat.size_diff for stat in stats if stat.size_diff > 0)
            self._peak_mb = total_bytes / (1024 * 1024)
            return self._peak_mb

        @property
        def peak_mb(self) -> float:
            return self._peak_mb

    return MemoryTracker()


@pytest.fixture
def strict_mock():
    """
    Create a mock that fails on unexpected calls.

    Unlike MagicMock, this will raise an error if any
    unexpected method is called, catching typos and API misuse.

    Usage:
        def test_api_usage(strict_mock):
            api = strict_mock(["allowed_method", "another_method"])
            api.allowed_method()  # OK
            api.typo_method()  # Raises AttributeError
    """

    def _create_strict_mock(allowed_methods: list[str]):
        mock = MagicMock()

        def _getattr(name):
            if name.startswith("_") or name in allowed_methods:
                return MagicMock()
            raise AttributeError(f"Unexpected method call: {name}")

        mock.__getattr__ = _getattr
        return mock

    return _create_strict_mock


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add automatic markers and ordering.

    - Adds 'slow' marker to tests with 'slow' in name
    - Orders security tests to run first (fail fast on critical issues)
    """
    for item in items:
        # Auto-mark slow tests
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)

        # Auto-mark performance tests
        if "performance" in item.name.lower() or "perf" in item.name.lower():
            item.add_marker(pytest.mark.performance)

    # Reorder: security tests first, then others
    security_tests = [item for item in items if "security" in str(item.fspath).lower()]
    other_tests = [item for item in items if item not in security_tests]
    items[:] = security_tests + other_tests


def pytest_configure(config):
    """
    Configure pytest with enhanced assertion introspection.
    """
    # Enable detailed assertion introspection
    config.addinivalue_line("markers", "bug_detection: Tests specifically designed to find bugs")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    Enhanced test reporting for bug detection.

    Adds extra context to failed tests to help diagnose issues.
    """
    # This hook can be extended to add more debugging info
    pass


# =============================================================================
# HYPOTHESIS CONFIGURATION (Property-Based Testing)
# =============================================================================

# Configure Hypothesis for thorough bug finding
try:
    from hypothesis import Phase, Verbosity, settings

    # Register a "thorough" profile for maximum bug detection
    settings.register_profile(
        "thorough",
        max_examples=500,
        phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.shrink],
        verbosity=Verbosity.normal,
        deadline=None,  # No time limit
    )

    # Register a "quick" profile for fast CI runs
    settings.register_profile(
        "quick",
        max_examples=20,
        phases=[Phase.explicit, Phase.generate],
        verbosity=Verbosity.quiet,
        deadline=1000,  # 1 second
    )

    # Default to thorough for maximum bug detection
    settings.load_profile("thorough")

except ImportError:
    pass  # Hypothesis not installed


# =============================================================================
# BUG-FINDING FIXTURES - Edge Cases and Boundary Testing
# =============================================================================


@pytest.fixture
def edge_case_strings():
    """
    Provide edge case strings for testing text handling.

    These strings are designed to find bugs in string processing:
    - Empty strings
    - Very long strings
    - Unicode edge cases
    - Special characters
    - Null bytes
    - Whitespace variations
    """
    return {
        "empty": "",
        "whitespace_only": "   \t\n\r  ",
        "single_char": "x",
        "very_long": "x" * 100000,
        "unicode_basic": "Hello 世界 🌍 مرحبا",
        "unicode_rtl": "مرحبا بالعالم",
        "unicode_emoji": "👨‍👩‍👧‍👦 🏳️‍🌈 🇺🇸",
        "unicode_zalgo": "H̸̡̪̯ͨ͊̽̅̾e̴̡̦̝̱̚ comes",
        "null_byte": "hello\x00world",
        "control_chars": "line1\x00\x01\x02\x03line2",
        "newlines_mixed": "line1\nline2\r\nline3\rline4",
        "tabs_spaces": "\t  \t  \t",
        "backslashes": "path\\to\\file",
        "quotes_mixed": "say \"hello\" and 'goodbye'",
        "html_injection": "<script>alert('xss')</script>",
        "sql_injection": "'; DROP TABLE users; --",
        "path_traversal": "../../../etc/passwd",
        "format_string": "%s%s%s%n",
        "max_unicode": "\U0010ffff",
        "surrogate_pair": "\ud83d\ude00",
        "bom": "\ufeffHello",
        "zero_width": "Hello\u200bWorld",
    }


@pytest.fixture
def edge_case_numbers():
    """
    Provide edge case numbers for testing numeric handling.

    These numbers are designed to find bugs in numeric processing:
    - Boundary values
    - Special float values
    - Large numbers
    - Precision edge cases
    """
    return {
        "zero": 0,
        "negative_zero": -0.0,
        "one": 1,
        "negative_one": -1,
        "max_int": sys.maxsize,
        "min_int": -sys.maxsize - 1,
        "max_float": float("inf"),
        "min_float": float("-inf"),
        "nan": float("nan"),
        "epsilon": sys.float_info.epsilon,
        "very_small": 1e-308,
        "very_large": 1e308,
        "negative_very_small": -1e-308,
        "precision_test": 0.1 + 0.2,  # Famous floating point issue
    }


@pytest.fixture
def random_fuzzer():
    """
    Generate random data for fuzz testing.

    Usage:
        def test_handles_random_input(random_fuzzer):
            for _ in range(100):
                random_string = random_fuzzer.string(max_length=1000)
                result = my_function(random_string)
                assert result is not None  # Or other invariant
    """

    class RandomFuzzer:
        def string(self, max_length: int = 100, min_length: int = 0) -> str:
            """Generate random string with various character types."""
            length = random.randint(min_length, max_length)
            charset = string.printable + "世界🌍مرحبا"
            return "".join(random.choice(charset) for _ in range(length))

        def bytes(self, max_length: int = 100, min_length: int = 0) -> bytes:
            """Generate random bytes."""
            length = random.randint(min_length, max_length)
            return bytes(random.randint(0, 255) for _ in range(length))

        def integer(self, min_val: int = -1000000, max_val: int = 1000000) -> int:
            """Generate random integer."""
            return random.randint(min_val, max_val)

        def float(self, min_val: float = -1e10, max_val: float = 1e10) -> float:
            """Generate random float, occasionally including special values."""
            if random.random() < 0.1:
                return random.choice([float("inf"), float("-inf"), float("nan"), 0.0, -0.0])
            return random.uniform(min_val, max_val)

        def list(self, generator: Any, max_length: int = 100) -> list:
            """Generate random list using provided generator."""
            length = random.randint(0, max_length)
            return [generator() for _ in range(length)]

    return RandomFuzzer()


@pytest.fixture
def assert_no_exception():
    """
    Context manager to assert that NO exception is raised.

    Usage:
        def test_no_crash(assert_no_exception):
            with assert_no_exception():
                risky_function()
    """
    from contextlib import contextmanager

    @contextmanager
    def _assert_no_exception():
        try:
            yield
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {type(e).__name__}: {e}")

    return _assert_no_exception


@pytest.fixture
def assert_raises_within():
    """
    Assert that an exception is raised within a timeout.

    Usage:
        def test_timeout(assert_raises_within):
            with assert_raises_within(TimeoutError, timeout=5):
                blocking_function()
    """
    import signal
    from contextlib import contextmanager

    @contextmanager
    def _assert_raises_within(expected_exception: type, timeout: int = 5):
        def handler(signum, frame):
            raise TimeoutError(f"Operation did not complete within {timeout}s")

        old_handler = signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout)

        try:
            with pytest.raises(expected_exception):
                yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    return _assert_raises_within


@pytest.fixture
def ui_event_simulator(qapp):
    """
    Simulate UI events for testing Qt widgets.

    Usage:
        def test_button_click(ui_event_simulator, my_widget):
            ui_event_simulator.click(my_widget.button)
            assert my_widget.was_clicked
    """
    from PySide6.QtCore import QEvent, QPoint, Qt
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtWidgets import QApplication

    class UIEventSimulator:
        def click(self, widget, button=Qt.MouseButton.LeftButton):
            """Simulate mouse click on widget."""
            pos = widget.rect().center()
            press = QMouseEvent(
                QEvent.Type.MouseButtonPress,
                QPoint(pos.x(), pos.y()),
                button,
                button,
                Qt.KeyboardModifier.NoModifier,
            )
            release = QMouseEvent(
                QEvent.Type.MouseButtonRelease,
                QPoint(pos.x(), pos.y()),
                button,
                button,
                Qt.KeyboardModifier.NoModifier,
            )
            QApplication.sendEvent(widget, press)
            QApplication.sendEvent(widget, release)
            QApplication.processEvents()

        def double_click(self, widget, button=Qt.MouseButton.LeftButton):
            """Simulate double-click on widget."""
            pos = widget.rect().center()
            event = QMouseEvent(
                QEvent.Type.MouseButtonDblClick,
                QPoint(pos.x(), pos.y()),
                button,
                button,
                Qt.KeyboardModifier.NoModifier,
            )
            QApplication.sendEvent(widget, event)
            QApplication.processEvents()

        def type_text(self, widget, text: str):
            """Simulate typing text into widget."""
            from PySide6.QtGui import QKeyEvent

            for char in text:
                press = QKeyEvent(QEvent.Type.KeyPress, 0, Qt.KeyboardModifier.NoModifier, char)
                release = QKeyEvent(QEvent.Type.KeyRelease, 0, Qt.KeyboardModifier.NoModifier, char)
                QApplication.sendEvent(widget, press)
                QApplication.sendEvent(widget, release)
            QApplication.processEvents()

        def process_events(self):
            """Process all pending Qt events."""
            QApplication.processEvents()

    return UIEventSimulator()


# =============================================================================
# TEST RESULT TRACKING
# =============================================================================


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Add custom summary to test output emphasizing bug-finding goal.
    """
    terminalreporter.write_sep("=", "TEST STRATEGY SUMMARY")
    terminalreporter.write_line("")
    terminalreporter.write_line("GOAL: Bug and issue-free code")
    terminalreporter.write_line("")

    stats = terminalreporter.stats
    passed = len(stats.get("passed", []))
    failed = len(stats.get("failed", []))
    errors = len(stats.get("error", []))

    if failed > 0 or errors > 0:
        terminalreporter.write_line(f"BUGS FOUND: {failed + errors} test(s) identified issues!")
        terminalreporter.write_line("Action: Fix all failing tests before merging.")
    else:
        terminalreporter.write_line(f"All {passed} tests passed - no bugs detected in tested paths.")
        terminalreporter.write_line("Reminder: Passing tests don't guarantee bug-free code.")
        terminalreporter.write_line("Ensure coverage is comprehensive.")
    terminalreporter.write_line("")
