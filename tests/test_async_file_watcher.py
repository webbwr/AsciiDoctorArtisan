"""
Tests for AsyncFileWatcher - Async file change monitoring.

Tests the async file watcher that monitors files for external changes
without blocking the UI thread.

v1.7.0: Task 4 - Enhanced Async I/O
"""

import asyncio
import time
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from asciidoc_artisan.core.async_file_watcher import AsyncFileWatcher, FileChangeEvent


class TestAsyncFileWatcher:
    """Test async file watcher functionality."""

    @pytest.fixture
    def temp_file(self, tmp_path: Path) -> Path:
        """Create a temporary file for testing."""
        test_file = tmp_path / "test_watch.txt"
        test_file.write_text("Initial content")
        return test_file

    @pytest.fixture
    def watcher(self, qtbot: QtBot) -> AsyncFileWatcher:
        """Create a file watcher instance."""
        # Fast polling for tests (0.1s instead of 1s)
        watcher = AsyncFileWatcher(poll_interval=0.1, debounce_period=0.05)
        yield watcher
        # Cleanup
        if watcher.is_running():
            asyncio.get_event_loop().run_until_complete(watcher.stop())

    @pytest.mark.asyncio
    async def test_watcher_initialization(self):
        """Test watcher initializes correctly."""
        watcher = AsyncFileWatcher(poll_interval=1.0, debounce_period=0.5)

        assert watcher.poll_interval == 1.0
        assert watcher.debounce_period == 0.5
        assert not watcher.is_running()
        assert watcher.get_file_path() is None

    @pytest.mark.asyncio
    async def test_set_file(self, temp_file: Path):
        """Test setting file to watch."""
        watcher = AsyncFileWatcher()
        watcher.set_file(temp_file)

        assert watcher.get_file_path() == temp_file
        assert watcher._file_exists is True
        assert watcher._last_mtime is not None
        assert watcher._last_size is not None

    @pytest.mark.asyncio
    async def test_set_nonexistent_file(self, tmp_path: Path):
        """Test setting file that doesn't exist yet."""
        nonexistent = tmp_path / "not_created_yet.txt"
        watcher = AsyncFileWatcher()
        watcher.set_file(nonexistent)

        assert watcher.get_file_path() == nonexistent
        assert watcher._file_exists is False
        assert watcher._last_mtime is None
        assert watcher._last_size is None

    @pytest.mark.asyncio
    async def test_start_stop(self, watcher: AsyncFileWatcher, temp_file: Path):
        """Test starting and stopping watcher."""
        watcher.set_file(temp_file)

        # Start watcher
        await watcher.start()
        assert watcher.is_running()

        # Stop watcher
        await watcher.stop()
        assert not watcher.is_running()

    @pytest.mark.asyncio
    async def test_detect_file_modification(
        self, qtbot: QtBot, watcher: AsyncFileWatcher, temp_file: Path
    ):
        """Test detecting file modifications."""
        watcher.set_file(temp_file)

        # Track signal emission
        signal_received = []

        def on_modified(path: Path):
            signal_received.append(path)

        watcher.file_modified.connect(on_modified)

        # Start watcher
        await watcher.start()
        await asyncio.sleep(0.2)

        # Modify file
        temp_file.write_text("Modified content")

        # Wait for signal with asyncio event loop running
        timeout = 3.0
        elapsed = 0.0
        while not signal_received and elapsed < timeout:
            await asyncio.sleep(0.1)
            elapsed += 0.1

        # Verify signal was emitted
        assert len(signal_received) > 0, "file_modified signal not emitted"
        assert signal_received[0] == temp_file

        await watcher.stop()

    @pytest.mark.asyncio
    async def test_detect_file_deletion(
        self, qtbot: QtBot, watcher: AsyncFileWatcher, temp_file: Path
    ):
        """Test detecting file deletion."""
        watcher.set_file(temp_file)

        # Track signal emission
        signal_received = []

        def on_deleted(path: Path):
            signal_received.append(path)

        watcher.file_deleted.connect(on_deleted)

        # Start watcher
        await watcher.start()
        await asyncio.sleep(0.2)

        # Delete file
        temp_file.unlink()

        # Wait for signal with asyncio event loop running
        timeout = 3.0
        elapsed = 0.0
        while not signal_received and elapsed < timeout:
            await asyncio.sleep(0.1)
            elapsed += 0.1

        # Verify signal was emitted
        assert len(signal_received) > 0, "file_deleted signal not emitted"
        assert signal_received[0] == temp_file

        await watcher.stop()

    @pytest.mark.asyncio
    async def test_detect_file_creation(
        self, qtbot: QtBot, watcher: AsyncFileWatcher, tmp_path: Path
    ):
        """Test detecting file creation."""
        new_file = tmp_path / "newly_created.txt"
        watcher.set_file(new_file)

        # Track signal emission
        signal_received = []

        def on_created(path: Path):
            signal_received.append(path)

        watcher.file_created.connect(on_created)

        # Start watcher
        await watcher.start()
        await asyncio.sleep(0.2)

        # Create file
        new_file.write_text("New file content")

        # Wait for signal with asyncio event loop running
        timeout = 3.0
        elapsed = 0.0
        while not signal_received and elapsed < timeout:
            await asyncio.sleep(0.1)
            elapsed += 0.1

        # Verify signal was emitted
        assert len(signal_received) > 0, "file_created signal not emitted"
        assert signal_received[0] == new_file

        await watcher.stop()

    @pytest.mark.asyncio
    async def test_debouncing(self, qtbot: QtBot, temp_file: Path):
        """Test debouncing prevents excessive signals."""
        # Watcher with very short debounce for testing
        watcher = AsyncFileWatcher(poll_interval=0.05, debounce_period=0.3)
        watcher.set_file(temp_file)

        modification_count = 0

        def on_modified(path: Path):
            nonlocal modification_count
            modification_count += 1

        watcher.file_modified.connect(on_modified)
        await watcher.start()
        await asyncio.sleep(0.1)

        # Rapid modifications
        for i in range(5):
            temp_file.write_text(f"Content {i}")
            await asyncio.sleep(0.05)  # Faster than debounce period

        # Wait for debounce period
        await asyncio.sleep(0.5)

        # Should receive only 1-2 signals due to debouncing, not 5
        assert modification_count < 5

        await watcher.stop()

    @pytest.mark.asyncio
    async def test_multiple_start_warning(
        self, watcher: AsyncFileWatcher, temp_file: Path, caplog
    ):
        """Test warning on multiple starts."""
        watcher.set_file(temp_file)

        await watcher.start()
        await watcher.start()  # Second start should log warning

        assert "already running" in caplog.text.lower()

        await watcher.stop()

    @pytest.mark.asyncio
    async def test_start_without_file(self, watcher: AsyncFileWatcher, caplog):
        """Test starting without setting file."""
        await watcher.start()

        assert "no file set" in caplog.text.lower()
        assert not watcher.is_running()

    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, watcher: AsyncFileWatcher, temp_file: Path):
        """Test graceful shutdown during active watching."""
        watcher.set_file(temp_file)
        await watcher.start()

        # Modify file while watching
        temp_file.write_text("Content during shutdown")

        # Should stop cleanly
        await watcher.stop()
        assert not watcher.is_running()


class TestFileChangeEvent:
    """Test FileChangeEvent dataclass."""

    def test_event_creation(self, tmp_path: Path):
        """Test creating file change event."""
        path = tmp_path / "test.txt"
        timestamp = time.time()

        event = FileChangeEvent(path=path, event_type="modified", timestamp=timestamp)

        assert event.path == path
        assert event.event_type == "modified"
        assert event.timestamp == timestamp

    def test_event_types(self, tmp_path: Path):
        """Test different event types."""
        path = tmp_path / "test.txt"
        timestamp = time.time()

        modified = FileChangeEvent(path, "modified", timestamp)
        deleted = FileChangeEvent(path, "deleted", timestamp)
        created = FileChangeEvent(path, "created", timestamp)

        assert modified.event_type == "modified"
        assert deleted.event_type == "deleted"
        assert created.event_type == "created"
