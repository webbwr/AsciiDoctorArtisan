"""
AI Conversion Coordinator - Orchestrates AI-enhanced conversion with Pandoc fallback.

Extracted from PandocWorker to reduce class size (MA principle).
Handles conversion strategy selection and result preparation.
"""

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:  # pragma: no cover
    from asciidoc_artisan.workers.pandoc_worker import ConversionRequest

logger = logging.getLogger(__name__)


class OllamaConverter(Protocol):
    """Protocol for Ollama conversion attempts."""

    def _try_ollama_conversion(self, source: str, from_format: str, to_format: str) -> str | None:  # pragma: no cover
        """Try Ollama conversion."""
        ...


class MetricsCollector(Protocol):
    """Protocol for metrics collection."""

    def record_operation(self, operation: str, duration_ms: float) -> None:  # pragma: no cover
        """Record operation metrics."""
        ...


class AIConversionCoordinator:
    """
    Coordinates AI-enhanced conversion with automatic Pandoc fallback.

    This class was extracted from PandocWorker to reduce class size
    per MA principle (354→~288 lines).

    Handles:
    - AI conversion attempts with Ollama
    - Fallback strategy selection
    - Result preparation for different output types
    - Metrics recording
    """

    def __init__(
        self,
        ollama_converter: OllamaConverter,
        ollama_enabled: bool,
        ollama_model: str | None,
        metrics_available: bool,
        get_metrics: Any,
    ) -> None:
        """
        Initialize the AI conversion coordinator.

        Args:
            ollama_converter: Object with _try_ollama_conversion method
            ollama_enabled: Whether Ollama is enabled
            ollama_model: Ollama model name
            metrics_available: Whether metrics collection is available
            get_metrics: Function to get metrics collector
        """
        self.ollama_converter = ollama_converter
        self.ollama_enabled = ollama_enabled
        self.ollama_model = ollama_model
        self.metrics_available = metrics_available
        self.get_metrics = get_metrics

    def try_ai_conversion_with_fallback(
        self,
        request: "ConversionRequest",
        start_time: float,
    ) -> tuple[str | None, str | bytes | Path, str]:
        """
        Attempt AI conversion with automatic fallback to source.

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
                ollama_result = self.ollama_converter._try_ollama_conversion(
                    source_content, request.from_format, request.to_format
                )

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
                        if self.metrics_available:
                            duration_ms = (time.perf_counter() - start_time) * 1000
                            metrics = self.get_metrics()
                            metrics.record_operation(f"conversion_{conversion_method}", duration_ms)

                        return ollama_result, request.source, conversion_method

                else:
                    logger.warning("Ollama conversion returned no result, falling back to Pandoc")

            except Exception as e:
                logger.warning(f"Ollama conversion failed, falling back to Pandoc: {e}")
                # Continue to Pandoc fallback

        return None, request.source, conversion_method
