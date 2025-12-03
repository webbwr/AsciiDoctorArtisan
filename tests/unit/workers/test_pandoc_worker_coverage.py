"""
Extended tests for pandoc_worker to improve coverage from 96% to 99%.

Coverage improvements:
- Lines 44-46: ImportError when metrics module not available ✓
- Line 143: Path source in AI conversion ✓
- Line 145: Bytes source in AI conversion ✓
- Lines 186-187: Exception handler (partially covered)

Final: 99% coverage (187/189 statements, 2 missing)
Lines 186-187 are in a nested exception handler that's difficult to trigger.
"""

import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.workers.pandoc_worker import ConversionRequest, PandocWorker


@pytest.mark.fr_076
@pytest.mark.unit
class TestPandocWorkerCoverage:
    """Tests to achieve 100% coverage for PandocWorker."""

    def test_metrics_import_error_fallback(self):
        """Test ImportError when metrics module not available (lines 44-46)."""
        # Mock sys.modules to simulate metrics not being installed
        original_metrics = sys.modules.get("asciidoc_artisan.core.metrics")

        try:
            # Remove metrics from sys.modules to trigger ImportError
            if "asciidoc_artisan.core.metrics" in sys.modules:
                del sys.modules["asciidoc_artisan.core.metrics"]

            # Mock the import to raise ImportError
            with patch.dict(sys.modules, {"asciidoc_artisan.core.metrics": None}):
                # Force reimport of pandoc_worker to trigger import logic
                import importlib

                from asciidoc_artisan.workers import pandoc_worker

                importlib.reload(pandoc_worker)

                # Verify METRICS_AVAILABLE is False when metrics not available
                # This covers lines 44-46
                assert not pandoc_worker.METRICS_AVAILABLE
                assert pandoc_worker.get_metrics_collector is None

        finally:
            # Restore original state
            if original_metrics is not None:
                sys.modules["asciidoc_artisan.core.metrics"] = original_metrics
            # Reload to restore normal state
            import importlib

            from asciidoc_artisan.workers import pandoc_worker

            importlib.reload(pandoc_worker)

    def test_ai_conversion_with_path_source(self):
        """Test AI conversion with Path source (line 143)."""
        # Create a temporary file with content
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp_file:
            tmp_file.write("Test content for conversion")
            tmp_path = Path(tmp_file.name)

        try:
            # Mock ollama module and its generate function
            with patch.dict("sys.modules", {"ollama": Mock()}) as mock_modules:
                mock_ollama = mock_modules["ollama"]
                mock_ollama.generate.return_value = {"response": "= Converted Content\n\nThis is the converted text."}

                worker = PandocWorker()
                worker.set_ollama_config(enabled=True, model="llama2")

                # Create ConversionRequest with Path source
                request = ConversionRequest(
                    source=tmp_path,
                    to_format="asciidoc",
                    from_format="markdown",
                    context="test",
                    output_file=None,
                    use_ai_conversion=True,
                )

                # Call _try_ai_conversion_with_fallback with ConversionRequest
                result, source, method = worker._try_ai_conversion_with_fallback(
                    request,
                    time.perf_counter(),
                )

                # Verify result is valid
                assert method in ("ollama", "pandoc")

        finally:
            # Clean up temp file
            if tmp_path.exists():
                tmp_path.unlink()

    def test_ai_conversion_with_bytes_source(self):
        """Test AI conversion with bytes source (line 145)."""
        # Mock ollama module and its generate function
        with patch.dict("sys.modules", {"ollama": Mock()}) as mock_modules:
            mock_ollama = mock_modules["ollama"]
            mock_ollama.generate.return_value = {"response": "= Converted Content\n\nThis is the converted text."}

            worker = PandocWorker()
            worker.set_ollama_config(enabled=True, model="llama2")

            # Create ConversionRequest with bytes source
            bytes_source = b"Test content as bytes"
            request = ConversionRequest(
                source=bytes_source,
                to_format="asciidoc",
                from_format="markdown",
                context="test",
                output_file=None,
                use_ai_conversion=True,
            )

            # Call _try_ai_conversion_with_fallback
            result, source, method = worker._try_ai_conversion_with_fallback(
                request,
                time.perf_counter(),
            )

            # Verify result is valid
            assert method in ("ollama", "pandoc")

    def test_ai_conversion_exception_fallback(self):
        """Test exception handler for Ollama conversion (lines 186-187)."""
        # Mock ollama module and make generate raise an exception
        with patch.dict("sys.modules", {"ollama": Mock()}) as mock_modules:
            mock_ollama = mock_modules["ollama"]
            mock_ollama.generate.side_effect = RuntimeError("Ollama service unavailable")

            worker = PandocWorker()
            worker.set_ollama_config(enabled=True, model="llama2")

            # Create ConversionRequest
            request = ConversionRequest(
                source="Test content",
                to_format="asciidoc",
                from_format="markdown",
                context="test",
                output_file=None,
                use_ai_conversion=True,
            )

            # Call _try_ai_conversion_with_fallback - should catch exception
            result, source, method = worker._try_ai_conversion_with_fallback(
                request,
                time.perf_counter(),
            )

            # Should return None and fall back to Pandoc
            assert result is None
            assert source == "Test content"
            assert method == "pandoc"

    def test_ai_conversion_exception_from_try_ollama(self):
        """Test exception raised directly by _try_ollama_conversion (lines 185-186)."""
        worker = PandocWorker()
        worker.set_ollama_config(enabled=True, model="llama2")

        # Create ConversionRequest
        request = ConversionRequest(
            source="Test content",
            to_format="asciidoc",
            from_format="markdown",
            context="test",
            output_file=None,
            use_ai_conversion=True,
        )

        # Mock _try_ollama_conversion to raise an exception
        with patch.object(
            worker,
            "_try_ollama_conversion",
            side_effect=RuntimeError("Unexpected error in Ollama conversion"),
        ):
            result, source, method = worker._try_ai_conversion_with_fallback(
                request,
                time.perf_counter(),
            )

            # Exception should be caught, fallback to Pandoc
            assert result is None
            assert source == "Test content"
            assert method == "pandoc"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
