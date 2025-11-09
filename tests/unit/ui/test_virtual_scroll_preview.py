"""
Tests for virtual scrolling preview.

Tests viewport calculation, partial rendering, and performance benefits.
"""

from unittest.mock import Mock

import pytest

from asciidoc_artisan.ui.virtual_scroll_preview import (
    Viewport,
    ViewportCalculator,
    VirtualScrollConfig,
    VirtualScrollPreview,
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
            line_height=20,
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
            line_height=20,
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
            line_height=20,
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
            line_height=0,  # Invalid
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
            line_height=20,
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
            max_render_lines=2000,
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
        small_doc = "\n".join([f"Line {i}" for i in range(100)])

        assert renderer.should_use_virtual_scrolling(small_doc) is False

    def test_should_use_virtual_scrolling_large_doc(self):
        """Test should use virtual scrolling for large documents."""
        api = Mock()
        renderer = VirtualScrollPreview(api)

        # Large document (> 500 lines)
        large_doc = "\n".join([f"Line {i}" for i in range(1000)])

        assert renderer.should_use_virtual_scrolling(large_doc) is True

    def test_should_use_virtual_scrolling_when_disabled(self):
        """Test respects enabled flag."""
        api = Mock()
        renderer = VirtualScrollPreview(api)
        renderer.enable(False)

        # Large document but virtual scrolling disabled
        large_doc = "\n".join([f"Line {i}" for i in range(1000)])

        assert renderer.should_use_virtual_scrolling(large_doc) is False

    def test_render_viewport_small_doc(self):
        """Test rendering small document (full render)."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Small document
        source = "\n".join([f"Line {i}" for i in range(100)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=2000,
            line_height=20,
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
        source = "\n".join([f"Line {i}" for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=1000,  # Scrolled to line 50
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20,
        )

        html, offset = renderer.render_viewport(source, viewport)

        # Should do partial render
        # Offset should be at start line
        assert offset > 0

        # Should have rendered fewer lines than total
        stats = renderer.get_statistics()
        assert stats["rendered_lines"] < stats["total_lines"]

    def test_render_viewport_top_of_doc(self):
        """Test rendering at top of document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Large document
        source = "\n".join([f"Line {i}" for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,  # At top
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20,
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
        source = "\n".join([f"Line {i}" for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=18000,  # Near bottom
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20,
        )

        html, offset = renderer.render_viewport(source, viewport)

        # Should handle bottom gracefully
        stats = renderer.get_statistics()
        assert stats["rendered_lines"] <= 1000

    def test_update_line_height(self):
        """Test updating line height."""
        api = Mock()
        renderer = VirtualScrollPreview(api)

        renderer.update_line_height(25)

        stats = renderer.get_statistics()
        assert stats["actual_line_height"] == 25

    def test_get_statistics(self):
        """Test getting statistics."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Render something
        source = "\n".join([f"Line {i}" for i in range(1000)])
        viewport = Viewport(
            scroll_x=0,
            scroll_y=1000,
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20,
        )

        renderer.render_viewport(source, viewport)

        stats = renderer.get_statistics()

        assert "enabled" in stats
        assert "total_lines" in stats
        assert "rendered_lines" in stats
        assert "render_ratio" in stats
        assert stats["total_lines"] == 1000
        assert stats["rendered_lines"] < stats["total_lines"]


class TestViewportCalculator:
    """Test ViewportCalculator."""

    def test_calculate_from_values(self):
        """Test calculating viewport from values."""
        viewport = ViewportCalculator.calculate_from_values(
            width=800, height=600, scroll_y=1000, document_height=5000, line_height=20
        )

        assert viewport.width == 800
        assert viewport.height == 600
        assert viewport.scroll_y == 1000
        assert viewport.document_height == 5000
        assert viewport.line_height == 20

    def test_calculate_from_values_defaults(self):
        """Test calculating viewport with defaults."""
        viewport = ViewportCalculator.calculate_from_values(width=800, height=600)

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
        source = "\n".join([f"Line {i}" for i in range(10000)])

        # Small viewport
        viewport = Viewport(
            scroll_x=0,
            scroll_y=5000,  # Middle of document
            width=800,
            height=600,
            document_width=800,
            document_height=200000,
            line_height=20,
        )

        renderer.render_viewport(source, viewport)

        stats = renderer.get_statistics()

        # Should render only ~1% of document
        # Viewport: 600px / 20px = 30 lines
        # Buffer: 10 + 10 = 20 lines
        # Total: ~50 lines out of 10,000 = 0.5%
        assert stats["render_ratio"] < 5  # Less than 5%

    def test_memory_efficiency(self):
        """Test memory efficiency of virtual scrolling."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Huge document
        source = "\n".join([f"Line {i}" for i in range(50000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=10000,
            width=800,
            height=600,
            document_width=800,
            document_height=1000000,
            line_height=20,
        )

        renderer.render_viewport(source, viewport)

        stats = renderer.get_statistics()

        # Should render less than 1% of document
        assert stats["rendered_lines"] < 500  # Out of 50,000
        assert stats["render_ratio"] < 1.0


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
            line_height=20,
        )

        html, offset = renderer.render_viewport("", viewport)

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
            line_height=20,
        )

        html, offset = renderer.render_viewport("Single line", viewport)

        # Small doc - should do full render
        assert offset == 0

    def test_render_failure_fallback(self):
        """Test fallback on render failure."""
        api = Mock()
        api.execute = Mock(side_effect=Exception("Render failed"))

        renderer = VirtualScrollPreview(api)

        # Large document
        source = "\n".join([f"Line {i}" for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20,
        )

        # Should not raise exception
        html, offset = renderer.render_viewport(source, viewport)

        # Should return fallback HTML (escaped text in <pre>)
        assert "<pre" in html

    def test_negative_scroll_position(self):
        """Test with negative scroll position."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        source = "\n".join([f"Line {i}" for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=-100,  # Negative (invalid)
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20,
        )

        # Should handle gracefully
        html, offset = renderer.render_viewport(source, viewport)

        # Should clamp to 0
        assert offset >= 0


@pytest.mark.unit
class TestViewportBufferSizes:
    """Test suite for viewport buffer size variations."""

    def test_zero_buffer_no_buffering(self):
        """Test viewport with zero buffer (no buffering)."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=200,
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=20,
        )

        start, end = viewport.get_visible_line_range(buffer_lines=0)

        # With zero buffer, only visible lines
        # scroll_y=200 / line_height=20 = line 10
        # height=600 / line_height=20 = 30 visible lines
        assert start == 10
        assert end == 41  # 10 + 30 + 1

    def test_small_buffer_2_lines(self):
        """Test viewport with small buffer (2 lines)."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=400,
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=20,
        )

        start, end = viewport.get_visible_line_range(buffer_lines=2)

        # scroll_y=400 / 20 = line 20
        # 20 - 2 (buffer) = 18
        # visible_lines = 600 / 20 + 1 = 31
        # end = 18 + 31 + (2 * 2) = 53
        assert start == 18
        assert end == 53

    def test_large_buffer_50_lines(self):
        """Test viewport with large buffer (50 lines)."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=1000,
            width=800,
            height=600,
            document_width=800,
            document_height=10000,
            line_height=20,
        )

        start, end = viewport.get_visible_line_range(buffer_lines=50)

        # scroll_y=1000 / 20 = line 50
        # 50 - 50 (buffer) = 0 (clamped)
        # visible_lines = 600 / 20 + 1 = 31
        # end = 0 + 31 + (2 * 50) = 131
        assert start == 0
        assert end == 131

    def test_buffer_larger_than_viewport(self):
        """Test buffer larger than viewport height."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=600,
            width=800,
            height=400,  # Small viewport
            document_width=800,
            document_height=5000,
            line_height=20,
        )

        start, end = viewport.get_visible_line_range(buffer_lines=50)

        # scroll_y=600 / 20 = line 30
        # 30 - 50 (buffer) = -20 → 0 (clamped)
        # visible_lines = 400 / 20 + 1 = 21
        # end = 0 + 21 + (2 * 50) = 121
        assert start == 0
        assert end == 121

    def test_negative_buffer_treated_as_zero(self):
        """Test negative buffer is handled gracefully."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=200,
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=20,
        )

        # Negative buffer should be handled like zero buffer
        start, end = viewport.get_visible_line_range(buffer_lines=-5)

        # scroll_y=200 / 20 = line 10
        # 10 - (-5) = 15
        # visible_lines = 600 / 20 + 1 = 31
        # end = 15 + 31 + (2 * -5) = 36
        assert start >= 0
        assert end > start


@pytest.mark.unit
class TestViewportBoundaryConditions:
    """Test suite for viewport boundary conditions."""

    def test_zero_width_viewport(self):
        """Test viewport with zero width."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=200,
            width=0,  # Zero width
            height=600,
            document_width=0,
            document_height=5000,
            line_height=20,
        )

        start, end = viewport.get_visible_line_range(buffer_lines=10)

        # Should still calculate line range based on height
        assert start >= 0
        assert end > start

    def test_zero_height_viewport(self):
        """Test viewport with zero height."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=200,
            width=800,
            height=0,  # Zero height
            document_width=800,
            document_height=5000,
            line_height=20,
        )

        start, end = viewport.get_visible_line_range(buffer_lines=10)

        # With zero height, should return small range
        assert start >= 0
        assert end >= start

    def test_scroll_beyond_document_height(self):
        """Test scrolling beyond document height."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=6000,  # Beyond document height
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=20,
        )

        start, end = viewport.get_visible_line_range(buffer_lines=10)

        # Should handle gracefully
        assert start >= 0
        assert end > start

    def test_very_large_document_height(self):
        """Test very large document height."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=100000,
            width=800,
            height=600,
            document_width=800,
            document_height=1000000,  # 1 million pixels
            line_height=20,
        )

        start, end = viewport.get_visible_line_range(buffer_lines=10)

        # Should calculate correctly for large documents
        # scroll_y=100000 / 20 = line 5000
        assert start >= 0
        assert end > start

    def test_is_line_visible_with_zero_line_height(self):
        """Test is_line_visible with zero line height."""
        viewport = Viewport(
            scroll_x=0,
            scroll_y=200,
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=0,  # Zero line height
        )

        # Should return (0, 0) for zero line height
        result = viewport.is_line_visible(10, buffer_lines=10)

        # With zero line height, is_line_visible returns False for all lines
        assert result is False


