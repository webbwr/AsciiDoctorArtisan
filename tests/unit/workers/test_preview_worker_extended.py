"""
Extended unit tests for PreviewWorker - Coverage completion.

This test suite covers remaining uncovered code paths in preview_worker.py
to achieve 100% coverage (Phase 2.4 of test coverage push).
"""

from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.workers import PreviewWorker


@pytest.mark.unit
class TestInitializeAsciiDocErrors:
    """Test error handling in initialize_asciidoc."""

    @patch("asciidoc_artisan.workers.preview_worker.ASCIIDOC3_AVAILABLE", True)
    @patch("asciidoc_artisan.workers.preview_worker.AsciiDoc3API")
    def test_initialize_asciidoc_exception_handling(self, mock_api_class):
        """Test initialize_asciidoc handles exceptions gracefully."""
        # Mock AsciiDoc3API to raise exception
        mock_api_class.side_effect = RuntimeError("Failed to initialize")

        worker = PreviewWorker()

        # Should not crash
        worker.initialize_asciidoc("/path/to/asciidoc3.py")

        # API should remain None
        assert worker._asciidoc_api is None

    @patch("asciidoc_artisan.workers.preview_worker.ASCIIDOC3_AVAILABLE", True)
    @patch(
        "asciidoc_artisan.workers.preview_worker.INCREMENTAL_RENDERER_AVAILABLE", True
    )
    @patch("asciidoc_artisan.workers.preview_worker.IncrementalPreviewRenderer")
    @patch("asciidoc_artisan.workers.preview_worker.AsciiDoc3API")
    def test_initialize_with_incremental_renderer_exception(
        self, mock_api_class, mock_incremental_class
    ):
        """Test initialize handles incremental renderer exception."""
        mock_api_instance = MagicMock()
        mock_api_class.return_value = mock_api_instance

        # Incremental renderer init raises exception
        mock_incremental_class.side_effect = RuntimeError("Incremental init failed")

        worker = PreviewWorker()

        # Should not crash
        worker.initialize_asciidoc("/path/to/asciidoc3.py")

        # API should be initialized, but incremental renderer should be None
        assert worker._asciidoc_api is not None
        assert worker._incremental_renderer is None

    @patch("asciidoc_artisan.workers.preview_worker.ASCIIDOC3_AVAILABLE", True)
    @patch(
        "asciidoc_artisan.workers.preview_worker.INCREMENTAL_RENDERER_AVAILABLE", True
    )
    @patch(
        "asciidoc_artisan.workers.preview_worker.PREDICTIVE_RENDERER_AVAILABLE", True
    )
    @patch("asciidoc_artisan.workers.preview_worker.PredictivePreviewRenderer")
    @patch("asciidoc_artisan.workers.preview_worker.IncrementalPreviewRenderer")
    @patch("asciidoc_artisan.workers.preview_worker.AsciiDoc3API")
    def test_initialize_with_predictive_renderer_exception(
        self, mock_api_class, mock_incremental_class, mock_predictive_class
    ):
        """Test initialize handles predictive renderer exception."""
        mock_api_instance = MagicMock()
        mock_api_class.return_value = mock_api_instance

        mock_incremental_instance = MagicMock()
        mock_incremental_class.return_value = mock_incremental_instance

        # Predictive renderer init raises exception
        mock_predictive_class.side_effect = RuntimeError("Predictive init failed")

        worker = PreviewWorker()

        # Should not crash
        worker.initialize_asciidoc("/path/to/asciidoc3.py")

        # API and incremental should be initialized, predictive should be None
        assert worker._asciidoc_api is not None
        assert worker._incremental_renderer is not None
        assert worker._predictive_renderer is None


@pytest.mark.unit
class TestSetIncrementalRenderingWithRenderer:
    """Test set_incremental_rendering when renderer exists."""

    def test_set_incremental_rendering_enabled_with_renderer(self):
        """Test enabling incremental rendering with renderer present."""
        worker = PreviewWorker()
        mock_incremental = MagicMock()
        worker._incremental_renderer = mock_incremental

        worker.set_incremental_rendering(True)

        assert worker._use_incremental is True
        mock_incremental.enable.assert_called_once_with(True)

    def test_set_incremental_rendering_disabled_with_renderer(self):
        """Test disabling incremental rendering with renderer present."""
        worker = PreviewWorker()
        mock_incremental = MagicMock()
        worker._incremental_renderer = mock_incremental

        worker.set_incremental_rendering(False)

        assert worker._use_incremental is False
        mock_incremental.enable.assert_called_once_with(False)


