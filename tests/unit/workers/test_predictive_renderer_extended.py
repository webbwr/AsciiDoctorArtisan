"""
Extended tests for predictive_renderer to achieve 100% coverage.

Tests for PredictivePreviewRenderer edge cases and disabled state.
"""

from unittest.mock import Mock

import pytest

from asciidoc_artisan.workers.predictive_renderer import (
    PredictivePreviewRenderer,
)


@pytest.mark.unit
class TestPredictivePreviewRendererCoverage:
    """Tests to achieve 100% coverage for PredictivePreviewRenderer."""

    def test_update_cursor_position_when_enabled(self):
        """Test update_cursor_position when predictive rendering enabled (lines 315-316)."""
        mock_incremental = Mock()
        renderer = PredictivePreviewRenderer(mock_incremental)

        # Enable predictive rendering
        renderer.enable(True)
        assert renderer.is_enabled() is True

        # Update cursor position - should call predictor.update_cursor_position
        renderer.update_cursor_position(42)

        # Verify predictor was updated (check last cursor position)
        assert renderer.predictor._current_cursor_line == 42

    def test_update_cursor_position_when_disabled(self):
        """Test update_cursor_position when predictive rendering disabled."""
        mock_incremental = Mock()
        renderer = PredictivePreviewRenderer(mock_incremental)

        # Disable predictive rendering
        renderer.enable(False)
        assert renderer.is_enabled() is False

        # Update cursor position - should do nothing
        renderer.update_cursor_position(42)

        # Predictor should not be updated (stays at default 0)
        assert renderer.predictor._current_cursor_line == 0

    def test_request_prediction_when_disabled(self):
        """Test request_prediction returns early when disabled (line 327)."""
        mock_incremental = Mock()
        renderer = PredictivePreviewRenderer(mock_incremental)

        # Disable predictive rendering
        renderer.enable(False)
        assert renderer.is_enabled() is False

        # Request prediction - should return early without queuing anything
        renderer.request_prediction(total_blocks=100, current_block=50)

        # Prerender queue should be empty
        assert len(renderer._prerender_queue) == 0

    def test_request_prediction_when_enabled(self):
        """Test request_prediction queues blocks when enabled."""
        mock_incremental = Mock()
        renderer = PredictivePreviewRenderer(mock_incremental)

        # Enable predictive rendering (already enabled by default)
        assert renderer.is_enabled() is True

        # Record some edits to establish pattern
        for i in range(10):
            renderer.predictor.record_edit(i)

        # Request prediction - should queue blocks
        renderer.request_prediction(total_blocks=100, current_block=5)

        # Prerender queue should have items (prediction happened)
        assert len(renderer._prerender_queue) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
