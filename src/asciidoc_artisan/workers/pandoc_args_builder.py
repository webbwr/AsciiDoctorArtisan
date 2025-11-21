"""
Pandoc Args Builder - Handles Pandoc command-line argument construction.

Extracted from PandocWorker to reduce class size (MA principle).
Handles PDF engine detection and argument building for different formats.
"""

import logging
import subprocess

logger = logging.getLogger(__name__)


class PandocArgsBuilder:
    """
    Handles Pandoc command-line argument construction.

    This class was extracted from PandocWorker to reduce class size
    per MA principle (489→~388 lines).

    Handles:
    - PDF engine detection and selection
    - Format-specific argument building
    - Base argument configuration
    """

    def detect_pdf_engine(self) -> str:
        """
        Detect available PDF engine for Pandoc PDF conversion.

        Tries engines in priority order: wkhtmltopdf (fastest), weasyprint,
        prince, pdflatex, xelatex, lualatex, context, pdfroff.

        Returns:
            Name of the first available PDF engine

        Raises:
            RuntimeError: If no PDF engine is available
        """
        pdf_engines = [
            "wkhtmltopdf",
            "weasyprint",
            "prince",
            "pdflatex",
            "xelatex",
            "lualatex",
            "context",
            "pdfroff",
        ]

        for engine in pdf_engines:
            try:
                subprocess.run(
                    [engine, "--version"],
                    capture_output=True,
                    check=True,
                    timeout=5,  # 5 second timeout for version check
                )
                logger.info(f"Using PDF engine: {engine}")
                return engine
            except (
                FileNotFoundError,
                subprocess.CalledProcessError,
                subprocess.TimeoutExpired,
                Exception,
            ):
                # Engine not found, returned error, timed out, or other issue
                # Continue to next engine
                continue

        # No PDF engine available - this should not happen in production
        logger.error("No PDF engine found. Install wkhtmltopdf, weasyprint, or pdflatex.")
        raise RuntimeError(
            "PDF conversion requires a PDF engine. Install wkhtmltopdf: sudo apt-get install wkhtmltopdf"
        )

    def build_pandoc_args(self, from_format: str, to_format: str) -> list[str]:
        """
        Build Pandoc command-line arguments based on format conversion.

        Args:
            from_format: Source format (e.g., "docx", "markdown")
            to_format: Target format (e.g., "pdf", "asciidoc")

        Returns:
            List of Pandoc command-line arguments
        """
        # Base Pandoc arguments
        extra_args = [
            "--wrap=preserve",
            "--reference-links",
            "--standalone",
            "--toc-depth=3",
        ]

        # Format-specific arguments - input format
        if from_format == "docx":
            extra_args.extend(
                [
                    "--extract-media=.",
                ]
            )

        # Format-specific arguments - output format
        if to_format == "pdf":
            # PDF-specific arguments
            extra_args.extend(
                [
                    "--variable=geometry:margin=1in",
                    "--variable=fontsize=11pt",
                    "--highlight-style=tango",
                ]
            )

            # Detect and configure PDF engine
            pdf_engine = self.detect_pdf_engine()
            extra_args.append(f"--pdf-engine={pdf_engine}")
        elif to_format == "docx":
            # DOCX-specific arguments (currently none)
            pass
        elif to_format == "markdown":
            extra_args.extend(
                [
                    "--wrap=none",
                ]
            )

        return extra_args
