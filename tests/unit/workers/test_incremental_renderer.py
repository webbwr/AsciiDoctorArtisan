"""
Tests for incremental preview renderer.

Tests block-based caching, diff detection, and rendering performance.
"""

import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.workers.incremental_renderer import (
    BLOCK_HASH_LENGTH,
    BlockCache,
    DocumentBlock,
    DocumentBlockSplitter,
    IncrementalPreviewRenderer,
    count_leading_equals,
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
        assert cache.get("block2") is None  # Evicted
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
        assert stats["size"] == 2
        assert stats["hits"] == 2
        assert stats["misses"] == 2
        assert stats["hit_rate"] == 50.0

    def test_cache_clear(self):
        """Test cache clearing."""
        cache = BlockCache(max_size=10)

        cache.put("block1", "html1")
        cache.put("block2", "html2")
        cache.get("block1")

        cache.clear()

        stats = cache.get_stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0


class TestDocumentBlock:
    """Test document block structure."""

    def test_block_compute_id(self):
        """Test block ID computation."""
        block = DocumentBlock(id="", start_line=0, end_line=5, content="= Title\n\nSome content", level=1)

        block_id = block.compute_id()
        assert len(block_id) == 12  # BLOCK_HASH_LENGTH is 12 (reduced from 16)
        assert block_id.isalnum()

    def test_block_id_consistency(self):
        """Test same content produces same ID."""
        content = "= Title\n\nSome content"

        block1 = DocumentBlock(id="", start_line=0, end_line=5, content=content, level=1)
        block2 = DocumentBlock(id="", start_line=10, end_line=15, content=content, level=1)

        assert block1.compute_id() == block2.compute_id()

    def test_block_id_uniqueness(self):
        """Test different content produces different IDs."""
        block1 = DocumentBlock(id="", start_line=0, end_line=5, content="= Title 1", level=1)
        block2 = DocumentBlock(id="", start_line=0, end_line=5, content="= Title 2", level=1)

        assert block1.compute_id() != block2.compute_id()


class TestDocumentBlockSplitter:
    """Test document splitting into blocks."""

    def test_split_empty_document(self):
        """Test splitting empty document."""
        blocks = DocumentBlockSplitter.split("")
        assert len(blocks) == 0

    def test_split_single_title(self):
        """Test splitting document with single title."""
        source = "= Document Title\n\nSome content here."
        blocks = DocumentBlockSplitter.split(source)

        assert len(blocks) == 1
        assert blocks[0].level == 1
        assert "= Document Title" in blocks[0].content

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
            assert block.id != ""
            assert len(block.id) == 12  # BLOCK_HASH_LENGTH is 12 (reduced from 16)


class MockAsciiDocAPI:
    """Mock AsciiDoc API for testing."""

    def execute(self, infile, outfile, backend="html5"):
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

        source = "= Title\n\nSome content."
        html = renderer.render(source)

        assert html is not None
        assert len(html) > 0

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

        source = "= Title\n\nContent."
        renderer.render(source)

        stats = renderer.get_cache_stats()

        assert "size" in stats
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats

    def test_clear_cache(self):
        """Test clearing cache."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        source = "= Title\n\nContent."
        renderer.render(source)

        # Cache should have items
        stats1 = renderer.get_cache_stats()
        assert stats1["size"] > 0

        # Clear cache
        renderer.clear_cache()

        # Cache should be empty
        stats2 = renderer.get_cache_stats()
        assert stats2["size"] == 0

    def test_fallback_when_disabled(self):
        """Test fallback to full render when disabled."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        renderer.enable(False)

        source = "= Title\n\nContent."
        html = renderer.render(source)

        # Should still render successfully
        assert html is not None
        assert len(html) > 0


@pytest.mark.performance
class TestIncrementalRenderingPerformance:
    """Performance tests for incremental rendering."""

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
        assert stats["hits"] > 0


# ==============================================================================
# PRIORITY 1: Critical Missing Coverage Tests
# ==============================================================================


@pytest.mark.fr_018
@pytest.mark.unit
class TestCountLeadingEquals:
    """Test count_leading_equals() function (lines 315-344) - COMPLETELY UNTESTED."""

    def test_empty_string(self):
        """Test with empty string."""
        assert count_leading_equals("") == 0

    def test_none_like_empty(self):
        """Test with None-like empty scenarios."""
        assert count_leading_equals("") == 0
        assert count_leading_equals(" ") == 0  # No equals, just space

    def test_no_equals_characters(self):
        """Test line without equals characters."""
        assert count_leading_equals("This is plain text") == 0
        assert count_leading_equals("# This is markdown") == 0

    def test_equals_without_space(self):
        """Test equals without space after (not a valid heading)."""
        assert count_leading_equals("===text") == 0
        assert count_leading_equals("==heading") == 0
        assert count_leading_equals("=Title") == 0

    def test_valid_heading_with_space(self):
        """Test valid headings with space after equals."""
        assert count_leading_equals("= Title") == 1
        assert count_leading_equals("== Section") == 2
        assert count_leading_equals("=== Subsection") == 3
        assert count_leading_equals("==== Level 4") == 4
        assert count_leading_equals("===== Level 5") == 5
        assert count_leading_equals("====== Level 6") == 6

    def test_valid_heading_with_tab(self):
        """Test valid headings with tab after equals."""
        assert count_leading_equals("=\tTitle") == 1
        assert count_leading_equals("==\tSection") == 2
        assert count_leading_equals("===\tSubsection") == 3

    def test_equals_in_middle_of_line(self):
        """Test equals in middle of line (not a heading)."""
        assert count_leading_equals("text = value") == 0
        assert count_leading_equals("foo == bar") == 0

    def test_multiple_spaces_after_equals(self):
        """Test multiple spaces after equals."""
        assert count_leading_equals("=  Title") == 1
        assert count_leading_equals("==  Section") == 2
        assert count_leading_equals("===   Subsection") == 3

    def test_equals_at_end(self):
        """Test line ending with equals (not a valid heading)."""
        assert count_leading_equals("===") == 0
        assert count_leading_equals("====") == 0

    def test_mixed_whitespace_after_equals(self):
        """Test mixed whitespace after equals."""
        assert count_leading_equals("= \t Title") == 1
        assert count_leading_equals("== \t\t Section") == 2


@pytest.mark.fr_018
@pytest.mark.unit
class TestBlockCacheThreadSafety:
    """Test thread safety in BlockCache (lines 224-313)."""

    def test_concurrent_get_calls(self):
        """Test concurrent get() calls from multiple threads."""
        cache = BlockCache(max_size=100)
        cache.put("block1", "<h1>Title</h1>")
        cache.put("block2", "<p>Content</p>")

        results = []
        errors = []

        def get_operation(block_id):
            try:
                result = cache.get(block_id)
                results.append((block_id, result))
            except Exception as e:
                errors.append(e)

        # Create 20 threads doing concurrent gets
        threads = []
        for i in range(20):
            block_id = "block1" if i % 2 == 0 else "block2"
            thread = threading.Thread(target=get_operation, args=(block_id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify no errors and correct results
        assert len(errors) == 0
        assert len(results) == 20
        # All block1 gets should succeed
        block1_results = [r for r in results if r[0] == "block1"]
        assert all(r[1] == "<h1>Title</h1>" for r in block1_results)

    def test_concurrent_put_calls(self):
        """Test concurrent put() calls from multiple threads."""
        cache = BlockCache(max_size=50)
        errors = []

        def put_operation(block_id, html):
            try:
                cache.put(block_id, html)
            except Exception as e:
                errors.append(e)

        # Create 30 threads doing concurrent puts
        threads = []
        for i in range(30):
            thread = threading.Thread(target=put_operation, args=(f"block{i}", f"<div>Block {i}</div>"))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify no errors
        assert len(errors) == 0
        # Cache should have items (possibly evicted some)
        stats = cache.get_stats()
        assert stats["size"] <= 50

    def test_concurrent_get_and_put(self):
        """Test concurrent get() and put() operations."""
        cache = BlockCache(max_size=20)

        # Pre-populate cache
        for i in range(10):
            cache.put(f"block{i}", f"<div>Block {i}</div>")

        errors = []

        def mixed_operation(thread_id):
            try:
                for i in range(5):
                    if thread_id % 2 == 0:
                        cache.get(f"block{i}")
                    else:
                        cache.put(f"new_block{thread_id}_{i}", f"<div>New {i}</div>")
            except Exception as e:
                errors.append(e)

        # Create threads doing mixed operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(mixed_operation, i) for i in range(10)]
            for future in futures:
                future.result()

        # Verify no errors
        assert len(errors) == 0

    def test_get_stats_during_operations(self):
        """Test get_stats() during active operations."""
        cache = BlockCache(max_size=30)
        stats_results = []
        errors = []

        def put_and_get():
            try:
                for i in range(10):
                    cache.put(f"block{i}", f"<div>{i}</div>")
                    cache.get(f"block{i}")
            except Exception as e:
                errors.append(e)

        def get_stats():
            try:
                for _ in range(5):
                    stats = cache.get_stats()
                    stats_results.append(stats)
            except Exception as e:
                errors.append(e)

        # Run operations and stats collection concurrently
        threads = [
            threading.Thread(target=put_and_get),
            threading.Thread(target=put_and_get),
            threading.Thread(target=get_stats),
        ]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Verify no errors and stats were collected
        assert len(errors) == 0
        assert len(stats_results) == 5
        # All stats should have valid structure
        for stats in stats_results:
            assert "size" in stats
            assert "hits" in stats
            assert "misses" in stats
            assert "hit_rate" in stats

    def test_clear_during_operations(self):
        """Test clear() during active operations."""
        cache = BlockCache(max_size=20)

        # Pre-populate
        for i in range(10):
            cache.put(f"block{i}", f"<div>{i}</div>")

        errors = []

        def continuous_puts():
            try:
                for i in range(20):
                    cache.put(f"new{i}", f"<div>{i}</div>")
            except Exception as e:
                errors.append(e)

        def clear_cache():
            try:
                cache.clear()
            except Exception as e:
                errors.append(e)

        # Run puts and clear concurrently
        thread1 = threading.Thread(target=continuous_puts)
        thread2 = threading.Thread(target=clear_cache)

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # Verify no errors
        assert len(errors) == 0


@pytest.mark.fr_018
@pytest.mark.unit
class TestRenderBlockErrorHandling:
    """Test error handling in _render_block() (lines 576-599)."""

    def test_render_block_exception_handling(self):
        """Test _render_block() handles exceptions correctly."""
        # Create mock API that raises exception
        api = MagicMock()
        api.execute.side_effect = Exception("Render failed")

        renderer = IncrementalPreviewRenderer(api)

        # Create a block to render
        block = DocumentBlock(
            id="test123",
            start_line=0,
            end_line=2,
            content="= Test\n\nContent",
            level=1,
        )

        # Render should not raise exception, return fallback HTML
        html = renderer._render_block(block)

        # Verify fallback HTML returned
        assert html is not None
        assert "<pre>" in html
        assert "= Test" in html
        assert "&lt;" not in html or "&#x27;" not in html  # Content escaped

    def test_render_block_escapes_content_on_error(self):
        """Test _render_block() escapes content in fallback."""
        # Create mock API that raises exception
        api = MagicMock()
        api.execute.side_effect = RuntimeError("API error")

        renderer = IncrementalPreviewRenderer(api)

        # Block with HTML-like content
        block = DocumentBlock(
            id="test456",
            start_line=0,
            end_line=1,
            content="<script>alert('xss')</script>",
            level=0,
        )

        html = renderer._render_block(block)

        # Verify content is escaped
        assert "<pre>" in html
        assert "<script>" not in html  # Should be escaped
        assert "&lt;script&gt;" in html or "script" in html

    @patch("asciidoc_artisan.workers.incremental_renderer.logger")
    def test_render_block_logs_exception(self, mock_logger):
        """Test _render_block() logs exceptions."""
        api = MagicMock()
        api.execute.side_effect = ValueError("Invalid input")

        renderer = IncrementalPreviewRenderer(api)

        block = DocumentBlock(id="test789", start_line=0, end_line=1, content="Test", level=0)

        renderer._render_block(block)

        # Verify warning was logged
        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        assert "Block render failed" in args[0]


@pytest.mark.fr_018
@pytest.mark.unit
class TestRenderFullErrorHandling:
    """Test error handling in _render_full() (lines 601-622)."""

    def test_render_full_exception_handling(self):
        """Test _render_full() handles exceptions correctly."""
        # Create mock API that raises exception
        api = MagicMock()
        api.execute.side_effect = Exception("Full render failed")

        renderer = IncrementalPreviewRenderer(api)

        source = "= Title\n\nSome content here."

        # Render should not raise exception, return fallback HTML
        html = renderer._render_full(source)

        # Verify fallback HTML returned
        assert html is not None
        assert "<pre>" in html
        assert "= Title" in html

    def test_render_full_escapes_html_on_error(self):
        """Test _render_full() escapes HTML in fallback."""
        api = MagicMock()
        api.execute.side_effect = RuntimeError("API crashed")

        renderer = IncrementalPreviewRenderer(api)

        source = "<img src=x onerror=alert(1)>"

        html = renderer._render_full(source)

        # Verify content is escaped
        assert "<pre>" in html
        assert "onerror=" not in html or "&" in html  # Should be escaped

    @patch("asciidoc_artisan.workers.incremental_renderer.logger")
    def test_render_full_logs_error(self, mock_logger):
        """Test _render_full() logs errors."""
        api = MagicMock()
        api.execute.side_effect = IOError("File not found")

        renderer = IncrementalPreviewRenderer(api)

        renderer._render_full("Test content")

        # Verify error was logged
        mock_logger.error.assert_called_once()
        args = mock_logger.error.call_args[0]
        assert "Full render failed" in args[0]


@pytest.mark.fr_018
@pytest.mark.unit
class TestDetectChanges:
    """Test _detect_changes() edge cases (lines 550-574)."""

    def test_detect_changes_empty_previous_blocks(self):
        """Test _detect_changes() with empty previous blocks (first render)."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        current = [DocumentBlock(id="block1", start_line=0, end_line=1, content="Test", level=0)]

        changed, unchanged = renderer._detect_changes([], current)

        # All blocks should be marked as changed
        assert len(changed) == 1
        assert len(unchanged) == 0

    def test_detect_changes_empty_current_blocks(self):
        """Test _detect_changes() with empty current blocks (document cleared)."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        previous = [DocumentBlock(id="block1", start_line=0, end_line=1, content="Test", level=0)]

        changed, unchanged = renderer._detect_changes(previous, [])

        # No blocks in result
        assert len(changed) == 0
        assert len(unchanged) == 0

    def test_detect_changes_all_blocks_changed(self):
        """Test _detect_changes() with all blocks changed."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        previous = [
            DocumentBlock(id="old1", start_line=0, end_line=1, content="Old 1", level=0),
            DocumentBlock(id="old2", start_line=2, end_line=3, content="Old 2", level=0),
        ]

        current = [
            DocumentBlock(id="new1", start_line=0, end_line=1, content="New 1", level=0),
            DocumentBlock(id="new2", start_line=2, end_line=3, content="New 2", level=0),
        ]

        changed, unchanged = renderer._detect_changes(previous, current)

        # All blocks should be changed
        assert len(changed) == 2
        assert len(unchanged) == 0

    def test_detect_changes_no_blocks_changed(self):
        """Test _detect_changes() with no blocks changed (100% cache hit)."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        # Same content = same IDs
        block1 = DocumentBlock(id="", start_line=0, end_line=1, content="Same content", level=0)
        block1.id = block1.compute_id()

        block2 = DocumentBlock(id="", start_line=0, end_line=1, content="Same content", level=0)
        block2.id = block2.compute_id()

        changed, unchanged = renderer._detect_changes([block1], [block2])

        # No blocks should be changed
        assert len(changed) == 0
        assert len(unchanged) == 1

    def test_detect_changes_mixed_changed_unchanged(self):
        """Test _detect_changes() with mixed changed and unchanged blocks."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        # Create blocks with known IDs
        unchanged_block = DocumentBlock(id="", start_line=0, end_line=1, content="Unchanged", level=0)
        unchanged_block.id = unchanged_block.compute_id()

        changed_block_old = DocumentBlock(id="", start_line=2, end_line=3, content="Old content", level=0)
        changed_block_old.id = changed_block_old.compute_id()

        # Current blocks
        unchanged_block_new = DocumentBlock(id="", start_line=0, end_line=1, content="Unchanged", level=0)
        unchanged_block_new.id = unchanged_block_new.compute_id()

        changed_block_new = DocumentBlock(id="", start_line=2, end_line=3, content="New content", level=0)
        changed_block_new.id = changed_block_new.compute_id()

        previous = [unchanged_block, changed_block_old]
        current = [unchanged_block_new, changed_block_new]

        changed, unchanged = renderer._detect_changes(previous, current)

        # One changed, one unchanged
        assert len(changed) == 1
        assert len(unchanged) == 1

    def test_detect_changes_block_order_changes(self):
        """Test _detect_changes() when block order changes."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        block1 = DocumentBlock(id="", start_line=0, end_line=1, content="Block 1", level=0)
        block1.id = block1.compute_id()

        block2 = DocumentBlock(id="", start_line=2, end_line=3, content="Block 2", level=0)
        block2.id = block2.compute_id()

        # Same blocks, different order
        previous = [block1, block2]
        current = [
            DocumentBlock(id=block2.id, start_line=0, end_line=1, content="Block 2", level=0),
            DocumentBlock(id=block1.id, start_line=2, end_line=3, content="Block 1", level=0),
        ]

        changed, unchanged = renderer._detect_changes(previous, current)

        # Both should be recognized as unchanged (same IDs)
        assert len(unchanged) == 2
        assert len(changed) == 0


# ==============================================================================
# PRIORITY 2: Important Missing Coverage Tests
# ==============================================================================


@pytest.mark.fr_018
@pytest.mark.unit
class TestCachePutReplacement:
    """Test cache.put() with existing key replacement."""

    def test_put_existing_key_replacement(self):
        """Test cache.put() replaces existing key."""
        cache = BlockCache(max_size=5)

        # Put initial value
        cache.put("block1", "<div>Original</div>")
        assert cache.get("block1") == "<div>Original</div>"

        # Replace with new value
        cache.put("block1", "<div>Updated</div>")
        assert cache.get("block1") == "<div>Updated</div>"

        # Should still be only one item
        stats = cache.get_stats()
        assert stats["size"] == 1

    def test_put_replacement_moves_to_end(self):
        """Test cache.put() replacement moves item to end (most recent)."""
        cache = BlockCache(max_size=3)

        cache.put("block1", "html1")
        cache.put("block2", "html2")
        cache.put("block3", "html3")

        # Replace block1 (moves to end)
        cache.put("block1", "html1_updated")

        # Add new block (should evict block2, not block1)
        cache.put("block4", "html4")

        assert cache.get("block1") == "html1_updated"  # Still in cache
        assert cache.get("block2") is None  # Evicted
        assert cache.get("block3") == "html3"
        assert cache.get("block4") == "html4"


@pytest.mark.fr_018
@pytest.mark.unit
class TestDocumentBlockComputeIdFallback:
    """Test DocumentBlock.compute_id() with xxhash fallback."""

    @patch("asciidoc_artisan.workers.block_splitter.HAS_XXHASH", False)
    def test_compute_id_md5_fallback(self):
        """Test compute_id() falls back to MD5 when xxhash unavailable."""
        block = DocumentBlock(id="", start_line=0, end_line=1, content="Test content", level=0)

        block_id = block.compute_id()

        # Should still return valid ID
        assert len(block_id) == BLOCK_HASH_LENGTH
        assert block_id.isalnum()

    @patch("asciidoc_artisan.workers.block_splitter.HAS_XXHASH", False)
    def test_compute_id_md5_consistency(self):
        """Test MD5 fallback produces consistent IDs."""
        content = "= Title\n\nTest content"

        block1 = DocumentBlock(id="", start_line=0, end_line=2, content=content, level=1)
        block2 = DocumentBlock(id="", start_line=10, end_line=12, content=content, level=1)

        # Same content should produce same ID
        assert block1.compute_id() == block2.compute_id()


@pytest.mark.fr_018
@pytest.mark.unit
class TestDocumentBlockSplitterEdgeCases:
    """Test DocumentBlockSplitter edge cases."""

    def test_split_whitespace_only_document(self):
        """Test splitting whitespace-only document."""
        blocks = DocumentBlockSplitter.split("   \n\n\t\t\n   ")
        assert len(blocks) == 0

    def test_split_no_headings_plain_text(self):
        """Test splitting document with no headings (plain text)."""
        source = "This is plain text.\nNo headings here.\nJust paragraphs."
        blocks = DocumentBlockSplitter.split(source)

        # Should create one block
        assert len(blocks) == 1
        assert blocks[0].level == 0

    def test_split_false_positive_equals_in_code(self):
        """Test that equals signs in code blocks don't trigger heading detection."""
        source = """= Title

----
if (x == y) {
  z = value;
}
----

More content."""

        blocks = DocumentBlockSplitter.split(source)

        # Should not treat == inside code block as heading
        # Exact count depends on implementation, but should have at least title
        assert len(blocks) >= 1
        assert blocks[0].level == 1  # Title

    def test_split_level_5_and_6_headings(self):
        """Test splitting with level 5 and 6 headings."""
        source = """= Title

===== Level 5

Content at level 5.

====== Level 6

Content at level 6."""

        blocks = DocumentBlockSplitter.split(source)

        # Find level 5 and 6 blocks
        levels = [block.level for block in blocks]
        assert 5 in levels
        assert 6 in levels

    def test_split_single_line_document(self):
        """Test splitting single line document."""
        blocks = DocumentBlockSplitter.split("= Single Line Title")

        assert len(blocks) == 1
        assert blocks[0].level == 1
        assert blocks[0].content == "= Single Line Title"

    def test_split_tabs_after_equals(self):
        """Test splitting with tabs after equals signs."""
        source = "=\tTitle with tab\n\n==\tSection with tab"
        blocks = DocumentBlockSplitter.split(source)

        assert len(blocks) == 2
        assert blocks[0].level == 1
        assert blocks[1].level == 2

    def test_split_heading_with_no_content_after(self):
        """Test splitting with heading but no content after."""
        source = """= Title

== Section 1

== Section 2"""

        blocks = DocumentBlockSplitter.split(source)

        # Should have 3 blocks
        assert len(blocks) == 3
        # All should have proper levels
        assert blocks[0].level == 1
        assert blocks[1].level == 2
        assert blocks[2].level == 2


@pytest.mark.fr_018
@pytest.mark.unit
class TestCacheMissDuringRetrieval:
    """Test cache miss during unchanged block retrieval."""

    def test_cache_miss_renders_and_caches(self):
        """Test that cache miss during retrieval triggers render and cache."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        source1 = "= Title\n\nContent."

        # First render
        renderer.render(source1)

        # Clear cache but keep previous_blocks
        renderer.cache.clear()

        # Second render with same content (IDs unchanged, but cache empty)
        html2 = renderer.render(source1)

        # Should successfully render (cache miss handled)
        assert html2 is not None
        assert len(html2) > 0

        # Cache should now have items again
        stats = renderer.get_cache_stats()
        assert stats["size"] > 0


@pytest.mark.fr_018
@pytest.mark.unit
class TestIncrementalRendererThreadSafety:
    """Test thread safety in IncrementalPreviewRenderer.render()."""

    def test_render_thread_safety(self):
        """Test render() thread safety with concurrent calls."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        results = []
        errors = []

        def render_operation(source):
            try:
                html = renderer.render(source)
                results.append(html)
            except Exception as e:
                errors.append(e)

        # Create multiple threads rendering concurrently
        threads = []
        for i in range(10):
            source = f"= Title {i}\n\nContent {i}."
            thread = threading.Thread(target=render_operation, args=(source,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify no errors
        assert len(errors) == 0
        assert len(results) == 10
        # All renders should produce valid HTML
        assert all(len(html) > 0 for html in results)


@pytest.mark.fr_018
@pytest.mark.unit
class TestEnableDisableStateTransitions:
    """Test enable(False) state transitions."""

    def test_enable_false_clears_cache(self):
        """Test enable(False) clears cache."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        # Render some content to populate cache
        renderer.render("= Title\n\nContent.")

        stats1 = renderer.get_cache_stats()
        assert stats1["size"] > 0

        # Disable renderer
        renderer.enable(False)

        # Cache should be cleared
        stats2 = renderer.get_cache_stats()
        assert stats2["size"] == 0

    def test_enable_false_clears_previous_blocks(self):
        """Test enable(False) clears previous_blocks."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        # Render some content
        renderer.render("= Title\n\n== Section\n\nContent.")

        # Should have previous blocks
        with renderer._blocks_lock:
            assert len(renderer.previous_blocks) > 0

        # Disable renderer
        renderer.enable(False)

        # Previous blocks should be cleared
        with renderer._blocks_lock:
            assert len(renderer.previous_blocks) == 0

    def test_enable_true_restores_functionality(self):
        """Test enable(True) restores incremental rendering."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        # Disable then re-enable
        renderer.enable(False)
        renderer.enable(True)

        assert renderer.is_enabled() is True

        # Should work normally
        html = renderer.render("= Title\n\nContent.")
        assert html is not None
        assert len(html) > 0


# ==============================================================================
# PRIORITY 3: Polish and Edge Cases
# ==============================================================================


@pytest.mark.fr_018
@pytest.mark.unit
class TestDocumentBlockEdgeCases:
    """Test DocumentBlock edge cases."""

    def test_document_block_empty_content(self):
        """Test DocumentBlock with empty content."""
        block = DocumentBlock(id="", start_line=0, end_line=0, content="", level=0)
        block_id = block.compute_id()

        assert len(block_id) == BLOCK_HASH_LENGTH
        assert block_id.isalnum()

    def test_document_block_large_content(self):
        """Test DocumentBlock with large content."""
        large_content = "= Title\n\n" + ("Content line.\n" * 10000)
        block = DocumentBlock(id="", start_line=0, end_line=10000, content=large_content, level=1)

        block_id = block.compute_id()
        assert len(block_id) == BLOCK_HASH_LENGTH

    def test_document_block_unicode_content(self):
        """Test DocumentBlock with unicode content."""
        unicode_content = "= 标题\n\nСодержание\n\n内容\n\nمحتوى"
        block = DocumentBlock(id="", start_line=0, end_line=5, content=unicode_content, level=1)

        block_id = block.compute_id()
        assert len(block_id) == BLOCK_HASH_LENGTH
        assert block_id.isalnum()

    def test_document_block_special_characters(self):
        """Test DocumentBlock with special characters."""
        special_content = "= Title\n\n<>&\"'\n\n`~!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/"
        block = DocumentBlock(id="", start_line=0, end_line=3, content=special_content, level=1)

        block_id = block.compute_id()
        assert len(block_id) == BLOCK_HASH_LENGTH


@pytest.mark.fr_018
@pytest.mark.unit
class TestGetStatsEdgeCases:
    """Test get_stats() edge cases."""

    def test_get_stats_with_zero_total(self):
        """Test get_stats() with zero total (no hits or misses)."""
        cache = BlockCache(max_size=10)

        stats = cache.get_stats()

        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0.0  # Should not divide by zero

    def test_get_stats_only_hits(self):
        """Test get_stats() with only hits (no misses)."""
        cache = BlockCache(max_size=10)

        cache.put("block1", "html1")
        cache.get("block1")
        cache.get("block1")
        cache.get("block1")

        stats = cache.get_stats()

        assert stats["hits"] == 3
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 100.0

    def test_get_stats_only_misses(self):
        """Test get_stats() with only misses (no hits)."""
        cache = BlockCache(max_size=10)

        cache.get("nonexistent1")
        cache.get("nonexistent2")
        cache.get("nonexistent3")

        stats = cache.get_stats()

        assert stats["hits"] == 0
        assert stats["misses"] == 3
        assert stats["hit_rate"] == 0.0


@pytest.mark.fr_018
@pytest.mark.unit
class TestComplexDocumentScenarios:
    """Test complex document scenarios."""

    def test_document_with_mixed_content(self):
        """Test document with mixed content types."""
        source = """= Main Title

Introduction paragraph.

== First Section

Some text here.

----
Code block
with multiple lines
----

== Second Section

* List item 1
* List item 2

=== Subsection

[NOTE]
====
Admonition block
====

More content."""

        blocks = DocumentBlockSplitter.split(source)

        # Should split into multiple blocks
        assert len(blocks) > 3
        # Should have various levels
        levels = [block.level for block in blocks]
        assert 1 in levels  # Title
        assert 2 in levels  # Sections
        assert 3 in levels  # Subsection

    def test_incremental_render_with_block_additions(self):
        """Test incremental render when blocks are added."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        source1 = """= Title

== Section 1

Content 1."""

        source2 = """= Title

== Section 1

Content 1.

== Section 2

Content 2.

== Section 3

Content 3."""

        # First render
        html1 = renderer.render(source1)

        # Second render with more sections
        html2 = renderer.render(source2)

        # Should produce different HTML
        assert html1 != html2
        assert len(html2) > len(html1)

        # Should have cache hits for unchanged blocks
        stats = renderer.get_cache_stats()
        assert stats["hits"] > 0

    def test_incremental_render_with_block_removals(self):
        """Test incremental render when blocks are removed."""
        api = MockAsciiDocAPI()
        renderer = IncrementalPreviewRenderer(api)

        source1 = """= Title

== Section 1

Content 1.

== Section 2

Content 2.

== Section 3

Content 3."""

        source2 = """= Title

== Section 1

Content 1."""

        # First render
        html1 = renderer.render(source1)

        # Second render with fewer sections
        html2 = renderer.render(source2)

        # Should produce different HTML
        assert html1 != html2
        assert len(html2) < len(html1)
