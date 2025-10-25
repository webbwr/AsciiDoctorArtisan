"""
Incremental Preview Renderer - Optimized rendering with block-based caching.

This module provides incremental rendering for AsciiDoc documents:
- Block-based caching: Only re-render changed sections
- Diff-based updates: Detect what changed in the document
- Partial rendering: Render only modified blocks
- Cache management: LRU cache for rendered blocks

Implements Phase 3.1 of Performance Optimization Plan:
- Incremental rendering for large documents
- 3-5x faster preview updates
- Reduced CPU usage for minor edits

Block Structure:
    Documents are split into blocks at section boundaries:
    - Level 0 heading (= Title)
    - Level 1 heading (== Section)
    - Level 2 heading (=== Subsection)
    - Paragraphs between headings
"""

import hashlib
import logging
import re
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Cache settings
MAX_CACHE_SIZE = 100  # Max blocks in cache
BLOCK_HASH_LENGTH = 16  # Hash length for block IDs


@dataclass
class DocumentBlock:
    """
    A section of the AsciiDoc document.

    Attributes:
        id: Unique ID (hash of content)
        start_line: Starting line number
        end_line: Ending line number
        content: Raw AsciiDoc content
        rendered_html: Cached rendered HTML
        level: Heading level (0=title, 1=section, etc.)
    """
    id: str
    start_line: int
    end_line: int
    content: str
    rendered_html: Optional[str] = None
    level: int = 0

    def compute_id(self) -> str:
        """Compute hash ID from content."""
        content_hash = hashlib.md5(self.content.encode('utf-8')).hexdigest()
        return content_hash[:BLOCK_HASH_LENGTH]


class BlockCache:
    """
    LRU cache for rendered blocks.

    Stores rendered HTML for document blocks with automatic eviction
    when cache size exceeds MAX_CACHE_SIZE.
    """

    def __init__(self, max_size: int = MAX_CACHE_SIZE):
        """
        Initialize block cache.

        Args:
            max_size: Maximum number of blocks to cache
        """
        self.max_size = max_size
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, block_id: str) -> Optional[str]:
        """
        Get rendered HTML from cache.

        Args:
            block_id: Block ID to retrieve

        Returns:
            Rendered HTML if cached, None otherwise
        """
        if block_id in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(block_id)
            self._hits += 1
            return self._cache[block_id]

        self._misses += 1
        return None

    def put(self, block_id: str, html: str) -> None:
        """
        Store rendered HTML in cache.

        Args:
            block_id: Block ID
            html: Rendered HTML
        """
        # Remove if already exists (will re-add at end)
        if block_id in self._cache:
            del self._cache[block_id]

        # Add to end (most recently used)
        self._cache[block_id] = html

        # Evict oldest if over size limit
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        """Clear all cached blocks."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with size, hits, misses, hit_rate
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        return {
            'size': len(self._cache),
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': round(hit_rate, 2)
        }


class DocumentBlockSplitter:
    """
    Split AsciiDoc document into blocks for incremental rendering.

    Splits on:
    - Document title (= Title)
    - Section headings (== Section)
    - Subsection headings (=== Subsection)
    - Paragraph breaks
    """

    # Regex patterns for block boundaries
    TITLE_PATTERN = re.compile(r'^=\s+\S+', re.MULTILINE)
    SECTION_PATTERN = re.compile(r'^==\s+\S+', re.MULTILINE)
    SUBSECTION_PATTERN = re.compile(r'^===\s+\S+', re.MULTILINE)
    HEADING_PATTERN = re.compile(r'^(={1,6})\s+(.+)$', re.MULTILINE)

    @staticmethod
    def split(source_text: str) -> List[DocumentBlock]:
        """
        Split document into blocks.

        Args:
            source_text: Full AsciiDoc source

        Returns:
            List of DocumentBlock objects
        """
        if not source_text.strip():
            return []

        lines = source_text.split('\n')
        blocks: List[DocumentBlock] = []
        current_block_lines: List[str] = []
        current_level = 0
        block_start_line = 0

        for line_num, line in enumerate(lines):
            # Check if this is a heading
            heading_match = DocumentBlockSplitter.HEADING_PATTERN.match(line)

            if heading_match:
                # Save previous block if exists
                if current_block_lines:
                    block = DocumentBlockSplitter._create_block(
                        current_block_lines,
                        block_start_line,
                        line_num - 1,
                        current_level
                    )
                    blocks.append(block)

                # Start new block
                current_level = len(heading_match.group(1))
                current_block_lines = [line]
                block_start_line = line_num
            else:
                current_block_lines.append(line)

        # Add final block
        if current_block_lines:
            block = DocumentBlockSplitter._create_block(
                current_block_lines,
                block_start_line,
                len(lines) - 1,
                current_level
            )
            blocks.append(block)

        logger.debug(f"Split document into {len(blocks)} blocks")
        return blocks

    @staticmethod
    def _create_block(
        lines: List[str],
        start_line: int,
        end_line: int,
        level: int
    ) -> DocumentBlock:
        """Create DocumentBlock from lines."""
        content = '\n'.join(lines)
        block = DocumentBlock(
            id='',
            start_line=start_line,
            end_line=end_line,
            content=content,
            level=level
        )
        block.id = block.compute_id()
        return block


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

    def __init__(self, asciidoc_api):
        """
        Initialize incremental renderer.

        Args:
            asciidoc_api: AsciiDoc3API instance for rendering
        """
        self.asciidoc_api = asciidoc_api
        self.cache = BlockCache(max_size=MAX_CACHE_SIZE)
        self.previous_blocks: List[DocumentBlock] = []
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
        changed_blocks, unchanged_blocks = self._detect_changes(
            self.previous_blocks,
            current_blocks
        )

        logger.debug(
            f"Incremental render: {len(changed_blocks)} changed, "
            f"{len(unchanged_blocks)} cached"
        )

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

        # Update previous blocks
        self.previous_blocks = current_blocks

        # Assemble final HTML
        html_parts = [block.rendered_html for block in current_blocks
                     if block.rendered_html]
        return '\n'.join(html_parts)

    def _detect_changes(
        self,
        previous: List[DocumentBlock],
        current: List[DocumentBlock]
    ) -> Tuple[List[DocumentBlock], List[DocumentBlock]]:
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
            self.asciidoc_api.execute(infile, outfile, backend='html5')
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
            self.asciidoc_api.execute(infile, outfile, backend='html5')
            return outfile.getvalue()

        except Exception as exc:
            logger.error(f"Full render failed: {exc}")
            return f"<pre>{html.escape(source_text)}</pre>"

    def get_cache_stats(self) -> Dict[str, int]:
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
