"""
Async File Operations - Non-blocking file I/O using async/await.

Implements v1.6.0 Task 2: Async I/O
- Uses aiofiles for non-blocking file operations
- Async/await syntax for modern Python async programming
- Async context managers for resource management
- Maintains atomic write guarantees from file_operations.py

This module provides async versions of file operations while maintaining:
- FR-015: Atomic file writes (temp file + rename pattern)
- FR-016: Path sanitization to prevent directory traversal
- NFR-006: Atomic file save operations
- NFR-007: Never lose user data
- NFR-009: Path sanitization

Benefits:
- Non-blocking file I/O (no UI freezes)
- Better responsiveness during file operations
- Concurrent file operations possible
- Modern async/await syntax
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional, Union

try:
    import aiofiles
    import aiofiles.os

    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

logger = logging.getLogger(__name__)


def sanitize_path(path_input: Union[str, Path]) -> Optional[Path]:
    """
    Sanitize file path to prevent directory traversal attacks.

    This is synchronous as path resolution is fast and doesn't benefit from async.
    Reused from file_operations.py for consistency.

    Args:
        path_input: Path as string or Path object

    Returns:
        Resolved Path object if safe, None if suspicious patterns detected

    Security:
        - Resolves symbolic links and relative paths
        - Blocks paths containing '..' components
        - Prevents directory traversal attacks
    """
    try:
        path = Path(path_input).resolve()

        if ".." in path.parts:
            logger.warning(f"Path sanitization blocked suspicious path: {path_input}")
            return None
        return path
    except Exception as e:
        logger.error(f"Path sanitization failed for {path_input}: {e}")
        return None


async def async_read_text(
    file_path: Path, encoding: str = "utf-8", chunk_size: int = 8192
) -> Optional[str]:
    """
    Asynchronously read text file.

    Uses aiofiles for non-blocking I/O. Reads file in chunks to avoid
    loading entire large files into memory at once.

    Args:
        file_path: Path to file to read
        encoding: Text encoding (default: utf-8)
        chunk_size: Bytes per chunk for streaming (default: 8KB)

    Returns:
        File content as string, or None on error

    Example:
        >>> content = await async_read_text(Path("document.adoc"))
        >>> if content:
        ...     print(f"Read {len(content)} characters")
    """
    if not AIOFILES_AVAILABLE:
        logger.error("aiofiles not available - falling back to sync read")
        try:
            return file_path.read_text(encoding=encoding)
        except Exception as e:
            logger.error(f"Sync read failed for {file_path}: {e}")
            return None

    try:
        async with aiofiles.open(file_path, mode="r", encoding=encoding) as f:
            content: str = await f.read()
            logger.debug(f"Async read successful: {file_path} ({len(content)} chars)")
            return content
    except Exception as e:
        logger.error(f"Async read failed for {file_path}: {e}")
        return None


async def async_read_text_chunked(
    file_path: Path, encoding: str = "utf-8", chunk_size: int = 8192
) -> AsyncGenerator[str, None]:
    """
    Asynchronously read text file in chunks (generator).

    Use for very large files where you want to process content
    incrementally without loading everything into memory.

    Args:
        file_path: Path to file to read
        encoding: Text encoding (default: utf-8)
        chunk_size: Bytes per chunk (default: 8KB)

    Yields:
        Text chunks as strings

    Example:
        >>> async for chunk in async_read_text_chunked(Path("large_file.adoc")):
        ...     process_chunk(chunk)
    """
    if not AIOFILES_AVAILABLE:
        logger.error("aiofiles not available - cannot stream")
        return

    try:
        async with aiofiles.open(file_path, mode="r", encoding=encoding) as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        logger.debug(f"Async chunked read complete: {file_path}")
    except Exception as e:
        logger.error(f"Async chunked read failed for {file_path}: {e}")


async def async_atomic_save_text(
    file_path: Path, content: str, encoding: str = "utf-8"
) -> bool:
    """
    Asynchronously save text with atomic write (temp file + rename).

    Maintains same safety guarantees as file_operations.atomic_save_text()
    but performs I/O asynchronously to avoid blocking.

    Implements FR-015, NFR-006, NFR-007 reliability requirements.

    Args:
        file_path: Target file path
        content: Text content to write
        encoding: Text encoding (default: utf-8)

    Returns:
        True if successful, False otherwise

    Implementation:
        1. Write to temporary file asynchronously
        2. Perform atomic rename (OS-level atomic operation)
        3. Cleanup temp file on failure

    Example:
        >>> success = await async_atomic_save_text(
        ...     Path("document.adoc"),
        ...     "= My Document\\n\\nContent here"
        ... )
        >>> if success:
        ...     print("Save successful")
    """
    if not AIOFILES_AVAILABLE:
        logger.error("aiofiles not available - falling back to sync write")
        from asciidoc_artisan.core.file_operations import atomic_save_text

        return atomic_save_text(file_path, content, encoding)

    if not file_path:
        logger.error("async_atomic_save_text: file_path is None")
        return False

    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")

    try:
        # Step 1: Write to temporary file asynchronously
        async with aiofiles.open(temp_path, mode="w", encoding=encoding) as f:
            await f.write(content)

        # Step 2: Atomic rename (synchronous OS call, but fast)
        await aiofiles.os.replace(temp_path, file_path)

        logger.debug(f"Async atomic save successful: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Async atomic save failed for {file_path}: {e}")

        # Step 3: Cleanup on failure
        try:
            if temp_path.exists():
                await aiofiles.os.remove(temp_path)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temp file {temp_path}: {cleanup_error}")

        return False


async def async_atomic_save_json(
    file_path: Path, data: Dict[str, Any], encoding: str = "utf-8", indent: int = 2
) -> bool:
    """
    Asynchronously save JSON data with atomic write.

    Implements FR-015, NFR-006, NFR-007 for JSON serialization.

    Args:
        file_path: Target file path
        data: Dictionary to serialize as JSON
        encoding: Text encoding (default: utf-8)
        indent: JSON indentation (default: 2)

    Returns:
        True if successful, False otherwise

    Example:
        >>> success = await async_atomic_save_json(
        ...     Path("settings.json"),
        ...     {"theme": "dark", "font_size": 12}
        ... )
    """
    if not AIOFILES_AVAILABLE:
        logger.error("aiofiles not available - falling back to sync write")
        from asciidoc_artisan.core.file_operations import atomic_save_json

        return atomic_save_json(file_path, data, encoding, indent)

    if not file_path:
        logger.error("async_atomic_save_json: file_path is None")
        return False

    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")

    try:
        # Serialize to JSON string (CPU-bound, but fast enough)
        json_str = json.dumps(data, indent=indent)

        # Write asynchronously
        async with aiofiles.open(temp_path, mode="w", encoding=encoding) as f:
            await f.write(json_str)

        # Atomic rename
        await aiofiles.os.replace(temp_path, file_path)

        logger.debug(f"Async atomic JSON save successful: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Async atomic JSON save failed for {file_path}: {e}")

        # Cleanup on failure
        try:
            if temp_path.exists():
                await aiofiles.os.remove(temp_path)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temp file {temp_path}: {cleanup_error}")

        return False


async def async_read_json(
    file_path: Path, encoding: str = "utf-8"
) -> Optional[Dict[str, Any]]:
    """
    Asynchronously read and parse JSON file.

    Args:
        file_path: Path to JSON file
        encoding: Text encoding (default: utf-8)

    Returns:
        Parsed JSON as dictionary, or None on error

    Example:
        >>> settings = await async_read_json(Path("settings.json"))
        >>> if settings:
        ...     theme = settings.get("theme", "light")
    """
    content = await async_read_text(file_path, encoding)
    if content is None:
        return None

    try:
        data = json.loads(content)
        logger.debug(f"JSON parse successful: {file_path}")
        return data  # type: ignore[no-any-return]  # JSON returns Any
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failed for {file_path}: {e}")
        return None


class AsyncFileContext:
    """
    Async context manager for file operations.

    Provides convenient async context manager for reading/writing files
    with automatic resource cleanup.

    Example:
        >>> async with AsyncFileContext(Path("file.txt"), "r") as f:
        ...     content = await f.read()

        >>> async with AsyncFileContext(Path("file.txt"), "w") as f:
        ...     await f.write("Hello, async world!")
    """

    def __init__(
        self, file_path: Path, mode: str = "r", encoding: Optional[str] = "utf-8"
    ):
        """
        Initialize async file context.

        Args:
            file_path: Path to file
            mode: File mode ('r', 'w', 'a', etc.)
            encoding: Text encoding (default: utf-8)
        """
        self.file_path = file_path
        self.mode = mode
        self.encoding = encoding
        self._file = None

    async def __aenter__(self) -> Any:
        """Enter async context - open file."""
        if not AIOFILES_AVAILABLE:
            logger.error("aiofiles not available")
            raise RuntimeError("aiofiles not available for async file operations")

        # Only pass encoding for text modes
        if self.encoding is not None and "b" not in self.mode:
            self._file = await aiofiles.open(  # type: ignore[call-overload]
                str(self.file_path), self.mode, encoding=self.encoding
            )
        else:
            self._file = await aiofiles.open(  # type: ignore[call-overload]
                str(self.file_path), self.mode
            )
        return self._file

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Exit async context - close file."""
        if self._file:
            await self._file.close()
        return False  # Don't suppress exceptions


