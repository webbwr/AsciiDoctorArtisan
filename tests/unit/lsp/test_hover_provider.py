"""
Tests for AsciiDoc LSP hover provider.

Tests cover:
- Hover documentation for syntax elements
- Hover for document attributes
- Pattern matching
"""

import pytest
from lsprotocol import types as lsp

from asciidoc_artisan.lsp.hover_provider import AsciiDocHoverProvider


@pytest.fixture
def provider() -> AsciiDocHoverProvider:
    """Create hover provider instance."""
    return AsciiDocHoverProvider()


class TestSyntaxHover:
    """Test hover for syntax elements."""

    def test_heading_hover(self, provider: AsciiDocHoverProvider) -> None:
        """Test hover on heading line."""
        text = "= Document Title\n"
        position = lsp.Position(line=0, character=5)

        hover = provider.get_hover(text, position)

        assert hover is not None
        assert isinstance(hover.contents, lsp.MarkupContent)
        assert "Title" in hover.contents.value or "Document" in hover.contents.value

    def test_section_heading_hover(self, provider: AsciiDocHoverProvider) -> None:
        """Test hover on section heading."""
        text = "== Section\n"
        position = lsp.Position(line=0, character=5)

        hover = provider.get_hover(text, position)

        assert hover is not None
        assert "Section" in hover.contents.value or "Heading" in hover.contents.value

    def test_source_block_hover(self, provider: AsciiDocHoverProvider) -> None:
        """Test hover on source block."""
        text = "[source,python]\n"
        position = lsp.Position(line=0, character=5)

        hover = provider.get_hover(text, position)

        assert hover is not None
        assert "source" in hover.contents.value.lower() or "code" in hover.contents.value.lower()

    def test_note_admonition_hover(self, provider: AsciiDocHoverProvider) -> None:
        """Test hover on NOTE admonition."""
        text = "[NOTE]\n"
        position = lsp.Position(line=0, character=3)

        hover = provider.get_hover(text, position)

        assert hover is not None
        assert "Note" in hover.contents.value

    def test_listing_delimiter_hover(self, provider: AsciiDocHoverProvider) -> None:
        """Test hover on listing delimiter."""
        text = "----\n"
        position = lsp.Position(line=0, character=2)

        hover = provider.get_hover(text, position)

        assert hover is not None
        assert "Listing" in hover.contents.value or "block" in hover.contents.value.lower()


class TestAttributeHover:
    """Test hover for document attributes."""

    def test_toc_attribute_hover(self, provider: AsciiDocHoverProvider) -> None:
        """Test hover on :toc: attribute."""
        text = ":toc:\n"
        position = lsp.Position(line=0, character=3)

        hover = provider.get_hover(text, position)

        assert hover is not None
        assert "toc" in hover.contents.value.lower() or "contents" in hover.contents.value.lower()

    def test_author_attribute_hover(self, provider: AsciiDocHoverProvider) -> None:
        """Test hover on :author: attribute."""
        text = ":author: John Doe\n"
        position = lsp.Position(line=0, character=5)

        hover = provider.get_hover(text, position)

        assert hover is not None
        assert "author" in hover.contents.value.lower()


class TestNoHover:
    """Test cases where no hover should be shown."""

    def test_plain_text_no_hover(self, provider: AsciiDocHoverProvider) -> None:
        """Test no hover on plain text."""
        text = "This is plain text without any special syntax.\n"
        position = lsp.Position(line=0, character=10)

        hover = provider.get_hover(text, position)

        # Plain text should not have hover
        assert hover is None

    def test_position_beyond_document(self, provider: AsciiDocHoverProvider) -> None:
        """Test hover beyond document returns None."""
        text = "= Title\n"
        position = lsp.Position(line=10, character=0)

        hover = provider.get_hover(text, position)

        assert hover is None


class TestHoverContent:
    """Test hover content format."""

    def test_hover_is_markdown(self, provider: AsciiDocHoverProvider) -> None:
        """Test hover content is markdown format."""
        text = "= Title\n"
        position = lsp.Position(line=0, character=2)

        hover = provider.get_hover(text, position)

        if hover:
            assert hover.contents.kind == lsp.MarkupKind.Markdown
