"""
Unit tests for PreviewWorker class.
"""

from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.workers import PreviewWorker


@pytest.mark.unit
class TestPreviewWorker:
    """Test PreviewWorker for AsciiDoc preview rendering."""

    def test_preview_worker_initialization(self):
        """Test PreviewWorker can be instantiated."""
        worker = PreviewWorker()
        assert worker is not None
        assert worker._asciidoc_api is None  # Starts uninitialized

    @patch("asciidoc_artisan.workers.preview_worker.asciidoc3")
    @patch("asciidoc_artisan.workers.preview_worker.AsciiDoc3API")
    def test_asciidoc_initialization(self, mock_api_class, mock_asciidoc3):
        """Test AsciiDoc API initialization."""
        mock_asciidoc3.__file__ = "/path/to/asciidoc3.py"
        mock_api_instance = MagicMock()
        mock_api_class.return_value = mock_api_instance

        worker = PreviewWorker()
        worker.initialize_asciidoc("/path/to/asciidoc3.py")

        # Verify API was initialized
        mock_api_class.assert_called_once_with("/path/to/asciidoc3.py")
        assert worker._asciidoc_api is not None

    @patch("asciidoc_artisan.workers.preview_worker.ASCIIDOC3_AVAILABLE", True)
    @patch("asciidoc_artisan.workers.preview_worker.AsciiDoc3API")
    def test_successful_preview_rendering(self, mock_api_class):
        """Test successful AsciiDoc preview rendering."""
        # Setup mock
        mock_api_instance = MagicMock()
        mock_api_instance.execute.return_value = None
        mock_api_class.return_value = mock_api_instance

        worker = PreviewWorker()
        worker._asciidoc_api = mock_api_instance

        result = None

        def capture_result(html):
            nonlocal result
            result = html

        worker.render_complete.connect(capture_result)

        # Execute render
        source_text = "= Test Document\n\nSome content"
        worker.render_preview(source_text)

        # Verify render was called
        assert mock_api_instance.execute.called

    def test_preview_without_asciidoc_api(self):
        """Test preview falls back when asciidoc3 not available."""
        worker = PreviewWorker()
        # Don't initialize _asciidoc_api (simulates missing asciidoc3)

        result = None

        def capture_result(html):
            nonlocal result
            result = html

        worker.render_complete.connect(capture_result)

        source_text = "= Test Document\n\nSome content"
        worker.render_preview(source_text)

        # Should emit fallback HTML
        assert result is not None
        assert "Test Document" in result  # Should show plain text content

    @patch("asciidoc_artisan.workers.preview_worker.ASCIIDOC3_AVAILABLE", True)
    @patch("asciidoc_artisan.workers.preview_worker.AsciiDoc3API")
    def test_preview_error_handling(self, mock_api_class):
        """Test preview handles rendering errors gracefully."""
        # Setup mock to raise error
        mock_api_instance = MagicMock()
        mock_api_instance.execute.side_effect = Exception("Render error")
        mock_api_class.return_value = mock_api_instance

        worker = PreviewWorker()
        worker._asciidoc_api = mock_api_instance

        error = None

        def capture_error(err):
            nonlocal error
            error = err

        worker.render_error.connect(capture_error)

        source_text = "= Test"
        worker.render_preview(source_text)

        # Should emit error
        assert error is not None
        assert "Render error" in error

    def test_preview_empty_content(self):
        """Test preview handles empty content."""
        worker = PreviewWorker()

        result = None

        def capture_result(html):
            nonlocal result
            result = html

        worker.render_complete.connect(capture_result)

        worker.render_preview("")

        # Should handle empty content gracefully
        assert result is not None

    @patch("asciidoc_artisan.workers.preview_worker.ASCIIDOC3_AVAILABLE", True)
    @patch("asciidoc_artisan.workers.preview_worker.AsciiDoc3API")
    def test_preview_special_characters(self, mock_api_class):
        """Test preview handles special characters."""
        mock_api_instance = MagicMock()
        mock_api_instance.execute.return_value = None
        mock_api_class.return_value = mock_api_instance

        worker = PreviewWorker()
        worker._asciidoc_api = mock_api_instance

        # Test with special characters
        source_text = "= Test & <Special> \"Characters\"\n\nContent with 'quotes'"
        worker.render_preview(source_text)

        # Should not raise exception
        assert mock_api_instance.execute.called


