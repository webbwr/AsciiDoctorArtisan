"""
Tests for predictive rendering system.

Tests prediction heuristics, priority scoring, and integration.
"""

import time

from asciidoc_artisan.workers.predictive_renderer import (
    PredictivePreviewRenderer,
    PredictiveRenderer,
)


def test_predictive_renderer_initialization():
    """Test predictive renderer initializes correctly."""
    renderer = PredictiveRenderer()

    assert renderer.max_predictions == 5
    assert len(renderer._recent_edits) == 0
    assert renderer._current_cursor_line == 0


def test_cursor_position_update():
    """Test cursor position tracking."""
    renderer = PredictiveRenderer()

    renderer.update_cursor_position(42)
    assert renderer._current_cursor_line == 42
    assert renderer._last_cursor_update > 0


def test_edit_recording():
    """Test edit history recording."""
    renderer = PredictiveRenderer()

    renderer.record_edit(0)
    renderer.record_edit(1)
    renderer.record_edit(2)

    assert list(renderer._recent_edits) == [0, 1, 2]
    assert len(renderer._edit_timestamps) == 3


def test_sequential_edit_detection():
    """Test sequential editing pattern detection."""
    renderer = PredictiveRenderer()

    # Edit blocks sequentially
    renderer.record_edit(5)
    assert renderer._sequential_edits == 0

    renderer.record_edit(6)
    assert renderer._sequential_edits == 1

    renderer.record_edit(7)
    assert renderer._sequential_edits == 2

    # Break sequence
    renderer.record_edit(10)
    assert renderer._sequential_edits == 0


def test_predict_current_block():
    """Test prediction includes current block."""
    renderer = PredictiveRenderer()

    prediction = renderer.predict_next_blocks(total_blocks=10, current_block_index=5)

    assert 5 in prediction.block_indices
    assert prediction.confidence > 0


def test_predict_adjacent_blocks():
    """Test prediction includes adjacent blocks."""
    renderer = PredictiveRenderer()

    prediction = renderer.predict_next_blocks(total_blocks=10, current_block_index=5)

    # Should predict blocks around cursor
    assert 4 in prediction.block_indices  # Before
    assert 5 in prediction.block_indices  # Current
    assert 6 in prediction.block_indices  # After


def test_predict_with_edit_history():
    """Test prediction uses edit history."""
    renderer = PredictiveRenderer()

    # Record some edits
    renderer.record_edit(3)
    renderer.record_edit(7)
    renderer.record_edit(9)

    prediction = renderer.predict_next_blocks(total_blocks=10, current_block_index=5)

    # Should include recently edited blocks
    assert (
        3 in prediction.block_indices
        or 7 in prediction.block_indices
        or 9 in prediction.block_indices
    )


def test_predict_sequential_pattern():
    """Test prediction for sequential editing."""
    renderer = PredictiveRenderer()

    # Establish sequential pattern
    renderer.record_edit(2)
    renderer.record_edit(3)
    renderer.record_edit(4)

    prediction = renderer.predict_next_blocks(total_blocks=10, current_block_index=4)

    # Should predict next block in sequence
    assert 5 in prediction.block_indices


def test_max_predictions_limit():
    """Test maximum predictions limit."""
    renderer = PredictiveRenderer(max_predictions=3)

    prediction = renderer.predict_next_blocks(total_blocks=100, current_block_index=50)

    # Should respect max limit
    assert len(prediction.block_indices) <= 3


def test_priority_score_current_block():
    """Test priority scoring for current block."""
    renderer = PredictiveRenderer()

    score = renderer.get_priority_score(block_index=5, current_block=5)

    # Current block should have highest priority
    assert score >= 0.5


def test_priority_score_distance():
    """Test priority scoring decreases with distance."""
    renderer = PredictiveRenderer()

    score_current = renderer.get_priority_score(block_index=5, current_block=5)
    score_adjacent = renderer.get_priority_score(block_index=6, current_block=5)
    score_far = renderer.get_priority_score(block_index=20, current_block=5)

    # Priority should decrease with distance
    assert score_current > score_adjacent
    assert score_adjacent > score_far


def test_priority_score_recent_edits():
    """Test priority scoring for recently edited blocks."""
    renderer = PredictiveRenderer()

    # Record edit
    renderer.record_edit(10)

    score_edited = renderer.get_priority_score(block_index=10, current_block=5)
    score_not_edited = renderer.get_priority_score(block_index=15, current_block=5)

    # Recently edited should have higher priority
    assert score_edited > score_not_edited


def test_priority_score_sequential_bonus():
    """Test priority bonus for sequential editing."""
    renderer = PredictiveRenderer()

    # Establish sequential pattern
    renderer.record_edit(5)
    renderer.record_edit(6)
    renderer.record_edit(7)

    # Next in sequence should have bonus
    score_next = renderer.get_priority_score(block_index=8, current_block=7)
    score_other = renderer.get_priority_score(block_index=10, current_block=7)

    assert score_next > score_other


