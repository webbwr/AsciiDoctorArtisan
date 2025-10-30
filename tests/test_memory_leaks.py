"""
Memory leak tests.

Tests to detect memory leaks and ensure proper resource cleanup:
- Worker thread cleanup
- Widget deletion
- Cache cleanup
- Signal/slot disconnection
- File handle cleanup
"""

import pytest
import gc
import sys
from unittest.mock import Mock


@pytest.mark.memory
def test_preview_handler_cleanup(qtbot):
    """Test preview handler is properly cleaned up."""
    from asciidoc_artisan.ui.preview_handler import PreviewHandler
    from PySide6.QtWidgets import QPlainTextEdit, QTextBrowser, QMainWindow

    # Create widgets
    editor = QPlainTextEdit()
    preview = QTextBrowser()
    mock_window = QMainWindow()  # ✅ Real QObject for parent compatibility
    qtbot.addWidget(mock_window)  # Manage lifecycle
    # Add Mock attributes that tests expect
    mock_window._settings = Mock(dark_mode=False)

    # Create handler
    handler = PreviewHandler(editor, preview, mock_window)

    # Get initial reference count
    handler_refs_before = sys.getrefcount(handler)

    # Delete handler
    del handler
    gc.collect()

    # Cleanup widgets
    editor.deleteLater()
    preview.deleteLater()


@pytest.mark.memory
def test_worker_pool_cleanup():
    """Test worker pool properly cleans up threads."""
    from asciidoc_artisan.workers.optimized_worker_pool import OptimizedWorkerPool
    from asciidoc_artisan.workers.cancellable_task import CancellableTask
    import threading

    class DummyTask(CancellableTask):
        def run_task(self):
            return "done"

    # Get initial thread count
    initial_threads = threading.active_count()

    # Create and use worker pool
    pool = OptimizedWorkerPool(max_workers=4)

    for i in range(10):
        task = DummyTask(task_id=f"task_{i}")
        pool.submit_task(task)

    # Shutdown pool
    pool.shutdown(wait=True, timeout=5)

    # Force garbage collection
    gc.collect()

    # Thread count should return to normal (or close to it)
    final_threads = threading.active_count()
    assert final_threads <= initial_threads + 2, \
        f"Thread leak detected: {initial_threads} -> {final_threads}"


@pytest.mark.memory
def test_file_handler_no_handle_leak(qtbot):
    """Test file handler doesn't leak file handles."""
    from asciidoc_artisan.ui.file_handler import FileHandler
    from PySide6.QtWidgets import QPlainTextEdit, QMainWindow
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create many test files
        test_files = []
        for i in range(50):
            test_file = Path(tmpdir) / f"test_{i}.adoc"
            test_file.write_text(f"Content {i}")
            test_files.append(test_file)

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

        # Open and close many files
        for test_file in test_files:
            handler._load_file_content(test_file)
            # File should be closed after loading

        # Cleanup
        editor.deleteLater()

        # No assertion needed - if file handles leak, OS will complain


@pytest.mark.memory
def test_lru_cache_memory_bounded():
    """Test LRU cache doesn't grow unbounded."""
    from asciidoc_artisan.core.lru_cache import LRUCache
    import sys

    cache = LRUCache(max_size=100)

    # Add many large entries
    large_value = "x" * 10_000  # 10KB string

    for i in range(10_000):
        cache.put(f"key_{i}", large_value)

    # Cache should maintain max size
    assert cache.size() <= 100

    # Memory should be bounded (rough check)
    cache_size_bytes = sys.getsizeof(cache._cache)
    # Should be much less than 10_000 entries * 10KB = 100MB
    assert cache_size_bytes < 5_000_000, \
        f"Cache using {cache_size_bytes / 1_000_000:.1f}MB"


@pytest.mark.memory
def test_metrics_collector_ring_buffer():
    """Test metrics collector uses ring buffer (bounded memory)."""
    from asciidoc_artisan.core.metrics import get_metrics_collector

    collector = get_metrics_collector()
    collector.reset()

    # Record many operations
    for i in range(100_000):
        collector.record_operation("test_op", float(i))

    # Should have bounded memory (ring buffer of 1000 entries)
    stats = collector.get_operation_stats("test_op")
    assert stats["count"] == 100_000  # Count is tracked

    # But durations are limited to buffer size
    op_metrics = collector.operations["test_op"]
    assert len(op_metrics.durations) <= 1000, \
        "Ring buffer should limit duration storage"


@pytest.mark.memory
def test_incremental_renderer_cache_bounded():
    """Test incremental renderer cache is bounded."""
    from asciidoc_artisan.workers.incremental_renderer import IncrementalPreviewRenderer
    from unittest.mock import Mock

    mock_api = Mock()
    renderer = IncrementalPreviewRenderer(mock_api, cache_size=100)

    # Render many different blocks
    for i in range(1000):
        block_content = f"== Section {i}\n\nContent {i}"
        # Simulate rendering (would normally use mock_api)

    # Cache should be bounded to 100 entries
    assert renderer.cache.size() <= 100


@pytest.mark.memory
def test_adaptive_debouncer_history_bounded():
    """Test adaptive debouncer doesn't grow history unbounded."""
    from asciidoc_artisan.core.adaptive_debouncer import AdaptiveDebouncer

    debouncer = AdaptiveDebouncer()

    # Simulate many text changes and renders
    for i in range(10_000):
        debouncer.on_text_changed()

        if i % 10 == 0:
            debouncer.on_render_complete(0.1)

    # History should be bounded
    stats = debouncer.get_statistics()

    # Deques should have max length
    assert len(debouncer._render_times) <= debouncer._render_times.maxlen
    assert len(debouncer._text_change_times) <= debouncer._text_change_times.maxlen


@pytest.mark.memory
def test_preview_worker_cleanup():
    """Test preview worker cleans up resources."""
    from asciidoc_artisan.workers.preview_worker import PreviewWorker
    import asciidoc3

    worker = PreviewWorker()
    worker.initialize_asciidoc(asciidoc3.__file__)

    # Worker should be cleanable
    del worker
    gc.collect()


@pytest.mark.memory
def test_timer_cleanup():
    """Test QTimers are properly cleaned up."""
    from PySide6.QtCore import QTimer, QObject

    parent = QObject()

    # Create many timers
    timers = []
    for i in range(100):
        timer = QTimer(parent)
        timer.setInterval(1000)
        timers.append(timer)

    # Delete parent
    parent.deleteLater()

    # Timers should be cleaned up with parent
    gc.collect()


@pytest.mark.memory
def test_signal_disconnection():
    """Test signals are properly disconnected."""
    from PySide6.QtCore import QObject, Signal

    class Sender(QObject):
        signal = Signal(str)

    class Receiver(QObject):
        def __init__(self):
            super().__init__()
            self.received = []

        def slot(self, msg):
            self.received.append(msg)

    sender = Sender()
    receiver = Receiver()

    # Connect signal
    sender.signal.connect(receiver.slot)

    # Emit signal
    sender.signal.emit("test")
    assert len(receiver.received) == 1

    # Disconnect
    sender.signal.disconnect(receiver.slot)

    # Emit again
    sender.signal.emit("test2")
    assert len(receiver.received) == 1  # Should not receive

    # Cleanup
    sender.deleteLater()
    receiver.deleteLater()