@pytest.mark.unit
class TestPreviewFallback:
    """Test preview fallback mode when asciidoc3 unavailable."""

    def test_fallback_html_generation(self):
        """Test fallback generates valid HTML."""
        worker = PreviewWorker()

        result = None

        def capture_result(html):
            nonlocal result
            result = html

        worker.render_complete.connect(capture_result)

        source_text = """= Document Title

== Section 1

Some content here.

== Section 2

More content."""

        worker.render_preview(source_text)

        # Verify HTML structure
        assert result is not None
        assert "<pre>" in result or "<div>" in result
        assert "Document Title" in result
        assert "Section 1" in result

    def test_fallback_preserves_line_breaks(self):
        """Test fallback mode preserves line breaks."""
        worker = PreviewWorker()

        result = None

        def capture_result(html):
            nonlocal result
            result = html

        worker.render_complete.connect(capture_result)

        source_text = "Line 1\nLine 2\nLine 3"
        worker.render_preview(source_text)

        # Should preserve structure
        assert result is not None
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result


@pytest.mark.unit
class TestIncrementalRendering:
    """Test incremental rendering features."""

    def test_incremental_rendering_default_enabled(self):
        """Test incremental rendering is enabled by default."""
        worker = PreviewWorker()
        assert worker._use_incremental is True

    def test_set_incremental_rendering_disabled(self):
        """Test disabling incremental rendering."""
        worker = PreviewWorker()
        worker.set_incremental_rendering(False)
        assert worker._use_incremental is False

    def test_set_incremental_rendering_enabled(self):
        """Test enabling incremental rendering."""
        worker = PreviewWorker()
        worker._use_incremental = False
        worker.set_incremental_rendering(True)
        assert worker._use_incremental is True

    @patch("asciidoc_artisan.workers.preview_worker.ASCIIDOC3_AVAILABLE", True)
    @patch(
        "asciidoc_artisan.workers.preview_worker.INCREMENTAL_RENDERER_AVAILABLE", True
    )
    @patch("asciidoc_artisan.workers.preview_worker.IncrementalPreviewRenderer")
    @patch("asciidoc_artisan.workers.preview_worker.AsciiDoc3API")
    def test_large_document_uses_incremental_rendering(
        self, mock_api_class, mock_incremental_class
    ):
        """Test large documents trigger incremental rendering."""
        # Setup mocks
        mock_api_instance = MagicMock()
        mock_api_class.return_value = mock_api_instance

        mock_incremental_instance = MagicMock()
        mock_incremental_instance.render.return_value = "<div>Rendered HTML</div>"
        mock_incremental_class.return_value = mock_incremental_instance

        worker = PreviewWorker()
        worker.initialize_asciidoc("/path/to/asciidoc3.py")

        # Large document (>1000 chars)
        large_text = "= Document\n\n" + ("Some content paragraph.\n" * 50)
        assert len(large_text) > 1000

        result = None

        def capture_result(html):
            nonlocal result
            result = html

        worker.render_complete.connect(capture_result)
        worker.render_preview(large_text)

        # Should use incremental renderer for large docs
        mock_incremental_instance.render.assert_called_once_with(large_text)
        assert result == "<div>Rendered HTML</div>"

    @patch("asciidoc_artisan.workers.preview_worker.ASCIIDOC3_AVAILABLE", True)
    @patch("asciidoc_artisan.workers.preview_worker.AsciiDoc3API")
    def test_small_document_uses_full_rendering(self, mock_api_class):
        """Test small documents use full rendering."""
        mock_api_instance = MagicMock()
        mock_api_instance.execute.return_value = None
        mock_api_class.return_value = mock_api_instance

        worker = PreviewWorker()
        worker._asciidoc_api = mock_api_instance
        worker._incremental_renderer = None  # No incremental renderer

        # Small document (<1000 chars)
        small_text = "= Small Doc\n\nBrief content."
        assert len(small_text) < 1000

        worker.render_preview(small_text)

        # Should use full render (execute called)
        assert mock_api_instance.execute.called


