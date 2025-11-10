"""
Extended tests for PandocWorker - Edge cases and error handling.

This test suite covers untested edge cases in pandoc_worker.py to achieve 100% coverage:
- Ollama AI integration scenarios (success, timeout, errors)
- Format conversion edge cases (empty docs, invalid formats, large files)
- Error handling paths (Pandoc unavailable, subprocess errors)
- PDF engine detection (all engines, fallbacks, none available)
- Progress signal emission

Phase 4A.1: 25 tests for pandoc_worker.py coverage gaps
"""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.core.constants import is_pandoc_available
from asciidoc_artisan.workers.pandoc_worker import PandocWorker

# ==============================================================================
# Ollama AI Integration Tests (7 tests)
# ==============================================================================


class TestPandocWorkerOllamaIntegration:
    """Test Ollama AI conversion with various scenarios."""

    @pytest.fixture
    def worker(self):
        """Create PandocWorker instance."""
        worker = PandocWorker()
        worker.set_ollama_config(enabled=True, model="test-model")
        return worker

    def test_ollama_conversion_success_text_output(self, worker, qtbot):
        """Test successful Ollama conversion for text output formats."""
        mock_response = {
            "response": "= Converted Document\n\nThis is the AI-converted content."
        }

        # Mock ollama module at import time
        mock_ollama = Mock()
        mock_ollama.generate.return_value = mock_response

        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            result = worker._try_ollama_conversion(
                source="# Markdown Header\n\nContent here",
                from_format="markdown",
                to_format="asciidoc",
            )

            assert result is not None
            assert "= Converted Document" in result
            assert len(result) > 10
            mock_ollama.generate.assert_called_once()

    def test_ollama_conversion_success_binary_output_path(self, worker, qtbot):
        """Test Ollama conversion path for binary formats (PDF/DOCX)."""
        # This tests the code path at pandoc_worker.py:160-167
        # where Ollama produces markup for binary formats
        mock_response = {
            "response": "= PDF Content\n\nThis will be converted to PDF by Pandoc."
        }

        mock_ollama = Mock()
        mock_ollama.generate.return_value = mock_response

        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            # Call _try_ai_conversion_with_fallback to test binary output path
            with patch(
                "asciidoc_artisan.workers.pandoc_worker.time.perf_counter",
                return_value=1.0,
            ):
                result, source, method = worker._try_ai_conversion_with_fallback(
                    source="# Markdown",
                    to_format="pdf",
                    from_format="markdown",
                    context="test",
                    output_file=Path("/tmp/test.pdf"),
                    start_time=1.0,
                    use_ai_conversion=True,
                )

            # Should return None for result (will continue to Pandoc)
            # But source should be updated to Ollama's result
            # And method should be "ollama_pandoc"
            assert result is None
            assert "= PDF Content" in source
            assert method == "ollama_pandoc"

    def test_ollama_conversion_timeout(self, worker, qtbot):
        """Test Ollama conversion timeout handling."""
        mock_ollama = Mock()
        # Simulate timeout error
        mock_ollama.generate.side_effect = Exception("Request timed out after 30s")

        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            result = worker._try_ollama_conversion(
                source="# Test document",
                from_format="markdown",
                to_format="asciidoc",
            )

            # Should return None (fallback to Pandoc)
            assert result is None

    def test_ollama_conversion_malformed_response(self, worker, qtbot):
        """Test Ollama conversion with malformed response."""
        mock_ollama = Mock()
        # Malformed response - missing "response" key
        mock_ollama.generate.return_value = {"error": "Model unavailable"}

        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            result = worker._try_ollama_conversion(
                source="# Test",
                from_format="markdown",
                to_format="asciidoc",
            )

            assert result is None

    def test_ollama_conversion_insufficient_output(self, worker, qtbot):
        """Test Ollama conversion with insufficient output (<10 chars)."""
        mock_ollama = Mock()
        # Response too short (< 10 characters)
        mock_ollama.generate.return_value = {"response": "= Title"}

        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            result = worker._try_ollama_conversion(
                source="# Test document with content",
                from_format="markdown",
                to_format="asciidoc",
            )

            # Should reject insufficient output
            assert result is None

    def test_ollama_service_unavailable(self, worker, qtbot):
        """Test Ollama conversion when service is unavailable."""
        mock_ollama = Mock()
        # Simulate connection refused
        mock_ollama.generate.side_effect = Exception("Connection refused")

        with patch.dict("sys.modules", {"ollama": mock_ollama}):
            result = worker._try_ollama_conversion(
                source="# Test",
                from_format="markdown",
                to_format="asciidoc",
            )

            assert result is None

    def test_ollama_library_not_installed(self, worker, qtbot):
        """Test Ollama conversion when library is not installed."""
        # Simulate import failure by not providing the module
        with patch.dict("sys.modules", {}, clear=False):
            # Remove ollama if it exists
            if "ollama" in __import__("sys").modules:
                del __import__("sys").modules["ollama"]

            result = worker._try_ollama_conversion(
                source="# Test",
                from_format="markdown",
                to_format="asciidoc",
            )

            # ImportError is caught, returns None
            assert result is None


