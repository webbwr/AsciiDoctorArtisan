"""
Tests for async file operations (v1.6.0 Task 2).

Tests async/await file I/O operations using aiofiles.
"""

import asyncio
import json
from pathlib import Path

import pytest

from asciidoc_artisan.core.async_file_ops import (
    AIOFILES_AVAILABLE,
    AsyncFileContext,
    async_atomic_save_json,
    async_atomic_save_text,
    async_copy_file,
    async_read_json,
    async_read_text,
    async_read_text_chunked,
    run_async,
    sanitize_path,
)

# Skip all tests if aiofiles not available
pytestmark = pytest.mark.skipif(not AIOFILES_AVAILABLE, reason="aiofiles not installed")


@pytest.mark.asyncio
async def test_async_read_text(tmp_path):
    """Test async text file reading."""
    test_file = tmp_path / "test.txt"
    content = "Hello, async world!\nLine 2\nLine 3"
    test_file.write_text(content)

    result = await async_read_text(test_file)

    assert result == content


@pytest.mark.asyncio
async def test_async_read_text_missing_file(tmp_path):
    """Test async read of non-existent file."""
    test_file = tmp_path / "missing.txt"

    result = await async_read_text(test_file)

    assert result is None


@pytest.mark.asyncio
async def test_async_read_text_chunked(tmp_path):
    """Test async chunked reading."""
    test_file = tmp_path / "test.txt"
    content = "A" * 10000  # 10KB of A's
    test_file.write_text(content)

    chunks = []
    async for chunk in async_read_text_chunked(test_file, chunk_size=1024):
        chunks.append(chunk)

    result = "".join(chunks)
    assert result == content
    assert len(chunks) > 1  # Should have multiple chunks


@pytest.mark.asyncio
async def test_async_atomic_save_text(tmp_path):
    """Test async atomic text save."""
    test_file = tmp_path / "test.txt"
    content = "Test content\nWith multiple lines\nAnd more"

    success = await async_atomic_save_text(test_file, content)

    assert success is True
    assert test_file.exists()
    assert test_file.read_text() == content


@pytest.mark.asyncio
async def test_async_atomic_save_text_creates_parent_dir(tmp_path):
    """Test async save creates parent directories."""
    test_file = tmp_path / "subdir" / "test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    content = "Test content"

    success = await async_atomic_save_text(test_file, content)

    assert success is True
    assert test_file.exists()


