"""
Export Helpers - Helper classes for document export operations.

This module provides focused helper classes extracted from ExportManager
to improve maintainability and reduce code duplication.

Helper Classes:
- HTMLConverter: Convert AsciiDoc to HTML
- PDFHelper: PDF engine detection and CSS generation
- ClipboardHelper: Clipboard format conversion

Extracted from export_manager.py to follow Single Responsibility Principle.
"""

import io
import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class HTMLConverter:
    """
    Helper class for converting AsciiDoc content to HTML.

    Handles AsciiDoc to HTML conversion using the asciidoc3 API.
    Extracted to eliminate duplication between export methods.
    """

    def __init__(self, asciidoc_api: Any) -> None:
        """
        Initialize HTMLConverter.

        Args:
            asciidoc_api: AsciiDoc API instance (from asciidoc3.AsciiDoc3)
        """
        self.asciidoc_api = asciidoc_api

    def asciidoc_to_html(self, content: str, backend: str = "html5") -> str:
        """
        Convert AsciiDoc content to HTML.

        Args:
            content: AsciiDoc content to convert
            backend: AsciiDoc backend (default: "html5")

        Returns:
            HTML content as string

        Raises:
            RuntimeError: If AsciiDoc API is not initialized
            Exception: If conversion fails
        """
        if self.asciidoc_api is None:
            raise RuntimeError("AsciiDoc renderer not initialized")

        infile = io.StringIO(content)
        outfile = io.StringIO()
        self.asciidoc_api.execute(infile, outfile, backend=backend)
        return outfile.getvalue()


class PDFHelper:
    """
    Helper class for PDF export operations.

    Provides:
    - PDF engine detection (wkhtmltopdf, weasyprint, etc.)
    - Print CSS generation for better PDF output
    """

    # PDF engines in priority order (fastest to slowest)
    PDF_ENGINES = [
        "wkhtmltopdf",
        "weasyprint",
        "prince",
        "pdflatex",
        "xelatex",
        "lualatex",
    ]

    @staticmethod
    def check_pdf_engine_available(engine: str | None = None) -> bool:
        """
        Check if a PDF engine is available on the system.

        Args:
            engine: Specific engine to check (None = check any)

        Returns:
            True if engine(s) available, False otherwise
        """
        engines_to_check = [engine] if engine else PDFHelper.PDF_ENGINES

        for eng in engines_to_check:
            try:
                result = subprocess.run(
                    [eng, "--version"],
                    capture_output=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0:
                    logger.debug(f"PDF engine available: {eng}")
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
                continue

        logger.warning("No PDF engine available")
        return False

    @staticmethod
    def _get_page_css() -> str:
        """Get @page CSS rules."""
        return """@page {
    size: A4;
    margin: 2cm;
}"""

    @staticmethod
    def _get_body_css() -> str:
        """Get body and heading CSS rules."""
        return """body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
    max-width: 100%;
}

h1, h2, h3, h4, h5, h6 {
    page-break-after: avoid;
    margin-top: 1.2em;
    margin-bottom: 0.6em;
}

h1 { font-size: 24pt; }
h2 { font-size: 20pt; }
h3 { font-size: 16pt; }"""

    @staticmethod
    def _get_code_css() -> str:
        """Get code and pre CSS rules."""
        return """pre, code {
    font-family: 'Courier New', Courier, monospace;
    font-size: 9pt;
    background: #f5f5f5;
    border: 1px solid #ddd;
    page-break-inside: avoid;
}

pre {
    padding: 10px;
    overflow-x: auto;
}

code {
    padding: 2px 4px;
}"""

    @staticmethod
    def _get_table_css() -> str:
        """Get table CSS rules."""
        return """table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #f0f0f0;
    font-weight: bold;
}"""

    @staticmethod
    def _get_misc_css() -> str:
        """Get miscellaneous element CSS rules."""
        return """img {
    max-width: 100%;
    page-break-inside: avoid;
}

a {
    color: #0066cc;
    text-decoration: none;
}

blockquote {
    border-left: 4px solid #ccc;
    margin: 1em 0;
    padding-left: 1em;
    font-style: italic;
}

ul, ol {
    margin: 0.5em 0;
    padding-left: 2em;
}"""

    @staticmethod
    def _get_print_media_css() -> str:
        """Get @media print CSS rules."""
        return """@media print {
    body {
        background: white;
    }

    a[href]:after {
        content: " (" attr(href) ")";
        font-size: 90%;
        color: #666;
    }

    pre, code, blockquote, table {
        border-color: #999;
    }
}"""

    @staticmethod
    def add_print_css_to_html(html_content: str) -> str:
        """
        Add print-optimized CSS to HTML content for better PDF output.

        Injects CSS rules for:
        - Page margins and sizes
        - Font sizing and readability
        - Code block formatting
        - Table styling
        - Print-specific optimizations

        Args:
            html_content: HTML content to enhance

        Returns:
            HTML content with injected CSS

        MA principle: Reduced from 107 lines to ~20 lines by splitting
        CSS generation into 6 category-specific helper methods.
        """
        # Combine all CSS sections
        css_parts = [
            PDFHelper._get_page_css(),
            PDFHelper._get_body_css(),
            PDFHelper._get_code_css(),
            PDFHelper._get_table_css(),
            PDFHelper._get_misc_css(),
            PDFHelper._get_print_media_css(),
        ]
        print_css = f"<style>\n{chr(10).join(css_parts)}\n</style>"

        # Insert CSS before closing </head> tag or at start of <body>
        if "</head>" in html_content:
            return html_content.replace("</head>", f"{print_css}</head>")
        elif "<body>" in html_content:
            return html_content.replace("<body>", f"<body>{print_css}")
        else:
            return print_css + html_content


class ClipboardHelper:
    """
    Helper class for clipboard format conversion operations.

    Handles converting clipboard content between formats using Pandoc.
    """

    @staticmethod
    def parse_format_from_clipboard(clipboard_text: str) -> str | None:
        """
        Detect format of clipboard content.

        Args:
            clipboard_text: Text from clipboard

        Returns:
            Detected format ("markdown", "html", etc.) or None
        """
        text_lower = clipboard_text.strip().lower()

        # HTML detection
        if text_lower.startswith("<!doctype html") or text_lower.startswith("<html"):
            return "html"
        if "<p>" in text_lower or "<div>" in text_lower:
            return "html"

        # Markdown detection
        if any(marker in clipboard_text for marker in ["# ", "## ", "**", "```", "[](", "* ", "- "]):
            return "markdown"

        # Default: treat as plain text
        return None
