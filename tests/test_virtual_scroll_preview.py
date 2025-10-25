"""
Tests for virtual scrolling preview.

Tests viewport calculation, partial rendering, and performance benefits.
"""

import pytest
from unittest.mock import Mock, MagicMock
from asciidoc_artisan.ui.virtual_scroll_preview import (
    Viewport,
    VirtualScrollConfig,
    VirtualScrollPreview,
    ViewportCalculator,
)


class TestViewport:
    """Test Viewport dataclass."""

    def test_viewport_creation(self):
        """Test creating viewport."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=100,
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=20
        )

        assert viewport.scroll_y == 100
        assert viewport.height == 600
        assert viewport.line_height == 20

    def test_get_visible_line_range_top(self):
        """Test visible line range at document top."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=20
        )

        start, end = viewport.get_visible_line_range(buffer_lines=10)

        # At top: 0 lines before
        assert start == 0
        # Visible: 600px / 20px = 30 lines + 1
        # Buffer: 10 before + 10 after = 20 lines
        # Total: 31 + 20 = 51 lines
        assert end == 51

    def test_get_visible_line_range_scrolled(self):
        """Test visible line range when scrolled."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=1000,  # Scrolled down
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=20
        )

        start, end = viewport.get_visible_line_range(buffer_lines=10)

        # Scroll position: 1000px / 20px = line 50
        # Buffer before: -10 lines = line 40
        assert start == 40

        # Visible: 31 lines (30 + 1)
        # End: 40 + 31 + 20 (buffer) = 91
        assert end == 91

    def test_get_visible_line_range_zero_line_height(self):
        """Test handling of zero line height."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=0  # Invalid
        )

        start, end = viewport.get_visible_line_range()
        assert start == 0
        assert end == 0

    def test_is_line_visible(self):
        """Test checking if line is visible."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=1000,
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=20
        )

        # Line in visible range (40-90)
        assert viewport.is_line_visible(50) is True
        assert viewport.is_line_visible(70) is True

        # Line outside visible range
        assert viewport.is_line_visible(10) is False
        assert viewport.is_line_visible(100) is False


class TestVirtualScrollConfig:
    """Test VirtualScrollConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = VirtualScrollConfig()

        assert config.buffer_lines == 10
        assert config.min_lines_for_virtual == 500
        assert config.estimated_line_height == 20
        assert config.max_render_lines == 1000

    def test_custom_config(self):
        """Test custom configuration."""
        config = VirtualScrollConfig(
            buffer_lines=20,
            min_lines_for_virtual=1000,
            estimated_line_height=25,
            max_render_lines=2000
        )

        assert config.buffer_lines == 20
        assert config.min_lines_for_virtual == 1000


