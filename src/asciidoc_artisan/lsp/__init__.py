"""
AsciiDoc Language Server Protocol (LSP) implementation.

MA principle: Modular architecture with focused modules (<400 lines each).

This package provides a full LSP server for AsciiDoc documents:
- Completion: Context-aware auto-complete (headings, attributes, xrefs)
- Diagnostics: Real-time syntax validation with quick fixes
- Hover: Documentation on hover
- Go-to-definition: Navigate to anchors and includes
- Document symbols: Outline view
- Code actions: Quick fixes for diagnostics
- Folding: Collapsible regions (sections, blocks, comments)
- Formatting: Document formatting (trailing whitespace, spacing)
- Semantic tokens: Syntax highlighting

Architecture:
    AsciiDocLanguageServer (server.py) - Core LSP server with pygls
    ├── CompletionProvider - Auto-complete logic
    ├── DiagnosticsProvider - Syntax validation
    ├── HoverProvider - Hover documentation
    ├── SymbolsProvider - Document outline + go-to-definition
    ├── CodeActionProvider - Quick fixes
    ├── FoldingProvider - Collapsible regions
    ├── FormattingProvider - Document formatting
    └── SemanticTokensProvider - Syntax highlighting

Example usage:
    # Start as standalone server
    python -m asciidoc_artisan.lsp

    # Or use with editor integrations
    from asciidoc_artisan.lsp import AsciiDocLanguageServer
    server = AsciiDocLanguageServer()
    server.start_io()
"""

from asciidoc_artisan.lsp.code_action_provider import AsciiDocCodeActionProvider
from asciidoc_artisan.lsp.folding_provider import AsciiDocFoldingProvider
from asciidoc_artisan.lsp.formatting_provider import AsciiDocFormattingProvider
from asciidoc_artisan.lsp.semantic_tokens_provider import AsciiDocSemanticTokensProvider
from asciidoc_artisan.lsp.server import AsciiDocLanguageServer

__all__ = [
    "AsciiDocLanguageServer",
    "AsciiDocCodeActionProvider",
    "AsciiDocFoldingProvider",
    "AsciiDocFormattingProvider",
    "AsciiDocSemanticTokensProvider",
]
