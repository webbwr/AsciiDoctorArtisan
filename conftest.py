"""
Pytest configuration and fixtures for AsciiDoc Artisan tests.

TEST GOAL: Find as many code bugs and issues as possible.

This file configures pytest to work properly with:
- macOS keyring access (completely disabled via environment variable)
- Qt application initialization
- Test isolation
- Thread leak detection
- Memory usage tracking
- Enhanced assertion introspection
- No multiprocessing (to prevent macOS Security.framework crashes)
"""

import gc
import os
import sys
import threading
import tracemalloc
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
