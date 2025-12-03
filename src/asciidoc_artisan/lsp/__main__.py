"""
Entry point for running AsciiDoc LSP server as a module.

Usage:
    python -m asciidoc_artisan.lsp          # stdio mode
    python -m asciidoc_artisan.lsp --tcp    # TCP mode (localhost:2087)
    python -m asciidoc_artisan.lsp --tcp --port 8080  # Custom port
"""

from asciidoc_artisan.lsp.server import main

if __name__ == "__main__":
    main()
