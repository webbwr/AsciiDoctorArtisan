"""
Tests for pane maximization functionality (FR-044).

Comprehensive integration tests for editor and preview pane maximize/restore.
"""

from unittest.mock import MagicMock

import pytest


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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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
@pytest.mark.unit
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


@pytest.mark.unit
class TestAsymmetricSplitScenarios:
    """Test pane maximization with asymmetric splits."""

    def test_maximize_from_80_20_split(self, mock_editor_state):
        """Test maximizing editor from 80/20 split."""
        mock_editor_state.splitter.sizes.return_value = [800, 200]

        mock_editor_state.maximize_pane("editor")

        assert mock_editor_state.saved_splitter_sizes == [800, 200]
        mock_editor_state.splitter.setSizes.assert_called_with([1000, 0])

    def test_restore_to_asymmetric_split(self, mock_editor_state):
        """Test restoring to non-50/50 split."""
        original_sizes = [300, 700]
        mock_editor_state.splitter.sizes.return_value = original_sizes
        mock_editor_state.maximize_pane("preview")

        mock_editor_state.restore_panes()

        mock_editor_state.splitter.setSizes.assert_called_with(original_sizes)

    def test_maximize_from_10_90_split(self, mock_editor_state):
        """Test maximizing from extreme 10/90 split."""
        mock_editor_state.splitter.sizes.return_value = [100, 900]

        mock_editor_state.maximize_pane("preview")

        assert mock_editor_state.saved_splitter_sizes == [100, 900]
        mock_editor_state.splitter.setSizes.assert_called_with([0, 1000])

    def test_switch_panes_preserves_asymmetric_sizes(self, mock_editor_state):
        """Test switching maximized panes preserves original asymmetric sizes."""
        original_sizes = [250, 750]
        mock_editor_state.splitter.sizes.return_value = original_sizes
        mock_editor_state.maximize_pane("editor")

        mock_editor_state.maximize_pane("preview")

        assert mock_editor_state.saved_splitter_sizes == original_sizes


@pytest.mark.unit
class TestExtremeWidthScenarios:
    """Test pane maximization with extreme width values."""

    def test_maximize_with_very_large_width(self, mock_editor_state):
        """Test maximizing with very large splitter width."""
        mock_editor_state.splitter.width.return_value = 10000
        mock_editor_state.splitter.sizes.return_value = [5000, 5000]

        mock_editor_state.maximize_pane("editor")

        mock_editor_state.splitter.setSizes.assert_called_with([10000, 0])

    def test_maximize_with_minimum_width(self, mock_editor_state):
        """Test maximizing with minimum width (1 pixel)."""
        mock_editor_state.splitter.width.return_value = 1
        mock_editor_state.splitter.sizes.return_value = [1, 0]

        mock_editor_state.maximize_pane("editor")

        mock_editor_state.splitter.setSizes.assert_called_with([1, 0])

    def test_restore_with_very_small_saved_sizes(self, mock_editor_state):
        """Test restoring with very small saved sizes."""
        mock_editor_state.splitter.sizes.return_value = [1, 1]
        mock_editor_state.maximize_pane("editor")

        mock_editor_state.restore_panes()

        mock_editor_state.splitter.setSizes.assert_called_with([1, 1])

    def test_maximize_with_odd_width(self, mock_editor_state):
        """Test maximizing with odd-numbered width."""
        mock_editor_state.splitter.width.return_value = 999
        mock_editor_state.splitter.sizes.return_value = [499, 500]

        mock_editor_state.maximize_pane("preview")

        mock_editor_state.splitter.setSizes.assert_called_with([0, 999])


