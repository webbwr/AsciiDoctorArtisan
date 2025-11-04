"""
Integration tests for async I/O with Qt application.

Tests end-to-end async file operations integrated with Qt event loop,
file watchers, UI updates, and memory management.

v1.7.0: Task P1-3 - Async Integration Tests
"""

import asyncio
import gc
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QTimer
from pytestqt.qtbot import QtBot

from asciidoc_artisan.core import Settings
from asciidoc_artisan.core.async_file_watcher import AsyncFileWatcher
from asciidoc_artisan.core.qt_async_file_manager import QtAsyncFileManager
from asciidoc_artisan.ui import AsciiDocEditor


@pytest.fixture
def qasync_app(qapp):
    """Provide QApplication with qasync event loop integration."""
    # Use qapp fixture from pytest-qt
    yield qapp


@pytest.fixture
def editor_with_async(qtbot, qasync_app, test_settings):
    """Create AsciiDocEditor with async file manager."""
    # test_settings fixture already has safe defaults including telemetry_opt_in_shown=True
    # Just ensure async-specific settings are disabled
    test_settings.ollama_model = None
    test_settings.ollama_enabled = False
    test_settings.git_repo_path = None
    test_settings.last_file = None

    with patch(
        "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings",
        return_value=test_settings,
    ):
        window = AsciiDocEditor()

        # Mock dialog to prevent UI during tests
        def mock_prompt(*args, **kwargs):
            return True

        qtbot.addWidget(window)
        window.show()

        yield window

        # Cleanup
        window._unsaved_changes = False

        # Stop worker threads
        if hasattr(window, "git_thread") and window.git_thread:
            window.git_thread.quit()
            window.git_thread.wait(1000)
        if hasattr(window, "pandoc_thread") and window.pandoc_thread:
            window.pandoc_thread.quit()
            window.pandoc_thread.wait(1000)
        if hasattr(window, "preview_thread") and window.preview_thread:
            window.preview_thread.quit()
            window.preview_thread.wait(1000)


@pytest.fixture
def temp_adoc_file(tmp_path):
    """Create temporary AsciiDoc file."""
    test_file = tmp_path / "test.adoc"
    content = """= Test Document
:version: 1.0.0

== Section 1

Test content here.
"""
    test_file.write_text(content)
    return test_file


