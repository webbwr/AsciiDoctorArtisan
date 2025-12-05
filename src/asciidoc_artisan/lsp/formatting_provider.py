"""
Document Formatting Provider for AsciiDoc LSP.

MA principle: ~150 lines focused on document formatting.

Provides formatting for AsciiDoc documents:
- Trailing whitespace removal
- Consistent blank lines between sections
- Block attribute spacing
"""

import logging
import re

from lsprotocol import types as lsp

logger = logging.getLogger(__name__)


class AsciiDocFormattingProvider:
    """
    Provides document formatting for AsciiDoc.

    Formatting rules:
    - Remove trailing whitespace
    - One blank line before headings (except at start)
    - No blank line after block attributes

    Performance: <100ms for typical documents.
    """

    def __init__(self) -> None:
        """Initialize formatting provider."""
        self._heading_pattern = re.compile(r"^(=+)\s+(.+)$")
        self._attribute_pattern = re.compile(r"^\[.+\]$")

    def format_document(
        self,
        text: str,
        options: lsp.FormattingOptions,
    ) -> list[lsp.TextEdit]:
        """
        Format entire document.

        Args:
            text: Document text
            options: Formatting options

        Returns:
            List of TextEdits to apply
        """
        lines = text.splitlines(keepends=True)
        edits: list[lsp.TextEdit] = []

        edits.extend(self._remove_trailing_whitespace(lines))
        edits.extend(self._normalize_heading_spacing(lines))
        edits.extend(self._normalize_block_spacing(lines))

        # Sort by position (descending) for safe application
        edits.sort(
            key=lambda e: (e.range.start.line, e.range.start.character),
            reverse=True,
        )

        return edits

    def _remove_trailing_whitespace(self, lines: list[str]) -> list[lsp.TextEdit]:
        """Remove trailing whitespace from all lines."""
        edits: list[lsp.TextEdit] = []

        for line_num, line in enumerate(lines):
            line_content = line.rstrip("\n\r")
            stripped = line_content.rstrip()

            if len(stripped) < len(line_content):
                edits.append(
                    lsp.TextEdit(
                        range=lsp.Range(
                            start=lsp.Position(line=line_num, character=len(stripped)),
                            end=lsp.Position(line=line_num, character=len(line_content)),
                        ),
                        new_text="",
                    )
                )

        return edits

    def _normalize_heading_spacing(self, lines: list[str]) -> list[lsp.TextEdit]:
        """Ensure one blank line before headings."""
        edits: list[lsp.TextEdit] = []

        for line_num, line in enumerate(lines):
            if line_num == 0:
                continue

            if self._heading_pattern.match(line.rstrip()):
                prev_line = lines[line_num - 1].rstrip() if line_num > 0 else ""

                if prev_line:  # Not already blank
                    edits.append(
                        lsp.TextEdit(
                            range=lsp.Range(
                                start=lsp.Position(line=line_num, character=0),
                                end=lsp.Position(line=line_num, character=0),
                            ),
                            new_text="\n",
                        )
                    )

        return edits

    def _normalize_block_spacing(self, lines: list[str]) -> list[lsp.TextEdit]:
        """Ensure block attributes not followed by blank line."""
        edits: list[lsp.TextEdit] = []

        for line_num, line in enumerate(lines):
            stripped = line.rstrip()

            if self._attribute_pattern.match(stripped):
                if line_num + 1 < len(lines):
                    next_line = lines[line_num + 1].rstrip()
                    if not next_line and line_num + 2 < len(lines):
                        edits.append(
                            lsp.TextEdit(
                                range=lsp.Range(
                                    start=lsp.Position(line=line_num + 1, character=0),
                                    end=lsp.Position(line=line_num + 2, character=0),
                                ),
                                new_text="",
                            )
                        )

        return edits

    def format_range(
        self,
        text: str,
        range_: lsp.Range,
        options: lsp.FormattingOptions,
    ) -> list[lsp.TextEdit]:
        """Format specific range (trailing whitespace only)."""
        lines = text.splitlines(keepends=True)
        edits: list[lsp.TextEdit] = []

        for line_num in range(range_.start.line, min(range_.end.line + 1, len(lines))):
            line = lines[line_num]
            line_content = line.rstrip("\n\r")
            stripped = line_content.rstrip()

            if len(stripped) < len(line_content):
                edits.append(
                    lsp.TextEdit(
                        range=lsp.Range(
                            start=lsp.Position(line=line_num, character=len(stripped)),
                            end=lsp.Position(line=line_num, character=len(line_content)),
                        ),
                        new_text="",
                    )
                )

        return edits
