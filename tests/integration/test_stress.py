"""
Stress tests for AsciiDoc Artisan.

Tests system behavior under heavy load:
- Large document handling
- Rapid operations
- Many concurrent workers
- Memory constraints
- Resource cleanup
"""

import pytest
import time
from pathlib import Path
import tempfile


@pytest.mark.stress
@pytest.mark.slow
def test_large_document_preview():
    """Test preview rendering with very large documents."""
    from asciidoc_artisan.workers.preview_worker import PreviewWorker
    import asciidoc3

    worker = PreviewWorker()
    worker.initialize_asciidoc(asciidoc3.__file__)

    # Create very large document (1MB+)
    sections = []
    for i in range(1000):
        sections.append(f"== Section {i}\n\n")
        sections.append("This is a test paragraph with some content. " * 20)
        sections.append("\n\n")

    large_doc = "".join(sections)
    assert len(large_doc) > 1_000_000, "Document should be > 1MB"

    # Should handle large documents without crashing
    # (Actual rendering happens in worker thread)


@pytest.mark.stress
@pytest.mark.slow
def test_rapid_file_operations(qtbot):
    """Test rapid successive file operations."""
    from asciidoc_artisan.ui.file_handler import FileHandler
    from unittest.mock import Mock
    from PySide6.QtWidgets import QPlainTextEdit, QMainWindow

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create handler
        editor = QPlainTextEdit()
        mock_window = QMainWindow()  # ✅ Real QObject for parent compatibility
        qtbot.addWidget(mock_window)  # Manage lifecycle
        # Add Mock attributes that tests expect
        mock_window.status_bar = Mock()
        mock_settings = Mock()
        mock_settings.load_settings = Mock(return_value=Mock(last_directory=""))
        mock_status = Mock()

        handler = FileHandler(editor, mock_window, mock_settings, mock_status)

        # Perform rapid file operations
        for i in range(50):
            test_file = Path(tmpdir) / f"test_{i}.adoc"
            handler.current_file_path = test_file
            editor.setPlainText(f"Content {i}")
            handler.save_file(save_as=False)

        # Should complete without errors
        editor.deleteLater()


@pytest.mark.stress
@pytest.mark.slow
def test_many_concurrent_tasks():
    """Test handling many concurrent tasks."""
    from asciidoc_artisan.workers.optimized_worker_pool import OptimizedWorkerPool
    import time

    def slow_func():
        time.sleep(0.01)  # 10ms task
        return "done"

    pool = OptimizedWorkerPool(max_threads=8)

    # Submit many tasks
    task_count = 200
    for i in range(task_count):
        pool.submit(slow_func, task_id=f"task_{i}")

    # Wait for completion
    pool.wait_for_done(timeout_ms=30000)

    # Should handle all tasks without issues


@pytest.mark.stress
@pytest.mark.slow
def test_rapid_preview_updates(qtbot):
    """Test rapid successive preview updates."""
    from asciidoc_artisan.ui.preview_handler import PreviewHandler
    from unittest.mock import Mock
    from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser, QMainWindow

    editor = QPlainTextEdit()
    preview = QTextBrowser()
    mock_window = QMainWindow()  # ✅ Real QObject for parent compatibility
    qtbot.addWidget(mock_window)  # Manage lifecycle
    # Add Mock attributes that tests expect
    mock_window._settings = Mock(dark_mode=False)
    mock_window.request_preview_render = Mock()

    handler = PreviewHandler(editor, preview, mock_window)

    # Simulate rapid typing (many text changes)
    for i in range(100):
        editor.setPlainText(f"Content version {i}")

    # Should handle rapid updates without crashing
    # (Debouncing should prevent overload)

    editor.deleteLater()
    preview.deleteLater()


@pytest.mark.stress
@pytest.mark.slow
def test_many_metrics_operations():
    """Test metrics collection under heavy load."""
    from asciidoc_artisan.core.metrics import get_metrics_collector

    collector = get_metrics_collector()
    collector.reset()

    # Record many operations
    iterations = 100_000
    for i in range(iterations):
        collector.record_operation(f"op_{i % 10}", float(i % 1000))

    # Get statistics (should not crash with large datasets)
    stats = collector.get_statistics()

    assert len(stats["operations"]) > 0
    # Ring buffer should limit memory (1000 entries per operation)


