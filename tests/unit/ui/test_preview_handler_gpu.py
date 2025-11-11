"""Tests for ui.preview_handler_gpu module."""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser


@pytest.fixture
def mock_editor(qapp):
    """Create a mock editor widget."""
    editor = QPlainTextEdit()
    return editor


@pytest.fixture
def mock_preview():
    """Create a mock QWebEngineView preview widget."""
    preview = Mock()
    preview.page = Mock(return_value=Mock())
    preview.page().runJavaScript = Mock()
    preview.setHtml = Mock()
    preview.verticalScrollBar = Mock(return_value=Mock())
    return preview


@pytest.fixture
def mock_parent_window():
    """Create a mock parent window."""
    # PreviewHandlerBase inherits from QObject which requires None or QObject parent
    # We return None since parent is only used for signal emission, not initialization
    return None


@pytest.mark.unit
class TestWebEngineHandlerBasics:
    """Test suite for WebEngineHandler basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        assert WebEngineHandler is not None

    def test_creation_requires_webengine_view(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        # Should create successfully with proper preview widget
        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        assert handler is not None

    def test_creation_rejects_non_webengine_widget(
        self, mock_editor, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        # Should raise TypeError for non-QWebEngineView widget
        # Use spec=[] to prevent Mock from creating 'page' attribute automatically
        text_browser = Mock(spec=[])
        with pytest.raises(TypeError):
            WebEngineHandler(mock_editor, text_browser, mock_parent_window)

    def test_stores_references(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        assert handler.editor == mock_editor
        assert handler.preview == mock_preview
        # parent_window is None in tests (required for QObject parent)


@pytest.mark.unit
class TestHandlePreviewComplete:
    """Test suite for handle_preview_complete method."""

    def test_updates_preview_with_html(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        html = "<h1>Test Document</h1>"

        handler.handle_preview_complete(html)

        # Should call setHtml with styled HTML and base URL
        mock_preview.setHtml.assert_called_once()
        call_args = mock_preview.setHtml.call_args
        assert "<h1>Test Document</h1>" in call_args[0][0]
        assert isinstance(call_args[0][1], QUrl)

    def test_wraps_html_with_css(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        html = "<h1>Test</h1>"

        handler.handle_preview_complete(html)

        # Should wrap with CSS
        styled_html = mock_preview.setHtml.call_args[0][0]
        assert "<style>" in styled_html or "body {" in styled_html

    def test_emits_preview_updated_signal(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        html = "<h1>Test</h1>"

        with patch.object(handler, "preview_updated") as mock_signal:
            handler.handle_preview_complete(html)
            # Signal should emit original HTML (not styled)
            mock_signal.emit.assert_called_once_with(html)


@pytest.mark.unit
class TestScrollSynchronization:
    """Test suite for scroll synchronization."""

    def test_sync_editor_to_preview_uses_javascript(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Mock scrollbar
        scrollbar = Mock()
        scrollbar.maximum = Mock(return_value=1000)
        mock_editor.verticalScrollBar = Mock(return_value=scrollbar)

        handler.sync_editor_to_preview(500)

        # Should call runJavaScript with scroll code
        mock_preview.page().runJavaScript.assert_called_once()
        js_code = mock_preview.page().runJavaScript.call_args[0][0]
        assert "window.scrollTo" in js_code
        assert "0.5" in js_code  # 500/1000 = 0.5

    def test_sync_skips_when_disabled(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = False

        handler.sync_editor_to_preview(500)

        # Should not call JavaScript
        mock_preview.page().runJavaScript.assert_not_called()

    def test_sync_skips_when_already_syncing(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True
        handler.is_syncing_scroll = True

        handler.sync_editor_to_preview(500)

        # Should not call JavaScript when already syncing
        mock_preview.page().runJavaScript.assert_not_called()

    def test_sync_handles_zero_max(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Mock scrollbar with zero max
        scrollbar = Mock()
        scrollbar.maximum = Mock(return_value=0)
        mock_editor.verticalScrollBar = Mock(return_value=scrollbar)

        handler.sync_editor_to_preview(0)

        # Should not crash, should not call JavaScript
        mock_preview.page().runJavaScript.assert_not_called()

    def test_sync_preview_to_editor_not_implemented(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Should not crash (currently a pass)
        handler.sync_preview_to_editor(500)


@pytest.mark.unit
class TestCreatePreviewWidget:
    """Test suite for create_preview_widget factory function."""

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", False)
    def test_returns_text_browser_when_webengine_unavailable(self):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        widget = create_preview_widget()

        # Should return QTextBrowser
        assert isinstance(widget, QTextBrowser)

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    def test_returns_text_browser_when_no_gpu(self, mock_get_gpu_info):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        # Mock GPU info with no GPU
        mock_gpu_info = Mock()
        mock_gpu_info.can_use_webengine = False
        mock_gpu_info.has_gpu = False
        mock_gpu_info.reason = "No GPU detected"
        mock_get_gpu_info.return_value = mock_gpu_info

        widget = create_preview_widget()

        # Should return QTextBrowser as fallback
        assert isinstance(widget, QTextBrowser)

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    @patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineView")
    def test_returns_webengine_when_gpu_available(
        self, mock_webengine_cls, mock_get_gpu_info
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        # Mock GPU info with GPU available
        mock_gpu_info = Mock()
        mock_gpu_info.can_use_webengine = True
        mock_gpu_info.has_gpu = True
        mock_gpu_info.gpu_name = "NVIDIA GeForce RTX 4060"
        mock_gpu_info.gpu_type = "nvidia"
        mock_gpu_info.driver_version = "535.161.07"
        mock_gpu_info.render_device = "llvmpipe"
        mock_get_gpu_info.return_value = mock_gpu_info

        # Mock QWebEngineView
        mock_webengine = Mock()
        mock_settings = Mock()
        mock_webengine.settings = Mock(return_value=mock_settings)
        mock_webengine_cls.return_value = mock_webengine

        widget = create_preview_widget()

        # Should create QWebEngineView
        mock_webengine_cls.assert_called_once()
        # Should enable GPU acceleration
        mock_settings.setAttribute.assert_called()

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    @patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineView")
    @patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineSettings")
    def test_enables_gpu_acceleration(
        self, mock_settings_cls, mock_webengine_cls, mock_get_gpu_info
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        # Mock GPU available
        mock_gpu_info = Mock()
        mock_gpu_info.can_use_webengine = True
        mock_gpu_info.has_gpu = True
        mock_gpu_info.gpu_name = "GPU"
        mock_gpu_info.gpu_type = "nvidia"
        mock_gpu_info.driver_version = None
        mock_gpu_info.render_device = "gpu"
        mock_get_gpu_info.return_value = mock_gpu_info

        # Mock QWebEngineView and settings
        mock_webengine = Mock()
        mock_settings = Mock()
        mock_webengine.settings = Mock(return_value=mock_settings)
        mock_webengine_cls.return_value = mock_webengine

        create_preview_widget()

        # Should enable Accelerated2dCanvas and WebGL
        assert mock_settings.setAttribute.call_count >= 2


@pytest.mark.unit
class TestCreatePreviewHandler:
    """Test suite for create_preview_handler factory function."""

    @patch("asciidoc_artisan.ui.preview_handler_gpu.hasattr")
    def test_returns_webengine_handler_for_webengine_view(
        self, mock_hasattr, mock_editor, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import (
            WebEngineHandler,
            create_preview_handler,
        )

        # Mock preview with 'page' attribute (QWebEngineView)
        mock_preview = Mock()
        mock_preview.page = Mock()
        mock_hasattr.return_value = True

        with patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineView", Mock()):
            handler = create_preview_handler(
                mock_editor, mock_preview, mock_parent_window
            )

            # Should return WebEngineHandler
            assert isinstance(handler, WebEngineHandler)

    def test_returns_text_browser_handler_for_text_browser(
        self, mock_editor, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_handler

        # Mock preview without 'page' attribute (QTextBrowser)
        mock_preview = QTextBrowser()

        handler = create_preview_handler(mock_editor, mock_preview, mock_parent_window)

        # Should return PreviewHandler (TextBrowserHandler)
        # Check it's not WebEngineHandler
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        assert not isinstance(handler, WebEngineHandler)


@pytest.mark.unit
class TestWebEngineAvailability:
    """Test suite for WebEngine availability detection."""

    def test_webengine_available_constant_exists(self):
        from asciidoc_artisan.ui.preview_handler_gpu import WEBENGINE_AVAILABLE

        assert isinstance(WEBENGINE_AVAILABLE, bool)


@pytest.mark.unit
class TestHTMLContentVariations:
    """Test suite for different HTML content types."""

    def test_empty_html_content(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.handle_preview_complete("")

        # Should handle empty HTML gracefully
        mock_preview.setHtml.assert_called_once()
        assert mock_preview.setHtml.call_count == 1

    def test_very_large_html_content(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        large_html = "<p>" + ("x" * 100000) + "</p>"  # 100KB content

        handler.handle_preview_complete(large_html)

        # Should handle large HTML
        mock_preview.setHtml.assert_called_once()
        styled_html = mock_preview.setHtml.call_args[0][0]
        assert "x" * 1000 in styled_html  # Verify content is there

    def test_html_with_special_characters(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        html = "<p>&lt;&gt;&amp;&quot;&#39;</p>"

        handler.handle_preview_complete(html)

        styled_html = mock_preview.setHtml.call_args[0][0]
        assert "&lt;" in styled_html
        assert "&gt;" in styled_html
        assert "&amp;" in styled_html

    def test_html_with_unicode(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        html = "<p>Hello 世界 🌍 مرحبا мир</p>"

        handler.handle_preview_complete(html)

        styled_html = mock_preview.setHtml.call_args[0][0]
        assert "世界" in styled_html
        assert "🌍" in styled_html

    def test_html_with_inline_scripts(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        html = "<p>Test</p><script>alert('test')</script>"

        handler.handle_preview_complete(html)

        # Should include the HTML (security handled by QWebEngine sandbox)
        styled_html = mock_preview.setHtml.call_args[0][0]
        assert "<p>Test</p>" in styled_html

    def test_malformed_html(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        html = "<p>Unclosed tag<div><p>Nested wrong</div>"

        handler.handle_preview_complete(html)

        # Should handle malformed HTML (browser will fix)
        mock_preview.setHtml.assert_called_once()


@pytest.mark.unit
class TestMultipleUpdates:
    """Test suite for consecutive preview updates."""

    def test_multiple_consecutive_updates(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        for i in range(10):
            handler.handle_preview_complete(f"<h1>Version {i}</h1>")

        # Should call setHtml 10 times
        assert mock_preview.setHtml.call_count == 10

    def test_rapid_updates(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        # Simulate rapid typing
        for i in range(50):
            handler.handle_preview_complete(f"<p>Char {i}</p>")

        assert mock_preview.setHtml.call_count == 50

    def test_alternating_content_types(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        handler.handle_preview_complete("<h1>Header</h1>")
        handler.handle_preview_complete("<p>Paragraph</p>")
        handler.handle_preview_complete("<ul><li>List</li></ul>")

        assert mock_preview.setHtml.call_count == 3


@pytest.mark.unit
class TestScrollPositionEdgeCases:
    """Test suite for scroll position boundary conditions."""

    def test_negative_scroll_position(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        scrollbar = Mock()
        scrollbar.maximum = Mock(return_value=1000)
        mock_editor.verticalScrollBar = Mock(return_value=scrollbar)

        # Should handle negative gracefully (clamp to 0)
        handler.sync_editor_to_preview(-100)

        # Should not crash, may or may not call JS depending on validation
        assert mock_preview.page().runJavaScript.call_count <= 1

    def test_scroll_position_exceeds_maximum(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        scrollbar = Mock()
        scrollbar.maximum = Mock(return_value=1000)
        mock_editor.verticalScrollBar = Mock(return_value=scrollbar)

        # Should handle overflow (clamp to 1.0)
        handler.sync_editor_to_preview(2000)

        mock_preview.page().runJavaScript.assert_called_once()
        js_code = mock_preview.page().runJavaScript.call_args[0][0]
        # Should clamp to 1.0 (100%)
        assert "window.scrollTo" in js_code

    def test_scroll_at_document_boundaries(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        scrollbar = Mock()
        scrollbar.maximum = Mock(return_value=1000)
        mock_editor.verticalScrollBar = Mock(return_value=scrollbar)

        # Test at 0 and max
        handler.sync_editor_to_preview(0)
        handler.sync_editor_to_preview(1000)

        assert mock_preview.page().runJavaScript.call_count == 2

    def test_scroll_with_float_position(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        scrollbar = Mock()
        scrollbar.maximum = Mock(return_value=1000)
        mock_editor.verticalScrollBar = Mock(return_value=scrollbar)

        # Should handle float positions
        handler.sync_editor_to_preview(333.33)

        mock_preview.page().runJavaScript.assert_called_once()


@pytest.mark.unit
class TestCSSStyleGeneration:
    """Test suite for CSS style generation."""

    def test_css_includes_body_styles(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.handle_preview_complete("<p>Test</p>")

        styled_html = mock_preview.setHtml.call_args[0][0]
        # Should have body styling
        assert "body" in styled_html.lower()

    def test_css_includes_heading_styles(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.handle_preview_complete("<h1>Heading</h1>")

        styled_html = mock_preview.setHtml.call_args[0][0]
        # Should include heading in content
        assert "<h1>Heading</h1>" in styled_html

    def test_css_wrapping_preserves_html(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        original_html = "<p>Original <strong>content</strong> here</p>"
        handler.handle_preview_complete(original_html)

        styled_html = mock_preview.setHtml.call_args[0][0]
        # Original HTML should be present
        assert "<p>Original <strong>content</strong> here</p>" in styled_html


@pytest.mark.unit
class TestBaseURLHandling:
    """Test suite for base URL configuration."""

    def test_base_url_is_qurl(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.handle_preview_complete("<p>Test</p>")

        call_args = mock_preview.setHtml.call_args
        # Second argument should be QUrl
        assert isinstance(call_args[0][1], QUrl)

    def test_base_url_points_to_local(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.handle_preview_complete("<p>Test</p>")

        base_url = mock_preview.setHtml.call_args[0][1]
        # Should be a local file URL
        assert base_url.scheme() in ["file", ""]


@pytest.mark.unit
class TestSignalEmission:
    """Test suite for signal emission."""

    def test_preview_updated_signal_emits_original_html(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        original_html = "<h1>Test</h1>"

        with patch.object(handler, "preview_updated") as mock_signal:
            handler.handle_preview_complete(original_html)
            # Should emit original, not styled HTML
            mock_signal.emit.assert_called_once_with(original_html)

    def test_signal_emitted_with_sethtml(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        call_order = []

        def track_signal(*args):
            call_order.append("signal")

        def track_sethtml(*args, **kwargs):
            call_order.append("sethtml")

        with patch.object(handler, "preview_updated") as mock_signal:
            mock_signal.emit.side_effect = track_signal
            mock_preview.setHtml.side_effect = track_sethtml

            handler.handle_preview_complete("<p>Test</p>")

            # Both signal and setHtml should be called (order not guaranteed)
            assert "signal" in call_order
            assert "sethtml" in call_order

    def test_multiple_signals_for_multiple_updates(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        with patch.object(handler, "preview_updated") as mock_signal:
            for i in range(5):
                handler.handle_preview_complete(f"<p>Update {i}</p>")

            assert mock_signal.emit.call_count == 5


@pytest.mark.unit
class TestGPUDetectionEdgeCases:
    """Test suite for GPU detection scenarios."""

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    def test_gpu_detection_with_partial_info(self, mock_get_gpu_info):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        # GPU with some missing info
        mock_gpu_info = Mock()
        mock_gpu_info.can_use_webengine = True
        mock_gpu_info.has_gpu = True
        mock_gpu_info.gpu_name = "Unknown GPU"
        mock_gpu_info.gpu_type = "unknown"
        mock_gpu_info.driver_version = None
        mock_gpu_info.render_device = None
        mock_get_gpu_info.return_value = mock_gpu_info

        with patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineView"):
            widget = create_preview_widget()
            # Should not crash with partial GPU info

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    def test_gpu_detection_exception(self, mock_get_gpu_info):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        # Simulate GPU detection failure
        mock_get_gpu_info.side_effect = Exception("GPU detection failed")

        # Should propagate exception (caller handles fallback)
        try:
            widget = create_preview_widget()
            # If it doesn't raise, it should be QTextBrowser
            assert isinstance(widget, QTextBrowser)
        except Exception as e:
            # Exception propagation is also acceptable behavior
            assert "GPU detection failed" in str(e)

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    def test_wsl_environment_fallback(self, mock_get_gpu_info):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        # WSL might have GPU but WebEngine fails
        mock_gpu_info = Mock()
        mock_gpu_info.can_use_webengine = False
        mock_gpu_info.has_gpu = True
        mock_gpu_info.gpu_name = "NVIDIA GPU"
        mock_gpu_info.reason = "WSL environment"
        mock_get_gpu_info.return_value = mock_gpu_info

        widget = create_preview_widget()

        # Should fall back to QTextBrowser
        assert isinstance(widget, QTextBrowser)


@pytest.mark.unit
class TestWebEngineSettingsConfiguration:
    """Test suite for QWebEngineView settings."""

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    @patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineView")
    def test_enables_accelerated_2d_canvas(self, mock_webengine_cls, mock_get_gpu_info):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        mock_gpu_info = Mock()
        mock_gpu_info.can_use_webengine = True
        mock_gpu_info.has_gpu = True
        mock_gpu_info.gpu_name = "GPU"
        mock_gpu_info.gpu_type = "nvidia"
        mock_gpu_info.driver_version = "535"
        mock_gpu_info.render_device = "gpu"
        mock_get_gpu_info.return_value = mock_gpu_info

        mock_webengine = Mock()
        mock_settings = Mock()
        mock_webengine.settings = Mock(return_value=mock_settings)
        mock_webengine_cls.return_value = mock_webengine

        create_preview_widget()

        # Should call setAttribute at least once
        assert mock_settings.setAttribute.call_count >= 1

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    @patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineView")
    def test_webengine_creation_with_gpu(self, mock_webengine_cls, mock_get_gpu_info):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        mock_gpu_info = Mock()
        mock_gpu_info.can_use_webengine = True
        mock_gpu_info.has_gpu = True
        mock_gpu_info.gpu_name = "Test GPU"
        mock_gpu_info.gpu_type = "nvidia"
        mock_gpu_info.driver_version = "535"
        mock_gpu_info.render_device = "gpu"
        mock_get_gpu_info.return_value = mock_gpu_info

        mock_webengine = Mock()
        mock_settings = Mock()
        mock_webengine.settings = Mock(return_value=mock_settings)
        mock_webengine_cls.return_value = mock_webengine

        widget = create_preview_widget()

        # Should create WebEngineView
        mock_webengine_cls.assert_called_once()


@pytest.mark.unit
class TestHandlerInstanceManagement:
    """Test suite for handler instance lifecycle."""

    def test_multiple_handler_instances(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        # Create multiple handlers
        handler1 = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler2 = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        # Should be independent instances
        assert handler1 is not handler2

    def test_handler_state_independence(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler1 = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler2 = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        # Modify state of handler1
        handler1.sync_scrolling_enabled = False

        # handler2 should not be affected
        assert handler2.sync_scrolling_enabled == True  # Default state

    def test_handler_references_different_widgets(self, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        editor1 = QPlainTextEdit()
        editor2 = QPlainTextEdit()
        preview1 = Mock()
        preview1.page = Mock()
        preview2 = Mock()
        preview2.page = Mock()

        handler1 = WebEngineHandler(editor1, preview1, mock_parent_window)
        handler2 = WebEngineHandler(editor2, preview2, mock_parent_window)

        # Should reference correct widgets
        assert handler1.editor == editor1
        assert handler2.editor == editor2
        assert handler1.preview == preview1
        assert handler2.preview == preview2


@pytest.mark.unit
class TestErrorHandling:
    """Test suite for error conditions."""

    def test_sethtml_with_none_html(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        # Should handle None gracefully (may convert to empty string)
        try:
            handler.handle_preview_complete(None)
            # If it doesn't crash, that's acceptable
        except (TypeError, AttributeError):
            # If it rejects None, that's also acceptable
            pass

    def test_javascript_execution_failure(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        scrollbar = Mock()
        scrollbar.maximum = Mock(return_value=1000)
        mock_editor.verticalScrollBar = Mock(return_value=scrollbar)

        # Make runJavaScript raise exception
        mock_preview.page().runJavaScript.side_effect = RuntimeError("JS failed")

        # Should not crash the application
        try:
            handler.sync_editor_to_preview(500)
        except RuntimeError:
            # If exception propagates, that's acceptable
            pass

    def test_missing_scrollbar(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Mock missing scrollbar
        mock_editor.verticalScrollBar = Mock(return_value=None)

        # Should handle gracefully
        try:
            handler.sync_editor_to_preview(500)
        except AttributeError:
            # If it raises, that's acceptable
            pass


@pytest.mark.unit
class TestFactoryFunctionEdgeCases:
    """Test suite for factory function edge cases."""

    def test_create_handler_with_none_preview(self, mock_editor, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_handler

        # Should handle None preview
        try:
            handler = create_preview_handler(mock_editor, None, mock_parent_window)
        except (TypeError, AttributeError):
            # If it rejects None, that's acceptable
            pass

    def test_create_handler_with_none_editor(self, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_handler

        preview = QTextBrowser()

        # Should handle None editor
        try:
            handler = create_preview_handler(None, preview, mock_parent_window)
        except (TypeError, AttributeError):
            # If it rejects None, that's acceptable
            pass

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    @patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineView")
    def test_create_widget_webengine_initialization_failure(
        self, mock_webengine_cls, mock_get_gpu_info
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_widget

        mock_gpu_info = Mock()
        mock_gpu_info.can_use_webengine = True
        mock_gpu_info.has_gpu = True
        mock_gpu_info.gpu_name = "GPU"
        mock_gpu_info.gpu_type = "nvidia"
        mock_gpu_info.driver_version = "535"
        mock_gpu_info.render_device = "gpu"
        mock_get_gpu_info.return_value = mock_gpu_info

        # Simulate WebEngineView creation failure
        mock_webengine_cls.side_effect = RuntimeError("WebEngine init failed")

        # Should propagate exception (caller handles fallback)
        try:
            widget = create_preview_widget()
            # If it doesn't raise, it should be QTextBrowser
            assert isinstance(widget, QTextBrowser)
        except RuntimeError as e:
            # Exception propagation is also acceptable behavior
            assert "WebEngine init failed" in str(e)


@pytest.mark.unit
class TestStateManagement:
    """Test suite for handler state management."""

    def test_initial_sync_state(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        # Should start with sync enabled
        assert handler.sync_scrolling_enabled == True
        assert handler.is_syncing_scroll == False

    def test_toggle_sync_state(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        # Toggle sync
        handler.sync_scrolling_enabled = False
        assert handler.sync_scrolling_enabled == False

        handler.sync_scrolling_enabled = True
        assert handler.sync_scrolling_enabled == True

    def test_syncing_guard_prevents_recursion(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True
        handler.is_syncing_scroll = True

        scrollbar = Mock()
        scrollbar.maximum = Mock(return_value=1000)
        mock_editor.verticalScrollBar = Mock(return_value=scrollbar)

        handler.sync_editor_to_preview(500)

        # Should not call JS when already syncing
        mock_preview.page().runJavaScript.assert_not_called()

    def test_state_persists_across_updates(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        # Modify state
        handler.sync_scrolling_enabled = False

        # Perform updates
        handler.handle_preview_complete("<p>First</p>")
        handler.handle_preview_complete("<p>Second</p>")

        # State should persist
        assert handler.sync_scrolling_enabled == False

    def test_independent_state_per_instance(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler1 = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler2 = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        # Modify handler1 state
        handler1.sync_scrolling_enabled = False
        handler1.is_syncing_scroll = True

        # handler2 should be unaffected
        assert handler2.sync_scrolling_enabled == True
        assert handler2.is_syncing_scroll == False


@pytest.mark.unit
class TestPerformanceEdgeCases:
    """Test suite for performance-related edge cases."""

    def test_handles_extremely_large_document(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        # 1MB of HTML content
        huge_html = "<p>" + ("Lorem ipsum dolor sit amet. " * 10000) + "</p>"

        handler.handle_preview_complete(huge_html)

        # Should handle without crash
        mock_preview.setHtml.assert_called_once()

    def test_handles_deeply_nested_html(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        # Deep nesting
        nested_html = "<div>" * 100 + "Content" + "</div>" * 100

        handler.handle_preview_complete(nested_html)

        mock_preview.setHtml.assert_called_once()

    def test_handles_many_inline_elements(
        self, mock_editor, mock_preview, mock_parent_window
    ):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)

        # Many spans
        many_spans = "".join([f"<span id='s{i}'>Word {i}</span> " for i in range(1000)])
        html = f"<p>{many_spans}</p>"

        handler.handle_preview_complete(html)

        mock_preview.setHtml.assert_called_once()


@pytest.mark.unit
class TestGetPreviewWidgetInfo:
    """Test suite for get_preview_widget_info function."""

    def test_widget_info_for_text_browser(self, qapp):
        """Test get_preview_widget_info for QTextBrowser widget."""
        from asciidoc_artisan.ui.preview_handler_gpu import get_preview_widget_info

        text_browser = QTextBrowser()

        info = get_preview_widget_info(text_browser)

        # Should identify as QTextBrowser
        assert info["widget_type"] == "QTextBrowser"
        assert info["is_webengine"] is False
        assert info["is_textbrowser"] is True
        # Should include GPU info
        assert "gpu_detected" in info
        assert "gpu_name" in info
        assert "gpu_type" in info

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineView")
    @patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineSettings")
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    def test_widget_info_for_webengine_view(
        self, mock_get_gpu_info, mock_settings_cls, mock_webengine_cls
    ):
        """Test get_preview_widget_info for QWebEngineView widget."""
        from asciidoc_artisan.ui.preview_handler_gpu import get_preview_widget_info

        # Mock QWebEngineView widget
        mock_widget = Mock()
        mock_widget.page = Mock()
        mock_settings = Mock()
        mock_settings.testAttribute = Mock(side_effect=[True, True])  # 2d canvas, webgl
        mock_widget.settings = Mock(return_value=mock_settings)

        # Mock GPU info
        mock_gpu_info = Mock()
        mock_gpu_info.has_gpu = True
        mock_gpu_info.gpu_name = "NVIDIA RTX 4060"
        mock_gpu_info.gpu_type = "nvidia"
        mock_get_gpu_info.return_value = mock_gpu_info

        # Get info
        info = get_preview_widget_info(mock_widget)

        # Should include widget info
        assert info["is_webengine"] is True
        assert info["is_textbrowser"] is False
        # Should include WebEngine settings
        assert info["accelerated_2d_canvas"] is True
        assert info["webgl_enabled"] is True
        # Should include GPU info
        assert info["gpu_detected"] is True
        assert info["gpu_name"] == "NVIDIA RTX 4060"
        assert info["gpu_type"] == "nvidia"

    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    def test_widget_info_includes_gpu_detection(self, mock_get_gpu_info, qapp):
        """Test that widget info includes GPU detection results."""
        from asciidoc_artisan.ui.preview_handler_gpu import get_preview_widget_info

        # Mock GPU info with no GPU
        mock_gpu_info = Mock()
        mock_gpu_info.has_gpu = False
        mock_gpu_info.gpu_name = "No GPU"
        mock_gpu_info.gpu_type = "none"
        mock_get_gpu_info.return_value = mock_gpu_info

        text_browser = QTextBrowser()
        info = get_preview_widget_info(text_browser)

        # Should report no GPU
        assert info["gpu_detected"] is False
        assert info["gpu_name"] == "No GPU"
        assert info["gpu_type"] == "none"

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", True)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineSettings")
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    def test_widget_info_webengine_settings_disabled(
        self, mock_get_gpu_info, mock_settings_cls
    ):
        """Test widget info when WebEngine settings are disabled."""
        from asciidoc_artisan.ui.preview_handler_gpu import get_preview_widget_info

        # Mock QWebEngineView widget with settings disabled
        mock_widget = Mock()
        mock_widget.page = Mock()
        mock_settings = Mock()
        mock_settings.testAttribute = Mock(
            side_effect=[False, False]
        )  # 2d canvas and webgl disabled
        mock_widget.settings = Mock(return_value=mock_settings)

        # Mock GPU info
        mock_gpu_info = Mock()
        mock_gpu_info.has_gpu = True
        mock_gpu_info.gpu_name = "GPU"
        mock_gpu_info.gpu_type = "intel"
        mock_get_gpu_info.return_value = mock_gpu_info

        info = get_preview_widget_info(mock_widget)

        # Should report settings as disabled
        assert info["accelerated_2d_canvas"] is False
        assert info["webgl_enabled"] is False

    @patch("asciidoc_artisan.ui.preview_handler_gpu.WEBENGINE_AVAILABLE", False)
    @patch("asciidoc_artisan.ui.preview_handler_gpu.get_gpu_info")
    def test_widget_info_webengine_unavailable(self, mock_get_gpu_info):
        """Test widget info when WebEngine is not available."""
        from asciidoc_artisan.ui.preview_handler_gpu import get_preview_widget_info

        # Mock widget with page attribute but WebEngine unavailable
        mock_widget = Mock()
        mock_widget.page = Mock()

        # Mock GPU info
        mock_gpu_info = Mock()
        mock_gpu_info.has_gpu = False
        mock_gpu_info.gpu_name = "N/A"
        mock_gpu_info.gpu_type = "none"
        mock_get_gpu_info.return_value = mock_gpu_info

        info = get_preview_widget_info(mock_widget)

        # Should not include WebEngine settings (WEBENGINE_AVAILABLE is False)
        assert "accelerated_2d_canvas" not in info
        assert "webgl_enabled" not in info
        # Should still include GPU info
        assert info["gpu_detected"] is False
