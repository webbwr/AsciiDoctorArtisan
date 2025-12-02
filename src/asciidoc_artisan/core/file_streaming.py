"""
File Streaming Module - Streaming file operations for large files.

MA principle: Extracted from async_file_handler.py for focused responsibility.

Implements:
- NFR-003: Large file handling (>10MB with streaming)
- NFR-004: Memory usage optimization (chunked I/O)

This module provides streaming file I/O:
- FileStreamReader: Read large files in chunks
- FileStreamWriter: Write large files in chunks
- BatchFileOperations: Process multiple files in parallel

Features:
- Memory efficient (no full file load)
- Chunked I/O for large files
- Parallel batch processing
"""

import logging
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FileOperationResult:
    """
    Result of file operation.

    Uses __slots__ for memory efficiency.
    """

    success: bool
    path: str
    error: str | None = None
    data: str | None = None
    bytes_processed: int = 0


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
        self._file: TextIO | None = None

    def __enter__(self) -> "FileStreamReader":
        """Context manager entry."""
        self._file = open(self.file_path, encoding="utf-8")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if self._file:
            self._file.close()

    def read_chunks(self) -> Generator[str]:
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
        self._file: TextIO | None = None
        self.bytes_written = 0

    def __enter__(self) -> "FileStreamWriter":
        """Context manager entry."""
        # Create parent directories
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        self._file = open(self.file_path, "w", encoding="utf-8")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
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

    def read_files(self, file_paths: list[str]) -> list[FileOperationResult]:
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
            future_to_path = {executor.submit(self._read_one, path): path for path in file_paths}

            # Collect results as they complete
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    logger.error(f"Batch read failed for {path}: {exc}")
                    results.append(FileOperationResult(success=False, path=path, error=str(exc)))

        logger.info(f"Batch read complete: {len(results)} files")
        return results

    def write_files(self, file_data: list[tuple[str, str]]) -> list[FileOperationResult]:
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
            future_to_path = {executor.submit(self._write_one, path, content): path for path, content in file_data}

            # Collect results as they complete
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    logger.error(f"Batch write failed for {path}: {exc}")
                    results.append(FileOperationResult(success=False, path=path, error=str(exc)))

        logger.info(f"Batch write complete: {len(results)} files")
        return results

    @staticmethod
    def _read_one(path: str) -> FileOperationResult:
        """Read single file."""
        try:
            file_path = Path(path)
            content = file_path.read_text(encoding="utf-8")
            return FileOperationResult(success=True, path=path, data=content, bytes_processed=len(content))
        except Exception as exc:
            return FileOperationResult(success=False, path=path, error=str(exc))

    @staticmethod
    def _write_one(path: str, content: str) -> FileOperationResult:
        """Write single file."""
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            return FileOperationResult(success=True, path=path, bytes_processed=len(content))
        except Exception as exc:
            return FileOperationResult(success=False, path=path, error=str(exc))
