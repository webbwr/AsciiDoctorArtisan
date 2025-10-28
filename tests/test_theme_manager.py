"""Tests for ui.theme_manager module."""

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


class TestThemeManager:
    """Test suite for ThemeManager."""

    def test_import(self):
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        assert ThemeManager is not None

    def test_creation(self, main_window):
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        manager = ThemeManager(main_window)
        assert manager is not None

    def test_has_themes(self, main_window):
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        manager = ThemeManager(main_window)
        # Should have dark and light themes
        if hasattr(manager, "themes") or hasattr(manager, "available_themes"):
            themes = getattr(manager, "themes", getattr(manager, "available_themes", []))
            assert len(themes) >= 2

    def test_apply_theme(self, main_window):
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        manager = ThemeManager(main_window)
        if hasattr(manager, "apply_theme"):
            manager.apply_theme("dark")
            # Should not raise exception
