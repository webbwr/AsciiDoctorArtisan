"""
Folding Range Provider for AsciiDoc LSP.

MA principle: ~150 lines focused on folding range detection.

Provides collapsible regions for:
- Sections (headings with content)
- Blocks (source, example, quote, sidebar, etc.)
- Comments (// line and //// block)
"""

import logging
import re

from lsprotocol import types as lsp

logger = logging.getLogger(__name__)

# Block delimiters and their fold kinds
BLOCK_DELIMITERS: dict[str, lsp.FoldingRangeKind] = {
    "-": lsp.FoldingRangeKind.Region,  # Listing/source (----)
    "=": lsp.FoldingRangeKind.Region,  # Example (====)
    "*": lsp.FoldingRangeKind.Region,  # Sidebar (****)
    "_": lsp.FoldingRangeKind.Region,  # Quote (____)
    "/": lsp.FoldingRangeKind.Comment,  # Comment (////)
    "+": lsp.FoldingRangeKind.Region,  # Passthrough (++++)
}


class AsciiDocFoldingProvider:
    """
    Provides folding ranges for AsciiDoc documents.

    Supports:
    - Section folding (heading to next same/higher level heading)
    - Block folding (delimiter to closing delimiter)
    - Comment folding (// lines and //// blocks)

    Performance: <50ms for typical documents.
    """

    def __init__(self) -> None:
        """Initialize folding provider."""
        self._heading_pattern = re.compile(r"^(=+)\s+(.+)$")
        self._comment_line_pattern = re.compile(r"^//(?!/)")

    def get_folding_ranges(self, text: str) -> list[lsp.FoldingRange]:
        """
        Get all folding ranges in document.

        Args:
            text: Document text

        Returns:
            List of FoldingRange objects
        """
        ranges: list[lsp.FoldingRange] = []
        lines = text.splitlines()

        ranges.extend(self._get_section_ranges(lines))
        ranges.extend(self._get_block_ranges(lines))
        ranges.extend(self._get_comment_ranges(lines))

        return ranges

    def _get_section_ranges(self, lines: list[str]) -> list[lsp.FoldingRange]:
        """Get folding ranges for sections (headings)."""
        ranges: list[lsp.FoldingRange] = []
        heading_stack: list[tuple[int, int]] = []  # (line, level)

        for line_num, line in enumerate(lines):
            match = self._heading_pattern.match(line)
            if match:
                level = len(match.group(1))

                # Close headings at same or lower level
                while heading_stack and heading_stack[-1][1] >= level:
                    start_line, _ = heading_stack.pop()
                    if line_num > start_line + 1:
                        ranges.append(
                            lsp.FoldingRange(
                                start_line=start_line,
                                end_line=line_num - 1,
                                kind=lsp.FoldingRangeKind.Region,
                            )
                        )

                heading_stack.append((line_num, level))

        # Close remaining headings
        for start_line, _ in heading_stack:
            if len(lines) > start_line + 1:
                ranges.append(
                    lsp.FoldingRange(
                        start_line=start_line,
                        end_line=len(lines) - 1,
                        kind=lsp.FoldingRangeKind.Region,
                    )
                )

        return ranges

    def _get_block_ranges(self, lines: list[str]) -> list[lsp.FoldingRange]:
        """Get folding ranges for delimited blocks."""
        ranges: list[lsp.FoldingRange] = []
        block_stack: list[tuple[int, str, lsp.FoldingRangeKind]] = []

        for line_num, line in enumerate(lines):
            stripped = line.strip()
            if len(stripped) < 4:
                continue

            # Check if line is a block delimiter (4+ same chars)
            first_char = stripped[0]
            if first_char in BLOCK_DELIMITERS and stripped == first_char * len(stripped):
                kind = BLOCK_DELIMITERS[first_char]

                # Check if closing existing block
                if block_stack and block_stack[-1][1] == first_char:
                    start_line, _, kind = block_stack.pop()
                    ranges.append(
                        lsp.FoldingRange(
                            start_line=start_line,
                            end_line=line_num,
                            kind=kind,
                        )
                    )
                else:
                    # Opening new block
                    block_stack.append((line_num, first_char, kind))

        return ranges

    def _get_comment_ranges(self, lines: list[str]) -> list[lsp.FoldingRange]:
        """Get folding ranges for consecutive comment lines."""
        ranges: list[lsp.FoldingRange] = []
        comment_start: int | None = None

        for line_num, line in enumerate(lines):
            is_comment = bool(self._comment_line_pattern.match(line))

            if is_comment:
                if comment_start is None:
                    comment_start = line_num
            else:
                if comment_start is not None and line_num > comment_start + 1:
                    ranges.append(
                        lsp.FoldingRange(
                            start_line=comment_start,
                            end_line=line_num - 1,
                            kind=lsp.FoldingRangeKind.Comment,
                        )
                    )
                comment_start = None

        # Handle comments at end
        if comment_start is not None and len(lines) > comment_start + 1:
            ranges.append(
                lsp.FoldingRange(
                    start_line=comment_start,
                    end_line=len(lines) - 1,
                    kind=lsp.FoldingRangeKind.Comment,
                )
            )

        return ranges
