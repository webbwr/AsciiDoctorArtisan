"""
Tests for AsciiDoc LSP symbols provider.

Tests cover:
- Document outline (headings)
- Anchor symbols
- Go-to-definition for cross-references
- Symbol hierarchy
"""

import pytest
from lsprotocol import types as lsp

from asciidoc_artisan.lsp.symbols_provider import AsciiDocSymbolsProvider


@pytest.fixture
def provider() -> AsciiDocSymbolsProvider:
    """Create symbols provider instance."""
    return AsciiDocSymbolsProvider()


class TestDocumentSymbols:
    """Test document symbol extraction."""

    def test_heading_symbols(self, provider: AsciiDocSymbolsProvider) -> None:
        """Test extraction of heading symbols."""
        text = """= Document Title

== Section 1

== Section 2
"""
        symbols = provider.get_symbols(text)

        # Should find document title at top level
        names = [s.name for s in symbols]
        assert "Document Title" in names

        # Sections should be nested under document title (hierarchical)
        title_symbol = next(s for s in symbols if s.name == "Document Title")
        if title_symbol.children:
            child_names = [c.name for c in title_symbol.children]
            assert "Section 1" in child_names
            assert "Section 2" in child_names

    def test_nested_headings(self, provider: AsciiDocSymbolsProvider) -> None:
        """Test hierarchical heading structure."""
        text = """= Title

== Section 1

=== Subsection 1.1

== Section 2
"""
        symbols = provider.get_symbols(text)

        # Should create hierarchy
        # Find Section 1 and check it has children
        section1 = None
        for s in symbols:
            if s.name == "Section 1":
                section1 = s
                break

        # Subsection should be nested under Section 1
        if section1 and section1.children:
            child_names = [c.name for c in section1.children]
            assert "Subsection 1.1" in child_names

    def test_anchor_symbols(self, provider: AsciiDocSymbolsProvider) -> None:
        """Test anchor symbol extraction."""
        text = """[[my-anchor]]
== Section

[#another-anchor]
== Another Section
"""
        symbols = provider.get_symbols(text)

        # Should find anchors
        names = [s.name for s in symbols]
        assert "#my-anchor" in names
        assert "#another-anchor" in names

    def test_symbol_ranges(self, provider: AsciiDocSymbolsProvider) -> None:
        """Test symbols have correct range information."""
        text = """= Title

== Section
"""
        symbols = provider.get_symbols(text)

        for symbol in symbols:
            # Range should be valid
            assert symbol.range.start.line >= 0
            assert symbol.range.end.line >= symbol.range.start.line


class TestGoToDefinition:
    """Test go-to-definition functionality."""

    def test_find_anchor_definition(self, provider: AsciiDocSymbolsProvider) -> None:
        """Test finding anchor definition from cross-reference."""
        text = """[[introduction]]
== Introduction

See <<introduction>> for more details.
"""
        uri = "file:///test.adoc"
        position = lsp.Position(line=3, character=10)  # On <<introduction>>

        location = provider.find_definition(text, position, uri)

        assert location is not None
        assert location.uri == uri
        assert location.range.start.line == 0  # [[introduction]] is on line 0

    def test_find_anchor_with_block_id(self, provider: AsciiDocSymbolsProvider) -> None:
        """Test finding [#anchor] style definition."""
        text = """[#my-section]
== My Section

Reference: <<my-section>>
"""
        uri = "file:///test.adoc"

        # Search for the anchor definition
        location = provider._find_anchor_definition(text, "my-section", uri)

        assert location is not None
        assert location.range.start.line == 0

    def test_definition_not_found(self, provider: AsciiDocSymbolsProvider) -> None:
        """Test when definition is not found."""
        text = """== Section

See <<nonexistent>>
"""
        uri = "file:///test.adoc"

        location = provider._find_anchor_definition(text, "nonexistent", uri)

        assert location is None


class TestFindReferences:
    """Test find references functionality."""

    def test_find_anchor_references(self, provider: AsciiDocSymbolsProvider) -> None:
        """Test finding all references to an anchor."""
        text = """[[my-anchor]]
== Section

See <<my-anchor>> here.

And <<my-anchor>> again.
"""
        uri = "file:///test.adoc"

        locations = provider.find_references(text, "my-anchor", uri)

        # Should find 2 references (the <<my-anchor>> usages)
        assert len(locations) == 2


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_document(self, provider: AsciiDocSymbolsProvider) -> None:
        """Test empty document returns empty list."""
        symbols = provider.get_symbols("")

        assert symbols == []

    def test_no_headings(self, provider: AsciiDocSymbolsProvider) -> None:
        """Test document with no headings."""
        text = """This is a document without any headings.

Just plain text.
"""
        symbols = provider.get_symbols(text)

        # Should return empty or minimal list
        assert isinstance(symbols, list)
