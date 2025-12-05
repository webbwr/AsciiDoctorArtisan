"""
Tests for AsciiDoc LSP formatting provider.

Tests cover:
- Trailing whitespace removal
- Heading spacing normalization
- Block attribute spacing
- Range formatting
"""

import pytest
from lsprotocol import types as lsp

from asciidoc_artisan.lsp.formatting_provider import AsciiDocFormattingProvider


@pytest.fixture
def provider() -> AsciiDocFormattingProvider:
    """Create formatting provider instance."""
    return AsciiDocFormattingProvider()


@pytest.fixture
def default_options() -> lsp.FormattingOptions:
    """Default formatting options."""
    return lsp.FormattingOptions(tab_size=2, insert_spaces=True)


class TestTrailingWhitespace:
    """Test trailing whitespace removal."""

    def test_remove_trailing_spaces(
        self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions
    ) -> None:
        """Test removing trailing spaces."""
        text = "Line with spaces   \nAnother line  \n"

        edits = provider.format_document(text, default_options)

        # Should have edits to remove trailing spaces
        assert len(edits) >= 2
        for edit in edits:
            assert edit.new_text == ""

    def test_no_edit_for_clean_lines(
        self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions
    ) -> None:
        """Test no edits needed for clean lines."""
        text = "Clean line\nAnother clean line\n"

        edits = provider.format_document(text, default_options)

        # Filter to only trailing whitespace edits (empty new_text)
        whitespace_edits = [e for e in edits if e.new_text == ""]
        assert len(whitespace_edits) == 0

    def test_remove_trailing_tabs(
        self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions
    ) -> None:
        """Test removing trailing tabs."""
        text = "Line with tab\t\n"

        edits = provider.format_document(text, default_options)

        whitespace_edits = [e for e in edits if e.new_text == ""]
        assert len(whitespace_edits) >= 1


class TestHeadingSpacing:
    """Test heading spacing normalization."""

    def test_add_blank_before_heading(
        self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions
    ) -> None:
        """Test adding blank line before heading."""
        text = "Some content\n== Heading\n"

        edits = provider.format_document(text, default_options)

        # Should have edit to add blank line before heading
        newline_edits = [e for e in edits if e.new_text == "\n"]
        assert len(newline_edits) >= 1

    def test_no_blank_at_document_start(
        self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions
    ) -> None:
        """Test no blank line added at document start."""
        text = "= Document Title\n"

        edits = provider.format_document(text, default_options)

        # First line heading shouldn't get blank line before it
        newline_edits = [e for e in edits if e.new_text == "\n" and e.range.start.line == 0]
        assert len(newline_edits) == 0

    def test_existing_blank_preserved(
        self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions
    ) -> None:
        """Test existing blank line before heading is preserved."""
        text = "Content\n\n== Heading\n"

        edits = provider.format_document(text, default_options)

        # No newline edit needed - already has blank
        newline_edits = [e for e in edits if e.new_text == "\n"]
        assert len(newline_edits) == 0


class TestBlockSpacing:
    """Test block attribute spacing."""

    def test_remove_blank_after_block_attr(
        self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions
    ) -> None:
        """Test removing blank line after block attribute."""
        text = "[source,python]\n\ncode here\n"

        edits = provider.format_document(text, default_options)

        # Should have edit to remove blank after [source,python]
        # The edit replaces the blank line with empty string
        removal_edits = [e for e in edits if e.new_text == "" and e.range.start.line == 1]
        assert len(removal_edits) >= 1

    def test_no_removal_when_no_blank(
        self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions
    ) -> None:
        """Test no edit when block attr followed by content."""
        text = "[NOTE]\nThis is a note.\n"

        edits = provider.format_document(text, default_options)

        # No removal edit for line 1
        removal_edits = [e for e in edits if e.new_text == "" and e.range.start.line == 1 and e.range.end.line == 2]
        assert len(removal_edits) == 0


class TestRangeFormatting:
    """Test range-specific formatting."""

    def test_format_range_trailing_whitespace(
        self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions
    ) -> None:
        """Test formatting specific range removes trailing whitespace."""
        text = "Line 1  \nLine 2  \nLine 3  \n"
        range_ = lsp.Range(
            start=lsp.Position(line=1, character=0),
            end=lsp.Position(line=1, character=6),
        )

        edits = provider.format_range(text, range_, default_options)

        # Should only format line 1
        assert len(edits) == 1
        assert edits[0].range.start.line == 1

    def test_format_empty_range(
        self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions
    ) -> None:
        """Test formatting empty range."""
        text = "Content\n"
        range_ = lsp.Range(
            start=lsp.Position(line=0, character=0),
            end=lsp.Position(line=0, character=0),
        )

        edits = provider.format_range(text, range_, default_options)

        assert len(edits) == 0


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_document(self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions) -> None:
        """Test formatting empty document."""
        edits = provider.format_document("", default_options)

        assert len(edits) == 0

    def test_edits_sorted_descending(
        self, provider: AsciiDocFormattingProvider, default_options: lsp.FormattingOptions
    ) -> None:
        """Test edits are sorted descending for safe application."""
        text = "Line 1  \nLine 2  \n"

        edits = provider.format_document(text, default_options)

        # Edits should be sorted by position descending
        if len(edits) >= 2:
            for i in range(len(edits) - 1):
                assert edits[i].range.start.line >= edits[i + 1].range.start.line