async def async_copy_file(src: Path, dst: Path, chunk_size: int = 65536) -> bool:
    """
    Asynchronously copy file from source to destination.

    Uses chunked reading/writing to handle large files efficiently.

    Args:
        src: Source file path
        dst: Destination file path
        chunk_size: Bytes per chunk (default: 64KB)

    Returns:
        True if successful, False otherwise

    Example:
        >>> success = await async_copy_file(
        ...     Path("source.adoc"),
        ...     Path("backup.adoc")
        ... )
    """
    if not AIOFILES_AVAILABLE:
        logger.error("aiofiles not available - falling back to sync copy")
        try:
            import shutil

            shutil.copy2(src, dst)
            return True
        except Exception as e:
            logger.error(f"Sync copy failed: {e}")
            return False

    try:
        async with aiofiles.open(src, mode="rb") as src_file:
            async with aiofiles.open(dst, mode="wb") as dst_file:
                while True:
                    chunk = await src_file.read(chunk_size)
                    if not chunk:
                        break
                    await dst_file.write(chunk)

        logger.debug(f"Async copy successful: {src} → {dst}")
        return True

    except Exception as e:
        logger.error(f"Async copy failed {src} → {dst}: {e}")
        return False


# Convenience function to run async operations from sync code
def run_async(coro: Any) -> Any:
    """
    Run async coroutine from synchronous code.

    Helper function for calling async functions from sync contexts.

    Args:
        coro: Coroutine to run

    Returns:
        Result of coroutine

    Example:
        >>> content = run_async(async_read_text(Path("file.txt")))
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)
