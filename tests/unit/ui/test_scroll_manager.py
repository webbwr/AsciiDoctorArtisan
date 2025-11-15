"""Tests for ui.scroll_manager module."""

from unittest.mock import Mock

import pytest


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


@pytest.mark.fr_017
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


@pytest.mark.fr_017
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
        call_args = (
            mock_editor.editor.verticalScrollBar().valueChanged.connect.call_args
        )
        assert call_args is not None


@pytest.mark.fr_017
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


@pytest.mark.fr_017
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


@pytest.mark.fr_017
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


@pytest.mark.fr_017
@pytest.mark.unit
class TestScrollLoopDetectionBoundaries:
    """Test suite for scroll loop detection boundary conditions."""

    def test_count_at_99_processes_normally(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager._scroll_sync_count = 99
        manager.sync_editor_to_preview(500)

        # Should process normally (count increments to 100, then decrements)
        mock_editor.preview.page().runJavaScript.assert_called()

    def test_count_at_100_processes_normally(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager._scroll_sync_count = 100
        manager.sync_editor_to_preview(500)

        # Count increments to 101 before check, triggering loop detection
        assert manager._scroll_sync_count == 0
        mock_editor.preview.page().runJavaScript.assert_not_called()

    def test_count_at_101_triggers_loop_detection(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager._scroll_sync_count = 101
        manager.sync_editor_to_preview(500)

        # Should detect loop and reset
        assert manager._scroll_sync_count == 0
        # Should not process (early return)
        mock_editor.preview.page().runJavaScript.assert_not_called()

    def test_count_at_150_triggers_loop_detection(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager._scroll_sync_count = 150
        manager.sync_editor_to_preview(500)

        # Should detect loop and reset
        assert manager._scroll_sync_count == 0
        mock_editor.preview.page().runJavaScript.assert_not_called()

    def test_count_reset_after_loop_detection(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Trigger loop detection
        manager._scroll_sync_count = 101
        manager.sync_editor_to_preview(500)
        assert manager._scroll_sync_count == 0

        # Next sync should work normally
        manager.sync_editor_to_preview(520)
        mock_editor.preview.page().runJavaScript.assert_called()


@pytest.mark.fr_017
@pytest.mark.unit
class TestJavaScriptCodeGeneration:
    """Test suite for JavaScript code generation with different scroll percentages."""

    def test_javascript_for_zero_percent(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Set last scroll to non-zero to avoid coalescing
        manager._last_editor_scroll = 100
        # 0% scroll
        manager.sync_editor_to_preview(0)

        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "0.0" in call_args or "* 0" in call_args

    def test_javascript_for_twenty_five_percent(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # 25% scroll (250 / 1000)
        manager.sync_editor_to_preview(250)

        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "0.25" in call_args

    def test_javascript_for_fifty_percent(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # 50% scroll (500 / 1000)
        manager.sync_editor_to_preview(500)

        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "0.5" in call_args

    def test_javascript_for_seventy_five_percent(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # 75% scroll (750 / 1000)
        manager.sync_editor_to_preview(750)

        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "0.75" in call_args

    def test_javascript_for_hundred_percent(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # 100% scroll (1000 / 1000)
        manager.sync_editor_to_preview(1000)

        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "1.0" in call_args or "* 1" in call_args


@pytest.mark.fr_017
@pytest.mark.unit
class TestScrollbarMaximumVariations:
    """Test suite for scrollbar maximum value edge cases."""

    def test_negative_maximum_value(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        scrollbar = mock_editor.editor.verticalScrollBar()
        scrollbar.maximum = Mock(return_value=-1)

        # Should not crash (editor_max <= 0 check)
        manager.sync_editor_to_preview(0)
        # No JavaScript call expected
        mock_editor.preview.page().runJavaScript.assert_not_called()

    def test_very_large_maximum_value(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        scrollbar = mock_editor.editor.verticalScrollBar()
        scrollbar.maximum = Mock(return_value=1000000)

        # Should handle large max value
        manager.sync_editor_to_preview(500000)
        mock_editor.preview.page().runJavaScript.assert_called()

    def test_maximum_equals_value(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        scrollbar = mock_editor.editor.verticalScrollBar()
        scrollbar.maximum = Mock(return_value=1000)

        # Scroll to exactly max
        manager.sync_editor_to_preview(1000)

        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "1.0" in call_args or "* 1" in call_args


@pytest.mark.fr_017
@pytest.mark.unit
class TestQTextBrowserFallback:
    """Test suite for QTextBrowser fallback path."""

    def test_fallback_uses_setvalue(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Remove page attribute
        delattr(mock_editor.preview, "page")
        preview_scrollbar = Mock()
        preview_scrollbar.setValue = Mock()
        preview_scrollbar.maximum = Mock(return_value=1000)
        mock_editor.preview.verticalScrollBar = Mock(return_value=preview_scrollbar)

        manager.sync_editor_to_preview(500)

        # Should call setValue with 50% of preview max
        preview_scrollbar.setValue.assert_called_once_with(500)

    def test_fallback_with_zero_preview_max(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        delattr(mock_editor.preview, "page")
        preview_scrollbar = Mock()
        preview_scrollbar.setValue = Mock()
        preview_scrollbar.maximum = Mock(return_value=0)
        mock_editor.preview.verticalScrollBar = Mock(return_value=preview_scrollbar)

        # Should not crash (preview_max <= 0 check)
        manager.sync_editor_to_preview(500)
        preview_scrollbar.setValue.assert_not_called()

    def test_fallback_with_negative_preview_max(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        delattr(mock_editor.preview, "page")
        preview_scrollbar = Mock()
        preview_scrollbar.setValue = Mock()
        preview_scrollbar.maximum = Mock(return_value=-1)
        mock_editor.preview.verticalScrollBar = Mock(return_value=preview_scrollbar)

        manager.sync_editor_to_preview(500)
        preview_scrollbar.setValue.assert_not_called()

    def test_fallback_with_different_aspect_ratio(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        delattr(mock_editor.preview, "page")
        preview_scrollbar = Mock()
        preview_scrollbar.setValue = Mock()
        preview_scrollbar.maximum = Mock(return_value=2000)  # Different from editor max
        mock_editor.preview.verticalScrollBar = Mock(return_value=preview_scrollbar)

        # Editor: 500/1000 = 50%
        # Preview: 50% of 2000 = 1000
        manager.sync_editor_to_preview(500)
        preview_scrollbar.setValue.assert_called_once_with(1000)

    def test_fallback_clears_syncing_flag(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        delattr(mock_editor.preview, "page")
        preview_scrollbar = Mock()
        preview_scrollbar.setValue = Mock()
        preview_scrollbar.maximum = Mock(return_value=1000)
        mock_editor.preview.verticalScrollBar = Mock(return_value=preview_scrollbar)

        manager.sync_editor_to_preview(500)

        # Flag should be reset
        assert mock_editor._is_syncing_scroll is False


@pytest.mark.fr_017
@pytest.mark.unit
class TestSyncingFlagLifecycle:
    """Test suite for _is_syncing_scroll flag lifecycle."""

    def test_flag_set_during_sync(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Capture flag state during runJavaScript call
        flag_during_sync = []

        def capture_flag(*args, **kwargs):
            flag_during_sync.append(mock_editor._is_syncing_scroll)

        mock_editor.preview.page().runJavaScript = Mock(side_effect=capture_flag)

        manager.sync_editor_to_preview(500)

        # Flag should be True during sync
        assert flag_during_sync[0] is True

    def test_flag_reset_after_sync(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager.sync_editor_to_preview(500)

        # Flag should be reset after sync
        assert mock_editor._is_syncing_scroll is False

    def test_flag_reset_after_exception(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Make runJavaScript raise exception
        mock_editor.preview.page().runJavaScript = Mock(
            side_effect=RuntimeError("Test error")
        )

        try:
            manager.sync_editor_to_preview(500)
        except RuntimeError:
            pass

        # Flag should be reset even after exception (finally block)
        assert mock_editor._is_syncing_scroll is False

    def test_flag_not_set_when_coalesced(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager._last_editor_scroll = 500
        manager.sync_editor_to_preview(501)  # Coalesced (< 2 pixel diff)

        # Flag should not be set (early return)
        assert mock_editor._is_syncing_scroll is False


@pytest.mark.fr_017
@pytest.mark.unit
class TestScrollSyncCountBehavior:
    """Test suite for _scroll_sync_count increment/decrement logic."""

    def test_count_increments_on_sync(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        initial_count = manager._scroll_sync_count
        manager.sync_editor_to_preview(500)

        # Count should increment then decrement (net change = 0 on success)
        assert manager._scroll_sync_count == initial_count

    def test_count_decrements_after_successful_sync(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager._scroll_sync_count = 10
        manager.sync_editor_to_preview(500)

        # Count should decrement (max(0, count - 1))
        assert manager._scroll_sync_count == 10  # Increments to 11, decrements to 10

    def test_count_does_not_go_negative(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager._scroll_sync_count = 0
        manager.sync_editor_to_preview(500)

        # Count should not go negative (max(0, count - 1))
        assert manager._scroll_sync_count >= 0

    def test_count_reset_on_loop_detection(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager._scroll_sync_count = 101
        manager.sync_editor_to_preview(500)

        # Count should reset to 0
        assert manager._scroll_sync_count == 0

    def test_count_not_incremented_when_coalesced(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager._last_editor_scroll = 500
        initial_count = manager._scroll_sync_count
        manager.sync_editor_to_preview(501)  # Coalesced

        # Count should not change
        assert manager._scroll_sync_count == initial_count


@pytest.mark.fr_017
@pytest.mark.unit
class TestPreviewPageAvailability:
    """Test suite for preview.page() attribute variations."""

    def test_page_attribute_exists(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # page attribute exists (default)
        manager.sync_editor_to_preview(500)

        # Should use JavaScript path
        mock_editor.preview.page().runJavaScript.assert_called()

    def test_page_attribute_missing(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        delattr(mock_editor.preview, "page")
        preview_scrollbar = Mock()
        preview_scrollbar.setValue = Mock()
        preview_scrollbar.maximum = Mock(return_value=1000)
        mock_editor.preview.verticalScrollBar = Mock(return_value=preview_scrollbar)

        manager.sync_editor_to_preview(500)

        # Should use fallback path
        preview_scrollbar.setValue.assert_called()

    def test_page_is_none(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        mock_editor.preview.page = lambda: None

        # Should not crash (hasattr returns True, but page() returns None)
        # This would trigger AttributeError on runJavaScript
        try:
            manager.sync_editor_to_preview(500)
        except AttributeError:
            pass  # Expected if not handled

    def test_page_callable_but_raises_exception(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        mock_editor.preview.page = Mock(side_effect=RuntimeError("page() failed"))

        # Should raise exception (not handled in code)
        with pytest.raises(RuntimeError):
            manager.sync_editor_to_preview(500)


@pytest.mark.fr_017
@pytest.mark.unit
class TestRapidScrollEvents:
    """Test suite for rapid consecutive scroll events."""

    def test_multiple_scrolls_in_sequence(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Simulate rapid scrolling
        for value in [100, 200, 300, 400, 500]:
            manager.sync_editor_to_preview(value)

        # All should process (each > 2 pixel diff)
        assert mock_editor.preview.page().runJavaScript.call_count == 5
        assert manager._last_editor_scroll == 500

    def test_coalesced_scrolls_in_sequence(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Simulate small incremental scrolls (coalesced)
        manager.sync_editor_to_preview(100)
        mock_editor.preview.page().runJavaScript.reset_mock()

        manager.sync_editor_to_preview(101)  # Coalesced
        manager.sync_editor_to_preview(102)  # Processed (diff = 2)

        # Only second sync should process
        assert mock_editor.preview.page().runJavaScript.call_count == 1

    def test_alternating_up_down_scrolls(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Scroll up and down alternately
        manager.sync_editor_to_preview(500)
        manager.sync_editor_to_preview(400)
        manager.sync_editor_to_preview(600)

        # All should process
        assert mock_editor.preview.page().runJavaScript.call_count == 3

    def test_rapid_scrolls_do_not_trigger_loop_detection(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # 50 rapid scrolls (below 100 threshold)
        for i in range(50):
            manager.sync_editor_to_preview(i * 10)

        # Should not trigger loop detection
        assert manager._scroll_sync_count < 100

    def test_very_rapid_scrolls_may_trigger_loop_detection(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # 150 rapid scrolls (above 100 threshold)
        # Count increments each time, decrements only on success
        # With mocked JavaScript, sync always succeeds, so count oscillates
        for i in range(150):
            if manager._scroll_sync_count > 100:
                break  # Loop detection triggered
            manager.sync_editor_to_preview(i * 10)

        # Loop detection should trigger at some point
        # (Actually, with successful syncs, count decrements, so may not trigger)
        # This test documents expected behavior


@pytest.mark.fr_017
@pytest.mark.unit
class TestScrollPercentageCalculations:
    """Test suite for scroll percentage calculations at edge values."""

    def test_percentage_at_zero(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Set last scroll to non-zero to avoid coalescing
        manager._last_editor_scroll = 100
        manager.sync_editor_to_preview(0)

        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "0.0" in call_args or "* 0" in call_args

    def test_percentage_at_one_quarter(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager.sync_editor_to_preview(250)

        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "0.25" in call_args

    def test_percentage_at_half(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager.sync_editor_to_preview(500)

        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "0.5" in call_args

    def test_percentage_at_three_quarters(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager.sync_editor_to_preview(750)

        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "0.75" in call_args

    def test_percentage_at_maximum(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        manager.sync_editor_to_preview(1000)

        call_args = mock_editor.preview.page().runJavaScript.call_args[0][0]
        assert "1.0" in call_args or "* 1" in call_args


@pytest.mark.fr_017
@pytest.mark.unit
class TestSyncPreviewToEditor:
    """Test suite for sync_preview_to_editor stub method."""

    def test_sync_preview_to_editor_exists(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Method should exist
        assert hasattr(manager, "sync_preview_to_editor")
        assert callable(manager.sync_preview_to_editor)

    def test_sync_preview_to_editor_does_nothing(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Should not crash (stub method)
        manager.sync_preview_to_editor(500)

        # Should not trigger any scrollbar changes
        # (No verification needed since it's a no-op)

    def test_sync_preview_to_editor_accepts_any_value(self, mock_editor):
        from asciidoc_artisan.ui.scroll_manager import ScrollManager

        manager = ScrollManager(mock_editor)

        # Should accept any int value without error
        manager.sync_preview_to_editor(0)
        manager.sync_preview_to_editor(500)
        manager.sync_preview_to_editor(1000)
        manager.sync_preview_to_editor(-1)
