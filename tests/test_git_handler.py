"""Tests for ui.git_handler module."""

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow


@pytest.fixture
def qapp():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window(qapp):
    return QMainWindow()


class TestGitHandler:
    """Test suite for GitHandler."""

    def test_import(self):
        from asciidoc_artisan.ui.git_handler import GitHandler
        assert GitHandler is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.git_handler import GitHandler
        handler = GitHandler(main_window)
        assert handler is not None

    def test_has_git_methods(self, main_window):
        from asciidoc_artisan.ui.git_handler import GitHandler
        handler = GitHandler(main_window)
        git_methods = [m for m in dir(handler) if any(x in m.lower() for x in ["commit", "push", "pull", "git"])]
        assert len(git_methods) > 0
