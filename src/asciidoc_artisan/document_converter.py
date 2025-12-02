"""
Document Converter Module for AsciiDoc Artisan.

Re-export module for backward compatibility.
MA principle: Reduced from 641→45 lines by extracting pandoc_integration.py and pdf_extractor.py.

Provides high-performance document conversion with:
- Pandoc integration for format conversion
- PDF extraction with PyMuPDF (3-5x faster than pdfplumber)
- GPU acceleration on supported hardware

Example:
    ```python
    from asciidoc_artisan.document_converter import pandoc, pdf_extractor

    # Check pandoc installation
    available, message = ensure_pandoc_available()

    # Convert file
    success, text, error = pandoc.convert_file(path, "asciidoc")

    # Extract PDF
    success, text, error = pdf_extractor.extract_text(pdf_path)
    ```
"""

# Re-export from pandoc_integration module
from asciidoc_artisan.pandoc_integration import (
    PandocIntegration,
    ensure_pandoc_available,
    pandoc,
)

# Re-export from pdf_extractor module
from asciidoc_artisan.pdf_extractor import (
    PDFExtractor,
    pdf_extractor,
)

__all__ = [
    # Pandoc integration
    "PandocIntegration",
    "pandoc",
    "ensure_pandoc_available",
    # PDF extraction
    "PDFExtractor",
    "pdf_extractor",
]


if __name__ == "__main__":
    available, message = ensure_pandoc_available()
    print(f"Pandoc available: {available}")
    print(f"Status: {message}")

    if available:
        print("\nSupported formats:")
        print(f"  Input: {len(pandoc.supported_formats['input'])}")
        print(f"  Output: {len(pandoc.supported_formats['output'])}")

    # Test PDF extraction
    print(f"\nPDF extraction available: {PDFExtractor.is_available()}")
