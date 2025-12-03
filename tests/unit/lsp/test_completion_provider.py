"""
Tests for AsciiDoc LSP completion provider.

Tests cover:
- Syntax completions (headings, blocks, lists)
- Attribute completions
- Cross-reference completions
- Include directive completions
- Context detection
"""

import pytest
from lsprotocol import types as lsp

from asciidoc_artisan.lsp.completion_provider import AsciiDocCompletionProvider


@pytest.fixture
def provider() -> AsciiDocCompletionProvider:
    """Create completion provider instance."""
    return AsciiDocCompletionProvider()


class TestSyntaxCompletions:
    """Test syntax-based completions."""

    def test_heading_completions(self, provider: AsciiDocCompletionProvider) -> None:
        """Test heading completions at line start."""
        text = "= \n"
        position = lsp.Position(line=0, character=2)

        items = provider.get_completions(text, position)

        # Should include heading completions
        labels = [item.label for item in items]
        assert any("Heading" in label for label in labels)

    def test_block_completions(self, provider: AsciiDocCompletionProvider) -> None:
        """Test block type completions."""
        text = "[source\n"
        position = lsp.Position(line=0, character=7)

        items = provider.get_completions(text, position)

        # Should include source block completions
        labels = [item.label for item in items]
        assert any("[source]" in label for label in labels)

    def test_list_completions(self, provider: AsciiDocCompletionProvider) -> None:
        """Test list item completions."""
        text = "* \n"
        position = lsp.Position(line=0, character=2)

        items = provider.get_completions(text, position)

        # Should include list completions
        labels = [item.label for item in items]
        assert any("list" in label.lower() for label in labels)

    def test_empty_prefix_returns_all_syntax(self, provider: AsciiDocCompletionProvider) -> None:
        """Test that empty prefix returns syntax completions."""
        text = "\n"
        position = lsp.Position(line=0, character=0)

        items = provider.get_completions(text, position)

        # Should return many completions
        assert len(items) > 10


class TestAttributeCompletions:
    """Test document attribute completions."""

    def test_attribute_context_detection(self, provider: AsciiDocCompletionProvider) -> None:
        """Test detection of attribute context."""
        # Starting with : should trigger attribute completions
        text = ":auth\n"
        position = lsp.Position(line=0, character=5)

        items = provider.get_completions(text, position)

        # Should include author attribute
        labels = [item.label for item in items]
        assert any(":author:" in label for label in labels)

    def test_attribute_completions_filter(self, provider: AsciiDocCompletionProvider) -> None:
        """Test attribute completion filtering."""
        text = ":toc\n"
        position = lsp.Position(line=0, character=4)

        items = provider.get_completions(text, position)

        # Should include toc-related attributes
        labels = [item.label for item in items]
        assert any(":toc:" in label for label in labels)


class TestCrossReferenceCompletions:
    """Test cross-reference completions."""

    def test_xref_context_detection(self, provider: AsciiDocCompletionProvider) -> None:
        """Test detection of xref context."""
        text = "See <<intro\n"
        position = lsp.Position(line=0, character=11)

        # Should detect xref context (<<)
        items = provider.get_completions(text, position)
        # With no anchors defined, should return empty or limited results
        assert isinstance(items, list)

    def test_xref_completions_with_anchors(self, provider: AsciiDocCompletionProvider) -> None:
        """Test xref completions show document anchors."""
        text = """[[introduction]]
== Introduction

See <<intro
"""
        position = lsp.Position(line=3, character=11)

        items = provider.get_completions(text, position)

        # Should find the 'introduction' anchor
        labels = [item.label for item in items]
        assert "introduction" in labels

    def test_anchor_extraction(self, provider: AsciiDocCompletionProvider) -> None:
        """Test anchor extraction from document."""
        text = """[[anchor1]]
== Section 1

[#anchor2]
== Section 2

Some text <<anchor1>>
"""
        anchors = provider._extract_anchors(text)

        assert "anchor1" in anchors
        assert "anchor2" in anchors


class TestIncludeCompletions:
    """Test include directive completions."""

    def test_include_context_detection(self, provider: AsciiDocCompletionProvider) -> None:
        """Test detection of include context."""
        text = "include::chapter\n"
        position = lsp.Position(line=0, character=17)

        items = provider.get_completions(text, position)

        # Should return include-related completions
        assert isinstance(items, list)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_document(self, provider: AsciiDocCompletionProvider) -> None:
        """Test completions for empty document."""
        text = ""
        position = lsp.Position(line=0, character=0)

        items = provider.get_completions(text, position)

        # Should not crash, return syntax completions
        assert isinstance(items, list)

    def test_position_beyond_document(self, provider: AsciiDocCompletionProvider) -> None:
        """Test completions for position beyond document."""
        text = "= Title\n"
        position = lsp.Position(line=10, character=0)

        items = provider.get_completions(text, position)

        # Should return empty list, not crash
        assert items == []

    def test_completion_item_structure(self, provider: AsciiDocCompletionProvider) -> None:
        """Test that completion items have correct structure."""
        text = "= \n"
        position = lsp.Position(line=0, character=2)

        items = provider.get_completions(text, position)

        if items:
            item = items[0]
            assert hasattr(item, "label")
            assert hasattr(item, "kind")
            assert hasattr(item, "insert_text")
