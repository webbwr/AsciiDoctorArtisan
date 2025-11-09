"""
Tests for core.resource_monitor module.

Tests resource monitoring, document metrics, and adaptive debouncing.
"""

from unittest.mock import Mock, patch

from asciidoc_artisan.core.resource_monitor import (
    DocumentMetrics,
    ResourceMetrics,
    ResourceMonitor,
)


class TestResourceMetrics:
    """Test suite for ResourceMetrics dataclass."""

    def test_resource_metrics_creation(self):
        """Test creating ResourceMetrics."""
        metrics = ResourceMetrics(
            memory_used_mb=512.5,
            memory_percent=45.2,
            cpu_percent=15.8,
            document_size_bytes=102400,
            document_line_count=500,
            recommended_debounce_ms=350,
        )

        assert metrics.memory_used_mb == 512.5
        assert metrics.memory_percent == 45.2
        assert metrics.cpu_percent == 15.8
        assert metrics.document_size_bytes == 102400
        assert metrics.document_line_count == 500
        assert metrics.recommended_debounce_ms == 350


class TestDocumentMetrics:
    """Test suite for DocumentMetrics dataclass."""

    def test_document_metrics_small(self):
        """Test DocumentMetrics for small document."""
        metrics = DocumentMetrics(
            size_bytes=5000, line_count=50, char_count=5000, is_large=False
        )

        assert metrics.size_bytes == 5000
        assert metrics.line_count == 50
        assert metrics.is_large is False

    def test_document_metrics_large(self):
        """Test DocumentMetrics for large document."""
        metrics = DocumentMetrics(
            size_bytes=600000, line_count=6000, char_count=600000, is_large=True
        )

        assert metrics.size_bytes == 600000
        assert metrics.is_large is True


