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
import time
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

# Lazy import check for Pandoc (deferred until first use for faster startup)
from asciidoc_artisan.core.constants import is_pandoc_available
from asciidoc_artisan.workers.asciidoc_enhancer import AsciiDocEnhancer
from asciidoc_artisan.workers.ollama_conversion_handler import OllamaConversionHandler
from asciidoc_artisan.workers.pandoc_args_builder import PandocArgsBuilder
from asciidoc_artisan.workers.pandoc_executor import PandocExecutor

# AI client removed - using Ollama for local AI features instead

# Import metrics
try:
    from asciidoc_artisan.core.metrics import get_metrics_collector

    METRICS_AVAILABLE = True
except ImportError:
    get_metrics_collector = None  # type: ignore[assignment]
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ConversionRequest:
    """
    Configuration for a document conversion operation.

    MA principle: Config object to reduce parameter count (8→3 params in
    _try_ai_conversion_with_fallback).

    Attributes:
        source: Document content (str/bytes) or Path to file
        to_format: Target format (e.g., 'html', 'pdf', 'docx')
        from_format: Source format (e.g., 'asciidoc', 'markdown')
        context: Context string for logging/signals
        output_file: Output file path (for binary formats like PDF/DOCX)
        use_ai_conversion: Whether AI-enhanced conversion is requested
    """

    source: str | bytes | Path
    to_format: str
    from_format: str
    context: str
    output_file: Path | None
    use_ai_conversion: bool



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

    def __init__(self) -> None:
        """Initialize PandocWorker."""
        super().__init__()
        self.ollama_model: str | None = None
        self.ollama_enabled: bool = False
        self._ollama_handler = OllamaConversionHandler(
            ollama_enabled=False,
            ollama_model=None,
            progress_signal=self.progress_update
        )
        self._args_builder = PandocArgsBuilder()
        self._asciidoc_enhancer = AsciiDocEnhancer()
        self._pandoc_executor = PandocExecutor(output_enhancer=self)

    def set_ollama_config(self, enabled: bool, model: str | None) -> None:
        """
        Set Ollama configuration for AI conversions.

        Args:
            enabled: Whether Ollama AI conversion is enabled
            model: Name of Ollama model to use
        """
        self.ollama_enabled = enabled
        self.ollama_model = model
        self._ollama_handler.ollama_enabled = enabled
        self._ollama_handler.ollama_model = model

    def _try_ai_conversion_with_fallback(
        self,
        request: ConversionRequest,
        start_time: float,
    ) -> tuple[str | None, str | bytes | Path, str]:
        """
        Attempt AI conversion with automatic fallback to source.

        MA principle: Reduced from 8→3 params using ConversionRequest config object (62% reduction).

        Args:
            request: Conversion configuration (source, formats, context, output_file, use_ai_conversion)
            start_time: Conversion start time (for metrics)

        Returns:
            Tuple of (result_or_none, updated_source, conversion_method)
            - If AI succeeds for text output: (result_text, source, "ollama")
            - If AI succeeds for binary output: (None, ollama_text, "ollama_pandoc")
            - If AI fails or not requested: (None, source, "pandoc")
        """
        conversion_method = "pandoc"

        # Try Ollama AI conversion first if requested
        if request.use_ai_conversion and self.ollama_enabled and self.ollama_model:
            # Get source content as string
            if isinstance(request.source, Path):
                source_content = request.source.read_text(encoding="utf-8")
            elif isinstance(request.source, bytes):
                source_content = request.source.decode("utf-8", errors="replace")
            else:
                source_content = str(request.source)

            # Try Ollama conversion
            try:
                ollama_result = self._try_ollama_conversion(source_content, request.from_format, request.to_format)

                if ollama_result:
                    # Ollama conversion succeeded
                    conversion_method = "ollama"
                    logger.info("Using Ollama AI conversion result")

                    # Handle output
                    if request.output_file and request.to_format in ["pdf", "docx"]:
                        # For binary formats, save the text and convert with Pandoc
                        # (Ollama can't directly create PDF/DOCX binaries)
                        logger.info(f"Ollama produced {request.to_format} markup, using Pandoc for binary output")
                        # Continue to Pandoc with Ollama's result as source
                        return None, ollama_result, "ollama_pandoc"
                    else:
                        # Text output - use Ollama result directly
                        # Record metrics
                        if METRICS_AVAILABLE:
                            duration_ms = (time.perf_counter() - start_time) * 1000
                            metrics = get_metrics_collector()
                            metrics.record_operation(f"conversion_{conversion_method}", duration_ms)

                        return ollama_result, request.source, conversion_method

                else:
                    logger.warning("Ollama conversion returned no result, falling back to Pandoc")

            except Exception as e:
                logger.warning(f"Ollama conversion failed, falling back to Pandoc: {e}")
                # Continue to Pandoc fallback

        return None, request.source, conversion_method

    def _detect_pdf_engine(self) -> str:
        """Detect PDF engine (delegates to args_builder)."""
        return self._args_builder.detect_pdf_engine()

    def _build_pandoc_args(self, from_format: str, to_format: str) -> list[str]:
        """Build Pandoc args (delegates to args_builder)."""
        return self._args_builder.build_pandoc_args(from_format, to_format)

    def _convert_binary_to_file(
        self,
        source: str | bytes | Path,
        to_format: str,
        from_format: str,
        output_file: Path,
        extra_args: list[str],
    ) -> str:
        """Convert to binary format (delegates to pandoc_executor)."""
        return self._pandoc_executor.convert_binary_to_file(source, to_format, from_format, output_file, extra_args)

    def _convert_path_source_to_text(
        self, source: Path, to_format: str, from_format: str, extra_args: list[str]
    ) -> str:
        """Convert Path source to text (delegates to pandoc_executor)."""
        return self._pandoc_executor.convert_path_source_to_text(source, to_format, from_format, extra_args)

    def _convert_bytes_source_to_text(
        self, source: bytes, to_format: str, from_format: str, extra_args: list[str]
    ) -> str:
        """Convert bytes source to text (delegates to pandoc_executor)."""
        return self._pandoc_executor.convert_bytes_source_to_text(source, to_format, from_format, extra_args)

    def _convert_str_source_to_text(self, source: str, to_format: str, from_format: str, extra_args: list[str]) -> str:
        """Convert string source to text (delegates to pandoc_executor)."""
        return self._pandoc_executor.convert_str_source_to_text(source, to_format, from_format, extra_args)

    def _execute_pandoc_conversion(
        self,
        source: str | bytes | Path,
        to_format: str,
        from_format: str,
        output_file: Path | None,
        extra_args: list[str],
    ) -> str:
        """Execute Pandoc conversion (delegates to pandoc_executor)."""
        return self._pandoc_executor.execute_pandoc_conversion(source, to_format, from_format, output_file, extra_args)

    @Slot(object, str, str, str, object, bool)
    def run_pandoc_conversion(
        self,
        source: str | bytes | Path,
        to_format: str,
        from_format: str,
        context: str,
        output_file: Path | None = None,
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
        start_time = time.perf_counter()

        # Try AI conversion with fallback
        request = ConversionRequest(
            source=source,
            to_format=to_format,
            from_format=from_format,
            context=context,
            output_file=output_file,
            use_ai_conversion=use_ai_conversion,
        )
        ai_result, source, conversion_method = self._try_ai_conversion_with_fallback(request, start_time)

        # If AI conversion completed successfully, we're done
        if ai_result is not None:
            self.conversion_complete.emit(ai_result, context)
            return

        # Pandoc conversion path (fallback or primary if AI not requested)
        # Check if Pandoc is available (pypandoc will be lazily imported in _execute_pandoc_conversion)
        if not is_pandoc_available():
            err = "Pandoc/pypandoc not available for conversion."
            logger.error(err)
            self.conversion_error.emit(err, context)
            return

        try:
            logger.info(f"Starting Pandoc conversion ({context})")

            # Build Pandoc arguments for format conversion
            extra_args = self._build_pandoc_args(from_format, to_format)

            # Execute Pandoc conversion
            result_text = self._execute_pandoc_conversion(source, to_format, from_format, output_file, extra_args)

            # Record metrics
            if METRICS_AVAILABLE:
                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics = get_metrics_collector()
                metrics.record_operation(f"conversion_{conversion_method}", duration_ms)

            logger.info(f"Pandoc conversion successful ({context})")
            self.conversion_complete.emit(result_text, context)

        except Exception as e:
            logger.exception(f"Pandoc conversion failed: {context}")
            self.conversion_error.emit(str(e), context)

    def _enhance_asciidoc_output(self, text: str) -> str:
        """Enhance AsciiDoc output (delegates to asciidoc_enhancer)."""
        return self._asciidoc_enhancer.enhance_asciidoc_output(text)

    def _try_ollama_conversion(self, source: str, from_format: str, to_format: str) -> str | None:
        """Attempt Ollama conversion (delegates to ollama_handler)."""
        return self._ollama_handler.try_ollama_conversion(source, from_format, to_format)

    def _get_format_display_names(self, from_format: str, to_format: str) -> tuple[str, str]:
        """Get format display names (delegates to ollama_handler)."""
        return self._ollama_handler.get_format_display_names(from_format, to_format)

    def _get_format_instructions(self, to_format: str, to_name: str) -> str:
        """Get format instructions (delegates to ollama_handler)."""
        return self._ollama_handler.get_format_instructions(to_format, to_name)

    def _create_conversion_prompt(self, source: str, from_format: str, to_format: str) -> str:
        """Create conversion prompt (delegates to ollama_handler)."""
        return self._ollama_handler.create_conversion_prompt(source, from_format, to_format)
