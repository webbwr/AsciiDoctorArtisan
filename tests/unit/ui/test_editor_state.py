"""Tests for ui.editor_state module."""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit, QPushButton, QSplitter, QStatusBar


@pytest.fixture
def mock_main_window(qapp):
    """Create a mock main window with required attributes for EditorState."""
    window = Mock()

    # Editor
    window.editor = QPlainTextEdit()
    font = QFont("Monospace", 12)
    window.editor.setFont(font)

    # Preview (mock with zoomFactor support)
    window.preview = Mock()
    window.preview.zoomFactor = Mock(return_value=1.0)
    window.preview.setZoomFactor = Mock()

    # Splitter (needs widgets added to work properly)
    window.splitter = QSplitter(Qt.Orientation.Horizontal)
    # Add editor and preview to splitter
    window.splitter.addWidget(window.editor)
    preview_widget = QPlainTextEdit()  # Dummy preview widget
    window.splitter.addWidget(preview_widget)
    window.splitter.setSizes([400, 600])

    # Status bar (use real widget but mock showMessage for testing)
    window.status_bar = QStatusBar()
    window.status_bar.showMessage = Mock()

    # Maximize buttons
    window.editor_max_btn = QPushButton()
    window.preview_max_btn = QPushButton()

    # Theme manager
    window.theme_manager = Mock()
    window.theme_manager.apply_theme = Mock()

    # Settings
    window._settings = Mock()
    window._settings.dark_mode = False
    window._settings.sync_scroll = True

    # Action manager
    window.action_manager = Mock()
    window.action_manager.dark_mode_act = Mock()
    window.action_manager.dark_mode_act.blockSignals = Mock()
    window.action_manager.dark_mode_act.setChecked = Mock()
    window.action_manager.sync_scrolling_act = Mock()
    window.action_manager.sync_scrolling_act.setChecked = Mock()

    return window


