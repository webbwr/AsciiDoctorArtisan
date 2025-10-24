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

        Args:
            source_text: AsciiDoc source content to render

        Emits:
            render_complete(str): HTML content on successful render
            render_error(str): Error HTML on render failure

        Behavior:
            - If AsciiDoc API not initialized: Returns escaped source as <pre>
            - If rendering succeeds: Emits HTML body content
            - If rendering fails: Emits red error message HTML

        Performance:
            Typical rendering time: <350ms (NFR-001)
            Main window handles debouncing (350ms delay, FR-004)
        """
        try:
            if self._asciidoc_api is None:
                # Fallback: Display source as plain text if AsciiDoc unavailable
                html_body = f"<pre>{html.escape(source_text)}</pre>"
                self.render_complete.emit(html_body)
                return

            # Render AsciiDoc to HTML using in-memory streams
            infile = io.StringIO(source_text)
            outfile = io.StringIO()
            self._asciidoc_api.execute(infile, outfile, backend="html5")
            html_body = outfile.getvalue()

            logger.debug("PreviewWorker: Rendering successful")
            self.render_complete.emit(html_body)

        except Exception as exc:
            # Render error as HTML for display in preview pane
            error_html = (
                f"<div style='color:red'>Render Error: {html.escape(str(exc))}</div>"
            )
            logger.error(f"PreviewWorker: Rendering failed: {exc}")
            self.render_error.emit(error_html)
