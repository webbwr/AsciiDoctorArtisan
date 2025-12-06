"""
===============================================================================
PREVIEW HANDLER BASE - Abstract Base for Preview Rendering
===============================================================================

FILE PURPOSE:
This file provides the base class for all preview handlers (GPU and software).
It contains shared logic for updating the preview window as you type.

WHAT THIS FILE DOES:
1. Debouncing (wait before updating preview - don't update on every keystroke!)
2. Coordinates with PreviewWorker (background thread for rendering)
3. Scroll synchronization (keep editor and preview in sync)
4. Statistics tracking (how long renders take, for adaptive behavior)

MA principle: Reduced from 665→503→~380 lines by extracting:
- preview_constants.py (constants)
- preview_css_manager.py (CSS generation, caching, error HTML)

ARCHITECTURE:
PreviewHandlerBase (this file - abstract base)
    ├── PreviewHandlerGPU (QWebEngineView - GPU accelerated)
    └── PreviewHandlerCPU (QTextBrowser - software fallback)

VERSION: 2.0.9 (MA refactoring - CSS manager extraction)
"""

# === STANDARD LIBRARY IMPORTS ===
import logging
import time
from abc import abstractmethod
from typing import Any

# === QT FRAMEWORK IMPORTS ===
from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtWidgets import QPlainTextEdit, QWidget

# === LOCAL IMPORTS ===
from asciidoc_artisan.ui.preview_constants import (
    PREVIEW_FAST_INTERVAL_MS,
    PREVIEW_INSTANT_MS,
    PREVIEW_NORMAL_INTERVAL_MS,
    PREVIEW_SLOW_INTERVAL_MS,
)
from asciidoc_artisan.ui.preview_css_manager import PreviewCSSManager

# === OPTIONAL IMPORTS (Adaptive Debouncer) ===
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

# === LOGGING SETUP ===
logger = logging.getLogger(__name__)


