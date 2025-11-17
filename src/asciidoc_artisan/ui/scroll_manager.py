"""
Scroll Manager - Handles synchronized scrolling between editor and preview.

Implements:
- Scroll synchronization setup
- Editor-to-preview scroll sync
- Scroll loop detection and prevention
- Event coalescing for smooth scrolling

Extracted from main_window.py as part of Phase 6 refactoring to reduce
main window complexity and improve modularity.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class ScrollManager:
    """Manages synchronized scrolling between editor and preview panes.

    This class encapsulates scroll synchronization logic, including loop
    detection, event coalescing, and JavaScript-based scrolling for
    QWebEngineView.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the ScrollManager with a reference to the main editor."""
        self.editor = editor
        self._last_editor_scroll = 0
        self._last_preview_scroll = 0
        self._scroll_sync_count = 0

    def setup_synchronized_scrolling(self) -> None:
        """
        Set up synchronized scrolling between editor and preview.

        Implements FR-043 with scroll loop protection and event coalescing.
        Note: QWebEngineView uses JavaScript for scroll synchronization.
        """
        editor_scrollbar = self.editor.editor.verticalScrollBar()
        editor_scrollbar.valueChanged.connect(self.sync_editor_to_preview)

    def sync_editor_to_preview(self, value: int) -> None:
        """
        Synchronize preview scroll position with editor.

        Implements FR-043 with loop detection and coalescing.
        Uses JavaScript for QWebEngineView scrolling.

        Args:
            value: Current scroll position value from editor scrollbar
        """
        if not self.editor._sync_scrolling or self.editor._is_syncing_scroll:
            return

        # Skip if value hasn't changed significantly (coalesce events)
        if abs(value - self._last_editor_scroll) < 2:
            return

        self._last_editor_scroll = value

        # Detect potential scroll loops
        self._scroll_sync_count += 1
        if self._scroll_sync_count > 100:
            logger.warning("Scroll loop detected, resetting")
            self._scroll_sync_count = 0
            return

        self.editor._is_syncing_scroll = True
        try:
            editor_scrollbar = self.editor.editor.verticalScrollBar()
            editor_max = editor_scrollbar.maximum()

            if editor_max > 0:
                scroll_percentage = value / editor_max

                # Check if preview has JavaScript capability (QWebEngineView)
                if hasattr(self.editor.preview, "page"):
                    # Use JavaScript to scroll QWebEngineView
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
                    self.editor.preview.page().runJavaScript(js_code)
                else:
                    # Fallback for QTextBrowser
                    preview_scrollbar = self.editor.preview.verticalScrollBar()
                    preview_max = preview_scrollbar.maximum()
                    if preview_max > 0:
                        preview_value = int(scroll_percentage * preview_max)
                        preview_scrollbar.setValue(preview_value)

            # Reset counter on successful sync
            self._scroll_sync_count = max(0, self._scroll_sync_count - 1)
        finally:
            self.editor._is_syncing_scroll = False

    def sync_preview_to_editor(self, value: int) -> None:
        """
        Synchronize editor scroll position with preview.

        Note: QWebEngineView does not provide scrollbar signals.
        Preview-to-editor sync is primarily handled via editor-to-preview.
        This method is kept for compatibility but has limited functionality.

        Args:
            value: Current scroll position value from preview scrollbar
        """
        # QWebEngineView doesn't provide scroll events in the same way
        # Primary sync direction is editor -> preview
        pass
