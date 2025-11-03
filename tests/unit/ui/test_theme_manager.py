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

    def test_css_constants(self, main_window):
        """Test that CSS constants are returned correctly for each theme."""
        from asciidoc_artisan.ui.theme_manager import (
            ThemeManager,
            DARK_MODE_CSS,
            LIGHT_MODE_CSS,
        )
        manager = ThemeManager(main_window)

        # Get light mode CSS (dark_mode = False)
        css1 = manager.get_preview_css()
        assert css1 is not None
        assert len(css1) > 0
        assert "background:#ffffff" in css1  # Light mode background
        assert css1 is LIGHT_MODE_CSS  # Should return module constant

        # Second call should return same constant
        css2 = manager.get_preview_css()
        assert css2 is css1  # Same object (constant)

        # Switch to dark mode
        main_window._settings.dark_mode = True

        # Get dark mode CSS
        css3 = manager.get_preview_css()
        assert css3 is not None
        assert len(css3) > 0
        assert "background:#1e1e1e" in css3  # Dark mode background
        assert css3 is DARK_MODE_CSS  # Should return module constant

        # Fourth call (still dark mode) should return same constant
        css4 = manager.get_preview_css()
        assert css4 is css3  # Same object (constant)

        # Switch back to light mode
        main_window._settings.dark_mode = False

        # Should return light mode constant
        css5 = manager.get_preview_css()
        assert css5 is css1  # Same object as first call (constant)

    def test_toggle_dark_mode_changes_setting(self, main_window):
        """Test toggle_dark_mode updates settings."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        manager = ThemeManager(main_window)
        main_window.dark_mode_act = Mock()
        main_window.dark_mode_act.isChecked.return_value = True
        main_window.preview_handler = Mock()
        main_window.update_preview = Mock()

        # Toggle to dark mode
        manager.toggle_dark_mode()

        assert main_window._settings.dark_mode is True
        main_window.preview_handler.clear_css_cache.assert_called_once()
        main_window.update_preview.assert_called_once()

    def test_apply_theme_dark_mode(self, main_window, qapp):
        """Test apply_theme applies dark palette."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)

        manager.apply_theme()

        # Dark mode should set dark palette
        palette = qapp.palette()
        # Window should be dark (not white)
        window_color = palette.color(palette.ColorRole.Window)
        assert window_color.red() < 100  # Dark color

    def test_apply_theme_light_mode(self, main_window, qapp):
        """Test apply_theme applies light palette."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        main_window._settings.dark_mode = False
        manager = ThemeManager(main_window)

        manager.apply_theme()

        # Light mode should reset to standard palette
        # Just verify it doesn't crash

    def test_label_colors_dark_mode(self, main_window):
        """Test labels are updated to white in dark mode."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        # Create mock labels
        main_window.editor_label = Mock()
        main_window.preview_label = Mock()
        main_window.chat_label = Mock()

        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)

        manager.apply_theme()

        # Labels should have white text
        main_window.editor_label.setStyleSheet.assert_called_with("color: white;")
        main_window.preview_label.setStyleSheet.assert_called_with("color: white;")
        main_window.chat_label.setStyleSheet.assert_called_with("color: white;")

    def test_label_colors_light_mode(self, main_window):
        """Test labels are updated to black in light mode."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        # Create mock labels
        main_window.editor_label = Mock()
        main_window.preview_label = Mock()
        main_window.chat_label = Mock()

        main_window._settings.dark_mode = False
        manager = ThemeManager(main_window)

        manager.apply_theme()

        # Labels should have black text
        main_window.editor_label.setStyleSheet.assert_called_with("color: black;")
        main_window.preview_label.setStyleSheet.assert_called_with("color: black;")
        main_window.chat_label.setStyleSheet.assert_called_with("color: black;")

    def test_chat_manager_dark_mode_update(self, main_window):
        """Test chat manager is updated when theme changes."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        # Create mock chat manager and panel
        chat_panel = Mock()
        chat_manager = Mock()
        chat_manager._chat_panel = chat_panel
        main_window.chat_manager = chat_manager

        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)

        manager.apply_theme()

        # Chat panel should be set to dark mode
        chat_panel.set_dark_mode.assert_called_once_with(True)

    def test_chat_manager_light_mode_update(self, main_window):
        """Test chat manager is updated to light mode."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        # Create mock chat manager and panel
        chat_panel = Mock()
        chat_manager = Mock()
        chat_manager._chat_panel = chat_panel
        main_window.chat_manager = chat_manager

        main_window._settings.dark_mode = False
        manager = ThemeManager(main_window)

        manager.apply_theme()

        # Chat panel should be set to light mode
        chat_panel.set_dark_mode.assert_called_once_with(False)

    def test_apply_theme_without_labels_no_crash(self, main_window):
        """Test apply_theme handles missing labels gracefully."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        # No labels set (editor_label, preview_label, chat_label don't exist)
        manager = ThemeManager(main_window)

        # Should not crash
        manager.apply_theme()

    def test_apply_theme_without_chat_manager_no_crash(self, main_window):
        """Test apply_theme handles missing chat_manager gracefully."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        # No chat_manager attribute
        manager = ThemeManager(main_window)

        # Should not crash
        manager.apply_theme()

    def test_dark_mode_css_contains_dark_colors(self):
        """Test dark mode CSS has dark background colors."""
        from asciidoc_artisan.ui.theme_manager import DARK_MODE_CSS

        assert "background:#1e1e1e" in DARK_MODE_CSS  # Dark body background
        assert "color:#dcdcdc" in DARK_MODE_CSS  # Light text
        assert "background:#2a2a2a" in DARK_MODE_CSS  # Dark code background

    def test_light_mode_css_contains_light_colors(self):
        """Test light mode CSS has light background colors."""
        from asciidoc_artisan.ui.theme_manager import LIGHT_MODE_CSS

        assert "background:#ffffff" in LIGHT_MODE_CSS  # White body background
        assert "color:#333333" in LIGHT_MODE_CSS  # Dark text
        assert "background:#f8f8f8" in LIGHT_MODE_CSS  # Light code background
