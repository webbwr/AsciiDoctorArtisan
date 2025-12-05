"""Virtual Scrolling Preview - Render only visible portions for large documents."""

import logging
from dataclasses import dataclass
from typing import Any

from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Viewport:
    """
    Visible viewport information.

    Uses __slots__ for memory efficiency.
    """

    # Scroll position (pixels)
    scroll_x: int
    scroll_y: int

    # Viewport size (pixels)
    width: int
    height: int

    # Document size (pixels)
    document_width: int
    document_height: int

    # Line height (pixels, average)
    line_height: int

    def get_visible_line_range(self, buffer_lines: int = 10) -> tuple[int, int]:
        """
        Calculate visible line range with buffer.

        Args:
            buffer_lines: Extra lines to render above/below viewport

        Returns:
            Tuple of (start_line, end_line)
        """
        if self.line_height <= 0:
            return (0, 0)

        # Calculate visible lines
        start_line = max(0, self.scroll_y // self.line_height - buffer_lines)
        visible_lines = (self.height // self.line_height) + 1
        end_line = start_line + visible_lines + (2 * buffer_lines)

        return (start_line, end_line)

    def is_line_visible(self, line_number: int, buffer_lines: int = 10) -> bool:
        """
        Check if line is in visible range.

        Args:
            line_number: Line number to check
            buffer_lines: Buffer size

        Returns:
            True if line is visible (with buffer)
        """
        start, end = self.get_visible_line_range(buffer_lines)
        return start <= line_number <= end


@dataclass(slots=True)
class VirtualScrollConfig:
    """
    Configuration for virtual scrolling.

    Uses __slots__ for memory efficiency.
    """

    # Buffer size (lines above/below viewport)
    buffer_lines: int = 10

    # Minimum document size to enable virtual scrolling
    min_lines_for_virtual: int = 500

    # Estimated line height (pixels)
    # Will be refined based on actual rendering
    estimated_line_height: int = 20

    # Maximum lines to render at once
    max_render_lines: int = 1000


class VirtualScrollPreview:
    """
    Virtual scrolling preview renderer.

    Renders only visible portions of large documents:
    1. Calculate viewport based on scroll position
    2. Determine visible line range (with buffer)
    3. Extract visible source lines
    4. Render only visible portion
    5. Position rendered content correctly

    Example:
        renderer = VirtualScrollPreview(asciidoc_api)

        # On scroll or content change
        viewport = Viewport(
            scroll_x=0,
            scroll_y=500,
            width=800,
            height=600,
            document_width=800,
            document_height=10000,
            line_height=20
        )

        html = renderer.render_viewport(source_text, viewport)
        # Only renders visible lines + buffer
    """

    def __init__(self, asciidoc_api: Any, config: VirtualScrollConfig | None = None):
        """
        Initialize virtual scroll preview.

        Args:
            asciidoc_api: AsciiDoc3API instance for rendering
            config: Optional configuration
        """
        self.asciidoc_api = asciidoc_api
        self.config = config or VirtualScrollConfig()
        self._enabled = True

        # Tracking
        self._total_lines = 0
        self._rendered_lines = 0
        self._actual_line_height: int | None = None

    def is_enabled(self) -> bool:
        """Check if virtual scrolling is enabled."""
        return self._enabled

    def enable(self, enabled: bool = True) -> None:
        """
        Enable or disable virtual scrolling.

        Args:
            enabled: True to enable, False to disable
        """
        self._enabled = enabled
        logger.info(f"Virtual scrolling {'enabled' if enabled else 'disabled'}")

    def should_use_virtual_scrolling(self, source_text: str) -> bool:
        """
        Determine if virtual scrolling should be used.

        Args:
            source_text: Full document source

        Returns:
            True if document is large enough for virtual scrolling
        """
        if not self._enabled:
            return False

        line_count = source_text.count("\n") + 1
        return line_count >= self.config.min_lines_for_virtual

    def render_viewport(self, source_text: str, viewport: Viewport) -> tuple[str, int]:
        """
        Render only visible viewport.

        Args:
            source_text: Full document source
            viewport: Viewport information

        Returns:
            Tuple of (rendered_html, offset_pixels)
            offset_pixels is vertical offset for positioning
        """
        if not self.should_use_virtual_scrolling(source_text):
            # Fall back to full render for small documents
            html = self._render_full(source_text)
            return (html, 0)

        lines = source_text.split("\n")
        self._total_lines = len(lines)

        # Calculate visible range
        start_line, end_line = viewport.get_visible_line_range(self.config.buffer_lines)

        # Clamp to document bounds
        start_line = max(0, start_line)
        end_line = min(len(lines), end_line)

        # Extract visible lines
        visible_lines = lines[start_line:end_line]
        visible_source = "\n".join(visible_lines)

        self._rendered_lines = len(visible_lines)

        # Calculate vertical offset for positioning
        offset_pixels = start_line * viewport.line_height

        logger.debug(
            f"Virtual render: lines {start_line}-{end_line} "
            f"({self._rendered_lines}/{self._total_lines}, "
            f"{self._rendered_lines / self._total_lines * 100:.1f}%)"
        )

        # Render visible portion
        html = self._render_partial(visible_source, start_line)

        return (html, offset_pixels)

    def _render_partial(self, source: str, start_line: int) -> str:
        """
        Render partial document.

        Args:
            source: Source text to render
            start_line: Starting line number

        Returns:
            Rendered HTML
        """
        import html
        import io

        try:
            # Render using AsciiDoc API
            infile = io.StringIO(source)
            outfile = io.StringIO()
            self.asciidoc_api.execute(infile, outfile, backend="html5")
            result = outfile.getvalue()

            # Wrap in container with line number attribute for debugging
            return f'<div data-start-line="{start_line}">{result}</div>'

        except Exception as exc:
            logger.warning(f"Partial render failed: {exc}")
            # Return escaped content as fallback
            return f'<pre data-start-line="{start_line}">{html.escape(source)}</pre>'

    def _render_full(self, source: str) -> str:
        """
        Full document render (fallback for small documents).

        Args:
            source: Full document source

        Returns:
            Rendered HTML
        """
        import html
        import io

        try:
            infile = io.StringIO(source)
            outfile = io.StringIO()
            self.asciidoc_api.execute(infile, outfile, backend="html5")
            return outfile.getvalue()

        except Exception as exc:
            logger.error(f"Full render failed: {exc}")
            return f"<pre>{html.escape(source)}</pre>"

    def update_line_height(self, measured_height: int) -> None:
        """
        Update actual line height based on measurements.

        Args:
            measured_height: Measured line height in pixels
        """
        self._actual_line_height = measured_height
        logger.debug(f"Updated line height: {measured_height}px")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get virtual scrolling statistics.

        Returns:
            Dictionary with stats
        """
        render_ratio = self._rendered_lines / self._total_lines if self._total_lines > 0 else 0

        return {
            "enabled": self._enabled,
            "total_lines": self._total_lines,
            "rendered_lines": self._rendered_lines,
            "render_ratio": round(render_ratio * 100, 2),
            "estimated_line_height": self.config.estimated_line_height,
            "actual_line_height": self._actual_line_height,
        }


class ViewportCalculator:
    """
    Helper to calculate viewport from QWidget.

    Extracts viewport information from Qt widgets for virtual scrolling.
    """

    @staticmethod
    def calculate_from_widget(widget: QWidget, document_height: int, line_height: int = 20) -> Viewport:
        """
        Calculate viewport from Qt widget.

        Args:
            widget: QWidget to calculate viewport from
            document_height: Total document height in pixels
            line_height: Estimated line height

        Returns:
            Viewport object
        """
        # Get widget geometry
        geometry = widget.geometry()

        # Get scroll position (if widget has scrollbars)
        scroll_x = 0
        scroll_y = 0

        # Try to get scroll area if available
        from PySide6.QtWidgets import QAbstractScrollArea, QScrollArea

        parent = widget.parent()
        while parent:
            if isinstance(parent, (QScrollArea, QAbstractScrollArea)):
                # Found scroll area
                h_bar = parent.horizontalScrollBar()
                v_bar = parent.verticalScrollBar()

                if h_bar:
                    scroll_x = h_bar.value()
                if v_bar:
                    scroll_y = v_bar.value()

                break

            parent = parent.parent()

        return Viewport(
            scroll_x=scroll_x,
            scroll_y=scroll_y,
            width=geometry.width(),
            height=geometry.height(),
            document_width=geometry.width(),
            document_height=document_height,
            line_height=line_height,
        )

    @staticmethod
    def calculate_from_values(
        width: int,
        height: int,
        scroll_y: int = 0,
        document_height: int = 0,
        line_height: int = 20,
    ) -> Viewport:
        """
        Calculate viewport from values.

        Args:
            width: Viewport width
            height: Viewport height
            scroll_y: Vertical scroll position
            document_height: Total document height
            line_height: Line height

        Returns:
            Viewport object
        """
        return Viewport(
            scroll_x=0,
            scroll_y=scroll_y,
            width=width,
            height=height,
            document_width=width,
            document_height=document_height or height,
            line_height=line_height,
        )
