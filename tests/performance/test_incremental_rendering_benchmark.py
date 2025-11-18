"""
Performance benchmark for incremental rendering.

Measures actual rendering speed improvements compared to full rendering.
Tests with realistic AsciiDoc documents of various sizes.
"""

import time

import pytest

try:
    from asciidoc3 import asciidoc3
    from asciidoc3.asciidoc3api import AsciiDoc3API

    ASCIIDOC3_AVAILABLE = True
except ImportError:
    asciidoc3 = None
    AsciiDoc3API = None
    ASCIIDOC3_AVAILABLE = False

from asciidoc_artisan.workers.incremental_renderer import IncrementalPreviewRenderer

# Skip tests if AsciiDoc3 not available
pytestmark = pytest.mark.skipif(not ASCIIDOC3_AVAILABLE, reason="AsciiDoc3 not available")


def create_test_document(num_sections: int = 10, section_size: int = 5) -> str:
    """
    Create test AsciiDoc document.

    Args:
        num_sections: Number of sections
        section_size: Paragraphs per section

    Returns:
        AsciiDoc source text
    """
    lines = ["= Performance Test Document", ""]

    for i in range(num_sections):
        lines.append(f"== Section {i + 1}")
        lines.append("")

        for j in range(section_size):
            lines.append(
                f"This is paragraph {j + 1} in section {i + 1}. "
                f"It contains some test content to simulate a real document. "
                f"AsciiDoc supports many features like *bold*, _italic_, "
                f"and `code` formatting."
            )
            lines.append("")

    return "\n".join(lines)


def benchmark_render(renderer, source: str, num_iterations: int = 5) -> float:
    """
    Benchmark rendering performance.

    Args:
        renderer: Renderer to test
        source: Document source
        num_iterations: Number of iterations

    Returns:
        Average render time in seconds
    """
    times = []

    for _ in range(num_iterations):
        start = time.time()
        renderer.render(source)
        elapsed = time.time() - start
        times.append(elapsed)

    return sum(times) / len(times)