@pytest.mark.unit
class TestEditorStateBasics:
    """Test suite for EditorState basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.editor_state import EditorState

        assert EditorState is not None

    def test_creation(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        assert state is not None

    def test_stores_window_reference(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        assert state.window == mock_main_window

    def test_stores_editor_reference(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        assert state.editor == mock_main_window.editor

    def test_initialization_sets_default_pane_state(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        assert state.maximized_pane is None
        assert state.saved_splitter_sizes is None

    def test_initialization_sets_sync_scrolling(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        assert state.sync_scrolling is True


@pytest.mark.unit
class TestZoomFunctionality:
    """Test suite for zoom functionality."""

    def test_zoom_increases_font_size(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        initial_size = state.editor.font().pointSize()
        state.zoom(2)

        assert state.editor.font().pointSize() == initial_size + 2

    def test_zoom_decreases_font_size(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        initial_size = state.editor.font().pointSize()
        state.zoom(-2)

        assert state.editor.font().pointSize() == initial_size - 2

    def test_zoom_respects_minimum_font_size(self, mock_main_window):
        from asciidoc_artisan.core import MIN_FONT_SIZE
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        # Try to zoom way out
        state.zoom(-100)

        # Should not go below minimum
        assert state.editor.font().pointSize() >= MIN_FONT_SIZE

    def test_zoom_updates_preview_zoom_factor(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        state.zoom(1)

        # Should call setZoomFactor
        state.preview.setZoomFactor.assert_called()

    def test_zoom_handles_preview_without_zoom_support(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Remove zoom methods to simulate software renderer
        delattr(mock_main_window.preview, "zoomFactor")
        delattr(mock_main_window.preview, "setZoomFactor")

        state = EditorState(mock_main_window)
        state.zoom(2)  # Should not crash

        # Font size should still increase
        assert state.editor.font().pointSize() > 10


@pytest.mark.unit
class TestDarkModeToggle:
    """Test suite for dark mode toggle."""

    def test_toggle_dark_mode_flips_state(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        mock_main_window._settings.dark_mode = False
        mock_main_window.update_preview = Mock()  # Mock to prevent crashes

        state.toggle_dark_mode()

        # Should apply theme (no arguments, reads from settings)
        mock_main_window.theme_manager.apply_theme.assert_called_once()
        # Dark mode should be flipped to True
        assert mock_main_window._settings.dark_mode is True

    def test_toggle_dark_mode_updates_menu_checkbox(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        mock_main_window._settings.dark_mode = False
        state.toggle_dark_mode()

        # Should set checkbox to True
        mock_main_window.action_manager.dark_mode_act.setChecked.assert_called_with(
            True
        )

    def test_toggle_dark_mode_blocks_signals(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        state.toggle_dark_mode()

        # Should block and unblock signals
        mock_main_window.action_manager.dark_mode_act.blockSignals.assert_called()


@pytest.mark.unit
class TestSyncScrollingToggle:
    """Test suite for sync scrolling toggle."""

    def test_toggle_sync_scrolling_flips_state(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        initial_state = state.sync_scrolling
        state.toggle_sync_scrolling()

        assert state.sync_scrolling != initial_state

    def test_toggle_sync_scrolling_reads_from_checkbox(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        # Set checkbox state
        mock_main_window.action_manager.sync_scrolling_act.isChecked = Mock(
            return_value=False
        )

        state.toggle_sync_scrolling()

        # Should read from checkbox and update internal state
        mock_main_window.action_manager.sync_scrolling_act.isChecked.assert_called()
        assert state.sync_scrolling is False


@pytest.mark.unit
class TestPaneMaximization:
    """Test suite for pane maximize/restore functionality."""

    def test_toggle_pane_maximize_maximizes_editor(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        state.toggle_pane_maximize("editor")

        assert state.maximized_pane == "editor"
        assert state.saved_splitter_sizes is not None

    def test_toggle_pane_maximize_restores_when_already_maximized(
        self, mock_main_window
    ):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        # Maximize first
        state.toggle_pane_maximize("editor")
        # Toggle again should restore
        state.toggle_pane_maximize("editor")

        assert state.maximized_pane is None

    def test_maximize_pane_saves_splitter_sizes(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        original_sizes = state.splitter.sizes()
        state.maximize_pane("preview")

        assert state.saved_splitter_sizes == original_sizes

    def test_maximize_pane_sets_editor_visibility(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        state.maximize_pane("preview")

        # Editor should be hidden when preview maximized
        # (Implementation detail: splitter sizes set to [0, large_number])
        sizes = state.splitter.sizes()
        assert sizes[0] == 0 or sizes[1] > sizes[0] * 10

    def test_restore_panes_resets_splitter_sizes(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        # Maximize and save sizes
        state.maximize_pane("editor")
        # Restore
        state.restore_panes()

        assert state.maximized_pane is None

    def test_restore_panes_shows_all_panes(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        state.maximize_pane("preview")
        state.restore_panes()

        # Both panes should be visible
        sizes = state.splitter.sizes()
        assert all(size > 0 for size in sizes)


@pytest.mark.unit
class TestCloseEventHandling:
    """Test suite for window close event handling."""

    def test_handle_close_event_accepts_event(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        event = Mock()
        event.accept = Mock()

        # Need to mock the shutdown methods
        with patch.object(state, "_shutdown_threads"):
            with patch.object(state, "_cleanup_temp_files"):
                state.handle_close_event(event)

        event.accept.assert_called_once()

    def test_handle_close_event_calls_shutdown(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        event = Mock()
        event.accept = Mock()

        with patch.object(state, "_shutdown_threads") as mock_shutdown:
            with patch.object(state, "_cleanup_temp_files"):
                state.handle_close_event(event)

        mock_shutdown.assert_called_once()


@pytest.mark.unit
class TestEdgeCases:
    """Test suite for edge cases."""

    def test_zoom_zero_delta_no_change(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        initial_size = state.editor.font().pointSize()
        state.zoom(0)

        assert state.editor.font().pointSize() == initial_size

    def test_maximize_unknown_pane_ignored(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        # Should not crash
        state.maximize_pane("unknown_pane")

        # State should not change
        assert state.maximized_pane in [None, "unknown_pane"]


@pytest.mark.unit
class TestThreePaneLayoutMaximization:
    """Test suite for 3-pane layout (editor/preview/chat) maximization."""

    def test_maximize_editor_with_chat_visible(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Setup 3-pane layout
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)
        mock_main_window.splitter.setSizes([400, 400, 200])
        mock_main_window.chat_container = Mock()
        mock_main_window.chat_container.isVisible = Mock(return_value=True)

        state = EditorState(mock_main_window)
        state.maximize_pane("editor")

        # Editor maximized, chat visible
        sizes = state.splitter.sizes()
        assert sizes[1] == 0  # Preview hidden
        assert sizes[2] > 0  # Chat still visible

    def test_maximize_editor_with_chat_hidden(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Setup 3-pane layout with hidden chat
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)
        mock_main_window.splitter.setSizes([400, 400, 0])
        mock_main_window.chat_container = Mock()
        mock_main_window.chat_container.isVisible = Mock(return_value=False)

        state = EditorState(mock_main_window)
        state.maximize_pane("editor")

        # Editor maximized, both preview and chat hidden
        sizes = state.splitter.sizes()
        assert sizes[1] == 0  # Preview hidden
        assert sizes[2] == 0  # Chat hidden

    def test_maximize_preview_with_chat_visible(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Setup 3-pane layout
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)
        mock_main_window.splitter.setSizes([400, 400, 200])
        mock_main_window.chat_container = Mock()
        mock_main_window.chat_container.isVisible = Mock(return_value=True)

        state = EditorState(mock_main_window)
        state.maximize_pane("preview")

        # Preview maximized, chat visible
        sizes = state.splitter.sizes()
        assert sizes[0] == 0  # Editor hidden
        assert sizes[2] > 0  # Chat still visible

    def test_maximize_preview_with_chat_hidden(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Setup 3-pane layout with hidden chat
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)
        mock_main_window.splitter.setSizes([400, 400, 0])
        mock_main_window.chat_container = Mock()
        mock_main_window.chat_container.isVisible = Mock(return_value=False)

        state = EditorState(mock_main_window)
        state.maximize_pane("preview")

        # Preview maximized, both editor and chat hidden
        sizes = state.splitter.sizes()
        assert sizes[0] == 0  # Editor hidden
        assert sizes[2] == 0  # Chat hidden

    def test_saved_splitter_sizes_stored_on_first_maximize(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Setup 3-pane layout
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)
        mock_main_window.splitter.setSizes([400, 400, 200])

        state = EditorState(mock_main_window)
        assert state.saved_splitter_sizes is None

        state.maximize_pane("editor")

        # Qt adjusts sizes based on actual widget width, just check it's saved
        assert state.saved_splitter_sizes is not None
        assert len(state.saved_splitter_sizes) == 3

    def test_button_states_updated_for_3pane_maximize(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Setup 3-pane layout
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)

        state = EditorState(mock_main_window)
        state.maximize_pane("editor")

        # Check button states
        assert state.editor_max_btn.text() == "⬛"
        assert "Restore" in state.editor_max_btn.toolTip()
        assert state.preview_max_btn.isEnabled()


@pytest.mark.unit
class TestThreePaneLayoutRestore:
    """Test suite for restoring 3-pane layouts."""

    def test_restore_from_3pane_saved_sizes(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Setup and maximize
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)
        mock_main_window.splitter.setSizes([400, 400, 200])
        mock_main_window.chat_container = Mock()
        mock_main_window.chat_container.isVisible = Mock(return_value=True)

        state = EditorState(mock_main_window)
        original_sizes = state.splitter.sizes()  # Get actual sizes after Qt adjustment
        state.maximize_pane("editor")
        state.restore_panes()

        # Should restore to sizes before maximize (with Qt adjustments)
        assert state.splitter.sizes() == original_sizes

    def test_restore_with_invalid_saved_sizes(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Setup 3-pane layout
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)
        mock_main_window.splitter.setSizes([400, 400, 200])
        mock_main_window.chat_container = Mock()
        mock_main_window.chat_container.isVisible = Mock(return_value=True)

        state = EditorState(mock_main_window)
        state.saved_splitter_sizes = [0, 0, 0]  # Invalid (sum is 0)
        state.restore_panes()

        # Should use defaults instead
        sizes = state.splitter.sizes()
        assert all(size >= 0 for size in sizes)

    def test_restore_from_2pane_to_3pane_layout(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Start with 2-pane, save sizes, then add chat
        state = EditorState(mock_main_window)
        state.saved_splitter_sizes = [500, 500]  # 2-pane sizes saved

        # Now add chat pane
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)
        mock_main_window.chat_container = Mock()
        mock_main_window.chat_container.isVisible = Mock(return_value=True)

        state.restore_panes()

        # Should adapt to 3-pane layout
        sizes = state.splitter.sizes()
        assert len(sizes) == 3
        assert sizes[2] > 0  # Chat gets space

    def test_restore_clears_maximized_pane_state(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        state.maximize_pane("editor")
        assert state.maximized_pane == "editor"

        state.restore_panes()

        assert state.maximized_pane is None

    def test_restore_resets_button_states(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        state.maximize_pane("preview")
        state.restore_panes()

        # Both buttons should be in default state
        assert state.editor_max_btn.text() == "⬜"
        assert state.preview_max_btn.text() == "⬜"
        assert state.editor_max_btn.isEnabled()
        assert state.preview_max_btn.isEnabled()

    def test_restore_with_chat_hidden_collapses_chat_pane(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Setup 3-pane with hidden chat
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)
        mock_main_window.chat_container = Mock()
        mock_main_window.chat_container.isVisible = Mock(return_value=False)

        state = EditorState(mock_main_window)
        # Use actual current sizes (Qt-adjusted) as saved sizes
        actual_sizes = state.splitter.sizes()
        state.saved_splitter_sizes = actual_sizes
        state.restore_panes()

        # Chat should be collapsed (very small or zero)
        sizes = state.splitter.sizes()
        assert sizes[2] < 10  # Allow for Qt rounding


@pytest.mark.unit
class TestSplitterSizeEdgeCases:
    """Test suite for splitter size edge cases and error handling."""

    def test_maximize_with_zero_splitter_width(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Mock splitter width as 0
        mock_main_window.splitter.width = Mock(return_value=0)

        state = EditorState(mock_main_window)
        state.maximize_pane("editor")  # Should not crash

        assert state.maximized_pane == "editor"

    def test_restore_with_wrong_number_of_saved_sizes(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        state.saved_splitter_sizes = [300]  # Only 1 size for 2-pane layout

        state.restore_panes()  # Should not crash

        # Should fall back to defaults
        assert state.maximized_pane is None

    def test_toggle_between_different_panes(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        # Maximize editor
        state.toggle_pane_maximize("editor")
        assert state.maximized_pane == "editor"

        # Toggle to preview (different pane)
        state.toggle_pane_maximize("preview")
        assert state.maximized_pane == "preview"

    def test_saved_sizes_not_overwritten_on_second_maximize(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        original_sizes = [400, 600]
        mock_main_window.splitter.setSizes(original_sizes)

        state = EditorState(mock_main_window)

        # First maximize saves sizes
        state.maximize_pane("editor")
        saved = state.saved_splitter_sizes

        # Second maximize shouldn't overwrite
        state.maximize_pane("preview")

        assert state.saved_splitter_sizes == saved

    def test_restore_with_negative_saved_sizes(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        state.saved_splitter_sizes = [-100, 500]  # Invalid negative size

        state.restore_panes()  # Should handle gracefully

        # Should use defaults
        sizes = state.splitter.sizes()
        assert all(size >= 0 for size in sizes)


@pytest.mark.unit
class TestDefaultSizeApplication:
    """Test suite for _apply_default_sizes method."""

    def test_apply_default_sizes_2pane_layout(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        state._apply_default_sizes(has_chat=False, chat_visible=False)

        # Should be 50/50 split
        sizes = state.splitter.sizes()
        assert len(sizes) == 2
        assert abs(sizes[0] - sizes[1]) <= 1  # Allow 1px rounding

    def test_apply_default_sizes_3pane_chat_visible(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Add chat pane
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)

        state = EditorState(mock_main_window)
        state._apply_default_sizes(has_chat=True, chat_visible=True)

        # Should be 40/40/20 split
        sizes = state.splitter.sizes()
        assert len(sizes) == 3
        assert sizes[2] < sizes[0]  # Chat smaller than editor
        assert sizes[2] < sizes[1]  # Chat smaller than preview

    def test_apply_default_sizes_3pane_chat_hidden(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Add chat pane
        chat_widget = QPlainTextEdit()
        mock_main_window.splitter.addWidget(chat_widget)

        state = EditorState(mock_main_window)
        state._apply_default_sizes(has_chat=True, chat_visible=False)

        # Should be 50/50/0 split
        sizes = state.splitter.sizes()
        assert len(sizes) == 3
        assert sizes[2] == 0  # Chat collapsed
        assert abs(sizes[0] - sizes[1]) <= 1  # Editor/preview equal

    def test_default_sizes_adapt_to_splitter_width(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        # Get actual splitter width
        actual_width = state.splitter.width()

        state._apply_default_sizes(has_chat=False, chat_visible=False)

        sizes = state.splitter.sizes()
        total = sum(sizes)
        # Total should be close to actual splitter width (Qt may adjust)
        # Allow 50% tolerance since Qt adjusts based on constraints
        assert total >= actual_width * 0.5
        assert total <= actual_width * 1.5

    def test_default_sizes_called_during_restore_fallback(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        state.saved_splitter_sizes = None  # No saved sizes

        with patch.object(state, "_apply_default_sizes") as mock_apply:
            state.restore_panes()

            # Should call _apply_default_sizes as fallback
            mock_apply.assert_called_once()


@pytest.mark.unit
class TestPreviewHandlerIntegration:
    """Test suite for preview handler integration."""

    def test_toggle_dark_mode_clears_css_cache(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Mock preview handler with clear_css_cache method
        mock_main_window.preview_handler = Mock()
        mock_main_window.preview_handler.clear_css_cache = Mock()
        mock_main_window.update_preview = Mock()

        state = EditorState(mock_main_window)
        state.toggle_dark_mode()

        # Should call clear_css_cache
        mock_main_window.preview_handler.clear_css_cache.assert_called_once()

    def test_toggle_dark_mode_updates_preview(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        mock_main_window.update_preview = Mock()
        mock_main_window.preview_handler = Mock()

        state = EditorState(mock_main_window)
        state.toggle_dark_mode()

        # Should trigger preview update
        mock_main_window.update_preview.assert_called_once()

    def test_toggle_dark_mode_without_preview_handler(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Remove preview_handler attribute
        (
            delattr(mock_main_window, "preview_handler")
            if hasattr(mock_main_window, "preview_handler")
            else None
        )
        mock_main_window.update_preview = Mock()

        state = EditorState(mock_main_window)
        state.toggle_dark_mode()  # Should not crash

        # Preview update should still be called
        mock_main_window.update_preview.assert_called_once()

    def test_theme_manager_apply_theme_called(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        state.toggle_dark_mode()

        # Should apply theme
        state.theme_manager.apply_theme.assert_called_once()

    def test_settings_dark_mode_state_updated(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        initial_dark_mode = mock_main_window._settings.dark_mode
        mock_main_window.update_preview = Mock()

        state = EditorState(mock_main_window)
        state.toggle_dark_mode()

        # Dark mode should be flipped
        assert mock_main_window._settings.dark_mode != initial_dark_mode


@pytest.mark.unit
class TestThreadShutdown:
    """Test suite for worker thread shutdown."""

    def test_shutdown_running_threads(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Force fallback code path by not having worker_manager
        mock_main_window.worker_manager = None

        # Mock running threads
        mock_main_window.git_thread = Mock()
        mock_main_window.git_thread.isRunning = Mock(return_value=True)
        mock_main_window.git_thread.quit = Mock()
        mock_main_window.git_thread.wait = Mock(return_value=True)

        mock_main_window.pandoc_thread = Mock()
        mock_main_window.pandoc_thread.isRunning = Mock(return_value=True)
        mock_main_window.pandoc_thread.quit = Mock()
        mock_main_window.pandoc_thread.wait = Mock(return_value=True)

        mock_main_window.preview_thread = Mock()
        mock_main_window.preview_thread.isRunning = Mock(return_value=True)
        mock_main_window.preview_thread.quit = Mock()
        mock_main_window.preview_thread.wait = Mock(return_value=True)

        state = EditorState(mock_main_window)
        state._shutdown_threads()

        # All threads should be stopped
        mock_main_window.git_thread.quit.assert_called_once()
        mock_main_window.pandoc_thread.quit.assert_called_once()
        mock_main_window.preview_thread.quit.assert_called_once()

    def test_shutdown_already_stopped_threads(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Mock stopped threads
        mock_main_window.git_thread = Mock()
        mock_main_window.git_thread.isRunning = Mock(return_value=False)
        mock_main_window.git_thread.quit = Mock()

        state = EditorState(mock_main_window)
        state._shutdown_threads()

        # quit() should not be called for stopped threads
        mock_main_window.git_thread.quit.assert_not_called()

    def test_shutdown_handles_stuck_threads(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Force fallback code path by not having worker_manager
        mock_main_window.worker_manager = None

        # Mock thread that doesn't stop within timeout
        mock_main_window.git_thread = Mock()
        mock_main_window.git_thread.isRunning = Mock(return_value=True)
        mock_main_window.git_thread.quit = Mock()
        mock_main_window.git_thread.wait = Mock(return_value=False)  # Timeout

        mock_main_window.pandoc_thread = None
        mock_main_window.preview_thread = None

        state = EditorState(mock_main_window)
        state._shutdown_threads()  # Should not crash

        # Should have tried to stop thread
        mock_main_window.git_thread.quit.assert_called_once()

    def test_shutdown_with_none_threads(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Set all threads to None
        mock_main_window.git_thread = None
        mock_main_window.pandoc_thread = None
        mock_main_window.preview_thread = None

        state = EditorState(mock_main_window)
        state._shutdown_threads()  # Should not crash

    def test_shutdown_waits_with_timeout(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Force fallback code path by not having worker_manager
        mock_main_window.worker_manager = None

        # Mock thread that responds to wait()
        mock_main_window.git_thread = Mock()
        mock_main_window.git_thread.isRunning = Mock(return_value=True)
        mock_main_window.git_thread.quit = Mock()
        mock_main_window.git_thread.wait = Mock(return_value=True)

        mock_main_window.pandoc_thread = None
        mock_main_window.preview_thread = None

        state = EditorState(mock_main_window)
        state._shutdown_threads()

        # Should wait with 1000ms timeout
        mock_main_window.git_thread.wait.assert_called_once_with(1000)

    def test_shutdown_mixed_thread_states(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Force fallback code path by not having worker_manager
        mock_main_window.worker_manager = None

        # Mix of running, stopped, and None threads
        mock_main_window.git_thread = Mock()
        mock_main_window.git_thread.isRunning = Mock(return_value=True)
        mock_main_window.git_thread.quit = Mock()
        mock_main_window.git_thread.wait = Mock(return_value=True)

        mock_main_window.pandoc_thread = Mock()
        mock_main_window.pandoc_thread.isRunning = Mock(return_value=False)

        mock_main_window.preview_thread = None

        state = EditorState(mock_main_window)
        state._shutdown_threads()

        # Only running thread should be quit
        mock_main_window.git_thread.quit.assert_called_once()


@pytest.mark.unit
class TestTempFileCleanup:
    """Test suite for temporary file cleanup."""

    def test_cleanup_calls_export_manager_cleanup(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        mock_main_window.export_manager = Mock()
        mock_main_window.export_manager.cleanup = Mock()

        state = EditorState(mock_main_window)
        state._cleanup_temp_files()

        mock_main_window.export_manager.cleanup.assert_called_once()

    def test_cleanup_handles_export_manager_error(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        mock_main_window.export_manager = Mock()
        mock_main_window.export_manager.cleanup = Mock(
            side_effect=Exception("Cleanup failed")
        )

        state = EditorState(mock_main_window)
        state._cleanup_temp_files()  # Should not crash

    def test_cleanup_handles_missing_export_manager(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Remove export_manager attribute
        if hasattr(mock_main_window, "export_manager"):
            delattr(mock_main_window, "export_manager")

        state = EditorState(mock_main_window)
        state._cleanup_temp_files()  # Should not crash

    def test_cleanup_calls_old_temp_dir_cleanup(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        mock_main_window._temp_dir = Mock()
        mock_main_window._temp_dir.cleanup = Mock()

        state = EditorState(mock_main_window)
        state._cleanup_temp_files()

        mock_main_window._temp_dir.cleanup.assert_called_once()


@pytest.mark.unit
class TestCloseEventWithUnsavedChanges:
    """Test suite for close event handling with unsaved changes."""

    def test_close_event_user_cancels(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # User cancels save prompt
        mock_main_window.status_manager = Mock()
        mock_main_window.status_manager.prompt_save_before_action = Mock(
            return_value=False
        )

        state = EditorState(mock_main_window)
        event = Mock()
        event.ignore = Mock()

        state.handle_close_event(event)

        # Event should be ignored
        event.ignore.assert_called_once()

    def test_close_event_user_proceeds(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # User proceeds with close
        mock_main_window.status_manager = Mock()
        mock_main_window.status_manager.prompt_save_before_action = Mock(
            return_value=True
        )
        mock_main_window._settings_manager = Mock()
        mock_main_window._settings_manager.save_settings_immediate = Mock()
        mock_main_window._current_file_path = None

        # Mock threads
        mock_main_window.git_thread = None
        mock_main_window.pandoc_thread = None
        mock_main_window.preview_thread = None

        state = EditorState(mock_main_window)
        event = Mock()
        event.accept = Mock()

        state.handle_close_event(event)

        # Event should be accepted
        event.accept.assert_called_once()

    def test_close_event_saves_settings_immediately(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        mock_main_window.status_manager = Mock()
        mock_main_window.status_manager.prompt_save_before_action = Mock(
            return_value=True
        )
        mock_main_window._settings_manager = Mock()
        mock_main_window._settings_manager.save_settings_immediate = Mock()
        mock_main_window._current_file_path = "/tmp/test.adoc"
        mock_main_window.git_thread = None
        mock_main_window.pandoc_thread = None
        mock_main_window.preview_thread = None

        state = EditorState(mock_main_window)
        event = Mock()

        state.handle_close_event(event)

        # Settings should be saved
        mock_main_window._settings_manager.save_settings_immediate.assert_called_once()

    def test_close_event_shuts_down_threads(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        mock_main_window.status_manager = Mock()
        mock_main_window.status_manager.prompt_save_before_action = Mock(
            return_value=True
        )
        mock_main_window._settings_manager = Mock()
        mock_main_window._settings_manager.save_settings_immediate = Mock()
        mock_main_window._current_file_path = None

        state = EditorState(mock_main_window)
        event = Mock()

        with patch.object(state, "_shutdown_threads") as mock_shutdown:
            state.handle_close_event(event)

            mock_shutdown.assert_called_once()

    def test_close_event_cleans_up_temp_files(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        mock_main_window.status_manager = Mock()
        mock_main_window.status_manager.prompt_save_before_action = Mock(
            return_value=True
        )
        mock_main_window._settings_manager = Mock()
        mock_main_window._settings_manager.save_settings_immediate = Mock()
        mock_main_window._current_file_path = None
        mock_main_window.git_thread = None
        mock_main_window.pandoc_thread = None
        mock_main_window.preview_thread = None

        state = EditorState(mock_main_window)
        event = Mock()

        with patch.object(state, "_cleanup_temp_files") as mock_cleanup:
            state.handle_close_event(event)

            mock_cleanup.assert_called_once()

    def test_close_event_prompt_action_is_closing(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        mock_main_window.status_manager = Mock()
        mock_main_window.status_manager.prompt_save_before_action = Mock(
            return_value=True
        )
        mock_main_window._settings_manager = Mock()
        mock_main_window._settings_manager.save_settings_immediate = Mock()
        mock_main_window._current_file_path = None
        mock_main_window.git_thread = None
        mock_main_window.pandoc_thread = None
        mock_main_window.preview_thread = None

        state = EditorState(mock_main_window)
        event = Mock()

        state.handle_close_event(event)

        # Should pass "closing" as action
        mock_main_window.status_manager.prompt_save_before_action.assert_called_once_with(
            "closing"
        )


@pytest.mark.unit
class TestZoomBoundaryConditions:
    """Test suite for zoom boundary conditions and clamping."""

    def test_zoom_preview_factor_clamped_at_minimum(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Set preview to minimum zoom
        mock_main_window.preview.zoomFactor = Mock(return_value=0.25)
        mock_main_window.preview.setZoomFactor = Mock()

        state = EditorState(mock_main_window)
        state.zoom(-10)  # Large negative delta

        # Should clamp at 0.25
        call_args = mock_main_window.preview.setZoomFactor.call_args
        if call_args:
            assert call_args[0][0] >= 0.25

    def test_zoom_preview_factor_clamped_at_maximum(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        # Set preview to maximum zoom
        mock_main_window.preview.zoomFactor = Mock(return_value=5.0)
        mock_main_window.preview.setZoomFactor = Mock()

        state = EditorState(mock_main_window)
        state.zoom(10)  # Large positive delta

        # Should clamp at 5.0
        call_args = mock_main_window.preview.setZoomFactor.call_args
        if call_args:
            assert call_args[0][0] <= 5.0

    def test_zoom_large_positive_delta(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        initial_size = state.editor.font().pointSize()

        state.zoom(100)  # Very large zoom in

        # Font size should increase significantly
        assert state.editor.font().pointSize() > initial_size

    def test_zoom_large_negative_delta(self, mock_main_window):
        from asciidoc_artisan.core import MIN_FONT_SIZE
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        state.zoom(-1000)  # Extremely large zoom out

        # Should be clamped at minimum
        assert state.editor.font().pointSize() == MIN_FONT_SIZE

    def test_zoom_delta_to_zoom_factor_conversion(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        mock_main_window.preview.zoomFactor = Mock(return_value=1.0)
        mock_main_window.preview.setZoomFactor = Mock()

        state = EditorState(mock_main_window)
        state.zoom(1)  # Delta of 1

        # Should convert to 0.1 zoom factor change
        call_args = mock_main_window.preview.setZoomFactor.call_args
        if call_args:
            new_zoom = call_args[0][0]
            assert 1.05 <= new_zoom <= 1.15  # Approximately 1.1


@pytest.mark.unit
class TestButtonAndStatusBarUpdates:
    """Test suite for button and status bar message consistency."""

    def test_maximize_editor_button_text_changes(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        # Before maximize
        initial_text = state.editor_max_btn.text()

        state.maximize_pane("editor")

        # Button text should change
        assert state.editor_max_btn.text() != initial_text
        assert state.editor_max_btn.text() == "⬛"

    def test_maximize_preview_button_text_changes(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        state.maximize_pane("preview")

        assert state.preview_max_btn.text() == "⬛"

    def test_maximize_shows_status_message(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        state.maximize_pane("editor")

        # Should show status message
        state.status_bar.showMessage.assert_called()
        call_args = str(state.status_bar.showMessage.call_args)
        assert "maximized" in call_args.lower()

    def test_restore_shows_status_message(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        state.maximize_pane("editor")

        state.restore_panes()

        # Should show restore message
        call_args_list = [
            str(call) for call in state.status_bar.showMessage.call_args_list
        ]
        assert any("restored" in call.lower() for call in call_args_list)

    def test_sync_scrolling_shows_status_message(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)
        mock_main_window.action_manager.sync_scrolling_act.isChecked = Mock(
            return_value=False
        )

        state.toggle_sync_scrolling()

        # Should show sync scrolling message
        state.status_bar.showMessage.assert_called()
        call_args = str(state.status_bar.showMessage.call_args)
        assert "scrolling" in call_args.lower()

    def test_button_tooltips_updated_on_maximize(self, mock_main_window):
        from asciidoc_artisan.ui.editor_state import EditorState

        state = EditorState(mock_main_window)

        state.maximize_pane("editor")

        # Tooltips should reflect current state
        assert "Restore" in state.editor_max_btn.toolTip()
        assert "Maximize" in state.preview_max_btn.toolTip()
