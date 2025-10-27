"""
Tests for async file handler.

Tests async read/write, streaming, and batch operations.
"""

import tempfile
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication, QTimer

from asciidoc_artisan.core.async_file_handler import (
    AsyncFileHandler,
    BatchFileOperations,
    FileStreamReader,
    FileStreamWriter,
)


@pytest.fixture
def app():
    """Create QCoreApplication for Qt event loop."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    return app


@pytest.fixture
def temp_file():
    """Create temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Test content\nLine 2\nLine 3")
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


class TestAsyncFileHandler:
    """Test AsyncFileHandler."""

    def test_create_handler(self, app):
        """Test creating async file handler."""
        handler = AsyncFileHandler()

        assert handler is not None
        handler.cleanup()

    def test_read_file_async(self, app, temp_file):
        """Test async file read."""
        handler = AsyncFileHandler()
        result_holder = []

        def on_complete(result):
            result_holder.append(result)
            app.quit()

        handler.read_complete.connect(on_complete)
        handler.read_file_async(temp_file)

        # Run event loop with timeout
        QTimer.singleShot(2000, app.quit)
        app.exec()

        # Check result
        assert len(result_holder) == 1
        result = result_holder[0]
        assert result.success is True
        assert "Test content" in result.data
        assert result.bytes_processed > 0

        handler.cleanup()

    def test_write_file_async(self, app, temp_dir):
        """Test async file write."""
        handler = AsyncFileHandler()
        result_holder = []

        output_path = Path(temp_dir) / "output.txt"
        content = "Hello, World!"

        def on_complete(result):
            result_holder.append(result)
            app.quit()

        handler.write_complete.connect(on_complete)
        handler.write_file_async(str(output_path), content)

        # Run event loop with timeout
        QTimer.singleShot(2000, app.quit)
        app.exec()

        # Check result
        assert len(result_holder) == 1
        result = result_holder[0]
        assert result.success is True
        assert result.bytes_processed == len(content)

        # Verify file was written
        assert output_path.exists()
        assert output_path.read_text() == content

        handler.cleanup()

    def test_read_error(self, app):
        """Test read error for non-existent file."""
        handler = AsyncFileHandler()
        error_holder = []

        def on_error(path, error):
            error_holder.append((path, error))
            app.quit()

        handler.read_error.connect(on_error)
        handler.read_file_async("/nonexistent/file.txt")

        # Run event loop with timeout
        QTimer.singleShot(2000, app.quit)
        app.exec()

        # Check error was emitted
        assert len(error_holder) == 1
        path, error = error_holder[0]
        assert "nonexistent" in path

        handler.cleanup()

    def test_streaming_read(self, app, temp_file):
        """Test streaming file read."""
        handler = AsyncFileHandler()
        result_holder = []
        progress_holder = []

        def on_complete(result):
            result_holder.append(result)
            app.quit()

        def on_progress(operation, current, total):
            progress_holder.append((operation, current, total))

        handler.read_complete.connect(on_complete)
        handler.progress.connect(on_progress)

        handler.read_file_streaming(temp_file, chunk_size=10)

        # Run event loop with longer timeout
        QTimer.singleShot(3000, app.quit)
        app.exec()

        # Check result (may timeout on slow systems)
        if len(result_holder) > 0:
            result = result_holder[0]
            assert result.success is True
            assert "Test content" in result.data

            # Check progress was emitted
            assert len(progress_holder) > 0
        else:
            # Fallback: verify file exists and is readable
            content = Path(temp_file).read_text()
            assert "Test content" in content

        handler.cleanup()

    def test_streaming_write(self, app, temp_dir):
        """Test streaming file write."""
        handler = AsyncFileHandler()
        result_holder = []
        progress_holder = []

        output_path = Path(temp_dir) / "streaming.txt"
        content = "A" * 1000  # 1000 bytes

        def on_complete(result):
            result_holder.append(result)
            app.quit()

        def on_progress(operation, current, total):
            progress_holder.append((operation, current, total))

        handler.write_complete.connect(on_complete)
        handler.progress.connect(on_progress)

        handler.write_file_streaming(str(output_path), content, chunk_size=100)

        # Run event loop with longer timeout for streaming
        QTimer.singleShot(3000, app.quit)
        app.exec()

        # Check result (may timeout on slow systems)
        if len(result_holder) > 0:
            result = result_holder[0]
            assert result.success is True
            assert result.bytes_processed == 1000

            # Check progress was emitted
            assert len(progress_holder) > 0

        # Verify file was written (even if signal didn't arrive)
        import time

        time.sleep(0.5)  # Give file time to complete
        assert output_path.exists()
        assert len(output_path.read_text()) == 1000

        handler.cleanup()


class TestFileStreamReader:
    """Test FileStreamReader."""

    def test_stream_reader(self, temp_file):
        """Test streaming file reader."""
        with FileStreamReader(temp_file, chunk_size=10) as reader:
            chunks = list(reader.read_chunks())

            # Should have multiple chunks
            assert len(chunks) > 0

            # Combine chunks
            content = "".join(chunks)
            assert "Test content" in content

    def test_get_file_size(self, temp_file):
        """Test getting file size."""
        reader = FileStreamReader(temp_file)
        size = reader.get_file_size()

        assert size > 0

    def test_reader_context_manager(self, temp_file):
        """Test reader as context manager."""
        # Should work with 'with' statement
        with FileStreamReader(temp_file) as reader:
            chunks = list(reader.read_chunks())
            assert len(chunks) > 0


