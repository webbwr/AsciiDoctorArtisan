"""
Tests for ParallelBlockRenderer - Multi-core rendering functionality.

Tests cover:
- Parallel rendering of multiple blocks
- Sequential fallback for small block counts
- Thread safety and ordering preservation
- Statistics tracking
- Enable/disable functionality
- Graceful error handling
"""

import pytest

from asciidoc_artisan.workers.block_splitter import DocumentBlock
from asciidoc_artisan.workers.parallel_block_renderer import ParallelBlockRenderer


class MockAsciiDocAPI:
    """Mock AsciiDoc API for testing."""

    attributes: dict[str, str] = {}

    def execute(self, infile: object, outfile: object, backend: str = "html5") -> None:
        """Mock execute that wraps content in div tags."""
        content = infile.read()  # type: ignore[union-attr]
        outfile.write(f"<div>{content}</div>")  # type: ignore[union-attr]


@pytest.fixture
def mock_api() -> MockAsciiDocAPI:
    """Create mock API instance."""
    return MockAsciiDocAPI()


@pytest.fixture
def renderer(mock_api: MockAsciiDocAPI) -> ParallelBlockRenderer:
    """Create parallel renderer with mock API."""
    return ParallelBlockRenderer(mock_api, max_workers=4)


def create_blocks(count: int) -> list[DocumentBlock]:
    """Create test blocks."""
    return [
        DocumentBlock(
            id=f"block_{i}",
            start_line=i * 2,
            end_line=i * 2 + 1,
            content=f"== Section {i}",
        )
        for i in range(count)
    ]


class TestParallelBlockRendererInit:
    """Test ParallelBlockRenderer initialization."""

    def test_init_with_default_workers(self, mock_api: MockAsciiDocAPI) -> None:
        """Test initialization with auto-detected worker count."""
        renderer = ParallelBlockRenderer(mock_api)
        assert renderer._max_workers >= 1
        assert renderer._max_workers <= 8  # MAX_WORKERS cap

    def test_init_with_custom_workers(self, mock_api: MockAsciiDocAPI) -> None:
        """Test initialization with custom worker count."""
        renderer = ParallelBlockRenderer(mock_api, max_workers=2)
        assert renderer._max_workers == 2

    def test_init_enabled_by_default(self, renderer: ParallelBlockRenderer) -> None:
        """Test parallel rendering is enabled by default."""
        assert renderer.is_enabled() is True


class TestParallelRendering:
    """Test parallel block rendering."""

    def test_render_preserves_order(self, renderer: ParallelBlockRenderer) -> None:
        """Test that parallel rendering preserves block order."""
        blocks = create_blocks(6)
        results = renderer.render_blocks_parallel(blocks)

        for i, (block, _) in enumerate(results):
            assert block.id == f"block_{i}"

    def test_render_sequential_for_few_blocks(self, renderer: ParallelBlockRenderer) -> None:
        """Test sequential fallback for small block counts."""
        blocks = create_blocks(2)  # Below MIN_BLOCKS_FOR_PARALLEL
        results = renderer.render_blocks_parallel(blocks)

        assert len(results) == 2
        stats = renderer.get_stats()
        assert stats["sequential_renders"] >= 1

    def test_render_empty_list(self, renderer: ParallelBlockRenderer) -> None:
        """Test rendering empty block list."""
        results = renderer.render_blocks_parallel([])
        assert results == []


class TestEnableDisable:
    """Test enable/disable functionality."""

    def test_disable_parallel_rendering(self, renderer: ParallelBlockRenderer) -> None:
        """Test disabling parallel rendering."""
        renderer.enable(False)
        assert renderer.is_enabled() is False

        blocks = create_blocks(5)
        results = renderer.render_blocks_parallel(blocks)

        # Should fall back to sequential
        assert len(results) == 5
        stats = renderer.get_stats()
        assert stats["sequential_renders"] >= 1

    def test_re_enable_parallel_rendering(self, renderer: ParallelBlockRenderer) -> None:
        """Test re-enabling parallel rendering."""
        renderer.enable(False)
        renderer.enable(True)
        assert renderer.is_enabled() is True


class TestStatistics:
    """Test statistics tracking."""

    def test_stats_initial_values(self, renderer: ParallelBlockRenderer) -> None:
        """Test initial statistics values."""
        stats = renderer.get_stats()
        assert stats["parallel_renders"] == 0
        assert stats["sequential_renders"] == 0
        assert stats["total_blocks_rendered"] == 0
        assert stats["enabled"] is True
        assert stats["max_workers"] == 4

    def test_stats_after_parallel_render(self, renderer: ParallelBlockRenderer) -> None:
        """Test statistics after parallel render."""
        blocks = create_blocks(5)
        renderer.render_blocks_parallel(blocks)

        stats = renderer.get_stats()
        assert stats["parallel_renders"] == 1
        assert stats["total_blocks_rendered"] == 5

    def test_stats_after_sequential_render(self, renderer: ParallelBlockRenderer) -> None:
        """Test statistics after sequential render."""
        blocks = create_blocks(2)
        renderer.render_blocks_parallel(blocks)

        stats = renderer.get_stats()
        assert stats["sequential_renders"] == 1
        assert stats["total_blocks_rendered"] == 2


class TestShutdown:
    """Test shutdown functionality."""

    def test_shutdown(self, renderer: ParallelBlockRenderer) -> None:
        """Test clean shutdown."""
        # First do a render to create the executor
        blocks = create_blocks(4)
        renderer.render_blocks_parallel(blocks)

        # Then shutdown
        renderer.shutdown()
        assert renderer._executor is None

    def test_shutdown_before_use(self, renderer: ParallelBlockRenderer) -> None:
        """Test shutdown when executor was never created."""
        renderer.shutdown()
        assert renderer._executor is None