class TestResourceMonitor:
    """Test suite for ResourceMonitor class."""

    def test_resource_monitor_creation(self):
        """Test creating ResourceMonitor instance."""
        monitor = ResourceMonitor()
        assert monitor is not None

    def test_thresholds_defined(self):
        """Test that document size thresholds are defined."""
        assert ResourceMonitor.SMALL_DOC_BYTES > 0
        assert ResourceMonitor.MEDIUM_DOC_BYTES > ResourceMonitor.SMALL_DOC_BYTES
        assert ResourceMonitor.LARGE_DOC_BYTES > ResourceMonitor.MEDIUM_DOC_BYTES

        assert ResourceMonitor.SMALL_DOC_LINES > 0
        assert ResourceMonitor.MEDIUM_DOC_LINES > ResourceMonitor.SMALL_DOC_LINES
        assert ResourceMonitor.LARGE_DOC_LINES > ResourceMonitor.MEDIUM_DOC_LINES

    def test_debounce_intervals_defined(self):
        """Test that debounce intervals are defined."""
        assert ResourceMonitor.MIN_DEBOUNCE_MS > 0
        assert ResourceMonitor.NORMAL_DEBOUNCE_MS >= ResourceMonitor.MIN_DEBOUNCE_MS
        assert hasattr(ResourceMonitor, "MIN_DEBOUNCE_MS")
        assert hasattr(ResourceMonitor, "NORMAL_DEBOUNCE_MS")

    @patch("asciidoc_artisan.core.resource_monitor.PSUTIL_AVAILABLE", True)
    @patch("asciidoc_artisan.core.resource_monitor.psutil")
    def test_get_metrics_small_document(self, mock_psutil):
        """Test getting metrics for small document."""
        # Mock psutil
        mock_process = Mock()
        mock_process.memory_info.return_value = Mock(rss=100 * 1024 * 1024)  # 100MB
        mock_psutil.Process.return_value = mock_process
        mock_psutil.virtual_memory.return_value = Mock(percent=50.0)
        mock_psutil.cpu_percent.return_value = 25.0

        monitor = ResourceMonitor()
        small_doc = "Hello World\n" * 10  # Small document

        metrics = monitor.get_metrics(small_doc)

        assert isinstance(metrics, ResourceMetrics)
        assert metrics.document_size_bytes == len(small_doc.encode())
        assert metrics.document_line_count == 11  # 10 lines + 1
        assert metrics.recommended_debounce_ms >= ResourceMonitor.MIN_DEBOUNCE_MS

    @patch("asciidoc_artisan.core.resource_monitor.PSUTIL_AVAILABLE", False)
    def test_get_metrics_without_psutil(self):
        """Test getting metrics when psutil is not available."""
        monitor = ResourceMonitor()
        doc = "Test document\n" * 100

        metrics = monitor.get_metrics(doc)

        # Should still return metrics but with default/zero values for system metrics
        assert isinstance(metrics, ResourceMetrics)
        assert metrics.document_size_bytes > 0
        assert metrics.document_line_count > 0

    def test_get_document_metrics_empty(self):
        """Test document metrics for empty document."""
        monitor = ResourceMonitor()
        metrics = monitor.get_document_metrics("")

        assert metrics.size_bytes == 0
        assert metrics.line_count >= 0  # Empty string may count as 0 or 1 line
        assert metrics.char_count == 0
        assert metrics.is_large is False

    def test_get_document_metrics_small(self):
        """Test document metrics for small document."""
        monitor = ResourceMonitor()
        small_text = "Small document"

        metrics = monitor.get_document_metrics(small_text)

        assert metrics.size_bytes == len(small_text.encode())
        assert metrics.line_count == 1
        assert metrics.char_count == len(small_text)
        assert metrics.is_large is False

    def test_get_document_metrics_large(self):
        """Test document metrics for large document."""
        monitor = ResourceMonitor()
        # Create a large document (> 500KB)
        large_text = "This is a line of text.\n" * 25000  # ~600KB

        metrics = monitor.get_document_metrics(large_text)

        assert metrics.size_bytes > ResourceMonitor.LARGE_DOC_BYTES
        assert metrics.line_count > ResourceMonitor.LARGE_DOC_LINES
        assert metrics.is_large is True

    def test_calculate_debounce_small_doc(self):
        """Test debounce calculation for small document."""
        monitor = ResourceMonitor()
        small_text = "Small document\n" * 50

        debounce = monitor.calculate_debounce_interval(small_text)

        assert debounce >= ResourceMonitor.MIN_DEBOUNCE_MS
        assert isinstance(debounce, int)

    def test_calculate_debounce_large_doc(self):
        """Test debounce calculation for large document."""
        monitor = ResourceMonitor()
        # Create a large document (> 500KB)
        large_text = "This is a line of text.\n" * 25000

        debounce = monitor.calculate_debounce_interval(large_text)

        # Large documents should have higher debounce
        assert debounce > ResourceMonitor.NORMAL_DEBOUNCE_MS
        assert isinstance(debounce, int)

    def test_calculate_debounce_medium_doc(self):
        """Test debounce calculation for medium document."""
        monitor = ResourceMonitor()
        medium_text = "Medium document line\n" * 500

        debounce = monitor.calculate_debounce_interval(medium_text)

        assert debounce >= ResourceMonitor.MIN_DEBOUNCE_MS
        assert isinstance(debounce, int)

    def test_multiline_document_line_count(self):
        """Test accurate line counting for multiline documents."""
        monitor = ResourceMonitor()
        multiline_text = """Line 1
Line 2
Line 3
Line 4
Line 5"""

        metrics = monitor.get_document_metrics(multiline_text)

        assert metrics.line_count == 5

    def test_unicode_document_handling(self):
        """Test handling of Unicode characters in documents."""
        monitor = ResourceMonitor()
        unicode_text = "Hello 世界 🌍\n" * 10

        metrics = monitor.get_document_metrics(unicode_text)

        # Size in bytes should be larger than char count due to multibyte chars
        assert metrics.size_bytes >= metrics.char_count
        assert metrics.char_count > 0
        assert metrics.line_count >= 10  # At least 10 lines

    @patch("asciidoc_artisan.core.resource_monitor.PSUTIL_AVAILABLE", True)
    @patch("asciidoc_artisan.core.resource_monitor.psutil")
    def test_memory_metrics_accuracy(self, mock_psutil):
        """Test that memory metrics are accurately retrieved."""
        # Mock specific memory values
        mock_process = Mock()
        mock_process.memory_info.return_value = Mock(rss=256 * 1024 * 1024)  # 256MB
        mock_process.memory_percent.return_value = 60.5
        mock_process.cpu_percent.return_value = 30.2
        mock_psutil.Process.return_value = mock_process

        monitor = ResourceMonitor()
        metrics = monitor.get_metrics("test")

        # Check that metrics are numeric
        assert isinstance(metrics.memory_used_mb, float)
        assert isinstance(metrics.memory_percent, (int, float, type(None)))
        assert isinstance(metrics.cpu_percent, (int, float, type(None)))

    def test_consistent_metrics_for_same_document(self):
        """Test that metrics are consistent for the same document."""
        monitor = ResourceMonitor()
        doc = "Test document\n" * 100

        metrics1 = monitor.get_document_metrics(doc)
        metrics2 = monitor.get_document_metrics(doc)

        assert metrics1.size_bytes == metrics2.size_bytes
        assert metrics1.line_count == metrics2.line_count
        assert metrics1.char_count == metrics2.char_count
        assert metrics1.is_large == metrics2.is_large

    def test_medium_document_debounce(self):
        """Test medium document debounce calculation (line 157)."""
        monitor = ResourceMonitor()
        # To hit line 157, need:
        # NOT (size < MEDIUM_DOC_BYTES AND lines < MEDIUM_DOC_LINES)
        # AND (size < LARGE_DOC_BYTES AND lines < LARGE_DOC_LINES)
        # SMALL_DOC: <10KB & <100 lines
        # MEDIUM_DOC: <100KB & <1000 lines
        # LARGE_DOC: <500KB & <5000 lines
        # Create 1500 lines with short content (not too large in bytes)
        medium_text = "x\n" * 1500  # 1500 lines, ~3KB
        debounce = monitor.calculate_debounce_interval(medium_text)
        assert debounce == monitor.MEDIUM_DEBOUNCE_MS  # Line 157

    def test_large_document_debounce_default(self):
        """Test large document debounce default (line 167)."""
        monitor = ResourceMonitor()
        # To hit line 167, need >= LARGE but < 2*LARGE
        # >= 500KB OR >= 5000 lines, but NOT >= 1MB and NOT >= 10000 lines
        # Create exactly 5500 lines (between LARGE and 2*LARGE)
        large_text = "x\n" * 5500  # 5500 lines, ~11KB
        debounce = monitor.calculate_debounce_interval(large_text)
        assert debounce == monitor.LARGE_DEBOUNCE_MS  # Line 167

    def test_is_available_when_available(self):
        """Test is_available returns True when available (line 239)."""
        monitor = ResourceMonitor()
        # If psutil is available and process initialized
        if hasattr(monitor, "process") and monitor.process is not None:
            assert monitor.is_available() is True  # Line 239
        else:
            # If not available, should return False
            assert monitor.is_available() is False

    def test_get_platform_info(self):
        """Test get_platform_info returns platform details (line 248)."""
        monitor = ResourceMonitor()
        info = monitor.get_platform_info()  # Line 248

        # Verify all expected keys are present
        assert "system" in info
        assert "release" in info
        assert "version" in info
        assert "machine" in info
        assert "processor" in info
        assert "python_version" in info
        assert "psutil_available" in info

    def test_psutil_process_init_exception(self):
        """Test exception handling when psutil.Process() fails (lines 91-92)."""
        from unittest.mock import patch

        with patch("asciidoc_artisan.core.resource_monitor.PSUTIL_AVAILABLE", True):
            with patch(
                "asciidoc_artisan.core.resource_monitor.psutil.Process",
                side_effect=RuntimeError("Mock error"),
            ):
                monitor = ResourceMonitor()
                # Process should be None due to exception
                assert monitor.process is None

    def test_memory_usage_exception(self):
        """Test exception handling in get_memory_usage (lines 185-187)."""
        from unittest.mock import Mock

        monitor = ResourceMonitor()
        if monitor.process is not None:
            # Mock memory_info to raise exception
            monitor.process.memory_info = Mock(side_effect=RuntimeError("Mock error"))
            memory_mb, memory_percent = monitor.get_memory_usage()
            # Should return (0.0, 0.0) on exception
            assert memory_mb == 0.0
            assert memory_percent == 0.0

    def test_cpu_usage_exception(self):
        """Test exception handling in get_cpu_usage (lines 204-206)."""
        from unittest.mock import Mock

        monitor = ResourceMonitor()
        if monitor.process is not None:
            # Mock cpu_percent to raise exception
            monitor.process.cpu_percent = Mock(side_effect=RuntimeError("Mock error"))
            cpu = monitor.get_cpu_usage()
            # Should return 0.0 on exception
            assert cpu == 0.0

    def test_psutil_import_error(self):
        """Test handling when psutil is not available (lines 27-29)."""
        import importlib
        import sys
        from unittest.mock import patch

        # Save original psutil if it exists
        original_psutil = sys.modules.get("psutil")
        original_resource_monitor = sys.modules.get(
            "asciidoc_artisan.core.resource_monitor"
        )

        try:
            # Remove psutil from sys.modules to simulate it not being installed
            if "psutil" in sys.modules:
                del sys.modules["psutil"]
            if "asciidoc_artisan.core.resource_monitor" in sys.modules:
                del sys.modules["asciidoc_artisan.core.resource_monitor"]

            # Mock the import to raise ImportError
            with patch.dict("sys.modules", {"psutil": None}):
                # Force ImportError when trying to import psutil
                import builtins

                original_import = builtins.__import__

                def mock_import(name, *args, **kwargs):
                    if name == "psutil":
                        raise ImportError("Mock psutil not available")
                    return original_import(name, *args, **kwargs)

                with patch("builtins.__import__", side_effect=mock_import):
                    # Reload the module to trigger the import error path
                    import asciidoc_artisan.core.resource_monitor as rm

                    importlib.reload(rm)

                    # Check that PSUTIL_AVAILABLE is False
                    assert rm.PSUTIL_AVAILABLE is False

        finally:
            # Restore original modules
            try:
                if original_psutil is not None:
                    sys.modules["psutil"] = original_psutil
                else:
                    # Ensure psutil is removed from blacklist
                    if "psutil" in sys.modules and sys.modules["psutil"] is None:
                        del sys.modules["psutil"]

                # Always restore the original resource_monitor module
                if original_resource_monitor is not None:
                    sys.modules["asciidoc_artisan.core.resource_monitor"] = (
                        original_resource_monitor
                    )
                else:
                    # If it wasn't loaded before, make sure it's available now
                    import asciidoc_artisan.core.resource_monitor as rm

                    sys.modules["asciidoc_artisan.core.resource_monitor"] = rm

                # Reload to ensure normal state
                if "asciidoc_artisan.core.resource_monitor" in sys.modules:
                    import asciidoc_artisan.core.resource_monitor

                    importlib.reload(asciidoc_artisan.core.resource_monitor)
            except (ImportError, KeyError):
                # Cleanup failed, but that's okay for this test
                pass
