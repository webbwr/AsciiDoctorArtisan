"""
AsciiDoc Language Server - Core LSP implementation using pygls.

MA principle: ~200 lines focused on server lifecycle and feature registration.

This module provides the main Language Server Protocol server for AsciiDoc.
Uses pygls for the heavy lifting, delegates to feature providers for logic.

Features:
- textDocument/completion: Auto-complete
- textDocument/publishDiagnostics: Real-time syntax validation
- textDocument/hover: Documentation on hover
- textDocument/definition: Go-to-definition
- textDocument/documentSymbol: Document outline

Example:
    # Standalone server
    server = AsciiDocLanguageServer()
    server.start_io()  # stdio transport

    # TCP server for debugging
    server.start_tcp("localhost", 2087)
"""

import logging

from lsprotocol import types as lsp
from pygls.lsp.server import LanguageServer

from asciidoc_artisan.lsp.completion_provider import AsciiDocCompletionProvider
from asciidoc_artisan.lsp.diagnostics_provider import AsciiDocDiagnosticsProvider
from asciidoc_artisan.lsp.document_state import DocumentState
from asciidoc_artisan.lsp.hover_provider import AsciiDocHoverProvider
from asciidoc_artisan.lsp.symbols_provider import AsciiDocSymbolsProvider

logger = logging.getLogger(__name__)