@pytest.mark.stress
@pytest.mark.slow
def test_large_file_open_save(qtbot):
    """Test opening and saving very large files."""
    from asciidoc_artisan.ui.file_handler import FileHandler
    from unittest.mock import Mock
    from PySide6.QtWidgets import QPlainTextEdit, QMainWindow

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create very large file (5MB)
        large_content = "= Large Document\n\n" + ("Test content. " * 500_000)
        assert len(large_content) > 5_000_000, "File should be > 5MB"

        test_file = Path(tmpdir) / "large.adoc"
        test_file.write_text(large_content)

        # Create handler
        editor = QPlainTextEdit()
        mock_window = QMainWindow()  # ✅ Real QObject for parent compatibility
        qtbot.addWidget(mock_window)  # Manage lifecycle
        # Add Mock attributes that tests expect
        mock_window.status_bar = Mock()
        mock_settings = Mock()
        mock_settings.load_settings = Mock(return_value=Mock(last_directory=""))
        mock_status = Mock()

        handler = FileHandler(editor, mock_window, mock_settings, mock_status)

        # Open large file
        start = time.perf_counter()
        handler._load_file_content(test_file)
        open_time = time.perf_counter() - start

        # Should handle large files (may be slow but shouldn't crash)
        assert open_time < 10.0, f"Large file open took {open_time:.1f}s"

        # Save large file
        start = time.perf_counter()
        handler.save_file(save_as=False)
        save_time = time.perf_counter() - start

        assert save_time < 10.0, f"Large file save took {save_time:.1f}s"

        editor.deleteLater()


@pytest.mark.stress
@pytest.mark.slow
def test_cache_with_many_entries():
    """Test LRU cache with many entries."""
    from asciidoc_artisan.core.lru_cache import LRUCache

    cache = LRUCache(max_size=1000)

    # Add many entries
    for i in range(10_000):
        cache.put(f"key_{i}", f"value_{i}" * 100)  # ~600 bytes per entry

    # Should maintain max size (use len() not size())
    assert len(cache) <= 1000

    # Should still be functional
    cache.put("test", "value")
    assert cache.get("test") == "value"


@pytest.mark.stress
@pytest.mark.slow
def test_incremental_renderer_many_blocks():
    """Test incremental renderer with document with many blocks."""
    from asciidoc_artisan.workers.incremental_renderer import IncrementalPreviewRenderer
    from unittest.mock import Mock

    mock_api = Mock()
    renderer = IncrementalPreviewRenderer(mock_api)

    # Create document with many sections (500+)
    sections = []
    for i in range(500):
        sections.append(f"== Section {i}\n\nContent for section {i}.\n\n")

    large_doc = "".join(sections)

    # Should detect many blocks
    blocks = renderer._split_into_blocks(large_doc)
    assert len(blocks) >= 500

    # Should handle caching efficiently
    # (Actual rendering would happen with mock_api)


@pytest.mark.stress
@pytest.mark.slow
def test_adaptive_debouncer_long_session():
    """Test adaptive debouncer over extended session."""
    from asciidoc_artisan.core.adaptive_debouncer import AdaptiveDebouncer

    debouncer = AdaptiveDebouncer()

    # Simulate long editing session
    for minute in range(60):  # 1 hour
        for edit in range(20):  # 20 edits per minute
            debouncer.on_text_changed()

            # Vary document sizes
            doc_size = 10_000 + (minute * 1000)
            delay = debouncer.calculate_delay(document_size=doc_size)

            # Simulate some renders completing
            if edit % 5 == 0:
                render_time = 0.1 + (minute * 0.01)  # Slightly slower over time
                debouncer.on_render_complete(render_time)

    # Should maintain reasonable delays
    final_delay = debouncer.calculate_delay(document_size=50_000)
    assert 200 < final_delay < 2000, f"Final delay: {final_delay}ms"


@pytest.mark.stress
@pytest.mark.slow
def test_memory_profiler_long_running():
    """Test memory profiler over extended period."""
    from asciidoc_artisan.core.memory_profiler import MemoryProfiler

    profiler = MemoryProfiler()
    profiler.start()

    # Take many snapshots
    for i in range(100):
        profiler.take_snapshot(f"snapshot_{i}")

        # Allocate and free some memory
        data = [0] * 10_000
        del data

    profiler.stop()

    # Should have collected many snapshots
    assert len(profiler.snapshots) == 100

    # Should be able to generate stats
    stats = profiler.get_statistics()
    assert stats["snapshots_count"] == 100
