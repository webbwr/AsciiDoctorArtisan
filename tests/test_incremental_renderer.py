"""
Tests for incremental preview renderer.

Tests block-based caching, diff detection, and rendering performance.
"""

import pytest
from asciidoc_artisan.workers.incremental_renderer import (
    BlockCache,
    DocumentBlock,
    DocumentBlockSplitter,
    IncrementalPreviewRenderer,
)


class TestBlockCache:
    """Test block cache LRU behavior."""

    def test_cache_put_and_get(self):
        """Test basic cache operations."""
        cache = BlockCache(max_size=3)

        cache.put("block1", "<h1>Title</h1>")
        cache.put("block2", "<p>Content</p>")

        assert cache.get("block1") == "<h1>Title</h1>"
        assert cache.get("block2") == "<p>Content</p>"
        assert cache.get("block3") is None

    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = BlockCache(max_size=2)

        cache.put("block1", "html1")
        cache.put("block2", "html2")
        cache.put("block3", "html3")  # Should evict block1

        assert cache.get("block1") is None  # Evicted
        assert cache.get("block2") == "html2"
        assert cache.get("block3") == "html3"

    def test_cache_lru_update(self):
        """Test LRU update on access."""
        cache = BlockCache(max_size=2)

        cache.put("block1", "html1")
        cache.put("block2", "html2")

        # Access block1 (moves to end)
        cache.get("block1")

        # Add block3 (should evict block2, not block1)
        cache.put("block3", "html3")

        assert cache.get("block1") == "html1"  # Still in cache
        assert cache.get("block2") is None     # Evicted
        assert cache.get("block3") == "html3"

    def test_cache_stats(self):
        """Test cache statistics tracking."""
        cache = BlockCache(max_size=10)

        cache.put("block1", "html1")
        cache.put("block2", "html2")

        # Hits
        cache.get("block1")
        cache.get("block2")

        # Misses
        cache.get("block3")
        cache.get("block4")

        stats = cache.get_stats()
        assert stats['size'] == 2
        assert stats['hits'] == 2
        assert stats['misses'] == 2
        assert stats['hit_rate'] == 50.0

    def test_cache_clear(self):
        """Test cache clearing."""
        cache = BlockCache(max_size=10)

        cache.put("block1", "html1")
        cache.put("block2", "html2")
        cache.get("block1")

        cache.clear()

        stats = cache.get_stats()
        assert stats['size'] == 0
        assert stats['hits'] == 0
        assert stats['misses'] == 0


class TestDocumentBlock:
    """Test document block structure."""

    def test_block_compute_id(self):
        """Test block ID computation."""
        block = DocumentBlock(
            id='',
            start_line=0,
            end_line=5,
            content='= Title\n\nSome content',
            level=1
        )

        block_id = block.compute_id()
        assert len(block_id) == 16
        assert block_id.isalnum()

    def test_block_id_consistency(self):
        """Test same content produces same ID."""
        content = '= Title\n\nSome content'

        block1 = DocumentBlock(
            id='', start_line=0, end_line=5, content=content, level=1
        )
        block2 = DocumentBlock(
            id='', start_line=10, end_line=15, content=content, level=1
        )

        assert block1.compute_id() == block2.compute_id()

    def test_block_id_uniqueness(self):
        """Test different content produces different IDs."""
        block1 = DocumentBlock(
            id='', start_line=0, end_line=5, content='= Title 1', level=1
        )
        block2 = DocumentBlock(
            id='', start_line=0, end_line=5, content='= Title 2', level=1
        )

        assert block1.compute_id() != block2.compute_id()


class TestDocumentBlockSplitter:
    """Test document splitting into blocks."""

    def test_split_empty_document(self):
        """Test splitting empty document."""
        blocks = DocumentBlockSplitter.split('')
        assert len(blocks) == 0

    def test_split_single_title(self):
        """Test splitting document with single title."""
        source = '= Document Title\n\nSome content here.'
        blocks = DocumentBlockSplitter.split(source)

        assert len(blocks) == 1
        assert blocks[0].level == 1
        assert '= Document Title' in blocks[0].content

    def test_split_multiple_sections(self):
        """Test splitting document with multiple sections."""
        source = """= Title

== Section 1

Content for section 1.

== Section 2

Content for section 2.
"""
        blocks = DocumentBlockSplitter.split(source)

        assert len(blocks) == 3
        assert blocks[0].level == 1  # Title
        assert blocks[1].level == 2  # Section 1
        assert blocks[2].level == 2  # Section 2

    def test_split_nested_headings(self):
        """Test splitting with nested heading levels."""
        source = """= Title

== Section

=== Subsection

Content here.

==== Level 4

More content.
"""
        blocks = DocumentBlockSplitter.split(source)

        assert len(blocks) == 4
        assert blocks[0].level == 1  # =
        assert blocks[1].level == 2  # ==
        assert blocks[2].level == 3  # ===
        assert blocks[3].level == 4  # ====

    def test_split_preserves_line_numbers(self):
        """Test that block line numbers are correct."""
        source = """= Title
Content
== Section 1
More content
== Section 2
Final content"""

        blocks = DocumentBlockSplitter.split(source)

        assert blocks[0].start_line == 0
        assert blocks[1].start_line == 2
        assert blocks[2].start_line == 4

    def test_split_block_ids_computed(self):
        """Test that block IDs are computed."""
        source = """= Title

== Section
"""
        blocks = DocumentBlockSplitter.split(source)

        for block in blocks:
            assert block.id != ''
            assert len(block.id) == 16