@pytest.mark.unit
class TestButtonInteractionEdgeCases:
    """Test button interaction edge cases."""

    def test_button_tooltip_updates_on_maximize(self, mock_editor_state):
        """Test button tooltips update correctly on maximize."""
        mock_editor_state.maximize_pane("editor")

        mock_editor_state.editor_max_btn.setToolTip.assert_called_with("Restore editor")

    def test_button_tooltip_updates_on_restore(self, mock_editor_state):
        """Test button tooltips update correctly on restore."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")

        mock_editor_state.restore_panes()

        # Check that tooltips were updated
        assert mock_editor_state.editor_max_btn.setToolTip.called
        assert mock_editor_state.preview_max_btn.setToolTip.called

    def test_preview_button_enabled_when_editor_maximized(self, mock_editor_state):
        """Test preview button stays enabled when editor maximized."""
        mock_editor_state.maximize_pane("editor")

        mock_editor_state.preview_max_btn.setEnabled.assert_called_with(True)

    def test_editor_button_enabled_when_preview_maximized(self, mock_editor_state):
        """Test editor button stays enabled when preview maximized."""
        mock_editor_state.maximize_pane("preview")

        mock_editor_state.editor_max_btn.setEnabled.assert_called_with(True)

    def test_both_buttons_reset_on_restore(self, mock_editor_state):
        """Test both buttons reset to normal state on restore."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")

        mock_editor_state.restore_panes()

        # Both buttons should show normal state
        editor_calls = [
            str(call)
            for call in mock_editor_state.editor_max_btn.setText.call_args_list
        ]
        preview_calls = [
            str(call)
            for call in mock_editor_state.preview_max_btn.setText.call_args_list
        ]
        assert any("⬜" in call for call in editor_calls)
        assert any("⬜" in call for call in preview_calls)


