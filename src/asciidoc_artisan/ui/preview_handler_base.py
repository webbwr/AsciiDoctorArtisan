"""
===============================================================================
PREVIEW HANDLER BASE - Abstract Base for Preview Rendering
===============================================================================

FILE PURPOSE:
This file provides the base class for all preview handlers (GPU and software).
It contains shared logic for updating the preview window as you type.

WHAT THIS FILE DOES:
1. Debouncing (wait before updating preview - don't update on every keystroke!)
2. CSS generation (styling for dark/light themes)
3. Coordinates with PreviewWorker (background thread for rendering)
4. Scroll synchronization (keep editor and preview in sync)
5. Statistics tracking (how long renders take, for adaptive behavior)

FOR BEGINNERS - WHAT IS A PREVIEW?:
The preview window shows what your AsciiDoc document looks like when formatted.
As you type in the editor, the preview updates to show the result.

ANALOGY:
Think of a cooking show where you see the chef cooking AND the finished dish:
- Editor = the chef chopping vegetables (raw AsciiDoc text)
- Preview = the finished dish on the plate (formatted HTML)
- This file = the camera operator deciding when to show the finished dish

WHY ABSTRACT BASE CLASS?:
We have TWO types of preview:
1. GPU Preview (QWebEngineView) - fast, hardware-accelerated (10-50x faster)
2. Software Preview (QTextBrowser) - slower, but works everywhere

Both need the same basic features (debouncing, CSS, scroll sync). Instead of
duplicating code, we put common logic HERE (base class) and each preview
type adds its specific implementation (concrete classes).

KEY CONCEPTS:

1. DEBOUNCING:
   Without debouncing: Preview updates on EVERY KEYSTROKE (slow, CPU-intensive)
   With debouncing: Wait 200-1000ms after typing stops, THEN update preview

   Why? If you type "Hello World" quickly:
   - Without debouncing: Renders 11 times (H, He, Hel, Hell, Hello, ...)
   - With debouncing: Renders once when you stop typing ("Hello World")

2. ADAPTIVE DEBOUNCING:
   - Small documents: Update fast (200ms delay)
   - Large documents: Update slow (1000ms delay)
   - Slow renders: Increase delay automatically
   - Fast renders: Decrease delay automatically

3. CSS GENERATION:
   - Dark theme: Dark background, light text
   - Light theme: Light background, dark text
   - CSS is cached (don't regenerate every time)

4. CONTENT SECURITY POLICY (CSP):
   - Prevents XSS attacks (malicious JavaScript in preview)
   - Blocks external resources, form submissions, plugins

SPECIFICATIONS IMPLEMENTED:
- FR-013 to FR-020: Preview rendering and synchronization
- NFR-008: Preview update debouncing (adaptive)
- NFR-009: Scroll synchronization
- SEC-001: Content Security Policy (XSS protection)

ARCHITECTURE:
PreviewHandlerBase (this file - abstract base)
    ├── PreviewHandlerGPU (QWebEngineView - GPU accelerated)
    └── PreviewHandlerCPU (QTextBrowser - software fallback)

REFACTORING HISTORY:
- v1.0: All preview logic in main_window.py
- v1.4.0: Extracted to preview_handler.py (GPU), preview_handler_gpu.py
- v1.5.0: Refactored to base class pattern (DRY - eliminate duplication)

VERSION: 1.5.0 (Base class refactoring)
"""

# === STANDARD LIBRARY IMPORTS ===
import logging  # For recording what the program does
import time  # For timing render performance
from abc import abstractmethod  # For creating abstract base classes
from typing import Any, Dict, Optional  # Type hints

# === QT FRAMEWORK IMPORTS ===
from PySide6.QtCore import (
    QObject,  # Base class for Qt objects (signal/slot support)
    QTimer,  # Timer for debouncing preview updates
    Signal,  # Qt signal class (publish/subscribe pattern)
    Slot,  # Qt slot decorator (marks methods that receive signals)
)
from PySide6.QtWidgets import (
    QPlainTextEdit,  # Text editor widget
    QWidget,  # Base widget class
)

