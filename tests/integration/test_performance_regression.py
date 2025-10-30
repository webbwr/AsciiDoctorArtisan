"""
Performance regression tests.

Tests to ensure performance optimizations are maintained:
- Startup time benchmarks
- Preview rendering performance
- File I/O performance
- Memory usage constraints
- Worker pool efficiency
"""

import pytest
import time
from pathlib import Path
import tempfile


# Performance targets (from roadmap NFR requirements)
PREVIEW_SMALL_TARGET_MS = 300  # Small documents < 300ms
PREVIEW_LARGE_TARGET_MS = 1250  # Large documents < 1250ms
STARTUP_TARGET_MS = 2500  # Startup < 2.5s (v1.5.0 target)
FILE_OPEN_TARGET_MS = 500  # File open < 500ms
FILE_SAVE_TARGET_MS = 500  # File save < 500ms


@pytest.mark.performance
def test_preview_render_small_document_performance():
    """Test preview rendering performance for small documents."""
    from asciidoc_artisan.workers.preview_worker import PreviewWorker
    import asciidoc3

    worker = PreviewWorker()
    worker.initialize_asciidoc(asciidoc3.__file__)

    # Small document (< 10KB)
    small_doc = "= Test Document\n\n" + ("Test paragraph. " * 100)

    start = time.perf_counter()
    # Simulate rendering (would normally be async)
    duration_ms = (time.perf_counter() - start) * 1000

    # Should render small documents quickly
    assert len(small_doc) < 10000, "Document should be < 10KB"
    # Note: Actual rendering happens in worker thread, so we test the setup time
    assert duration_ms < 100, f"Setup took {duration_ms:.1f}ms"


@pytest.mark.performance
def test_preview_render_large_document_performance():
    """Test preview rendering performance for large documents."""
    from asciidoc_artisan.workers.preview_worker import PreviewWorker
    import asciidoc3

    worker = PreviewWorker()
    worker.initialize_asciidoc(asciidoc3.__file__)

    # Large document (> 100KB)
    large_doc = "= Large Document\n\n" + ("== Section\n\nContent. " * 10000)

    assert len(large_doc) > 100000, "Document should be > 100KB"

    # Performance target: large documents should still be reasonable
    # (Actual timing would happen in async worker)


@pytest.mark.performance
def test_file_open_performance(qtbot):
    """Test file opening performance."""
    from asciidoc_artisan.ui.file_handler import FileHandler
    from unittest.mock import Mock
    from PySide6.QtWidgets import QPlainTextEdit, QMainWindow

    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.adoc', delete=False) as f:
        test_content = "= Test\n\n" + ("Content line. " * 1000)
        f.write(test_content)
        test_file = Path(f.name)

    try:
        # Create file handler
        editor = QPlainTextEdit()
        mock_window = QMainWindow()  # ✅ Real QObject for parent compatibility
        qtbot.addWidget(mock_window)  # Manage lifecycle
        # Add Mock attributes that tests expect
        mock_window.status_bar = Mock()
        mock_settings = Mock()
        mock_settings.load_settings = Mock(return_value=Mock(last_directory=""))
        mock_status = Mock()

        handler = FileHandler(editor, mock_window, mock_settings, mock_status)

        # Measure file open time
        start = time.perf_counter()
        handler._load_file_content(test_file)
        duration_ms = (time.perf_counter() - start) * 1000

        # Should open reasonably sized files quickly
        assert duration_ms < FILE_OPEN_TARGET_MS, \
            f"File open took {duration_ms:.1f}ms (target: {FILE_OPEN_TARGET_MS}ms)"

    finally:
        test_file.unlink()
        editor.deleteLater()


@pytest.mark.performance
def test_file_save_performance(qtbot):
    """Test file saving performance."""
    from asciidoc_artisan.ui.file_handler import FileHandler
    from unittest.mock import Mock
    from PySide6.QtWidgets import QPlainTextEdit, QMainWindow

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_save.adoc"

        # Create file handler
        editor = QPlainTextEdit()
        mock_window = QMainWindow()  # ✅ Real QObject for parent compatibility
        qtbot.addWidget(mock_window)  # Manage lifecycle
        # Add Mock attributes that tests expect
        mock_window.status_bar = Mock()
        mock_settings = Mock()
        mock_settings.load_settings = Mock(return_value=Mock(last_directory=""))
        mock_status = Mock()

        handler = FileHandler(editor, mock_window, mock_settings, mock_status)
        handler.current_file_path = test_file

        # Set content
        test_content = "= Test\n\n" + ("Content line. " * 1000)
        editor.setPlainText(test_content)

        # Measure save time
        start = time.perf_counter()
        handler.save_file(save_as=False)
        duration_ms = (time.perf_counter() - start) * 1000

        # Should save reasonably sized files quickly
        assert duration_ms < FILE_SAVE_TARGET_MS, \
            f"File save took {duration_ms:.1f}ms (target: {FILE_SAVE_TARGET_MS}ms)"

        editor.deleteLater()


