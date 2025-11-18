"""
Performance benchmark tests using pytest-benchmark.

Tracks baseline performance and detects regressions.
QA-8: Phase 3 - Quality Infrastructure

Run with: pytest tests/performance/test_benchmarks.py --benchmark-only
Compare: pytest tests/performance/test_benchmarks.py --benchmark-compare
"""

import pytest

from asciidoc_artisan.core import atomic_save_text, sanitize_path
from asciidoc_artisan.core.adaptive_debouncer import AdaptiveDebouncer
from asciidoc_artisan.core.lru_cache import LRUCache
from asciidoc_artisan.workers.incremental_renderer import DocumentBlockSplitter


@pytest.mark.benchmark
class TestFileOperationBenchmarks:
    """Benchmark file I/O operations."""

    def test_benchmark_atomic_save_small_file(self, benchmark, tmp_path):
        """Benchmark atomic save for small files (1KB)."""
        file_path = tmp_path / "small.txt"
        content = "X" * 1024  # 1KB

        result = benchmark(atomic_save_text, file_path, content)
        assert result is True

    def test_benchmark_atomic_save_medium_file(self, benchmark, tmp_path):
        """Benchmark atomic save for medium files (100KB)."""
        file_path = tmp_path / "medium.txt"
        content = "X" * (100 * 1024)  # 100KB

        result = benchmark(atomic_save_text, file_path, content)
        assert result is True

    def test_benchmark_atomic_save_large_file(self, benchmark, tmp_path):
        """Benchmark atomic save for large files (1MB)."""
        file_path = tmp_path / "large.txt"
        content = "X" * (1024 * 1024)  # 1MB

        result = benchmark(atomic_save_text, file_path, content)
        assert result is True

    def test_benchmark_path_sanitization(self, benchmark):
        """Benchmark path sanitization performance."""
        paths = [
            "/home/user/documents/file.adoc",
            "../../etc/passwd",
            "/tmp/test.txt",
            "relative/path/to/file.adoc",
        ]

        def sanitize_multiple():
            return [sanitize_path(p) for p in paths]

        result = benchmark(sanitize_multiple)
        assert len(result) == len(paths)


@pytest.mark.benchmark
class TestCacheBenchmarks:
    """Benchmark LRU cache operations."""

    def test_benchmark_cache_put(self, benchmark):
        """Benchmark cache put operations."""
        cache = LRUCache(max_size=100)
        data = [(f"key_{i}", f"value_{i}") for i in range(100)]

        def put_all():
            for key, value in data:
                cache.put(key, value)

        benchmark(put_all)

    def test_benchmark_cache_get(self, benchmark):
        """Benchmark cache get operations."""
        cache = LRUCache(max_size=100)
        # Populate cache
        for i in range(100):
            cache.put(f"key_{i}", f"value_{i}")

        keys = [f"key_{i}" for i in range(100)]

        def get_all():
            return [cache.get(key) for key in keys]

        result = benchmark(get_all)
        assert len(result) == 100

    def test_benchmark_cache_mixed_operations(self, benchmark):
        """Benchmark mixed cache operations (put/get)."""
        cache = LRUCache(max_size=50)

        def mixed_ops():
            for i in range(100):
                if i % 2 == 0:
                    cache.put(f"key_{i}", f"value_{i}")
                else:
                    cache.get(f"key_{i - 1}")

        benchmark(mixed_ops)


@pytest.mark.benchmark
class TestDebouncerBenchmarks:
    """Benchmark adaptive debouncer calculations."""

    def test_benchmark_delay_calculation_small_doc(self, benchmark):
        """Benchmark delay calculation for small documents."""
        debouncer = AdaptiveDebouncer()

        result = benchmark(debouncer.calculate_delay, document_size=1000)
        assert result >= 0

    def test_benchmark_delay_calculation_large_doc(self, benchmark):
        """Benchmark delay calculation for large documents."""
        debouncer = AdaptiveDebouncer()

        result = benchmark(debouncer.calculate_delay, document_size=1_000_000)
        assert result >= 0

    def test_benchmark_delay_with_render_time(self, benchmark):
        """Benchmark delay calculation with render time tracking."""
        debouncer = AdaptiveDebouncer()

        result = benchmark(debouncer.calculate_delay, document_size=50_000, last_render_time=0.3)
        assert result >= 0


