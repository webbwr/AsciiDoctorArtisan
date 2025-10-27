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

    Supports both Pandoc and Ollama AI-enhanced conversion.
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

    def __init__(self):
        """Initialize PandocWorker."""
        super().__init__()
        self.ollama_model = None
        self.ollama_enabled = False

    def set_ollama_config(self, enabled: bool, model: Optional[str]) -> None:
        """
        Set Ollama configuration for AI conversions.

        Args:
            enabled: Whether Ollama AI conversion is enabled
            model: Name of Ollama model to use
        """
        self.ollama_enabled = enabled
        self.ollama_model = model

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
            1. If use_ai_conversion=True -> Try Ollama AI conversion
            2. If Ollama fails or disabled -> Fallback to Pandoc
            3. Post-process AsciiDoc output for quality
        """
        # Try Ollama AI conversion first if requested
        if use_ai_conversion and self.ollama_enabled and self.ollama_model:
            # Get source content as string
            if isinstance(source, Path):
                source_content = source.read_text(encoding="utf-8")
            elif isinstance(source, bytes):
                source_content = source.decode("utf-8", errors="replace")
            else:
                source_content = str(source)

            # Try Ollama conversion
            try:
                ollama_result = self._try_ollama_conversion(
                    source_content, from_format, to_format
                )

                if ollama_result:
                    # Ollama conversion succeeded
                    logger.info("Using Ollama AI conversion result")

                    # Handle output
                    if output_file and to_format in ["pdf", "docx"]:
                        # For binary formats, save the text and convert with Pandoc
                        # (Ollama can't directly create PDF/DOCX binaries)
                        logger.info(
                            f"Ollama produced {to_format} markup, using Pandoc for binary output"
                        )
                        # Continue to Pandoc with Ollama's result as source
                        source = ollama_result
                    else:
                        # Text output - use Ollama result directly
                        if to_format.lower() in ["asciidoc", "adoc"]:
                            # Apply AsciiDoc post-processing
                            ollama_result = self._post_process_asciidoc(ollama_result)

                        self.conversion_complete.emit(ollama_result, context)
                        return

                else:
                    logger.warning(
                        "Ollama conversion returned no result, falling back to Pandoc"
                    )

            except Exception as e:
                logger.warning(f"Ollama conversion failed, falling back to Pandoc: {e}")
                # Continue to Pandoc fallback

        # Pandoc conversion path (fallback or primary if AI not requested)
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

                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=f".{from_format}"
                    ) as tmp:
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

    def _try_ollama_conversion(
        self, source: str, from_format: str, to_format: str
    ) -> Optional[str]:
        """
        Attempt document conversion using Ollama AI.

        Args:
            source: Source document content
            from_format: Source format (e.g., "markdown", "docx", "html")
            to_format: Target format (e.g., "asciidoc", "markdown")

        Returns:
            Converted document text if successful, None if failed

        Raises:
            Exception: If Ollama conversion fails (caller should fallback to Pandoc)
        """
        if not self.ollama_enabled or not self.ollama_model:
            logger.debug("Ollama conversion not enabled or model not set")
            return None

        try:
            import ollama

            logger.info(
                f"Attempting Ollama AI conversion: {from_format} -> {to_format} using {self.ollama_model}"
            )
            self.progress_update.emit(f"Converting with AI ({self.ollama_model})...")

            # Create conversion prompt
            prompt = self._create_conversion_prompt(source, from_format, to_format)

            # Call Ollama API
            response = ollama.generate(model=self.ollama_model, prompt=prompt)

            if not response or "response" not in response:
                logger.warning("Ollama returned empty or invalid response")
                return None

            converted_text = response["response"].strip()

            # Validate conversion
            if not converted_text or len(converted_text) < 10:
                logger.warning("Ollama conversion produced insufficient output")
                return None

            logger.info(
                f"Ollama conversion successful ({len(converted_text)} characters)"
            )
            return converted_text

        except ImportError:
            logger.error("Ollama library not available")
            return None
        except Exception as e:
            logger.error(f"Ollama conversion failed: {e}")
            return None

    def _create_conversion_prompt(
        self, source: str, from_format: str, to_format: str
    ) -> str:
        """
        Create a prompt for Ollama to convert between document formats.

        Args:
            source: Source document content
            from_format: Source format
            to_format: Target format

        Returns:
            Formatted prompt for Ollama
        """
        # Map format names to readable names
        format_names = {
            "markdown": "Markdown",
            "md": "Markdown",
            "asciidoc": "AsciiDoc",
            "adoc": "AsciiDoc",
            "html": "HTML",
            "docx": "Microsoft Word",
            "rst": "reStructuredText",
            "latex": "LaTeX",
            "org": "Org Mode",
        }

        from_name = format_names.get(from_format.lower(), from_format)
        to_name = format_names.get(to_format.lower(), to_format)

        # Create format-specific instructions
        if to_format.lower() in ["asciidoc", "adoc"]:
            format_instructions = """
AsciiDoc formatting rules:
- Use = for document title (level 0)
- Use == for level 1 headings, === for level 2, etc.
- Use *bold* for bold, _italic_ for italic
- Use [source,language] blocks for code
- Use `backticks` for inline code
- Use * or - for unordered lists
- Use . for ordered lists
- Use |=== for tables
- Use image::path[] for images
- Use link:url[text] for links
"""
        elif to_format.lower() in ["markdown", "md"]:
            format_instructions = """
Markdown formatting rules:
- Use # for h1, ## for h2, ### for h3, etc.
- Use **bold** for bold, *italic* for italic
- Use ```language blocks for code
- Use `backticks` for inline code
- Use - or * for unordered lists
- Use 1. for ordered lists
- Use | for tables
- Use ![alt](path) for images
- Use [text](url) for links
"""
        else:
            format_instructions = f"Follow standard {to_name} formatting conventions."

        prompt = f"""You are a document format conversion expert. Convert the following {from_name} document to {to_name} format.

{format_instructions}

IMPORTANT INSTRUCTIONS:
1. Convert ALL content from the source document
2. Preserve the document structure and hierarchy
3. Maintain all formatting (bold, italic, code, links, etc.)
4. Keep all tables, lists, and code blocks
5. Do NOT add explanations or comments
6. Output ONLY the converted document
7. Do NOT wrap the output in code blocks or markdown
8. Start immediately with the converted content

SOURCE DOCUMENT ({from_name}):
{source}

CONVERTED DOCUMENT ({to_name}):"""

        return prompt
