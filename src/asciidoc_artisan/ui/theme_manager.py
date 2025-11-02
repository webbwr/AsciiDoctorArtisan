"""
===============================================================================
THEME MANAGER - Dark/Light Mode and CSS Generation
===============================================================================

FILE PURPOSE:
This file manages the application's appearance: dark mode, light mode, and
CSS styling for the preview window.

WHAT THIS FILE DOES:
1. Toggles between dark and light themes (Ctrl+D keyboard shortcut)
2. Applies color palettes to the entire application
3. Generates CSS for the preview window (dark or light styles)
4. Persists theme preference in settings

FOR BEGINNERS - WHAT IS A THEME?:
A theme controls the colors of the application. There are two themes:
- Light mode: Light background, dark text (like reading a paper book)
- Dark mode: Dark background, light text (easier on eyes at night)

ANALOGY:
Think of adjusting your phone's brightness:
- Light mode = brightness up (daytime, outdoor use)
- Dark mode = brightness down (nighttime, battery saving)

The theme affects:
- Application background (window color)
- Text color (black on white vs white on black)
- Button colors, menu colors, etc.
- Preview window CSS (HTML styling)

WHY THIS FILE WAS EXTRACTED:
Before v1.5.0, theme logic was in main_window.py. We extracted it to:
- Reduce main_window.py size (part of 67% reduction)
- Separate concerns (main window doesn't need to know about color palettes)
- Make theme logic testable independently
- Follow Single Responsibility Principle

KEY CONCEPTS:

1. COLOR PALETTE:
   Qt uses QPalette to define colors for UI elements:
   - Window: Main background color
   - WindowText: Text on windows
   - Base: Input field backgrounds (text editors)
   - Button: Button backgrounds
   - HighlightedText: Selected text
   etc.

2. CSS GENERATION:
   The preview window needs HTML/CSS styling. We generate CSS strings
   with colors matching the current theme (dark or light).

3. THEME PERSISTENCE:
   When you toggle dark mode, it's saved to settings. Next time you
   open the app, your theme preference is remembered.

4. CACHE INVALIDATION:
   When theme changes, we clear the CSS cache. This forces the preview
   to regenerate with new theme colors.

SPECIFICATIONS IMPLEMENTED:
- FR-041: Dark mode toggle with keyboard shortcut (Ctrl+D)
- NFR-015: Theme persistence in settings

REFACTORING HISTORY:
- v1.0: All theme code in main_window.py
- v1.4.1: CSS generation moved to ThemeManager (63 lines reduced)
- v1.5.0: Complete extraction to theme_manager.py

VERSION: 1.5.0 (Phase 2 refactoring)
"""

# === STANDARD LIBRARY IMPORTS ===
from typing import TYPE_CHECKING  # Type hints without circular imports

# === QT FRAMEWORK IMPORTS ===
from PySide6.QtCore import Qt  # Qt constants (colors, key codes, etc.)
from PySide6.QtGui import (
    QColor,  # Color class (RGB values)
    QPalette,  # Color palette for application theme
)
from PySide6.QtWidgets import QApplication  # Main application class

# === TYPE CHECKING (Avoid Circular Imports) ===
if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

# === PRE-GENERATED CSS CONSTANTS (Performance Optimization) ===
# CSS strings are static and never change at runtime
# Pre-generating them as constants eliminates method call overhead
DARK_MODE_CSS = """
body {
    background:#1e1e1e; color:#dcdcdc;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    padding: 20px; line-height: 1.6; max-width: 900px; margin: 0 auto;
}
h1,h2,h3,h4,h5,h6 { color:#ececec; margin-top: 1.5em; margin-bottom: 0.5em; }
h1 { font-size: 2.2em; border-bottom: 2px solid #444; padding-bottom: 0.3em; }
h2 { font-size: 1.8em; border-bottom: 1px solid #333; padding-bottom: 0.2em; }
h3 { font-size: 1.4em; }
a { color:#80d0ff; text-decoration: none; }
a:hover { text-decoration: underline; }
code { background:#2a2a2a; color:#f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
pre { background:#2a2a2a; color:#f0f0f0; padding: 15px; overflow-x: auto; border-radius: 5px; }
pre code { background: none; padding: 0; }
blockquote { border-left: 4px solid #666; margin: 1em 0; padding-left: 1em; color: #aaa; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #444; padding: 8px; text-align: left; }
th { background: #2a2a2a; font-weight: bold; }
ul, ol { padding-left: 2em; margin: 1em 0; }
.admonitionblock { margin: 1em 0; padding: 1em; border-radius: 5px; }
.admonitionblock.note { background: #1e3a5f; border-left: 4px solid #4a90e2; }
.admonitionblock.tip { background: #1e4d2b; border-left: 4px solid #5cb85c; }
.admonitionblock.warning { background: #5d4037; border-left: 4px solid #ff9800; }
.admonitionblock.caution { background: #5d4037; border-left: 4px solid #f44336; }
.admonitionblock.important { background: #4a148c; border-left: 4px solid #9c27b0; }
.imageblock { text-align: center; margin: 1em 0; }
.imageblock img { max-width: 100%; height: auto; }
"""

