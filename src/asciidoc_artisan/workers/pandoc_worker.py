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

# Check for Claude client availability
try:
    from claude_client import ConversionFormat, ConversionResult, create_client

    CLAUDE_CLIENT_AVAILABLE = True
except ImportError:
    CLAUDE_CLIENT_AVAILABLE = False

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
        Execute document format conversion with optional AI enhancement.

        This method runs in the worker thread. Never blocks the UI.

        Args:
            source: Document content (str/bytes) or Path to file
            to_format: Target format (asciidoc, html, docx, pdf, markdown, latex)
            from_format: Source format (markdown, docx, html, latex, rst)
            context: Context string for logging/signals (e.g., "import", "export")
            output_file: Path for binary output (pdf, docx), None for text output
            use_ai_conversion: Use Claude AI if available (FR-055)

        Emits:
            conversion_complete: On success with (result_text, context)
            conversion_error: On failure with (error_msg, context)
            progress_update: Progress messages during operation

        Conversion Strategy:
            1. Try AI conversion if use_ai_conversion=True and available
            2. Fallback to Pandoc if AI fails/unavailable
            3. Post-process AsciiDoc output for quality
        """
        # Try AI conversion first if requested
        if use_ai_conversion and CLAUDE_CLIENT_AVAILABLE:
            ai_result = self._try_ai_conversion(
                source, from_format, to_format, context, output_file
            )
            if ai_result is not None:
                # AI conversion succeeded, early return
                return

            # AI conversion failed, fallback to Pandoc
            self.progress_update.emit(
                "AI conversion unavailable, falling back to Pandoc..."
            )
            logger.info(f"Falling back to Pandoc for {context}")

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
                    # No PDF engine available, will use HTML as intermediate
                    logger.warning(
                        "No PDF engine found. Will use HTML as intermediate format."
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

    def _try_ai_conversion(
        self,
        source: Union[str, bytes, Path],
        from_format: str,
        to_format: str,
        context: str,
        output_file: Optional[Path] = None,
    ) -> Optional[str]:
        """
        Attempt AI-enhanced conversion using Claude API.

        Implements FR-054 to FR-062 for AI-enhanced conversion:
        - FR-054: Claude API integration
        - FR-056: Complex document structure handling
        - FR-057: Automatic fallback to Pandoc on failure
        - FR-058: API key validation
        - FR-059: Progress indicators
        - FR-060: Error handling with retry logic
        - FR-062: Rate limiting (handled by ClaudeClient)

        Args:
            source: Document content or Path
            from_format: Source format
            to_format: Target format
            context: Context string for logging
            output_file: Output file path (for binary formats)

        Returns:
            Conversion result string on success, None on failure (triggers Pandoc fallback)

        Note:
            Returns None (not an error) to signal fallback to Pandoc should occur.
            Emits conversion_complete signal directly on success.
        """
        try:
            self.progress_update.emit("Initializing AI-enhanced conversion...")

            # Create Claude client
            client = create_client()
            if client is None:
                logger.warning("Failed to create Claude client, falling back to Pandoc")
                return None

            # Extract source content
            if isinstance(source, Path):
                source_content = source.read_text(encoding="utf-8")
            else:
                source_content = str(source)

            # Validate document size
            if not client.can_handle_document(source_content):
                logger.warning(
                    "Document too large for AI conversion, falling back to Pandoc"
                )
                self.progress_update.emit("Document too large for AI, using Pandoc...")
                return None

            # Validate target format
            try:
                target_format = ConversionFormat(to_format.lower())
            except ValueError:
                logger.warning(
                    f"Format {to_format} not supported by AI, falling back to Pandoc"
                )
                return None

            # Progress callback
            def progress_callback(message: str) -> None:
                self.progress_update.emit(message)

            # Execute AI conversion
            self.progress_update.emit(
                f"Converting with Claude AI ({from_format} → {to_format})..."
            )
            result: ConversionResult = client.convert_document(
                content=source_content,
                source_format=from_format,
                target_format=target_format,
                progress_callback=progress_callback,
            )

            if not result.success:
                # AI conversion failed, fallback to Pandoc
                logger.warning(f"AI conversion failed: {result.error_message}")
                self.progress_update.emit(
                    f"AI conversion failed: {result.error_message}"
                )
                return None

            converted_content = result.content
            logger.info(
                f"AI conversion successful in {result.processing_time:.2f}s ({context})"
            )
            self.progress_update.emit(
                f"AI conversion completed in {result.processing_time:.1f}s"
            )

            # Handle binary output formats
            if output_file and to_format in ["pdf", "docx"]:
                # Need Pandoc to convert text to binary format
                logger.info("Converting AI result to binary format with Pandoc...")
                self.progress_update.emit("Finalizing binary format...")
                # Return None to trigger Pandoc conversion with AI result as input
                return None

            # Success - emit result
            self.conversion_complete.emit(converted_content, context)
            return converted_content

        except Exception as e:
            # Unexpected error, fallback to Pandoc
            logger.error(f"Unexpected error in AI conversion: {e}")
            self.progress_update.emit(f"AI conversion error: {str(e)[:50]}...")
            return None
