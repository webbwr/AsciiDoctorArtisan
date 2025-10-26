"""
Pandoc Worker - Background thread for document format conversion.

This module provides the PandocWorker class which executes Pandoc document
conversions in a background QThread, with optional AI-enhanced conversion
using Claude API.

Implements:
- FR-021 to FR-030: Format conversion requirements
- FR-054 to FR-062: AI-enhanced conversion with Claude API
- NFR-005: Long-running operations in background threads
- NFR-010: Parameterized subprocess calls (no shell injection)

Conversion Flow:
1. If use_ai_conversion=True and Claude available -> Try AI conversion
2. If AI fails or unavailable -> Fallback to Pandoc
3. Emit progress signals during operation
4. Emit conversion_complete or conversion_error signal

Supported Formats:
- Input: docx, markdown, html, latex, rst, org, textile
- Output: asciidoc, html, docx, pdf, markdown, latex
"""

import logging
import re
import subprocess
from pathlib import Path
from typing import Optional, Union

from PySide6.QtCore import QObject, Signal, Slot

# Check for Pandoc availability
try:
    import pypandoc

    PANDOC_AVAILABLE = True
except ImportError:
    pypandoc = None
    PANDOC_AVAILABLE = False

# AI client removed - using Ollama for local AI features instead

logger = logging.getLogger(__name__)