LIGHT_MODE_CSS = """
body {
    background:#ffffff; color:#333333;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    padding: 20px; line-height: 1.6; max-width: 900px; margin: 0 auto;
}
h1,h2,h3,h4,h5,h6 { color:#111111; margin-top: 1.5em; margin-bottom: 0.5em; }
h1 { font-size: 2.2em; border-bottom: 2px solid #ddd; padding-bottom: 0.3em; }
h2 { font-size: 1.8em; border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
h3 { font-size: 1.4em; }
a { color:#007bff; text-decoration: none; }
a:hover { text-decoration: underline; }
code { background:#f8f8f8; color:#333; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; border: 1px solid #e1e4e8; }
pre { background:#f8f8f8; color:#333; padding: 15px; overflow-x: auto; border-radius: 5px; border: 1px solid #e1e4e8; }
pre code { background: none; padding: 0; border: none; }
blockquote { border-left: 4px solid #ddd; margin: 1em 0; padding-left: 1em; color: #666; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background: #f8f8f8; font-weight: bold; }
ul, ol { padding-left: 2em; margin: 1em 0; }
.admonitionblock { margin: 1em 0; padding: 1em; border-radius: 5px; }
.admonitionblock.note { background: #e3f2fd; border-left: 4px solid #2196f3; }
.admonitionblock.tip { background: #e8f5e9; border-left: 4px solid #4caf50; }
.admonitionblock.warning { background: #fff3e0; border-left: 4px solid #ff9800; }
.admonitionblock.caution { background: #ffebee; border-left: 4px solid #f44336; }
.admonitionblock.important { background: #f3e5f5; border-left: 4px solid #9c27b0; }
.imageblock { text-align: center; margin: 1em 0; }
.imageblock img { max-width: 100%; height: auto; }
"""


