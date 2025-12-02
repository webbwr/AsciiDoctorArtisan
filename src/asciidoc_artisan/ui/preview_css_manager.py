"""
Preview CSS Manager - Handles CSS generation and caching for preview rendering.

Extracted from PreviewHandlerBase to reduce class size (MA principle).
Manages CSS generation, caching, custom CSS, and HTML wrapping.
"""

import logging
from typing import Protocol

from asciidoc_artisan.ui.preview_constants import (
    CSP_POLICY,
    ERROR_COLORS_DARK,
    ERROR_COLORS_LIGHT,
    FALLBACK_CSS,
)

logger = logging.getLogger(__name__)


class ThemeManagerProtocol(Protocol):
    """Protocol for theme manager interface."""

    def get_preview_css(self) -> str:
        """Get preview CSS from theme."""
        ...


class SettingsProtocol(Protocol):
    """Protocol for settings interface."""

    dark_mode: bool


class WindowProtocol(Protocol):
    """Protocol for main window interface."""

    theme_manager: ThemeManagerProtocol | None
    _settings: SettingsProtocol | None


class PreviewCSSManager:
    """
    Manages CSS generation and caching for preview rendering.

    Extracted from PreviewHandlerBase per MA principle (~80 lines).

    Handles:
    - CSS generation with theme support
    - CSS caching for performance
    - Custom CSS injection (fonts, etc.)
    - HTML wrapping with security headers
    - Error display HTML generation
    """

    def __init__(self, window: WindowProtocol) -> None:
        """
        Initialize CSS manager.

        Args:
            window: Main window for theme access
        """
        self.window = window
        self._css_cache: str | None = None
        self._custom_css: str = ""

    def get_preview_css(self) -> str:
        """Get preview CSS (cached for performance).

        Returns:
            CSS content as string (includes custom CSS for fonts)
        """
        if self._css_cache is None:
            self._css_cache = self._generate_preview_css()

        if self._custom_css:
            return self._css_cache + "\n" + self._custom_css

        return self._css_cache

    def set_custom_css(self, css: str) -> None:
        """Set custom CSS for preview (e.g., font settings).

        Args:
            css: Custom CSS string to append to preview CSS
        """
        self._custom_css = css
        self._css_cache = None
        logger.debug("Custom CSS applied to preview")

    def clear_cache(self) -> None:
        """Clear CSS cache (call when theme changes)."""
        self._css_cache = None
        logger.debug("CSS cache cleared")

    def _generate_preview_css(self) -> str:
        """Generate preview CSS by delegating to ThemeManager.

        Returns:
            CSS content as string
        """
        if hasattr(self.window, "theme_manager") and self.window.theme_manager:
            return self.window.theme_manager.get_preview_css()

        return FALLBACK_CSS

    def wrap_with_css(self, html: str) -> str:
        """
        Wrap HTML content with CSS styling and security headers.

        Args:
            html: HTML body content

        Returns:
            Complete HTML with CSS and CSP security headers
        """
        css = self.get_preview_css()

        logger.debug("Applying Content Security Policy to preview HTML")

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Security-Policy" content="{CSP_POLICY}">
            <style>
                {css}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """

    def get_error_display_colors(self) -> dict[str, str]:
        """Get color scheme for error display based on theme.

        Returns:
            Dictionary with color keys: bg, text, heading, pre_bg
        """
        dark_mode = False
        if hasattr(self.window, "_settings") and self.window._settings:
            dark_mode = self.window._settings.dark_mode

        return ERROR_COLORS_DARK if dark_mode else ERROR_COLORS_LIGHT

    def build_error_html(self, error: str) -> str:
        """Build error display HTML.

        Args:
            error: Error message

        Returns:
            Complete HTML for error display
        """
        colors = self.get_error_display_colors()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Security-Policy" content="{CSP_POLICY}">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    background-color: {colors["bg"]};
                    color: {colors["text"]};
                }}
                h2 {{ color: {colors["heading"]}; }}
                pre {{
                    background-color: {colors["pre_bg"]};
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                    color: {colors["text"]};
                }}
            </style>
        </head>
        <body>
            <h2>Preview Error</h2>
            <p>Could not render preview:</p>
            <pre>{error}</pre>
        </body>
        </html>
        """

    def build_clear_html(self) -> str:
        """Build HTML for cleared preview.

        Returns:
            HTML for cleared preview state
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Security-Policy" content="{CSP_POLICY}">
        </head>
        <body>
            <p>Preview cleared</p>
        </body>
        </html>
        """