@pytest.mark.unit
class TestVirtualScrollConfigValidation:
    """Test suite for VirtualScrollConfig validation."""

    def test_negative_buffer_lines(self):
        """Test config with negative buffer_lines."""
        config = VirtualScrollConfig(
            buffer_lines=-10,
            min_lines_for_virtual=500,
            estimated_line_height=20,
            max_render_lines=1000,
        )

        # Should store negative value (no validation)
        assert config.buffer_lines == -10

    def test_zero_min_lines_for_virtual(self):
        """Test config with zero min_lines_for_virtual."""
        config = VirtualScrollConfig(
            buffer_lines=10,
            min_lines_for_virtual=0,
            estimated_line_height=20,
            max_render_lines=1000,
        )

        # Should store zero value
        assert config.min_lines_for_virtual == 0

    def test_very_large_max_render_lines(self):
        """Test config with very large max_render_lines."""
        config = VirtualScrollConfig(
            buffer_lines=10,
            min_lines_for_virtual=500,
            estimated_line_height=20,
            max_render_lines=1000000,  # 1 million
        )

        # Should store large value
        assert config.max_render_lines == 1000000

    def test_negative_estimated_line_height(self):
        """Test config with negative estimated_line_height."""
        config = VirtualScrollConfig(
            buffer_lines=10,
            min_lines_for_virtual=500,
            estimated_line_height=-20,
            max_render_lines=1000,
        )

        # Should store negative value (no validation)
        assert config.estimated_line_height == -20

    def test_config_immutability(self):
        """Test config is mutable dataclass (not frozen)."""
        config = VirtualScrollConfig(
            buffer_lines=10,
            min_lines_for_virtual=500,
            estimated_line_height=20,
            max_render_lines=1000,
        )

        # Should be able to modify (not frozen)
        config.buffer_lines = 20
        assert config.buffer_lines == 20


