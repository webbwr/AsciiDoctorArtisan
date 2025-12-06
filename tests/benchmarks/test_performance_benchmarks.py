"""Performance benchmark tests for critical operations.

Uses pytest-benchmark for consistent measurement.
Run with: pytest tests/benchmarks/ --benchmark-only

Baseline metrics (v2.1.0):
- Core imports: 90ms
- Settings load: <50ms
- Template instantiation: <10ms
- Search (1KB doc): <5ms
"""

import pytest

# Mark all tests as benchmarks
pytestmark = [pytest.mark.benchmark, pytest.mark.performance]


class TestImportBenchmarks:
    """Benchmark import times for critical modules."""

    def test_core_imports(self, benchmark):
        """Benchmark core module imports."""

        def import_core():
            # Force fresh import
            import sys

            modules_to_remove = [k for k in sys.modules.keys() if k.startswith("asciidoc_artisan.core")]
            for mod in modules_to_remove:
                del sys.modules[mod]

            from asciidoc_artisan import core

            return core

        # Warm up
        import_core()

        # Benchmark
        result = benchmark(import_core)
        assert result is not None

    def test_settings_import(self, benchmark):
        """Benchmark Settings class import and instantiation."""

        def create_settings():
            from asciidoc_artisan.core import Settings

            return Settings()

        result = benchmark(create_settings)
        assert result is not None


class TestSearchBenchmarks:
    """Benchmark search operations."""

    @pytest.fixture
    def sample_content(self):
        """Generate sample content for search benchmarks."""
        return """= Large Document
:author: Test

""" + "\n".join([f"== Section {i}\n\nParagraph content {i} with some searchable text." for i in range(100)])

    def test_search_small_doc(self, benchmark):
        """Benchmark search in small document (~1KB)."""
        from asciidoc_artisan.core.search_engine import SearchEngine

        content = "Hello World. This is a test. Hello again. More text here."

        def search():
            engine = SearchEngine(content)
            return engine.find_all("Hello")

        result = benchmark(search)
        assert len(result) == 2

    def test_search_large_doc(self, benchmark, sample_content):
        """Benchmark search in large document (~10KB)."""
        from asciidoc_artisan.core.search_engine import SearchEngine

        def search():
            engine = SearchEngine(sample_content)
            return engine.find_all("Section")

        result = benchmark(search)
        assert len(result) == 100


class TestTemplateBenchmarks:
    """Benchmark template operations."""

    def test_template_instantiation(self, benchmark):
        """Benchmark template variable substitution."""
        from asciidoc_artisan.core.template_engine import TemplateEngine
        from asciidoc_artisan.core.template_models import Template, TemplateVariable

        engine = TemplateEngine()

        template = Template(
            name="Benchmark",
            category="test",
            description="Benchmark template",
            author="Test",
            version="1.0",
            variables=[
                TemplateVariable(name="title", description="Title"),
                TemplateVariable(name="author", description="Author"),
                TemplateVariable(name="date", description="Date"),
            ],
            content="= {{title}}\n{{author}}\n{{date}}\n\n== Introduction\n\nContent.",
        )

        variables = {"title": "My Doc", "author": "John", "date": "2025-01-01"}

        def instantiate():
            return engine.instantiate(template, variables)

        result = benchmark(instantiate)
        assert "My Doc" in result


class TestFileOperationBenchmarks:
    """Benchmark file operations."""

    def test_atomic_save_small(self, benchmark, tmp_path):
        """Benchmark atomic save of small file."""
        from asciidoc_artisan.core.file_operations import atomic_save_text

        content = "= Test\n\nSmall content."
        file_path = tmp_path / "test.adoc"

        def save():
            return atomic_save_text(file_path, content)

        result = benchmark(save)
        assert result is True

    def test_atomic_save_medium(self, benchmark, tmp_path):
        """Benchmark atomic save of medium file (~50KB)."""
        from asciidoc_artisan.core.file_operations import atomic_save_text

        content = "= Large Document\n\n" + ("Paragraph content. " * 1000 + "\n\n") * 10
        file_path = tmp_path / "medium.adoc"

        def save():
            return atomic_save_text(file_path, content)

        result = benchmark(save)
        assert result is True


class TestGPUDetectionBenchmarks:
    """Benchmark GPU detection (cached vs uncached)."""

    def test_gpu_info_cached(self, benchmark):
        """Benchmark cached GPU info retrieval."""
        from asciidoc_artisan.core.gpu_detection import get_gpu_info

        # Warm cache
        get_gpu_info()

        def get_cached():
            return get_gpu_info()

        result = benchmark(get_cached)
        assert result is not None

    def test_gpu_cache_lookup(self, benchmark):
        """Benchmark GPU cache file lookup."""
        from asciidoc_artisan.core.gpu_cache import GPUDetectionCache

        def lookup():
            return GPUDetectionCache.load()

        benchmark(lookup)
        # May be None if no cache exists, just verify benchmark ran
        assert True