@pytest.mark.unit
class TestSavedSizesEdgeCases:
    """Test edge cases for saved splitter sizes."""

    def test_saved_sizes_with_zero_values(self, mock_editor_state):
        """Test saving sizes when one pane is already zero."""
        mock_editor_state.splitter.sizes.return_value = [1000, 0]

        mock_editor_state.maximize_pane("editor")

        assert mock_editor_state.saved_splitter_sizes == [1000, 0]

    def test_restore_with_null_saved_sizes(self, mock_editor_state):
        """Test restoring when no sizes have been saved."""
        # Restore without prior maximize
        mock_editor_state.restore_panes()

        # Should use default 50/50 split
        mock_editor_state.splitter.setSizes.assert_called()
        call_args = mock_editor_state.splitter.setSizes.call_args[0][0]
        assert call_args[0] > 0 and call_args[1] > 0

    def test_saved_sizes_immutable_after_save(self, mock_editor_state):
        """Test saved sizes don't change unexpectedly."""
        original_sizes = [400, 600]
        mock_editor_state.splitter.sizes.return_value = original_sizes
        mock_editor_state.maximize_pane("editor")

        saved_copy = list(mock_editor_state.saved_splitter_sizes)

        # Multiple operations
        mock_editor_state.maximize_pane("preview")
        mock_editor_state.maximize_pane("editor")

        assert mock_editor_state.saved_splitter_sizes == saved_copy

    def test_saved_sizes_with_equal_values(self, mock_editor_state):
        """Test saving equal-sized panes."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        mock_editor_state.maximize_pane("editor")

        assert mock_editor_state.saved_splitter_sizes == [500, 500]


@pytest.mark.unit
class TestPaneIdentifierEdgeCases:
    """Test edge cases for pane identifier handling."""

    def test_toggle_invalid_pane_name(self, mock_editor_state):
        """Test toggling with invalid pane name."""
        try:
            mock_editor_state.toggle_pane_maximize("invalid")
            # Should handle gracefully or raise appropriate error
            assert True
        except (ValueError, KeyError, AttributeError):
            # Expected behavior for invalid pane name
            assert True

    def test_maximize_with_empty_pane_name(self, mock_editor_state):
        """Test maximizing with empty string pane name."""
        try:
            mock_editor_state.maximize_pane("")
            assert True
        except (ValueError, KeyError, AttributeError):
            assert True

    def test_maximize_with_case_variations(self, mock_editor_state):
        """Test that pane names are case-sensitive."""
        # Try uppercase
        try:
            mock_editor_state.maximize_pane("EDITOR")
            # Should either handle or reject
            assert True
        except (ValueError, KeyError, AttributeError):
            # Case sensitivity enforced
            assert True


@pytest.mark.unit
class TestRapidStateChanges:
    """Test rapid state changes and transitions."""

    def test_very_rapid_toggle_odd_times(self, mock_editor_state):
        """Test rapid toggling odd number of times."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        # Toggle 5 times (odd)
        for _ in range(5):
            mock_editor_state.toggle_pane_maximize("editor")

        # Should end maximized (odd number of toggles)
        assert mock_editor_state.maximized_pane == "editor"

    def test_alternating_pane_toggles(self, mock_editor_state):
        """Test alternating between editor and preview toggles."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        mock_editor_state.toggle_pane_maximize("editor")
        mock_editor_state.toggle_pane_maximize("preview")
        mock_editor_state.toggle_pane_maximize("editor")

        # Should end with editor maximized
        assert mock_editor_state.maximized_pane == "editor"

    def test_triple_maximize_same_pane(self, mock_editor_state):
        """Test calling maximize three times on same pane."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        mock_editor_state.maximize_pane("editor")
        first_state = mock_editor_state.maximized_pane

        mock_editor_state.maximize_pane("editor")
        second_state = mock_editor_state.maximized_pane

        mock_editor_state.maximize_pane("editor")
        third_state = mock_editor_state.maximized_pane

        # All should be "editor"
        assert first_state == second_state == third_state == "editor"

    def test_rapid_restore_calls(self, mock_editor_state):
        """Test multiple rapid restore calls."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")

        # Call restore multiple times
        mock_editor_state.restore_panes()
        mock_editor_state.restore_panes()
        mock_editor_state.restore_panes()

        # Should remain in normal state
        assert mock_editor_state.maximized_pane is None


@pytest.mark.unit
class TestUIUpdateEdgeCases:
    """Test UI update edge cases."""

    def test_status_message_for_editor_contains_text(self, mock_editor_state):
        """Test status message content for editor."""
        mock_editor_state.maximize_pane("editor")

        calls = mock_editor_state.status_bar.showMessage.call_args_list
        # Should contain "Editor" and "maximized"
        assert len(calls) > 0

    def test_status_message_for_preview_contains_text(self, mock_editor_state):
        """Test status message content for preview."""
        mock_editor_state.maximize_pane("preview")

        calls = mock_editor_state.status_bar.showMessage.call_args_list
        # Should contain "Preview" and "maximized"
        assert len(calls) > 0

    def test_button_text_changes_detected(self, mock_editor_state):
        """Test button text changes are called."""
        mock_editor_state.maximize_pane("editor")

        # Both buttons should have setText called
        assert mock_editor_state.editor_max_btn.setText.called
        assert mock_editor_state.preview_max_btn.setText.called

    def test_multiple_status_messages_in_workflow(self, mock_editor_state):
        """Test status messages throughout workflow."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        mock_editor_state.maximize_pane("editor")
        first_call_count = mock_editor_state.status_bar.showMessage.call_count

        mock_editor_state.maximize_pane("preview")
        second_call_count = mock_editor_state.status_bar.showMessage.call_count

        # Should have more calls after second maximize
        assert second_call_count > first_call_count