@pytest.mark.unit
class TestRenderViewportClamping:
    """Test suite for render viewport clamping logic."""

    def test_start_line_clamped_to_zero(self):
        """Test start line is clamped to 0."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        source = "\n".join([f"Line {i}" for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,  # At top
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20,
        )

        html, offset = renderer.render_viewport(source, viewport)

        # Offset should be 0 (start_line * line_height = 0 * 20 = 0)
        assert offset == 0

    def test_end_line_clamped_to_document_length(self):
        """Test end line is clamped to document length."""
        api = Mock()
        api.execute = Mock()

        config = VirtualScrollConfig(buffer_lines=500)  # Large buffer
        renderer = VirtualScrollPreview(api, config)

        source = "\n".join([f"Line {i}" for i in range(100)])  # Small document

        viewport = Viewport(
            scroll_x=0,
            scroll_y=1000,  # Near end
            width=800,
            height=600,
            document_width=800,
            document_height=2000,
            line_height=20,
        )

        html, offset = renderer.render_viewport(source, viewport)

        # Should clamp end_line to 100 (document length)
        # Render should succeed without IndexError
        assert html is not None

    def test_both_start_and_end_clamped(self):
        """Test both start and end lines are clamped."""
        api = Mock()
        api.execute = Mock()

        config = VirtualScrollConfig(buffer_lines=1000)  # Huge buffer
        renderer = VirtualScrollPreview(api, config)

        source = "\n".join([f"Line {i}" for i in range(50)])  # Tiny document

        viewport = Viewport(
            scroll_x=0,
            scroll_y=500,
            width=800,
            height=600,
            document_width=800,
            document_height=1000,
            line_height=20,
        )

        html, offset = renderer.render_viewport(source, viewport)

        # Should clamp and render entire document
        assert html is not None

    def test_viewport_larger_than_document(self):
        """Test viewport larger than document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        source = "\n".join([f"Line {i}" for i in range(10)])  # Very small document

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=2000,  # Larger than document
            document_width=800,
            document_height=200,  # Small document (10 lines * 20px)
            line_height=20,
        )

        html, offset = renderer.render_viewport(source, viewport)

        # Should render entire document
        assert offset == 0

    def test_empty_line_range_start_equals_end(self):
        """Test handling when start line equals end line."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # This is a tricky case - try to create a situation where start == end
        source = "Single line"

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=20,
            line_height=20,
        )

        html, offset = renderer.render_viewport(source, viewport)

        # Should handle gracefully
        assert html is not None


@pytest.mark.unit
class TestStatisticsAccuracy:
    """Test suite for statistics tracking accuracy."""

    def test_statistics_zero_total_lines(self):
        """Test statistics with zero total lines."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        stats = renderer.get_statistics()

        # Should show zero values initially
        assert stats["total_lines"] == 0
        assert stats["rendered_lines"] == 0
        assert stats["render_ratio"] == 0.0

    def test_statistics_all_lines_rendered_100_percent(self):
        """Test statistics when viewport shows entire document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        source = "\n".join([f"Line {i}" for i in range(600)])  # 600 lines

        # Viewport large enough to show all 600 lines + buffer
        # 600 lines * 20px + 10 buffer lines top + 10 buffer lines bottom = 620 lines total
        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=12400,  # 620 lines * 20px = 12400px
            document_width=800,
            document_height=12400,
            line_height=20,
        )

        html, offset = renderer.render_viewport(source, viewport)

        stats = renderer.get_statistics()

        # Should render 100% (virtual scrolling active, all lines visible in viewport + buffer)
        assert stats["render_ratio"] == 100.0

    def test_statistics_partial_render_50_percent(self):
        """Test statistics with partial render (~50%)."""
        api = Mock()
        api.execute = Mock()

        config = VirtualScrollConfig(buffer_lines=0)  # No buffer for precise control
        renderer = VirtualScrollPreview(api, config)

        source = "\n".join([f"Line {i}" for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=10000,  # Render about half
            document_width=800,
            document_height=20000,
            line_height=20,
        )

        html, offset = renderer.render_viewport(source, viewport)

        stats = renderer.get_statistics()

        # Should render about 50% of lines
        assert 40 <= stats["render_ratio"] <= 60

    def test_statistics_render_ratio_precision(self):
        """Test render ratio has 2 decimal places precision."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)
        renderer._total_lines = 1000
        renderer._rendered_lines = 333  # 33.3%

        stats = renderer.get_statistics()

        # Should round to 2 decimal places
        assert stats["render_ratio"] == 33.30

    def test_statistics_after_disable(self):
        """Test statistics after disabling virtual scrolling."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)
        renderer.enable(False)

        stats = renderer.get_statistics()

        # enabled flag should be False
        assert stats["enabled"] is False


@pytest.mark.unit
class TestEnableDisableToggle:
    """Test suite for enable/disable toggle behavior."""

    def test_disable_during_render(self):
        """Test disabling during render operation."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        source = "\n".join([f"Line {i}" for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20,
        )

        # Disable before render
        renderer.enable(False)

        html, offset = renderer.render_viewport(source, viewport)

        # Should fall back to full render
        # Offset should be 0 (no virtual scrolling)
        assert offset == 0

    def test_re_enable_after_disable(self):
        """Test re-enabling after disable."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Disable
        renderer.enable(False)
        assert not renderer.is_enabled()

        # Re-enable
        renderer.enable(True)
        assert renderer.is_enabled()

    def test_toggle_with_large_document(self):
        """Test toggling with large document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        source = "\n".join([f"Line {i}" for i in range(2000)])  # Large document

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=40000,
            line_height=20,
        )

        # Enable should use virtual scrolling
        renderer.enable(True)
        html1, offset1 = renderer.render_viewport(source, viewport)
        assert renderer.should_use_virtual_scrolling(source)

        # Disable should use full render
        renderer.enable(False)
        html2, offset2 = renderer.render_viewport(source, viewport)
        assert not renderer.should_use_virtual_scrolling(source)
        assert offset2 == 0  # No virtual scrolling

    def test_toggle_with_small_document(self):
        """Test toggling with small document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        source = "\n".join([f"Line {i}" for i in range(100)])  # Small document

        # Small document should not use virtual scrolling regardless
        renderer.enable(True)
        assert not renderer.should_use_virtual_scrolling(source)

        renderer.enable(False)
        assert not renderer.should_use_virtual_scrolling(source)

    def test_multiple_enable_calls(self):
        """Test multiple enable calls."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Multiple enable calls should be idempotent
        renderer.enable(True)
        assert renderer.is_enabled()

        renderer.enable(True)
        assert renderer.is_enabled()

        renderer.enable(True)
        assert renderer.is_enabled()

    def test_multiple_disable_calls(self):
        """Test multiple disable calls."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Multiple disable calls should be idempotent
        renderer.enable(False)
        assert not renderer.is_enabled()

        renderer.enable(False)
        assert not renderer.is_enabled()

        renderer.enable(False)
        assert not renderer.is_enabled()


@pytest.mark.unit
class TestViewportCalculatorWidgetHierarchy:
    """Test suite for ViewportCalculator widget hierarchy."""

    def test_widget_with_no_parent(self, qtbot):
        """Test calculate_from_widget with widget that has no parent."""
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        qtbot.addWidget(widget)
        widget.setGeometry(0, 0, 800, 600)

        viewport = ViewportCalculator.calculate_from_widget(
            widget, document_height=5000, line_height=20
        )

        # Should create viewport with zero scroll position
        assert viewport.scroll_x == 0
        assert viewport.scroll_y == 0
        assert viewport.width == 800
        assert viewport.height == 600

    def test_widget_with_qscrollarea_parent(self, qtbot):
        """Test calculate_from_widget with QScrollArea parent."""
        from PySide6.QtWidgets import QScrollArea, QWidget

        scroll_area = QScrollArea()
        qtbot.addWidget(scroll_area)

        widget = QWidget()
        scroll_area.setWidget(widget)
        widget.setGeometry(0, 0, 800, 600)

        # Set scroll bar ranges before setting values
        scroll_area.verticalScrollBar().setRange(0, 1000)
        scroll_area.horizontalScrollBar().setRange(0, 500)

        # Set scroll position
        scroll_area.verticalScrollBar().setValue(200)
        scroll_area.horizontalScrollBar().setValue(50)

        viewport = ViewportCalculator.calculate_from_widget(
            widget, document_height=5000, line_height=20
        )

        # Should extract scroll position from parent
        assert viewport.scroll_x == 50
        assert viewport.scroll_y == 200

    def test_widget_with_nested_scroll_areas(self, qtbot):
        """Test widget with multiple nested scroll areas."""
        from PySide6.QtWidgets import QScrollArea, QWidget

        outer_scroll = QScrollArea()
        qtbot.addWidget(outer_scroll)

        inner_scroll = QScrollArea()
        outer_scroll.setWidget(inner_scroll)

        widget = QWidget()
        inner_scroll.setWidget(widget)
        widget.setGeometry(0, 0, 800, 600)

        # Set scroll bar range before setting value
        inner_scroll.verticalScrollBar().setRange(0, 1000)

        # Set scroll position on inner scroll (closest ancestor)
        inner_scroll.verticalScrollBar().setValue(100)

        viewport = ViewportCalculator.calculate_from_widget(
            widget, document_height=5000, line_height=20
        )

        # Should find the closest scroll area parent
        assert viewport.scroll_y == 100

    def test_widget_with_qabstractscrollarea_parent(self, qtbot):
        """Test widget with QAbstractScrollArea as direct widget."""
        from PySide6.QtWidgets import QTextBrowser

        # QTextBrowser is a QAbstractScrollArea
        text_browser = QTextBrowser()
        qtbot.addWidget(text_browser)

        # Set scroll bar range before setting value
        text_browser.verticalScrollBar().setRange(0, 1000)

        # Set scroll position
        text_browser.verticalScrollBar().setValue(150)

        # Get the viewport widget (child of QTextBrowser)
        viewport_widget = text_browser.viewport()

        viewport = ViewportCalculator.calculate_from_widget(
            viewport_widget, document_height=5000, line_height=20
        )

        # Should extract scroll position from parent QAbstractScrollArea
        assert viewport.scroll_y == 150

    def test_scroll_position_extraction(self, qtbot):
        """Test scroll position is correctly extracted."""
        from PySide6.QtWidgets import QScrollArea, QWidget

        scroll_area = QScrollArea()
        qtbot.addWidget(scroll_area)

        widget = QWidget()
        scroll_area.setWidget(widget)
        widget.setGeometry(0, 0, 1000, 2000)

        # Set scroll bar ranges before setting values
        scroll_area.horizontalScrollBar().setRange(0, 500)
        scroll_area.verticalScrollBar().setRange(0, 1000)

        # Set specific scroll positions
        scroll_area.horizontalScrollBar().setValue(75)
        scroll_area.verticalScrollBar().setValue(300)

        viewport = ViewportCalculator.calculate_from_widget(
            widget, document_height=5000, line_height=20
        )

        # Should match exactly
        assert viewport.scroll_x == 75
        assert viewport.scroll_y == 300


@pytest.mark.unit
class TestLineHeightTracking:
    """Test suite for line height tracking."""

    def test_update_line_height_from_initial(self):
        """Test updating line height from initial estimate."""
        api = Mock()
        api.execute = Mock()

        config = VirtualScrollConfig(estimated_line_height=20)
        renderer = VirtualScrollPreview(api, config)

        # Initially None
        stats = renderer.get_statistics()
        assert stats["actual_line_height"] is None

        # Update with measured value
        renderer.update_line_height(25)

        stats = renderer.get_statistics()
        assert stats["actual_line_height"] == 25

    def test_multiple_line_height_updates(self):
        """Test multiple line height updates."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Update multiple times
        renderer.update_line_height(20)
        assert renderer._actual_line_height == 20

        renderer.update_line_height(22)
        assert renderer._actual_line_height == 22

        renderer.update_line_height(18)
        assert renderer._actual_line_height == 18

    def test_line_height_affects_viewport_calculation(self):
        """Test line height affects viewport calculation."""
        # Different line heights should produce different line ranges
        viewport1 = Viewport(
            scroll_x=0,
            scroll_y=400,
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=20,  # 20px lines
        )

        viewport2 = Viewport(
            scroll_x=0,
            scroll_y=400,
            width=800,
            height=600,
            document_width=800,
            document_height=5000,
            line_height=40,  # 40px lines (larger)
        )

        start1, end1 = viewport1.get_visible_line_range(buffer_lines=10)
        start2, end2 = viewport2.get_visible_line_range(buffer_lines=10)

        # Larger line height should result in smaller line range
        assert (end1 - start1) > (end2 - start2)

    def test_actual_vs_estimated_line_height(self):
        """Test difference between actual and estimated line height."""
        api = Mock()
        api.execute = Mock()

        config = VirtualScrollConfig(estimated_line_height=20)
        renderer = VirtualScrollPreview(api, config)

        stats = renderer.get_statistics()
        assert stats["estimated_line_height"] == 20
        assert stats["actual_line_height"] is None

        # Update with actual measurement
        renderer.update_line_height(24)

        stats = renderer.get_statistics()
        assert stats["estimated_line_height"] == 20  # Config unchanged
        assert stats["actual_line_height"] == 24  # Measured value

    def test_line_height_logging(self):
        """Test line height update is logged."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Update line height (should not crash)
        renderer.update_line_height(25)

        # Verify the height was updated
        assert renderer._actual_line_height == 25


@pytest.mark.unit
class TestRenderingFallbacks:
    """Test suite for rendering fallback behavior."""

    def test_partial_render_exception_handling(self):
        """Test partial render handles exceptions."""
        api = Mock()
        api.execute = Mock(side_effect=Exception("Render failed"))

        renderer = VirtualScrollPreview(api)

        source = "\n".join([f"Line {i}" for i in range(1000)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=200,
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20,
        )

        # Should not raise exception
        html, offset = renderer.render_viewport(source, viewport)

        # Should return fallback HTML
        assert "<pre" in html
        assert "data-start-line" in html

    def test_full_render_exception_handling(self):
        """Test full render handles exceptions."""
        api = Mock()
        api.execute = Mock(side_effect=Exception("Render failed"))

        renderer = VirtualScrollPreview(api)

        source = "\n".join([f"Line {i}" for i in range(100)])  # Small document

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=2000,
            line_height=20,
        )

        # Should fall back to full render
        html, offset = renderer.render_viewport(source, viewport)

        # Should return fallback HTML
        assert "<pre>" in html

    def test_html_escaping_in_partial_fallback(self):
        """Test HTML is escaped in partial render fallback."""
        api = Mock()
        api.execute = Mock(side_effect=Exception("Render failed"))

        renderer = VirtualScrollPreview(api)

        source = "<script>alert('xss')</script>\n" * 100
        source += "\n".join([f"Line {i}" for i in range(900)])

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20,
        )

        html, offset = renderer.render_viewport(source, viewport)

        # HTML should be escaped
        assert "&lt;script&gt;" in html
        assert "<script>" not in html

    def test_html_escaping_in_full_fallback(self):
        """Test HTML is escaped in full render fallback."""
        api = Mock()
        api.execute = Mock(side_effect=Exception("Render failed"))

        renderer = VirtualScrollPreview(api)

        source = "<script>alert('xss')</script>\n" * 10

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=200,
            line_height=20,
        )

        html, offset = renderer.render_viewport(source, viewport)

        # HTML should be escaped
        assert "&lt;script&gt;" in html
        assert "<script>" not in html

    def test_asciidoc_api_execute_failure(self):
        """Test AsciiDoc API execute method failure."""
        api = Mock()
        api.execute = Mock(side_effect=RuntimeError("API error"))

        renderer = VirtualScrollPreview(api)

        source = "= Test Document\n\nTest content"

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=200,
            line_height=20,
        )

        # Should not raise exception
        html, offset = renderer.render_viewport(source, viewport)

        # Should return fallback
        assert html is not None
        assert offset == 0

    def test_empty_source_rendering(self):
        """Test rendering empty source."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        source = ""

        viewport = Viewport(
            scroll_x=0,
            scroll_y=0,
            width=800,
            height=600,
            document_width=800,
            document_height=200,
            line_height=20,
        )

        # Should handle empty source
        html, offset = renderer.render_viewport(source, viewport)

        assert html is not None
        assert offset == 0


