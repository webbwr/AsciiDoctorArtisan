"""
Advanced tests for IncrementalPreviewRenderer - Cache and performance edge cases.

This test suite complements existing incremental_renderer tests with:
- Cache behavior (eviction, hash collision, invalidation, persistence, stats)
- Block splitting edge cases (no headings, 100+ headings, deep nesting, malformed, unicode)
- Performance scenarios (1000-heading docs, rapid edits, cache efficiency)

Phase 4A.3: 15 focused tests for critical incremental_renderer.py gaps
"""

from unittest.mock import Mock

import pytest

from asciidoc_artisan.workers.incremental_renderer import (
    BlockCache,
    DocumentBlock,
    DocumentBlockSplitter,
    IncrementalPreviewRenderer,
)

# ==============================================================================
# Cache Behavior Tests (5 tests)
# ==============================================================================


class TestBlockCacheAdvanced:
    """Test BlockCache with advanced scenarios."""

    def test_cache_eviction_when_exceeds_max_size(self):
        """Test LRU cache eviction when size exceeds MAX_CACHE_SIZE."""
        cache = BlockCache(max_size=3)

        # Add 4 blocks (should evict oldest)
        cache.put("block1", "<p>Block 1</p>")
        cache.put("block2", "<p>Block 2</p>")
        cache.put("block3", "<p>Block 3</p>")
        cache.put("block4", "<p>Block 4</p>")

        # block1 should be evicted (oldest)
        assert cache.get("block1") is None
        assert cache.get("block2") == "<p>Block 2</p>"
        assert cache.get("block3") == "<p>Block 3</p>"
        assert cache.get("block4") == "<p>Block 4</p>"

        stats = cache.get_stats()
        assert stats["size"] == 3  # Max size enforced

    def test_cache_hash_collision_handling(self):
        """Test cache behavior with duplicate block IDs (hash collision)."""
        cache = BlockCache(max_size=10)

        # Add block with ID "abc123"
        cache.put("abc123", "<p>First content</p>")
        assert cache.get("abc123") == "<p>First content</p>"

        # Add different content with same ID (simulates collision)
        cache.put("abc123", "<p>Second content</p>")
        assert cache.get("abc123") == "<p>Second content</p>"

        # Should have replaced, not duplicated
        stats = cache.get_stats()
        assert stats["size"] == 1

    def test_cache_invalidation_on_content_change(self):
        """Test cache updates when block content changes."""
        cache = BlockCache()

        # Original block
        block1 = DocumentBlock(
            id="block1", start_line=0, end_line=5, content="= Original Title"
        )
        block1.id = block1.compute_id()
        cache.put(block1.id, "<h1>Original Title</h1>")

        # Modified block (different content)
        block2 = DocumentBlock(
            id="block2", start_line=0, end_line=5, content="= Modified Title"
        )
        block2.id = block2.compute_id()

        # IDs should be different (content changed)
        assert block1.id != block2.id
        assert cache.get(block2.id) is None  # Cache miss for new content

    def test_cache_persistence_across_renders(self):
        """Test cache persists across multiple renders."""
        mock_api = Mock()
        mock_api.execute = Mock()

        renderer = IncrementalPreviewRenderer(mock_api)

        # First render
        source1 = "= Title\n\nParagraph 1"
        renderer.render(source1)

        # Get cache stats after first render
        stats1 = renderer.get_cache_stats()
        assert stats1["size"] > 0

        # Second render with same content
        renderer.render(source1)

        # Cache should have hits
        stats2 = renderer.get_cache_stats()
        assert stats2["hits"] > 0
        assert stats2["hit_rate"] > 0

    def test_cache_statistics_tracking(self):
        """Test cache hit/miss statistics are accurate."""
        cache = BlockCache()

        # Add 3 blocks
        cache.put("b1", "<p>1</p>")
        cache.put("b2", "<p>2</p>")
        cache.put("b3", "<p>3</p>")

        # 2 hits
        cache.get("b1")
        cache.get("b2")

        # 3 misses
        cache.get("b4")
        cache.get("b5")
        cache.get("b6")

        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 3
        assert stats["hit_rate"] == 40.0  # 2 / 5 * 100


# ==============================================================================
# Block Splitting Edge Cases (6 tests)
# ==============================================================================