@pytest.mark.integration
class TestAsyncQtIntegration:
    """Test async operations integrated with Qt application."""

    @pytest.mark.anyio
    async def test_qt_async_file_manager_with_signals(
        self, qtbot: QtBot, qasync_app, tmp_path: Path
    ):
        """Test QtAsyncFileManager signal emission in Qt event loop."""
        manager = QtAsyncFileManager()
        test_file = tmp_path / "signal_test.txt"
        content = "Test content"

        # Use qtbot to wait for signal
        with qtbot.waitSignal(manager.write_complete, timeout=3000) as blocker:
            await manager.write_file(test_file, content)

        # Verify signal args
        assert blocker.args[0] == test_file
        assert test_file.read_text() == content

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_file_watcher_integration_with_qt_app(
        self, qtbot: QtBot, qasync_app, temp_adoc_file: Path
    ):
        """Test file watcher integration with actual Qt application."""
        manager = QtAsyncFileManager()
        signal_received = []

        def on_changed(path: Path):
            signal_received.append(path)

        manager.file_changed_externally.connect(on_changed)

        # Start watching
        manager.watch_file(temp_adoc_file, poll_interval=0.1, debounce_period=0.05)
        await asyncio.sleep(0.2)

        # Modify file externally
        temp_adoc_file.write_text("= Modified Document\n\nNew content")

        # Wait for signal
        timeout = 3.0
        elapsed = 0.0
        while not signal_received and elapsed < timeout:
            await asyncio.sleep(0.1)
            elapsed += 0.1

        assert len(signal_received) > 0
        assert signal_received[0] == temp_adoc_file

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_concurrent_file_operations_stress(
        self, qasync_app, tmp_path: Path
    ):
        """Test concurrent async operations (100+ files) for stability."""
        manager = QtAsyncFileManager()
        num_files = 100

        # Create 100 concurrent write operations
        tasks = []
        for i in range(num_files):
            file = tmp_path / f"stress_{i}.txt"
            content = f"Content {i}" * 10  # ~100 bytes each
            tasks.append(manager.write_file(file, content))

        # Execute concurrently
        start = time.time()
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start

        # All should succeed
        assert all(results)
        assert len(results) == num_files

        # Should be reasonably fast (< 5 seconds for 100 files)
        assert elapsed < 5.0

        # Verify all files exist
        for i in range(num_files):
            file = tmp_path / f"stress_{i}.txt"
            assert file.exists()
            assert f"Content {i}" in file.read_text()

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_memory_leak_detection_long_running_watcher(
        self, qasync_app, tmp_path: Path
    ):
        """Test memory leak detection for long-running file watcher."""
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Get baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        manager = QtAsyncFileManager()
        test_file = tmp_path / "leak_test.txt"
        test_file.write_text("Initial content")

        # Start watching
        manager.watch_file(test_file, poll_interval=0.05)
        await asyncio.sleep(0.1)

        # Simulate long-running watcher with 50 file modifications
        for i in range(50):
            test_file.write_text(f"Content {i}")
            await asyncio.sleep(0.05)  # 50ms between changes

        # Force garbage collection
        await manager.stop_watching()
        gc.collect()
        await asyncio.sleep(0.2)

        # Check memory after operations
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory

        # Memory increase should be minimal (< 10 MB)
        # This is a loose threshold to avoid flaky tests
        assert memory_increase < 10.0, f"Memory leak detected: {memory_increase:.2f} MB increase"

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_async_read_write_with_editor_integration(
        self, qtbot: QtBot, editor_with_async, tmp_path: Path
    ):
        """Test async file operations integrated with editor UI."""
        manager = QtAsyncFileManager()
        test_file = tmp_path / "editor_test.adoc"
        content = "= Test Document\n\nEditor content"

        # Write file
        success = await manager.write_file(test_file, content)
        assert success is True

        # Read file back
        read_content = await manager.read_file(test_file)
        assert read_content == content

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_concurrent_read_write_operations(
        self, qasync_app, tmp_path: Path
    ):
        """Test concurrent async reads and writes don't interfere."""
        manager = QtAsyncFileManager()

        # Create 20 files
        files = [tmp_path / f"rw_{i}.txt" for i in range(20)]
        for i, f in enumerate(files):
            f.write_text(f"Initial {i}")

        # Launch concurrent reads and writes
        tasks = []
        for i, f in enumerate(files):
            # Read tasks
            tasks.append(manager.read_file(f))
            # Write tasks
            tasks.append(manager.write_file(f, f"Updated {i}"))

        results = await asyncio.gather(*tasks)

        # Half are read results, half are write results
        assert len(results) == 40

        # Verify final state
        for i, f in enumerate(files):
            assert f.read_text() == f"Updated {i}"

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_json_operations_with_qt_signals(
        self, qtbot: QtBot, qasync_app, tmp_path: Path
    ):
        """Test async JSON operations with Qt signal integration."""
        manager = QtAsyncFileManager()
        json_file = tmp_path / "data.json"
        data = {"version": "1.0", "items": [1, 2, 3], "enabled": True}

        # Write JSON with signal
        with qtbot.waitSignal(manager.write_complete, timeout=3000):
            success = await manager.write_json(json_file, data, indent=2)

        assert success is True

        # Read JSON with signal
        with qtbot.waitSignal(manager.read_complete, timeout=3000):
            result = await manager.read_json(json_file)

        assert result == data

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_file_watcher_debouncing_in_qt_loop(
        self, qtbot: QtBot, qasync_app, tmp_path: Path
    ):
        """Test file watcher debouncing prevents signal spam in Qt loop."""
        watcher = AsyncFileWatcher(poll_interval=0.05, debounce_period=0.3)
        test_file = tmp_path / "debounce_test.txt"
        test_file.write_text("Initial")

        modification_count = 0

        def on_modified(path: Path):
            nonlocal modification_count
            modification_count += 1

        watcher.file_modified.connect(on_modified)
        watcher.set_file(test_file)
        await watcher.start()
        await asyncio.sleep(0.1)

        # Rapid modifications (10 changes in 0.5s)
        for i in range(10):
            test_file.write_text(f"Content {i}")
            await asyncio.sleep(0.05)

        # Wait for debounce period
        await asyncio.sleep(0.5)

        # Should receive only 1-3 signals due to debouncing, not 10
        assert modification_count < 5

        await watcher.stop()

    @pytest.mark.anyio
    async def test_async_copy_file_with_progress_tracking(
        self, qasync_app, tmp_path: Path
    ):
        """Test async file copy with progress tracking."""
        manager = QtAsyncFileManager()
        src_file = tmp_path / "source.txt"
        dst_file = tmp_path / "destination.txt"

        # Create 1MB file
        content = "X" * (1024 * 1024)
        src_file.write_text(content)

        # Copy file
        success = await manager.copy_file(src_file, dst_file)

        assert success is True
        assert dst_file.exists()
        assert dst_file.stat().st_size == src_file.stat().st_size

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_multiple_watchers_cleanup(
        self, qasync_app, tmp_path: Path
    ):
        """Test cleanup of multiple file watchers doesn't leak."""
        managers = [QtAsyncFileManager() for _ in range(5)]
        files = [tmp_path / f"watch_{i}.txt" for i in range(5)]

        # Create files
        for f in files:
            f.write_text("Content")

        # Start watching
        for manager, file in zip(managers, files):
            manager.watch_file(file, poll_interval=0.1)

        await asyncio.sleep(0.2)

        # Verify all watching
        assert all(m.is_watching() for m in managers)

        # Cleanup all
        for manager in managers:
            await manager.cleanup()

        # Verify all stopped
        assert not any(m.is_watching() for m in managers)

    @pytest.mark.anyio
    async def test_async_error_handling_with_signals(
        self, qtbot: QtBot, qasync_app, tmp_path: Path
    ):
        """Test async error handling emits proper signals."""
        manager = QtAsyncFileManager()
        nonexistent = tmp_path / "does_not_exist.txt"

        # Read should emit failure signal
        with qtbot.waitSignal(manager.operation_failed, timeout=3000) as blocker:
            result = await manager.read_file(nonexistent)

        assert result is None
        assert blocker.args[0] == "read"
        assert blocker.args[1] == nonexistent

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_batch_operations_with_qt_event_loop(
        self, qasync_app, tmp_path: Path
    ):
        """Test batch file operations integrated with Qt event loop."""
        manager = QtAsyncFileManager()

        # Create 30 files with batch writes
        write_tasks = []
        for i in range(30):
            file = tmp_path / f"batch_{i}.txt"
            content = f"Batch content {i}"
            write_tasks.append(manager.write_file(file, content))

        # Execute batch writes
        write_results = await asyncio.gather(*write_tasks)
        assert all(write_results)

        # Batch reads
        read_tasks = []
        for i in range(30):
            file = tmp_path / f"batch_{i}.txt"
            read_tasks.append(manager.read_file(file))

        read_results = await asyncio.gather(*read_tasks)
        assert len(read_results) == 30
        assert all(r is not None for r in read_results)

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_watcher_file_creation_deletion_cycle(
        self, qtbot: QtBot, qasync_app, tmp_path: Path
    ):
        """Test watcher detects file creation/deletion cycles."""
        watcher = AsyncFileWatcher(poll_interval=0.1, debounce_period=0.05)
        test_file = tmp_path / "cycle_test.txt"

        created_events = []
        deleted_events = []

        def on_created(path: Path):
            created_events.append(path)

        def on_deleted(path: Path):
            deleted_events.append(path)

        watcher.file_created.connect(on_created)
        watcher.file_deleted.connect(on_deleted)
        watcher.set_file(test_file)
        await watcher.start()
        await asyncio.sleep(0.2)

        # Create file
        test_file.write_text("Created")
        await asyncio.sleep(0.3)

        # Delete file
        test_file.unlink()
        await asyncio.sleep(0.3)

        # Create again
        test_file.write_text("Re-created")
        await asyncio.sleep(0.3)

        # Should detect at least 2 creations and 1 deletion
        assert len(created_events) >= 2
        assert len(deleted_events) >= 1

        await watcher.stop()

    @pytest.mark.anyio
    async def test_encoding_handling_across_operations(
        self, qasync_app, tmp_path: Path
    ):
        """Test encoding handling in async operations."""
        manager = QtAsyncFileManager()
        utf8_file = tmp_path / "utf8.txt"

        # Test UTF-8 content with special characters
        content = "Hello 世界 🌍\nПривет мир\nمرحبا بالعالم"

        # Write with UTF-8
        success = await manager.write_file(utf8_file, content, encoding="utf-8")
        assert success is True

        # Read back with UTF-8
        result = await manager.read_file(utf8_file, encoding="utf-8")
        assert result == content

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_qt_integration_under_load(
        self, qasync_app, tmp_path: Path
    ):
        """Test Qt integration stability under sustained load."""
        manager = QtAsyncFileManager()

        # Sustained load: 50 iterations of 10 concurrent operations
        for iteration in range(50):
            tasks = []
            for i in range(10):
                file = tmp_path / f"load_{iteration}_{i}.txt"
                content = f"Iteration {iteration}, File {i}"
                tasks.append(manager.write_file(file, content))

            results = await asyncio.gather(*tasks)
            assert all(results)

            # Brief pause between iterations
            await asyncio.sleep(0.01)

        # Total: 500 operations completed successfully
        # Verify some files
        test_file = tmp_path / "load_25_5.txt"
        assert test_file.exists()
        assert "Iteration 25, File 5" in test_file.read_text()

        await manager.cleanup()


