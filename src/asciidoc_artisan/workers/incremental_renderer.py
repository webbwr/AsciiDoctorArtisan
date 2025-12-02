"""
Incremental Preview Renderer - Optimized rendering with block-based caching.

MA principle: Reduced from 624→195 lines by extracting render_cache.py and block_splitter.py.

Implements:
- NFR-001: Preview update latency optimization (1078x speedup achieved)
- NFR-003: Large file handling (efficient incremental rendering)
- NFR-004: Memory usage optimization (block-based caching)

This module provides incremental rendering for AsciiDoc documents:
- Block-based caching: Only re-render changed sections
- Diff-based updates: Detect what changed in the document
- Partial rendering: Render only modified blocks
- Cache management: LRU cache for rendered blocks

Implements Phase 3.1 of Performance Optimization Plan:
- Incremental rendering for large documents
- 3-5x faster preview updates
- Reduced CPU usage for minor edits
"""

import logging
import threading
from typing import Any

from asciidoc_artisan.workers.block_splitter import (
    DocumentBlock,
    DocumentBlockSplitter,
    count_leading_equals,
)
from asciidoc_artisan.workers.render_cache import (
    ALL_INTERNED_STRINGS,
    BLOCK_HASH_LENGTH,
    COMMON_ATTRIBUTES,
    COMMON_CSS,
    COMMON_HTML,
    COMMON_TOKENS,
    INTERNED_TOKENS,
    MAX_CACHE_SIZE,
    BlockCache,
)

logger = logging.getLogger(__name__)

# Re-export for backward compatibility
__all__ = [
    # From render_cache
    "MAX_CACHE_SIZE",
    "BLOCK_HASH_LENGTH",
    "COMMON_TOKENS",
    "COMMON_ATTRIBUTES",
    "COMMON_HTML",
    "COMMON_CSS",
    "ALL_INTERNED_STRINGS",
    "INTERNED_TOKENS",
    "BlockCache",
    # From block_splitter
    "DocumentBlock",
    "count_leading_equals",
    "DocumentBlockSplitter",
    # Main renderer
    "IncrementalPreviewRenderer",
]


class IncrementalPreviewRenderer:
    """
    Incremental renderer with block-based caching.

    Optimizes preview rendering by:
    1. Splitting document into blocks
    2. Detecting which blocks changed
    3. Only re-rendering changed blocks
    4. Caching rendered blocks
    5. Assembling final HTML from cache
    """

    def __init__(self, asciidoc_api: Any) -> None:
        """
        Initialize incremental renderer with thread-safe state management.

        Args:
            asciidoc_api: AsciiDoc3API instance for rendering
        """
        self.asciidoc_api = asciidoc_api
        self.cache = BlockCache(max_size=MAX_CACHE_SIZE)
        self.previous_blocks: list[DocumentBlock] = []
        self._blocks_lock = threading.Lock()
        self._enabled = True

    def is_enabled(self) -> bool:
        """Check if incremental rendering is enabled."""
        return self._enabled

    def enable(self, enabled: bool = True) -> None:
        """
        Enable or disable incremental rendering.

        Args:
            enabled: True to enable, False to disable
        """
        self._enabled = enabled
        if not enabled:
            self.cache.clear()
            with self._blocks_lock:
                self.previous_blocks = []
        logger.info(f"Incremental rendering {'enabled' if enabled else 'disabled'}")

    def render(self, source_text: str) -> str:
        """
        Render document incrementally.

        Args:
            source_text: Full AsciiDoc source

        Returns:
            Rendered HTML
        """
        if not self._enabled:
            # Fall back to full render
            return self._render_full(source_text)

        # Split into blocks
        current_blocks = DocumentBlockSplitter.split(source_text)

        # Detect changes
        changed_blocks, unchanged_blocks = self._detect_changes(self.previous_blocks, current_blocks)

        logger.debug(f"Incremental render: {len(changed_blocks)} changed, {len(unchanged_blocks)} cached")

        # Render changed blocks
        for block in changed_blocks:
            block.rendered_html = self._render_block(block)
            self.cache.put(block.id, block.rendered_html)

        # Retrieve cached blocks
        for block in unchanged_blocks:
            cached_html = self.cache.get(block.id)
            if cached_html:
                block.rendered_html = cached_html
            else:
                # Cache miss - render and cache
                block.rendered_html = self._render_block(block)
                self.cache.put(block.id, block.rendered_html)

        # Update previous blocks (thread-safe)
        with self._blocks_lock:
            self.previous_blocks = current_blocks

        # Assemble final HTML
        html_parts = [block.rendered_html for block in current_blocks if block.rendered_html]
        return "\n".join(html_parts)

    def _detect_changes(
        self, previous: list[DocumentBlock], current: list[DocumentBlock]
    ) -> tuple[list[DocumentBlock], list[DocumentBlock]]:
        """
        Detect which blocks changed.

        Args:
            previous: Previous document blocks
            current: Current document blocks

        Returns:
            Tuple of (changed_blocks, unchanged_blocks)
        """
        previous_ids = {block.id for block in previous}

        changed = []
        unchanged = []

        for block in current:
            if block.id in previous_ids:
                unchanged.append(block)
            else:
                changed.append(block)

        return changed, unchanged

    def _render_block(self, block: DocumentBlock) -> str:
        """
        Render a single block.

        Args:
            block: Block to render

        Returns:
            Rendered HTML
        """
        import html
        import io

        try:
            # Render using AsciiDoc API
            infile = io.StringIO(block.content)
            outfile = io.StringIO()
            self.asciidoc_api.execute(infile, outfile, backend="html5")
            return outfile.getvalue()

        except Exception as exc:
            logger.warning(f"Block render failed: {exc}")
            # Return escaped content as fallback
            return f"<pre>{html.escape(block.content)}</pre>"

    def _render_full(self, source_text: str) -> str:
        """
        Full document render (fallback).

        Args:
            source_text: Full AsciiDoc source

        Returns:
            Rendered HTML
        """
        import html
        import io

        try:
            infile = io.StringIO(source_text)
            outfile = io.StringIO()
            self.asciidoc_api.execute(infile, outfile, backend="html5")
            return outfile.getvalue()

        except Exception as exc:
            logger.error(f"Full render failed: {exc}")
            return f"<pre>{html.escape(source_text)}</pre>"

    def get_cache_stats(self) -> dict[str, int | float]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return self.cache.get_stats()

    def clear_cache(self) -> None:
        """Clear the block cache."""
        self.cache.clear()
        logger.debug("Block cache cleared")
