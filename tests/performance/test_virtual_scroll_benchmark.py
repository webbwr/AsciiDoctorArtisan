"""
Performance benchmarks for virtual scrolling.

Tests performance improvements with large documents.
"""

import time
from unittest.mock import Mock

import pytest

from asciidoc_artisan.ui.virtual_scroll_preview import (
    Viewport,
    VirtualScrollConfig,
    VirtualScrollPreview,
)


def create_large_document(lines: int) -> str:
    """
    Create large test document.

    Args:
        lines: Number of lines

    Returns:
        AsciiDoc source text
    """
    doc_lines = ["= Large Document Test", ""]

    for i in range(lines // 10):
        doc_lines.append(f"== Section {i}")
        doc_lines.append("")
        doc_lines.append(f"This is section {i} of the test document.")
        doc_lines.append("")
        doc_lines.append("Some content with *bold* and _italic_ text.")
        doc_lines.append("")
        doc_lines.append("- List item 1")
        doc_lines.append("- List item 2")
        doc_lines.append("- List item 3")
        doc_lines.append("")

    return "\n".join(doc_lines[:lines])


@pytest.mark.performance
class TestVirtualScrollBenchmark:
    """Benchmark virtual scrolling performance."""

    def test_small_document_1000_lines(self):
        """Benchmark with 1,000 line document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)
        source = create_large_document(1000)

        viewport = Viewport(
            scroll_x=0,
            scroll_y=5000,  # Middle
            width=800,
            height=600,
            document_width=800,
            document_height=20000,
            line_height=20,
        )

        start = time.time()
        renderer.render_viewport(source, viewport)
        elapsed = time.time() - start

        stats = renderer.get_statistics()

        print("\n1000 lines:")
        print(f"  Render time: {elapsed * 1000:.2f}ms")
        print(f"  Lines rendered: {stats['rendered_lines']}/{stats['total_lines']}")
        print(f"  Render ratio: {stats['render_ratio']:.2f}%")

        # Should render only small fraction
        assert stats["render_ratio"] < 10

    def test_medium_document_5000_lines(self):
        """Benchmark with 5,000 line document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)
        source = create_large_document(5000)

        viewport = Viewport(
            scroll_x=0,
            scroll_y=50000,  # Middle
            width=800,
            height=600,
            document_width=800,
            document_height=100000,
            line_height=20,
        )

        start = time.time()
        renderer.render_viewport(source, viewport)
        elapsed = time.time() - start

        stats = renderer.get_statistics()

        print("\n5000 lines:")
        print(f"  Render time: {elapsed * 1000:.2f}ms")
        print(f"  Lines rendered: {stats['rendered_lines']}/{stats['total_lines']}")
        print(f"  Render ratio: {stats['render_ratio']:.2f}%")

        # Should render even smaller fraction
        assert stats["render_ratio"] < 5

    def test_large_document_10000_lines(self):
        """Benchmark with 10,000 line document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)
        source = create_large_document(10000)

        viewport = Viewport(
            scroll_x=0,
            scroll_y=100000,  # Middle
            width=800,
            height=600,
            document_width=800,
            document_height=200000,
            line_height=20,
        )

        start = time.time()
        renderer.render_viewport(source, viewport)
        elapsed = time.time() - start

        stats = renderer.get_statistics()

        print("\n10000 lines:")
        print(f"  Render time: {elapsed * 1000:.2f}ms")
        print(f"  Lines rendered: {stats['rendered_lines']}/{stats['total_lines']}")
        print(f"  Render ratio: {stats['render_ratio']:.2f}%")

        # Should render tiny fraction
        assert stats["render_ratio"] < 2

    def test_huge_document_50000_lines(self):
        """Benchmark with 50,000 line document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)
        source = create_large_document(50000)

        viewport = Viewport(
            scroll_x=0,
            scroll_y=500000,  # Middle
            width=800,
            height=600,
            document_width=800,
            document_height=1000000,
            line_height=20,
        )

        start = time.time()
        renderer.render_viewport(source, viewport)
        elapsed = time.time() - start

        stats = renderer.get_statistics()

        print("\n50000 lines:")
        print(f"  Render time: {elapsed * 1000:.2f}ms")
        print(f"  Lines rendered: {stats['rendered_lines']}/{stats['total_lines']}")
        print(f"  Render ratio: {stats['render_ratio']:.2f}%")

        # Should render very tiny fraction
        assert stats["render_ratio"] < 1

    def test_scroll_through_document(self):
        """Benchmark scrolling through document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)
        source = create_large_document(10000)

        # Simulate scrolling through document
        scroll_positions = [0, 2000, 4000, 6000, 8000, 10000]
        times = []

        for scroll_y in scroll_positions:
            viewport = Viewport(
                scroll_x=0,
                scroll_y=scroll_y,
                width=800,
                height=600,
                document_width=800,
                document_height=200000,
                line_height=20,
            )

            start = time.time()
            renderer.render_viewport(source, viewport)
            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)

        print("\nScroll through 10000 lines:")
        print(f"  Positions tested: {len(scroll_positions)}")
        print(f"  Average time: {avg_time * 1000:.2f}ms")
        print(f"  Min time: {min(times) * 1000:.2f}ms")
        print(f"  Max time: {max(times) * 1000:.2f}ms")

        # All scroll positions should be fast
        assert all(t < 0.1 for t in times)  # Under 100ms

    def test_memory_footprint(self):
        """Test memory efficiency with huge document."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        # Very large document
        source = create_large_document(100000)

        viewport = Viewport(
            scroll_x=0,
            scroll_y=1000000,  # Deep in document
            width=800,
            height=600,
            document_width=800,
            document_height=2000000,
            line_height=20,
        )

        renderer.render_viewport(source, viewport)

        stats = renderer.get_statistics()

        print("\n100000 lines:")
        print(f"  Lines rendered: {stats['rendered_lines']}/{stats['total_lines']}")
        print(f"  Render ratio: {stats['render_ratio']:.2f}%")
        print(f"  Memory saved: {100 - stats['render_ratio']:.2f}%")

        # Should render less than 0.1% of document
        assert stats["render_ratio"] < 0.1
        assert stats["rendered_lines"] < 100

    def test_comparison_with_full_render(self):
        """Compare virtual scrolling vs full render."""
        api = Mock()
        api.execute = Mock()

        source = create_large_document(10000)

        # Virtual scrolling
        renderer = VirtualScrollPreview(api)
        viewport = Viewport(
            scroll_x=0,
            scroll_y=50000,
            width=800,
            height=600,
            document_width=800,
            document_height=200000,
            line_height=20,
        )

        start = time.time()
        renderer.render_viewport(source, viewport)
        virtual_time = time.time() - start

        stats = renderer.get_statistics()

        # Full render (disabled virtual scrolling)
        renderer.enable(False)

        start = time.time()
        renderer.render_viewport(source, viewport)
        full_time = time.time() - start

        speedup = full_time / virtual_time if virtual_time > 0 else 1

        print("\nComparison (10000 lines):")
        print(f"  Virtual scroll: {virtual_time * 1000:.2f}ms")
        print(f"  Full render: {full_time * 1000:.2f}ms")
        print(f"  Speedup: {speedup:.1f}x")
        print(f"  Render ratio: {stats['render_ratio']:.2f}%")

        # Virtual scrolling renders fewer lines
        # (Note: Mock doesn't actually render, so timing is overhead only)
        # In real usage with actual rendering, virtual scroll will be much faster
        assert stats["render_ratio"] < 1  # Renders less than 1% of document


