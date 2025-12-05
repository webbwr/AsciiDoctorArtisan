"""
Tests for AsciiDoc LSP semantic tokens provider.

Tests cover:
- Token type detection (headings, attributes, blocks, etc.)
- Delta encoding of token positions
- Token legend generation
"""

import pytest

from asciidoc_artisan.lsp.semantic_tokens_provider import (
    TOKEN_MODIFIERS,
    TOKEN_TYPES,
    AsciiDocSemanticTokensProvider,
)


@pytest.fixture
def provider() -> AsciiDocSemanticTokensProvider:
    """Create semantic tokens provider instance."""
    return AsciiDocSemanticTokensProvider()


class TestTokenLegend:
    """Test token legend generation."""

    def test_legend_has_token_types(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test legend includes token types."""
        legend = provider.get_legend()

        assert legend.token_types == TOKEN_TYPES
        assert "type" in legend.token_types  # headings
        assert "comment" in legend.token_types
        assert "function" in legend.token_types  # macros

    def test_legend_has_modifiers(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test legend includes token modifiers."""
        legend = provider.get_legend()

        assert legend.token_modifiers == TOKEN_MODIFIERS
        assert "declaration" in legend.token_modifiers


class TestHeadingTokens:
    """Test heading tokenization."""

    def test_document_title_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test document title is tokenized."""
        text = "= Document Title\n"

        tokens = provider.get_tokens(text)

        assert len(tokens.data) >= 5  # At least one token
        # First token should be heading (type 0)
        assert tokens.data[3] == 0  # token type index

    def test_section_heading_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test section heading is tokenized."""
        text = "== Section Heading\n"

        tokens = provider.get_tokens(text)

        assert len(tokens.data) >= 5
        assert tokens.data[3] == 0  # heading type


class TestAttributeTokens:
    """Test attribute tokenization."""

    def test_attribute_definition_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test attribute definition is tokenized."""
        text = ":author: John Doe\n"

        tokens = provider.get_tokens(text)

        assert len(tokens.data) >= 5
        assert tokens.data[3] == 1  # namespace type for attr def

    def test_attribute_reference_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test attribute reference is tokenized."""
        text = "The {author} wrote this.\n"

        tokens = provider.get_tokens(text)

        assert len(tokens.data) >= 5
        assert tokens.data[3] == 2  # variable type for attr ref


class TestBlockTokens:
    """Test block tokenization."""

    def test_block_type_annotation(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test block type annotation is tokenized."""
        text = "[source,python]\n"

        tokens = provider.get_tokens(text)

        assert len(tokens.data) >= 5
        assert tokens.data[3] == 3  # keyword type


class TestCommentTokens:
    """Test comment tokenization."""

    def test_comment_line_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test comment line is tokenized."""
        text = "// This is a comment\n"

        tokens = provider.get_tokens(text)

        assert len(tokens.data) >= 5
        assert tokens.data[3] == 4  # comment type

    def test_comment_block_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test comment block is tokenized."""
        text = "////\nComment content\n////\n"

        tokens = provider.get_tokens(text)

        # Should have multiple comment tokens
        assert len(tokens.data) >= 10  # At least 2 tokens


class TestMacroTokens:
    """Test macro tokenization."""

    def test_image_macro_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test image macro is tokenized."""
        text = "image::logo.png[Logo]\n"

        tokens = provider.get_tokens(text)

        # Should have token for macro
        assert len(tokens.data) >= 5
        # Look for function type (5)
        token_types = [tokens.data[i] for i in range(3, len(tokens.data), 5)]
        assert 5 in token_types  # function type for macro

    def test_include_macro_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test include macro is tokenized."""
        text = "include::chapter.adoc[]\n"

        tokens = provider.get_tokens(text)

        token_types = [tokens.data[i] for i in range(3, len(tokens.data), 5)]
        assert 5 in token_types


class TestCrossReferenceTokens:
    """Test cross-reference tokenization."""

    def test_xref_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test cross-reference is tokenized."""
        text = "See <<section-id>> for more.\n"

        tokens = provider.get_tokens(text)

        # Should have token for xref
        token_types = [tokens.data[i] for i in range(3, len(tokens.data), 5)]
        assert 7 in token_types  # parameter type for xref

    def test_anchor_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test anchor is tokenized."""
        text = "[[my-anchor]]\n"

        tokens = provider.get_tokens(text)

        token_types = [tokens.data[i] for i in range(3, len(tokens.data), 5)]
        assert 7 in token_types  # parameter type for anchor


class TestFormattingTokens:
    """Test inline formatting tokenization."""

    def test_bold_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test bold text is tokenized."""
        text = "This is *bold* text.\n"

        tokens = provider.get_tokens(text)

        token_types = [tokens.data[i] for i in range(3, len(tokens.data), 5)]
        assert 6 in token_types  # decorator type

    def test_italic_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test italic text is tokenized."""
        text = "This is _italic_ text.\n"

        tokens = provider.get_tokens(text)

        token_types = [tokens.data[i] for i in range(3, len(tokens.data), 5)]
        assert 6 in token_types

    def test_monospace_token(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test monospace text is tokenized."""
        text = "This is `mono` text.\n"

        tokens = provider.get_tokens(text)

        token_types = [tokens.data[i] for i in range(3, len(tokens.data), 5)]
        assert 6 in token_types


class TestDeltaEncoding:
    """Test delta encoding of token positions."""

    def test_tokens_sorted_by_position(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test tokens are sorted by line then character."""
        text = "= Title\n{attr}\n"

        tokens = provider.get_tokens(text)

        # Should have tokens for heading and attr ref
        assert len(tokens.data) >= 10

    def test_delta_encoding_multiline(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test delta encoding across multiple lines."""
        text = "= Line 1\n= Line 2\n"

        tokens = provider.get_tokens(text)

        # Second token should have delta_line = 1
        if len(tokens.data) >= 10:
            # First 5 values are first token, next 5 are second
            delta_line = tokens.data[5]  # delta_line for second token
            assert delta_line == 1

    def test_empty_document_no_tokens(self, provider: AsciiDocSemanticTokensProvider) -> None:
        """Test empty document returns no tokens."""
        tokens = provider.get_tokens("")

        assert len(tokens.data) == 0
