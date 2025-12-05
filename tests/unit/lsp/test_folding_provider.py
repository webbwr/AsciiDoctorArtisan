"""
Tests for AsciiDoc LSP folding provider.

Tests cover:
- Section folding (headings)
- Block folding (delimited blocks)
- Comment folding (line and block comments)
"""

import pytest
from lsprotocol import types as lsp

from asciidoc_artisan.lsp.folding_provider import AsciiDocFoldingProvider


@pytest.fixture
def provider() -> AsciiDocFoldingProvider:
    """Create folding provider instance."""
    return AsciiDocFoldingProvider()


class TestSectionFolding:
    """Test folding for sections (headings)."""

    def test_single_section_fold(self, provider: AsciiDocFoldingProvider) -> None:
        """Test folding a single section."""
        text = """= Document Title

Some content here.

More content.
"""
        ranges = provider.get_folding_ranges(text)

        assert len(ranges) >= 1
        section_range = next((r for r in ranges if r.start_line == 0), None)
        assert section_range is not None
        assert section_range.kind == lsp.FoldingRangeKind.Region

    def test_nested_sections_fold(self, provider: AsciiDocFoldingProvider) -> None:
        """Test folding nested sections."""
        text = """= Title

== Section 1

Content 1.

== Section 2

Content 2.
"""
        ranges = provider.get_folding_ranges(text)

        # Should have folds for title and sections
        assert len(ranges) >= 2

    def test_section_ends_at_next_same_level(self, provider: AsciiDocFoldingProvider) -> None:
        """Test section fold ends at next same-level heading."""
        text = """== Section A

Content A.

== Section B

Content B.
"""
        ranges = provider.get_folding_ranges(text)

        # Find Section A fold
        section_a = next((r for r in ranges if r.start_line == 0), None)
        assert section_a is not None
        # Should end before Section B
        assert section_a.end_line < 4


class TestBlockFolding:
    """Test folding for delimited blocks."""

    def test_listing_block_fold(self, provider: AsciiDocFoldingProvider) -> None:
        """Test folding listing block (----)."""
        text = """----
code here
more code
----
"""
        ranges = provider.get_folding_ranges(text)

        block_range = next((r for r in ranges if r.start_line == 0), None)
        assert block_range is not None
        assert block_range.end_line == 3
        assert block_range.kind == lsp.FoldingRangeKind.Region

    def test_example_block_fold(self, provider: AsciiDocFoldingProvider) -> None:
        """Test folding example block (====)."""
        text = """====
Example content
====
"""
        ranges = provider.get_folding_ranges(text)

        block_range = next((r for r in ranges if r.start_line == 0), None)
        assert block_range is not None
        assert block_range.end_line == 2

    def test_sidebar_block_fold(self, provider: AsciiDocFoldingProvider) -> None:
        """Test folding sidebar block (****)."""
        text = """****
Sidebar content
****
"""
        ranges = provider.get_folding_ranges(text)

        block_range = next((r for r in ranges if r.start_line == 0), None)
        assert block_range is not None

    def test_quote_block_fold(self, provider: AsciiDocFoldingProvider) -> None:
        """Test folding quote block (____)."""
        text = """____
Quote text
____
"""
        ranges = provider.get_folding_ranges(text)

        block_range = next((r for r in ranges if r.start_line == 0), None)
        assert block_range is not None

    def test_comment_block_fold(self, provider: AsciiDocFoldingProvider) -> None:
        """Test folding comment block (////)."""
        text = """////
Hidden comment
////
"""
        ranges = provider.get_folding_ranges(text)

        block_range = next((r for r in ranges if r.start_line == 0), None)
        assert block_range is not None
        assert block_range.kind == lsp.FoldingRangeKind.Comment


class TestCommentLineFolding:
    """Test folding for consecutive comment lines."""

    def test_consecutive_comments_fold(self, provider: AsciiDocFoldingProvider) -> None:
        """Test folding consecutive comment lines."""
        text = """// Comment line 1
// Comment line 2
// Comment line 3

Regular text.
"""
        ranges = provider.get_folding_ranges(text)

        comment_range = next((r for r in ranges if r.kind == lsp.FoldingRangeKind.Comment), None)
        assert comment_range is not None
        assert comment_range.start_line == 0
        assert comment_range.end_line == 2

    def test_single_comment_no_fold(self, provider: AsciiDocFoldingProvider) -> None:
        """Test single comment line doesn't create fold."""
        text = """// Single comment

Regular text.
"""
        ranges = provider.get_folding_ranges(text)

        # Single comment shouldn't create a fold
        comment_ranges = [r for r in ranges if r.kind == lsp.FoldingRangeKind.Comment]
        assert len(comment_ranges) == 0

    def test_comments_at_end_of_file(self, provider: AsciiDocFoldingProvider) -> None:
        """Test comments at end of file are folded."""
        text = """Regular text.

// End comment 1
// End comment 2
"""
        ranges = provider.get_folding_ranges(text)

        comment_range = next((r for r in ranges if r.kind == lsp.FoldingRangeKind.Comment), None)
        assert comment_range is not None


class TestMixedContent:
    """Test folding with mixed content types."""

    def test_section_with_block(self, provider: AsciiDocFoldingProvider) -> None:
        """Test section containing a block."""
        text = """== Section

----
code
----

More content.
"""
        ranges = provider.get_folding_ranges(text)

        # Should have both section and block folds
        assert len(ranges) >= 2

    def test_empty_document(self, provider: AsciiDocFoldingProvider) -> None:
        """Test empty document returns no folds."""
        ranges = provider.get_folding_ranges("")

        assert len(ranges) == 0

    def test_short_delimiter_ignored(self, provider: AsciiDocFoldingProvider) -> None:
        """Test delimiters less than 4 chars are ignored."""
        text = """---
not a block
---
"""
        ranges = provider.get_folding_ranges(text)

        # 3-char delimiter shouldn't create fold
        block_ranges = [r for r in ranges if r.start_line == 0]
        assert len(block_ranges) == 0
