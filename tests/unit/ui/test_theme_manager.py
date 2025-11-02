"""Tests for ui.theme_manager module."""

import pytest
from PySide6.QtWidgets import QMainWindow


@pytest.fixture
def main_window(qapp):
    from unittest.mock import Mock
    window = QMainWindow()
    # ThemeManager needs _settings attribute with dark_mode property
    window._settings = Mock()
    window._settings.dark_mode = False
    return window


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
            manager.apply_theme()  # No arguments - reads from settings
            # Should not raise exception

    def test_css_caching(self, main_window):
        """Test that CSS is cached and reused on subsequent calls."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        manager = ThemeManager(main_window)

        # Initial state: caches should be empty
        assert manager._cached_dark_css is None
        assert manager._cached_light_css is None

        # Get light mode CSS (dark_mode = False)
        css1 = manager.get_preview_css()
        assert css1 is not None
        assert len(css1) > 0
        assert "background:#ffffff" in css1  # Light mode background

        # Cache should be populated for light mode only
        assert manager._cached_light_css is not None
        assert manager._cached_dark_css is None

        # Second call should return same cached instance
        css2 = manager.get_preview_css()
        assert css2 is css1  # Same object (cached)

        # Switch to dark mode
        main_window._settings.dark_mode = True

        # Get dark mode CSS
        css3 = manager.get_preview_css()
        assert css3 is not None
        assert len(css3) > 0
        assert "background:#1e1e1e" in css3  # Dark mode background

        # Both caches should now be populated
        assert manager._cached_light_css is not None
        assert manager._cached_dark_css is not None

        # Fourth call (still dark mode) should return cached dark CSS
        css4 = manager.get_preview_css()
        assert css4 is css3  # Same object (cached)

        # Switch back to light mode
        main_window._settings.dark_mode = False

        # Should return cached light CSS (not regenerate)
        css5 = manager.get_preview_css()
        assert css5 is css1  # Same object as first call (still cached)
