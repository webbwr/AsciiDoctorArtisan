"""
Theme Manager - Handles theme and appearance management for AsciiDoc Artisan.

Implements:
- FR-041: Dark mode toggle (Ctrl+D) with persistence

This module manages dark/light theme switching and color palette configuration,
extracted from main_window.py as part of Phase 2 architectural refactoring.

The ThemeManager provides a clean interface for theme-related operations.
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor


class ThemeManager:
    """Manages theme and appearance for AsciiDoc Artisan.

    This class encapsulates all theme-related logic including dark/light mode
    switching and color palette management.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the ThemeManager with a reference to the main editor."""
        self.editor = editor

    def apply_theme(self) -> None:
        """Apply the current theme (dark or light mode)."""
        if self.editor._settings.dark_mode:
            self._apply_dark_theme()

            # Update label colors for dark mode
            if hasattr(self.editor, "editor_label"):
                self.editor.editor_label.setStyleSheet("color: white;")
            if hasattr(self.editor, "preview_label"):
                self.editor.preview_label.setStyleSheet("color: white;")
        else:
            # Reset to system default light theme
            QApplication.setPalette(QApplication.style().standardPalette())

            # Update label colors for light mode
            if hasattr(self.editor, "editor_label"):
                self.editor.editor_label.setStyleSheet("color: black;")
            if hasattr(self.editor, "preview_label"):
                self.editor.preview_label.setStyleSheet("color: black;")

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

        Returns:
            CSS string for dark or light mode preview rendering
        """
        if self.editor._settings.dark_mode:
            return self._get_dark_mode_css()
        else:
            return self._get_light_mode_css()

    def _get_dark_mode_css(self) -> str:
        """Get CSS for dark mode preview."""
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
        """Get CSS for light mode preview."""
        return """
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