class TestDocumentBlockSplitterEdgeCases:
    """Test DocumentBlockSplitter with edge cases."""

    def test_document_with_no_headings(self):
        """Test splitting document with no headings (single block)."""
        source = "Just a paragraph.\n\nAnother paragraph.\n\nNo headings here."
        blocks = DocumentBlockSplitter.split(source)

        # Should create one block for entire document
        assert len(blocks) == 1
        assert blocks[0].level == 0
        assert "Just a paragraph" in blocks[0].content

    def test_document_with_100_plus_headings(self):
        """Test splitting document with 100+ headings (many blocks)."""
        # Generate document with 150 headings
        lines = []
        for i in range(150):
            lines.append(f"== Section {i}")
            lines.append(f"Content for section {i}")

        source = "\n".join(lines)
        blocks = DocumentBlockSplitter.split(source)

        # Should create 150 blocks (one per heading)
        assert len(blocks) == 150
        assert all(block.level == 2 for block in blocks)

    def test_deeply_nested_headings(self):
        """Test splitting with 6 levels of nesting."""
        source = """= Level 0 Title
== Level 1 Section
=== Level 2 Subsection
==== Level 3 Sub-subsection
===== Level 4 Paragraph
====== Level 5 Subparagraph
Content at deepest level
"""
        blocks = DocumentBlockSplitter.split(source)

        # Should have 6 blocks (one per heading level)
        assert len(blocks) == 6
        assert blocks[0].level == 1  # = Title
        assert blocks[1].level == 2  # == Section
        assert blocks[2].level == 3  # === Subsection
        assert blocks[3].level == 4  # ==== Sub-subsection
        assert blocks[4].level == 5  # ===== Paragraph
        assert blocks[5].level == 6  # ====== Subparagraph

    def test_malformed_headings_without_space(self):
        """Test headings without space after '=' are not detected."""
        source = """===NoSpace
This should not be a heading

=== Correct Heading
This is a proper heading
"""
        blocks = DocumentBlockSplitter.split(source)

        # Only one heading should be detected (the correct one)
        assert len(blocks) == 2
        # First block contains malformed heading (not split)
        assert "===NoSpace" in blocks[0].content
        # Second block is the proper heading
        assert "Correct Heading" in blocks[1].content

    def test_empty_blocks_between_headings(self):
        """Test handling of empty blocks between headings."""
        source = """= Title

== Section 1

== Section 2

== Section 3
"""
        blocks = DocumentBlockSplitter.split(source)

        # Should have 4 blocks (title + 3 sections)
        assert len(blocks) == 4
        # Check levels
        assert blocks[0].level == 1  # Title
        assert blocks[1].level == 2  # Section 1
        assert blocks[2].level == 2  # Section 2
        assert blocks[3].level == 2  # Section 3

    def test_unicode_in_headings(self):
        """Test splitting with Unicode characters in headings."""
        source = """= 日本語タイトル
== Émoji 🚀 Section
=== Čeština Subsection
Content with Unicode: 你好世界
"""
        blocks = DocumentBlockSplitter.split(source)

        # Should handle Unicode without crashing
        assert len(blocks) == 3
        assert "日本語" in blocks[0].content
        assert "🚀" in blocks[1].content
        assert "Čeština" in blocks[2].content
        assert "你好世界" in blocks[2].content


# ==============================================================================
# Performance Scenarios (4 tests)
# ==============================================================================


class TestIncrementalRendererPerformance:
    """Test IncrementalPreviewRenderer performance scenarios."""

    def test_large_document_with_1000_headings(self):
        """Test rendering document with 1000 headings (stress test)."""
        mock_api = Mock()
        mock_api.execute = Mock(
            side_effect=lambda inf, outf, backend: outf.write("<p>Rendered</p>")
        )

        renderer = IncrementalPreviewRenderer(mock_api)

        # Generate 1000-heading document
        lines = []
        for i in range(1000):
            lines.append(f"== Heading {i}")
            lines.append(f"Content {i}")

        source = "\n".join(lines)

        # Should not crash or timeout
        html = renderer.render(source)
        assert html is not None
        assert len(html) > 0

        # Cache should have blocks
        stats = renderer.get_cache_stats()
        assert stats["size"] > 0

    def test_rapid_sequential_edits(self):
        """Test multiple rapid renders in succession."""
        mock_api = Mock()
        mock_api.execute = Mock(
            side_effect=lambda inf, outf, backend: outf.write("<p>Rendered</p>")
        )

        renderer = IncrementalPreviewRenderer(mock_api)

        # First render
        source1 = "= Title\n\n== Section 1\n\nStatic content\n\n== Section 2\n\nMore static content"
        renderer.render(source1)

        # Perform 10 rapid renders - keep Section 1 unchanged, modify Section 2
        for i in range(10):
            source = (
                f"= Title\n\n== Section 1\n\nStatic content\n\n== Section 2\n\nEdit {i}"
            )
            html = renderer.render(source)
            assert html is not None

        # Cache should have accumulated stats (Section 1 should be cached)
        stats = renderer.get_cache_stats()
        # With Section 1 staying the same, we should have cache hits
        assert stats["hits"] > 0  # Section 1 was cached and reused

    def test_cache_efficiency_with_repeated_edits(self):
        """Test cache efficiency when editing same section repeatedly."""
        mock_api = Mock()
        render_count = {"count": 0}

        def mock_execute(inf, outf, backend):
            render_count["count"] += 1
            outf.write("<p>Rendered</p>")

        mock_api.execute = Mock(side_effect=mock_execute)

        renderer = IncrementalPreviewRenderer(mock_api)

        # Initial render
        source1 = "= Title\n\n== Section 1\n\nContent\n\n== Section 2\n\nMore content"
        renderer.render(source1)
        initial_renders = render_count["count"]

        # Edit only Section 2 (Section 1 should be cached)
        source2 = "= Title\n\n== Section 1\n\nContent\n\n== Section 2\n\nEdited content"
        renderer.render(source2)
        final_renders = render_count["count"]

        # Should render fewer blocks than total (cache hit for Section 1)
        assert final_renders < initial_renders + 3  # Not all blocks re-rendered

        # Cache hit rate should be reasonable
        stats = renderer.get_cache_stats()
        assert stats["hit_rate"] > 0

    def test_disabled_incremental_rendering_falls_back(self):
        """Test that disabling incremental rendering falls back to full render."""
        mock_api = Mock()
        mock_api.execute = Mock(
            side_effect=lambda inf, outf, backend: outf.write("<p>Full render</p>")
        )

        renderer = IncrementalPreviewRenderer(mock_api)

        # Disable incremental rendering
        renderer.enable(False)
        assert not renderer.is_enabled()

        # Render should fall back to full render
        source = "= Title\n\nContent"
        html = renderer.render(source)

        # Should render without using cache
        assert "<p>Full render</p>" in html

        # Cache should be empty
        stats = renderer.get_cache_stats()
        assert stats["size"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
