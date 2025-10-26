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
        if hasattr(self.editor, 'preview_handler'):
            self.editor.preview_handler.clear_css_cache()

        self.editor.update_preview()
