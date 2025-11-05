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

    # Additional CSS verification tests
    def test_dark_mode_css_is_string(self):
        """Test dark mode CSS is a string."""
        from asciidoc_artisan.ui.theme_manager import DARK_MODE_CSS
        assert isinstance(DARK_MODE_CSS, str)
        assert len(DARK_MODE_CSS) > 100  # Should have substantial content

    def test_light_mode_css_is_string(self):
        """Test light mode CSS is a string."""
        from asciidoc_artisan.ui.theme_manager import LIGHT_MODE_CSS
        assert isinstance(LIGHT_MODE_CSS, str)
        assert len(LIGHT_MODE_CSS) > 100  # Should have substantial content

    def test_dark_mode_css_contains_all_required_styles(self):
        """Test dark mode CSS contains all required style sections."""
        from asciidoc_artisan.ui.theme_manager import DARK_MODE_CSS
        # Should style body, code blocks, links, etc.
        assert "body {" in DARK_MODE_CSS or "body{" in DARK_MODE_CSS
        assert "pre {" in DARK_MODE_CSS or "pre{" in DARK_MODE_CSS or "code {" in DARK_MODE_CSS

    def test_light_mode_css_contains_all_required_styles(self):
        """Test light mode CSS contains all required style sections."""
        from asciidoc_artisan.ui.theme_manager import LIGHT_MODE_CSS
        # Should style body, code blocks, links, etc.
        assert "body {" in LIGHT_MODE_CSS or "body{" in LIGHT_MODE_CSS
        assert "pre {" in LIGHT_MODE_CSS or "pre{" in LIGHT_MODE_CSS or "code {" in LIGHT_MODE_CSS

    def test_css_constants_are_different(self):
        """Test dark and light mode CSS are different strings."""
        from asciidoc_artisan.ui.theme_manager import DARK_MODE_CSS, LIGHT_MODE_CSS
        assert DARK_MODE_CSS != LIGHT_MODE_CSS

    # Theme switching edge cases
    def test_toggle_dark_mode_multiple_times(self, main_window):
        """Test toggling dark mode multiple times works correctly."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        manager = ThemeManager(main_window)
        main_window.dark_mode_act = Mock()
        main_window.preview_handler = Mock()
        main_window.update_preview = Mock()

        # Toggle to dark
        main_window.dark_mode_act.isChecked.return_value = True
        manager.toggle_dark_mode()
        assert main_window._settings.dark_mode is True

        # Toggle back to light
        main_window.dark_mode_act.isChecked.return_value = False
        manager.toggle_dark_mode()
        assert main_window._settings.dark_mode is False

        # Toggle to dark again
        main_window.dark_mode_act.isChecked.return_value = True
        manager.toggle_dark_mode()
        assert main_window._settings.dark_mode is True

    def test_toggle_dark_mode_with_missing_preview_handler_attr(self, main_window):
        """Test toggle dark mode when preview_handler attribute doesn't exist."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        manager = ThemeManager(main_window)
        main_window.dark_mode_act = Mock()
        main_window.dark_mode_act.isChecked.return_value = True
        # No preview_handler attribute at all
        main_window.update_preview = Mock()

        # Should work - hasattr will be False
        manager.toggle_dark_mode()
        assert main_window._settings.dark_mode is True

    def test_toggle_dark_mode_clears_css_cache(self, main_window):
        """Test toggle dark mode clears CSS cache in preview handler."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        manager = ThemeManager(main_window)
        main_window.dark_mode_act = Mock()
        main_window.dark_mode_act.isChecked.return_value = True
        main_window.preview_handler = Mock()
        main_window.update_preview = Mock()

        manager.toggle_dark_mode()

        # Should call clear_css_cache if available
        if hasattr(main_window.preview_handler, 'clear_css_cache'):
            main_window.preview_handler.clear_css_cache.assert_called()

    # Label handling edge cases
    def test_apply_theme_with_only_editor_label(self, main_window):
        """Test apply_theme with only editor_label present."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        main_window.editor_label = Mock()
        # No preview_label or chat_label

        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)
        manager.apply_theme()

        # Editor label should be styled
        main_window.editor_label.setStyleSheet.assert_called_with("color: white;")

    def test_apply_theme_with_only_preview_label(self, main_window):
        """Test apply_theme with only preview_label present."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        main_window.preview_label = Mock()
        # No editor_label or chat_label

        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)
        manager.apply_theme()

        # Preview label should be styled
        main_window.preview_label.setStyleSheet.assert_called_with("color: white;")

    def test_apply_theme_with_only_chat_label(self, main_window):
        """Test apply_theme with only chat_label present."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        main_window.chat_label = Mock()
        # No editor_label or preview_label

        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)
        manager.apply_theme()

        # Chat label should be styled
        main_window.chat_label.setStyleSheet.assert_called_with("color: white;")

    def test_apply_theme_labels_called_with_correct_colors(self, main_window):
        """Test labels are styled with correct colors based on theme."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        main_window.editor_label = Mock()
        main_window.preview_label = Mock()
        main_window.chat_label = Mock()

        # Dark mode
        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)
        manager.apply_theme()

        # All labels should be white
        for label in [main_window.editor_label, main_window.preview_label, main_window.chat_label]:
            label.setStyleSheet.assert_called_with("color: white;")

        # Reset mocks
        main_window.editor_label.reset_mock()
        main_window.preview_label.reset_mock()
        main_window.chat_label.reset_mock()

        # Light mode
        main_window._settings.dark_mode = False
        manager = ThemeManager(main_window)
        manager.apply_theme()

        # All labels should be black
        for label in [main_window.editor_label, main_window.preview_label, main_window.chat_label]:
            label.setStyleSheet.assert_called_with("color: black;")

    # Chat manager integration edge cases
    def test_apply_theme_without_chat_manager_attr(self, main_window):
        """Test apply_theme when chat_manager attribute doesn't exist."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        # No chat_manager attribute at all (hasattr will be False)
        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)

        # Should not crash
        manager.apply_theme()

    def test_apply_theme_chat_manager_without_panel_attr(self, main_window):
        """Test apply_theme when chat_manager has no _chat_panel attribute."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        chat_manager = Mock(spec=[])  # No _chat_panel attribute
        main_window.chat_manager = chat_manager

        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)

        # Should not crash (hasattr will be False)
        manager.apply_theme()

    def test_apply_theme_chat_manager_multiple_calls(self, main_window):
        """Test applying theme multiple times updates chat manager each time."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        chat_panel = Mock()
        chat_manager = Mock()
        chat_manager._chat_panel = chat_panel
        main_window.chat_manager = chat_manager

        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)

        # Apply theme multiple times
        manager.apply_theme()
        manager.apply_theme()
        manager.apply_theme()

        # Should be called each time
        assert chat_panel.set_dark_mode.call_count == 3

    # get_preview_css edge cases
    def test_get_preview_css_returns_same_object_for_same_mode(self, main_window):
        """Test get_preview_css returns same constant object for repeated calls."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        manager = ThemeManager(main_window)
        main_window._settings.dark_mode = False

        css1 = manager.get_preview_css()
        css2 = manager.get_preview_css()
        css3 = manager.get_preview_css()

        # Should all be the same object (constant)
        assert css1 is css2
        assert css2 is css3

    def test_get_preview_css_changes_when_mode_changes(self, main_window):
        """Test get_preview_css returns different CSS when theme changes."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        manager = ThemeManager(main_window)

        # Light mode
        main_window._settings.dark_mode = False
        css_light = manager.get_preview_css()

        # Dark mode
        main_window._settings.dark_mode = True
        css_dark = manager.get_preview_css()

        # Should be different
        assert css_light is not css_dark
        assert css_light != css_dark

    def test_get_preview_css_light_mode_is_constant(self, main_window):
        """Test light mode CSS is the module constant."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager, LIGHT_MODE_CSS

        manager = ThemeManager(main_window)
        main_window._settings.dark_mode = False

        css = manager.get_preview_css()
        assert css is LIGHT_MODE_CSS

    def test_get_preview_css_dark_mode_is_constant(self, main_window):
        """Test dark mode CSS is the module constant."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager, DARK_MODE_CSS

        manager = ThemeManager(main_window)
        main_window._settings.dark_mode = True

        css = manager.get_preview_css()
        assert css is DARK_MODE_CSS

    # Palette verification tests
    def test_dark_mode_palette_window_color_is_dark(self, main_window, qapp):
        """Test dark mode sets a dark window color."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)
        manager.apply_theme()

        palette = qapp.palette()
        window_color = palette.color(palette.ColorRole.Window)
        # Dark color should have low RGB values
        assert window_color.red() < 100
        assert window_color.green() < 100
        assert window_color.blue() < 100

    def test_dark_mode_palette_text_color_is_light(self, main_window, qapp):
        """Test dark mode sets a light text color."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)
        manager.apply_theme()

        palette = qapp.palette()
        text_color = palette.color(palette.ColorRole.WindowText)
        # Light text should have high RGB values
        assert text_color.red() > 150 or text_color.green() > 150 or text_color.blue() > 150

    def test_light_mode_does_not_crash(self, main_window, qapp):
        """Test light mode palette application does not crash."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        main_window._settings.dark_mode = False
        manager = ThemeManager(main_window)

        # Should not crash
        manager.apply_theme()

    def test_theme_manager_stores_parent_reference(self, main_window):
        """Test ThemeManager stores reference to parent window."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        manager = ThemeManager(main_window)
        assert hasattr(manager, 'editor')
        assert manager.editor == main_window

    def test_theme_manager_initialization_does_not_crash(self, main_window):
        """Test ThemeManager initialization completes without error."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        # Should not raise exception
        manager = ThemeManager(main_window)
        assert manager is not None

    # Edge cases for settings interaction
    def test_apply_theme_reads_dark_mode_from_settings(self, main_window):
        """Test apply_theme reads dark_mode value from settings."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        main_window.editor_label = Mock()

        # Set to dark mode via settings
        main_window._settings.dark_mode = True
        manager = ThemeManager(main_window)
        manager.apply_theme()

        # Should apply dark mode styling
        main_window.editor_label.setStyleSheet.assert_called_with("color: white;")

        # Change settings to light mode
        main_window.editor_label.reset_mock()
        main_window._settings.dark_mode = False
        manager.apply_theme()

        # Should apply light mode styling
        main_window.editor_label.setStyleSheet.assert_called_with("color: black;")

    def test_get_preview_css_respects_settings_changes(self, main_window):
        """Test get_preview_css immediately reflects settings changes."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        manager = ThemeManager(main_window)

        # Start in light mode
        main_window._settings.dark_mode = False
        css1 = manager.get_preview_css()
        assert "background:#ffffff" in css1

        # Change to dark mode
        main_window._settings.dark_mode = True
        css2 = manager.get_preview_css()
        assert "background:#1e1e1e" in css2

        # Back to light mode
        main_window._settings.dark_mode = False
        css3 = manager.get_preview_css()
        assert "background:#ffffff" in css3

    # Performance and consistency tests
    def test_apply_theme_is_idempotent(self, main_window):
        """Test calling apply_theme multiple times is safe."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager

        manager = ThemeManager(main_window)

        # Call multiple times - should not crash or change behavior
        manager.apply_theme()
        manager.apply_theme()
        manager.apply_theme()

    def test_toggle_dark_mode_triggers_update_preview(self, main_window):
        """Test toggle_dark_mode triggers preview update."""
        from asciidoc_artisan.ui.theme_manager import ThemeManager
        from unittest.mock import Mock

        manager = ThemeManager(main_window)
        main_window.dark_mode_act = Mock()
        main_window.dark_mode_act.isChecked.return_value = True
        main_window.preview_handler = Mock()
        main_window.update_preview = Mock()

        manager.toggle_dark_mode()

        # Should trigger preview update
        main_window.update_preview.assert_called_once()

    def test_css_constants_are_module_level(self):
        """Test CSS constants are defined at module level."""
        from asciidoc_artisan.ui import theme_manager

        assert hasattr(theme_manager, 'DARK_MODE_CSS')
        assert hasattr(theme_manager, 'LIGHT_MODE_CSS')
        assert theme_manager.DARK_MODE_CSS is not None
        assert theme_manager.LIGHT_MODE_CSS is not None