# === OPTIONAL IMPORTS (Adaptive Debouncer) ===
# Try to import adaptive debouncer - graceful degradation if not available
try:
    from asciidoc_artisan.core.adaptive_debouncer import (
        AdaptiveDebouncer,  # Adaptive delay calculator
        DebounceConfig,  # Configuration for debouncing
    )

    ADAPTIVE_DEBOUNCER_AVAILABLE = True  # Flag: Feature available
except ImportError:
    # If import fails, set to None and disable feature
    AdaptiveDebouncer = None
    DebounceConfig = None
    ADAPTIVE_DEBOUNCER_AVAILABLE = False  # Flag: Feature disabled

# === LOGGING SETUP ===
logger = logging.getLogger(__name__)


# === DEBOUNCE INTERVAL CONSTANTS ===
# These define how long to wait before updating preview
# Shorter intervals = faster updates but more CPU usage
PREVIEW_FAST_INTERVAL_MS = 200  # 200ms for small documents (fast typing)
PREVIEW_NORMAL_INTERVAL_MS = 500  # 500ms for medium documents (normal)
PREVIEW_SLOW_INTERVAL_MS = 1000  # 1000ms for large documents (slow typing)

# === CONTENT SECURITY POLICY (CSP) ===
# Security rules for preview HTML to prevent XSS attacks
# Applied to all HTML rendered in preview widget
CSP_POLICY = (
    "default-src 'self'; "  # Only load resources from same origin
    "script-src 'unsafe-eval'; "  # Allow Qt runJavaScript() for scroll sync
    "object-src 'none'; "  # Block plugins (Flash, Java applets, etc.)
    "style-src 'unsafe-inline'; "  # Allow inline CSS (required for AsciiDoc)
    "img-src 'self' data:; "  # Images from same origin or data URIs only
    "base-uri 'self'; "  # Restrict base URL (prevent base tag attacks)
    "form-action 'none'"  # Block all form submissions (no forms in preview)
)


