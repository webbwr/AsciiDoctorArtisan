"""
GPU-Enabled Preview Handler - Automatically detect and use GPU when available.

This module provides a drop-in replacement for preview_handler.py that:
- Detects GPU availability automatically
- Uses QWebEngineView when GPU is available
- Falls back to QTextBrowser for software rendering
- Provides the same API as the original PreviewHandler

To enable, replace the import in main_window.py:
    from asciidoc_artisan.ui.preview_handler_gpu import PreviewHandler
"""

import logging
from typing import Optional

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QTextBrowser, QWidget

from asciidoc_artisan.core.gpu_detection import get_gpu_info

# Import base handler
from asciidoc_artisan.ui.preview_handler import PreviewHandler as BasePreviewHandler

# Try to import QWebEngineView (may not be available)
try:
    from PySide6.QtWebEngineCore import QWebEngineSettings
    from PySide6.QtWebEngineWidgets import QWebEngineView

    WEBENGINE_AVAILABLE = True
except ImportError:
    QWebEngineView = None
    QWebEngineSettings = None
    WEBENGINE_AVAILABLE = False

logger = logging.getLogger(__name__)


def create_preview_widget(parent: Optional[QWidget] = None) -> QWidget:
    """
    Create appropriate preview widget based on GPU availability.

    Returns:
        QWebEngineView if GPU available, QTextBrowser otherwise
    """
    if not WEBENGINE_AVAILABLE:
        logger.info("QWebEngineView not available, using QTextBrowser")
        return QTextBrowser(parent)

    # Detect GPU
    gpu_info = get_gpu_info()

    if gpu_info.can_use_webengine and gpu_info.has_gpu:
        logger.info(
            f"GPU detected ({gpu_info.gpu_name}), using QWebEngineView with acceleration"
        )

        # Create QWebEngineView with GPU acceleration
        web_view = QWebEngineView(parent)

        # Enable hardware acceleration
        settings = web_view.settings()
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)

        # Log GPU info
        logger.info(f"  GPU Type: {gpu_info.gpu_type}")
        logger.info(f"  GPU Name: {gpu_info.gpu_name}")
        if gpu_info.driver_version:
            logger.info(f"  Driver: {gpu_info.driver_version}")
        logger.info(f"  Device: {gpu_info.render_device}")
        logger.info("  Accelerated2dCanvas: ENABLED")
        logger.info("  WebGL: ENABLED")

        return web_view
    else:
        logger.info(f"Using QTextBrowser: {gpu_info.reason}")
        return QTextBrowser(parent)


class PreviewHandler(BasePreviewHandler):
    """
    GPU-enabled preview handler.

    Drop-in replacement for the base PreviewHandler that automatically
    detects and uses GPU acceleration when available.

    Usage in main_window.py:
        # Replace:
        # from asciidoc_artisan.ui.preview_handler import PreviewHandler
        # with:
        from asciidoc_artisan.ui.preview_handler_gpu import PreviewHandler
    """

    def __init__(self, editor, preview, parent_window):
        """
        Initialize GPU-enabled PreviewHandler.

        Note: This expects the preview widget to be created by
        create_preview_widget() function, not passed in pre-created.
        """
        # Detect if preview is QWebEngineView or QTextBrowser
        self.is_webengine = hasattr(preview, "page")

        # Initialize base handler
        super().__init__(editor, preview, parent_window)

        if self.is_webengine:
            logger.info("Preview handler initialized with QWebEngineView (GPU-accelerated)")
        else:
            logger.info("Preview handler initialized with QTextBrowser (software rendering)")

    def handle_preview_complete(self, html: str) -> None:
        """
        Handle completed preview rendering (GPU-aware).

        Args:
            html: Rendered HTML content
        """
        # Calculate render time
        if self._last_render_start is not None:
            import time

            render_time = time.time() - self._last_render_start

            # Update adaptive debouncer with render time
            if self._adaptive_debouncer:
                self._adaptive_debouncer.on_render_complete(render_time)

            logger.debug(f"Render completed in {render_time:.3f}s")

        # Add CSS styling
        styled_html = self._wrap_with_css(html)

        # Update preview (different methods for QWebEngineView vs QTextBrowser)
        if self.is_webengine:
            # QWebEngineView uses setHtml with base URL
            self.preview.setHtml(styled_html, QUrl("file://"))
        else:
            # QTextBrowser uses simple setHtml
            self.preview.setHtml(styled_html)

        # Emit signal
        self.preview_updated.emit(html)

        logger.debug("Preview updated successfully")

    def sync_editor_to_preview(self, editor_value: int) -> None:
        """
        Sync preview scroll position to editor (GPU-aware).

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

                if self.is_webengine:
                    # QWebEngineView: Use JavaScript
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
                else:
                    # QTextBrowser: Direct scrollbar control
                    preview_scrollbar = self.preview.verticalScrollBar()
                    preview_max = preview_scrollbar.maximum()
                    preview_value = int(preview_max * scroll_percentage)
                    preview_scrollbar.setValue(preview_value)

        finally:
            self.is_syncing_scroll = False


def get_preview_widget_info(preview_widget: QWidget) -> dict:
    """
    Get information about the preview widget.

    Args:
        preview_widget: Preview widget (QWebEngineView or QTextBrowser)

    Returns:
        Dictionary with widget info
    """
    widget_type = type(preview_widget).__name__
    is_webengine = hasattr(preview_widget, "page")

    info = {
        "widget_type": widget_type,
        "is_webengine": is_webengine,
        "is_textbrowser": isinstance(preview_widget, QTextBrowser),
    }

    if is_webengine and WEBENGINE_AVAILABLE:
        settings = preview_widget.settings()
        info["accelerated_2d_canvas"] = settings.testAttribute(
            QWebEngineSettings.Accelerated2dCanvasEnabled
        )
        info["webgl_enabled"] = settings.testAttribute(QWebEngineSettings.WebGLEnabled)

    # Add GPU info
    gpu_info = get_gpu_info()
    info["gpu_detected"] = gpu_info.has_gpu
    info["gpu_name"] = gpu_info.gpu_name
    info["gpu_type"] = gpu_info.gpu_type

    return info