# ==============================================================================
# Format Conversion Edge Cases (7 tests)
# ==============================================================================


class TestPandocWorkerFormatConversionEdgeCases:
    """Test format conversion edge cases."""

    @pytest.fixture
    def worker(self):
        """Create PandocWorker instance."""
        return PandocWorker()

    def test_empty_document_conversion(self, worker, qtbot):
        """Test conversion of empty document."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        with qtbot.waitSignal(worker.conversion_complete, timeout=5000) as blocker:
            worker.run_pandoc_conversion(
                source="",
                to_format="asciidoc",
                from_format="markdown",
                context="empty_test",
                use_ai_conversion=False,
            )

        # Should complete without error
        result, context = blocker.args
        assert context == "empty_test"
        assert isinstance(result, str)

    def test_very_large_document_conversion(self, worker, qtbot):
        """Test conversion of very large document (>10MB of text)."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        # Create a large document (simulate)
        large_content = "# Heading\n\n" + ("Lorem ipsum dolor sit amet. " * 10000)

        with qtbot.waitSignal(worker.conversion_complete, timeout=30000) as blocker:
            worker.run_pandoc_conversion(
                source=large_content,
                to_format="asciidoc",
                from_format="markdown",
                context="large_test",
                use_ai_conversion=False,
            )

        result, context = blocker.args
        assert context == "large_test"
        assert len(result) > 0

    def test_document_with_non_utf8_encoding(self, worker, qtbot):
        """Test conversion of document with non-UTF8 bytes."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        # Create bytes with Latin-1 encoding
        content_bytes = "Café résumé naïve".encode("latin-1")

        with qtbot.waitSignal(worker.conversion_complete, timeout=5000) as blocker:
            worker.run_pandoc_conversion(
                source=content_bytes,
                to_format="asciidoc",
                from_format="markdown",
                context="encoding_test",
                use_ai_conversion=False,
            )

        result, context = blocker.args
        assert context == "encoding_test"
        # Should handle encoding errors with 'replace' strategy
        assert isinstance(result, str)

    def test_conversion_with_binary_input(self, worker, qtbot):
        """Test conversion with binary bytes input."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        content_bytes = b"# Test Heading\n\nTest content"

        with qtbot.waitSignal(worker.conversion_complete, timeout=5000) as blocker:
            worker.run_pandoc_conversion(
                source=content_bytes,
                to_format="asciidoc",
                from_format="markdown",
                context="binary_test",
                use_ai_conversion=False,
            )

        result, context = blocker.args
        assert context == "binary_test"
        assert isinstance(result, str)

    def test_conversion_with_path_input(self, worker, qtbot, tmp_path):
        """Test conversion with Path object as input."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        # Create temp file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test\n\nContent", encoding="utf-8")

        with qtbot.waitSignal(worker.conversion_complete, timeout=5000) as blocker:
            worker.run_pandoc_conversion(
                source=test_file,
                to_format="asciidoc",
                from_format="markdown",
                context="path_test",
                use_ai_conversion=False,
            )

        result, context = blocker.args
        assert context == "path_test"
        assert isinstance(result, str)

    def test_unsupported_input_format(self, worker, qtbot):
        """Test conversion with unsupported input format."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        # Pandoc will fail on invalid format
        with qtbot.waitSignal(worker.conversion_error, timeout=5000) as blocker:
            worker.run_pandoc_conversion(
                source="test content",
                to_format="asciidoc",
                from_format="invalid_format_xyz",
                context="invalid_input_test",
                use_ai_conversion=False,
            )

        error_msg, context = blocker.args
        assert context == "invalid_input_test"
        # Pandoc error message says "invalid input format!"
        assert "invalid" in error_msg.lower() or "error" in error_msg.lower()

    def test_unsupported_output_format(self, worker, qtbot):
        """Test conversion with unsupported output format."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        with qtbot.waitSignal(worker.conversion_error, timeout=5000) as blocker:
            worker.run_pandoc_conversion(
                source="# Test",
                to_format="invalid_output_format_xyz",
                from_format="markdown",
                context="invalid_output_test",
                use_ai_conversion=False,
            )

        error_msg, context = blocker.args
        assert context == "invalid_output_test"
        # Pandoc error message says "invalid output format!"
        assert "invalid" in error_msg.lower() or "error" in error_msg.lower()


# ==============================================================================
# Error Handling Tests (6 tests)
# ==============================================================================


class TestPandocWorkerErrorHandling:
    """Test error handling in PandocWorker."""

    @pytest.fixture
    def worker(self):
        """Create PandocWorker instance."""
        return PandocWorker()

    def test_pandoc_subprocess_crash(self, worker, qtbot):
        """Test handling of Pandoc subprocess crash."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        with patch("pypandoc.convert_text") as mock_convert:
            # Simulate subprocess crash
            mock_convert.side_effect = RuntimeError("Pandoc subprocess crashed")

            with qtbot.waitSignal(worker.conversion_error, timeout=5000) as blocker:
                worker.run_pandoc_conversion(
                    source="# Test",
                    to_format="asciidoc",
                    from_format="markdown",
                    context="crash_test",
                    use_ai_conversion=False,
                )

            error_msg, context = blocker.args
            assert context == "crash_test"
            # Error message will contain the exception text
            assert "crashed" in error_msg.lower() or "pandoc" in error_msg.lower()

    def test_output_file_write_permission_denied(self, worker, qtbot, tmp_path):
        """Test handling of output file write permission denied."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        # Create a read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        output_file = readonly_dir / "output.pdf"

        with patch.object(
            PandocWorker, "_detect_pdf_engine", return_value="wkhtmltopdf"
        ):
            with patch("pypandoc.convert_text") as mock_convert:
                # Simulate permission denied error
                mock_convert.side_effect = PermissionError(
                    "Permission denied: cannot write to readonly directory"
                )

                with qtbot.waitSignal(worker.conversion_error, timeout=5000) as blocker:
                    worker.run_pandoc_conversion(
                        source="# Test",
                        to_format="pdf",
                        from_format="markdown",
                        context="permission_test",
                        output_file=output_file,
                        use_ai_conversion=False,
                    )

        error_msg, context = blocker.args
        assert context == "permission_test"
        # Should get permission error
        assert "permission" in error_msg.lower() or "error" in error_msg.lower()

        # Cleanup
        readonly_dir.chmod(0o755)

    def test_disk_full_during_conversion(self, worker, qtbot):
        """Test handling of disk full error during conversion."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        with patch("pypandoc.convert_text") as mock_convert:
            # Simulate disk full error
            mock_convert.side_effect = OSError(28, "No space left on device")

            with qtbot.waitSignal(worker.conversion_error, timeout=5000) as blocker:
                worker.run_pandoc_conversion(
                    source="# Test",
                    to_format="asciidoc",
                    from_format="markdown",
                    context="disk_full_test",
                    use_ai_conversion=False,
                )

            error_msg, context = blocker.args
            assert context == "disk_full_test"
            # Error message contains errno and description
            assert "errno" in error_msg.lower() or "space" in error_msg.lower()

    def test_conversion_timeout_large_document(self, worker, qtbot):
        """Test conversion timeout for extremely large documents."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        with patch("pypandoc.convert_text") as mock_convert:
            # Simulate timeout
            mock_convert.side_effect = subprocess.TimeoutExpired(
                cmd="pandoc", timeout=30
            )

            with qtbot.waitSignal(worker.conversion_error, timeout=5000) as blocker:
                worker.run_pandoc_conversion(
                    source="# Test",
                    to_format="asciidoc",
                    from_format="markdown",
                    context="timeout_test",
                    use_ai_conversion=False,
                )

            error_msg, context = blocker.args
            assert context == "timeout_test"
            # Error message says "command 'pandoc' timed out after X seconds"
            assert "timed out" in error_msg.lower() or "timeout" in error_msg.lower()

    def test_invalid_pandoc_arguments(self, worker, qtbot):
        """Test handling of invalid Pandoc arguments."""
        if not is_pandoc_available():
            pytest.skip("Pandoc not available")

        with patch("pypandoc.convert_text") as mock_convert:
            # Simulate argument error
            mock_convert.side_effect = RuntimeError("Unknown option --invalid-arg")

            with qtbot.waitSignal(worker.conversion_error, timeout=5000) as blocker:
                worker.run_pandoc_conversion(
                    source="# Test",
                    to_format="asciidoc",
                    from_format="markdown",
                    context="invalid_args_test",
                    use_ai_conversion=False,
                )

            error_msg, context = blocker.args
            assert context == "invalid_args_test"
            # Error message says "unknown option"
            assert "unknown" in error_msg.lower() or "option" in error_msg.lower()

    def test_pandoc_not_available_error_path(self, qtbot):
        """Test error path when is_pandoc_available() returns False."""
        # Create worker when Pandoc is not available
        # Patch where it's imported TO, not where it's imported FROM
        with patch(
            "asciidoc_artisan.workers.pandoc_worker.is_pandoc_available",
            return_value=False,
        ):
            worker = PandocWorker()

            with qtbot.waitSignal(worker.conversion_error, timeout=5000) as blocker:
                worker.run_pandoc_conversion(
                    source="# Test",
                    to_format="asciidoc",
                    from_format="markdown",
                    context="no_pandoc_test",
                    use_ai_conversion=False,
                )

            error_msg, context = blocker.args
            assert context == "no_pandoc_test"
            assert "pandoc" in error_msg.lower() and "not" in error_msg.lower()


# ==============================================================================
# PDF Engine Detection Tests (5 tests)
# ==============================================================================


class TestPandocWorkerPDFEngineDetection:
    """Test PDF engine detection and prioritization."""

    @pytest.fixture
    def worker(self):
        """Create PandocWorker instance."""
        return PandocWorker()

    def test_wkhtmltopdf_available_primary_choice(self, worker):
        """Test that wkhtmltopdf is selected when available (highest priority)."""

        def mock_run(cmd, *args, **kwargs):
            if cmd[0] == "wkhtmltopdf":
                # wkhtmltopdf is available
                return subprocess.CompletedProcess(cmd, 0, stdout=b"0.12.6", stderr=b"")
            raise FileNotFoundError()

        with patch("subprocess.run", side_effect=mock_run):
            engine = worker._detect_pdf_engine()
            assert engine == "wkhtmltopdf"

    def test_weasyprint_fallback(self, worker):
        """Test weasyprint selected when wkhtmltopdf unavailable."""

        def mock_run(cmd, *args, **kwargs):
            if cmd[0] == "wkhtmltopdf":
                raise FileNotFoundError()
            elif cmd[0] == "weasyprint":
                # weasyprint is available
                return subprocess.CompletedProcess(cmd, 0, stdout=b"52.5", stderr=b"")
            raise FileNotFoundError()

        with patch("subprocess.run", side_effect=mock_run):
            engine = worker._detect_pdf_engine()
            assert engine == "weasyprint"

    def test_pdflatex_fallback(self, worker):
        """Test pdflatex selected when other engines unavailable."""

        def mock_run(cmd, *args, **kwargs):
            if cmd[0] in ["wkhtmltopdf", "weasyprint", "prince"]:
                raise FileNotFoundError()
            elif cmd[0] == "pdflatex":
                # pdflatex is available
                return subprocess.CompletedProcess(cmd, 0, stdout=b"3.14", stderr=b"")
            raise FileNotFoundError()

        with patch("subprocess.run", side_effect=mock_run):
            engine = worker._detect_pdf_engine()
            assert engine == "pdflatex"

    def test_multiple_engines_available_priority_order(self, worker):
        """Test that correct priority is used when multiple engines available."""

        def mock_run(cmd, *args, **kwargs):
            # Both weasyprint and pdflatex available
            if cmd[0] in ["weasyprint", "pdflatex"]:
                return subprocess.CompletedProcess(cmd, 0, stdout=b"1.0", stderr=b"")
            raise FileNotFoundError()

        with patch("subprocess.run", side_effect=mock_run):
            engine = worker._detect_pdf_engine()
            # Should choose weasyprint (higher priority than pdflatex)
            assert engine == "weasyprint"

    def test_no_pdf_engine_available_raises_error(self, worker):
        """Test RuntimeError raised when no PDF engine available."""

        def mock_run(cmd, *args, **kwargs):
            # No engine available
            raise FileNotFoundError()

        with patch("subprocess.run", side_effect=mock_run):
            with pytest.raises(RuntimeError) as exc_info:
                worker._detect_pdf_engine()

            # Should raise with helpful message
            assert "PDF conversion requires a PDF engine" in str(exc_info.value)
            assert "wkhtmltopdf" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