@pytest.mark.unit
class TestPredictiveRendering:
    """Test predictive rendering features (v1.6.0)."""

    def test_predictive_rendering_default_enabled(self):
        """Test predictive rendering is enabled by default."""
        worker = PreviewWorker()
        assert worker._use_predictive is True

    def test_set_predictive_rendering_disabled(self):
        """Test disabling predictive rendering."""
        worker = PreviewWorker()
        worker.set_predictive_rendering(False)
        assert worker._use_predictive is False

    def test_set_predictive_rendering_enabled(self):
        """Test enabling predictive rendering."""
        worker = PreviewWorker()
        worker._use_predictive = False
        worker.set_predictive_rendering(True)
        assert worker._use_predictive is True

    def test_update_cursor_position(self):
        """Test cursor position update."""
        worker = PreviewWorker()
        mock_predictive = MagicMock()
        worker._predictive_renderer = mock_predictive

        worker.update_cursor_position(42)

        mock_predictive.update_cursor_position.assert_called_once_with(42)

    def test_update_cursor_position_no_renderer(self):
        """Test cursor position update when renderer not available."""
        worker = PreviewWorker()
        # Should not crash when predictive renderer is None
        worker.update_cursor_position(10)

    @patch("asciidoc_artisan.workers.incremental_renderer.DocumentBlockSplitter")
    def test_request_prediction(self, mock_splitter):
        """Test prediction request."""
        worker = PreviewWorker()
        mock_predictive = MagicMock()
        worker._predictive_renderer = mock_predictive

        # Mock block splitter
        mock_block1 = MagicMock(start_line=0, end_line=5)
        mock_block2 = MagicMock(start_line=6, end_line=10)
        mock_splitter.split.return_value = [mock_block1, mock_block2]

        source_text = "= Doc\n\nContent\n\nMore"
        cursor_line = 7

        worker.request_prediction(source_text, cursor_line)

        # Should request prediction
        mock_predictive.request_prediction.assert_called_once()
        call_args = mock_predictive.request_prediction.call_args
        assert call_args[1]["total_blocks"] == 2
        assert call_args[1]["current_block"] == 1  # Cursor at line 7 is in block 2

    def test_request_prediction_disabled(self):
        """Test prediction request when disabled."""
        worker = PreviewWorker()
        worker._use_predictive = False
        mock_predictive = MagicMock()
        worker._predictive_renderer = mock_predictive

        worker.request_prediction("= Doc\n\nContent", 1)

        # Should not call request_prediction when disabled
        mock_predictive.request_prediction.assert_not_called()

    def test_get_predictive_stats(self):
        """Test getting predictive statistics."""
        worker = PreviewWorker()
        mock_predictive = MagicMock()
        mock_predictive.get_statistics.return_value = {
            "predictions": 10,
            "accuracy": 0.85,
        }
        worker._predictive_renderer = mock_predictive

        stats = worker.get_predictive_stats()

        assert stats["predictions"] == 10
        assert stats["accuracy"] == 0.85

    def test_get_predictive_stats_no_renderer(self):
        """Test getting stats when predictive renderer not available."""
        worker = PreviewWorker()
        stats = worker.get_predictive_stats()
        assert stats == {}


