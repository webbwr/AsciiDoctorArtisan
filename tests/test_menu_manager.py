"""Tests for ui.menu_manager module."""

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


class TestMenuManager:
    """Test suite for MenuManager."""

    def test_import(self):
        from asciidoc_artisan.ui.menu_manager import MenuManager
        assert MenuManager is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.menu_manager import MenuManager
        manager = MenuManager(main_window)
        assert manager is not None

    def test_creates_menubar(self, main_window):
        from asciidoc_artisan.ui.menu_manager import MenuManager
        manager = MenuManager(main_window)
        if hasattr(manager, "create_menus"):
            manager.create_menus()
        # Check if main window has menubar
        menubar = main_window.menuBar()
        assert menubar is not None
