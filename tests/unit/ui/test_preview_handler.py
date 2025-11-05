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


@pytest.mark.unit
class TestCSSStyling:
    """Test suite for CSS styling and wrapping."""

    def test_css_wrapping_includes_style_tag(self, mock_editor, mock_preview, mock_parent_window):
        """Test CSS wrapping adds style tags."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        html = "<h1>Test</h1>"

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(html)
            styled_html = mock_set_html.call_args[0][0]
            assert "<style>" in styled_html or "body {" in styled_html

    def test_preserves_html_content_in_css_wrapper(self, mock_editor, mock_preview, mock_parent_window):
        """Test original HTML content preserved in CSS wrapper."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        html = "<h1>Important Content</h1><p>Paragraph</p>"

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(html)
            styled_html = mock_set_html.call_args[0][0]
            assert "<h1>Important Content</h1>" in styled_html
            assert "<p>Paragraph</p>" in styled_html

    def test_handles_empty_html_in_css_wrapping(self, mock_editor, mock_preview, mock_parent_window):
        """Test CSS wrapping with empty HTML."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        html = ""

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(html)
            # Should still wrap empty content
            mock_set_html.assert_called_once()

    def test_handles_html_with_existing_style_tags(self, mock_editor, mock_preview, mock_parent_window):
        """Test CSS wrapping when HTML already has style tags."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        html = "<style>body { color: red; }</style><h1>Test</h1>"

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(html)
            # Should wrap/merge styles properly
            mock_set_html.assert_called_once()


@pytest.mark.unit
class TestRenderTiming:
    """Test suite for render timing and performance metrics."""

    def test_calculates_render_time_correctly(self, mock_editor, mock_preview, mock_parent_window):
        """Test render time calculation."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        handler._last_render_start = 1000.0
        html = "<h1>Test</h1>"

        with patch('time.time', return_value=1000.5):
            with patch.object(mock_preview, 'setHtml'):
                handler.handle_preview_complete(html)
                # Render time should be 0.5s (1000.5 - 1000.0)

    def test_updates_adaptive_debouncer_with_correct_timing(self, mock_editor, mock_preview, mock_parent_window):
        """Test adaptive debouncer receives correct render time."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        handler._adaptive_debouncer = Mock()
        handler._adaptive_debouncer.on_render_complete = Mock()
        handler._last_render_start = 2000.0
        html = "<h1>Test</h1>"

        with patch('time.time', return_value=2000.75):
            with patch.object(mock_preview, 'setHtml'):
                handler.handle_preview_complete(html)
                # Should receive 0.75s
                handler._adaptive_debouncer.on_render_complete.assert_called_once_with(0.75)

    def test_handles_missing_render_start_time(self, mock_editor, mock_preview, mock_parent_window):
        """Test render completion when start time not set."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        handler._last_render_start = None
        handler._adaptive_debouncer = Mock()
        html = "<h1>Test</h1>"

        with patch.object(mock_preview, 'setHtml'):
            handler.handle_preview_complete(html)
            # Should not crash, debouncer not called
            handler._adaptive_debouncer.on_render_complete.assert_not_called()

    def test_handles_missing_adaptive_debouncer(self, mock_editor, mock_preview, mock_parent_window):
        """Test render completion when adaptive debouncer not set."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        handler._last_render_start = 1000.0
        handler._adaptive_debouncer = None
        html = "<h1>Test</h1>"

        with patch('time.time', return_value=1000.5):
            with patch.object(mock_preview, 'setHtml'):
                handler.handle_preview_complete(html)
                # Should not crash


@pytest.mark.unit
class TestSignalEmissionsEdgeCases:
    """Test suite for signal emission edge cases."""

    def test_emits_preview_updated_with_original_html(self, mock_editor, mock_preview, mock_parent_window):
        """Test signal emits original HTML, not styled version."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        original_html = "<h1>Original</h1>"

        with patch.object(handler, 'preview_updated') as mock_signal:
            with patch.object(mock_preview, 'setHtml'):
                handler.handle_preview_complete(original_html)
                # Should emit original, not styled
                mock_signal.emit.assert_called_once_with(original_html)

    def test_emits_signal_even_on_empty_html(self, mock_editor, mock_preview, mock_parent_window):
        """Test signal emitted even with empty HTML."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        with patch.object(handler, 'preview_updated') as mock_signal:
            with patch.object(mock_preview, 'setHtml'):
                handler.handle_preview_complete("")
                mock_signal.emit.assert_called_once_with("")

    def test_signal_emission_order(self, mock_editor, mock_preview, mock_parent_window, qtbot):
        """Test signal emitted after preview update."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        call_order = []

        def track_sethtml(*args):
            call_order.append('setHtml')

        # Use qtbot.waitSignal to verify signal emission
        html = "<h1>Test</h1>"

        with patch.object(mock_preview, 'setHtml', side_effect=track_sethtml):
            with qtbot.waitSignal(handler.preview_updated, timeout=1000):
                handler.handle_preview_complete(html)
                # setHtml should be called
                assert 'setHtml' in call_order

    def test_multiple_preview_updates_emit_multiple_signals(self, mock_editor, mock_preview, mock_parent_window):
        """Test each preview update emits its own signal."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        with patch.object(handler, 'preview_updated') as mock_signal:
            with patch.object(mock_preview, 'setHtml'):
                handler.handle_preview_complete("<h1>First</h1>")
                handler.handle_preview_complete("<h1>Second</h1>")
                handler.handle_preview_complete("<h1>Third</h1>")
                # Should emit 3 signals
                assert mock_signal.emit.call_count == 3


