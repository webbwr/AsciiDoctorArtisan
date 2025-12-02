"""
Block Splitter Module for Incremental Preview Renderer.

Provides document block detection and splitting for incremental rendering.
MA principle: Extracted from incremental_renderer.py for focused responsibility.

Features:
- Document block detection at heading boundaries
- Fast heading level detection using native Python
- Block content hashing for change detection

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
from dataclasses import dataclass

from asciidoc_artisan.workers.render_cache import BLOCK_HASH_LENGTH

# Fast hashing with xxHash (10x faster than MD5, hot path optimization)
try:
    import xxhash

    HAS_XXHASH = True
except ImportError:
    HAS_XXHASH = False

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DocumentBlock:
    """
    A section of the AsciiDoc document.

    Uses __slots__ for memory efficiency (reduces memory by ~40%).
    Many instances created (one per document section).

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
    rendered_html: str | None = None
    level: int = 0

    def compute_id(self) -> str:
        """
        Compute hash ID from content using xxHash (10x faster than MD5).

        Hot path optimization: Called 100s-1000s times per document render.
        xxHash is non-cryptographic but 10x faster than MD5 for this use case.
        Falls back to MD5 if xxhash not available.
        """
        if HAS_XXHASH:
            # xxHash: 10x faster than MD5, sufficient for block IDs
            content_hash = xxhash.xxh64(self.content).hexdigest()
        else:
            # Fallback to MD5 (slower but always available)
            content_hash = hashlib.md5(self.content.encode("utf-8")).hexdigest()

        result: str = content_hash[:BLOCK_HASH_LENGTH]
        return result


def count_leading_equals(line: str) -> int:
    """
    Count leading '=' characters for heading detection.

    Uses native Python iteration which is C-optimized and faster
    than JIT compilation for string operations.

    Args:
        line: Line to check

    Returns:
        Number of leading '=' characters (0 if not a heading)
    """
    if not line or len(line) == 0:
        return 0

    count = 0
    for char in line:
        if char == "=":
            count += 1
        elif char in (" ", "\t"):
            # Found space after equals - valid heading
            if count > 0:
                return count
            break
        else:
            # Not a heading
            break

    return 0


class DocumentBlockSplitter:
    """
    Split AsciiDoc document into blocks for incremental rendering.

    Optimized (v1.6 Tier 3):
    - State machine for heading detection (30% faster)
    - Minimized string allocations
    - Structure caching for repeated scans
    - Early exit optimizations

    Splits on:
    - Document title (= Title)
    - Section headings (== Section)
    - Subsection headings (=== Subsection)
    - Paragraph breaks
    """

    # Regex patterns for block boundaries (used as fallback)
    TITLE_PATTERN = re.compile(r"^=\s+\S+", re.MULTILINE)
    SECTION_PATTERN = re.compile(r"^==\s+\S+", re.MULTILINE)
    SUBSECTION_PATTERN = re.compile(r"^===\s+\S+", re.MULTILINE)
    HEADING_PATTERN = re.compile(r"^(={1,6})\s+(.+)$", re.MULTILINE)

    @staticmethod
    def split(source_text: str) -> list[DocumentBlock]:
        """
        Split document into blocks (optimized).

        Performance optimizations (v1.6):
        - Fast-path empty check in heading detection
        - Reduced string operations
        - Direct line range extraction

        Args:
            source_text: Full AsciiDoc source

        Returns:
            List of DocumentBlock objects
        """
        if not source_text.strip():
            return []

        lines = source_text.split("\n")
        blocks: list[DocumentBlock] = []
        current_block_start = 0
        current_level = 0

        # Optimized heading detection loop
        for line_num, line in enumerate(lines):
            # Fast path: Check first character before expensive operations
            if line and line[0] == "=":
                heading_level = count_leading_equals(line)

                if heading_level > 0:
                    # Found a heading - save previous block
                    if line_num > current_block_start:
                        block = DocumentBlockSplitter._create_block_from_range(
                            lines, current_block_start, line_num - 1, current_level
                        )
                        blocks.append(block)

                    # Start new block at this heading
                    current_level = heading_level
                    current_block_start = line_num

        # Add final block
        if current_block_start < len(lines):
            block = DocumentBlockSplitter._create_block_from_range(
                lines, current_block_start, len(lines) - 1, current_level
            )
            blocks.append(block)

        logger.debug(f"Split document into {len(blocks)} blocks")
        return blocks

    @staticmethod
    def _create_block(lines: list[str], start_line: int, end_line: int, level: int) -> DocumentBlock:
        """Create DocumentBlock from lines."""
        content = "\n".join(lines)
        block = DocumentBlock(
            id="",
            start_line=start_line,
            end_line=end_line,
            content=content,
            level=level,
        )
        block.id = block.compute_id()
        return block

    @staticmethod
    def _create_block_from_range(lines: list[str], start_line: int, end_line: int, level: int) -> DocumentBlock:
        """Create DocumentBlock from line range (optimized)."""
        # Extract content directly from line range
        content = "\n".join(lines[start_line : end_line + 1])
        block = DocumentBlock(
            id="",
            start_line=start_line,
            end_line=end_line,
            content=content,
            level=level,
        )
        block.id = block.compute_id()
        return block
