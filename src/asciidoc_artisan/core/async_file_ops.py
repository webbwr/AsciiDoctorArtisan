"""Async File Operations - Non-blocking file I/O using async/await."""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

try:
    import aiofiles
    import aiofiles.os

    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

logger = logging.getLogger(__name__)


def sanitize_path(path_input: str | Path) -> Path | None:
    """Sanitize file path to prevent directory traversal attacks."""
    try:
        path = Path(path_input).resolve()
        if ".." in path.parts:
            logger.warning(f"Path sanitization blocked suspicious path: {path_input}")
            return None
        return path
    except Exception as e:
        logger.error(f"Path sanitization failed for {path_input}: {e}")
        return None


async def async_read_text(file_path: Path, encoding: str = "utf-8", chunk_size: int = 8192) -> str | None:
    """Asynchronously read text file. Returns content or None on error."""
    if not AIOFILES_AVAILABLE:
        logger.error("aiofiles not available - falling back to sync read")
        try:
            return file_path.read_text(encoding=encoding)
        except Exception as e:
            logger.error(f"Sync read failed for {file_path}: {e}")
            return None

    try:
        async with aiofiles.open(file_path, encoding=encoding) as f:
            content: str = await f.read()
            logger.debug(f"Async read successful: {file_path} ({len(content)} chars)")
            return content
    except Exception as e:
        logger.error(f"Async read failed for {file_path}: {e}")
        return None


async def async_read_text_chunked(
    file_path: Path, encoding: str = "utf-8", chunk_size: int = 8192
) -> AsyncGenerator[str]:
    """Asynchronously read text file in chunks (generator)."""
    if not AIOFILES_AVAILABLE:
        logger.error("aiofiles not available - cannot stream")
        return

    try:
        async with aiofiles.open(file_path, encoding=encoding) as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        logger.debug(f"Async chunked read complete: {file_path}")
    except Exception as e:
        logger.error(f"Async chunked read failed for {file_path}: {e}")


async def async_atomic_save_text(file_path: Path, content: str, encoding: str = "utf-8") -> bool:
    """Asynchronously save text with atomic write (temp file + rename)."""
    if not AIOFILES_AVAILABLE:
        logger.error("aiofiles not available - falling back to sync write")
        from asciidoc_artisan.core.file_operations import atomic_save_text

        return atomic_save_text(file_path, content, encoding)

    if not file_path:
        logger.error("async_atomic_save_text: file_path is None")
        return False

    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")

    try:
        async with aiofiles.open(temp_path, mode="w", encoding=encoding) as f:
            await f.write(content)
        await aiofiles.os.replace(temp_path, file_path)
        logger.debug(f"Async atomic save successful: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Async atomic save failed for {file_path}: {e}")
        try:
            if temp_path.exists():
                await aiofiles.os.remove(temp_path)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temp file {temp_path}: {cleanup_error}")
        return False


async def async_atomic_save_json(
    file_path: Path, data: dict[str, Any], encoding: str = "utf-8", indent: int = 2
) -> bool:
    """Asynchronously save JSON data with atomic write."""
    if not AIOFILES_AVAILABLE:
        logger.error("aiofiles not available - falling back to sync write")
        from asciidoc_artisan.core.file_operations import atomic_save_json

        return atomic_save_json(file_path, data, encoding, indent)

    if not file_path:
        logger.error("async_atomic_save_json: file_path is None")
        return False

    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")

    try:
        json_str = json.dumps(data, indent=indent)
        async with aiofiles.open(temp_path, mode="w", encoding=encoding) as f:
            await f.write(json_str)
        await aiofiles.os.replace(temp_path, file_path)
        logger.debug(f"Async atomic JSON save successful: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Async atomic JSON save failed for {file_path}: {e}")
        try:
            if temp_path.exists():
                await aiofiles.os.remove(temp_path)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temp file {temp_path}: {cleanup_error}")
        return False


async def async_read_json(file_path: Path, encoding: str = "utf-8") -> dict[str, Any] | None:
    """Asynchronously read and parse JSON file."""
    content = await async_read_text(file_path, encoding)
    if content is None:
        return None

    try:
        data = json.loads(content)
        logger.debug(f"JSON parse successful: {file_path}")
        return data  # type: ignore[no-any-return]
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failed for {file_path}: {e}")
        return None


class AsyncFileContext:
    """Async context manager for file operations."""

    def __init__(self, file_path: Path, mode: str = "r", encoding: str | None = "utf-8"):
        """Initialize async file context."""
        self.file_path = file_path
        self.mode = mode
        self.encoding = encoding
        self._file = None

    async def __aenter__(self) -> Any:
        """Enter async context - open file."""
        if not AIOFILES_AVAILABLE:
            raise RuntimeError("aiofiles not available for async file operations")

        if self.encoding is not None and "b" not in self.mode:
            self._file = await aiofiles.open(  # type: ignore[call-overload]
                str(self.file_path), self.mode, encoding=self.encoding
            )
        else:
            self._file = await aiofiles.open(str(self.file_path), self.mode)  # type: ignore[call-overload]
        return self._file

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Exit async context - close file."""
        if self._file:
            await self._file.close()
        return False


async def async_copy_file(src: Path, dst: Path, chunk_size: int = 65536) -> bool:
    """Asynchronously copy file from source to destination."""
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


def run_async(coro: Any) -> Any:
    """Run async coroutine from synchronous code."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)