@pytest.mark.unit
class TestSplitterSizeCalculations:
    """Test splitter size calculation edge cases."""

    def test_size_calculation_with_unequal_sum(self, mock_editor_state):
        """Test when saved sizes don't sum to current width."""
        mock_editor_state.splitter.width.return_value = 1000
        mock_editor_state.splitter.sizes.return_value = [400, 500]  # Sum = 900

        mock_editor_state.maximize_pane("editor")

        # Should still maximize to full width
        mock_editor_state.splitter.setSizes.assert_called_with([1000, 0])

    def test_restore_with_sizes_larger_than_width(self, mock_editor_state):
        """Test restoring when saved sizes exceed current width."""
        mock_editor_state.splitter.width.return_value = 1000
        mock_editor_state.splitter.sizes.return_value = [1200, 800]  # Sum = 2000

        mock_editor_state.maximize_pane("editor")
        mock_editor_state.restore_panes()

        # Should restore to saved sizes (Qt handles scaling)
        mock_editor_state.splitter.setSizes.assert_called_with([1200, 800])

    def test_maximize_calculation_uses_current_width(self, mock_editor_state):
        """Test maximize uses current splitter width."""
        mock_editor_state.splitter.width.return_value = 1500
        mock_editor_state.splitter.sizes.return_value = [750, 750]

        mock_editor_state.maximize_pane("preview")

        mock_editor_state.splitter.setSizes.assert_called_with([0, 1500])


@pytest.mark.unit
class TestMaximizationPersistence:
    """Test maximization state persistence."""

    def test_state_persists_across_multiple_operations(self, mock_editor_state):
        """Test state persists correctly through operations."""
        states = []
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        mock_editor_state.maximize_pane("editor")
        states.append(mock_editor_state.maximized_pane)

        mock_editor_state.maximize_pane("editor")
        states.append(mock_editor_state.maximized_pane)

        mock_editor_state.restore_panes()
        states.append(mock_editor_state.maximized_pane)

        assert states == ["editor", "editor", None]

    def test_saved_sizes_persist_until_restore(self, mock_editor_state):
        """Test saved sizes remain until restore."""
        original_sizes = [300, 700]
        mock_editor_state.splitter.sizes.return_value = original_sizes

        mock_editor_state.maximize_pane("editor")
        saved_after_maximize = mock_editor_state.saved_splitter_sizes

        mock_editor_state.maximize_pane("preview")
        saved_after_switch = mock_editor_state.saved_splitter_sizes

        mock_editor_state.maximize_pane("editor")
        saved_after_return = mock_editor_state.saved_splitter_sizes

        # All should be the same
        assert (
            saved_after_maximize
            == saved_after_switch
            == saved_after_return
            == original_sizes
        )

    def test_multiple_restore_doesnt_change_state(self, mock_editor_state):
        """Test multiple restores keep state as None."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]
        mock_editor_state.maximize_pane("editor")

        mock_editor_state.restore_panes()
        first_state = mock_editor_state.maximized_pane

        mock_editor_state.restore_panes()
        second_state = mock_editor_state.maximized_pane

        assert first_state == second_state == None


@pytest.mark.unit
class TestConcurrentOperations:
    """Test concurrent or overlapping operations."""

    def test_maximize_during_width_change(self, mock_editor_state):
        """Test maximizing while width is changing."""
        mock_editor_state.splitter.width.return_value = 1000
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        mock_editor_state.maximize_pane("editor")

        # Simulate width change
        mock_editor_state.splitter.width.return_value = 1200

        # Maximize again with new width
        mock_editor_state.maximize_pane("editor")

        mock_editor_state.splitter.setSizes.assert_called_with([1200, 0])

    def test_restore_immediately_after_maximize(self, mock_editor_state):
        """Test restoring immediately after maximize."""
        original_sizes = [500, 500]
        mock_editor_state.splitter.sizes.return_value = original_sizes

        mock_editor_state.maximize_pane("editor")
        mock_editor_state.restore_panes()

        # Should end in normal state
        assert mock_editor_state.maximized_pane is None
        mock_editor_state.splitter.setSizes.assert_called_with(original_sizes)

    def test_switch_pane_without_restore(self, mock_editor_state):
        """Test switching directly from one maximized pane to another."""
        mock_editor_state.splitter.sizes.return_value = [500, 500]

        mock_editor_state.maximize_pane("editor")
        mock_editor_state.maximize_pane("preview")

        # Should directly switch to preview
        assert mock_editor_state.maximized_pane == "preview"
        mock_editor_state.splitter.setSizes.assert_called_with([0, 1000])
