"""
Pandoc Executor - Handles Pandoc subprocess execution for document conversion.

Extracted from PandocWorker to reduce class size (MA principle).
Handles conversion execution for different source types (str, bytes, Path) and output formats.
"""

import os
import tempfile
from pathlib import Path
from typing import Protocol

import pypandoc


class OutputEnhancer(Protocol):
    """Protocol for output enhancement (e.g., AsciiDoc post-processing)."""

    def _enhance_asciidoc_output(self, text: str) -> str:  # pragma: no cover
        """Enhance AsciiDoc output with formatting fixes."""
        ...


class PandocExecutor:
    """
    Handles Pandoc subprocess execution for document conversion.

    This class was extracted from PandocWorker to reduce class size
    per MA principle (623→~454 lines).

    Handles:
    - Binary format conversion (PDF, DOCX) to file
    - Text conversion from Path sources
    - Text conversion from bytes sources
    - Text conversion from string sources
    - Conversion orchestration based on source/output types
    """

    def __init__(self, output_enhancer: OutputEnhancer | None = None) -> None:
        """
        Initialize the Pandoc executor.

        Args:
            output_enhancer: Optional enhancer for output post-processing
        """
        self.output_enhancer = output_enhancer

    def convert_binary_to_file(
        self,
        source: str | bytes | Path,
        to_format: str,
        from_format: str,
        output_file: Path,
        extra_args: list[str],
    ) -> str:
        """
        Convert to binary format (PDF/DOCX) and save to file.

        Args:
            source: Document content or Path to file
            to_format: Target format (pdf or docx)
            from_format: Source format
            output_file: Output file path
            extra_args: Pandoc command-line arguments

        Returns:
            Status message indicating file location
        """
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
        return f"File saved to: {output_file}"

    def convert_path_source_to_text(
        self, source: Path, to_format: str, from_format: str, extra_args: list[str]
    ) -> str:
        """
        Convert Path source to text output.

        Args:
            source: Path to source file
            to_format: Target format
            from_format: Source format
            extra_args: Pandoc command-line arguments

        Returns:
            Converted text content
        """
        source_content = source.read_text(encoding="utf-8")
        converted = pypandoc.convert_text(
            source=source_content,
            to=to_format,
            format=from_format,
            extra_args=extra_args,
        )
        return str(converted) if not isinstance(converted, bytes) else converted.decode("utf-8")

    def convert_bytes_source_to_text(
        self, source: bytes, to_format: str, from_format: str, extra_args: list[str]
    ) -> str:
        """
        Convert bytes source to text output using temp file.

        Args:
            source: Binary document content
            to_format: Target format
            from_format: Source format
            extra_args: Pandoc command-line arguments

        Returns:
            Converted text content
        """
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
            return str(converted) if not isinstance(converted, bytes) else converted.decode("utf-8")
        finally:
            os.unlink(tmp_path)

    def convert_str_source_to_text(
        self, source: str, to_format: str, from_format: str, extra_args: list[str]
    ) -> str:
        """
        Convert string source to text output.

        Args:
            source: String document content
            to_format: Target format
            from_format: Source format
            extra_args: Pandoc command-line arguments

        Returns:
            Converted text content
        """
        converted = pypandoc.convert_text(
            source=source,
            to=to_format,
            format=from_format,
            extra_args=extra_args,
        )
        return str(converted) if not isinstance(converted, bytes) else converted.decode("utf-8")

    def execute_pandoc_conversion(
        self,
        source: str | bytes | Path,
        to_format: str,
        from_format: str,
        output_file: Path | None,
        extra_args: list[str],
    ) -> str:
        """
        Execute Pandoc conversion with the given parameters.

        Args:
            source: Document content or Path to file
            to_format: Target format
            from_format: Source format
            output_file: Output file path for binary formats (None for text output)
            extra_args: Pandoc command-line arguments

        Returns:
            Result text (converted content or status message)
        """
        # Binary output to file (PDF/DOCX)
        if output_file and to_format in ["pdf", "docx"]:
            return self.convert_binary_to_file(source, to_format, from_format, output_file, extra_args)

        # Text output - route by source type
        if isinstance(source, Path):
            result_text = self.convert_path_source_to_text(source, to_format, from_format, extra_args)
        elif isinstance(source, bytes):
            result_text = self.convert_bytes_source_to_text(source, to_format, from_format, extra_args)
        else:
            result_text = self.convert_str_source_to_text(str(source), to_format, from_format, extra_args)

        # Post-process AsciiDoc output
        if to_format == "asciidoc" and self.output_enhancer:
            result_text = self.output_enhancer._enhance_asciidoc_output(result_text)

        return result_text