@pytest.mark.unit
class TestSetPredictiveRenderingWithRenderer:
    """Test set_predictive_rendering when renderer exists."""

    def test_set_predictive_rendering_enabled_with_renderer(self):
        """Test enabling predictive rendering with renderer present."""
        worker = PreviewWorker()
        mock_predictive = MagicMock()
        worker._predictive_renderer = mock_predictive

        worker.set_predictive_rendering(True)

        assert worker._use_predictive is True
        mock_predictive.enable.assert_called_once_with(True)

    def test_set_predictive_rendering_disabled_with_renderer(self):
        """Test disabling predictive rendering with renderer present."""
        worker = PreviewWorker()
        mock_predictive = MagicMock()
        worker._predictive_renderer = mock_predictive

        worker.set_predictive_rendering(False)

        assert worker._use_predictive is False
        mock_predictive.enable.assert_called_once_with(False)


@pytest.mark.unit
class TestRequestPredictionEdgeCases:
    """Test edge cases in request_prediction."""

    @patch("asciidoc_artisan.workers.incremental_renderer.DocumentBlockSplitter")
    def test_request_prediction_no_blocks(self, mock_splitter):
        """Test request_prediction when splitter returns no blocks."""
        worker = PreviewWorker()
        worker._use_predictive = True
        mock_predictive = MagicMock()
        worker._predictive_renderer = mock_predictive

        # Return empty blocks list
        mock_splitter.split.return_value = []

        # Should not crash
        worker.request_prediction("= Test", 0)

        # Should not call request_prediction
        mock_predictive.request_prediction.assert_not_called()

    @patch("asciidoc_artisan.workers.incremental_renderer.DocumentBlockSplitter")
    def test_request_prediction_exception_handling(self, mock_splitter):
        """Test request_prediction handles exceptions gracefully."""
        worker = PreviewWorker()
        worker._use_predictive = True
        mock_predictive = MagicMock()
        worker._predictive_renderer = mock_predictive

        # Splitter raises exception
        mock_splitter.split.side_effect = RuntimeError("Split failed")

        # Should not crash
        worker.request_prediction("= Test", 0)

        # Should not call request_prediction
        mock_predictive.request_prediction.assert_not_called()

    @patch("asciidoc_artisan.workers.incremental_renderer.DocumentBlockSplitter")
    def test_request_prediction_cursor_outside_block_range(self, mock_splitter):
        """Test request_prediction when cursor is outside all block ranges."""
        worker = PreviewWorker()
        worker._use_predictive = True
        mock_predictive = MagicMock()
        worker._predictive_renderer = mock_predictive

        # Mock blocks that don't contain cursor line
        mock_block1 = MagicMock(start_line=0, end_line=5)
        mock_block2 = MagicMock(start_line=6, end_line=10)
        mock_splitter.split.return_value = [mock_block1, mock_block2]

        # Cursor at line 15 (outside all blocks)
        worker.request_prediction("= Test", 15)

        # Should still call request_prediction with block 0 (default)
        mock_predictive.request_prediction.assert_called_once()


