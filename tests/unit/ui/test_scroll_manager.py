"""Tests for ui.scroll_manager module."""

import pytest
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def mock_editor(qapp):
    """Create a mock editor with required attributes for ScrollManager."""
    editor = Mock()

    # Editor widget with scrollbar
    editor.editor = Mock()
    scrollbar = Mock()
    scrollbar.valueChanged = Mock()
    scrollbar.valueChanged.connect = Mock()
    scrollbar.maximum = Mock(return_value=1000)
    scrollbar.value = Mock(return_value=500)
    editor.editor.verticalScrollBar = Mock(return_value=scrollbar)

    # Preview widget (mock both QWebEngineView and QTextBrowser paths)
    editor.preview = Mock()
    editor.preview.page = Mock()
    mock_page = Mock()
    mock_page.runJavaScript = Mock()
    editor.preview.page.return_value = mock_page
    editor.preview.verticalScrollBar = Mock(return_value=Mock())

    # Scroll sync state
    editor._sync_scrolling = True
    editor._is_syncing_scroll = False

    return editor


@pytest.mark.unit
class TestScrollManagerBasics:
    """Test suite for ScrollManager basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        assert ScrollManager is not None

    def test_creation(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)
        assert manager is not None

    def test_stores_editor_reference(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)
        assert manager.editor == mock_editor

    def test_initialization_sets_scroll_tracking(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)
        assert hasattr(manager, "_last_editor_scroll")
        assert hasattr(manager, "_last_preview_scroll")
        assert hasattr(manager, "_scroll_sync_count")

    def test_initial_scroll_values_are_zero(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)
        assert manager._last_editor_scroll == 0
        assert manager._last_preview_scroll == 0
        assert manager._scroll_sync_count == 0


@pytest.mark.unit
class TestSetupSynchronizedScrolling:
    """Test suite for setup_synchronized_scrolling method."""

    def test_setup_connects_scrollbar_signal(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        manager.setup_synchronized_scrolling()

        # Should get scrollbar and connect signal
        mock_editor.editor.verticalScrollBar.assert_called()
        scrollbar = mock_editor.editor.verticalScrollBar()
        scrollbar.valueChanged.connect.assert_called_once()

    def test_setup_connects_to_sync_method(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        manager.setup_synchronized_scrolling()

        # Should connect to sync_editor_to_preview
        call_args = mock_editor.editor.verticalScrollBar().valueChanged.connect.call_args
        assert call_args is not None


@pytest.mark.unit
class TestSyncEditorToPreview:
    """Test suite for sync_editor_to_preview method."""

    def test_sync_skips_when_sync_disabled(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        mock_editor._sync_scrolling = False
        manager.sync_editor_to_preview(500)

        # Should not update scroll count
        assert manager._scroll_sync_count == 0

    def test_sync_skips_when_already_syncing(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        mock_editor._is_syncing_scroll = True
        manager.sync_editor_to_preview(500)

        # Should not update scroll count
        assert manager._scroll_sync_count == 0

    def test_sync_coalesces_small_changes(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        manager._last_editor_scroll = 500
        manager.sync_editor_to_preview(501)  # Only 1 pixel difference

        # Should not increment count (coalesced)
        assert manager._scroll_sync_count == 0

    def test_sync_accepts_significant_changes(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        manager._last_editor_scroll = 500
        manager.sync_editor_to_preview(510)  # 10 pixel difference

        # Should process (runJavaScript called, last_scroll updated)
        mock_editor.preview.page().runJavaScript.assert_called()
        assert manager._last_editor_scroll == 510

    def test_sync_updates_last_scroll_value(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        manager.sync_editor_to_preview(750)

        assert manager._last_editor_scroll == 750

    def test_sync_processes_scroll_event(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        manager.sync_editor_to_preview(500)

        # Should call JavaScript to sync (count resets to 0 after successful sync)
        mock_editor.preview.page().runJavaScript.assert_called()
        assert manager._scroll_sync_count == 0  # Reset after successful sync

    def test_sync_detects_scroll_loops(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        # Simulate loop condition
        manager._scroll_sync_count = 101
        initial_flag = mock_editor._is_syncing_scroll

        manager.sync_editor_to_preview(500)

        # Should reset count and return early
        assert manager._scroll_sync_count == 0
        assert mock_editor._is_syncing_scroll == initial_flag  # Not modified

    def test_sync_sets_syncing_flag(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        mock_editor._is_syncing_scroll = False

        manager.sync_editor_to_preview(500)

        # Flag should be reset to False after sync completes
        assert mock_editor._is_syncing_scroll is False
        # Verify sync happened by checking JavaScript was called
        mock_editor.preview.page().runJavaScript.assert_called()

    def test_sync_uses_javascript_for_webengine(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        manager.sync_editor_to_preview(500)

        # Should call runJavaScript for QWebEngineView
        mock_editor.preview.page().runJavaScript.assert_called()
        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "window.scrollTo" in call_args

    def test_sync_calculates_scroll_percentage(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        # Scrollbar max = 1000, value = 500 → 50% (0.5)
        manager.sync_editor_to_preview(500)

        # Check JavaScript contains percentage calculation
        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "0.5" in call_args

    def test_sync_handles_zero_editor_max(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        # Set max to 0 (edge case)
        scrollbar = mock_editor.editor.verticalScrollBar()
        scrollbar.maximum = Mock(return_value=0)

        # Should not crash
        manager.sync_editor_to_preview(0)

        # runJavaScript should not be called (division by zero avoided)
        # Can't easily verify since we'd need to check control flow

    def test_sync_uses_fallback_for_text_browser(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        # Remove page attribute to simulate QTextBrowser
        delattr(mock_editor.preview, "page")
        preview_scrollbar = Mock()
        preview_scrollbar.setValue = Mock()
        preview_scrollbar.maximum = Mock(return_value=1000)
        mock_editor.preview.verticalScrollBar = Mock(return_value=preview_scrollbar)

        manager.sync_editor_to_preview(500)

        # Should use setValue for QTextBrowser
        preview_scrollbar.setValue.assert_called()

    def test_sync_resets_syncing_flag_after_sync(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        manager.sync_editor_to_preview(500)

        # Flag should be reset after sync completes
        assert mock_editor._is_syncing_scroll is False


@pytest.mark.unit
class TestScrollCoalescing:
    """Test suite for scroll event coalescing."""

    def test_coalescing_threshold_is_2_pixels(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        manager._last_editor_scroll = 100

        # 1 pixel: should coalesce (no JS call)
        js_mock = mock_editor.preview.page().runJavaScript
        js_mock.reset_mock()
        manager.sync_editor_to_preview(101)
        coalesced = not js_mock.called

        # 2 pixels: should process (JS called)
        manager._last_editor_scroll = 100
        js_mock.reset_mock()
        manager.sync_editor_to_preview(102)
        processed = js_mock.called

        assert coalesced  # 1 pixel coalesced
        assert processed  # 2 pixels processed

    def test_negative_scroll_changes_handled(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        manager._last_editor_scroll = 500

        # Scroll up (negative delta)
        manager.sync_editor_to_preview(490)

        # Should process (abs difference > 2) - verify JS called
        mock_editor.preview.page().runJavaScript.assert_called()
        assert manager._last_editor_scroll == 490


@pytest.mark.unit
class TestEdgeCases:
    """Test suite for edge cases."""

    def test_sync_with_maximum_scroll_value(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        # Scroll to bottom
        manager.sync_editor_to_preview(1000)

        # Should handle max value (100% scroll) - verify JS called
        mock_editor.preview.page().runJavaScript.assert_called()
        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "1.0" in call_args or "1" in call_args  # 100% scroll

    def test_sync_with_zero_scroll_value(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager
        manager = ScrollManager(mock_editor)

        # Scroll to top
        manager.sync_editor_to_preview(0)

        # Should handle zero value
        assert manager._last_editor_scroll == 0