class MockAsciiDocAPI:
    """Mock AsciiDoc API for testing."""

    def execute(self, infile, outfile, backend='html5'):
        """Mock execute method."""
        content = infile.read()
        # Simple mock rendering
        html = f"<div>{content}</div>"
        outfile.write(html)


class TestIncrementalPreviewRenderer:
    """Test incremental rendering."""

    def test_renderer_initialization(self):
        """Test renderer initializes correctly."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        assert renderer.is_enabled() is True
        assert renderer.asciidoc_api == api

    def test_renderer_enable_disable(self):
        """Test enabling and disabling renderer."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        renderer.enable(False)
        assert renderer.is_enabled() is False

        renderer.enable(True)
        assert renderer.is_enabled() is True

    def test_render_simple_document(self):
        """Test rendering simple document."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        source = '= Title\n\nSome content.'
        html = renderer.render(source)

        assert html is not None
        assert len(html) > 0

    def test_incremental_render_unchanged_content(self):
        """Test incremental render with unchanged content."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        source = """= Title

== Section 1

Content 1.

== Section 2

Content 2.
"""
        # First render
        html1 = renderer.render(source)

        # Get cache stats
        stats1 = renderer.get_cache_stats()

        # Second render (same content)
        html2 = renderer.render(source)

        # Get cache stats after second render
        stats2 = renderer.get_cache_stats()

        # Should have cache hits
        assert stats2['hits'] > stats1['hits']
        assert html1 == html2

    def test_incremental_render_changed_content(self):
        """Test incremental render with changed content."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        source1 = """= Title

== Section 1

Content 1.
"""
        source2 = """= Title

== Section 1

Content 1 MODIFIED.
"""
        # First render
        html1 = renderer.render(source1)

        # Second render with changes
        html2 = renderer.render(source2)

        # HTML should be different
        assert html1 != html2

    def test_cache_stats(self):
        """Test cache statistics."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        source = '= Title\n\nContent.'
        renderer.render(source)

        stats = renderer.get_cache_stats()

        assert 'size' in stats
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'hit_rate' in stats

    def test_clear_cache(self):
        """Test clearing cache."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        source = '= Title\n\nContent.'
        renderer.render(source)

        # Cache should have items
        stats1 = renderer.get_cache_stats()
        assert stats1['size'] > 0

        # Clear cache
        renderer.clear_cache()

        # Cache should be empty
        stats2 = renderer.get_cache_stats()
        assert stats2['size'] == 0

    def test_fallback_when_disabled(self):
        """Test fallback to full render when disabled."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        renderer.enable(False)

        source = '= Title\n\nContent.'
        html = renderer.render(source)

        # Should still render successfully
        assert html is not None
        assert len(html) > 0


@pytest.mark.performance
class TestIncrementalRenderingPerformance:
    """Performance tests for incremental rendering."""

    def test_large_document_performance(self):
        """Test rendering large document."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        # Create large document with many sections
        sections = []
        for i in range(50):
            sections.append(f"== Section {i}\n\nContent for section {i}.\n")

        source = "= Large Document\n\n" + "\n".join(sections)

        # First render
        import time
        start = time.time()
        html1 = renderer.render(source)
        first_render_time = time.time() - start

        # Second render (should be faster with cache)
        start = time.time()
        html2 = renderer.render(source)
        second_render_time = time.time() - start

        # Second render should use cache
        assert second_render_time < first_render_time
        assert html1 == html2

    def test_partial_edit_performance(self):
        """Test performance with partial edits."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        # Large document
        sections = []
        for i in range(30):
            sections.append(f"== Section {i}\n\nContent {i}.\n")

        source1 = "= Document\n\n" + "\n".join(sections)

        # First render
        renderer.render(source1)

        # Modify only one section
        sections[15] = "== Section 15 MODIFIED\n\nContent 15 CHANGED.\n"
        source2 = "= Document\n\n" + "\n".join(sections)

        # Second render should be fast (only one block changed)
        import time
        start = time.time()
        renderer.render(source2)
        edit_render_time = time.time() - start

        # Should be very fast (< 100ms for mock renderer)
        assert edit_render_time < 0.1

        stats = renderer.get_cache_stats()
        # Should have cache hits
        assert stats['hits'] > 0
