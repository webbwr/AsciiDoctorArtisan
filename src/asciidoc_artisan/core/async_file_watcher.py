"""
Async File Watcher - Monitor files for external changes.

Implements v1.7.0 Task 4: Enhanced Async I/O - File Watcher
- Asynchronous file monitoring without blocking UI
- Detects external changes to files
- Debouncing to avoid excessive notifications
- Qt signal integration via qasync

This module provides file watching capabilities:
- Monitor single file for changes
- Detect modifications, deletions, renames
- Debounced notifications
- Non-blocking async implementation
- Integrates with Qt event loop via qasync

Design Goals:
- No UI blocking
- Efficient polling with asyncio
- Configurable debounce period
- Simple API for Qt applications
"""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


@dataclass
class FileChangeEvent:
    """
    File change event data.

    Attributes:
        path: Path to file that changed
        event_type: Type of change (modified, deleted, created)
        timestamp: When change was detected
    """

    path: Path
    event_type: str  # 'modified', 'deleted', 'created'
    timestamp: float


class AsyncFileWatcher(QObject):
    """
    Async file watcher with Qt integration.

    Monitors a file for external changes and emits Qt signals.
    Uses asyncio for non-blocking polling with configurable intervals.

    Features:
    - Non-blocking async monitoring
    - Debouncing to reduce noise
    - Qt signal emission on changes
    - Automatic start/stop
    - Graceful shutdown

    Signals:
        file_modified: Emitted when file content changes
        file_deleted: Emitted when file is deleted
        file_created: Emitted when file is created
        error: Emitted on watcher errors

    Example:
        watcher = AsyncFileWatcher()
        watcher.file_modified.connect(on_file_modified)
        watcher.set_file(Path("/path/to/file.adoc"))
        await watcher.start()

        # Later...
        await watcher.stop()
    """

    # Signals
    file_modified = Signal(Path)  # Emitted when file is modified
    file_deleted = Signal(Path)  # Emitted when file is deleted
    file_created = Signal(Path)  # Emitted when file is created
    error = Signal(str)  # Emitted on errors

    def __init__(
        self,
        poll_interval: float = 1.0,
        debounce_period: float = 0.5,
        adaptive_polling: bool = True,
        min_poll_interval: float = 0.1,
        max_poll_interval: float = 5.0,
    ):
        """
        Initialize async file watcher.

        Args:
            poll_interval: Initial/default poll interval (seconds)
            debounce_period: Minimum time between notifications (seconds)
            adaptive_polling: Enable adaptive poll interval adjustment
            min_poll_interval: Minimum poll interval for active files (seconds)
            max_poll_interval: Maximum poll interval for idle files (seconds)
        """
        super().__init__()

        self.base_poll_interval = poll_interval
        self.poll_interval = poll_interval
        self.debounce_period = debounce_period

        # Adaptive polling settings (QA-13)
        self.adaptive_polling = adaptive_polling
        self.min_poll_interval = min_poll_interval
        self.max_poll_interval = max_poll_interval

        self._file_path: Path | None = None
        self._last_mtime: float | None = None
        self._last_size: int | None = None
        self._file_exists: bool = False

        self._watch_task: asyncio.Task[None] | None = None
        self._running = False

        self._last_notification_time: float = 0.0

        # Adaptive polling state (QA-13)
        self._last_change_time: float = 0.0
        self._idle_count: int = 0
        self._activity_streak: int = 0

        logger.debug(
            f"AsyncFileWatcher initialized (poll={poll_interval}s, "
            f"debounce={debounce_period}s, adaptive={adaptive_polling})"
        )

    def set_file(self, file_path: Path) -> None:
        """
        Set file to watch.

        Args:
            file_path: Path to file to monitor
        """
        self._file_path = file_path

        # Initialize file state
        if file_path.exists():
            try:
                stat = file_path.stat()
                self._last_mtime = stat.st_mtime
                self._last_size = stat.st_size
                self._file_exists = True
                logger.info(f"Watching file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to stat file {file_path}: {e}")
                self._last_mtime = None
                self._last_size = None
                self._file_exists = False
        else:
            self._last_mtime = None
            self._last_size = None
            self._file_exists = False
            logger.info(f"Watching file (not yet created): {file_path}")

    async def start(self) -> None:
        """Start watching file."""
        if self._running:
            logger.warning("File watcher already running")
            return

        if not self._file_path:
            logger.error("Cannot start watcher: no file set")
            return

        self._running = True
        self._watch_task = asyncio.create_task(self._watch_loop())
        logger.info(f"File watcher started for: {self._file_path}")

    async def stop(self) -> None:
        """Stop watching file."""
        if not self._running:
            return

        self._running = False

        if self._watch_task:
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass
            self._watch_task = None

        logger.info(f"File watcher stopped for: {self._file_path}")

    async def _watch_loop(self) -> None:
        """
        Main watch loop.

        Polls file periodically and detects changes.
        """
        while self._running:
            try:
                await self._check_file()
                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in watch loop: {e}")
                self.error.emit(str(e))
                await asyncio.sleep(self.poll_interval)

    async def _check_file(self) -> None:
        """
        Check file for changes.

        MA principle: Reduced from 73→20 lines by extracting 3 helpers (73% reduction).

        Compares current state with last known state.
        """
        if not self._file_path:
            return

        current_time = asyncio.get_event_loop().time()
        file_exists = self._file_path.exists()

        # Handle three file state transitions
        if self._file_exists and not file_exists:
            file_changed = self._handle_file_deleted(current_time)
        elif not self._file_exists and file_exists:
            file_changed = self._handle_file_created(current_time)
        else:
            file_changed = self._handle_file_modified(file_exists, current_time)

        self._adjust_poll_interval(file_changed, current_time)

    def _handle_file_deleted(self, current_time: float) -> bool:
        """Handle file deletion event.

        MA principle: Extracted helper (13 lines) - focused deletion logic.

        Args:
            current_time: Current timestamp

        Returns:
            True to indicate file changed
        """
        if self._should_notify(current_time):
            logger.info(f"File deleted: {self._file_path}")
            self.file_deleted.emit(self._file_path)
            self._last_notification_time = current_time

        self._file_exists = False
        self._last_mtime = None
        self._last_size = None
        return True

    def _handle_file_created(self, current_time: float) -> bool:
        """Handle file creation event.

        MA principle: Extracted helper (19 lines) - focused creation logic.

        Args:
            current_time: Current timestamp

        Returns:
            True to indicate file changed
        """
        if self._should_notify(current_time):
            logger.info(f"File created: {self._file_path}")
            self.file_created.emit(self._file_path)
            self._last_notification_time = current_time

        self._file_exists = True

        # Update state with new file metadata
        # Type narrowing: _file_path is guaranteed to be Path (checked in _check_file)
        assert self._file_path is not None
        try:
            stat = self._file_path.stat()
            self._last_mtime = stat.st_mtime
            self._last_size = stat.st_size
        except Exception as e:
            logger.error(f"Failed to stat file {self._file_path}: {e}")

        return True

    def _handle_file_modified(self, file_exists: bool, current_time: float) -> bool:
        """Handle file modification event.

        MA principle: Extracted helper (27 lines) - focused modification logic.

        Args:
            file_exists: Whether file currently exists
            current_time: Current timestamp

        Returns:
            True if file changed, False otherwise
        """
        if not file_exists:
            return False

        # Type narrowing: _file_path is guaranteed to be Path (checked in _check_file)
        assert self._file_path is not None
        try:
            stat = self._file_path.stat()
            current_mtime = stat.st_mtime
            current_size = stat.st_size

            # Check if modified (mtime or size changed)
            mtime_changed = self._last_mtime is not None and current_mtime != self._last_mtime
            size_changed = self._last_size is not None and current_size != self._last_size

            if mtime_changed or size_changed:
                if self._should_notify(current_time):
                    logger.info(f"File modified: {self._file_path}")
                    self.file_modified.emit(self._file_path)
                    self._last_notification_time = current_time

                # Update state
                self._last_mtime = current_mtime
                self._last_size = current_size
                return True

        except Exception as e:
            logger.error(f"Failed to check file {self._file_path}: {e}")

        return False

    def _should_notify(self, current_time: float) -> bool:
        """
        Check if enough time has passed since last notification (debouncing).

        Args:
            current_time: Current time

        Returns:
            True if should notify, False if too soon
        """
        time_since_last = current_time - self._last_notification_time
        return time_since_last >= self.debounce_period

    def _adjust_poll_interval(self, file_changed: bool, current_time: float) -> None:
        """
        Adjust poll interval based on file activity (QA-13: Adaptive Polling).

        Strategy:
        - Active files (recent changes): Fast polling (0.1-0.5s)
        - Idle files (no recent changes): Slow polling (2-5s)
        - Exponential backoff for increasingly idle files
        - Quick response to activity resumption

        Args:
            file_changed: Whether file changed in this check
            current_time: Current time
        """
        if not self.adaptive_polling:
            return  # Adaptive polling disabled

        if file_changed:
            # File is active - use fast polling
            self._activity_streak += 1
            self._idle_count = 0
            self._last_change_time = current_time

            # Faster polling for active files (min 0.1s)
            self.poll_interval = max(self.min_poll_interval, self.base_poll_interval / 2)

            logger.debug(
                f"Active file detected (streak={self._activity_streak}), poll interval: {self.poll_interval:.2f}s"
            )
        else:
            # File is idle - increase polling interval
            time_since_change = current_time - self._last_change_time

            if time_since_change > 10.0:  # Idle for 10+ seconds
                self._idle_count += 1
                self._activity_streak = 0

                # Exponential backoff: 1.0s → 2.0s → 4.0s → 5.0s (capped)
                backoff_multiplier = min(2**self._idle_count, 5)
                self.poll_interval = min(self.base_poll_interval * backoff_multiplier, self.max_poll_interval)

                if self._idle_count <= 3:  # Only log first few backoffs
                    logger.debug(
                        f"Idle file detected (count={self._idle_count}), poll interval: {self.poll_interval:.2f}s"
                    )

    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._running

    def get_file_path(self) -> Path | None:
        """Get current file being watched."""
        return self._file_path