@pytest.mark.performance
class TestVirtualScrollScaling:
    """Test how virtual scrolling scales with document size."""

    def test_scaling_constant_render_time(self):
        """Test that render time stays constant as document grows."""
        api = Mock()
        api.execute = Mock()

        renderer = VirtualScrollPreview(api)

        sizes = [1000, 5000, 10000, 20000, 50000]
        times = []

        for size in sizes:
            source = create_large_document(size)

            # Always scroll to middle
            scroll_y = (size * 20) // 2

            viewport = Viewport(
                scroll_x=0,
                scroll_y=scroll_y,
                width=800,
                height=600,
                document_width=800,
                document_height=size * 20,
                line_height=20,
            )

            start = time.time()
            renderer.render_viewport(source, viewport)
            elapsed = time.time() - start
            times.append(elapsed)

        print("\nScaling test:")
        for size, elapsed in zip(sizes, times):
            print(f"  {size:6d} lines: {elapsed * 1000:6.2f}ms")

        # Time should not increase significantly
        # (Variance should be low)
        avg_time = sum(times) / len(times)
        max_deviation = max(abs(t - avg_time) for t in times)

        print(f"  Average: {avg_time * 1000:.2f}ms")
        print(f"  Max deviation: {max_deviation * 1000:.2f}ms")

        # Max deviation should be small relative to average
        assert max_deviation < avg_time * 2  # Within 2x of average


@pytest.mark.performance
class TestVirtualScrollBuffering:
    """Test buffering behavior."""

    def test_buffer_size_impact(self):
        """Test impact of buffer size on render time."""
        api = Mock()
        api.execute = Mock()

        source = create_large_document(10000)

        buffer_sizes = [0, 5, 10, 20, 50]
        results = []

        for buffer_size in buffer_sizes:
            config = VirtualScrollConfig(buffer_lines=buffer_size)
            renderer = VirtualScrollPreview(api, config)

            viewport = Viewport(
                scroll_x=0,
                scroll_y=50000,
                width=800,
                height=600,
                document_width=800,
                document_height=200000,
                line_height=20,
            )

            start = time.time()
            renderer.render_viewport(source, viewport)
            elapsed = time.time() - start

            stats = renderer.get_statistics()
            results.append(
                {
                    "buffer": buffer_size,
                    "time": elapsed,
                    "lines": stats["rendered_lines"],
                    "ratio": stats["render_ratio"],
                }
            )

        print("\nBuffer size impact:")
        for r in results:
            print(f"  Buffer {r['buffer']:2d}: {r['time'] * 1000:6.2f}ms, {r['lines']:3d} lines, {r['ratio']:5.2f}%")

        # Larger buffer should render more lines
        assert results[0]["lines"] < results[-1]["lines"]
