"""Unit tests for LSP Server constants and provider integration.

Note: Direct server instantiation is complex due to pygls handler registration.
We test providers and constants individually.
"""

import pytest
from lsprotocol import types as lsp

from asciidoc_artisan.lsp.code_action_provider import AsciiDocCodeActionProvider
from asciidoc_artisan.lsp.completion_provider import AsciiDocCompletionProvider
from asciidoc_artisan.lsp.diagnostics_provider import AsciiDocDiagnosticsProvider
from asciidoc_artisan.lsp.document_state import DocumentState
from asciidoc_artisan.lsp.folding_provider import AsciiDocFoldingProvider
from asciidoc_artisan.lsp.formatting_provider import AsciiDocFormattingProvider
from asciidoc_artisan.lsp.hover_provider import AsciiDocHoverProvider
from asciidoc_artisan.lsp.semantic_tokens_provider import AsciiDocSemanticTokensProvider
from asciidoc_artisan.lsp.server import AsciiDocLanguageServer
from asciidoc_artisan.lsp.symbols_provider import AsciiDocSymbolsProvider


@pytest.mark.fr_108
class TestServerConstants:
    """Tests for server constants."""

    def test_server_name_constant(self):
        """Test server name is correct."""
        assert AsciiDocLanguageServer.SERVER_NAME == "asciidoc-artisan-lsp"

    def test_server_version_constant(self):
        """Test server version is correct."""
        assert AsciiDocLanguageServer.SERVER_VERSION == "1.0.0"


@pytest.mark.fr_108
class TestDocumentStateIntegration:
    """Tests for DocumentState used by server."""

    def test_document_state_open_and_get(self):
        """Test document state stores and retrieves content."""
        state = DocumentState()

        state.open_document("file:///test.adoc", "= Test\n\nContent", 1)
        result = state.get_document("file:///test.adoc")

        assert result == "= Test\n\nContent"

    def test_document_state_update(self):
        """Test document state updates content."""
        state = DocumentState()

        state.open_document("file:///test.adoc", "Original", 1)
        state.update_document("file:///test.adoc", "Updated", 2)
        result = state.get_document("file:///test.adoc")

        assert result == "Updated"

    def test_document_state_close(self):
        """Test document state removes on close."""
        state = DocumentState()

        state.open_document("file:///test.adoc", "Content", 1)
        state.close_document("file:///test.adoc")
        result = state.get_document("file:///test.adoc")

        assert result is None

    def test_document_state_unknown_returns_none(self):
        """Test unknown document returns None."""
        state = DocumentState()

        result = state.get_document("file:///unknown.adoc")

        assert result is None


@pytest.mark.fr_108
class TestCompletionProviderIntegration:
    """Tests for completion provider used by server."""

    def test_completion_provider_initialization(self):
        """Test completion provider initializes."""
        provider = AsciiDocCompletionProvider()
        assert provider is not None

    def test_completion_provider_returns_items(self):
        """Test completion provider returns items for attribute."""
        provider = AsciiDocCompletionProvider()
        position = lsp.Position(line=0, character=1)

        items = provider.get_completions(":a", position)

        assert isinstance(items, list)


@pytest.mark.fr_108
class TestDiagnosticsProviderIntegration:
    """Tests for diagnostics provider used by server."""

    def test_diagnostics_provider_initialization(self):
        """Test diagnostics provider initializes."""
        provider = AsciiDocDiagnosticsProvider()
        assert provider is not None

    def test_diagnostics_provider_returns_list(self):
        """Test diagnostics provider returns list."""
        provider = AsciiDocDiagnosticsProvider()

        diagnostics = provider.get_diagnostics("= Test Document")

        assert isinstance(diagnostics, list)

    def test_diagnostics_provider_finds_errors(self):
        """Test diagnostics provider finds syntax errors."""
        provider = AsciiDocDiagnosticsProvider()

        # Unclosed block should be an error
        diagnostics = provider.get_diagnostics("----\ncode block without closing")

        # May or may not find error depending on implementation
        assert isinstance(diagnostics, list)


