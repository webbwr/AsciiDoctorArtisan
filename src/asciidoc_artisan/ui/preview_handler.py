"""
Text Browser Preview Handler - Software rendering fallback.

This module provides a QTextBrowser-based preview handler for:
- Systems without GPU support
- WSLg environments
- Software rendering fallback

Uses Qt's QTextBrowser widget which provides:
- Reliable cross-platform rendering
- No GPU dependencies
- Good performance for typical documents
- Direct scrollbar control

Extracted from monolithic main_window.py to improve maintainability.
"""

import logging
import time
from typing import Any

from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser

from asciidoc_artisan.ui.preview_handler_base import PreviewHandlerBase

logger = logging.getLogger(__name__)


class PreviewHandler(PreviewHandlerBase):
    """
    QTextBrowser-based preview handler (software rendering).

    Provides reliable preview rendering without GPU dependencies.
    Suitable for:
    - WSLg environments
    - Systems without GPU
    - Software rendering fallback

    Implements abstract methods from PreviewHandlerBase:
    - handle_preview_complete() - Update QTextBrowser with HTML
    - sync_editor_to_preview() - Sync scroll via scrollbar
    - sync_preview_to_editor() - Sync scroll via scrollbar
    """

    def __init__(
        self, editor: QPlainTextEdit, preview: QTextBrowser, parent_window: Any
    ) -> None:
        """
        Initialize TextBrowser PreviewHandler.

        Args:
            editor: The text editor widget
            preview: The QTextBrowser widget for HTML preview
            parent_window: Main window (for signals and state)
        """
        super().__init__(editor, preview, parent_window)

        logger.info("PreviewHandler initialized with QTextBrowser (software rendering)")

    def handle_preview_complete(self, html: str) -> None:
        """
        Handle completed preview rendering (QTextBrowser).

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

        # Update preview (QTextBrowser uses simple setHtml)
        self.preview.setHtml(styled_html)

        # Emit signal
        self.preview_updated.emit(html)

        logger.debug("Preview updated successfully")

    def sync_editor_to_preview(self, editor_value: int) -> None:
        """
        Sync preview scroll position to editor (QTextBrowser).

        Uses direct scrollbar control for QTextBrowser widget.

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

                # Scroll preview via scrollbar (QTextBrowser-specific)
                preview_scrollbar = self.preview.verticalScrollBar()
                preview_max = preview_scrollbar.maximum()
                preview_value = int(preview_max * scroll_percentage)
                preview_scrollbar.setValue(preview_value)

        finally:
            self.is_syncing_scroll = False

    def sync_preview_to_editor(self, preview_value: int) -> None:
        """
        Sync editor scroll position to preview (QTextBrowser).

        Uses direct scrollbar control for bi-directional scrolling.

        Args:
            preview_value: Preview scroll value
        """
        if not self.sync_scrolling_enabled or self.is_syncing_scroll:
            return

        self.is_syncing_scroll = True
        try:
            # Calculate scroll percentage
            preview_scrollbar = self.preview.verticalScrollBar()
            preview_max = preview_scrollbar.maximum()

            if preview_max > 0:
                scroll_percentage = preview_value / preview_max

                # Scroll editor via scrollbar
                editor_scrollbar = self.editor.verticalScrollBar()
                editor_max = editor_scrollbar.maximum()
                editor_value = int(editor_max * scroll_percentage)
                editor_scrollbar.setValue(editor_value)

        finally:
            self.is_syncing_scroll = False
