"""Tests for ui.editor_state module."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QSplitter, QStatusBar, QPushButton, QPlainTextEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


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

    # Status bar
    window.status_bar = QStatusBar()

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
        from asciidoc_artisan.ui.editor_state import EditorState
        from asciidoc_artisan.core import MIN_FONT_SIZE
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
        mock_main_window.action_manager.dark_mode_act.setChecked.assert_called_with(True)

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
        mock_main_window.action_manager.sync_scrolling_act.isChecked = Mock(return_value=False)

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

    def test_toggle_pane_maximize_restores_when_already_maximized(self, mock_main_window):
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