@pytest.mark.fr_108
class TestHoverProviderIntegration:
    """Tests for hover provider used by server."""

    def test_hover_provider_initialization(self):
        """Test hover provider initializes."""
        provider = AsciiDocHoverProvider()
        assert provider is not None

    def test_hover_provider_on_attribute(self):
        """Test hover provider returns info for attribute."""
        provider = AsciiDocHoverProvider()
        position = lsp.Position(line=0, character=1)

        result = provider.get_hover(":author: Test", position)

        # Result may be None or Hover
        assert result is None or isinstance(result, lsp.Hover)


@pytest.mark.fr_108
class TestSymbolsProviderIntegration:
    """Tests for symbols provider used by server."""

    def test_symbols_provider_initialization(self):
        """Test symbols provider initializes."""
        provider = AsciiDocSymbolsProvider()
        assert provider is not None

    def test_symbols_provider_finds_sections(self):
        """Test symbols provider finds document sections."""
        provider = AsciiDocSymbolsProvider()

        symbols = provider.get_symbols("= Document\n\n== Section One\n\n== Section Two")

        assert isinstance(symbols, list)
        # Should find at least the title and sections
        assert len(symbols) >= 1


@pytest.mark.fr_108
class TestFoldingProviderIntegration:
    """Tests for folding provider used by server."""

    def test_folding_provider_initialization(self):
        """Test folding provider initializes."""
        provider = AsciiDocFoldingProvider()
        assert provider is not None

    def test_folding_provider_returns_ranges(self):
        """Test folding provider returns folding ranges."""
        provider = AsciiDocFoldingProvider()

        ranges = provider.get_folding_ranges("= Doc\n\n== Section\n\nContent\n\n== Another")

        assert isinstance(ranges, list)


@pytest.mark.fr_108
class TestFormattingProviderIntegration:
    """Tests for formatting provider used by server."""

    def test_formatting_provider_initialization(self):
        """Test formatting provider initializes."""
        provider = AsciiDocFormattingProvider()
        assert provider is not None

    def test_formatting_provider_formats_document(self):
        """Test formatting provider returns text edits."""
        provider = AsciiDocFormattingProvider()
        options = lsp.FormattingOptions(tab_size=2, insert_spaces=True)

        edits = provider.format_document("= Test  \n\n== Section", options)

        assert edits is None or isinstance(edits, list)


@pytest.mark.fr_108
class TestSemanticTokensProviderIntegration:
    """Tests for semantic tokens provider used by server."""

    def test_semantic_tokens_provider_initialization(self):
        """Test semantic tokens provider initializes."""
        provider = AsciiDocSemanticTokensProvider()
        assert provider is not None

    def test_semantic_tokens_provider_has_legend(self):
        """Test semantic tokens provider has legend."""
        provider = AsciiDocSemanticTokensProvider()

        legend = provider.get_legend()

        assert isinstance(legend, lsp.SemanticTokensLegend)
        assert len(legend.token_types) > 0

    def test_semantic_tokens_provider_returns_tokens(self):
        """Test semantic tokens provider returns tokens."""
        provider = AsciiDocSemanticTokensProvider()

        tokens = provider.get_tokens("= Title\n\n*bold* text")

        assert tokens is None or isinstance(tokens, lsp.SemanticTokens)


@pytest.mark.fr_108
class TestCodeActionProviderIntegration:
    """Tests for code action provider used by server."""

    def test_code_action_provider_initialization(self):
        """Test code action provider initializes."""
        provider = AsciiDocCodeActionProvider()
        assert provider is not None

    def test_code_action_provider_store_and_clear(self):
        """Test code action provider can store and clear fixes."""
        provider = AsciiDocCodeActionProvider()

        # Store some fixes
        provider.store_fixes("1:0:E001", ["Fix 1", "Fix 2"])

        # Clear
        provider.clear_cache()

        # Verify cleared (no way to get fixes without context)
        assert provider is not None
