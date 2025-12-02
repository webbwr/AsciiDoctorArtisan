"""
Extended tests for incremental_renderer to achieve 100% coverage.

Tests for missing lines:
- Lines 47-48: ImportError when xxhash not available
- Lines 427-428, 435-436: Unused _create_block method (legacy/dead code)
"""

import sys
from unittest.mock import patch

import pytest

from asciidoc_artisan.workers.incremental_renderer import (
    DocumentBlockSplitter,
)


@pytest.mark.fr_018
@pytest.mark.fr_076
@pytest.mark.unit
class TestIncrementalRendererCoverage:
    """Tests to achieve 100% coverage for IncrementalRenderer."""

    def test_xxhash_import_error_fallback(self):
        """Test ImportError when xxhash is not available (lines 47-48).

        Note: HAS_XXHASH is now in block_splitter.py after MA refactoring.
        """
        # Mock sys.modules to simulate xxhash not being installed
        original_xxhash = sys.modules.get("xxhash")

        try:
            # Remove xxhash from sys.modules to trigger ImportError
            if "xxhash" in sys.modules:
                del sys.modules["xxhash"]

            # Mock the import to raise ImportError
            with patch.dict(sys.modules, {"xxhash": None}):
                # Force reimport of block_splitter to trigger import logic
                import importlib

                from asciidoc_artisan.workers import block_splitter

                importlib.reload(block_splitter)

                # Verify HAS_XXHASH is False when xxhash not available
                assert not block_splitter.HAS_XXHASH

                # Test that DocumentBlock can still compute IDs using MD5 fallback
                block = block_splitter.DocumentBlock(
                    id="",
                    start_line=0,
                    end_line=5,
                    content="Test content",
                    level=1,
                )
                block_id = block.compute_id()
                assert block_id is not None
                assert len(block_id) > 0
        finally:
            # Restore original state
            if original_xxhash is not None:
                sys.modules["xxhash"] = original_xxhash
            # Reload to restore normal state
            import importlib

            from asciidoc_artisan.workers import block_splitter

            importlib.reload(block_splitter)

    def test_create_block_legacy_method(self):
        """Test unused _create_block method (lines 427-428, 435-436)."""
        # This method appears to be legacy/dead code that's not called anywhere
        # in the codebase, but we can still test it for completeness
        lines = ["= Heading", "", "Some content", "", "More content"]

        # Call the unused _create_block method directly
        block = DocumentBlockSplitter._create_block(
            lines=lines,
            start_line=0,
            end_line=4,
            level=1,
        )

        assert block is not None
        # Verify basic block attributes
        assert block.start_line == 0
        assert block.end_line == 4
        assert block.level == 1
        # Lines 427-428 create content and DocumentBlock
        assert block.content == "= Heading\n\nSome content\n\nMore content"
        # Lines 435-436 compute and set the ID
        assert block.id is not None
        assert len(block.id) > 0
        # Verify it has the expected attributes of a DocumentBlock
        assert hasattr(block, "rendered_html")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
