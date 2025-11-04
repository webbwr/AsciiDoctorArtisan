"""Tests for ui.preview_handler_gpu module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser
from PySide6.QtCore import QUrl


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

    def test_creation_requires_webengine_view(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        # Should create successfully with proper preview widget
        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        assert handler is not None

    def test_creation_rejects_non_webengine_widget(self, mock_editor, mock_parent_window):
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

    def test_updates_preview_with_html(self, mock_editor, mock_preview, mock_parent_window):
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

    def test_emits_preview_updated_signal(self, mock_editor, mock_preview, mock_parent_window):
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

    def test_sync_editor_to_preview_uses_javascript(self, mock_editor, mock_preview, mock_parent_window):
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

    def test_sync_skips_when_disabled(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import WebEngineHandler

        handler = WebEngineHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = False

        handler.sync_editor_to_preview(500)

        # Should not call JavaScript
        mock_preview.page().runJavaScript.assert_not_called()

    def test_sync_skips_when_already_syncing(self, mock_editor, mock_preview, mock_parent_window):
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

    def test_sync_preview_to_editor_not_implemented(self, mock_editor, mock_preview, mock_parent_window):
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
    def test_returns_webengine_when_gpu_available(self, mock_webengine_cls, mock_get_gpu_info):
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
    def test_enables_gpu_acceleration(self, mock_settings_cls, mock_webengine_cls, mock_get_gpu_info):
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
    def test_returns_webengine_handler_for_webengine_view(self, mock_hasattr, mock_editor, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler_gpu import create_preview_handler, WebEngineHandler

        # Mock preview with 'page' attribute (QWebEngineView)
        mock_preview = Mock()
        mock_preview.page = Mock()
        mock_hasattr.return_value = True

        with patch("asciidoc_artisan.ui.preview_handler_gpu.QWebEngineView", Mock()):
            handler = create_preview_handler(mock_editor, mock_preview, mock_parent_window)

            # Should return WebEngineHandler
            assert isinstance(handler, WebEngineHandler)

    def test_returns_text_browser_handler_for_text_browser(self, mock_editor, mock_parent_window):
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
