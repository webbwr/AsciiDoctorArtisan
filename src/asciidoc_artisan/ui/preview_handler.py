"""
Preview Handler - Manage HTML preview rendering.

This module handles all preview-related operations:
- Update preview from editor text
- Generate preview CSS
- Handle preview rendering with worker
- Manage preview timer (adaptive based on document size)
- Sync scrolling between editor and preview

Extracted from main_window.py to improve maintainability and testability.
"""

import logging
import time
from typing import Any, Optional

from PySide6.QtCore import QObject, QTimer, Signal, Slot

# QWebEngine disabled for WSLg compatibility
# from PySide6.QtWebEngineCore import QWebEngineSettings
# from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser

try:
    from asciidoc_artisan.core.adaptive_debouncer import (
        AdaptiveDebouncer,
        DebounceConfig,
    )

    ADAPTIVE_DEBOUNCER_AVAILABLE = True
except ImportError:
    AdaptiveDebouncer = None
    DebounceConfig = None
    ADAPTIVE_DEBOUNCER_AVAILABLE = False

logger = logging.getLogger(__name__)


# Constants for preview timing
PREVIEW_FAST_INTERVAL_MS = 200  # For small documents
PREVIEW_NORMAL_INTERVAL_MS = 500  # For medium documents
PREVIEW_SLOW_INTERVAL_MS = 1000  # For large documents