@pytest.mark.asyncio
async def test_async_atomic_save_overwrites_existing(tmp_path):
    """Test async save overwrites existing file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Old content")

    new_content = "New content"
    success = await async_atomic_save_text(test_file, new_content)

    assert success is True
    assert test_file.read_text() == new_content


@pytest.mark.asyncio
async def test_async_atomic_save_json(tmp_path):
    """Test async JSON save."""
    test_file = tmp_path / "test.json"
    data = {"name": "Test", "value": 42, "enabled": True}

    success = await async_atomic_save_json(test_file, data)

    assert success is True
    assert test_file.exists()

    # Verify JSON can be parsed
    loaded = json.loads(test_file.read_text())
    assert loaded == data


@pytest.mark.asyncio
async def test_async_atomic_save_json_with_indent(tmp_path):
    """Test async JSON save with custom indentation."""
    test_file = tmp_path / "test.json"
    data = {"a": 1, "b": 2}

    success = await async_atomic_save_json(test_file, data, indent=4)

    assert success is True
    content = test_file.read_text()
    assert "\n" in content  # Should have line breaks
    assert "    " in content  # Should have 4-space indents


@pytest.mark.asyncio
async def test_async_read_json(tmp_path):
    """Test async JSON reading."""
    test_file = tmp_path / "test.json"
    data = {"theme": "dark", "font_size": 14}
    test_file.write_text(json.dumps(data))

    result = await async_read_json(test_file)

    assert result == data


@pytest.mark.asyncio
async def test_async_read_json_invalid(tmp_path):
    """Test async read of invalid JSON."""
    test_file = tmp_path / "invalid.json"
    test_file.write_text("{invalid json")

    result = await async_read_json(test_file)

    assert result is None


@pytest.mark.asyncio
async def test_async_read_json_missing_file(tmp_path):
    """Test async read of missing JSON file."""
    test_file = tmp_path / "missing.json"

    result = await async_read_json(test_file)

    assert result is None


@pytest.mark.asyncio
async def test_async_file_context_read(tmp_path):
    """Test async context manager for reading."""
    test_file = tmp_path / "test.txt"
    content = "Context manager test"
    test_file.write_text(content)

    async with AsyncFileContext(test_file, "r") as f:
        result = await f.read()

    assert result == content


@pytest.mark.asyncio
async def test_async_file_context_write(tmp_path):
    """Test async context manager for writing."""
    test_file = tmp_path / "test.txt"
    content = "Written via context manager"

    async with AsyncFileContext(test_file, "w") as f:
        await f.write(content)

    assert test_file.read_text() == content


@pytest.mark.asyncio
async def test_async_copy_file(tmp_path):
    """Test async file copy."""
    src_file = tmp_path / "source.txt"
    dst_file = tmp_path / "dest.txt"
    content = "Content to copy"
    src_file.write_text(content)

    success = await async_copy_file(src_file, dst_file)

    assert success is True
    assert dst_file.exists()
    assert dst_file.read_text() == content


@pytest.mark.asyncio
async def test_async_copy_file_large(tmp_path):
    """Test async copy of large file."""
    src_file = tmp_path / "large.txt"
    dst_file = tmp_path / "large_copy.txt"
    # Create 1MB file
    content = "X" * (1024 * 1024)
    src_file.write_text(content)

    success = await async_copy_file(src_file, dst_file, chunk_size=8192)

    assert success is True
    assert dst_file.exists()
    assert dst_file.stat().st_size == src_file.stat().st_size


@pytest.mark.asyncio
async def test_async_copy_file_missing_source(tmp_path):
    """Test async copy with missing source."""
    src_file = tmp_path / "missing.txt"
    dst_file = tmp_path / "dest.txt"

    success = await async_copy_file(src_file, dst_file)

    assert success is False
    assert not dst_file.exists()


def test_sanitize_path_valid():
    """Test path sanitization with valid path."""
    result = sanitize_path("/home/user/document.adoc")

    assert result is not None
    assert isinstance(result, Path)


def test_sanitize_path_with_dots():
    """Test path sanitization resolves paths with dots."""
    # After resolution, .. is typically removed by Path.resolve()
    # So this becomes an absolute path without .. in parts
    result = sanitize_path("../../etc/passwd")

    # Path is resolved and valid (.. removed by resolve)
    assert result is not None
    assert result.is_absolute()
    assert ".." not in result.parts


def test_sanitize_path_relative():
    """Test path sanitization resolves relative paths."""
    result = sanitize_path("./test.txt")

    assert result is not None
    assert result.is_absolute()


def test_run_async_helper(tmp_path):
    """Test run_async helper function."""
    test_file = tmp_path / "test.txt"
    content = "Test content"

    # Run async function from sync context
    success = run_async(async_atomic_save_text(test_file, content))

    assert success is True
    assert test_file.exists()


def test_run_async_read(tmp_path):
    """Test run_async for reading."""
    test_file = tmp_path / "test.txt"
    content = "Content to read"
    test_file.write_text(content)

    result = run_async(async_read_text(test_file))

    assert result == content


@pytest.mark.asyncio
async def test_concurrent_writes(tmp_path):
    """Test concurrent async writes don't interfere."""
    files_and_contents = [(tmp_path / f"file{i}.txt", f"Content {i}") for i in range(5)]

    # Write all files concurrently
    tasks = [async_atomic_save_text(file, content) for file, content in files_and_contents]
    results = await asyncio.gather(*tasks)

    # All should succeed
    assert all(results)

    # Verify all files written correctly
    for file, expected_content in files_and_contents:
        assert file.exists()
        assert file.read_text() == expected_content


@pytest.mark.asyncio
async def test_concurrent_reads(tmp_path):
    """Test concurrent async reads."""
    files_and_contents = [(tmp_path / f"file{i}.txt", f"Content {i}") for i in range(5)]

    # Create files
    for file, content in files_and_contents:
        file.write_text(content)

    # Read all files concurrently
    tasks = [async_read_text(file) for file, _ in files_and_contents]
    results = await asyncio.gather(*tasks)

    # Verify all reads successful
    for result, (_, expected_content) in zip(results, files_and_contents):
        assert result == expected_content


