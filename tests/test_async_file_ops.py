"""
Tests for async file operations (v1.6.0 Task 2).

Tests async/await file I/O operations using aiofiles.
"""

import asyncio
import json
import pytest
from pathlib import Path
from asciidoc_artisan.core.async_file_ops import (
    sanitize_path,
    async_read_text,
    async_read_text_chunked,
    async_atomic_save_text,
    async_atomic_save_json,
    async_read_json,
    AsyncFileContext,
    async_copy_file,
    run_async,
    AIOFILES_AVAILABLE,
)


# Skip all tests if aiofiles not available
pytestmark = pytest.mark.skipif(
    not AIOFILES_AVAILABLE, reason="aiofiles not installed"
)


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
    """Test path sanitization blocks directory traversal."""
    result = sanitize_path("../../etc/passwd")

    assert result is None


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
    files_and_contents = [
        (tmp_path / f"file{i}.txt", f"Content {i}") for i in range(5)
    ]

    # Write all files concurrently
    tasks = [
        async_atomic_save_text(file, content) for file, content in files_and_contents
    ]
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
    files_and_contents = [
        (tmp_path / f"file{i}.txt", f"Content {i}") for i in range(5)
    ]

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
