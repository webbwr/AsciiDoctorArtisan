"""
Unit tests for PreviewWorker class.
"""

from unittest.mock import MagicMock, patch

import pytest

from adp_windows import PreviewWorker


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