@pytest.mark.performance
class TestIncrementalRenderingBenchmark:
    """Benchmark tests for incremental rendering."""

    def setup_method(self):
        """Set up AsciiDoc API for each test."""
        if ASCIIDOC3_AVAILABLE and AsciiDoc3API:
            self.api = AsciiDoc3API(asciidoc3.__file__)
            self.api.options("--no-header-footer")
            self.api.attributes["icons"] = "font"
            self.api.attributes["source-highlighter"] = "highlight.js"

    def test_benchmark_small_document_full_vs_incremental(self):
        """Benchmark small document (10 sections)."""
        source = create_test_document(num_sections=10, section_size=3)

        # Create renderers
        incremental = IncrementalPreviewRenderer(self.api)
        full_render = IncrementalPreviewRenderer(self.api)
        full_render.enable(False)  # Disable incremental

        # First render (both should be similar - cold start)
        incremental_first = benchmark_render(incremental, source, num_iterations=3)
        full_first = benchmark_render(full_render, source, num_iterations=3)

        # Second render (incremental should be faster)
        incremental_second = benchmark_render(incremental, source, num_iterations=3)
        full_second = benchmark_render(full_render, source, num_iterations=3)

        print("\nSmall Document (10 sections):")
        print(f"  Incremental first render: {incremental_first:.4f}s")
        print(f"  Full first render: {full_first:.4f}s")
        print(f"  Incremental cached render: {incremental_second:.4f}s")
        print(f"  Full second render: {full_second:.4f}s")
        print(f"  Speedup: {full_second / incremental_second:.2f}x")

        # Incremental should be faster on second render
        assert incremental_second < full_second

        # Cache stats
        stats = incremental.get_cache_stats()
        print(f"  Cache stats: {stats}")

    def test_benchmark_medium_document_full_vs_incremental(self):
        """Benchmark medium document (30 sections)."""
        source = create_test_document(num_sections=30, section_size=5)

        # Create renderers
        incremental = IncrementalPreviewRenderer(self.api)
        full_render = IncrementalPreviewRenderer(self.api)
        full_render.enable(False)

        # Warm up
        incremental.render(source)
        full_render.render(source)

        # Benchmark
        incremental_time = benchmark_render(incremental, source, num_iterations=5)
        full_time = benchmark_render(full_render, source, num_iterations=5)

        print("\nMedium Document (30 sections):")
        print(f"  Incremental render: {incremental_time:.4f}s")
        print(f"  Full render: {full_time:.4f}s")
        print(f"  Speedup: {full_time / incremental_time:.2f}x")

        # Incremental should be significantly faster
        assert incremental_time < full_time

        stats = incremental.get_cache_stats()
        print(f"  Cache stats: {stats}")
        assert stats["hit_rate"] > 80  # Should have high cache hit rate

    def test_benchmark_large_document_full_vs_incremental(self):
        """Benchmark large document (50 sections)."""
        source = create_test_document(num_sections=50, section_size=8)

        # Create renderers
        incremental = IncrementalPreviewRenderer(self.api)
        full_render = IncrementalPreviewRenderer(self.api)
        full_render.enable(False)

        # Warm up
        incremental.render(source)
        full_render.render(source)

        # Benchmark
        incremental_time = benchmark_render(incremental, source, num_iterations=3)
        full_time = benchmark_render(full_render, source, num_iterations=3)

        print("\nLarge Document (50 sections):")
        print(f"  Incremental render: {incremental_time:.4f}s")
        print(f"  Full render: {full_time:.4f}s")
        print(f"  Speedup: {full_time / incremental_time:.2f}x")

        # Incremental should be much faster for large docs
        assert incremental_time < full_time

        stats = incremental.get_cache_stats()
        print(f"  Cache stats: {stats}")
        assert stats["hit_rate"] > 85

    def test_benchmark_partial_edit(self):
        """Benchmark partial edit (change one section)."""
        source1 = create_test_document(num_sections=40, section_size=5)

        # Create lines for modification
        lines = source1.split("\n")

        # Find first section and modify it
        for i, line in enumerate(lines):
            if line.startswith("== Section 1"):
                lines[i] = "== Section 1 MODIFIED"
                break

        source2 = "\n".join(lines)

        # Create renderer
        incremental = IncrementalPreviewRenderer(self.api)

        # First render (warm cache)
        incremental.render(source1)

        # Benchmark partial edit render
        edit_time = benchmark_render(incremental, source2, num_iterations=5)

        # Benchmark full render for comparison
        full_render = IncrementalPreviewRenderer(self.api)
        full_render.enable(False)
        full_time = benchmark_render(full_render, source2, num_iterations=5)

        print("\nPartial Edit (1 section changed out of 40):")
        print(f"  Incremental render: {edit_time:.4f}s")
        print(f"  Full render: {full_time:.4f}s")
        print(f"  Speedup: {full_time / edit_time:.2f}x")

        # Incremental should be much faster (3x+ target)
        assert edit_time < full_time
        speedup = full_time / edit_time
        assert speedup >= 3.0, f"Expected 3x+ speedup, got {speedup:.2f}x"

        stats = incremental.get_cache_stats()
        print(f"  Cache stats: {stats}")

    def test_benchmark_multiple_edits(self):
        """Benchmark multiple sequential edits."""
        base_source = create_test_document(num_sections=30, section_size=5)

        # Create renderer
        incremental = IncrementalPreviewRenderer(self.api)

        # First render
        start = time.time()
        incremental.render(base_source)
        first_render = time.time() - start

        # Make 10 sequential edits
        edit_times = []
        for i in range(10):
            # Modify document slightly
            modified = base_source.replace("paragraph 1", f"paragraph 1 edit {i}")

            # Render
            start = time.time()
            incremental.render(modified)
            edit_time = time.time() - start
            edit_times.append(edit_time)

        avg_edit_time = sum(edit_times) / len(edit_times)

        print("\nMultiple Edits (10 sequential edits):")
        print(f"  First render: {first_render:.4f}s")
        print(f"  Average edit render: {avg_edit_time:.4f}s")
        print(f"  Speedup vs first: {first_render / avg_edit_time:.2f}x")

        # Edit renders should be similar or faster than first render
        # Allow 35% variance due to incremental renderer overhead + environmental factors
        # (block detection, hashing, cache lookup, CPU/I/O load variance)
        # For small edits on medium documents, overhead roughly equals caching benefit
        # Empirical data shows 0.77x-1.00x speedup range (up to 30% slower in worst case)
        assert avg_edit_time < first_render * 1.35, (
            f"Edit renders ({avg_edit_time:.4f}s) should not be >35% slower than first ({first_render:.4f}s)"
        )

        stats = incremental.get_cache_stats()
        print(f"  Final cache stats: {stats}")

    def test_benchmark_cache_efficiency(self):
        """Benchmark cache hit rate with repeated renders."""
        source = create_test_document(num_sections=25, section_size=5)

        # Create renderer
        incremental = IncrementalPreviewRenderer(self.api)

        # First render (cold cache)
        incremental.render(source)

        # Render 20 more times (should be all cache hits)
        for _ in range(20):
            incremental.render(source)

        stats = incremental.get_cache_stats()

        print("\nCache Efficiency (21 renders of same document):")
        print(f"  Cache size: {stats['size']}")
        print(f"  Cache hits: {stats['hits']}")
        print(f"  Cache misses: {stats['misses']}")
        print(f"  Hit rate: {stats['hit_rate']:.2f}%")

        # After first render, all should be cache hits
        # First render = N misses (one per block)
        # Next 20 renders = 20*N hits
        # Hit rate should be ~95%+ (20N / (20N + N) = 95.2%)
        assert stats["hit_rate"] > 90

    def test_benchmark_summary(self):
        """Summary benchmark showing target achievement."""
        print("\n" + "=" * 60)
        print("INCREMENTAL RENDERING BENCHMARK SUMMARY")
        print("=" * 60)

        # Test various document sizes
        test_cases = [(10, 3, "Small"), (25, 5, "Medium"), (50, 8, "Large")]

        results = []

        for num_sections, section_size, label in test_cases:
            source = create_test_document(num_sections, section_size)

            # Incremental renderer
            incremental = IncrementalPreviewRenderer(self.api)
            incremental.render(source)  # Warm cache
            inc_time = benchmark_render(incremental, source, num_iterations=5)

            # Full renderer
            full = IncrementalPreviewRenderer(self.api)
            full.enable(False)
            full_time = benchmark_render(full, source, num_iterations=5)

            speedup = full_time / inc_time
            results.append((label, num_sections, inc_time, full_time, speedup))

            print(f"\n{label} Document ({num_sections} sections):")
            print(f"  Full render:        {full_time:.4f}s")
            print(f"  Incremental render: {inc_time:.4f}s")
            print(f"  Speedup:            {speedup:.2f}x")

            stats = incremental.get_cache_stats()
            print(f"  Cache hit rate:     {stats['hit_rate']:.1f}%")

        print("\n" + "=" * 60)
        print("TARGET: 3-5x speedup for incremental rendering")

        # Check if we meet the 3x target
        avg_speedup = sum(r[4] for r in results) / len(results)
        print(f"AVERAGE SPEEDUP: {avg_speedup:.2f}x")

        if avg_speedup >= 3.0:
            print("STATUS: ✓ TARGET ACHIEVED")
        else:
            print("STATUS: ✗ TARGET NOT MET")

        print("=" * 60)

        # Assert target met
        assert avg_speedup >= 3.0, f"Target: 3x, Actual: {avg_speedup:.2f}x"
