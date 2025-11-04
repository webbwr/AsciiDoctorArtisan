"""Tests for ui.preview_handler module."""

import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser


@pytest.fixture
def mock_editor(qapp):
    """Create mock editor widget with scrollbar."""
    editor = QPlainTextEdit()
    # Mock scrollbar
    scrollbar = Mock()
    scrollbar.maximum = Mock(return_value=1000)
    scrollbar.value = Mock(return_value=500)
    scrollbar.setValue = Mock()
    editor.verticalScrollBar = Mock(return_value=scrollbar)
    return editor


@pytest.fixture
def mock_preview(qapp):
    """Create mock preview widget with scrollbar."""
    preview = QTextBrowser()
    # Mock scrollbar
    scrollbar = Mock()
    scrollbar.maximum = Mock(return_value=1000)
    scrollbar.value = Mock(return_value=500)
    scrollbar.setValue = Mock()
    preview.verticalScrollBar = Mock(return_value=scrollbar)
    return preview


@pytest.fixture
def mock_parent_window():
    """Create mock parent window."""
    # PreviewHandlerBase inherits from QObject which requires None or QObject parent
    return None


@pytest.mark.unit
class TestPreviewHandlerBasics:
    """Test suite for PreviewHandler basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        assert PreviewHandler is not None

    def test_creation(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        assert handler is not None

    def test_is_qobject(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        from PySide6.QtCore import QObject
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        assert isinstance(handler, QObject)

    def test_stores_references(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        assert handler.editor == mock_editor
        assert handler.preview == mock_preview

    def test_inherits_from_base(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        from asciidoc_artisan.ui.preview_handler_base import PreviewHandlerBase
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        assert isinstance(handler, PreviewHandlerBase)


@pytest.mark.unit
class TestHandlePreviewComplete:
    """Test suite for handle_preview_complete method."""

    def test_updates_preview_with_html(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        html = "<h1>Test Document</h1>"

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(html)
            # Should call setHtml with styled HTML
            mock_set_html.assert_called_once()
            call_args = mock_set_html.call_args[0][0]
            assert "<h1>Test Document</h1>" in call_args

    def test_wraps_html_with_css(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        html = "<h1>Test</h1>"

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(html)
            # Should wrap with CSS
            styled_html = mock_set_html.call_args[0][0]
            assert "body {" in styled_html or "<style>" in styled_html

    def test_emits_preview_updated_signal(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        html = "<h1>Test</h1>"

        with patch.object(handler, "preview_updated") as mock_signal:
            with patch.object(mock_preview, 'setHtml'):
                handler.handle_preview_complete(html)
                # Signal should emit original HTML (not styled)
                mock_signal.emit.assert_called_once_with(html)

    def test_updates_adaptive_debouncer_with_render_time(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        # Mock adaptive debouncer
        handler._adaptive_debouncer = Mock()
        handler._adaptive_debouncer.on_render_complete = Mock()
        handler._last_render_start = 1000.0

        html = "<h1>Test</h1>"

        with patch('time.time', return_value=1000.5):
            with patch.object(mock_preview, 'setHtml'):
                handler.handle_preview_complete(html)
                # Should update debouncer with 0.5s render time
                handler._adaptive_debouncer.on_render_complete.assert_called_once()
                call_args = handler._adaptive_debouncer.on_render_complete.call_args[0][0]
                assert call_args == 0.5


@pytest.mark.unit
class TestScrollSynchronization:
    """Test suite for scroll synchronization methods."""

    def test_sync_editor_to_preview_uses_scrollbar(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        handler.sync_editor_to_preview(500)

        # Should call setValue on preview scrollbar
        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.setValue.assert_called_once()
        # 500/1000 = 0.5 → preview_value = 1000 * 0.5 = 500
        preview_scrollbar.setValue.assert_called_with(500)

    def test_sync_skips_when_disabled(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = False

        handler.sync_editor_to_preview(500)

        # Should not call setValue
        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.setValue.assert_not_called()

    def test_sync_skips_when_already_syncing(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True
        handler.is_syncing_scroll = True

        handler.sync_editor_to_preview(500)

        # Should not call setValue when already syncing
        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.setValue.assert_not_called()

    def test_sync_handles_zero_editor_max(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Set editor max to 0
        editor_scrollbar = mock_editor.verticalScrollBar()
        editor_scrollbar.maximum = Mock(return_value=0)

        handler.sync_editor_to_preview(0)

        # Should not crash, should not call setValue
        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.setValue.assert_not_called()

    def test_sync_sets_and_clears_syncing_flag(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True
        handler.is_syncing_scroll = False

        handler.sync_editor_to_preview(500)

        # Flag should be cleared after sync (finally block)
        assert handler.is_syncing_scroll is False

    def test_sync_preview_to_editor_uses_scrollbar(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        handler.sync_preview_to_editor(500)

        # Should call setValue on editor scrollbar
        editor_scrollbar = mock_editor.verticalScrollBar()
        editor_scrollbar.setValue.assert_called_once()
        # 500/1000 = 0.5 → editor_value = 1000 * 0.5 = 500
        editor_scrollbar.setValue.assert_called_with(500)

    def test_sync_preview_to_editor_skips_when_disabled(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = False

        handler.sync_preview_to_editor(500)

        # Should not call setValue
        editor_scrollbar = mock_editor.verticalScrollBar()
        editor_scrollbar.setValue.assert_not_called()

    def test_sync_preview_to_editor_skips_when_already_syncing(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True
        handler.is_syncing_scroll = True

        handler.sync_preview_to_editor(500)

        # Should not call setValue when already syncing
        editor_scrollbar = mock_editor.verticalScrollBar()
        editor_scrollbar.setValue.assert_not_called()

    def test_sync_preview_to_editor_handles_zero_preview_max(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Set preview max to 0
        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.maximum = Mock(return_value=0)

        handler.sync_preview_to_editor(0)

        # Should not crash, should not call setValue
        editor_scrollbar = mock_editor.verticalScrollBar()
        editor_scrollbar.setValue.assert_not_called()


@pytest.mark.unit
class TestScrollPercentageCalculation:
    """Test suite for scroll percentage calculations."""

    def test_calculates_correct_percentage(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Editor: 250/1000 = 25%
        handler.sync_editor_to_preview(250)

        # Preview should scroll to 25% → 1000 * 0.25 = 250
        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.setValue.assert_called_with(250)

    def test_handles_different_scrollbar_ranges(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Editor: max=1000, Preview: max=500
        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.maximum = Mock(return_value=500)

        # Editor at 50% (500/1000)
        handler.sync_editor_to_preview(500)

        # Preview should scroll to 50% → 500 * 0.5 = 250
        preview_scrollbar.setValue.assert_called_with(250)

    def test_handles_maximum_scroll_position(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Scroll to bottom (100%)
        handler.sync_editor_to_preview(1000)

        # Preview should scroll to 100% → 1000
        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.setValue.assert_called_with(1000)


@pytest.mark.unit
class TestClearPreview:
    """Test suite for clear_preview method."""

    def test_clear_preview_sets_empty_html(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.clear_preview()
            # Should set HTML with "Preview cleared" message
            mock_set_html.assert_called_once()
            call_args = mock_set_html.call_args[0][0]
            assert "Preview cleared" in call_args

    def test_clear_preview_does_not_crash(self, mock_editor, mock_preview, mock_parent_window):
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        # Should not raise exception
        handler.clear_preview()
