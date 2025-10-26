"""
Tests for pane maximization functionality (FR-044).

Comprehensive integration tests for editor and preview pane maximize/restore.
"""

import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import MagicMock, patch


# Mock the main_window module to avoid GUI initialization
@pytest.fixture
def mock_editor_state():
    """Create a mock EditorState for testing."""
    from asciidoc_artisan.ui.editor_state import EditorState

    # Create mock main window with all required attributes
    mock_window = MagicMock()
    mock_window.editor = MagicMock()
    mock_window.preview = MagicMock()
    mock_window.splitter = MagicMock()
    mock_window.splitter.width.return_value = 1000
    mock_window.splitter.sizes.return_value = [500, 500]
    mock_window.status_bar = MagicMock()
    mock_window.editor_max_btn = MagicMock()
    mock_window.preview_max_btn = MagicMock()
    mock_window.theme_manager = MagicMock()
    mock_window._settings = MagicMock()
    mock_window.action_manager = MagicMock()

    # Create EditorState instance
    state = EditorState(mock_window)

    return state


class TestPaneMaximization:
    """Test pane maximize/restore functionality."""

    def test_initial_state(self, mock_editor_state):
        """Test initial state is not maximized."""
        assert mock_editor_state.maximized_pane is None
        assert mock_editor_state.saved_splitter_sizes is None

    def test_maximize_editor(self, mock_editor_state):
        """Test maximizing editor pane."""
        # Setup
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        # Execute
        mock_editor_state.maximize_pane("editor")

        # Verify
        assert mock_editor_state.maximized_pane == "editor"
        assert mock_editor_state.saved_splitter_sizes == [500, 500]
        mock_editor_state.splitter.setSizes.assert_called_with([1000, 0])
        mock_editor_state.editor_max_btn.setText.assert_called_with("⬛")
        mock_editor_state.status_bar.showMessage.assert_called()

    def test_maximize_preview(self, mock_editor_state):
        """Test maximizing preview pane."""
        # Setup
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        # Execute
        mock_editor_state.maximize_pane("preview")

        # Verify
        assert mock_editor_state.maximized_pane == "preview"
        assert mock_editor_state.saved_splitter_sizes == [500, 500]
        mock_editor_state.splitter.setSizes.assert_called_with([0, 1000])
        mock_editor_state.preview_max_btn.setText.assert_called_with("⬛")
        mock_editor_state.status_bar.showMessage.assert_called()

    def test_restore_panes(self, mock_editor_state):
        """Test restoring panes to original sizes."""
        # Setup - maximize editor first
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")

        # Execute restore
        mock_editor_state.restore_panes()

        # Verify
        assert mock_editor_state.maximized_pane is None
        mock_editor_state.splitter.setSizes.assert_called_with([500, 500])
        mock_editor_state.editor_max_btn.setText.assert_called_with("⬜")
        mock_editor_state.preview_max_btn.setText.assert_called_with("⬜")

    def test_toggle_maximize_from_normal(self, mock_editor_state):
        """Test toggling maximization from normal view."""
        # Setup
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        # Execute
        mock_editor_state.toggle_pane_maximize("editor")

        # Verify - should maximize
        assert mock_editor_state.maximized_pane == "editor"

    def test_toggle_maximize_from_maximized(self, mock_editor_state):
        """Test toggling maximization when already maximized."""
        # Setup - maximize editor
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")

        # Execute - toggle same pane
        mock_editor_state.toggle_pane_maximize("editor")

        # Verify - should restore
        assert mock_editor_state.maximized_pane is None

    def test_switch_maximized_pane(self, mock_editor_state):
        """Test switching from one maximized pane to another."""
        # Setup - maximize editor
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")

        # Execute - maximize preview instead
        mock_editor_state.toggle_pane_maximize("preview")

        # Verify - should now maximize preview
        assert mock_editor_state.maximized_pane == "preview"
        mock_editor_state.splitter.setSizes.assert_called_with([0, 1000])

    def test_saved_sizes_persist(self, mock_editor_state):
        """Test that saved sizes persist across maximize operations."""
        # Setup
        original_sizes = [400, 600]
        mock_editor_state.splitter.sizes.return_value = original_sizes

        # Maximize editor
        mock_editor_state.maximize_pane("editor")
        assert mock_editor_state.saved_splitter_sizes == original_sizes

        # Switch to preview (sizes should still be saved)
        mock_editor_state.maximize_pane("preview")
        assert mock_editor_state.saved_splitter_sizes == original_sizes

        # Restore
        mock_editor_state.restore_panes()
        mock_editor_state.splitter.setSizes.assert_called_with(original_sizes)


