"""Qt Async File Manager - Async file operations with Qt integration and signals."""

import asyncio
import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal

from asciidoc_artisan.core.async_file_ops import (
    async_atomic_save_json,
    async_atomic_save_text,
    async_copy_file,
    async_read_json,
    async_read_text,
)
from asciidoc_artisan.core.async_file_watcher import AsyncFileWatcher

logger = logging.getLogger(__name__)


class QtAsyncFileManager(QObject):
    """Qt-integrated async file manager with signals for read/write/watch operations."""

    # Signals
    read_complete = Signal(Path, str)  # path, content
    write_complete = Signal(Path)  # path
    operation_failed = Signal(str, Path, str)  # operation, path, error
    file_changed_externally = Signal(Path)  # path

    def __init__(self) -> None:
        """Initialize Qt async file manager."""
        super().__init__()

        # File watcher
        self._watcher: AsyncFileWatcher | None = None
        self._watched_file: Path | None = None

        # Track running operations
        self._running_operations: set[int] = set()

        logger.info("QtAsyncFileManager initialized")

    async def read_file(self, file_path: Path, encoding: str = "utf-8") -> str | None:
        """
        Read file asynchronously.

        Args:
            file_path: Path to file
            encoding: Text encoding (default: utf-8)

        Returns:
            File content as string, or None on error

        Emits:
            read_complete: On success (path, content)
            operation_failed: On error (operation, path, error)
        """
        operation_id = id(asyncio.current_task())
        self._running_operations.add(operation_id)

        try:
            logger.debug(f"Reading file: {file_path}")
            content = await async_read_text(file_path, encoding)

            if content is not None:
                self.read_complete.emit(file_path, content)
                logger.info(f"File read complete: {file_path} ({len(content)} chars)")
                return content
            else:
                error = "Read returned None"
                self.operation_failed.emit("read", file_path, error)
                logger.error(f"File read failed: {file_path}")
                return None

        except Exception as e:
            error = str(e)
            self.operation_failed.emit("read", file_path, error)
            logger.error(f"File read error: {file_path}: {e}")
            return None

        finally:
            self._running_operations.discard(operation_id)

    async def write_file(self, file_path: Path, content: str, encoding: str = "utf-8") -> bool:
        """
        Write file asynchronously with atomic save.

        Args:
            file_path: Path to file
            content: Content to write
            encoding: Text encoding (default: utf-8)

        Returns:
            True if successful, False otherwise

        Emits:
            write_complete: On success (path)
            operation_failed: On error (operation, path, error)
        """
        operation_id = id(asyncio.current_task())
        self._running_operations.add(operation_id)

        try:
            logger.debug(f"Writing file: {file_path}")
            success = await async_atomic_save_text(file_path, content, encoding)

            if success:
                self.write_complete.emit(file_path)
                logger.info(f"File write complete: {file_path} ({len(content)} chars)")
                return True
            else:
                error = "Atomic save returned False"
                self.operation_failed.emit("write", file_path, error)
                logger.error(f"File write failed: {file_path}")
                return False

        except Exception as e:
            error = str(e)
            self.operation_failed.emit("write", file_path, error)
            logger.error(f"File write error: {file_path}: {e}")
            return False

        finally:
            self._running_operations.discard(operation_id)

    async def read_json(self, file_path: Path, encoding: str = "utf-8") -> dict[str, Any] | None:
        """
        Read and parse JSON file asynchronously.

        Args:
            file_path: Path to JSON file
            encoding: Text encoding (default: utf-8)

        Returns:
            Parsed JSON as dictionary, or None on error

        Emits:
            read_complete: On success (path, content as JSON string)
            operation_failed: On error (operation, path, error)
        """
        operation_id = id(asyncio.current_task())
        self._running_operations.add(operation_id)

        try:
            logger.debug(f"Reading JSON file: {file_path}")
            data = await async_read_json(file_path, encoding)

            if data is not None:
                import json

                content_str = json.dumps(data)
                self.read_complete.emit(file_path, content_str)
                logger.info(f"JSON file read complete: {file_path}")
                return data
            else:
                error = "JSON read returned None"
                self.operation_failed.emit("read_json", file_path, error)
                logger.error(f"JSON file read failed: {file_path}")
                return None

        except Exception as e:
            error = str(e)
            self.operation_failed.emit("read_json", file_path, error)
            logger.error(f"JSON file read error: {file_path}: {e}")
            return None

        finally:
            self._running_operations.discard(operation_id)

    async def write_json(
        self,
        file_path: Path,
        data: dict[str, Any],
        encoding: str = "utf-8",
        indent: int = 2,
    ) -> bool:
        """
        Write JSON file asynchronously with atomic save.

        Args:
            file_path: Path to file
            data: Dictionary to serialize as JSON
            encoding: Text encoding (default: utf-8)
            indent: JSON indentation (default: 2)

        Returns:
            True if successful, False otherwise

        Emits:
            write_complete: On success (path)
            operation_failed: On error (operation, path, error)
        """
        operation_id = id(asyncio.current_task())
        self._running_operations.add(operation_id)

        try:
            logger.debug(f"Writing JSON file: {file_path}")
            success = await async_atomic_save_json(file_path, data, encoding, indent)

            if success:
                self.write_complete.emit(file_path)
                logger.info(f"JSON file write complete: {file_path}")
                return True
            else:
                error = "Atomic JSON save returned False"
                self.operation_failed.emit("write_json", file_path, error)
                logger.error(f"JSON file write failed: {file_path}")
                return False

        except Exception as e:
            error = str(e)
            self.operation_failed.emit("write_json", file_path, error)
            logger.error(f"JSON file write error: {file_path}: {e}")
            return False

        finally:
            self._running_operations.discard(operation_id)

    async def copy_file(self, src: Path, dst: Path, chunk_size: int = 65536) -> bool:
        """
        Copy file asynchronously.

        Args:
            src: Source file path
            dst: Destination file path
            chunk_size: Bytes per chunk (default: 64KB)

        Returns:
            True if successful, False otherwise

        Emits:
            write_complete: On success (dst path)
            operation_failed: On error (operation, path, error)
        """
        operation_id = id(asyncio.current_task())
        self._running_operations.add(operation_id)

        try:
            logger.debug(f"Copying file: {src} → {dst}")
            success = await async_copy_file(src, dst, chunk_size)

            if success:
                self.write_complete.emit(dst)
                logger.info(f"File copy complete: {src} → {dst}")
                return True
            else:
                error = "Copy returned False"
                self.operation_failed.emit("copy", dst, error)
                logger.error(f"File copy failed: {src} → {dst}")
                return False

        except Exception as e:
            error = str(e)
            self.operation_failed.emit("copy", dst, error)
            logger.error(f"File copy error: {src} → {dst}: {e}")
            return False

        finally:
            self._running_operations.discard(operation_id)

    def watch_file(self, file_path: Path, poll_interval: float = 1.0, debounce_period: float = 0.5) -> None:
        """
        Start watching file for external changes.

        Args:
            file_path: Path to file to watch
            poll_interval: How often to check file (seconds)
            debounce_period: Minimum time between notifications (seconds)
        """
        # Stop existing watcher if any
        if self._watcher:
            # Save reference to old watcher and clear member variable first
            # to avoid race condition in stop_watching()
            old_watcher = self._watcher
            self._watcher = None
            self._watched_file = None

            # Stop old watcher asynchronously
            async def _stop_old_watcher() -> None:
                await old_watcher.stop()

            asyncio.ensure_future(_stop_old_watcher())

        # Create new watcher
        self._watcher = AsyncFileWatcher(poll_interval, debounce_period)
        self._watcher.file_modified.connect(self._on_file_modified)
        self._watcher.file_deleted.connect(self._on_file_deleted)
        self._watcher.file_created.connect(self._on_file_created)
        self._watcher.error.connect(self._on_watcher_error)

        self._watcher.set_file(file_path)
        self._watched_file = file_path

        # Start watching
        asyncio.ensure_future(self._watcher.start())
        logger.info(f"Started watching file: {file_path}")

    async def stop_watching(self) -> None:
        """Stop watching current file."""
        if self._watcher:
            await self._watcher.stop()
            self._watcher = None
            self._watched_file = None
            logger.info("Stopped watching file")

    def _on_file_modified(self, path: Path) -> None:
        """Handle file modified event."""
        logger.info(f"File modified externally: {path}")
        self.file_changed_externally.emit(path)

    def _on_file_deleted(self, path: Path) -> None:
        """Handle file deleted event."""
        logger.warning(f"File deleted externally: {path}")
        self.file_changed_externally.emit(path)

    def _on_file_created(self, path: Path) -> None:
        """Handle file created event."""
        logger.info(f"File created externally: {path}")
        self.file_changed_externally.emit(path)

    def _on_watcher_error(self, error: str) -> None:
        """Handle file watcher error."""
        logger.error(f"File watcher error: {error}")
        if self._watched_file:
            self.operation_failed.emit("watch", self._watched_file, error)

    def is_watching(self) -> bool:
        """Check if currently watching a file."""
        return self._watcher is not None and self._watcher.is_running()

    def get_watched_file(self) -> Path | None:
        """Get currently watched file path."""
        return self._watched_file

    def has_running_operations(self) -> bool:
        """Check if any operations are currently running."""
        return len(self._running_operations) > 0

    async def cleanup(self) -> None:
        """Clean up resources."""
        # Stop file watcher
        if self._watcher:
            await self.stop_watching()

        # Wait for running operations to complete
        if self._running_operations:
            logger.info(f"Waiting for {len(self._running_operations)} operations to complete...")
            # Give operations a chance to complete
            await asyncio.sleep(0.5)

        logger.info("QtAsyncFileManager cleanup complete")