class AsciiDocLanguageServer(LanguageServer):
    """
    Language Server for AsciiDoc documents.

    Provides IDE-like features via LSP:
    - Auto-complete for syntax, attributes, cross-references
    - Real-time diagnostics with quick fixes
    - Hover documentation
    - Go-to-definition for anchors and includes
    - Document outline (symbols)

    Thread Safety:
        Uses pygls's built-in threading model - all feature handlers
        run on a separate thread pool.

    Attributes:
        document_state: Manages document content and state
        completion_provider: Handles completion requests
        diagnostics_provider: Handles diagnostics
        hover_provider: Handles hover requests
        symbols_provider: Handles document symbol requests
    """

    SERVER_NAME = "asciidoc-artisan-lsp"
    SERVER_VERSION = "1.0.0"

    def __init__(self) -> None:
        """Initialize AsciiDoc Language Server."""
        super().__init__(name=self.SERVER_NAME, version=self.SERVER_VERSION)

        # Document state management
        self.document_state = DocumentState()

        # Feature providers
        self.completion_provider = AsciiDocCompletionProvider()
        self.diagnostics_provider = AsciiDocDiagnosticsProvider()
        self.hover_provider = AsciiDocHoverProvider()
        self.symbols_provider = AsciiDocSymbolsProvider()

        # Register handlers
        self._register_handlers()

        logger.info(f"AsciiDoc Language Server {self.SERVER_VERSION} initialized")

    def _register_handlers(self) -> None:
        """Register LSP feature handlers."""
        # Document sync
        self.feature(lsp.TEXT_DOCUMENT_DID_OPEN)(self._on_did_open)
        self.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)(self._on_did_change)
        self.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)(self._on_did_close)
        self.feature(lsp.TEXT_DOCUMENT_DID_SAVE)(self._on_did_save)

        # Language features
        self.feature(lsp.TEXT_DOCUMENT_COMPLETION)(self._on_completion)
        self.feature(lsp.TEXT_DOCUMENT_HOVER)(self._on_hover)
        self.feature(lsp.TEXT_DOCUMENT_DEFINITION)(self._on_definition)
        self.feature(lsp.TEXT_DOCUMENT_DOCUMENT_SYMBOL)(self._on_document_symbol)

    def _on_did_open(self, params: lsp.DidOpenTextDocumentParams) -> None:
        """Handle document open - store content and run initial diagnostics."""
        uri = params.text_document.uri
        text = params.text_document.text
        version = params.text_document.version

        self.document_state.open_document(uri, text, version)
        logger.debug(f"Document opened: {uri}")

        # Run initial diagnostics
        self._publish_diagnostics(uri, text)

    def _on_did_change(self, params: lsp.DidChangeTextDocumentParams) -> None:
        """Handle document change - update content and refresh diagnostics."""
        uri = params.text_document.uri
        version = params.text_document.version

        # Apply changes (full sync mode - get full text)
        text: str | None = None
        for change in params.content_changes:
            if isinstance(change, lsp.TextDocumentContentChangeWholeDocument):
                # Full document sync
                self.document_state.update_document(uri, change.text, version)
                text = change.text
            else:
                # Incremental sync not fully supported yet
                text = self.document_state.get_document(uri)

        logger.debug(f"Document changed: {uri}")

        # Refresh diagnostics
        if text is not None:
            self._publish_diagnostics(uri, text)

    def _on_did_close(self, params: lsp.DidCloseTextDocumentParams) -> None:
        """Handle document close - clean up state."""
        uri = params.text_document.uri
        self.document_state.close_document(uri)
        logger.debug(f"Document closed: {uri}")

        # Clear diagnostics
        self.text_document_publish_diagnostics(lsp.PublishDiagnosticsParams(uri=uri, diagnostics=[]))

    def _on_did_save(self, params: lsp.DidSaveTextDocumentParams) -> None:
        """Handle document save - refresh diagnostics if text included."""
        uri = params.text_document.uri

        if params.text:
            self._publish_diagnostics(uri, params.text)

        logger.debug(f"Document saved: {uri}")

    def _on_completion(self, params: lsp.CompletionParams) -> lsp.CompletionList | None:
        """Handle completion request."""
        uri = params.text_document.uri
        position = params.position
        text = self.document_state.get_document(uri)

        if not text:
            return None

        items = self.completion_provider.get_completions(text, position)
        return lsp.CompletionList(is_incomplete=False, items=items)

    def _on_hover(self, params: lsp.HoverParams) -> lsp.Hover | None:
        """Handle hover request."""
        uri = params.text_document.uri
        position = params.position
        text = self.document_state.get_document(uri)

        if not text:
            return None

        return self.hover_provider.get_hover(text, position)

    def _on_definition(self, params: lsp.DefinitionParams) -> lsp.Location | list[lsp.Location] | None:
        """Handle go-to-definition request."""
        uri = params.text_document.uri
        position = params.position
        text = self.document_state.get_document(uri)

        if not text:
            return None

        # Find definition in same document
        location = self.symbols_provider.find_definition(text, position, uri)
        return location

    def _on_document_symbol(self, params: lsp.DocumentSymbolParams) -> list[lsp.DocumentSymbol] | None:
        """Handle document symbol request (outline)."""
        uri = params.text_document.uri
        text = self.document_state.get_document(uri)

        if not text:
            return None

        return self.symbols_provider.get_symbols(text)

    def _publish_diagnostics(self, uri: str, text: str) -> None:
        """Run diagnostics and publish results."""
        diagnostics = self.diagnostics_provider.get_diagnostics(text)
        self.text_document_publish_diagnostics(lsp.PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics))

    def get_capabilities(self) -> lsp.ServerCapabilities:
        """Return server capabilities for initialization."""
        return lsp.ServerCapabilities(
            text_document_sync=lsp.TextDocumentSyncOptions(
                open_close=True,
                change=lsp.TextDocumentSyncKind.Full,
                save=lsp.SaveOptions(include_text=True),
            ),
            completion_provider=lsp.CompletionOptions(
                trigger_characters=[":", "[", "<", "=", "{"],
                resolve_provider=False,
            ),
            hover_provider=lsp.HoverOptions(),
            definition_provider=lsp.DefinitionOptions(),
            document_symbol_provider=lsp.DocumentSymbolOptions(),
        )


def main() -> None:
    """Run the AsciiDoc Language Server."""
    import argparse

    parser = argparse.ArgumentParser(description="AsciiDoc Language Server")
    parser.add_argument(
        "--tcp",
        action="store_true",
        help="Use TCP transport instead of stdio",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="TCP host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=2087,
        help="TCP port (default: 2087)",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    server = AsciiDocLanguageServer()

    if args.tcp:
        logger.info(f"Starting TCP server on {args.host}:{args.port}")
        server.start_tcp(args.host, args.port)
    else:
        logger.info("Starting stdio server")
        server.start_io()


if __name__ == "__main__":
    main()
