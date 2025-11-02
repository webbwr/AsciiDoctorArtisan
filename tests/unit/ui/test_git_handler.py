"""Tests for ui.git_handler module."""

import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QMainWindow


@pytest.fixture
def main_window(qapp):
    return QMainWindow()


@pytest.fixture
def mock_managers(qapp):
    """Create mock settings_manager and status_manager for GitHandler."""
    settings_manager = Mock()
    status_manager = Mock()
    return settings_manager, status_manager


class TestGitHandler:
    """Test suite for GitHandler."""

    def test_import(self):
        from asciidoc_artisan.ui.git_handler import GitHandler
        assert GitHandler is not None

    def test_creation(self, main_window, mock_managers):
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers
        handler = GitHandler(main_window, settings_manager, status_manager)
        assert handler is not None

    def test_has_git_methods(self, main_window, mock_managers):
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers
        handler = GitHandler(main_window, settings_manager, status_manager)
        git_methods = [m for m in dir(handler) if any(x in m.lower() for x in ["commit", "push", "pull", "git"])]
        assert len(git_methods) > 0