def test_prediction_statistics():
    """Test prediction statistics tracking."""
    renderer = PredictiveRenderer()

    # Make some predictions
    renderer.predict_next_blocks(total_blocks=10, current_block_index=5)
    renderer.predict_next_blocks(total_blocks=10, current_block_index=6)

    # Record some uses
    renderer.record_prediction_used(5)

    stats = renderer.get_statistics()

    assert stats["predictions_made"] == 2
    assert stats["predictions_used"] == 1
    assert stats["hit_rate"] == 0.5


def test_reset_statistics():
    """Test resetting statistics."""
    renderer = PredictiveRenderer()

    renderer.predict_next_blocks(total_blocks=10, current_block_index=5)
    renderer.record_prediction_used(5)

    renderer.reset_statistics()

    stats = renderer.get_statistics()
    assert stats["predictions_made"] == 0
    assert stats["predictions_used"] == 0


def test_predictive_preview_renderer_initialization():
    """Test predictive preview renderer initialization."""
    from unittest.mock import Mock

    mock_incremental = Mock()
    renderer = PredictivePreviewRenderer(mock_incremental)

    assert renderer.incremental_renderer is mock_incremental
    assert renderer.predictor is not None
    assert renderer.is_enabled() is True


def test_predictive_preview_enable_disable():
    """Test enabling/disabling predictive rendering."""
    from unittest.mock import Mock

    mock_incremental = Mock()
    renderer = PredictivePreviewRenderer(mock_incremental)

    renderer.enable(False)
    assert not renderer.is_enabled()

    renderer.enable(True)
    assert renderer.is_enabled()


def test_request_prediction_queues_blocks():
    """Test prediction request queues blocks."""
    from unittest.mock import Mock

    mock_incremental = Mock()
    renderer = PredictivePreviewRenderer(mock_incremental)

    renderer.request_prediction(total_blocks=10, current_block=5)

    # Should have blocks in queue
    assert len(renderer._prerender_queue) > 0


def test_prerender_queue_prioritized():
    """Test pre-render queue is prioritized."""
    from unittest.mock import Mock

    mock_incremental = Mock()
    renderer = PredictivePreviewRenderer(mock_incremental)

    # Record edit pattern
    renderer.predictor.record_edit(5)
    renderer.predictor.record_edit(6)

    renderer.request_prediction(total_blocks=10, current_block=6)

    # Queue should be sorted by priority
    if len(renderer._prerender_queue) >= 2:
        first_priority = renderer._prerender_queue[0][1]
        second_priority = renderer._prerender_queue[1][1]
        assert first_priority >= second_priority


def test_get_next_prerender_block():
    """Test getting next block from queue."""
    from unittest.mock import Mock

    mock_incremental = Mock()
    renderer = PredictivePreviewRenderer(mock_incremental)

    renderer.request_prediction(total_blocks=10, current_block=5)

    # Should return block index
    block_idx = renderer.get_next_prerender_block()
    assert block_idx is not None
    assert isinstance(block_idx, int)


def test_get_next_prerender_empty_queue():
    """Test getting from empty queue returns None."""
    from unittest.mock import Mock

    mock_incremental = Mock()
    renderer = PredictivePreviewRenderer(mock_incremental)

    # Empty queue
    block_idx = renderer.get_next_prerender_block()
    assert block_idx is None


def test_predictive_statistics():
    """Test predictive preview renderer statistics."""
    from unittest.mock import Mock

    mock_incremental = Mock()
    renderer = PredictivePreviewRenderer(mock_incremental)

    renderer.request_prediction(total_blocks=10, current_block=5)

    stats = renderer.get_statistics()

    assert "predictions_made" in stats
    assert "prerender_queue_size" in stats
    assert stats["prerender_queue_size"] > 0


def test_temporal_locality_prediction():
    """Test temporal locality heuristic."""
    renderer = PredictiveRenderer()

    # Record recent edit
    renderer.record_edit(10)

    # Small time delay (simulate immediate follow-up edit)
    time.sleep(0.01)

    prediction = renderer.predict_next_blocks(total_blocks=20, current_block_index=10)

    # Should predict blocks near recent edit
    nearby_blocks = [8, 9, 10, 11, 12]
    predicted = set(prediction.block_indices)

    # At least some nearby blocks should be predicted
    assert any(block in predicted for block in nearby_blocks)


def test_prediction_boundary_handling():
    """Test prediction handles document boundaries."""
    renderer = PredictiveRenderer()

    # Test at beginning of document
    prediction_start = renderer.predict_next_blocks(
        total_blocks=10, current_block_index=0
    )
    assert all(0 <= idx < 10 for idx in prediction_start.block_indices)

    # Test at end of document
    prediction_end = renderer.predict_next_blocks(
        total_blocks=10, current_block_index=9
    )
    assert all(0 <= idx < 10 for idx in prediction_end.block_indices)


def test_edit_history_limit():
    """Test edit history respects maxlen."""
    renderer = PredictiveRenderer()

    # Record more edits than maxlen (10)
    for i in range(20):
        renderer.record_edit(i)

    # Should only keep last 10
    assert len(renderer._recent_edits) == 10
    assert len(renderer._edit_timestamps) == 10