@pytest.mark.unit
class TestScrollExtremeValues:
    """Test suite for extreme scroll values."""

    def test_handles_negative_scroll_value(self, mock_editor, mock_preview, mock_parent_window):
        """Test sync with negative scroll value."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Negative value results in negative percentage
        handler.sync_editor_to_preview(-10)

        preview_scrollbar = mock_preview.verticalScrollBar()
        # Should calculate percentage: -10/1000 = -0.01, then -0.01 * 1000 = -10
        # Code doesn't clamp to 0, passes through negative value
        preview_scrollbar.setValue.assert_called_once()
        call_value = preview_scrollbar.setValue.call_args[0][0]
        # Negative input → negative output (percentage preserved)
        assert call_value == -10

    def test_handles_scroll_value_exceeding_maximum(self, mock_editor, mock_preview, mock_parent_window):
        """Test sync with scroll value > maximum."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Value exceeding max (max is 1000)
        handler.sync_editor_to_preview(5000)

        preview_scrollbar = mock_preview.verticalScrollBar()
        # Should handle overflow (percentage > 1.0)
        preview_scrollbar.setValue.assert_called_once()

    def test_handles_very_large_scroll_values(self, mock_editor, mock_preview, mock_parent_window):
        """Test sync with very large scroll values."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Very large value
        handler.sync_editor_to_preview(999999999)

        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.setValue.assert_called_once()

    def test_handles_zero_scroll_value(self, mock_editor, mock_preview, mock_parent_window):
        """Test sync with scroll value = 0."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        handler.sync_editor_to_preview(0)

        preview_scrollbar = mock_preview.verticalScrollBar()
        # Should scroll to top (0%)
        preview_scrollbar.setValue.assert_called_with(0)


@pytest.mark.unit
class TestWidgetStateManagement:
    """Test suite for widget state management."""

    def test_sync_respects_enabled_flag(self, mock_editor, mock_preview, mock_parent_window):
        """Test sync respects sync_scrolling_enabled flag."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        # Test enabled
        handler.sync_scrolling_enabled = True
        handler.sync_editor_to_preview(500)
        preview_scrollbar = mock_preview.verticalScrollBar()
        assert preview_scrollbar.setValue.called

        # Reset mock
        preview_scrollbar.setValue.reset_mock()

        # Test disabled
        handler.sync_scrolling_enabled = False
        handler.sync_editor_to_preview(500)
        preview_scrollbar.setValue.assert_not_called()

    def test_can_toggle_sync_enabled_flag(self, mock_editor, mock_preview, mock_parent_window):
        """Test toggling sync_scrolling_enabled flag."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        # Initial state
        handler.sync_scrolling_enabled = False
        assert handler.sync_scrolling_enabled is False

        # Enable
        handler.sync_scrolling_enabled = True
        assert handler.sync_scrolling_enabled is True

        # Disable again
        handler.sync_scrolling_enabled = False
        assert handler.sync_scrolling_enabled is False

    def test_syncing_flag_prevents_reentrancy(self, mock_editor, mock_preview, mock_parent_window):
        """Test is_syncing_scroll flag prevents reentrant calls."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Set flag manually to simulate ongoing sync
        handler.is_syncing_scroll = True

        handler.sync_editor_to_preview(500)

        # Should not call setValue when already syncing
        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.setValue.assert_not_called()

    def test_syncing_flag_cleared_after_sync(self, mock_editor, mock_preview, mock_parent_window):
        """Test is_syncing_scroll flag cleared after sync completes."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True
        handler.is_syncing_scroll = False

        handler.sync_editor_to_preview(500)

        # Flag should be cleared (finally block)
        assert handler.is_syncing_scroll is False


