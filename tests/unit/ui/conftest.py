"""
UI-specific pytest configuration and fixtures.

Provides Qt cleanup fixtures to prevent modal dialog test pollution.

Key Fixtures:
- cleanup_qt_modal_dialogs: Autouse fixture to close modal dialogs between tests
- mock_qmessagebox: Global QMessageBox mocking to prevent blocking
- cleanup_qt_event_loop: Autouse fixture to reset Qt event loop state

This file addresses GitHub issue #28: Qt modal dialog test pollution.
"""

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget


@pytest.fixture(autouse=True)
def cleanup_qt_modal_dialogs(qtbot):
    """
    Ensure all Qt modal dialogs are closed between tests.

    This prevents test pollution where modal dialogs from one test
    leave the Qt event loop in a bad state for subsequent tests.

    Runs automatically for all UI tests (autouse=True).
    """
    yield

    # Close all modal dialogs after test completes
    app = QApplication.instance()
    if app:
        # Close all top-level widgets that are modal
        for widget in app.topLevelWidgets():
            if widget.isModal():
                widget.close()
                widget.deleteLater()

        # Process pending events to ensure cleanup completes
        app.processEvents()


class MockParentWidget(QWidget):
    """
    Mock parent widget for dialog tests.

    Provides a real QWidget that can be used as a dialog parent,
    solving the PySide6 type validation issue where MagicMock
    instances are rejected by Qt's C++ bindings.

    Tracks method calls for verification in tests.

    Attributes:
        refresh_from_settings_called: Whether _refresh_from_settings was called
        status_bar_updates: List of status bar messages
        model_changes: List of model changes
    """

    def __init__(self):
        super().__init__()
        self.refresh_from_settings_called = False
        self.status_bar_updates = []
        self.model_changes = []

    def _refresh_from_settings(self):
        """Mock implementation of refresh_from_settings."""
        self.refresh_from_settings_called = True

    def _update_ai_status_bar(self, message: str = ""):
        """Mock implementation of update_status_bar."""
        self.status_bar_updates.append(message)

    def on_model_changed(self, model: str):
        """Mock implementation of model change handler."""
        self.model_changes.append(model)


@pytest.fixture
def mock_parent_widget(qtbot):
    """
    Provides a mock parent widget for dialog tests.

    Returns a real QWidget instance with trackable methods,
    avoiding PySide6's C++ type validation issues with mocks.

    Automatically cleaned up after test completion.

    Usage:
        def test_dialog_with_parent(mock_parent_widget):
            dialog = SomeDialog(parent=mock_parent_widget)
            dialog.accept()
            assert mock_parent_widget.refresh_from_settings_called
    """
    parent = MockParentWidget()
    yield parent
    parent.deleteLater()


@pytest.fixture(autouse=True)
def cleanup_qt_event_loop(qtbot):
    """
    Reset Qt event loop state between tests.

    Ensures the event loop is in a clean state for each test,
    preventing state leakage from modal dialogs.
    """
    yield

    # Process all pending events
    app = QApplication.instance()
    if app:
        app.processEvents()


@pytest.fixture
def mock_qmessagebox():
    """
    Mock QMessageBox to prevent modal dialogs from blocking tests.

    Usage:
        def test_something(mock_qmessagebox):
            mock_qmessagebox.question.return_value = QMessageBox.Yes
            # ... test code that shows QMessageBox.question ...
    """
    with patch("PySide6.QtWidgets.QMessageBox") as mock:
        # Set up common return values
        mock.question = MagicMock(return_value=QMessageBox.StandardButton.Yes)
        mock.information = MagicMock(return_value=QMessageBox.StandardButton.Ok)
        mock.warning = MagicMock(return_value=QMessageBox.StandardButton.Ok)
        mock.critical = MagicMock(return_value=QMessageBox.StandardButton.Ok)

        # Allow instances to be created
        mock.return_value = MagicMock()
        mock.return_value.exec = MagicMock(return_value=QMessageBox.StandardButton.Ok)

        yield mock


@pytest.fixture(autouse=True, scope="function")
def reset_qt_application_state(qtbot):
    """
    Reset QApplication state between tests.

    Ensures application-level state (like quit requests) is reset.
    """
    yield

    # Clear any quit requests
    app = QApplication.instance()
    if app:
        # Reset application state flags
        app.setQuitOnLastWindowClosed(True)


@pytest.fixture
def isolated_event_loop(qtbot):
    """
    Provide an isolated Qt event loop for tests that need complete isolation.

    Usage:
        def test_something(isolated_event_loop):
            # Test runs in a fresh event loop context
            ...
    """
    app = QApplication.instance()

    # Clear event queue before test
    if app:
        app.processEvents()
        while app.hasPendingEvents():
            app.processEvents()

    yield

    # Clear event queue after test
    if app:
        app.processEvents()
        while app.hasPendingEvents():
            app.processEvents()


@pytest.fixture
def fast_ui_test_settings(tmp_path):
    """
    UI test settings optimized for speed.

    Disables all features that cause delays or external calls:
    - Telemetry dialogs
    - AI features
    - Git operations
    - Network calls
    """
    from asciidoc_artisan.core import Settings

    settings = Settings()

    # Prevent telemetry dialog
    settings.telemetry_opt_in_shown = True
    settings.telemetry_enabled = False
    settings.telemetry_session_id = None

    # Disable slow features
    settings.ollama_enabled = False
    settings.ollama_model = None
    settings.ai_conversion_enabled = False
    settings.ai_chat_enabled = False

    # Disable Git features
    settings.git_repo_path = None
    settings.git_auto_stage = False
    settings.git_auto_commit = False

    # Fast defaults
    settings.last_directory = str(tmp_path)
    settings.last_file = None
    settings.preview_update_delay = 0  # Instant preview updates

    return settings


@pytest.fixture(autouse=True)
def cleanup_widget_references(qtbot):
    """
    Clean up widget references to prevent memory leaks between tests.

    Deletes all widgets that have been scheduled for deletion.
    """
    yield

    app = QApplication.instance()
    if app:
        # Delete widgets scheduled for deletion
        app.sendPostedEvents(None, 0)  # QEvent.DeferredDelete = 0
        app.processEvents()


# ============================================================================
# Test Isolation Markers
# ============================================================================


def pytest_configure(config):
    """
    Register custom markers for test isolation.

    Markers:
    - @pytest.mark.requires_fresh_qt_state: Test needs clean Qt state
    - @pytest.mark.modal_dialog_test: Test involves modal dialogs
    """
    config.addinivalue_line(
        "markers",
        "requires_fresh_qt_state: Test requires clean Qt application state",
    )
    config.addinivalue_line("markers", "modal_dialog_test: Test involves modal dialogs (QMessageBox, etc.)")


def pytest_runtest_setup(item):
    """
    Setup hook for tests with special requirements.

    Tests marked with 'requires_fresh_qt_state' get extra cleanup.
    """
    if "requires_fresh_qt_state" in item.keywords:
        app = QApplication.instance()
        if app:
            # Extra thorough cleanup for tests that need it
            for widget in app.topLevelWidgets():
                widget.close()
                widget.deleteLater()
            app.processEvents()
