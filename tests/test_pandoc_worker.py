"""
Unit tests for PandocWorker class.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.workers import PandocWorker


@pytest.mark.unit
class TestPandocWorker:
    """Test PandocWorker for document conversion."""

    def test_pandoc_worker_initialization(self):
        """Test PandocWorker can be instantiated."""
        worker = PandocWorker()
        assert worker is not None

    @patch("asciidoc_artisan.workers.pandoc_worker.pypandoc")
    def test_successful_text_conversion(self, mock_pypandoc):
        """Test successful text-to-text conversion."""
        mock_pypandoc.convert_text.return_value = "# Converted AsciiDoc"

        worker = PandocWorker()
        result = None
        context = None

        def capture_result(text, ctx):
            nonlocal result, context
            result = text
            context = ctx

        worker.conversion_complete.connect(capture_result)

        # Execute conversion
        worker.run_pandoc_conversion(
            source="# Markdown",
            to_format="asciidoc",
            from_format="markdown",
            context="test conversion",
            output_file=None,
            use_ai_conversion=False,
        )

        # Verify
        assert result is not None
        assert "Converted" in result
        assert context == "test conversion"

    @patch("asciidoc_artisan.workers.pandoc_worker.pypandoc")
    def test_conversion_error_handling(self, mock_pypandoc):
        """Test conversion error is properly handled."""
        mock_pypandoc.convert_text.side_effect = Exception("Conversion failed")

        worker = PandocWorker()
        error = None
        context = None

        def capture_error(err, ctx):
            nonlocal error, context
            error = err
            context = ctx

        worker.conversion_error.connect(capture_error)

        # Execute conversion
        worker.run_pandoc_conversion(
            source="# Test",
            to_format="asciidoc",
            from_format="markdown",
            context="error test",
            output_file=None,
            use_ai_conversion=False,
        )

        # Verify error was emitted
        assert error is not None
        assert "Conversion failed" in error

    def test_asciidoc_output_enhancement(self):
        """Test AsciiDoc output enhancement."""
        worker = PandocWorker()

        # Test adding document title
        text_without_title = "== Section Header\n\nContent here"
        enhanced = worker._enhance_asciidoc_output(text_without_title)

        assert enhanced.startswith("=")  # Should have title added

        # Test preserving existing title
        text_with_title = "= My Document\n\n== Section\n\nContent"
        enhanced = worker._enhance_asciidoc_output(text_with_title)

        assert enhanced.startswith("= My Document")  # Should keep original

    @patch("asciidoc_artisan.workers.pandoc_worker.pypandoc")
    def test_bytes_to_string_conversion(self, mock_pypandoc):
        """Test conversion handles bytes return value."""
        mock_pypandoc.convert_text.return_value = b"Converted bytes"

        worker = PandocWorker()
        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        worker.run_pandoc_conversion(
            source="Test",
            to_format="asciidoc",
            from_format="markdown",
            context="bytes test",
            output_file=None,
            use_ai_conversion=False,
        )

        # Verify bytes were decoded to string
        assert isinstance(result, str)
        assert "Converted bytes" in result

    @patch("asciidoc_artisan.workers.pandoc_worker.pypandoc")
    def test_file_output_conversion(self, mock_pypandoc):
        """Test conversion with file output."""
        mock_pypandoc.convert_text.return_value = None  # File output returns None

        worker = PandocWorker()
        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        output_path = Path("/tmp/test.docx")
        worker.run_pandoc_conversion(
            source="Test content",
            to_format="docx",
            from_format="asciidoc",
            context="file output test",
            output_file=output_path,
            use_ai_conversion=False,
        )

        # Verify result indicates file was saved
        assert result is not None
        assert "File saved to:" in result or str(output_path) in result

    @patch("asciidoc_artisan.workers.pandoc_worker.pypandoc")
    @patch("asciidoc_artisan.workers.pandoc_worker.create_client")
    def test_ai_conversion_attempt(self, mock_create_client, mock_pypandoc):
        """Test AI conversion attempt when enabled."""
        from claude_client import ConversionResult

        # Mock Claude client with successful conversion
        mock_client_instance = MagicMock()
        mock_client_instance.convert_document.return_value = ConversionResult(
            success=True,
            content="AI converted content",
            used_ai=True,
            processing_time=0.1,
        )
        mock_create_client.return_value = mock_client_instance

        # Mock pypandoc as fallback (should not be called if AI succeeds)
        mock_pypandoc.convert_text.return_value = "Fallback content"

        worker = PandocWorker()
        result = None

        def capture_result(text, ctx):
            nonlocal result
            result = text

        worker.conversion_complete.connect(capture_result)

        # This should attempt AI conversion
        worker.run_pandoc_conversion(
            source="Complex document",
            to_format="markdown",
            from_format="asciidoc",
            context="ai test",
            output_file=None,
            use_ai_conversion=True,
        )

        # Verify AI conversion was attempted
        assert mock_create_client.called
        assert mock_client_instance.convert_document.called
        assert result == "AI converted content"


@pytest.mark.unit
class TestPandocOutputEnhancement:
    """Test AsciiDoc output enhancement logic."""

    def test_source_code_block_formatting(self):
        """Test source code block formatting is fixed."""
        worker = PandocWorker()

        # Pandoc sometimes outputs [source]python instead of [source,python]
        text = "[source]python\n----\ncode here\n----"
        enhanced = worker._enhance_asciidoc_output(text)

        assert "[source,python]" in enhanced

    def test_multiple_source_blocks(self):
        """Test multiple source blocks are all fixed."""
        worker = PandocWorker()

        text = """
[source]python
----
code1
----

[source]javascript
----
code2
----
"""
        enhanced = worker._enhance_asciidoc_output(text)

        assert "[source,python]" in enhanced
        assert "[source,javascript]" in enhanced
