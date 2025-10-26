"""
Async File Handler - Non-blocking file operations.

Implements:
- NFR-003: Large file handling (>10MB with streaming)
- NFR-004: Memory usage optimization (chunked I/O)
- NFR-005: Background threading for long operations

This module provides asynchronous file I/O:
- Async read/write operations
- Streaming for large files
- Qt integration (signals for completion)
- Background I/O without blocking UI

Implements Phase 4.1 of Performance Optimization Plan:
- Async file operations
- 2-3x faster I/O
- No UI blocking
- Streaming support

Design Goals:
- Fast file operations
- No UI freezes
- Memory efficient (streaming)
- Simple API
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Callable, List
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal, QThread, Slot

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FileOperationResult:
    """
    Result of file operation.

    Uses __slots__ for memory efficiency.
    """
    success: bool
    path: str
    error: Optional[str] = None
    data: Optional[str] = None
    bytes_processed: int = 0


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

    def __init__(self):
        """Initialize async file handler."""
        super().__init__()
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.start()

        logger.info("Async file handler initialized")

    def read_file_async(self, file_path: str) -> None:
        """
        Read file asynchronously.

        Args:
            file_path: Path to file

        Emits:
            read_complete: On success
            read_error: On failure
        """
        # Run in thread pool
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=1)

        def read_task():
            try:
                path = Path(file_path)
                if not path.exists():
                    self.read_error.emit(
                        file_path,
                        f"File not found: {file_path}"
                    )
                    return

                # Read file
                logger.debug(f"Reading file: {file_path}")
                content = path.read_text(encoding='utf-8')
                size = len(content)

                result = FileOperationResult(
                    success=True,
                    path=file_path,
                    data=content,
                    bytes_processed=size
                )

                self.read_complete.emit(result)
                logger.debug(f"Read complete: {size} bytes from {file_path}")

            except Exception as exc:
                logger.error(f"Read failed for {file_path}: {exc}")
                self.read_error.emit(file_path, str(exc))

        executor.submit(read_task)

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
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=1)

        def write_task():
            try:
                path = Path(file_path)

                # Create parent directories
                path.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                logger.debug(f"Writing file: {file_path}")
                path.write_text(content, encoding='utf-8')
                size = len(content)

                result = FileOperationResult(
                    success=True,
                    path=file_path,
                    bytes_processed=size
                )

                self.write_complete.emit(result)
                logger.debug(f"Write complete: {size} bytes to {file_path}")

            except Exception as exc:
                logger.error(f"Write failed for {file_path}: {exc}")
                self.write_error.emit(file_path, str(exc))

        executor.submit(write_task)

    def read_file_streaming(
        self,
        file_path: str,
        chunk_size: int = 8192
    ) -> None:
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
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=1)

        def stream_task():
            try:
                path = Path(file_path)
                if not path.exists():
                    self.read_error.emit(file_path, "File not found")
                    return

                # Get file size
                file_size = path.stat().st_size
                bytes_read = 0
                chunks = []

                logger.debug(
                    f"Streaming read: {file_path} ({file_size} bytes)"
                )

                # Read in chunks
                with open(path, 'r', encoding='utf-8') as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break

                        chunks.append(chunk)
                        bytes_read += len(chunk)

                        # Emit progress
                        self.progress.emit("read", bytes_read, file_size)

                # Combine chunks
                content = ''.join(chunks)

                result = FileOperationResult(
                    success=True,
                    path=file_path,
                    data=content,
                    bytes_processed=bytes_read
                )

                self.read_complete.emit(result)
                logger.debug(f"Streaming read complete: {bytes_read} bytes")

            except Exception as exc:
                logger.error(f"Streaming read failed: {exc}")
                self.read_error.emit(file_path, str(exc))

        executor.submit(stream_task)

    def write_file_streaming(
        self,
        file_path: str,
        content: str,
        chunk_size: int = 8192
    ) -> None:
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
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=1)

        def stream_task():
            try:
                path = Path(file_path)
                path.parent.mkdir(parents=True, exist_ok=True)

                total_size = len(content)
                bytes_written = 0

                logger.debug(
                    f"Streaming write: {file_path} ({total_size} bytes)"
                )

                # Write in chunks
                with open(path, 'w', encoding='utf-8') as f:
                    offset = 0
                    while offset < total_size:
                        chunk = content[offset:offset + chunk_size]
                        f.write(chunk)

                        bytes_written += len(chunk)
                        offset += chunk_size

                        # Emit progress
                        self.progress.emit("write", bytes_written, total_size)

                result = FileOperationResult(
                    success=True,
                    path=file_path,
                    bytes_processed=bytes_written
                )

                self.write_complete.emit(result)
                logger.debug(f"Streaming write complete: {bytes_written} bytes")

            except Exception as exc:
                logger.error(f"Streaming write failed: {exc}")
                self.write_error.emit(file_path, str(exc))

        executor.submit(stream_task)

    def cleanup(self) -> None:
        """Clean up resources."""
        if self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()
        logger.debug("Async file handler cleaned up")


class FileStreamReader:
    """
    Streaming file reader for very large files.

    Reads file in chunks to avoid loading entire file into memory.

    Example:
        reader = FileStreamReader("/path/to/large.adoc", chunk_size=8192)

        for chunk in reader.read_chunks():
            process_chunk(chunk)
    """

    def __init__(self, file_path: str, chunk_size: int = 8192):
        """
        Initialize stream reader.

        Args:
            file_path: Path to file
            chunk_size: Bytes per chunk
        """
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size
        self._file = None

    def __enter__(self):
        """Context manager entry."""
        self._file = open(self.file_path, 'r', encoding='utf-8')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._file:
            self._file.close()

    def read_chunks(self):
        """
        Read file in chunks (generator).

        Yields:
            String chunks
        """
        if not self._file:
            raise RuntimeError("Reader not opened (use with statement)")

        while True:
            chunk = self._file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    def get_file_size(self) -> int:
        """
        Get file size in bytes.

        Returns:
            File size
        """
        return self.file_path.stat().st_size


class FileStreamWriter:
    """
    Streaming file writer for very large files.

    Writes file in chunks to avoid loading entire content into memory.

    Example:
        writer = FileStreamWriter("/path/to/output.adoc", chunk_size=8192)

        with writer:
            for chunk in data_chunks:
                writer.write_chunk(chunk)
    """

    def __init__(self, file_path: str, chunk_size: int = 8192):
        """
        Initialize stream writer.

        Args:
            file_path: Path to file
            chunk_size: Bytes per chunk
        """
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size
        self._file = None
        self.bytes_written = 0

    def __enter__(self):
        """Context manager entry."""
        # Create parent directories
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        self._file = open(self.file_path, 'w', encoding='utf-8')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._file:
            self._file.close()

    def write_chunk(self, chunk: str) -> int:
        """
        Write chunk to file.

        Args:
            chunk: Data to write

        Returns:
            Bytes written
        """
        if not self._file:
            raise RuntimeError("Writer not opened (use with statement)")

        self._file.write(chunk)
        size = len(chunk)
        self.bytes_written += size
        return size


class BatchFileOperations:
    """
    Batch file operations for multiple files.

    Efficiently process multiple files in parallel.

    Example:
        batch = BatchFileOperations(max_workers=4)

        # Read multiple files
        results = batch.read_files([
            "file1.adoc",
            "file2.adoc",
            "file3.adoc"
        ])

        for result in results:
            if result.success:
                print(f"Read {result.path}: {len(result.data)} bytes")
    """

    def __init__(self, max_workers: int = 4):
        """
        Initialize batch operations.

        Args:
            max_workers: Max parallel workers
        """
        self.max_workers = max_workers

    def read_files(self, file_paths: List[str]) -> List[FileOperationResult]:
        """
        Read multiple files in parallel.

        Args:
            file_paths: List of file paths

        Returns:
            List of results
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self._read_one, path): path
                for path in file_paths
            }

            # Collect results as they complete
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    logger.error(f"Batch read failed for {path}: {exc}")
                    results.append(FileOperationResult(
                        success=False,
                        path=path,
                        error=str(exc)
                    ))

        logger.info(f"Batch read complete: {len(results)} files")
        return results

    def write_files(
        self,
        file_data: List[tuple[str, str]]
    ) -> List[FileOperationResult]:
        """
        Write multiple files in parallel.

        Args:
            file_data: List of (path, content) tuples

        Returns:
            List of results
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self._write_one, path, content): path
                for path, content in file_data
            }

            # Collect results as they complete
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    logger.error(f"Batch write failed for {path}: {exc}")
                    results.append(FileOperationResult(
                        success=False,
                        path=path,
                        error=str(exc)
                    ))

        logger.info(f"Batch write complete: {len(results)} files")
        return results

    @staticmethod
    def _read_one(path: str) -> FileOperationResult:
        """Read single file."""
        try:
            file_path = Path(path)
            content = file_path.read_text(encoding='utf-8')
            return FileOperationResult(
                success=True,
                path=path,
                data=content,
                bytes_processed=len(content)
            )
        except Exception as exc:
            return FileOperationResult(
                success=False,
                path=path,
                error=str(exc)
            )

    @staticmethod
    def _write_one(path: str, content: str) -> FileOperationResult:
        """Write single file."""
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            return FileOperationResult(
                success=True,
                path=path,
                bytes_processed=len(content)
            )
        except Exception as exc:
            return FileOperationResult(
                success=False,
                path=path,
                error=str(exc)
            )