class ThemeManager:
    """
    Theme Manager - Controls Dark/Light Mode and CSS Generation.

    FOR BEGINNERS - WHAT IS THIS CLASS?:
    This class is like the "interior decorator" for the application. It:
    - Paints the walls (sets background colors)
    - Chooses the text color (dark or light)
    - Styles the preview window (generates CSS)
    - Remembers your preference (saves to settings)

    RESPONSIBILITIES:
    1. Apply dark or light theme to entire application
    2. Generate CSS for preview window (matching theme)
    3. Toggle between themes (on keyboard shortcut or menu click)
    4. Update label colors (Editor/Preview labels at top of panes)
    5. Clear CSS cache when theme changes

    WHY IT EXISTS:
    Before this class, theme logic was scattered in main_window.py. Now
    it's all centralized in one place, making it easier to:
    - Understand (all theme code in one file)
    - Test (can test theme without main window)
    - Modify (add new themes or colors)

    USAGE:
    Called by main_window.py:
        theme_mgr = ThemeManager(self)
        theme_mgr.apply_theme()  # Apply current theme
        theme_mgr.toggle_dark_mode()  # Switch themes

    PARAMETERS:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """
        Initialize Theme Manager.

        WHAT THIS DOES:
        Stores a reference to the main editor window. This allows the theme
        manager to access settings, update labels, and trigger preview updates.

        PARAMETERS:
            editor: The main application window (AsciiDocEditor)

        CREATES:
            self.editor: Reference to main window
            _cached_dark_css: Cached dark mode CSS (generated once)
            _cached_light_css: Cached light mode CSS (generated once)
        """
        # Store reference to main editor window
        self.editor = editor

        # CSS cache to avoid regenerating on every preview update
        self._cached_dark_css: str | None = None
        self._cached_light_css: str | None = None

    def apply_theme(self) -> None:
        """
        Apply Current Theme - Dark or Light Mode.

        WHAT THIS DOES:
        Checks the settings to see if dark mode is enabled, then applies
        the appropriate theme (dark or light) to the entire application.

        Also updates the Editor/Preview labels at the top of each pane
        to match the theme (white text on dark, black text on light).
        """
        # Check if dark mode is enabled in settings
        if self.editor._settings.dark_mode:
            # Apply dark color palette to application
            self._apply_dark_theme()

            # Update label colors for dark mode (white text on dark background)
            if hasattr(self.editor, "editor_label"):
                self.editor.editor_label.setStyleSheet("color: white;")
            if hasattr(self.editor, "preview_label"):
                self.editor.preview_label.setStyleSheet("color: white;")
            if hasattr(self.editor, "chat_label"):
                self.editor.chat_label.setStyleSheet("color: white;")

            # Update chat panel messages to dark mode
            if hasattr(self.editor, "chat_manager") and hasattr(
                self.editor.chat_manager, "_chat_panel"
            ):
                self.editor.chat_manager._chat_panel.set_dark_mode(True)
        else:
            # Light mode - reset to system default light theme
            QApplication.setPalette(QApplication.style().standardPalette())

            # Update label colors for light mode (black text on light background)
            if hasattr(self.editor, "editor_label"):
                self.editor.editor_label.setStyleSheet("color: black;")
            if hasattr(self.editor, "preview_label"):
                self.editor.preview_label.setStyleSheet("color: black;")
            if hasattr(self.editor, "chat_label"):
                self.editor.chat_label.setStyleSheet("color: black;")

            # Update chat panel messages to light mode
            if hasattr(self.editor, "chat_manager") and hasattr(
                self.editor.chat_manager, "_chat_panel"
            ):
                self.editor.chat_manager._chat_panel.set_dark_mode(False)

    def _apply_dark_theme(self) -> None:
        """Apply dark theme color palette to the application."""
        palette = QPalette()

        # Window and text colors
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)

        # Editor/input colors
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))

        # Tooltip colors
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)

        # Text and button colors
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)

        # Link and highlight colors
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

        # Apply the palette to the application
        QApplication.setPalette(palette)

    def toggle_dark_mode(self) -> None:
        """Toggle between dark and light mode."""
        self.editor._settings.dark_mode = self.editor.dark_mode_act.isChecked()
        self.apply_theme()

        # Clear CSS cache so preview regenerates with new theme colors
        if hasattr(self.editor, "preview_handler"):
            self.editor.preview_handler.clear_css_cache()

        self.editor.update_preview()

    def get_preview_css(self) -> str:
        """Get CSS for preview rendering based on current theme.

        Returns pre-generated CSS constants for zero overhead.
        CSS is defined at module level and never changes.

        Returns:
            CSS string for dark or light mode preview rendering
        """
        # Return module-level constants (zero method call overhead)
        if self.editor._settings.dark_mode:
            return DARK_MODE_CSS
        else:
            return LIGHT_MODE_CSS

    def _get_dark_mode_css(self) -> str:
        """Get CSS for dark mode preview - DEPRECATED, use constant."""
        return DARK_MODE_CSS

    def _get_dark_mode_css_old(self) -> str:
        """Old implementation - kept for reference only."""
        return """
            body {
                background:#1e1e1e; color:#dcdcdc;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 20px; line-height: 1.6; max-width: 900px; margin: 0 auto;
            }
            h1,h2,h3,h4,h5,h6 { color:#ececec; margin-top: 1.5em; margin-bottom: 0.5em; }
            h1 { font-size: 2.2em; border-bottom: 2px solid #444; padding-bottom: 0.3em; }
            h2 { font-size: 1.8em; border-bottom: 1px solid #333; padding-bottom: 0.2em; }
            h3 { font-size: 1.4em; }
            a { color:#80d0ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            code { background:#2a2a2a; color:#f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
            pre { background:#2a2a2a; color:#f0f0f0; padding: 15px; overflow-x: auto; border-radius: 5px; }
            pre code { background: none; padding: 0; }
            blockquote { border-left: 4px solid #666; margin: 1em 0; padding-left: 1em; color: #aaa; }
            table { border-collapse: collapse; width: 100%; margin: 1em 0; }
            th, td { border: 1px solid #444; padding: 8px; text-align: left; }
            th { background: #2a2a2a; font-weight: bold; }
            ul, ol { padding-left: 2em; margin: 1em 0; }
            .admonitionblock { margin: 1em 0; padding: 1em; border-radius: 5px; }
            .admonitionblock.note { background: #1e3a5f; border-left: 4px solid #4a90e2; }
            .admonitionblock.tip { background: #1e4d2b; border-left: 4px solid #5cb85c; }
            .admonitionblock.warning { background: #5d4037; border-left: 4px solid #ff9800; }
            .admonitionblock.caution { background: #5d4037; border-left: 4px solid #f44336; }
            .admonitionblock.important { background: #4a148c; border-left: 4px solid #9c27b0; }
            .imageblock { text-align: center; margin: 1em 0; }
            .imageblock img { max-width: 100%; height: auto; }
        """

    def _get_light_mode_css(self) -> str:
        """Get CSS for light mode preview - DEPRECATED, use constant."""
        return LIGHT_MODE_CSS