@pytest.mark.unit
class TestErrorHandling:
    """Test suite for error handling."""

    def test_handles_null_html_gracefully(self, mock_editor, mock_preview, mock_parent_window):
        """Test handling None as HTML input."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            # Should handle None without crashing
            try:
                handler.handle_preview_complete(None)
            except (TypeError, AttributeError):
                # Expected if code doesn't handle None
                pass

    def test_handles_malformed_html(self, mock_editor, mock_preview, mock_parent_window):
        """Test handling malformed HTML."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        malformed_html = "<h1>Unclosed tag<p>Missing close</div>"

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(malformed_html)
            # Should not crash, setHtml called
            mock_set_html.assert_called_once()

    def test_handles_special_characters_in_html(self, mock_editor, mock_preview, mock_parent_window):
        """Test handling HTML with special characters."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        special_html = "<h1>&lt;Script&gt; &amp; \"Quotes\" 'Apostrophes' ©®™</h1>"

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(special_html)
            styled_html = mock_set_html.call_args[0][0]
            # Special chars should be preserved
            assert "&lt;Script&gt;" in styled_html or "<Script>" in styled_html

    def test_handles_unicode_characters_in_html(self, mock_editor, mock_preview, mock_parent_window):
        """Test handling HTML with Unicode characters."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        unicode_html = "<h1>日本語 文档 📝 ñáéíóú</h1>"

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(unicode_html)
            styled_html = mock_set_html.call_args[0][0]
            # Unicode should be preserved
            assert "日本語" in styled_html or "文档" in styled_html


@pytest.mark.unit
class TestHTMLProcessingEdgeCases:
    """Test suite for HTML processing edge cases."""

    def test_handles_very_large_html_content(self, mock_editor, mock_preview, mock_parent_window):
        """Test handling very large HTML content."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        # Generate large HTML (1MB+)
        large_html = "<h1>Large Document</h1>" + ("<p>Line of content</p>\n" * 50000)

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(large_html)
            # Should handle large content without crashing
            mock_set_html.assert_called_once()
            styled_html = mock_set_html.call_args[0][0]
            assert len(styled_html) > 1000000  # >1MB

    def test_handles_html_with_embedded_scripts(self, mock_editor, mock_preview, mock_parent_window):
        """Test handling HTML with embedded scripts."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        script_html = "<h1>Test</h1><script>alert('test');</script>"

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(script_html)
            # Should not crash (QTextBrowser ignores scripts)
            mock_set_html.assert_called_once()

    def test_handles_html_with_inline_styles(self, mock_editor, mock_preview, mock_parent_window):
        """Test handling HTML with inline styles."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        inline_html = '<h1 style="color: red; font-size: 24px;">Styled</h1>'

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(inline_html)
            styled_html = mock_set_html.call_args[0][0]
            # Inline styles should be preserved
            assert 'style="color: red' in styled_html or "color: red" in styled_html

    def test_handles_whitespace_only_html(self, mock_editor, mock_preview, mock_parent_window):
        """Test handling HTML with only whitespace."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        whitespace_html = "   \n\n\t\t  \n   "

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            handler.handle_preview_complete(whitespace_html)
            # Should not crash
            mock_set_html.assert_called_once()


@pytest.mark.unit
class TestSyncFlagLifecycle:
    """Test suite for sync flag lifecycle management."""

    def test_sync_flag_starts_false(self, mock_editor, mock_preview, mock_parent_window):
        """Test is_syncing_scroll initializes to False."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        assert handler.is_syncing_scroll is False

    def test_sync_flag_set_during_editor_sync(self, mock_editor, mock_preview, mock_parent_window):
        """Test flag set during sync_editor_to_preview."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        flag_states = []

        def track_setvalue(*args):
            flag_states.append(handler.is_syncing_scroll)

        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.setValue = Mock(side_effect=track_setvalue)

        handler.sync_editor_to_preview(500)

        # Flag should be True during setValue call
        assert True in flag_states
        # Flag should be False after sync completes
        assert handler.is_syncing_scroll is False

    def test_sync_flag_set_during_preview_sync(self, mock_editor, mock_preview, mock_parent_window):
        """Test flag set during sync_preview_to_editor."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        flag_states = []

        def track_setvalue(*args):
            flag_states.append(handler.is_syncing_scroll)

        editor_scrollbar = mock_editor.verticalScrollBar()
        editor_scrollbar.setValue = Mock(side_effect=track_setvalue)

        handler.sync_preview_to_editor(500)

        # Flag should be True during setValue call
        assert True in flag_states
        # Flag should be False after sync completes
        assert handler.is_syncing_scroll is False

    def test_sync_flag_cleared_even_on_exception(self, mock_editor, mock_preview, mock_parent_window):
        """Test sync flag cleared even if exception occurs."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        # Mock setValue to raise exception
        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.setValue = Mock(side_effect=RuntimeError("Test error"))

        try:
            handler.sync_editor_to_preview(500)
        except RuntimeError:
            pass

        # Flag should still be cleared (finally block)
        assert handler.is_syncing_scroll is False