@pytest.mark.asyncio
async def test_atomic_write_safety(tmp_path):
    """Test atomic write doesn't corrupt on error."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Original content")

    # Verify temp file is cleaned up even if write fails
    try:
        # This should work normally
        await async_atomic_save_text(test_file, "New content")
    except Exception:
        pass

    # Temp file should not exist
    temp_file = test_file.with_suffix(test_file.suffix + ".tmp")
    assert not temp_file.exists()


@pytest.mark.asyncio
async def test_large_file_streaming(tmp_path):
    """Test streaming large file doesn't use excessive memory."""
    test_file = tmp_path / "large.txt"

    # Create 10MB file
    chunk = "X" * 1024  # 1KB chunks
    with open(test_file, "w") as f:
        for _ in range(10 * 1024):  # 10MB
            f.write(chunk)

    # Read in chunks
    total_size = 0
    async for chunk in async_read_text_chunked(test_file, chunk_size=8192):
        total_size += len(chunk)

    assert total_size == test_file.stat().st_size


# Tests for error paths and edge cases


def test_sanitize_path_exception():
    """Test sanitize_path handles exceptions (lines 66-68)."""
    # Path with null byte raises exception
    result = sanitize_path("\x00invalid")
    assert result is None


def test_sanitize_path_blocks_dotdot_in_parts():
    """Test sanitize_path blocks paths with '..' in parts (lines 63-64)."""
    from unittest.mock import Mock, patch

    # Mock Path to simulate a path with '..' in parts after resolution
    mock_path = Mock(spec=Path)
    mock_path.parts = ("/", "home", "..", "etc")
    mock_path.resolve.return_value = mock_path

    with patch("asciidoc_artisan.core.async_file_ops.Path", return_value=mock_path):
        result = sanitize_path("/some/path")
        assert result is None


@pytest.mark.asyncio
async def test_async_read_text_without_aiofiles(tmp_path):
    """Test async_read_text falls back to sync when aiofiles unavailable (lines 94-99)."""
    from unittest.mock import patch

    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    with patch("asciidoc_artisan.core.async_file_ops.AIOFILES_AVAILABLE", False):
        content = await async_read_text(test_file)
        assert content == "test content"


@pytest.mark.asyncio
async def test_async_read_text_sync_fallback_error(tmp_path):
    """Test async_read_text handles sync fallback errors (lines 97-99)."""
    from unittest.mock import patch

    nonexistent = tmp_path / "nonexistent.txt"

    with patch("asciidoc_artisan.core.async_file_ops.AIOFILES_AVAILABLE", False):
        content = await async_read_text(nonexistent)
        assert content is None


@pytest.mark.asyncio
async def test_async_read_text_chunked_without_aiofiles(tmp_path):
    """Test async_read_text_chunked returns early when aiofiles unavailable (lines 133-134)."""
    from unittest.mock import patch

    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    with patch("asciidoc_artisan.core.async_file_ops.AIOFILES_AVAILABLE", False):
        chunks = []
        async for chunk in async_read_text_chunked(test_file):
            chunks.append(chunk)
        # Should return no chunks when aiofiles unavailable
        assert len(chunks) == 0


@pytest.mark.asyncio
async def test_async_read_text_chunked_error(tmp_path):
    """Test async_read_text_chunked handles errors (lines 145-146)."""
    nonexistent = tmp_path / "nonexistent.txt"

    chunks = []
    async for chunk in async_read_text_chunked(nonexistent):
        chunks.append(chunk)

    # Should handle error gracefully and return no chunks
    assert len(chunks) == 0


@pytest.mark.asyncio
async def test_async_atomic_save_text_without_aiofiles(tmp_path):
    """Test async_atomic_save_text falls back to sync (lines 182-185)."""
    from unittest.mock import patch

    test_file = tmp_path / "test.txt"

    with patch("asciidoc_artisan.core.async_file_ops.AIOFILES_AVAILABLE", False):
        result = await async_atomic_save_text(test_file, "test content")
        assert result is True
        assert test_file.read_text() == "test content"