@pytest.mark.unit
class TestSchedulePrerender:
    """Test _schedule_prerender internal method."""

    def test_schedule_prerender_no_predictive_renderer(self):
        """Test _schedule_prerender when predictive renderer is None."""
        worker = PreviewWorker()
        worker._predictive_renderer = None
        worker._incremental_renderer = MagicMock()

        # Should not crash
        worker._schedule_prerender([])

    def test_schedule_prerender_no_incremental_renderer(self):
        """Test _schedule_prerender when incremental renderer is None."""
        worker = PreviewWorker()
        worker._predictive_renderer = MagicMock()
        worker._incremental_renderer = None

        # Should not crash
        worker._schedule_prerender([])

    def test_schedule_prerender_no_blocks_in_queue(self):
        """Test _schedule_prerender when prediction queue is empty."""
        worker = PreviewWorker()
        mock_predictive = MagicMock()
        mock_incremental = MagicMock()

        # get_next_prerender_block returns None (queue empty)
        mock_predictive.get_next_prerender_block.return_value = None

        worker._predictive_renderer = mock_predictive
        worker._incremental_renderer = mock_incremental

        # Should not crash
        worker._schedule_prerender([MagicMock()])

        # Should not render any blocks
        mock_incremental._render_block.assert_not_called()

    def test_schedule_prerender_block_index_out_of_range(self):
        """Test _schedule_prerender when block index exceeds blocks list."""
        worker = PreviewWorker()
        mock_predictive = MagicMock()
        mock_incremental = MagicMock()

        # get_next_prerender_block returns index beyond blocks list
        mock_predictive.get_next_prerender_block.return_value = 5

        worker._predictive_renderer = mock_predictive
        worker._incremental_renderer = mock_incremental

        blocks = [MagicMock(id="block1"), MagicMock(id="block2")]  # Only 2 blocks

        # Should not crash
        worker._schedule_prerender(blocks)

        # Should not render any blocks
        mock_incremental._render_block.assert_not_called()

    def test_schedule_prerender_block_already_cached(self):
        """Test _schedule_prerender skips already cached blocks."""
        worker = PreviewWorker()
        mock_predictive = MagicMock()
        mock_incremental = MagicMock()

        # Block already in cache
        mock_cache = MagicMock()
        mock_cache.get.return_value = "<cached html>"
        mock_incremental.cache = mock_cache

        # Return block index 0, then None
        mock_predictive.get_next_prerender_block.side_effect = [0, None]

        worker._predictive_renderer = mock_predictive
        worker._incremental_renderer = mock_incremental

        mock_block = MagicMock(id="block1")

        worker._schedule_prerender([mock_block])

        # Should check cache
        mock_cache.get.assert_called_once_with("block1")
        # Should NOT render block (already cached)
        mock_incremental._render_block.assert_not_called()

    def test_schedule_prerender_successful_prerender(self):
        """Test _schedule_prerender successfully pre-renders blocks."""
        worker = PreviewWorker()
        mock_predictive = MagicMock()
        mock_incremental = MagicMock()

        # Mock cache (not cached)
        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # Not in cache
        mock_incremental.cache = mock_cache

        # Mock render
        mock_incremental._render_block.return_value = "<rendered html>"

        # Return block index 0, then None
        mock_predictive.get_next_prerender_block.side_effect = [0, None]
        mock_predictive.predictor = MagicMock()

        worker._predictive_renderer = mock_predictive
        worker._incremental_renderer = mock_incremental

        mock_block = MagicMock(id="block1", content="Test content")

        worker._schedule_prerender([mock_block])

        # Should render block
        mock_incremental._render_block.assert_called_once_with(mock_block)
        # Should cache result
        mock_cache.put.assert_called_once_with("block1", "<rendered html>")
        # Should record prediction used
        mock_predictive.predictor.record_prediction_used.assert_called_once_with(0)

    def test_schedule_prerender_max_blocks_limit(self):
        """Test _schedule_prerender respects max_blocks limit."""
        worker = PreviewWorker()
        mock_predictive = MagicMock()
        mock_incremental = MagicMock()

        # Mock cache (not cached)
        mock_cache = MagicMock()
        mock_cache.get.return_value = None
        mock_incremental.cache = mock_cache

        # Mock render
        mock_incremental._render_block.return_value = "<html>"

        # Return block indices 0, 1, 2, 3, 4 (more than max_blocks=3)
        mock_predictive.get_next_prerender_block.side_effect = [0, 1, 2, 3, 4]
        mock_predictive.predictor = MagicMock()

        worker._predictive_renderer = mock_predictive
        worker._incremental_renderer = mock_incremental

        blocks = [MagicMock(id=f"block{i}", content=f"Content {i}") for i in range(5)]

        # max_blocks=2 (only render 2 blocks)
        worker._schedule_prerender(blocks, max_blocks=2)

        # Should only render 2 blocks (max_blocks limit)
        assert mock_incremental._render_block.call_count == 2

    def test_schedule_prerender_exception_handling(self):
        """Test _schedule_prerender handles exceptions gracefully."""
        worker = PreviewWorker()
        mock_predictive = MagicMock()
        mock_incremental = MagicMock()

        # Raise exception during rendering
        mock_incremental._render_block.side_effect = RuntimeError("Render failed")

        mock_cache = MagicMock()
        mock_cache.get.return_value = None
        mock_incremental.cache = mock_cache

        mock_predictive.get_next_prerender_block.return_value = 0

        worker._predictive_renderer = mock_predictive
        worker._incremental_renderer = mock_incremental

        mock_block = MagicMock(id="block1", content="Test")

        # Should not crash
        worker._schedule_prerender([mock_block])


@pytest.mark.unit
class TestRenderPreviewMetrics:
    """Test metrics recording variations in render_preview."""

    @patch("asciidoc_artisan.workers.preview_worker.METRICS_AVAILABLE", True)
    @patch("asciidoc_artisan.workers.preview_worker.get_metrics_collector")
    def test_fallback_render_no_metrics(self, mock_get_metrics):
        """Test fallback render does not record metrics."""
        worker = PreviewWorker()
        # Don't initialize asciidoc_api

        mock_metrics = MagicMock()
        mock_get_metrics.return_value = mock_metrics

        worker.render_preview("= Test")

        # Should not record metrics for fallback
        mock_metrics.record_operation.assert_not_called()


