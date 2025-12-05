"""
E2E Test Configuration and Fixtures

Provides shared fixtures for end-to-end integration tests using pytest-bdd.
"""

from pathlib import Path
from typing import Generator

import pytest
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from asciidoc_artisan.ui.main_window import AsciiDocEditor


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """
    Provide QApplication instance for the test session.

    Note: This is session-scoped to avoid creating multiple QApplication instances.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def app(qtbot: QtBot, qapp: QApplication, tmp_path: Path, monkeypatch) -> Generator[AsciiDocEditor, None, None]:
    """
    Launch application for E2E testing with isolated settings.

    Provides a fully initialized AsciiDocEditor with all managers and workers.
    Uses temporary settings file to avoid modifying user's actual settings.

    Args:
        qtbot: pytest-qt fixture for Qt testing
        qapp: QApplication instance
        tmp_path: pytest temporary directory for test isolation
        monkeypatch: pytest monkeypatch for settings path override

    Yields:
        AsciiDocEditor: Initialized and displayed main window

    Example:
        def test_window_title(app):
            assert "AsciiDoc Artisan" in app.windowTitle()
    """
    # Create temp settings directory for test isolation
    temp_settings_dir = tmp_path / "test_settings"
    temp_settings_dir.mkdir(parents=True, exist_ok=True)
    temp_settings_file = temp_settings_dir / "AsciiDocArtisan.json"

    # Monkey-patch SettingsManager to use temp settings file
    from asciidoc_artisan.ui.settings_manager import SettingsManager

    def temp_get_settings_path(self) -> Path:
        """Return temporary settings path for testing."""
        return temp_settings_file

    monkeypatch.setattr(SettingsManager, "get_settings_path", temp_get_settings_path)

    # Create app with temp settings
    window = AsciiDocEditor()

    # Disable telemetry opt-in dialog for E2E tests (prevents QTimer issues)
    window._settings.telemetry_opt_in_shown = True
    window._settings.telemetry_enabled = False

    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window, timeout=5000)

    yield window

    # Cleanup
    window.close()


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """
    Create temporary workspace for file operations.

    Provides an isolated directory for creating and manipulating test files.
    Automatically cleaned up after test completion.

    Args:
        tmp_path: pytest tmp_path fixture

    Returns:
        Path: Temporary workspace directory

    Example:
        def test_save_file(temp_workspace):
            file = temp_workspace / "test.adoc"
            file.write_text("= Test")
            assert file.exists()
    """
    workspace = tmp_path / "test_workspace"
    workspace.mkdir(exist_ok=True)
    return workspace


@pytest.fixture
def sample_document(temp_workspace: Path) -> Path:
    """
    Create sample AsciiDoc document for testing.

    Provides a pre-created AsciiDoc file with basic content.

    Args:
        temp_workspace: Temporary workspace directory

    Returns:
        Path: Path to sample document

    Example:
        def test_open_document(app, sample_document):
            app.open_file(str(sample_document))
            assert sample_document.name in app.windowTitle()
    """
    doc = temp_workspace / "sample.adoc"
    content = """= Sample Document

This is a sample AsciiDoc document for testing.

== Section 1

Some content here.

== Section 2

More content here.
"""
    doc.write_text(content)
    return doc


@pytest.fixture
def git_repo(temp_workspace: Path) -> Path:
    """
    Create a Git repository for testing Git operations.

    Initializes a Git repository in the workspace with initial commit.

    Args:
        temp_workspace: Temporary workspace directory

    Returns:
        Path: Path to Git repository root

    Example:
        def test_git_status(app, git_repo):
            os.chdir(git_repo)
            # Test Git operations
    """
    import subprocess

    # Initialize Git repo
    subprocess.run(
        ["git", "init"],
        cwd=temp_workspace,
        capture_output=True,
        check=True,
    )

    # Configure Git
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_workspace,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_workspace,
        capture_output=True,
        check=True,
    )

    # Create initial commit
    readme = temp_workspace / "README.md"
    readme.write_text("# Test Repository\n")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=temp_workspace,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=temp_workspace,
        capture_output=True,
        check=True,
    )

    return temp_workspace


@pytest.fixture
def sample_content() -> str:
    """
    Provide sample AsciiDoc content for testing.

    Returns:
        str: Sample AsciiDoc content

    Example:
        def test_editor_content(app, sample_content):
            app.editor.setPlainText(sample_content)
            assert "Sample Document" in app.editor.toPlainText()
    """
    return """= Sample Document
Author Name
v1.0, 2025-11-20

== Introduction

This is a sample document.

== Features

* Feature 1
* Feature 2
* Feature 3

== Conclusion

Thank you for reading.
"""


# pytest-bdd plugin registered in root conftest.py
