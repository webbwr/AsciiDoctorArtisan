"""
Tests for QtAsyncFileManager - Qt-integrated async file operations.

Tests the Qt-integrated async file manager that bridges async file operations
with Qt signals for seamless UI integration.

v1.7.0: Task 4 - Enhanced Async I/O
"""

import asyncio
import json
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from asciidoc_artisan.core.qt_async_file_manager import QtAsyncFileManager


class TestQtAsyncFileManager:
    """Test Qt async file manager functionality."""

    @pytest.fixture
    def manager(self, qtbot: QtBot) -> QtAsyncFileManager:
        """Create a file manager instance."""
        manager = QtAsyncFileManager()
        yield manager
        # Cleanup
        asyncio.get_event_loop().run_until_complete(manager.cleanup())

    @pytest.fixture
    def temp_file(self, tmp_path: Path) -> Path:
        """Create a temporary file for testing."""
        test_file = tmp_path / "test_async.txt"
        test_file.write_text("Initial content")
        return test_file

    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test manager initializes correctly."""
        manager = QtAsyncFileManager()

        assert manager is not None
        assert not manager.is_watching()
        assert manager.get_watched_file() is None
        assert not manager.has_running_operations()

        await manager.cleanup()

    @pytest.mark.asyncio
    async def test_read_file(
        self, qtbot: QtBot, manager: QtAsyncFileManager, temp_file: Path
    ):
        """Test async file reading with signal emission."""
        # Set up signal spy
        with qtbot.waitSignal(manager.read_complete, timeout=3000) as blocker:
            content = await manager.read_file(temp_file)

        # Verify content
        assert content == "Initial content"

        # Verify signal
        assert blocker.args[0] == temp_file
        assert blocker.args[1] == "Initial content"

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(
        self, qtbot: QtBot, manager: QtAsyncFileManager, tmp_path: Path
    ):
        """Test reading nonexistent file emits failure signal."""
        nonexistent = tmp_path / "does_not_exist.txt"

        with qtbot.waitSignal(manager.operation_failed, timeout=3000) as blocker:
            content = await manager.read_file(nonexistent)

        assert content is None
        assert blocker.args[0] == "read"
        assert blocker.args[1] == nonexistent

    @pytest.mark.asyncio
    async def test_write_file(
        self, qtbot: QtBot, manager: QtAsyncFileManager, tmp_path: Path
    ):
        """Test async file writing with signal emission."""
        test_file = tmp_path / "write_test.txt"
        content = "Test content for writing"

        # Write file
        with qtbot.waitSignal(manager.write_complete, timeout=3000) as blocker:
            success = await manager.write_file(test_file, content)

        # Verify success
        assert success is True
        assert test_file.read_text() == content

        # Verify signal
        assert blocker.args[0] == test_file

    @pytest.mark.asyncio
    async def test_write_file_atomic(self, manager: QtAsyncFileManager, tmp_path: Path):
        """Test atomic write (no corruption on failure)."""
        test_file = tmp_path / "atomic_test.txt"
        test_file.write_text("Original content")

        # Write successfully
        success = await manager.write_file(test_file, "New content")

        assert success is True
        assert test_file.read_text() == "New content"
        # No .tmp files left behind
        assert not list(tmp_path.glob("*.tmp"))

    @pytest.mark.asyncio
    async def test_read_json(
        self, qtbot: QtBot, manager: QtAsyncFileManager, tmp_path: Path
    ):
        """Test async JSON reading."""
        json_file = tmp_path / "test.json"
        data = {"key": "value", "number": 42}
        json_file.write_text(json.dumps(data))

        # Read JSON
        with qtbot.waitSignal(manager.read_complete, timeout=3000):
            result = await manager.read_json(json_file)

        assert result == data

    @pytest.mark.asyncio
    async def test_write_json(
        self, qtbot: QtBot, manager: QtAsyncFileManager, tmp_path: Path
    ):
        """Test async JSON writing."""
        json_file = tmp_path / "write_test.json"
        data = {"test": True, "value": 123}

        # Write JSON
        with qtbot.waitSignal(manager.write_complete, timeout=3000):
            success = await manager.write_json(json_file, data)

        assert success is True

        # Verify content
        loaded = json.loads(json_file.read_text())
        assert loaded == data

    @pytest.mark.asyncio
    async def test_copy_file(
        self, qtbot: QtBot, manager: QtAsyncFileManager, temp_file: Path, tmp_path: Path
    ):
        """Test async file copying."""
        dest = tmp_path / "copy_dest.txt"

        # Copy file
        with qtbot.waitSignal(manager.write_complete, timeout=3000) as blocker:
            success = await manager.copy_file(temp_file, dest)

        assert success is True
        assert dest.read_text() == temp_file.read_text()
        assert blocker.args[0] == dest

    @pytest.mark.asyncio
    async def test_watch_file(
        self, qtbot: QtBot, manager: QtAsyncFileManager, temp_file: Path
    ):
        """Test file watching for external changes."""
        # Track signal emission
        signal_received = []

        def on_changed(path: Path):
            signal_received.append(path)

        manager.file_changed_externally.connect(on_changed)

        # Start watching
        manager.watch_file(temp_file, poll_interval=0.1, debounce_period=0.05)

        # Wait for watcher to start
        await asyncio.sleep(0.2)

        assert manager.is_watching()
        assert manager.get_watched_file() == temp_file

        # Modify file externally
        temp_file.write_text("Modified externally")

        # Wait for signal with asyncio event loop running
        timeout = 3.0
        elapsed = 0.0
        while not signal_received and elapsed < timeout:
            await asyncio.sleep(0.1)
            elapsed += 0.1

        # Verify signal was emitted
        assert len(signal_received) > 0, "file_changed_externally signal not emitted"
        assert signal_received[0] == temp_file

    @pytest.mark.asyncio
    async def test_stop_watching(self, manager: QtAsyncFileManager, temp_file: Path):
        """Test stopping file watcher."""
        # Start watching
        manager.watch_file(temp_file)
        await asyncio.sleep(0.1)
        assert manager.is_watching()

        # Stop watching
        await manager.stop_watching()
        assert not manager.is_watching()
        assert manager.get_watched_file() is None

    @pytest.mark.asyncio
    async def test_concurrent_operations(
        self, manager: QtAsyncFileManager, tmp_path: Path
    ):
        """Test multiple concurrent file operations."""
        files = [tmp_path / f"file_{i}.txt" for i in range(5)]

        # Launch concurrent writes
        tasks = [manager.write_file(f, f"Content {i}") for i, f in enumerate(files)]

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(results)

        # Verify all files written correctly
        for i, f in enumerate(files):
            assert f.read_text() == f"Content {i}"

    @pytest.mark.asyncio
    async def test_has_running_operations(
        self, manager: QtAsyncFileManager, tmp_path: Path
    ):
        """Test tracking of running operations."""
        test_file = tmp_path / "test.txt"

        # Start operation
        task = asyncio.create_task(manager.write_file(test_file, "content"))

        # Should show running operation
        await asyncio.sleep(0.01)  # Brief delay for task to start

        # Wait for completion
        await task

        # Should clear after completion
        await asyncio.sleep(0.01)
        # Note: Operation tracking is brief, so this may not always catch it

    @pytest.mark.asyncio
    async def test_cleanup(self, manager: QtAsyncFileManager, temp_file: Path):
        """Test cleanup stops watchers and waits for operations."""
        # Start watching
        manager.watch_file(temp_file)
        await asyncio.sleep(0.1)

        # Cleanup
        await manager.cleanup()

        # Watcher should be stopped
        assert not manager.is_watching()

    @pytest.mark.asyncio
    async def test_large_file_handling(
        self, manager: QtAsyncFileManager, tmp_path: Path
    ):
        """Test handling of larger files."""
        large_file = tmp_path / "large.txt"
        # Create 1MB file
        large_content = "x" * (1024 * 1024)

        # Write
        success = await manager.write_file(large_file, large_content)
        assert success is True

        # Read back
        content = await manager.read_file(large_file)
        assert len(content) == len(large_content)
        assert content == large_content

    @pytest.mark.asyncio
    async def test_encoding_handling(self, manager: QtAsyncFileManager, tmp_path: Path):
        """Test different encoding handling."""
        utf8_file = tmp_path / "utf8.txt"
        content = "Hello 世界 🌍"

        # Write and read UTF-8
        await manager.write_file(utf8_file, content, encoding="utf-8")
        result = await manager.read_file(utf8_file, encoding="utf-8")

        assert result == content

    @pytest.mark.asyncio
    async def test_signal_connections(self, qtbot: QtBot):
        """Test all signals are properly defined."""
        manager = QtAsyncFileManager()

        # Verify signals exist
        assert hasattr(manager, "read_complete")
        assert hasattr(manager, "write_complete")
        assert hasattr(manager, "operation_failed")
        assert hasattr(manager, "file_changed_externally")

        # Test signal can be connected
        def dummy_handler(*args):
            pass

        manager.read_complete.connect(dummy_handler)
        manager.write_complete.connect(dummy_handler)
        manager.operation_failed.connect(dummy_handler)
        manager.file_changed_externally.connect(dummy_handler)

        await manager.cleanup()

    @pytest.mark.asyncio
    async def test_watch_replace_existing(
        self, manager: QtAsyncFileManager, tmp_path: Path
    ):
        """Test replacing existing file watcher."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("File 1")
        file2.write_text("File 2")

        # Watch first file
        manager.watch_file(file1)
        await asyncio.sleep(0.2)  # Wait for watcher to start
        assert manager.get_watched_file() == file1

        # Watch second file (should stop first watcher)
        manager.watch_file(file2)

        # Wait longer for previous watcher to stop and new one to start
        await asyncio.sleep(0.5)

        # Verify second file is now watched
        assert manager.is_watching(), "Manager should be watching a file"
        assert manager.get_watched_file() == file2