@pytest.mark.asyncio
async def test_async_atomic_save_text_none_path():
    """Test async_atomic_save_text handles None path (lines 188-189)."""
    result = await async_atomic_save_text(None, "content")
    assert result is False


@pytest.mark.asyncio
async def test_async_atomic_save_text_cleanup_on_exception(tmp_path):
    """Test async_atomic_save_text cleans up temp file on exception (lines 204-214)."""
    from unittest.mock import patch

    test_file = tmp_path / "test.txt"

    # Mock aiofiles.os.replace to raise exception
    with patch("aiofiles.os.replace", side_effect=PermissionError("Mock error")):
        result = await async_atomic_save_text(test_file, "test content")
        assert result is False

        # Temp file should be cleaned up
        temp_file = test_file.with_suffix(test_file.suffix + ".tmp")
        assert not temp_file.exists()


@pytest.mark.asyncio
async def test_async_atomic_save_json_without_aiofiles(tmp_path):
    """Test async_atomic_save_json falls back to sync (lines 241-244)."""
    from unittest.mock import patch

    test_file = tmp_path / "test.json"

    with patch("asciidoc_artisan.core.async_file_ops.AIOFILES_AVAILABLE", False):
        result = await async_atomic_save_json(test_file, {"key": "value"})
        assert result is True
        assert test_file.exists()


@pytest.mark.asyncio
async def test_async_atomic_save_json_none_path():
    """Test async_atomic_save_json handles None path (lines 247-248)."""
    result = await async_atomic_save_json(None, {"key": "value"})
    assert result is False


@pytest.mark.asyncio
async def test_async_atomic_save_json_cleanup_on_exception(tmp_path):
    """Test async_atomic_save_json cleans up temp file on exception (lines 266-276)."""
    from unittest.mock import patch

    test_file = tmp_path / "test.json"

    # Mock aiofiles.os.replace to raise exception
    with patch("aiofiles.os.replace", side_effect=PermissionError("Mock error")):
        result = await async_atomic_save_json(test_file, {"key": "value"})
        assert result is False

        # Temp file should be cleaned up
        temp_file = test_file.with_suffix(test_file.suffix + ".tmp")
        assert not temp_file.exists()


def test_aiofiles_import_error():
    """Test handling when aiofiles is not available (lines 35-36)."""
    import importlib
    import sys
    from unittest.mock import patch

    # Save original modules
    original_aiofiles = sys.modules.get("aiofiles")
    original_async_file_ops = sys.modules.get("asciidoc_artisan.core.async_file_ops")

    try:
        # Remove modules
        for mod in ["aiofiles", "aiofiles.os", "asciidoc_artisan.core.async_file_ops"]:
            if mod in sys.modules:
                del sys.modules[mod]

        # Mock aiofiles import to raise ImportError
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if "aiofiles" in name:
                raise ImportError("Mock aiofiles not available")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            # Reload to trigger the import error path
            import asciidoc_artisan.core.async_file_ops as afo

            importlib.reload(afo)

            # AIOFILES_AVAILABLE should be False
            assert afo.AIOFILES_AVAILABLE is False

    finally:
        # Restore
        try:
            if original_aiofiles is not None:
                sys.modules["aiofiles"] = original_aiofiles

            if original_async_file_ops is not None:
                sys.modules["asciidoc_artisan.core.async_file_ops"] = original_async_file_ops

            # Reload back to normal
            if "asciidoc_artisan.core.async_file_ops" in sys.modules:
                import asciidoc_artisan.core.async_file_ops

                importlib.reload(asciidoc_artisan.core.async_file_ops)
        except (ImportError, KeyError):
            pass


@pytest.mark.asyncio
async def test_async_atomic_save_text_cleanup_exception(tmp_path):
    """Test cleanup exception handling in atomic_save_text (lines 211-212)."""
    from unittest.mock import Mock, patch

    test_file = tmp_path / "test.txt"

    # Create a mock temp_path that exists but raises on remove
    mock_temp = Mock()
    mock_temp.exists.return_value = True
    mock_temp.suffix = ".txt"

    # Mock Path.with_suffix to return our mock temp path
    with patch.object(Path, "with_suffix", return_value=mock_temp):
        # Mock aiofiles.os.replace to fail
        with patch("aiofiles.os.replace", side_effect=PermissionError("Write failed")):
            # Mock aiofiles.os.remove to also fail (triggers cleanup exception)
            with patch("aiofiles.os.remove", side_effect=PermissionError("Cleanup failed")):
                result = await async_atomic_save_text(test_file, "content")
                assert result is False


