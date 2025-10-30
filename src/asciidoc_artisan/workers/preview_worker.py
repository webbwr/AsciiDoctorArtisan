"""
Preview Worker - Background thread for AsciiDoc HTML rendering.

This module provides the PreviewWorker class which renders AsciiDoc content
to HTML in a background QThread to prevent UI blocking during live preview.

Implements:
- FR-002: Live HTML preview display
- FR-003: Automatic preview updates
- FR-004: Debounced updates (handled by main window)
- FR-010: Background rendering to prevent UI blocking
- NFR-001: Preview updates <350ms (95th percentile)
- NFR-005: Long-running operations in background threads

The worker maintains an AsciiDoc3API instance and renders documents
asynchronously, emitting signals when rendering completes or fails.
"""

import html
import io
import logging
import time
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal, Slot

# Check for AsciiDoc3 availability
try:
    from asciidoc3 import asciidoc3
    from asciidoc3.asciidoc3api import AsciiDoc3API

    ASCIIDOC3_AVAILABLE = True
except ImportError:
    asciidoc3 = None
    AsciiDoc3API = None
    ASCIIDOC3_AVAILABLE = False

# Import incremental renderer
try:
    from asciidoc_artisan.workers.incremental_renderer import IncrementalPreviewRenderer

    INCREMENTAL_RENDERER_AVAILABLE = True
except ImportError:
    IncrementalPreviewRenderer = None  # type: ignore[assignment, misc]
    INCREMENTAL_RENDERER_AVAILABLE = False

# Import predictive renderer (v1.6.0)
try:
    from asciidoc_artisan.workers.predictive_renderer import (
        PredictivePreviewRenderer,
        PredictiveRenderer,
    )

    PREDICTIVE_RENDERER_AVAILABLE = True
except ImportError:
    PredictiveRenderer = None  # type: ignore[assignment, misc]
    PredictivePreviewRenderer = None  # type: ignore[assignment, misc]
    PREDICTIVE_RENDERER_AVAILABLE = False

# Import metrics
try:
    from asciidoc_artisan.core.metrics import get_metrics_collector

    METRICS_AVAILABLE = True
except ImportError:
    get_metrics_collector = None  # type: ignore[assignment]
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)