@pytest.mark.unit
class TestVirtualScrollingThresholds:
    """Test suite for virtual scrolling threshold behavior."""

    def test_exactly_at_min_lines_threshold_500(self):
        """Test document with exactly 500 lines (threshold)."""
        api = Mock()
        api.execute = Mock()

        config = VirtualScrollConfig(min_lines_for_virtual=500)
        renderer = VirtualScrollPreview(api, config)

        source = "\n".join(
            [f"Line {i}" for i in range(500)]
        )  # 500 newlines = 501 lines (counting starts at 1)

        # Should use virtual scrolling (>= threshold)
        assert renderer.should_use_virtual_scrolling(source)

    def test_one_below_threshold_499_lines(self):
        """Test document with 499 lines (one below threshold)."""
        api = Mock()
        api.execute = Mock()

        config = VirtualScrollConfig(min_lines_for_virtual=500)
        renderer = VirtualScrollPreview(api, config)

        source = "\n".join(
            [f"Line {i}" for i in range(498)]
        )  # 498 newlines = 499 lines

        # Should NOT use virtual scrolling (< threshold)
        assert not renderer.should_use_virtual_scrolling(source)

    def test_one_above_threshold_501_lines(self):
        """Test document with 501 lines (one above threshold)."""
        api = Mock()
        api.execute = Mock()

        config = VirtualScrollConfig(min_lines_for_virtual=500)
        renderer = VirtualScrollPreview(api, config)

        source = "\n".join(
            [f"Line {i}" for i in range(500)]
        )  # 500 newlines = 501 lines

        # Should use virtual scrolling (> threshold)
        assert renderer.should_use_virtual_scrolling(source)

    def test_zero_lines_document(self):
        """Test document with zero lines."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        source = ""  # Empty document

        # Should NOT use virtual scrolling
        assert not renderer.should_use_virtual_scrolling(source)

    def test_very_large_document_10000_lines(self):
        """Test very large document (10,000+ lines)."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        source = "\n".join([f"Line {i}" for i in range(10000)])

        # Should use virtual scrolling
        assert renderer.should_use_virtual_scrolling(source)

        viewport = Viewport(
            scroll_x=0,
            scroll_y=100000,  # Far down in document
            width=800,
            height=600,
            document_width=800,
            document_height=200000,
            line_height=20,
        )

        # Should handle large document efficiently
        html, offset = renderer.render_viewport(source, viewport)

        assert html is not None
        assert offset > 0