class PreviewHandlerBase(QObject):
    """
    Preview Handler Base - Abstract Base Class for All Preview Handlers.

    FOR BEGINNERS - ABSTRACT BASE CLASS:
    An abstract base class is like a template or blueprint. It says:
    "All preview handlers MUST have these features" but doesn't specify
    exactly HOW to implement them. Concrete classes (GPU/CPU handlers)
    provide the specific implementation.

    WHAT THIS CLASS PROVIDES:
    - Debouncing logic (wait before updating preview)
    - CSS generation (styling for dark/light themes)
    - Preview rendering coordination
    - Error handling
    - Scroll synchronization
    - Statistics tracking (render times, document sizes)

    WHAT SUBCLASSES MUST IMPLEMENT:
    - handle_preview_complete() - Update widget with rendered HTML
    - sync_editor_to_preview() - Scroll preview to match editor
    - sync_preview_to_editor() - Scroll editor to match preview

    WHY ABSTRACT BASE CLASS?:
    GPU and CPU previews need the same debouncing, CSS, and coordination
    logic. Instead of duplicating code, we put it here. Each preview type
    just adds its widget-specific operations.

    SIGNALS:
    - preview_updated: Fired when preview HTML changes
    - preview_error: Fired when rendering fails
    """

    # === QT SIGNALS ===
    # These are "events" that other parts of the app can listen to
    preview_updated = Signal(str)  # Emits HTML when preview updates
    preview_error = Signal(str)  # Emits error message when render fails

    def __init__(
        self, editor: QPlainTextEdit, preview: QWidget, parent_window: QObject
    ):
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
        self._css_cache: Optional[str] = None
        self._custom_css: str = ""  # Custom CSS for font settings

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

        # Cursor position tracking (v1.6.0 for predictive rendering)
        self._current_cursor_line = 0
        self.editor.cursorPositionChanged.connect(self._on_cursor_position_changed)

        # Connect editor text changes to preview updates
        self.editor.textChanged.connect(self._on_text_changed)

    def _on_cursor_position_changed(self) -> None:
        """
        Handle cursor position changes (v1.6.0 for predictive rendering).

        Tracks cursor line and notifies preview worker for prediction.
        """
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

        # Request predictive pre-rendering during debounce (v1.6.0)
        if hasattr(self.window, "preview_worker"):
            worker = self.window.preview_worker
            if hasattr(worker, "request_prediction"):
                source_text = self.editor.toPlainText()
                worker.request_prediction(source_text, self._current_cursor_line)

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

    @abstractmethod
    def handle_preview_complete(self, html: str) -> None:
        """
        Handle completed preview rendering from worker.

        Must be implemented by subclass to update the specific widget type.

        Args:
            html: Rendered HTML content
        """
        pass

    def handle_preview_error(self, error: str) -> None:
        """
        Handle preview rendering error with security headers.

        Security:
            - Applies CSP to error display HTML to prevent XSS
            - Same security policy as preview content

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
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Security-Policy" content="{CSP_POLICY}">
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
        Wrap HTML content with CSS styling and security headers.

        Security:
            - Content Security Policy (CSP) prevents XSS attacks
            - Restricts script execution, plugin loading, and external resources
            - Allows inline CSS for AsciiDoc styling requirements

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

    def get_preview_css(self) -> str:
        """
        Get preview CSS (cached for performance).

        Returns:
            CSS content as string (includes custom CSS for fonts)
        """
        if self._css_cache is None:
            self._css_cache = self._generate_preview_css()

        # Append custom CSS (for font settings)
        if self._custom_css:
            return self._css_cache + "\n" + self._custom_css

        return self._css_cache

    def set_custom_css(self, css: str) -> None:
        """
        Set custom CSS for preview (e.g., font settings).

        Args:
            css: Custom CSS string to append to preview CSS
        """
        self._custom_css = css
        # Clear cache to force regeneration with new custom CSS
        self._css_cache = None
        # Trigger preview update to apply new CSS
        self.preview_timer.start(100)  # Schedule update in 100ms
        logger.debug("Custom CSS applied to preview")

    def clear_css_cache(self) -> None:
        """Clear CSS cache (call when theme changes)."""
        self._css_cache = None
        logger.debug("CSS cache cleared")

    def _generate_preview_css(self) -> str:
        """
        Generate preview CSS by delegating to ThemeManager.

        Returns:
            CSS content as string
        """
        # Delegate to ThemeManager for single source of truth
        if hasattr(self.window, "theme_manager"):
            return self.window.theme_manager.get_preview_css()  # type: ignore[no-any-return]  # ThemeManager returns Any

        # Fallback CSS if ThemeManager not available (shouldn't happen in production)
        return """
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
            }
        """

    def enable_sync_scrolling(self, enabled: bool) -> None:
        """
        Enable or disable synchronized scrolling.

        Args:
            enabled: True to enable, False to disable
        """
        self.sync_scrolling_enabled = enabled
        logger.info(f"Sync scrolling {'enabled' if enabled else 'disabled'}")

    @abstractmethod
    def sync_editor_to_preview(self, editor_value: int) -> None:
        """
        Sync preview scroll position to editor.

        Must be implemented by subclass for specific widget type.

        Args:
            editor_value: Editor scroll bar value (0-max)
        """
        pass

    @abstractmethod
    def sync_preview_to_editor(self, preview_value: int) -> None:
        """
        Sync editor scroll position to preview.

        Must be implemented by subclass for specific widget type.

        Args:
            preview_value: Preview scroll value
        """
        pass

    def clear_preview(self) -> None:
        """
        Clear preview content with security headers.

        Security:
            - Applies CSP even to cleared/empty preview state
        """
        clear_html = f"""
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
        self.preview.setHtml(clear_html)
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

    def get_debouncer_stats(self) -> Dict[str, Any]:
        """
        Get adaptive debouncer statistics.

        Returns:
            Dictionary with stats, or empty dict if not available
        """
        if self._adaptive_debouncer:
            return self._adaptive_debouncer.get_statistics()  # type: ignore[no-any-return]  # AdaptiveDebouncer returns Any
        return {}

    def reset_debouncer(self) -> None:
        """Reset adaptive debouncer state."""
        if self._adaptive_debouncer:
            self._adaptive_debouncer.reset()
            logger.debug("Adaptive debouncer reset")