class TestPaneMaximizationEdgeCases:
    """Test edge cases for pane maximization."""

    def test_maximize_with_zero_width(self, mock_editor_state):
        """Test maximizing when splitter has zero width."""
        # Setup
        mock_editor_state.splitter.width.return_value = 0
        mock_editor_state.splitter.sizes.return_value = [0, 0]

        # Execute
        mock_editor_state.maximize_pane("editor")

        # Verify - should handle gracefully
        assert mock_editor_state.maximized_pane == "editor"
        mock_editor_state.splitter.setSizes.assert_called_with([0, 0])

    def test_restore_without_maximize(self, mock_editor_state):
        """Test restoring when not maximized."""
        # Execute
        mock_editor_state.restore_panes()

        # Verify - should handle gracefully by setting 50/50 split
        assert mock_editor_state.maximized_pane is None
        # Should set to 50/50 split (fallback behavior)
        mock_editor_state.splitter.setSizes.assert_called()
        call_args = mock_editor_state.splitter.setSizes.call_args[0][0]
        # Should be roughly 50/50 split
        assert call_args[0] > 0 and call_args[1] > 0

    def test_multiple_maximize_same_pane(self, mock_editor_state):
        """Test maximizing same pane multiple times."""
        # Setup
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        # Execute - maximize editor twice
        mock_editor_state.maximize_pane("editor")
        first_saved = mock_editor_state.saved_splitter_sizes

        mock_editor_state.maximize_pane("editor")
        second_saved = mock_editor_state.saved_splitter_sizes

        # Verify - saved sizes should not change on second maximize
        assert first_saved == second_saved

    def test_button_states_after_maximize(self, mock_editor_state):
        """Test button states are updated correctly."""
        # Maximize editor
        mock_editor_state.maximize_pane("editor")

        # Verify editor button shows "restore" state
        mock_editor_state.editor_max_btn.setText.assert_called_with("⬛")
        mock_editor_state.editor_max_btn.setToolTip.assert_called_with("Restore editor")

        # Verify preview button still enabled
        mock_editor_state.preview_max_btn.setEnabled.assert_called_with(True)

    def test_button_states_after_restore(self, mock_editor_state):
        """Test button states after restoring panes."""
        # Setup - maximize then restore
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")
        mock_editor_state.restore_panes()

        # Verify both buttons show normal state
        calls = mock_editor_state.editor_max_btn.setText.call_args_list
        assert any("⬜" in str(call) for call in calls)


class TestPaneMaximizationStateManagement:
    """Test state management during pane operations."""

    def test_state_cleared_on_restore(self, mock_editor_state):
        """Test that state is properly cleared on restore."""
        # Setup and maximize
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")

        # Restore
        mock_editor_state.restore_panes()

        # Verify state is cleared
        assert mock_editor_state.maximized_pane is None

    def test_saved_sizes_not_lost_on_switch(self, mock_editor_state):
        """Test saved sizes are preserved when switching panes."""
        # Setup
        original_sizes = [300, 700]
        mock_editor_state.splitter.sizes.return_value = original_sizes

        # Maximize editor
        mock_editor_state.maximize_pane("editor")
        saved_sizes = mock_editor_state.saved_splitter_sizes

        # Switch to preview
        mock_editor_state.maximize_pane("preview")

        # Verify sizes still saved
        assert mock_editor_state.saved_splitter_sizes == saved_sizes
        assert mock_editor_state.saved_splitter_sizes == original_sizes

    def test_status_messages(self, mock_editor_state):
        """Test status bar messages are shown."""
        # Maximize editor
        mock_editor_state.maximize_pane("editor")
        calls = mock_editor_state.status_bar.showMessage.call_args_list
        assert any("Editor maximized" in str(call) for call in calls)

        # Reset and maximize preview
        mock_editor_state.status_bar.reset_mock()
        mock_editor_state.maximize_pane("preview")
        calls = mock_editor_state.status_bar.showMessage.call_args_list
        assert any("Preview maximized" in str(call) for call in calls)


