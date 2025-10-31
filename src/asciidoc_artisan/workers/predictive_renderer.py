"""
Predictive Renderer - Pre-render sections during idle time to reduce latency.

Implements v1.6.0 Task 3: Predictive Rendering
- Predicts which sections user will view/edit next
- Pre-renders during debounce periods
- Uses idle time for background rendering
- Heuristics based on cursor position and edit patterns

Expected Impact: 30-50% reduction in perceived latency
"""

import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class RenderPrediction:
    """
    Prediction for which blocks to pre-render.

    Attributes:
        block_indices: List of block indices to pre-render (in priority order)
        confidence: Confidence score (0.0-1.0) for this prediction
        reason: Human-readable reason for prediction (for debugging)
    """

    block_indices: List[int]
    confidence: float
    reason: str


class PredictiveRenderer:
    """
    Predictive rendering system for reducing perceived latency.

    Uses heuristics to predict which document sections the user will
    view/edit next and pre-renders them during idle time.

    Heuristics:
    1. Cursor Position: Pre-render blocks around current cursor position
    2. Edit History: Pre-render recently edited blocks
    3. Sequential Editing: If editing block N, likely to edit N+1 next
    4. View Context: Pre-render visible blocks in viewport

    Performance:
    - Reduces perceived latency by 30-50% (target)
    - Uses idle CPU time during debounce periods
    - No impact on UI responsiveness
    """

    def __init__(self, max_predictions: int = 5):
        """
        Initialize predictive renderer.

        Args:
            max_predictions: Maximum number of blocks to predict for pre-rendering
        """
        self.max_predictions = max_predictions

        # Edit history tracking
        self._recent_edits: Deque[int] = deque(maxlen=10)  # Recent block indices
        self._edit_timestamps: Deque[float] = deque(maxlen=10)

        # Cursor tracking
        self._current_cursor_line: int = 0
        self._last_cursor_update: float = 0.0

        # Sequential editing detection
        self._last_edited_block: Optional[int] = None
        self._sequential_edits: int = 0

        # Statistics
        self._predictions_made = 0
        self._predictions_used = 0

    def update_cursor_position(self, line_number: int) -> None:
        """
        Update current cursor position.

        Args:
            line_number: Current cursor line number (0-indexed)
        """
        self._current_cursor_line = line_number
        self._last_cursor_update = time.time()

    def record_edit(self, block_index: int) -> None:
        """
        Record that a block was edited.

        Args:
            block_index: Index of edited block
        """
        current_time = time.time()

        self._recent_edits.append(block_index)
        self._edit_timestamps.append(current_time)

        # Detect sequential editing pattern
        if self._last_edited_block is not None:
            if block_index == self._last_edited_block + 1:
                self._sequential_edits += 1
            else:
                self._sequential_edits = 0

        self._last_edited_block = block_index

    def predict_next_blocks(
        self, total_blocks: int, current_block_index: Optional[int] = None
    ) -> RenderPrediction:
        """
        Predict which blocks should be pre-rendered next.

        Uses multiple heuristics to predict user's next action:
        1. Current cursor position (highest priority)
        2. Recent edit history
        3. Sequential editing patterns
        4. Proximity to cursor

        Args:
            total_blocks: Total number of blocks in document
            current_block_index: Index of block containing cursor (if known)

        Returns:
            RenderPrediction with block indices to pre-render
        """
        self._predictions_made += 1

        predictions: Set[int] = set()
        reasons: List[str] = []

        # Heuristic 1: Blocks around cursor position
        if current_block_index is not None:
            predictions.add(current_block_index)
            reasons.append(f"cursor at block {current_block_index}")

            # Add adjacent blocks
            if current_block_index > 0:
                predictions.add(current_block_index - 1)
                reasons.append("block before cursor")

            if current_block_index < total_blocks - 1:
                predictions.add(current_block_index + 1)
                reasons.append("block after cursor")

        # Heuristic 2: Recently edited blocks
        if self._recent_edits:
            for block_idx in list(self._recent_edits)[-3:]:  # Last 3 edits
                if block_idx < total_blocks:
                    predictions.add(block_idx)
                    reasons.append(f"recent edit at {block_idx}")

        # Heuristic 3: Sequential editing prediction
        if self._sequential_edits >= 2 and self._last_edited_block is not None:
            next_block = self._last_edited_block + 1
            if next_block < total_blocks:
                predictions.add(next_block)
                reasons.append(f"sequential pattern predicts {next_block}")

        # Heuristic 4: Time-based proximity
        # If recently edited a block, likely to continue in that area
        if self._edit_timestamps:
            last_edit_time = self._edit_timestamps[-1]
            time_since_edit = time.time() - last_edit_time

            if time_since_edit < 2.0:  # Within 2 seconds
                last_edited = self._recent_edits[-1]
                # Add blocks in vicinity
                for offset in [-2, -1, 1, 2]:
                    nearby_block = last_edited + offset
                    if 0 <= nearby_block < total_blocks:
                        predictions.add(nearby_block)
                reasons.append("temporal locality")

        # Convert to sorted list (prioritize lower indices)
        block_indices = sorted(list(predictions))[: self.max_predictions]

        # Calculate confidence based on heuristics strength
        confidence = min(1.0, len(reasons) * 0.2)

        return RenderPrediction(
            block_indices=block_indices,
            confidence=confidence,
            reason=", ".join(reasons) if reasons else "no strong signals",
        )

    def record_prediction_used(self, block_index: int) -> None:
        """
        Record that a prediction was actually used (hit).

        Args:
            block_index: Block that was predicted and rendered
        """
        self._predictions_used += 1

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get predictive rendering statistics.

        Returns:
            Dictionary with prediction accuracy and usage stats
        """
        hit_rate = 0.0
        if self._predictions_made > 0:
            hit_rate = self._predictions_used / self._predictions_made

        return {
            "predictions_made": self._predictions_made,
            "predictions_used": self._predictions_used,
            "hit_rate": round(hit_rate, 3),
            "sequential_edits": self._sequential_edits,
            "recent_edits_count": len(self._recent_edits),
        }

    def reset_statistics(self) -> None:
        """Reset prediction statistics."""
        self._predictions_made = 0
        self._predictions_used = 0

    def get_priority_score(self, block_index: int, current_block: int) -> float:
        """
        Calculate priority score for pre-rendering a block.

        Higher score = higher priority for pre-rendering.

        Args:
            block_index: Index of block to score
            current_block: Index of block containing cursor

        Returns:
            Priority score (0.0-1.0)
        """
        score = 0.0

        # Distance from cursor (closer = higher priority)
        distance = abs(block_index - current_block)
        if distance == 0:
            score += 0.5  # Current block highest priority
        elif distance == 1:
            score += 0.3  # Adjacent blocks
        elif distance == 2:
            score += 0.1  # Nearby blocks
        else:
            score += max(0.0, 0.05 - distance * 0.01)  # Diminishing priority

        # Recent edit history (recently edited = higher priority)
        if block_index in self._recent_edits:
            # More recent edits get higher scores
            recent_list = list(self._recent_edits)
            if block_index in recent_list:
                recency_index = (
                    len(recent_list) - 1 - recent_list[::-1].index(block_index)
                )
                recency_score = 0.3 * (1.0 - recency_index / len(recent_list))
                score += recency_score

        # Sequential editing bonus
        if self._sequential_edits >= 2 and self._last_edited_block is not None:
            if block_index == self._last_edited_block + 1:
                score += 0.2  # Likely next in sequence

        return min(1.0, score)


class PredictivePreviewRenderer:
    """
    Integrates predictive rendering with incremental renderer.

    Manages pre-rendering queue and coordinates with main rendering pipeline.
    """

    def __init__(
        self, incremental_renderer: Any, predictor: Optional[PredictiveRenderer] = None
    ) -> None:
        """
        Initialize predictive preview renderer.

        Args:
            incremental_renderer: IncrementalPreviewRenderer instance
            predictor: Optional PredictiveRenderer instance
        """
        self.incremental_renderer = incremental_renderer
        self.predictor = predictor or PredictiveRenderer()

        # Pre-render queue (block indices waiting to be pre-rendered)
        self._prerender_queue: List[Tuple[int, float]] = []  # (block_idx, priority)

        # Enabled flag
        self._enabled = True

    def enable(self, enabled: bool = True) -> None:
        """
        Enable or disable predictive rendering.

        Args:
            enabled: True to enable, False to disable
        """
        self._enabled = enabled
        if not enabled:
            self._prerender_queue.clear()

        logger.info(f"Predictive rendering {'enabled' if enabled else 'disabled'}")

    def is_enabled(self) -> bool:
        """Check if predictive rendering is enabled."""
        return self._enabled

    def update_cursor_position(self, line_number: int) -> None:
        """Update cursor position for prediction."""
        if self._enabled:
            self.predictor.update_cursor_position(line_number)

    def request_prediction(self, total_blocks: int, current_block: int) -> None:
        """
        Request prediction and queue blocks for pre-rendering.

        Args:
            total_blocks: Total number of blocks in document
            current_block: Index of block containing cursor
        """
        if not self._enabled:
            return

        # Get prediction
        prediction = self.predictor.predict_next_blocks(total_blocks, current_block)

        # Queue blocks for pre-rendering with priorities
        self._prerender_queue.clear()
        for block_idx in prediction.block_indices:
            priority = self.predictor.get_priority_score(block_idx, current_block)
            self._prerender_queue.append((block_idx, priority))

        # Sort by priority (highest first)
        self._prerender_queue.sort(key=lambda x: x[1], reverse=True)

        logger.debug(
            f"Predicted {len(prediction.block_indices)} blocks to pre-render "
            f"(confidence: {prediction.confidence:.2f}, reason: {prediction.reason})"
        )

    def get_next_prerender_block(self) -> Optional[int]:
        """
        Get next block index to pre-render.

        Returns:
            Block index to pre-render, or None if queue empty
        """
        if self._prerender_queue:
            block_idx, priority = self._prerender_queue.pop(0)
            logger.debug(f"Pre-rendering block {block_idx} (priority: {priority:.3f})")
            return block_idx

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get predictive rendering statistics."""
        stats = self.predictor.get_statistics()
        stats["prerender_queue_size"] = len(self._prerender_queue)
        return stats