@pytest.mark.unit
class TestCacheManagement:
    """Test cache management features."""

    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        worker = PreviewWorker()
        mock_incremental = MagicMock()
        mock_incremental.get_cache_stats.return_value = {
            "hits": 25,
            "misses": 5,
            "size": 30,
        }
        worker._incremental_renderer = mock_incremental

        stats = worker.get_cache_stats()

        assert stats["hits"] == 25
        assert stats["misses"] == 5
        assert stats["size"] == 30

    def test_get_cache_stats_no_renderer(self):
        """Test getting cache stats when incremental renderer not available."""
        worker = PreviewWorker()
        stats = worker.get_cache_stats()
        assert stats == {}

    def test_clear_cache(self):
        """Test clearing cache."""
        worker = PreviewWorker()
        mock_incremental = MagicMock()
        worker._incremental_renderer = mock_incremental

        worker.clear_cache()

        mock_incremental.clear_cache.assert_called_once()

    def test_clear_cache_no_renderer(self):
        """Test clearing cache when incremental renderer not available."""
        worker = PreviewWorker()
        # Should not crash when incremental renderer is None
        worker.clear_cache()


@pytest.mark.unit
class TestMetricsRecording:
    """Test metrics recording during rendering."""

    @patch("asciidoc_artisan.workers.preview_worker.METRICS_AVAILABLE", True)
    @patch("asciidoc_artisan.workers.preview_worker.get_metrics_collector")
    @patch("asciidoc_artisan.workers.preview_worker.ASCIIDOC3_AVAILABLE", True)
    @patch("asciidoc_artisan.workers.preview_worker.AsciiDoc3API")
    def test_metrics_recorded_on_full_render(self, mock_api_class, mock_get_metrics):
        """Test metrics are recorded for full rendering."""
        mock_api_instance = MagicMock()
        mock_api_instance.execute.return_value = None
        mock_api_class.return_value = mock_api_instance

        mock_metrics = MagicMock()
        mock_get_metrics.return_value = mock_metrics

        worker = PreviewWorker()
        worker._asciidoc_api = mock_api_instance

        worker.render_preview("= Test\n\nContent")

        # Should record full render metric
        mock_metrics.record_operation.assert_called_once()
        call_args = mock_metrics.record_operation.call_args[0]
        assert call_args[0] == "preview_render_full"
        assert call_args[1] >= 0  # Duration in ms

    @patch("asciidoc_artisan.workers.preview_worker.METRICS_AVAILABLE", True)
    @patch("asciidoc_artisan.workers.preview_worker.get_metrics_collector")
    @patch("asciidoc_artisan.workers.preview_worker.ASCIIDOC3_AVAILABLE", True)
    @patch(
        "asciidoc_artisan.workers.preview_worker.INCREMENTAL_RENDERER_AVAILABLE", True
    )
    @patch("asciidoc_artisan.workers.preview_worker.IncrementalPreviewRenderer")
    @patch("asciidoc_artisan.workers.preview_worker.AsciiDoc3API")
    def test_metrics_recorded_on_incremental_render(
        self, mock_api_class, mock_incremental_class, mock_get_metrics
    ):
        """Test metrics are recorded for incremental rendering."""
        mock_api_instance = MagicMock()
        mock_api_class.return_value = mock_api_instance

        mock_incremental_instance = MagicMock()
        mock_incremental_instance.render.return_value = "<div>HTML</div>"
        mock_incremental_class.return_value = mock_incremental_instance

        mock_metrics = MagicMock()
        mock_get_metrics.return_value = mock_metrics

        worker = PreviewWorker()
        worker.initialize_asciidoc("/path/to/asciidoc3.py")

        # Large document to trigger incremental (must be >1000 chars)
        large_text = "= Document Title\n\n" + (
            "This is a content paragraph with some text.\n" * 30
        )
        assert len(large_text) > 1000  # Verify it's large enough
        worker.render_preview(large_text)

        # Should record incremental render metric
        mock_metrics.record_operation.assert_called_once()
        call_args = mock_metrics.record_operation.call_args[0]
        assert call_args[0] == "preview_render_incremental"
        assert call_args[1] >= 0  # Duration in ms