class PreviewHandler(QObject):
    """Handle preview rendering and synchronization."""

    # Signals
    preview_updated = Signal(str)  # Emitted when preview HTML is updated
    preview_error = Signal(str)  # Emitted on preview error

    def __init__(self, editor: QPlainTextEdit, preview: QTextBrowser, parent_window):
        """
        Initialize PreviewHandler.

        Args:
            editor: The text editor widget
            preview: The QTextBrowser widget for HTML preview (WSLg compatible)
            parent_window: Main window (for signals and state)
        """
        super().__init__(parent_window)
        self.editor = editor
        self.preview = preview
        self.window = parent_window

        # WSLg FIX: Using QTextBrowser instead of QWebEngineView for better compatibility
        logger.info("PreviewHandler initialized with QTextBrowser (WSLg compatible)")

        # Preview state
        self.sync_scrolling_enabled = True
        self.is_syncing_scroll = False
        self._css_cache: Optional[str] = None

        # Preview timer (adaptive based on document size)
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)

        # Adaptive debouncer (if available)
        self._adaptive_debouncer: Optional[Any] = None
        self._use_adaptive_debouncing = True
        self._last_render_start: Optional[float] = None

        if ADAPTIVE_DEBOUNCER_AVAILABLE and AdaptiveDebouncer:
            self._adaptive_debouncer = AdaptiveDebouncer()
            logger.info("Adaptive debouncing enabled")

        # Connect editor text changes to preview updates
        self.editor.textChanged.connect(self._on_text_changed)

    def start_preview_updates(self) -> None:
        """Start automatic preview updates on text changes."""
        logger.info("Preview updates enabled")

    def stop_preview_updates(self) -> None:
        """Stop automatic preview updates."""
        self.preview_timer.stop()
        logger.info("Preview updates disabled")

    def _on_text_changed(self) -> None:
        """
        Handle text changed in editor.

        Uses adaptive timing based on:
        - Document size
        - System CPU load
        - Recent render times
        - User typing speed
        """
        # Cancel any pending update
        self.preview_timer.stop()

        # Get document size
        text_size = len(self.editor.toPlainText())

        # Use adaptive debouncing if available
        if self._use_adaptive_debouncing and self._adaptive_debouncer:
            # Notify debouncer of text change (for typing detection)
            self._adaptive_debouncer.on_text_changed()

            # Calculate adaptive delay
            delay = self._adaptive_debouncer.calculate_delay(document_size=text_size)
        else:
            # Fall back to simple size-based delay
            if text_size < 10000:  # < 10KB
                delay = PREVIEW_FAST_INTERVAL_MS
            elif text_size < 100000:  # < 100KB
                delay = PREVIEW_NORMAL_INTERVAL_MS
            else:  # >= 100KB
                delay = PREVIEW_SLOW_INTERVAL_MS

        # Start timer with calculated delay
        self.preview_timer.start(delay)

    @Slot()
    def update_preview(self) -> None:
        """
        Update preview with current editor content.

        Emits request_preview_render signal to worker thread.
        Tracks render start time for adaptive debouncing.
        """
        source_text = self.editor.toPlainText()

        # Track render start time
        self._last_render_start = time.time()

        # Emit signal to worker for rendering
        if hasattr(self.window, "request_preview_render"):
            self.window.request_preview_render.emit(source_text)

        logger.debug(f"Preview update requested ({len(source_text)} chars)")

    def handle_preview_complete(self, html: str) -> None:
        """
        Handle completed preview rendering from worker.

        Args:
            html: Rendered HTML content
        """
        # Calculate render time
        if self._last_render_start is not None:
            render_time = time.time() - self._last_render_start

            # Update adaptive debouncer with render time
            if self._adaptive_debouncer:
                self._adaptive_debouncer.on_render_complete(render_time)

            logger.debug(f"Render completed in {render_time:.3f}s")

        # Add CSS styling
        styled_html = self._wrap_with_css(html)

        # Update preview
        self.preview.setHtml(styled_html)

        # Emit signal
        self.preview_updated.emit(html)

        logger.debug("Preview updated successfully")

    def handle_preview_error(self, error: str) -> None:
        """
        Handle preview rendering error.

        Args:
            error: Error message
        """
        # Check dark mode for error display
        dark_mode = False
        if hasattr(self.window, "_settings") and hasattr(
            self.window._settings, "dark_mode"
        ):
            dark_mode = self.window._settings.dark_mode

        if dark_mode:
            bg_color = "#3a2a1a"
            text_color = "#ffcc99"
            heading_color = "#ff6666"
            pre_bg = "#2a2a2a"
        else:
            bg_color = "#fff3cd"
            text_color = "#856404"
            heading_color = "#dc3545"
            pre_bg = "#f8f9fa"

        error_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    background-color: {bg_color};
                    color: {text_color};
                }}
                h2 {{ color: {heading_color}; }}
                pre {{
                    background-color: {pre_bg};
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                    color: {text_color};
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
        self.preview.setHtml(error_html)

        # Emit signal
        self.preview_error.emit(error)

        logger.error(f"Preview error: {error}")

    def _wrap_with_css(self, html: str) -> str:
        """
        Wrap HTML content with CSS styling.

        Args:
            html: HTML body content

        Returns:
            Complete HTML with CSS
        """
        css = self.get_preview_css()

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                {css}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """

    def get_preview_css(self) -> str:
        """
        Get preview CSS (cached for performance).

        Returns:
            CSS content as string
        """
        if self._css_cache is None:
            self._css_cache = self._generate_preview_css()

        return self._css_cache

    def clear_css_cache(self) -> None:
        """Clear CSS cache (call when theme changes)."""
        self._css_cache = None
        logger.debug("CSS cache cleared")

    def _generate_preview_css(self) -> str:
        """
        Generate preview CSS.

        Returns:
            CSS content as string
        """
        # Check if dark mode is enabled
        dark_mode = False
        if hasattr(self.window, "_settings") and hasattr(
            self.window._settings, "dark_mode"
        ):
            dark_mode = self.window._settings.dark_mode

        # Set colors based on theme
        if dark_mode:
            text_color = "#e0e0e0"
            bg_color = "#1a1a1a"
            heading_color = "#ffffff"
            border_color = "#404040"
            code_bg = "#2a2a2a"
            table_bg = "#2a2a2a"
            link_color = "#66b3ff"
            quote_color = "#a0a0a0"
            quote_border = "#505050"
        else:
            text_color = "#333"
            bg_color = "#fff"
            heading_color = "#000"
            border_color = "#eaecef"
            code_bg = "#f6f8fa"
            table_bg = "#f6f8fa"
            link_color = "#0366d6"
            quote_color = "#6a737d"
            quote_border = "#dfe2e5"

        # Basic responsive CSS for AsciiDoc preview
        return f"""
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                color: {text_color};
                background-color: {bg_color};
            }}

            h1, h2, h3, h4, h5, h6 {{
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
                color: {heading_color};
            }}

            h1 {{ font-size: 2em; border-bottom: 1px solid {border_color}; padding-bottom: 0.3em; }}
            h2 {{ font-size: 1.5em; border-bottom: 1px solid {border_color}; padding-bottom: 0.3em; }}
            h3 {{ font-size: 1.25em; }}
            h4 {{ font-size: 1em; }}
            h5 {{ font-size: 0.875em; }}
            h6 {{ font-size: 0.85em; color: {quote_color}; }}

            p {{ margin-bottom: 16px; }}

            code {{
                padding: 0.2em 0.4em;
                margin: 0;
                font-size: 85%;
                background-color: {code_bg};
                border-radius: 3px;
                font-family: 'Courier New', Courier, monospace;
            }}

            pre {{
                padding: 16px;
                overflow: auto;
                font-size: 85%;
                line-height: 1.45;
                background-color: {code_bg};
                border-radius: 3px;
            }}

            pre code {{
                display: inline;
                padding: 0;
                margin: 0;
                overflow: visible;
                line-height: inherit;
                background-color: transparent;
                border: 0;
            }}

            blockquote {{
                padding: 0 1em;
                color: {quote_color};
                border-left: 0.25em solid {quote_border};
                margin: 0 0 16px 0;
            }}

            table {{
                border-spacing: 0;
                border-collapse: collapse;
                margin-bottom: 16px;
                width: 100%;
            }}

            table th, table td {{
                padding: 6px 13px;
                border: 1px solid {border_color};
            }}

            table th {{
                font-weight: 600;
                background-color: {table_bg};
            }}

            table tr:nth-child(2n) {{
                background-color: {table_bg};
            }}

            ul, ol {{
                padding-left: 2em;
                margin-bottom: 16px;
            }}

            li + li {{
                margin-top: 0.25em;
            }}

            a {{
                color: {link_color};
                text-decoration: none;
            }}

            a:hover {{
                text-decoration: underline;
            }}

            img {{
                max-width: 100%;
                height: auto;
            }}

            hr {{
                height: 0.25em;
                padding: 0;
                margin: 24px 0;
                background-color: {border_color};
                border: 0;
            }}
        """

    def enable_sync_scrolling(self, enabled: bool) -> None:
        """
        Enable or disable synchronized scrolling.

        Args:
            enabled: True to enable, False to disable
        """
        self.sync_scrolling_enabled = enabled
        logger.info(f"Sync scrolling {'enabled' if enabled else 'disabled'}")

    def sync_editor_to_preview(self, editor_value: int) -> None:
        """
        Sync preview scroll position to editor.

        Args:
            editor_value: Editor scroll bar value (0-max)
        """
        if not self.sync_scrolling_enabled or self.is_syncing_scroll:
            return

        self.is_syncing_scroll = True
        try:
            # Calculate scroll percentage
            editor_scrollbar = self.editor.verticalScrollBar()
            editor_max = editor_scrollbar.maximum()

            if editor_max > 0:
                scroll_percentage = editor_value / editor_max

                # Scroll preview (via JavaScript)
                js_code = f"""
                    var body = document.body;
                    var html = document.documentElement;
                    var height = Math.max(
                        body.scrollHeight, body.offsetHeight,
                        html.clientHeight, html.scrollHeight, html.offsetHeight
                    );
                    var maxScroll = height - window.innerHeight;
                    window.scrollTo(0, maxScroll * {scroll_percentage});
                """
                self.preview.page().runJavaScript(js_code)

        finally:
            self.is_syncing_scroll = False

    def sync_preview_to_editor(self, preview_value: int) -> None:
        """
        Sync editor scroll position to preview.

        Args:
            preview_value: Preview scroll value
        """
        if not self.sync_scrolling_enabled or self.is_syncing_scroll:
            return

        self.is_syncing_scroll = True
        try:
            # This would require JavaScript callback from preview
            # For now, we primarily sync editor -> preview
            pass
        finally:
            self.is_syncing_scroll = False

    def clear_preview(self) -> None:
        """Clear preview content."""
        self.preview.setHtml("<p>Preview cleared</p>")
        logger.debug("Preview cleared")

    def get_preview_html(self) -> str:
        """
        Get current preview HTML (async).

        Note: This is async, use with callback.
        """
        # Would need to implement async retrieval
        return ""

    def set_adaptive_debouncing(self, enabled: bool) -> None:
        """
        Enable or disable adaptive debouncing.

        Args:
            enabled: True to enable, False to disable
        """
        self._use_adaptive_debouncing = enabled
        logger.info(f"Adaptive debouncing {'enabled' if enabled else 'disabled'}")

    def get_debouncer_stats(self) -> dict:
        """
        Get adaptive debouncer statistics.

        Returns:
            Dictionary with stats, or empty dict if not available
        """
        if self._adaptive_debouncer:
            return self._adaptive_debouncer.get_statistics()
        return {}

    def reset_debouncer(self) -> None:
        """Reset adaptive debouncer state."""
        if self._adaptive_debouncer:
            self._adaptive_debouncer.reset()
            logger.debug("Adaptive debouncer reset")