class PandocWorker(QObject):
    """
    Background worker for document format conversion.

    Supports both Pandoc and AI-enhanced conversion via Claude API.
    Runs in separate QThread to prevent UI blocking.

    Signals:
        conversion_complete(str, str): Emitted on success with (result_text, context)
        conversion_error(str, str): Emitted on failure with (error_msg, context)
        progress_update(str): Emitted during long operations with status messages

    Example:
        ```python
        pandoc_worker = PandocWorker()
        pandoc_thread = QThread()
        pandoc_worker.moveToThread(pandoc_thread)
        pandoc_thread.start()

        pandoc_worker.conversion_complete.connect(self._on_conversion_done)
        pandoc_worker.run_pandoc_conversion(
            source="# Markdown",
            to_format="asciidoc",
            from_format="markdown",
            context="import",
            use_ai_conversion=True
        )
        ```
    """

    conversion_complete = Signal(str, str)
    conversion_error = Signal(str, str)
    progress_update = Signal(str)

    @Slot(object, str, str, str, object, bool)
    def run_pandoc_conversion(
        self,
        source: Union[str, bytes, Path],
        to_format: str,
        from_format: str,
        context: str,
        output_file: Optional[Path] = None,
        use_ai_conversion: bool = False,
    ) -> None:
        """
        Execute document format conversion using Pandoc.

        This method runs in the worker thread. Never blocks the UI.

        Args:
            source: Document content (str/bytes) or Path to file
            to_format: Target format (asciidoc, html, docx, pdf, markdown, latex)
            from_format: Source format (markdown, docx, html, latex, rst)
            context: Context string for logging/signals (e.g., "import", "export")
            output_file: Path for binary output (pdf, docx), None for text output
            use_ai_conversion: Ignored (kept for API compatibility)

        Emits:
            conversion_complete: On success with (result_text, context)
            conversion_error: On failure with (error_msg, context)
            progress_update: Progress messages during operation

        Conversion Strategy:
            1. Use Pandoc for conversion
            2. Post-process AsciiDoc output for quality
        """
        # AI conversion removed - using Ollama for local AI features instead

        # Pandoc conversion path
        if not PANDOC_AVAILABLE or not pypandoc:
            err = "Pandoc/pypandoc not available for conversion."
            logger.error(err)
            self.conversion_error.emit(err, context)
            return

        try:
            logger.info(f"Starting Pandoc conversion ({context})")

            # Base Pandoc arguments
            extra_args = [
                "--wrap=preserve",
                "--reference-links",
                "--standalone",
                "--toc-depth=3",
            ]

            # Format-specific arguments
            if from_format == "docx":
                extra_args.extend(
                    [
                        "--extract-media=.",
                    ]
                )

            if to_format == "pdf":
                # PDF-specific arguments
                extra_args.extend(
                    [
                        "--variable=geometry:margin=1in",
                        "--variable=fontsize=11pt",
                        "--highlight-style=tango",
                    ]
                )

                # Detect available PDF engine
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

                pdf_engine_found = False
                for engine in pdf_engines:
                    try:
                        subprocess.run(
                            [engine, "--version"], capture_output=True, check=True
                        )
                        extra_args.append(f"--pdf-engine={engine}")
                        logger.info(f"Using PDF engine: {engine}")
                        pdf_engine_found = True
                        break
                    except (
                        FileNotFoundError,
                        subprocess.CalledProcessError,
                        Exception,
                    ):
                        continue

                if not pdf_engine_found:
                    # No PDF engine available - this should not happen in production
                    logger.error(
                        "No PDF engine found. Install wkhtmltopdf, weasyprint, or pdflatex."
                    )
                    raise RuntimeError(
                        "PDF conversion requires a PDF engine. "
                        "Install wkhtmltopdf: sudo apt-get install wkhtmltopdf"
                    )
            elif to_format == "docx":
                # DOCX-specific arguments (currently none)
                pass
            elif to_format == "markdown":
                extra_args.extend(
                    [
                        "--wrap=none",
                    ]
                )

            # Execute conversion
            if output_file and to_format in ["pdf", "docx"]:
                # Binary output to file
                if isinstance(source, Path):
                    pypandoc.convert_file(
                        source_file=str(source),
                        to=to_format,
                        format=from_format,
                        outputfile=str(output_file),
                        extra_args=extra_args,
                    )
                else:
                    # Source is str or bytes
                    pypandoc.convert_text(
                        source=source,
                        to=to_format,
                        format=from_format,
                        outputfile=str(output_file),
                        extra_args=extra_args,
                    )
                result_text = f"File saved to: {output_file}"
            else:
                # Text output (load into editor)
                if isinstance(source, Path):
                    source_content = source.read_text(encoding="utf-8")
                    converted = pypandoc.convert_text(
                        source=source_content,
                        to=to_format,
                        format=from_format,
                        extra_args=extra_args,
                    )
                elif isinstance(source, bytes):
                    # Binary content (like DOCX) - save to temp file and use convert_file
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{from_format}") as tmp:
                        tmp.write(source)
                        tmp_path = tmp.name
                    try:
                        converted = pypandoc.convert_file(
                            source_file=tmp_path,
                            to=to_format,
                            format=from_format,
                            extra_args=extra_args,
                        )
                    finally:
                        import os
                        os.unlink(tmp_path)
                else:
                    source_content = str(source)
                    converted = pypandoc.convert_text(
                        source=source_content,
                        to=to_format,
                        format=from_format,
                        extra_args=extra_args,
                    )
                if isinstance(converted, bytes):
                    result_text = converted.decode("utf-8")
                else:
                    result_text = str(converted)

                # Post-process AsciiDoc output
                if to_format == "asciidoc":
                    result_text = self._enhance_asciidoc_output(result_text)

            logger.info(f"Pandoc conversion successful ({context})")
            self.conversion_complete.emit(result_text, context)

        except Exception as e:
            logger.exception(f"Pandoc conversion failed: {context}")
            self.conversion_error.emit(str(e), context)

    def _enhance_asciidoc_output(self, text: str) -> str:
        """
        Post-process AsciiDoc output for better quality.

        Improvements:
        - Add document title if missing
        - Fix source block attributes
        - Add proper spacing around headings
        - Clean up table syntax
        - Format admonition blocks

        Args:
            text: Raw AsciiDoc output from Pandoc

        Returns:
            Enhanced AsciiDoc with better formatting
        """
        # Add document title if missing
        if not text.strip().startswith("="):
            lines = text.strip().split("\n")

            # Try to find first heading to use as title
            for i, line in enumerate(lines):
                if line.startswith("=="):
                    title = line[2:].strip()
                    lines.insert(0, f"= {title}\n")
                    lines[i + 1] = line
                    break
            else:
                # No heading found, add generic title
                lines.insert(0, "= Converted Document\n")
            text = "\n".join(lines)

        # Fix source block attributes: [source]python -> [source,python]
        text = re.sub(r"\[source\](\w+)", r"[source,\1]", text)

        # Add spacing around headings
        text = re.sub(r"\n(=+\s+[^\n]+)\n(?!=)", r"\n\n\1\n", text)

        # Clean up table syntax
        text = re.sub(r"\|===\n\n", r"|===\n", text)

        # Format admonition blocks
        text = re.sub(r"(?m)^(NOTE|TIP|IMPORTANT|WARNING|CAUTION):\s*", r"\n\1: ", text)

        return text