class TestPaneMaximizationIntegration:
    """Integration tests for pane maximization workflow."""

    def test_complete_workflow(self, mock_editor_state):
        """Test complete maximize/restore workflow."""
        # Setup
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        # Step 1: Start in normal view
        assert mock_editor_state.maximized_pane is None

        # Step 2: Maximize editor
        mock_editor_state.toggle_pane_maximize("editor")
        assert mock_editor_state.maximized_pane == "editor"

        # Step 3: Switch to preview
        mock_editor_state.toggle_pane_maximize("preview")
        assert mock_editor_state.maximized_pane == "preview"

        # Step 4: Restore
        mock_editor_state.toggle_pane_maximize("preview")
        assert mock_editor_state.maximized_pane is None

    def test_rapid_toggle(self, mock_editor_state):
        """Test rapid toggling doesn't break state."""
        # Setup
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        # Rapidly toggle even number of times (should return to normal)
        for _ in range(6):
            mock_editor_state.toggle_pane_maximize("editor")

        # Should end in normal view (even number of toggles)
        assert mock_editor_state.maximized_pane is None

    def test_window_resize_with_maximized_pane(self, mock_editor_state):
        """Test behavior when window resizes while pane is maximized."""
        # Setup
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")

        # Simulate window resize
        mock_editor_state.splitter.width.return_value = 1200

        # Re-maximize should use new width
        mock_editor_state.maximize_pane("editor")
        mock_editor_state.splitter.setSizes.assert_called_with([1200, 0])


# Additional acceptance criteria tests
class TestFR044AcceptanceCriteria:
    """Test FR-044 acceptance criteria."""

    def test_maximize_editor_pane_acceptance(self, mock_editor_state):
        """FR-044: User can maximize editor pane."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")

        assert mock_editor_state.maximized_pane == "editor"
        # Editor should take full width
        mock_editor_state.splitter.setSizes.assert_called()
        call_args = mock_editor_state.splitter.setSizes.call_args[0][0]
        assert call_args[0] > 0 and call_args[1] == 0

    def test_maximize_preview_pane_acceptance(self, mock_editor_state):
        """FR-044: User can maximize preview pane."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("preview")

        assert mock_editor_state.maximized_pane == "preview"
        # Preview should take full width
        mock_editor_state.splitter.setSizes.assert_called()
        call_args = mock_editor_state.splitter.setSizes.call_args[0][0]
        assert call_args[0] == 0 and call_args[1] > 0

    def test_restore_from_maximized_acceptance(self, mock_editor_state):
        """FR-044: User can restore panes from maximized state."""
        original_sizes = [500, 500]
        mock_editor_state.splitter.sizes.return_value = original_sizes
        mock_editor_state.maximize_pane("editor")
        mock_editor_state.restore_panes()

        assert mock_editor_state.maximized_pane is None
        mock_editor_state.splitter.setSizes.assert_called_with(original_sizes)

    def test_state_persistence_acceptance(self, mock_editor_state):
        """FR-044: Maximization state is tracked correctly."""
        # Test state transitions
        states = []

        # Normal -> Editor Maximized
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")
        states.append(mock_editor_state.maximized_pane)

        # Editor Maximized -> Preview Maximized
        mock_editor_state.maximize_pane("preview")
        states.append(mock_editor_state.maximized_pane)

        # Preview Maximized -> Normal
        mock_editor_state.restore_panes()
        states.append(mock_editor_state.maximized_pane)

        # Verify state transitions
        assert states == ["editor", "preview", None]
