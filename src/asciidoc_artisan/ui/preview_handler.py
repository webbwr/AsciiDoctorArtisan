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

    def _set_preview_html(self, html: str) -> None:
        """
        Set HTML in QTextBrowser widget.

        Args:
            html: Styled HTML content to display
        """
        # QTextBrowser uses simple setHtml (no base URL needed)
        self.preview.setHtml(html)

    def _scroll_preview_to_percentage(self, percentage: float) -> None:
        """
        Scroll QTextBrowser to percentage via scrollbar.

        Args:
            percentage: Scroll position as percentage (0.0 to 1.0)
        """
        # Scroll preview via direct scrollbar manipulation
        preview_scrollbar = self.preview.verticalScrollBar()
        preview_max = preview_scrollbar.maximum()
        preview_value = int(preview_max * percentage)
        preview_scrollbar.setValue(preview_value)

    def _get_preview_scroll_percentage(self) -> float | None:
        """
        Get scroll percentage from QTextBrowser scrollbar.

        Returns:
            Scroll percentage (0.0 to 1.0), or None if not available
        """
        preview_scrollbar = self.preview.verticalScrollBar()
        preview_max = preview_scrollbar.maximum()

        if preview_max > 0:
            preview_value = preview_scrollbar.value()
            scroll_percent: float = preview_value / preview_max
            return scroll_percent

        return None