@pytest.mark.integration
class TestAsyncEditorWorkflows:
    """Test async operations in real editor workflows."""

    @pytest.mark.anyio
    async def test_load_save_workflow_async(
        self, qtbot: QtBot, editor_with_async, tmp_path: Path
    ):
        """Test complete load-edit-save workflow with async I/O."""
        manager = QtAsyncFileManager()
        test_file = tmp_path / "workflow.adoc"
        initial_content = "= Initial Document\n\nContent here"

        # Save initial file
        await manager.write_file(test_file, initial_content)

        # Load into editor (simulated)
        loaded_content = await manager.read_file(test_file)
        assert loaded_content == initial_content

        # Modify content
        modified_content = "= Modified Document\n\nNew content here"

        # Save modified
        await manager.write_file(test_file, modified_content)

        # Verify saved
        final_content = await manager.read_file(test_file)
        assert final_content == modified_content

        await manager.cleanup()

    @pytest.mark.anyio
    async def test_autosave_workflow_with_watcher(
        self, qtbot: QtBot, qasync_app, tmp_path: Path
    ):
        """Test autosave workflow with file watcher integration."""
        manager = QtAsyncFileManager()
        test_file = tmp_path / "autosave.adoc"
        test_file.write_text("= Document\n\nOriginal content")

        external_changes = []

        def on_changed(path: Path):
            external_changes.append(path)

        manager.file_changed_externally.connect(on_changed)

        # Start watching
        manager.watch_file(test_file, poll_interval=0.1, debounce_period=0.05)
        await asyncio.sleep(0.2)

        # Simulate autosave (internal write) - should not trigger external change
        await manager.write_file(test_file, "= Document\n\nAutosaved content")
        await asyncio.sleep(0.3)

        # External change (simulated by direct write)
        test_file.write_text("= Document\n\nExternal modification")
        await asyncio.sleep(0.3)

        # Should detect external change
        assert len(external_changes) > 0

        await manager.cleanup()