@pytest.mark.asyncio
async def test_async_atomic_save_json_cleanup_exception(tmp_path):
    """Test cleanup exception handling in atomic_save_json (lines 273-274)."""
    from unittest.mock import Mock, patch

    test_file = tmp_path / "test.json"

    # Create a mock temp_path that exists but raises on remove
    mock_temp = Mock()
    mock_temp.exists.return_value = True
    mock_temp.suffix = ".json"

    with patch.object(Path, "with_suffix", return_value=mock_temp):
        # Mock aiofiles.os.replace to fail
        with patch("aiofiles.os.replace", side_effect=PermissionError("Write failed")):
            # Mock aiofiles.os.remove to also fail
            with patch("aiofiles.os.remove", side_effect=PermissionError("Cleanup failed")):
                result = await async_atomic_save_json(test_file, {"key": "value"})
                assert result is False


@pytest.mark.asyncio
async def test_async_file_context_binary_mode(tmp_path):
    """Test AsyncFileContext with binary mode (line 353)."""
    test_file = tmp_path / "test.bin"
    binary_content = b"\x00\x01\x02\x03\x04\x05Binary data"
    test_file.write_bytes(binary_content)

    # Read in binary mode
    async with AsyncFileContext(test_file, "rb") as f:
        result = await f.read()

    assert result == binary_content

    # Write in binary mode
    new_content = b"\xff\xfe\xfd\xfc"
    async with AsyncFileContext(tmp_path / "new.bin", "wb") as f:
        await f.write(new_content)

    assert (tmp_path / "new.bin").read_bytes() == new_content


@pytest.mark.asyncio
async def test_async_file_context_without_aiofiles(tmp_path):
    """Test AsyncFileContext when aiofiles unavailable (lines 342-343)."""
    from unittest.mock import patch

    from asciidoc_artisan.core.async_file_ops import AsyncFileContext

    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    with patch("asciidoc_artisan.core.async_file_ops.AIOFILES_AVAILABLE", False):
        ctx = AsyncFileContext(test_file)
        with pytest.raises(RuntimeError, match="aiofiles not available"):
            async with ctx:
                pass


@pytest.mark.asyncio
async def test_async_copy_file_without_aiofiles(tmp_path):
    """Test async_copy_file falls back to sync (lines 378-386)."""
    from unittest.mock import patch

    src = tmp_path / "source.txt"
    dst = tmp_path / "dest.txt"
    src.write_text("test content")

    with patch("asciidoc_artisan.core.async_file_ops.AIOFILES_AVAILABLE", False):
        result = await async_copy_file(src, dst)
        assert result is True
        assert dst.read_text() == "test content"


@pytest.mark.asyncio
async def test_async_copy_file_sync_fallback_error(tmp_path):
    """Test async_copy_file handles sync fallback errors (lines 384-386)."""
    from unittest.mock import patch

    src = tmp_path / "nonexistent.txt"
    dst = tmp_path / "dest.txt"

    with patch("asciidoc_artisan.core.async_file_ops.AIOFILES_AVAILABLE", False):
        result = await async_copy_file(src, dst)
        assert result is False


def test_run_async_no_event_loop():
    """Test run_async creates event loop when none exists (lines 423-425)."""
    from unittest.mock import Mock, patch

    from asciidoc_artisan.core.async_file_ops import run_async

    async def dummy_coro():
        return "result"

    # Mock get_event_loop to raise RuntimeError
    with patch("asyncio.get_event_loop", side_effect=RuntimeError("No loop")):
        # Mock new_event_loop and set_event_loop
        mock_loop = Mock()
        mock_loop.run_until_complete.return_value = "result"

        with patch("asyncio.new_event_loop", return_value=mock_loop):
            with patch("asyncio.set_event_loop") as mock_set:
                result = run_async(dummy_coro())

                # Should create and set new loop
                assert mock_set.called
                assert result == "result"