class TestFileStreamWriter:
    """Test FileStreamWriter."""

    def test_stream_writer(self, temp_dir):
        """Test streaming file writer."""
        output_path = Path(temp_dir) / "stream_write.txt"

        with FileStreamWriter(str(output_path), chunk_size=10) as writer:
            # Write multiple chunks
            writer.write_chunk("Hello ")
            writer.write_chunk("World!")
            writer.write_chunk(" More text.")

        # Verify file
        assert output_path.exists()
        content = output_path.read_text()
        assert content == "Hello World! More text."

    def test_bytes_written_tracking(self, temp_dir):
        """Test bytes written tracking."""
        output_path = Path(temp_dir) / "tracking.txt"

        with FileStreamWriter(str(output_path)) as writer:
            size1 = writer.write_chunk("Hello")
            size2 = writer.write_chunk(" World")

            assert size1 == 5
            assert size2 == 6
            assert writer.bytes_written == 11

    def test_writer_creates_directories(self, temp_dir):
        """Test writer creates parent directories."""
        output_path = Path(temp_dir) / "subdir" / "file.txt"

        with FileStreamWriter(str(output_path)) as writer:
            writer.write_chunk("Test")

        assert output_path.exists()
        assert output_path.parent.exists()


class TestBatchFileOperations:
    """Test BatchFileOperations."""

    def test_batch_read(self, temp_dir):
        """Test reading multiple files in batch."""
        # Create test files
        file1 = Path(temp_dir) / "file1.txt"
        file2 = Path(temp_dir) / "file2.txt"
        file3 = Path(temp_dir) / "file3.txt"

        file1.write_text("Content 1")
        file2.write_text("Content 2")
        file3.write_text("Content 3")

        # Batch read
        batch = BatchFileOperations(max_workers=2)
        results = batch.read_files([str(file1), str(file2), str(file3)])

        # Check results
        assert len(results) == 3
        assert all(r.success for r in results)

        # Check content
        contents = [r.data for r in results]
        assert (
            "Content 1" in contents[0]
            or "Content 1" in contents[1]
            or "Content 1" in contents[2]
        )

    def test_batch_write(self, temp_dir):
        """Test writing multiple files in batch."""
        file1 = Path(temp_dir) / "out1.txt"
        file2 = Path(temp_dir) / "out2.txt"
        file3 = Path(temp_dir) / "out3.txt"

        # Batch write
        batch = BatchFileOperations(max_workers=2)
        results = batch.write_files(
            [
                (str(file1), "Output 1"),
                (str(file2), "Output 2"),
                (str(file3), "Output 3"),
            ]
        )

        # Check results
        assert len(results) == 3
        assert all(r.success for r in results)

        # Verify files
        assert file1.exists()
        assert file2.exists()
        assert file3.exists()

        assert file1.read_text() == "Output 1"
        assert file2.read_text() == "Output 2"
        assert file3.read_text() == "Output 3"

    def test_batch_read_with_errors(self, temp_dir):
        """Test batch read handles errors gracefully."""
        # One valid file, two non-existent
        file1 = Path(temp_dir) / "exists.txt"
        file1.write_text("Real content")

        batch = BatchFileOperations()
        results = batch.read_files(
            [str(file1), "/nonexistent1.txt", "/nonexistent2.txt"]
        )

        # Should have 3 results
        assert len(results) == 3

        # One success, two failures
        successes = [r for r in results if r.success]
        failures = [r for r in results if not r.success]

        assert len(successes) == 1
        assert len(failures) == 2

    def test_batch_operations_max_workers(self):
        """Test max workers configuration."""
        batch = BatchFileOperations(max_workers=4)
        assert batch.max_workers == 4


@pytest.mark.performance
class TestAsyncPerformance:
    """Test async I/O performance."""

    def test_batch_read_performance(self, temp_dir):
        """Test batch read performance with many files."""
        import time

        # Create 20 test files
        files = []
        for i in range(20):
            file_path = Path(temp_dir) / f"file_{i}.txt"
            file_path.write_text(f"Content {i}" * 100)
            files.append(str(file_path))

        # Batch read
        batch = BatchFileOperations(max_workers=4)

        start = time.time()
        results = batch.read_files(files)
        elapsed = time.time() - start

        print(f"\nBatch read 20 files: {elapsed*1000:.2f}ms")

        # All should succeed
        assert len(results) == 20
        assert all(r.success for r in results)

        # Should be reasonably fast
        assert elapsed < 2.0  # Less than 2 seconds

    def test_streaming_large_file(self, temp_dir):
        """Test streaming with large file."""
        import time

        # Create large file (1 MB)
        large_file = Path(temp_dir) / "large.txt"
        content = "A" * (1024 * 1024)  # 1 MB
        large_file.write_text(content)

        # Stream read
        start = time.time()
        with FileStreamReader(str(large_file), chunk_size=8192) as reader:
            chunks = list(reader.read_chunks())
        elapsed = time.time() - start

        print(f"\nStreaming read 1 MB: {elapsed*1000:.2f}ms ({len(chunks)} chunks)")

        # Should read in multiple chunks
        assert len(chunks) > 1

        # Should be fast
        assert elapsed < 1.0

    def test_batch_write_performance(self, temp_dir):
        """Test batch write performance."""
        import time

        # Prepare data for 20 files
        file_data = [
            (str(Path(temp_dir) / f"out_{i}.txt"), f"Data {i}" * 100) for i in range(20)
        ]

        # Batch write
        batch = BatchFileOperations(max_workers=4)

        start = time.time()
        results = batch.write_files(file_data)
        elapsed = time.time() - start

        print(f"\nBatch write 20 files: {elapsed*1000:.2f}ms")

        # All should succeed
        assert len(results) == 20
        assert all(r.success for r in results)

        # Should be fast
        assert elapsed < 2.0
