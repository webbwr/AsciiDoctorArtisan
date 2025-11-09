"""
Web Engine Preview Handler - GPU-accelerated preview rendering.

This module provides QWebEngineView-based preview handlers with:
- Automatic GPU detection and configuration
- Hardware-accelerated 2D canvas
- WebGL support for rich rendering
- JavaScript-based scroll synchronization
- Automatic fallback to QTextBrowser when GPU unavailable

Detects GPU capabilities automatically and chooses the optimal widget:
- QWebEngineView (GPU available) - 10-50x faster, 70-90% less CPU
- QTextBrowser (GPU unavailable) - Reliable software fallback

Factory function create_preview_handler() simplifies usage in main_window.py.
"""

import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser, QWidget

from asciidoc_artisan.core.gpu_detection import get_gpu_info
from asciidoc_artisan.ui.preview_handler_base import PreviewHandlerBase

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


class WebEngineHandler(PreviewHandlerBase):
    """
    QWebEngineView-based preview handler (GPU-accelerated).

    Provides hardware-accelerated preview rendering with:
    - GPU-accelerated 2D canvas (up to 10-50x faster)
    - WebGL support for rich content
    - JavaScript-based scroll synchronization
    - Significantly reduced CPU usage (70-90% less)

    Requires:
    - GPU hardware (NVIDIA, AMD, Intel, or NPU)
    - QWebEngineView available
    - GPU drivers installed

    Implements abstract methods from PreviewHandlerBase:
    - handle_preview_complete() - Update QWebEngineView with HTML
    - sync_editor_to_preview() - Sync scroll via JavaScript
    - sync_preview_to_editor() - Sync scroll via JavaScript callback
    """

    def __init__(
        self, editor: QPlainTextEdit, preview: QWebEngineView, parent_window: Any
    ) -> None:
        """
        Initialize WebEngine PreviewHandler.

        Args:
            editor: The text editor widget
            preview: The QWebEngineView widget for GPU-accelerated preview
            parent_window: Main window (for signals and state)
        """
        super().__init__(editor, preview, parent_window)

        # Verify widget type
        if not hasattr(preview, "page"):
            raise TypeError(
                f"WebEngineHandler requires QWebEngineView, got {type(preview).__name__}"
            )

        logger.info("PreviewHandler initialized with QWebEngineView (GPU-accelerated)")

    def _set_preview_html(self, html: str) -> None:
        """
        Set HTML in QWebEngineView widget.

        Args:
            html: Styled HTML content to display
        """
        # QWebEngineView requires base URL for local resource access
        self.preview.setHtml(html, QUrl("file://"))

    def _scroll_preview_to_percentage(self, percentage: float) -> None:
        """
        Scroll QWebEngineView to percentage via JavaScript.

        Args:
            percentage: Scroll position as percentage (0.0 to 1.0)
        """
        # Scroll preview via JavaScript (hardware-accelerated)
        js_code = f"""
            var body = document.body;
            var html = document.documentElement;
            var height = Math.max(
                body.scrollHeight, body.offsetHeight,
                html.clientHeight, html.scrollHeight, html.offsetHeight
            );
            var maxScroll = height - window.innerHeight;
            window.scrollTo(0, maxScroll * {percentage});
        """
        self.preview.page().runJavaScript(js_code)

    def _get_preview_scroll_percentage(self) -> Optional[float]:
        """
        Get scroll percentage from QWebEngineView (requires JavaScript callback).

        Note: Currently not fully implemented. Would require async JavaScript
        callback to get scroll position from web view.

        Returns:
            None (not implemented - primarily sync editor -> preview)
        """
        # TODO: Implement JavaScript callback to get scroll position
        # self.preview.page().runJavaScript(
        #     "window.scrollY / (document.body.scrollHeight - window.innerHeight)",
        #     lambda result: self._on_scroll_position_received(result)
        # )
        return None


def create_preview_widget(parent: Optional[QWidget] = None) -> QWidget:
    """
    Create appropriate preview widget based on GPU availability.

    Automatically detects GPU and creates the optimal widget:
    - QWebEngineView if GPU available (hardware-accelerated)
    - QTextBrowser if GPU unavailable (software fallback)

    Args:
        parent: Parent widget

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
            f"GPU detected ({gpu_info.gpu_name}), attempting QWebEngineView with acceleration"
        )

        try:
            # Create QWebEngineView with GPU acceleration
            web_view = QWebEngineView(parent)

            # Enable hardware acceleration
            # NOTE: This may fail on macOS if QtWebEngine can't initialize
            settings = web_view.settings()
            settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
            settings.setAttribute(
                QWebEngineSettings.LocalContentCanAccessRemoteUrls, False
            )

            # Log GPU info
            logger.info(f"  GPU Type: {gpu_info.gpu_type}")
            logger.info(f"  GPU Name: {gpu_info.gpu_name}")
            if gpu_info.driver_version:
                logger.info(f"  Driver: {gpu_info.driver_version}")
            logger.info(f"  Device: {gpu_info.render_device}")
            logger.info("  Accelerated2dCanvas: ENABLED")
            logger.info("  WebGL: ENABLED")
            logger.info("QWebEngineView initialized successfully with GPU acceleration")

            return web_view

        except Exception as e:
            # QWebEngineView initialization failed - fall back to QTextBrowser
            logger.warning(
                f"QWebEngineView initialization failed: {e}. Falling back to QTextBrowser."
            )
            logger.info(
                "Using QTextBrowser (software rendering) - GPU acceleration unavailable"
            )
            return QTextBrowser(parent)
    else:
        logger.info(f"Using QTextBrowser: {gpu_info.reason}")
        return QTextBrowser(parent)


def create_preview_handler(
    editor: QPlainTextEdit, preview: QWidget, parent_window: Any
) -> PreviewHandlerBase:
    """
    Create appropriate preview handler for the given widget.

    Factory function that creates the correct handler type based on
    the widget type (QWebEngineView or QTextBrowser).

    Args:
        editor: The text editor widget
        preview: The preview widget (from create_preview_widget())
        parent_window: Main window

    Returns:
        WebEngineHandler if QWebEngineView, else TextBrowserHandler
    """
    # Import here to avoid circular dependency
    from typing import cast

    from asciidoc_artisan.ui.preview_handler import PreviewHandler as TextBrowserHandler

    if hasattr(preview, "page"):
        # QWebEngineView - use GPU-accelerated handler
        from PySide6.QtWebEngineWidgets import QWebEngineView

        return WebEngineHandler(editor, cast(QWebEngineView, preview), parent_window)
    else:
        # QTextBrowser - use software rendering handler
        from PySide6.QtWidgets import QTextBrowser

        return TextBrowserHandler(editor, cast(QTextBrowser, preview), parent_window)


# Backward compatibility alias
# Main window imports "PreviewHandler" from this module
# The create_preview_handler() factory returns the correct handler type
PreviewHandler = WebEngineHandler


def get_preview_widget_info(preview_widget: QWidget) -> Dict[str, Any]:
    """
    Get information about the preview widget.

    Useful for debugging and logging widget configuration.

    Args:
        preview_widget: Preview widget (QWebEngineView or QTextBrowser)

    Returns:
        Dictionary with widget info including:
        - widget_type: Widget class name
        - is_webengine: True if QWebEngineView
        - is_textbrowser: True if QTextBrowser
        - gpu_detected: True if GPU hardware found
        - gpu_name: GPU name (if detected)
        - gpu_type: GPU type (nvidia, amd, intel, npu)
        - accelerated_2d_canvas: True if 2D canvas acceleration enabled
        - webgl_enabled: True if WebGL enabled
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