class TestVirtualScrollPreview:
    """Test VirtualScrollPreview."""

    def test_initialization(self):
        """Test creating virtual scroll preview."""
        api = Mock()
        renderer = VirtualScrollPreview(api)

        assert renderer.is_enabled() is True
        assert renderer.asciidoc_api is api

    def test_enable_disable(self):
        """Test enabling/disabling virtual scrolling."""
        api = Mock()
        renderer = VirtualScrollPreview(api)

        assert renderer.is_enabled() is True

        renderer.enable(False)
        assert renderer.is_enabled() is False

        renderer.enable(True)
        assert renderer.is_enabled() is True

    def test_should_use_virtual_scrolling_small_doc(self):
        """Test should not use virtual scrolling for small documents."""
        api = Mock()
        renderer = VirtualScrollPreview(api)

        # Small document (< 500 lines)
        small_doc = '\n'.join([f'Line {i}' for i in range(100)])

        assert renderer.should_use_virtual_scrolling(small_doc) is False

    def test_should_use_virtual_scrolling_large_doc(self):
        """Test should use virtual scrolling for large documents."""
        api = Mock()
        renderer = VirtualScrollPreview(api)

        # Large document (> 500 lines)
        large_doc = '\n'.join([f'Line {i}' for i in range(1000)])

        assert renderer.should_use_virtual_scrolling(large_doc) is True

    def test_should_use_virtual_scrolling_when_disabled(self):
        """Test respects enabled flag."""
        api = Mock()
        renderer = VirtualScrollPreview(api)
        renderer.enable(False)

        # Large document but virtual scrolling disabled
        large_doc = '\n'.join([f'Line {i}' for i in range(1000)])

        assert renderer.should_use_virtual_scrolling(large_doc) is False

    def test_render_viewport_small_doc(self):
        """Test rendering small document (full render)."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Small document
        source = '\n'.join([f'Line {i}' for i in range(100)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=2000,
            line_height=20
        )

        html, offset = renderer.render_viewport(source, viewport)

        # Should do full render
        assert offset == 0
        assert api.execute.called

    def test_render_viewport_large_doc(self):
        """Test rendering large document (partial render)."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Large document (1000 lines)
        source = '\n'.join([f'Line {i}' for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=1000,  # Scrolled to line 50
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20
        )

        html, offset = renderer.render_viewport(source, viewport)

        # Should do partial render
        # Offset should be at start line
        assert offset > 0

        # Should have rendered fewer lines than total
        stats = renderer.get_statistics()
        assert stats['rendered_lines'] < stats['total_lines']

    def test_render_viewport_top_of_doc(self):
        """Test rendering at top of document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Large document
        source = '\n'.join([f'Line {i}' for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,  # At top
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20
        )

        html, offset = renderer.render_viewport(source, viewport)

        # Offset should be 0 at top
        assert offset == 0

    def test_render_viewport_bottom_of_doc(self):
        """Test rendering at bottom of document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Large document
        source = '\n'.join([f'Line {i}' for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=18000,  # Near bottom
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20
        )

        html, offset = renderer.render_viewport(source, viewport)

        # Should handle bottom gracefully
        stats = renderer.get_statistics()
        assert stats['rendered_lines'] <= 1000

    def test_update_line_height(self):
        """Test updating line height."""
        api = Mock()
        renderer = VirtualScrollPreview(api)

        renderer.update_line_height(25)

        stats = renderer.get_statistics()
        assert stats['actual_line_height'] == 25

    def test_get_statistics(self):
        """Test getting statistics."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Render something
        source = '\n'.join([f'Line {i}' for i in range(1000)])
        viewport = Viewport(
            scroll_x=0,
            scroll_y=1000,
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20
        )

        renderer.render_viewport(source, viewport)

        stats = renderer.get_statistics()

        assert 'enabled' in stats
        assert 'total_lines' in stats
        assert 'rendered_lines' in stats
        assert 'render_ratio' in stats
        assert stats['total_lines'] == 1000
        assert stats['rendered_lines'] < stats['total_lines']


class TestViewportCalculator:
    """Test ViewportCalculator."""

    def test_calculate_from_values(self):
        """Test calculating viewport from values."""
        viewport = ViewportCalculator.calculate_from_values(
            width=800,
            height=600,
            scroll_y=1000,
            document_height=5000,
            line_height=20
        )

        assert viewport.width == 800
        assert viewport.height == 600
        assert viewport.scroll_y == 1000
        assert viewport.document_height == 5000
        assert viewport.line_height == 20

    def test_calculate_from_values_defaults(self):
        """Test calculating viewport with defaults."""
        viewport = ViewportCalculator.calculate_from_values(
            width=800,
            height=600
        )

        assert viewport.scroll_y == 0
        assert viewport.document_height == 600  # Defaults to height
        assert viewport.line_height == 20  # Default


@pytest.mark.performance
class TestVirtualScrollPerformance:
    """Test performance benefits of virtual scrolling."""

    def test_render_ratio_small_viewport(self):
        """Test render ratio with small viewport."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Very large document (10,000 lines)
        source = '\n'.join([f'Line {i}' for i in range(10000)])

        # Small viewport
        viewport = Viewport(
            scroll_x=0,
            scroll_y=5000,  # Middle of document
            width=800,
            height=600,
            document_width=800,
            document_height=200000,
            line_height=20
        )

        renderer.render_viewport(source, viewport)

        stats = renderer.get_statistics()

        # Should render only ~1% of document
        # Viewport: 600px / 20px = 30 lines
        # Buffer: 10 + 10 = 20 lines
        # Total: ~50 lines out of 10,000 = 0.5%
        assert stats['render_ratio'] < 5  # Less than 5%

    def test_memory_efficiency(self):
        """Test memory efficiency of virtual scrolling."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Huge document
        source = '\n'.join([f'Line {i}' for i in range(50000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=10000,
            width=800,
            height=600,
            document_width=800,
            document_height=1000000,
            line_height=20
        )

        renderer.render_viewport(source, viewport)

        stats = renderer.get_statistics()

        # Should render less than 1% of document
        assert stats['rendered_lines'] < 500  # Out of 50,000
        assert stats['render_ratio'] < 1.0


class TestVirtualScrollEdgeCases:
    """Test edge cases for virtual scrolling."""

    def test_empty_document(self):
        """Test with empty document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=0,
            line_height=20
        )

        html, offset = renderer.render_viewport('', viewport)

        assert offset == 0

    def test_single_line_document(self):
        """Test with single line."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=20,
            line_height=20
        )

        html, offset = renderer.render_viewport('Single line', viewport)

        # Small doc - should do full render
        assert offset == 0

    def test_render_failure_fallback(self):
        """Test fallback on render failure."""
        api = Mock()
        api.execute = Mock(side_effect=Exception("Render failed"))

        renderer = VirtualScrollPreview(api)

        # Large document
        source = '\n'.join([f'Line {i}' for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20
        )

        # Should not raise exception
        html, offset = renderer.render_viewport(source, viewport)

        # Should return fallback HTML (escaped text in <pre>)
        assert '<pre' in html

    def test_negative_scroll_position(self):
        """Test with negative scroll position."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        source = '\n'.join([f'Line {i}' for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=-100,  # Negative (invalid)
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20
        )

        # Should handle gracefully
        html, offset = renderer.render_viewport(source, viewport)

        # Should clamp to 0
        assert offset >= 0
