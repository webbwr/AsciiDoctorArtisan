"""
Async File Handler - Non-blocking file operations.

MA principle: Reduced from 529→185 lines by extracting file_streaming.py.

Implements:
- NFR-003: Large file handling (>10MB with streaming)
- NFR-004: Memory usage optimization (chunked I/O)
- NFR-005: Background threading for long operations

This module provides asynchronous file I/O:
- Async read/write operations
- Streaming for large files
- Qt integration (signals for completion)
- Background I/O without blocking UI

Design Goals:
- Fast file operations
- No UI freezes
- Memory efficient (streaming)
- Simple API
"""

import logging
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from asciidoc_artisan.core.file_streaming import (
    BatchFileOperations,
    FileOperationResult,
    FileStreamReader,
    FileStreamWriter,
)

logger = logging.getLogger(__name__)

# Re-export for backward compatibility
__all__ = [
    "FileOperationResult",
    "AsyncFileHandler",
    "FileStreamReader",
    "FileStreamWriter",
    "BatchFileOperations",
]


class AsyncFileHandler(QObject):
    """
    Async file handler with Qt integration.

    Performs file I/O in background without blocking UI.

    Features:
    - Async read/write
    - Large file streaming
    - Progress signals
    - Error handling

    Example:
        handler = AsyncFileHandler()

        # Connect signals
        handler.read_complete.connect(on_read_done)
        handler.read_error.connect(on_error)

        # Read file async
        handler.read_file_async("/path/to/file.adoc")

        # Write file async
        handler.write_file_async("/path/to/output.adoc", content)
    """

    # Signals
    read_complete = Signal(FileOperationResult)
    write_complete = Signal(FileOperationResult)
    read_error = Signal(str, str)  # path, error
    write_error = Signal(str, str)  # path, error
    progress = Signal(str, int, int)  # operation, current, total

    def __init__(self, max_workers: int = 4) -> None:
        """
        Initialize async file handler with persistent thread pool.

        Args:
            max_workers: Maximum number of worker threads (default: 4)
        """
        super().__init__()
        # ThreadPoolExecutor handles threading - no need for QThread
        # Signals can be emitted from worker threads safely

        # Persistent thread pool for efficient async I/O
        from concurrent.futures import ThreadPoolExecutor

        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        logger.info(f"Async file handler initialized with {max_workers} worker threads")

    def read_file_async(self, file_path: str) -> None:
        """
        Read file asynchronously.

        Args:
            file_path: Path to file

        Emits:
            read_complete: On success
            read_error: On failure
        """

        # Run in thread pool using persistent executor
        def read_task() -> None:
            try:
                path = Path(file_path)
                if not path.exists():
                    self.read_error.emit(file_path, f"File not found: {file_path}")
                    return

                # Read file
                logger.debug(f"Reading file: {file_path}")
                content = path.read_text(encoding="utf-8")
                size = len(content)

                result = FileOperationResult(success=True, path=file_path, data=content, bytes_processed=size)

                self.read_complete.emit(result)
                logger.debug(f"Read complete: {size} bytes from {file_path}")

            except Exception as exc:
                logger.error(f"Read failed for {file_path}: {exc}")
                self.read_error.emit(file_path, str(exc))

        self._executor.submit(read_task)

    def write_file_async(self, file_path: str, content: str) -> None:
        """
        Write file asynchronously.

        Args:
            file_path: Path to file
            content: Content to write

        Emits:
            write_complete: On success
            write_error: On failure
        """

        def write_task() -> None:
            try:
                path = Path(file_path)

                # Create parent directories
                path.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                logger.debug(f"Writing file: {file_path}")
                path.write_text(content, encoding="utf-8")
                size = len(content)

                result = FileOperationResult(success=True, path=file_path, bytes_processed=size)

                self.write_complete.emit(result)
                logger.debug(f"Write complete: {size} bytes to {file_path}")

            except Exception as exc:
                logger.error(f"Write failed for {file_path}: {exc}")
                self.write_error.emit(file_path, str(exc))

        self._executor.submit(write_task)

    def read_file_streaming(self, file_path: str, chunk_size: int = 8192) -> None:
        """
        Read large file in chunks (streaming).

        Args:
            file_path: Path to file
            chunk_size: Bytes per chunk

        Emits:
            progress: For each chunk
            read_complete: When done
            read_error: On failure
        """

        def stream_task() -> None:
            try:
                path = Path(file_path)
                if not path.exists():
                    self.read_error.emit(file_path, "File not found")
                    return

                # Get file size
                file_size = path.stat().st_size
                bytes_read = 0
                chunks = []

                logger.debug(f"Streaming read: {file_path} ({file_size} bytes)")

                # Read in chunks
                with open(path, encoding="utf-8") as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break

                        chunks.append(chunk)
                        bytes_read += len(chunk)

                        # Emit progress
                        self.progress.emit("read", bytes_read, file_size)

                # Combine chunks
                content = "".join(chunks)

                result = FileOperationResult(
                    success=True,
                    path=file_path,
                    data=content,
                    bytes_processed=bytes_read,
                )

                self.read_complete.emit(result)
                logger.debug(f"Streaming read complete: {bytes_read} bytes")

            except Exception as exc:
                logger.error(f"Streaming read failed: {exc}")
                self.read_error.emit(file_path, str(exc))

        self._executor.submit(stream_task)

    def write_file_streaming(self, file_path: str, content: str, chunk_size: int = 8192) -> None:
        """
        Write large file in chunks (streaming).

        Args:
            file_path: Path to file
            content: Content to write
            chunk_size: Bytes per chunk

        Emits:
            progress: For each chunk
            write_complete: When done
            write_error: On failure
        """

        def stream_task() -> None:
            try:
                path = Path(file_path)
                path.parent.mkdir(parents=True, exist_ok=True)

                total_size = len(content)
                bytes_written = 0

                logger.debug(f"Streaming write: {file_path} ({total_size} bytes)")

                # Write in chunks
                with open(path, "w", encoding="utf-8") as f:
                    offset = 0
                    while offset < total_size:
                        chunk = content[offset : offset + chunk_size]
                        f.write(chunk)

                        bytes_written += len(chunk)
                        offset += chunk_size

                        # Emit progress
                        self.progress.emit("write", bytes_written, total_size)

                result = FileOperationResult(success=True, path=file_path, bytes_processed=bytes_written)

                self.write_complete.emit(result)
                logger.debug(f"Streaming write complete: {bytes_written} bytes")

            except Exception as exc:
                logger.error(f"Streaming write failed: {exc}")
                self.write_error.emit(file_path, str(exc))

        self._executor.submit(stream_task)

    def cleanup(self) -> None:
        """Clean up resources and shutdown thread pool."""
        logger.info("Cleaning up async file handler resources")

        # Shutdown thread pool (wait for completion)
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=True)
            logger.debug("Thread pool shutdown complete")

        logger.info("Async file handler cleanup complete")