class PreviewHandlerBase(QObject):
    """
    Preview Handler Base - Abstract Base Class for All Preview Handlers.

    WHAT THIS CLASS PROVIDES:
    - Debouncing logic (wait before updating preview)
    - CSS generation (styling for dark/light themes)
    - Preview rendering coordination
    - Error handling
    - Scroll synchronization
    - Statistics tracking (render times, document sizes)

    WHAT SUBCLASSES MUST IMPLEMENT:
    - _set_preview_html() - Update widget with rendered HTML
    - _scroll_preview_to_percentage() - Scroll preview to match editor
    - _get_preview_scroll_percentage() - Get preview scroll position

    SIGNALS:
    - preview_updated: Fired when preview HTML changes
    - preview_error: Fired when rendering fails
    """

    # === QT SIGNALS ===
    preview_updated = Signal(str)
    preview_error = Signal(str)

    def __init__(self, editor: QPlainTextEdit, preview: QWidget, parent_window: QObject):
        """
        Initialize PreviewHandlerBase.

        Args:
            editor: The text editor widget
            preview: The preview widget (QTextBrowser or QWebEngineView)
            parent_window: Main window (for signals and state)
        """
        super().__init__(parent_window)
        self.editor = editor
        self.preview = preview
        self.window = parent_window

        # Preview state
        self.sync_scrolling_enabled = True
        self.is_syncing_scroll = False

        # CSS manager (extracted per MA principle)
        self._css_manager = PreviewCSSManager(parent_window)  # type: ignore[arg-type]

        # Preview timer (adaptive based on document size)
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)

        # Adaptive debouncer (if available)
        self._adaptive_debouncer: Any | None = None
        self._use_adaptive_debouncing = True
        self._last_render_start: float | None = None

        if ADAPTIVE_DEBOUNCER_AVAILABLE and AdaptiveDebouncer:
            self._adaptive_debouncer = AdaptiveDebouncer()
            logger.info("Adaptive debouncing enabled")

        # Cursor position tracking (v1.6.0 for predictive rendering)
        self._current_cursor_line = 0
        self.editor.cursorPositionChanged.connect(self._on_cursor_position_changed)

        # Connect editor text changes to preview updates
        self.editor.textChanged.connect(self._on_text_changed)

    def _on_cursor_position_changed(self) -> None:
        """Handle cursor position changes (v1.6.0 for predictive rendering)."""
        cursor = self.editor.textCursor()
        self._current_cursor_line = cursor.blockNumber()

        # Notify preview worker for predictive rendering
        if hasattr(self.window, "preview_worker"):
            worker = self.window.preview_worker
            if hasattr(worker, "update_cursor_position"):
                worker.update_cursor_position(self._current_cursor_line)

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

        Uses adaptive timing based on document size, CPU load, render times.
        """
        # Cancel any pending update
        self.preview_timer.stop()

        # Get document size
        text_size = len(self.editor.toPlainText())

        # Use adaptive debouncing if available
        if self._use_adaptive_debouncing and self._adaptive_debouncer:
            self._adaptive_debouncer.on_text_changed()
            delay = self._adaptive_debouncer.calculate_delay(document_size=text_size)
        else:
            # Fall back to simple size-based delay
            delay = self._calculate_simple_delay(text_size)

        # Request predictive pre-rendering during debounce (v1.6.0)
        if hasattr(self.window, "preview_worker"):
            worker = self.window.preview_worker
            if hasattr(worker, "request_prediction"):
                source_text = self.editor.toPlainText()
                worker.request_prediction(source_text, self._current_cursor_line)

        # Start timer with calculated delay
        self.preview_timer.start(delay)

    def _calculate_simple_delay(self, text_size: int) -> int:
        """Calculate simple size-based delay.

        Args:
            text_size: Document size in characters

        Returns:
            Delay in milliseconds
        """
        if text_size < 1000:
            return PREVIEW_INSTANT_MS
        elif text_size < 10000:
            return PREVIEW_FAST_INTERVAL_MS
        elif text_size < 100000:
            return PREVIEW_NORMAL_INTERVAL_MS
        else:
            return PREVIEW_SLOW_INTERVAL_MS

    @Slot()
    def update_preview(self) -> None:
        """Update preview with current editor content."""
        source_text = self.editor.toPlainText()

        # Track render start time
        self._last_render_start = time.time()

        # Emit signal to worker for rendering
        if hasattr(self.window, "request_preview_render"):
            self.window.request_preview_render.emit(source_text)

        logger.debug(f"Preview update requested ({len(source_text)} chars)")

    def handle_preview_complete(self, html: str) -> None:
        """
        Handle completed preview rendering from worker (template method).

        Args:
            html: Rendered HTML content
        """
        # Calculate render time
        if self._last_render_start is not None:
            render_time = time.time() - self._last_render_start

            # Update adaptive debouncer
            if self._adaptive_debouncer:
                self._adaptive_debouncer.on_render_complete(render_time)

            logger.debug(f"Render completed in {render_time:.3f}s")

        # Add CSS styling (delegated to CSS manager)
        styled_html = self._css_manager.wrap_with_css(html)

        # Update widget (delegate to subclass)
        self._set_preview_html(styled_html)

        # Emit signal
        self.preview_updated.emit(html)

        logger.debug(f"Preview updated successfully ({self.__class__.__name__})")

    @abstractmethod
    def _set_preview_html(self, html: str) -> None:
        """
        Set HTML in preview widget (widget-specific implementation).

        Args:
            html: Styled HTML content to display
        """
        pass

    def handle_preview_error(self, error: str) -> None:
        """
        Handle preview rendering error with security headers.

        Args:
            error: Error message
        """
        error_html = self._css_manager.build_error_html(error)
        # Use subclass method for thread-safe setHtml
        self._set_preview_html(error_html)
        self.preview_error.emit(error)

    # === CSS DELEGATION METHODS (backward compatibility) ===

    def get_preview_css(self) -> str:
        """Get preview CSS (delegated to CSS manager)."""
        return self._css_manager.get_preview_css()

    def set_custom_css(self, css: str) -> None:
        """Set custom CSS for preview (delegated to CSS manager)."""
        self._css_manager.set_custom_css(css)
        self.preview_timer.start(100)

    def clear_css_cache(self) -> None:
        """Clear CSS cache (delegated to CSS manager)."""
        self._css_manager.clear_cache()

    def enable_sync_scrolling(self, enabled: bool) -> None:
        """Enable or disable synchronized scrolling.

        Args:
            enabled: True to enable, False to disable
        """
        self.sync_scrolling_enabled = enabled
        logger.info(f"Sync scrolling {'enabled' if enabled else 'disabled'}")

    def sync_editor_to_preview(self, editor_value: int) -> None:
        """Sync preview scroll position to editor (template method).

        Args:
            editor_value: Editor scroll bar value (0-max)
        """
        if not self.sync_scrolling_enabled or self.is_syncing_scroll:
            return

        self.is_syncing_scroll = True
        try:
            editor_scrollbar = self.editor.verticalScrollBar()
            editor_max = editor_scrollbar.maximum()

            if editor_max > 0:
                scroll_percentage = editor_value / editor_max
                self._scroll_preview_to_percentage(scroll_percentage)

        finally:
            self.is_syncing_scroll = False

    @abstractmethod
    def _scroll_preview_to_percentage(self, percentage: float) -> None:
        """Scroll preview widget to percentage (widget-specific).

        Args:
            percentage: Scroll position as percentage (0.0 to 1.0)
        """
        pass

    def sync_preview_to_editor(self, preview_value: int) -> None:
        """Sync editor scroll position to preview (template method).

        Args:
            preview_value: Preview scroll value (widget-specific units)
        """
        if not self.sync_scrolling_enabled or self.is_syncing_scroll:
            return

        self.is_syncing_scroll = True
        try:
            scroll_percentage = self._get_preview_scroll_percentage()

            if scroll_percentage is not None:
                editor_scrollbar = self.editor.verticalScrollBar()
                editor_max = editor_scrollbar.maximum()
                editor_value = int(editor_max * scroll_percentage)
                editor_scrollbar.setValue(editor_value)

        finally:
            self.is_syncing_scroll = False

    @abstractmethod
    def _get_preview_scroll_percentage(self) -> float | None:
        """Get current scroll percentage from preview widget.

        Returns:
            Scroll percentage (0.0 to 1.0), or None if not available
        """
        pass

    def clear_preview(self) -> None:
        """Clear preview content with security headers."""
        clear_html = self._css_manager.build_clear_html()
        # Use subclass method for thread-safe setHtml
        self._set_preview_html(clear_html)
        logger.debug("Preview cleared")

    def get_preview_html(self) -> str:
        """Get current preview HTML (async - use with callback)."""
        return ""

    def set_adaptive_debouncing(self, enabled: bool) -> None:
        """Enable or disable adaptive debouncing.

        Args:
            enabled: True to enable, False to disable
        """
        self._use_adaptive_debouncing = enabled
        logger.info(f"Adaptive debouncing {'enabled' if enabled else 'disabled'}")

    def get_debouncer_stats(self) -> dict[str, Any]:
        """Get adaptive debouncer statistics.

        Returns:
            Dictionary with stats, or empty dict if not available
        """
        if self._adaptive_debouncer:
            return self._adaptive_debouncer.get_statistics()  # type: ignore[no-any-return]
        return {}

    def reset_debouncer(self) -> None:
        """Reset adaptive debouncer state."""
        if self._adaptive_debouncer:
            self._adaptive_debouncer.reset()
            logger.debug("Adaptive debouncer reset")