@pytest.mark.benchmark
class TestTextProcessingBenchmarks:
    """Benchmark text processing operations."""

    def test_benchmark_block_splitting_small(self, benchmark):
        """Benchmark document block splitting for small documents."""
        text = """= Document

== Section 1
Content here.

== Section 2
More content.

== Section 3
Final content.
"""
        result = benchmark(DocumentBlockSplitter.split, text)
        assert len(result) > 0

    def test_benchmark_block_splitting_large(self, benchmark):
        """Benchmark document block splitting for large documents."""
        # Generate large document with 100 sections
        sections = []
        for i in range(100):
            sections.append(f"== Section {i}\n\nContent for section {i}.\n\n")
        text = "= Large Document\n\n" + "".join(sections)

        result = benchmark(DocumentBlockSplitter.split, text)
        assert len(result) > 0

    def test_benchmark_string_operations(self, benchmark):
        """Benchmark common string operations on large text."""
        text = "Line of text\n" * 10000  # 10K lines

        def process_text():
            lines = text.split("\n")
            stripped = [line.strip() for line in lines]
            filtered = [line for line in stripped if line]
            return len(filtered)

        result = benchmark(process_text)
        assert result > 0


@pytest.mark.benchmark
class TestRenderingBenchmarks:
    """Benchmark rendering and preview operations."""

    def test_benchmark_markdown_to_html_small(self, benchmark):
        """Benchmark small document rendering (1KB)."""
        content = "= Test Document\n\n" + "Test paragraph.\n\n" * 20

        # Simple HTML conversion (placeholder - would use actual renderer)
        def render():
            return f"<html><body>{content.replace('=', '<h1>').replace('\n\n', '</h1><p>')}</body></html>"

        result = benchmark(render)
        assert len(result) > 0

    def test_benchmark_markdown_to_html_medium(self, benchmark):
        """Benchmark medium document rendering (100KB)."""
        # Generate ~100KB document
        sections = []
        for i in range(200):
            sections.append(f"== Section {i}\n\n{'Content. ' * 50}\n\n")
        content = "= Large Document\n\n" + "".join(sections)

        def render():
            return f"<html><body>{content[:1000]}</body></html>"  # Simplified

        result = benchmark(render)
        assert len(result) > 0


@pytest.mark.benchmark
class TestCollectionBenchmarks:
    """Benchmark collection operations."""

    def test_benchmark_list_operations(self, benchmark):
        """Benchmark list creation and manipulation."""

        def list_ops():
            data = list(range(10000))
            doubled = [x * 2 for x in data]
            filtered = [x for x in doubled if x % 3 == 0]
            return len(filtered)

        result = benchmark(list_ops)
        assert result > 0

    def test_benchmark_dict_operations(self, benchmark):
        """Benchmark dictionary creation and lookups."""

        def dict_ops():
            data = {f"key_{i}": f"value_{i}" for i in range(1000)}
            lookups = [data.get(f"key_{i}") for i in range(1000)]
            return len(lookups)

        result = benchmark(dict_ops)
        assert result == 1000

    def test_benchmark_set_operations(self, benchmark):
        """Benchmark set operations."""

        def set_ops():
            set1 = set(range(1000))
            set2 = set(range(500, 1500))
            union = set1 | set2
            intersection = set1 & set2
            difference = set1 - set2
            return len(union) + len(intersection) + len(difference)

        result = benchmark(set_ops)
        assert result > 0


@pytest.mark.benchmark
@pytest.mark.slow
class TestMemoryBenchmarks:
    """Benchmark memory-intensive operations."""

    def test_benchmark_large_cache_population(self, benchmark):
        """Benchmark populating large cache."""
        cache = LRUCache(max_size=1000)
        data = [(f"key_{i}", "X" * 1000) for i in range(1000)]  # 1MB total

        def populate():
            for key, value in data:
                cache.put(key, value)

        benchmark(populate)

    def test_benchmark_large_text_processing(self, benchmark):
        """Benchmark processing very large text."""
        # 10MB text
        text = "Line of text with some content here.\n" * 200_000

        def process():
            lines = text.split("\n")
            return len([line for line in lines if "content" in line])

        result = benchmark(process)
        assert result > 0


# Performance baselines (used for regression detection)
PERFORMANCE_BASELINES = {
    "atomic_save_small": 0.001,  # 1ms
    "atomic_save_medium": 0.010,  # 10ms
    "atomic_save_large": 0.100,  # 100ms
    "cache_put_100": 0.001,  # 1ms for 100 puts
    "cache_get_100": 0.0005,  # 0.5ms for 100 gets
    "debouncer_small": 0.0001,  # 100µs
    "debouncer_large": 0.0002,  # 200µs
    "block_split_small": 0.001,  # 1ms
    "block_split_large": 0.050,  # 50ms for 100 sections
}


def pytest_benchmark_scale_unit(config, unit, benchmarks, best, worst, sort):
    """Custom scale for benchmark output."""
    if unit == "seconds":
        return "milliseconds", 1000.0
    return unit, 1.0