class PreviewWorker(QObject):
    """
    Worker thread for rendering AsciiDoc preview without blocking UI.

    Maintains an AsciiDoc3API instance and renders documents in a background
    thread, emitting signals when rendering completes or encounters errors.

    Implements FR-010: Background worker thread prevents UI blocking.
    Supports NFR-001: Rendering typically completes in <350ms.

    Signals:
        render_complete(str): Emitted with HTML content on successful render
        render_error(str): Emitted with error HTML on render failure

    Example:
        ```python
        preview_worker = PreviewWorker()
        preview_thread = QThread()
        preview_worker.moveToThread(preview_thread)
        preview_thread.start()

        preview_worker.initialize_asciidoc(asciidoc3.__file__)
        preview_worker.render_complete.connect(self._update_preview)
        preview_worker.render_preview("= My Document\\n\\nContent here")
        ```
    """

    render_complete = Signal(str)
    render_error = Signal(str)

    def __init__(self) -> None:
        """Initialize PreviewWorker with uninitialized AsciiDoc API."""
        super().__init__()
        self._asciidoc_api: Optional[Any] = None
        self._incremental_renderer: Optional[Any] = None
        self._use_incremental = True  # Enable incremental rendering by default
        self._predictive_renderer: Optional[Any] = None  # v1.6.0: Predictive rendering
        self._use_predictive = True  # Enable predictive rendering by default

    def initialize_asciidoc(self, asciidoc_module_file: str) -> None:
        """
        Initialize AsciiDoc API in worker thread.

        Must be called after worker is moved to thread, before any rendering.
        Configures AsciiDoc attributes for optimal preview rendering.

        Args:
            asciidoc_module_file: Path to asciidoc3 module (from asciidoc3.__file__)

        Configured Attributes:
            - icons: font (use Font Awesome icons)
            - source-highlighter: highlight.js (syntax highlighting)
            - toc: left (table of contents on left side)
            - sectanchors: enabled (section anchor links)
            - sectnums: enabled (section numbering)
            - imagesdir: . (relative image directory)

        Note:
            Uses --no-header-footer option to render body content only,
            allowing main window to provide HTML wrapper with styles.
        """
        if ASCIIDOC3_AVAILABLE and AsciiDoc3API and asciidoc3:
            try:
                self._asciidoc_api = AsciiDoc3API(asciidoc_module_file)

                # Render body only (main window provides HTML wrapper)
                self._asciidoc_api.options("--no-header-footer")

                # Configure rendering attributes
                self._asciidoc_api.attributes["icons"] = "font"
                self._asciidoc_api.attributes["source-highlighter"] = "highlight.js"
                self._asciidoc_api.attributes["toc"] = "left"
                self._asciidoc_api.attributes["sectanchors"] = ""
                self._asciidoc_api.attributes["sectnums"] = ""
                self._asciidoc_api.attributes["imagesdir"] = "."

                # Initialize incremental renderer if available
                if INCREMENTAL_RENDERER_AVAILABLE and IncrementalPreviewRenderer:  # type: ignore[truthy-function]
                    self._incremental_renderer = IncrementalPreviewRenderer(
                        self._asciidoc_api
                    )
                    logger.debug("PreviewWorker: Incremental renderer initialized")

                    # Initialize predictive renderer if available (v1.6.0)
                    if PREDICTIVE_RENDERER_AVAILABLE and PredictivePreviewRenderer:  # type: ignore[truthy-function]
                        self._predictive_renderer = PredictivePreviewRenderer(
                            self._incremental_renderer
                        )
                        logger.debug("PreviewWorker: Predictive renderer initialized")

                logger.debug("PreviewWorker: AsciiDoc API initialized")
            except Exception as exc:
                logger.error(
                    f"PreviewWorker: AsciiDoc API initialization failed: {exc}"
                )

    @Slot(str)
    def render_preview(self, source_text: str) -> None:
        """
        Render AsciiDoc source to HTML in background thread.

        This method runs in the worker thread. Never blocks the UI.
        Emits render_complete or render_error signal when done.

        Uses incremental rendering when available for better performance.

        Args:
            source_text: AsciiDoc source content to render

        Emits:
            render_complete(str): HTML content on successful render
            render_error(str): Error HTML on render failure

        Behavior:
            - If AsciiDoc API not initialized: Returns escaped source as <pre>
            - If incremental renderer available: Uses block-based caching
            - If rendering succeeds: Emits HTML body content
            - If rendering fails: Emits red error message HTML

        Performance:
            Incremental rendering: 3-5x faster for minor edits
            Typical rendering time: <350ms (NFR-001)
            Main window handles debouncing (350ms delay, FR-004)
            Metrics tracked: preview_render_full, preview_render_incremental
        """
        start_time = time.perf_counter()
        render_type = "full"

        try:
            if self._asciidoc_api is None:
                # Fallback: Display source as plain text if AsciiDoc unavailable
                html_body = f"<pre>{html.escape(source_text)}</pre>"
                self.render_complete.emit(html_body)
                return

            # Use incremental renderer if available and enabled
            if (
                self._use_incremental
                and self._incremental_renderer is not None
                and len(source_text) > 1000
            ):  # Only for larger docs
                render_type = "incremental"
                html_body = self._incremental_renderer.render(source_text)
                logger.debug("PreviewWorker: Incremental rendering successful")
            else:
                # Full render for small documents
                infile = io.StringIO(source_text)
                outfile = io.StringIO()
                self._asciidoc_api.execute(infile, outfile, backend="html5")
                html_body = outfile.getvalue()
                logger.debug("PreviewWorker: Full rendering successful")

            # Record metrics
            if METRICS_AVAILABLE and get_metrics_collector:
                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics = get_metrics_collector()
                metrics.record_operation(f"preview_render_{render_type}", duration_ms)

            self.render_complete.emit(html_body)

        except Exception as exc:
            # Render error as HTML for display in preview pane
            error_html = (
                f"<div style='color:red'>Render Error: {html.escape(str(exc))}</div>"
            )
            logger.error(f"PreviewWorker: Rendering failed: {exc}")
            self.render_error.emit(error_html)

    def set_incremental_rendering(self, enabled: bool) -> None:
        """
        Enable or disable incremental rendering.

        Args:
            enabled: True to enable, False to disable
        """
        self._use_incremental = enabled
        if self._incremental_renderer:
            self._incremental_renderer.enable(enabled)
        logger.info(f"Incremental rendering {'enabled' if enabled else 'disabled'}")

    def set_predictive_rendering(self, enabled: bool) -> None:
        """
        Enable or disable predictive rendering (v1.6.0).

        Args:
            enabled: True to enable, False to disable
        """
        self._use_predictive = enabled
        if self._predictive_renderer:
            self._predictive_renderer.enable(enabled)
        logger.info(f"Predictive rendering {'enabled' if enabled else 'disabled'}")

    def update_cursor_position(self, line_number: int) -> None:
        """
        Update cursor position for predictive rendering (v1.6.0).

        Args:
            line_number: Current cursor line number (0-indexed)
        """
        if self._predictive_renderer:
            self._predictive_renderer.update_cursor_position(line_number)

    def request_prediction(self, source_text: str, cursor_line: int) -> None:
        """
        Request predictive pre-rendering during debounce period (v1.6.0).

        Splits document into blocks, determines current block from cursor,
        and requests prediction for pre-rendering.

        Args:
            source_text: Current document text
            cursor_line: Current cursor line number (0-indexed)
        """
        if not self._use_predictive or not self._predictive_renderer:
            return

        try:
            # Import block splitter
            from asciidoc_artisan.workers.incremental_renderer import (
                DocumentBlockSplitter,
            )

            # Split document into blocks
            blocks = DocumentBlockSplitter.split(source_text)
            if not blocks:
                return

            # Find block containing cursor line
            current_block_index = 0
            for i, block in enumerate(blocks):
                if block.start_line <= cursor_line <= block.end_line:
                    current_block_index = i
                    break

            # Request prediction
            self._predictive_renderer.request_prediction(
                total_blocks=len(blocks), current_block=current_block_index
            )

            logger.debug(
                f"Prediction requested: {len(blocks)} blocks, cursor at block {current_block_index}"
            )

            # Schedule pre-rendering during debounce period
            self._schedule_prerender(blocks)

        except Exception as exc:
            logger.warning(f"Prediction request failed: {exc}")

    def _schedule_prerender(self, blocks: list, max_blocks: int = 3) -> None:
        """
        Schedule pre-rendering of predicted blocks (v1.6.0).

        Pre-renders up to max_blocks from the prediction queue during
        the debounce period for reduced latency.

        Args:
            blocks: List of DocumentBlock objects
            max_blocks: Maximum blocks to pre-render (default: 3)
        """
        if not self._predictive_renderer or not self._incremental_renderer:
            return

        prerendered_count = 0

        try:
            # Pre-render multiple blocks from queue (up to max_blocks)
            while prerendered_count < max_blocks:
                # Get next block to pre-render from prediction queue
                block_index = self._predictive_renderer.get_next_prerender_block()

                if block_index is None or block_index >= len(blocks):
                    break  # No more blocks in queue

                block = blocks[block_index]

                # Skip if already cached
                if self._incremental_renderer.cache.get(block.id) is not None:
                    logger.debug(f"Block {block_index} already cached, skipping")
                    continue

                # Pre-render the block
                rendered_html = self._incremental_renderer._render_block(block)

                # Cache it for later use
                self._incremental_renderer.cache.put(block.id, rendered_html)

                # Record prediction was used
                self._predictive_renderer.predictor.record_prediction_used(block_index)

                prerendered_count += 1

                logger.debug(
                    f"Pre-rendered block {block_index} "
                    f"(size: {len(block.content)} chars, {prerendered_count}/{max_blocks})"
                )

            if prerendered_count > 0:
                logger.debug(
                    f"Pre-rendering complete: {prerendered_count} blocks cached"
                )

        except Exception as exc:
            logger.debug(f"Pre-render failed: {exc}")

    def get_predictive_stats(self) -> dict:
        """
        Get predictive rendering statistics (v1.6.0).

        Returns:
            Dictionary with prediction stats, or empty dict if not available
        """
        if self._predictive_renderer:
            return self._predictive_renderer.get_statistics()
        return {}

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics from incremental renderer.

        Returns:
            Dictionary with cache stats, or empty dict if not available
        """
        if self._incremental_renderer:
            return self._incremental_renderer.get_cache_stats()
        return {}

    def clear_cache(self) -> None:
        """Clear the incremental renderer cache."""
        if self._incremental_renderer:
            self._incremental_renderer.clear_cache()
            logger.debug("Incremental renderer cache cleared")