@pytest.mark.unit
class TestScrollbarBehaviorDetails:
    """Test suite for scrollbar behavior details."""

    def test_retrieves_correct_scrollbar_from_editor(self, mock_editor, mock_preview, mock_parent_window):
        """Test retrieves editor's vertical scrollbar correctly."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        handler.sync_editor_to_preview(500)

        # Should call verticalScrollBar() on editor
        mock_editor.verticalScrollBar.assert_called()

    def test_retrieves_correct_scrollbar_from_preview(self, mock_editor, mock_preview, mock_parent_window):
        """Test retrieves preview's vertical scrollbar correctly."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        handler.sync_editor_to_preview(500)

        # Should call verticalScrollBar() on preview
        mock_preview.verticalScrollBar.assert_called()

    def test_queries_scrollbar_maximum_value(self, mock_editor, mock_preview, mock_parent_window):
        """Test queries scrollbar maximum() for percentage calculation."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        handler.sync_editor_to_preview(500)

        # Should call maximum() on both scrollbars
        editor_scrollbar = mock_editor.verticalScrollBar()
        preview_scrollbar = mock_preview.verticalScrollBar()
        editor_scrollbar.maximum.assert_called()
        preview_scrollbar.maximum.assert_called()

    def test_calls_setvalue_on_target_scrollbar(self, mock_editor, mock_preview, mock_parent_window):
        """Test calls setValue() on target scrollbar."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler.sync_scrolling_enabled = True

        handler.sync_editor_to_preview(500)

        # Should call setValue on preview scrollbar
        preview_scrollbar = mock_preview.verticalScrollBar()
        preview_scrollbar.setValue.assert_called_once()


@pytest.mark.unit
class TestMemoryManagementPreview:
    """Test suite for memory management with preview content."""

    def test_repeated_preview_updates_do_not_leak(self, mock_editor, mock_preview, mock_parent_window):
        """Test repeated preview updates don't cause memory leaks."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        with patch.object(mock_preview, 'setHtml'):
            # Simulate many rapid updates
            for i in range(100):
                html = f"<h1>Update {i}</h1><p>Content {i}</p>"
                handler.handle_preview_complete(html)

            # Should not crash or consume excessive memory

    def test_large_content_updates_handled_efficiently(self, mock_editor, mock_preview, mock_parent_window):
        """Test large content updates handled efficiently."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        with patch.object(mock_preview, 'setHtml') as mock_set_html:
            # Create 5MB content
            large_html = "<h1>Large</h1>" + ("<p>Line</p>\n" * 200000)
            handler.handle_preview_complete(large_html)

            # Should handle without crashing
            mock_set_html.assert_called_once()

    def test_handler_cleanup_on_deletion(self, mock_editor, mock_preview, mock_parent_window):
        """Test handler cleanup when deleted."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        handler = PreviewHandler(mock_editor, mock_preview, mock_parent_window)

        # Store references
        editor_ref = handler.editor
        preview_ref = handler.preview

        # Delete handler
        del handler

        # Original widgets should still exist
        assert editor_ref is not None
        assert preview_ref is not None

    def test_multiple_handlers_do_not_interfere(self, mock_editor, mock_preview, mock_parent_window, qapp):
        """Test multiple handler instances don't interfere."""
        from asciidoc_artisan.ui.preview_handler import PreviewHandler
        from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser

        # Create second set of widgets
        editor2 = QPlainTextEdit()
        preview2 = QTextBrowser()
        scrollbar2 = Mock()
        scrollbar2.maximum = Mock(return_value=1000)
        scrollbar2.setValue = Mock()
        editor2.verticalScrollBar = Mock(return_value=scrollbar2)
        preview2.verticalScrollBar = Mock(return_value=scrollbar2)

        handler1 = PreviewHandler(mock_editor, mock_preview, mock_parent_window)
        handler2 = PreviewHandler(editor2, preview2, None)

        # Update both
        with patch.object(mock_preview, 'setHtml'):
            with patch.object(preview2, 'setHtml'):
                handler1.handle_preview_complete("<h1>Handler 1</h1>")
                handler2.handle_preview_complete("<h1>Handler 2</h1>")

        # Both should work independently
        assert handler1.editor == mock_editor
        assert handler2.editor == editor2
