"""
AsciiDoc Language Server Protocol (LSP) implementation.

MA principle: Modular architecture with focused modules (<400 lines each).

This package provides a full LSP server for AsciiDoc documents:
- Completion: Context-aware auto-complete (headings, attributes, xrefs)
- Diagnostics: Real-time syntax validation with quick fixes
- Hover: Documentation on hover
- Go-to-definition: Navigate to anchors and includes
- Document symbols: Outline view
- Formatting: Document formatting (future)

Architecture:
    AsciiDocLanguageServer (server.py) - Core LSP server with pygls
    ├── CompletionProvider (completion_provider.py) - Auto-complete logic
    ├── DiagnosticsProvider (diagnostics_provider.py) - Syntax validation
    ├── HoverProvider (hover_provider.py) - Hover documentation
    ├── DefinitionProvider (definition_provider.py) - Go-to-definition
    └── DocumentSymbolProvider (symbols_provider.py) - Document outline

Example usage:
    # Start as standalone server
    python -m asciidoc_artisan.lsp

    # Or use with editor integrations
    from asciidoc_artisan.lsp import AsciiDocLanguageServer
    server = AsciiDocLanguageServer()
    server.start_io()
"""

from asciidoc_artisan.lsp.server import AsciiDocLanguageServer

__all__ = [
    "AsciiDocLanguageServer",
]
