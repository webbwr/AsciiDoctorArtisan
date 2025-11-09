"""
Pytest configuration and fixtures for AsciiDoc Artisan tests.

This file configures pytest to work properly with:
- macOS keyring access (completely disabled via environment variable)
- Qt application initialization
- Test isolation
- No multiprocessing (to prevent macOS Security.framework crashes)
"""

import os
import sys
from unittest.mock import MagicMock

import pytest

# CRITICAL: Disable keyring BEFORE any imports
# This prevents macOS Security.framework crashes in multiprocess/fork scenarios
os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.null.Keyring"

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