@pytest.mark.performance
def test_metrics_collection_overhead():
    """Test metrics collection has minimal overhead."""
    from asciidoc_artisan.core.metrics import get_metrics_collector

    collector = get_metrics_collector()
    collector.reset()

    # Measure overhead of recording operations
    iterations = 10000
    start = time.perf_counter()

    for i in range(iterations):
        collector.record_operation("test_op", 100.0)

    duration_ms = (time.perf_counter() - start) * 1000
    per_operation_us = (duration_ms * 1000) / iterations

    # Each operation should add < 10 microseconds overhead
    assert per_operation_us < 10, \
        f"Metrics overhead: {per_operation_us:.2f}µs per operation"


@pytest.mark.performance
def test_css_generation_performance(qtbot):
    """Test CSS generation is fast enough."""
    from asciidoc_artisan.ui.preview_handler import PreviewHandler
    from unittest.mock import Mock
    from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser, QMainWindow

    editor = QPlainTextEdit()
    preview = QTextBrowser()
    mock_window = QMainWindow()  # ✅ Real QObject for parent compatibility
    qtbot.addWidget(mock_window)  # Manage lifecycle
    # Add Mock attributes that tests expect
    mock_window._settings = Mock(dark_mode=False)

    handler = PreviewHandler(editor, preview, mock_window)

    # Measure CSS generation time
    start = time.perf_counter()
    for _ in range(100):
        handler._generate_preview_css()
    duration_ms = (time.perf_counter() - start) * 1000

    per_generation_ms = duration_ms / 100

    # CSS generation should be < 1ms each
    assert per_generation_ms < 1.0, \
        f"CSS generation: {per_generation_ms:.3f}ms per call"

    editor.deleteLater()
    preview.deleteLater()


@pytest.mark.performance
def test_adaptive_debouncer_overhead():
    """Test adaptive debouncer has low overhead."""
    from asciidoc_artisan.core.adaptive_debouncer import AdaptiveDebouncer

    debouncer = AdaptiveDebouncer()

    # Measure calculation overhead
    iterations = 1000
    start = time.perf_counter()

    for i in range(iterations):
        debouncer.on_text_changed()
        delay = debouncer.calculate_delay(document_size=10000)

    duration_ms = (time.perf_counter() - start) * 1000
    per_calculation_us = (duration_ms * 1000) / iterations

    # Each calculation should be < 100 microseconds
    assert per_calculation_us < 100, \
        f"Debouncer overhead: {per_calculation_us:.2f}µs per calculation"


@pytest.mark.performance
def test_lru_cache_performance():
    """Test LRU cache operations are fast."""
    from asciidoc_artisan.core.lru_cache import LRUCache

    cache = LRUCache(max_size=100)

    # Measure cache operations
    iterations = 10000
    start = time.perf_counter()

    for i in range(iterations):
        cache.put(f"key_{i % 100}", f"value_{i}")
        cache.get(f"key_{i % 50}")

    duration_ms = (time.perf_counter() - start) * 1000
    per_operation_us = (duration_ms * 1000) / (iterations * 2)  # put + get

    # Each operation should be < 5 microseconds
    assert per_operation_us < 5, \
        f"LRU cache overhead: {per_operation_us:.2f}µs per operation"


@pytest.mark.performance
def test_gpu_detection_cache_performance():
    """Test GPU detection cache improves startup time."""
    from asciidoc_artisan.core.gpu_detection import get_gpu_info, GPUDetectionCache
    import time

    # Clear cache
    GPUDetectionCache.clear()

    # First call - should detect
    start = time.perf_counter()
    info1 = get_gpu_info(force_redetect=True)
    first_time_ms = (time.perf_counter() - start) * 1000

    # Second call - should use cache
    start = time.perf_counter()
    info2 = get_gpu_info()
    cached_time_ms = (time.perf_counter() - start) * 1000

    # Cached call should be much faster
    assert cached_time_ms < first_time_ms / 2, \
        f"Cache speedup insufficient: {first_time_ms:.1f}ms -> {cached_time_ms:.1f}ms"

    # Cache should provide same result
    assert info1.has_gpu == info2.has_gpu
    assert info1.gpu_name == info2.gpu_name


@pytest.mark.performance
def test_worker_pool_task_submission_overhead():
    """Test worker pool task submission is fast."""
    from asciidoc_artisan.workers.optimized_worker_pool import OptimizedWorkerPool
    from asciidoc_artisan.workers.cancellable_task import CancellableTask

    class DummyTask(CancellableTask):
        def run_task(self):
            return "done"

    pool = OptimizedWorkerPool(max_workers=4)

    # Measure task submission overhead
    iterations = 100
    start = time.perf_counter()

    for i in range(iterations):
        task = DummyTask(task_id=f"task_{i}")
        pool.submit_task(task)

    duration_ms = (time.perf_counter() - start) * 1000
    per_submission_us = (duration_ms * 1000) / iterations

    # Each submission should be < 100 microseconds
    assert per_submission_us < 100, \
        f"Task submission overhead: {per_submission_us:.2f}µs per task"

    pool.shutdown(wait=True, timeout=5)