@pytest.mark.unit
class TestImportFallbacks:
    """Test import error fallback behavior."""

    def test_asciidoc3_import_fallback(self):
        """Test that ASCIIDOC3_AVAILABLE is False when import fails."""
        # Reload module with mocked import failure
        import sys
        from importlib import reload

        # Save original state
        original_asciidoc3 = sys.modules.get('asciidoc3')
        original_api = sys.modules.get('asciidoc3.asciidoc3api')

        try:
            # Remove modules to simulate import failure
            if 'asciidoc3' in sys.modules:
                del sys.modules['asciidoc3']
            if 'asciidoc3.asciidoc3api' in sys.modules:
                del sys.modules['asciidoc3.asciidoc3api']

            # Mock the import to fail
            import builtins
            original_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if 'asciidoc3' in name:
                    raise ImportError("Mocked asciidoc3 import failure")
                return original_import(name, *args, **kwargs)

            builtins.__import__ = mock_import

            # Reload preview_worker to trigger import error path
            import asciidoc_artisan.workers.preview_worker as pw
            reload(pw)

            # Verify fallback values are set
            assert pw.ASCIIDOC3_AVAILABLE is False
            assert pw.asciidoc3 is None
            assert pw.AsciiDoc3API is None

        finally:
            # Restore original state
            builtins.__import__ = original_import
            if original_asciidoc3 is not None:
                sys.modules['asciidoc3'] = original_asciidoc3
            if original_api is not None:
                sys.modules['asciidoc3.asciidoc3api'] = original_api
            reload(pw)

    def test_incremental_renderer_import_fallback(self):
        """Test that INCREMENTAL_RENDERER_AVAILABLE is False when import fails."""
        import sys
        from importlib import reload

        # Save original state
        original_incremental = sys.modules.get('asciidoc_artisan.workers.incremental_renderer')

        try:
            # Remove module to simulate import failure
            if 'asciidoc_artisan.workers.incremental_renderer' in sys.modules:
                del sys.modules['asciidoc_artisan.workers.incremental_renderer']

            import builtins
            original_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if 'incremental_renderer' in name:
                    raise ImportError("Mocked incremental_renderer import failure")
                return original_import(name, *args, **kwargs)

            builtins.__import__ = mock_import

            import asciidoc_artisan.workers.preview_worker as pw
            reload(pw)

            assert pw.INCREMENTAL_RENDERER_AVAILABLE is False
            assert pw.IncrementalPreviewRenderer is None

        finally:
            builtins.__import__ = original_import
            if original_incremental is not None:
                sys.modules['asciidoc_artisan.workers.incremental_renderer'] = original_incremental
            reload(pw)

    def test_predictive_renderer_import_fallback(self):
        """Test that PREDICTIVE_RENDERER_AVAILABLE is False when import fails."""
        import sys
        from importlib import reload

        original_predictive = sys.modules.get('asciidoc_artisan.workers.predictive_renderer')

        try:
            if 'asciidoc_artisan.workers.predictive_renderer' in sys.modules:
                del sys.modules['asciidoc_artisan.workers.predictive_renderer']

            import builtins
            original_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if 'predictive_renderer' in name:
                    raise ImportError("Mocked predictive_renderer import failure")
                return original_import(name, *args, **kwargs)

            builtins.__import__ = mock_import

            import asciidoc_artisan.workers.preview_worker as pw
            reload(pw)

            assert pw.PREDICTIVE_RENDERER_AVAILABLE is False
            assert pw.PredictiveRenderer is None
            assert pw.PredictivePreviewRenderer is None

        finally:
            builtins.__import__ = original_import
            if original_predictive is not None:
                sys.modules['asciidoc_artisan.workers.predictive_renderer'] = original_predictive
            reload(pw)

    def test_metrics_import_fallback(self):
        """Test that METRICS_AVAILABLE is False when import fails."""
        import sys
        from importlib import reload

        original_metrics = sys.modules.get('asciidoc_artisan.core.metrics')

        try:
            if 'asciidoc_artisan.core.metrics' in sys.modules:
                del sys.modules['asciidoc_artisan.core.metrics']

            import builtins
            original_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name == 'asciidoc_artisan.core.metrics' or 'metrics' in str(kwargs.get('fromlist', [])):
                    raise ImportError("Mocked metrics import failure")
                return original_import(name, *args, **kwargs)

            builtins.__import__ = mock_import

            import asciidoc_artisan.workers.preview_worker as pw
            reload(pw)

            assert pw.METRICS_AVAILABLE is False
            assert pw.get_metrics_collector is None

        finally:
            builtins.__import__ = original_import
            if original_metrics is not None:
                sys.modules['asciidoc_artisan.core.metrics'] = original_metrics
            reload(pw)
