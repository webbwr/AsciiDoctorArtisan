"""
Tests for large file handler module.

Tests file size categorization, optimized loading strategies, and progress signals.
"""

import pytest
from PySide6.QtCore import QCoreApplication

from asciidoc_artisan.core.large_file_handler import (
    LARGE_FILE,
    MEDIUM_FILE,
    PREVIEW_CHUNK_SIZE,
    PREVIEW_DISABLE_THRESHOLD,
    SMALL_FILE,
    LargeFileHandler,
)


@pytest.fixture
def handler(qtbot):
    """Create LargeFileHandler instance."""
    return LargeFileHandler()


class TestFileSizeCategorization:
    """Test file size category detection."""

    def test_small_file_category(self, tmp_path):
        """Test files < 1MB categorized as small."""
        file_path = tmp_path / "small.txt"
        file_path.write_text("x" * (SMALL_FILE - 1000))  # Just under 1MB

        category = LargeFileHandler.get_file_size_category(file_path)
        assert category == "small"

    def test_medium_file_category(self, tmp_path):
        """Test files 1-10MB categorized as medium."""
        file_path = tmp_path / "medium.txt"
        file_path.write_text("x" * (MEDIUM_FILE + 1000))  # Just over 1MB

        category = LargeFileHandler.get_file_size_category(file_path)
        assert category == "medium"

    def test_large_file_category(self, tmp_path):
        """Test files > 10MB categorized as large."""
        file_path = tmp_path / "large.txt"
        # Create a large file using write in chunks (faster than single write)
        with open(file_path, "w") as f:
            chunk = "x" * (1024 * 1024)  # 1MB chunk
            for _ in range(11):  # Write 11MB
                f.write(chunk)

        category = LargeFileHandler.get_file_size_category(file_path)
        assert category == "large"

    def test_nonexistent_file_defaults_to_small(self, tmp_path):
        """Test nonexistent file returns 'small' category."""
        file_path = tmp_path / "nonexistent.txt"
        category = LargeFileHandler.get_file_size_category(file_path)
        assert category == "small"

    def test_empty_file_is_small(self, tmp_path):
        """Test empty file categorized as small."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")

        category = LargeFileHandler.get_file_size_category(file_path)
        assert category == "small"


class TestPreviewOptimization:
    """Test preview optimization decision logic."""

    def test_should_optimize_preview_small_file(self):
        """Test small files don't need preview optimization."""
        assert LargeFileHandler.should_optimize_preview(SMALL_FILE - 1) is False

    def test_should_optimize_preview_medium_file(self):
        """Test medium files should optimize preview."""
        assert LargeFileHandler.should_optimize_preview(MEDIUM_FILE) is True

    def test_should_optimize_preview_large_file(self):
        """Test large files should optimize preview."""
        assert LargeFileHandler.should_optimize_preview(LARGE_FILE) is True

    def test_should_disable_preview_small_file(self):
        """Test small files don't disable preview."""
        assert LargeFileHandler.should_disable_preview(SMALL_FILE) is False

    def test_should_disable_preview_large_file(self):
        """Test large files don't disable preview unless very large."""
        assert LargeFileHandler.should_disable_preview(LARGE_FILE) is False

    def test_should_disable_preview_very_large_file(self):
        """Test very large files (> 50MB) disable preview."""
        assert (
            LargeFileHandler.should_disable_preview(PREVIEW_DISABLE_THRESHOLD + 1)
            is True
        )


class TestSmallFileLoading:
    """Test small file loading (< 1MB)."""

    def test_load_small_file_success(self, handler, tmp_path):
        """Test loading small file succeeds."""
        file_path = tmp_path / "small.txt"
        content = "Small file content\nLine 2\nLine 3"
        file_path.write_text(content)

        success, loaded_content, error = handler.load_file_optimized(file_path)

        assert success is True
        assert loaded_content == content
        assert error == ""

    def test_load_small_file_utf8(self, handler, tmp_path):
        """Test loading small file with UTF-8 characters."""
        file_path = tmp_path / "utf8.txt"
        content = "Unicode: 测试 🔑 café"
        file_path.write_text(content, encoding="utf-8")

        success, loaded_content, error = handler.load_file_optimized(file_path)

        assert success is True
        assert loaded_content == content
        assert error == ""

    def test_load_empty_file(self, handler, tmp_path):
        """Test loading empty file."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")

        success, loaded_content, error = handler.load_file_optimized(file_path)

        assert success is True
        assert loaded_content == ""
        assert error == ""


class TestMediumFileLoading:
    """Test medium file loading (1-10MB) with progress signals."""

    def test_load_medium_file_success(self, handler, qtbot, tmp_path):
        """Test loading medium file with progress signals."""
        file_path = tmp_path / "medium.txt"
        # Create 2MB file (medium size)
        content = "x" * (2 * 1024 * 1024)
        file_path.write_text(content)

        # Track progress signals
        progress_updates = []

        def track_progress(percentage, message):
            progress_updates.append((percentage, message))

        handler.progress_update.connect(track_progress)

        success, loaded_content, error = handler.load_file_optimized(file_path)

        # Process Qt events to ensure signals are delivered
        QCoreApplication.processEvents()

        assert success is True
        assert len(loaded_content) == len(content)
        assert error == ""

        # Should have progress updates
        assert len(progress_updates) > 0
        # Should start at 0%
        assert progress_updates[0][0] == 0
        # Should end at 100%
        assert progress_updates[-1][0] == 100
        assert "complete" in progress_updates[-1][1].lower()

    def test_medium_file_progress_messages(self, handler, qtbot, tmp_path):
        """Test progress messages during medium file load."""
        file_path = tmp_path / "medium.txt"
        content = "x" * (2 * 1024 * 1024)
        file_path.write_text(content)

        messages = []

        def track_messages(percentage, message):
            messages.append(message)

        handler.progress_update.connect(track_messages)
        handler.load_file_optimized(file_path)
        QCoreApplication.processEvents()

        assert any("Loading" in msg for msg in messages)
        assert any("complete" in msg.lower() for msg in messages)


class TestLargeFileLoading:
    """Test large file loading (> 10MB) with line-by-line processing."""

    def test_load_large_file_success(self, handler, qtbot, tmp_path):
        """Test loading large file with progress signals."""
        file_path = tmp_path / "large.txt"
        # Create 11MB file (large size) with lines
        lines = ["Line content " * 100 + "\n"] * 10000
        file_path.write_text("".join(lines))

        progress_updates = []

        def track_progress(percentage, message):
            progress_updates.append((percentage, message))

        handler.progress_update.connect(track_progress)

        success, loaded_content, error = handler.load_file_optimized(file_path)
        QCoreApplication.processEvents()

        assert success is True
        assert len(loaded_content) > 0
        assert error == ""

        # Should have progress updates
        assert len(progress_updates) > 0
        assert progress_updates[0][0] == 0
        assert progress_updates[-1][0] == 100

    def test_large_file_progress_updates_every_5_percent(
        self, handler, qtbot, tmp_path
    ):
        """Test large file emits progress every 5%."""
        file_path = tmp_path / "large.txt"
        lines = ["x" * 1000 + "\n"] * 10000
        file_path.write_text("".join(lines))

        percentages = []

        def track_percentage(percentage, message):
            percentages.append(percentage)

        handler.progress_update.connect(track_percentage)
        handler.load_file_optimized(file_path)
        QCoreApplication.processEvents()

        # Should have updates roughly every 5%
        assert len(percentages) > 0
        # Check we got intermediate updates, not just 0 and 100
        assert any(0 < p < 100 for p in percentages)


class TestErrorHandling:
    """Test error handling during file loading."""

    def test_load_nonexistent_file(self, handler, tmp_path):
        """Test loading nonexistent file returns error."""
        file_path = tmp_path / "nonexistent.txt"

        success, content, error = handler.load_file_optimized(file_path)

        assert success is False
        assert content == ""
        assert error != ""
        assert "No such file" in error or "not found" in error.lower()

    def test_load_file_permission_error(self, handler, tmp_path, monkeypatch):
        """Test loading file with permission error."""
        file_path = tmp_path / "restricted.txt"
        file_path.write_text("content")

        # Mock open to raise PermissionError
        def mock_open(*args, **kwargs):
            raise PermissionError("Access denied")

        monkeypatch.setattr("builtins.open", mock_open)

        success, content, error = handler.load_file_optimized(file_path)

        assert success is False
        assert content == ""
        assert "Access denied" in error or "Permission" in error

    def test_load_file_unicode_decode_error(self, handler, tmp_path):
        """Test loading file with invalid encoding uses error replacement."""
        file_path = tmp_path / "invalid.txt"
        # Write invalid UTF-8 bytes
        file_path.write_bytes(b"\x80\x81\x82\x83")

        # Should succeed but replace invalid characters
        success, content, error = handler.load_file_optimized(file_path)

        assert success is True
        # Content should be replaced with replacement characters
        assert len(content) > 0
        assert error == ""


class TestPreviewContent:
    """Test preview content truncation for large documents."""

    def test_preview_content_small_document(self):
        """Test small documents not truncated."""
        content = "Short content"
        preview = LargeFileHandler.get_preview_content(content)
        assert preview == content

    def test_preview_content_large_document_truncated(self):
        """Test large documents truncated at max_chars."""
        content = "x" * (PREVIEW_CHUNK_SIZE * 2)
        preview = LargeFileHandler.get_preview_content(content)

        assert len(preview) < len(content)
        assert "truncated" in preview.lower()

    def test_preview_content_truncates_at_line_boundary(self):
        """Test truncation happens at line boundaries."""
        # Create content with lines
        lines = ["Line content\n"] * 10000
        content = "".join(lines)

        preview = LargeFileHandler.get_preview_content(content, max_chars=50000)

        # Should end with a complete line (newline before truncation notice)
        assert "\n\n[Preview truncated" in preview

    def test_preview_content_includes_remaining_count(self):
        """Test truncation notice includes remaining character count."""
        content = "x" * (PREVIEW_CHUNK_SIZE * 2)
        preview = LargeFileHandler.get_preview_content(content)

        # Should show how many characters not shown
        assert "characters not shown" in preview
        # Should have comma-separated number formatting
        assert "," in preview  # e.g., "100,000 characters"

    def test_preview_content_custom_max_chars(self):
        """Test preview content with custom max_chars."""
        content = "x" * 10000
        preview = LargeFileHandler.get_preview_content(content, max_chars=1000)

        assert len(preview) < 2000  # Much shorter than original


class TestLoadTimeEstimation:
    """Test load time estimation."""

    def test_estimate_very_small_file(self):
        """Test estimation for very small files."""
        estimate = LargeFileHandler.estimate_load_time(100 * 1024)  # 100KB
        assert "< 1 second" in estimate

    def test_estimate_small_file(self):
        """Test estimation for small files."""
        estimate = LargeFileHandler.estimate_load_time(5 * 1024 * 1024)  # 5MB
        assert "second" in estimate.lower()

    def test_estimate_medium_file(self):
        """Test estimation for medium files."""
        estimate = LargeFileHandler.estimate_load_time(30 * 1024 * 1024)  # 30MB
        assert "second" in estimate.lower() or "minute" in estimate.lower()

    def test_estimate_large_file(self):
        """Test estimation for large files."""
        estimate = LargeFileHandler.estimate_load_time(200 * 1024 * 1024)  # 200MB
        assert "minute" in estimate.lower()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_file_exactly_at_small_threshold(self, handler, tmp_path):
        """Test file exactly at 1MB threshold."""
        file_path = tmp_path / "threshold.txt"
        file_path.write_text("x" * SMALL_FILE)

        category = LargeFileHandler.get_file_size_category(file_path)
        # At exactly 1MB, should be medium (>= SMALL_FILE)
        assert category == "medium"

    def test_file_exactly_at_large_threshold(self, handler, tmp_path):
        """Test file exactly at 10MB threshold."""
        file_path = tmp_path / "threshold.txt"
        with open(file_path, "w") as f:
            f.write("x" * LARGE_FILE)

        category = LargeFileHandler.get_file_size_category(file_path)
        # At exactly 10MB, should be large (>= LARGE_FILE)
        assert category == "large"

    def test_last_file_size_tracking(self, handler, tmp_path):
        """Test handler tracks last loaded file size."""
        file_path = tmp_path / "test.txt"
        content = "x" * 5000
        file_path.write_text(content)

        handler.load_file_optimized(file_path)

        assert handler._last_file_size == file_path.stat().st_size

    def test_multiple_loads_update_last_size(self, handler, tmp_path):
        """Test multiple loads update last file size."""
        file1 = tmp_path / "file1.txt"
        file1.write_text("x" * 1000)

        file2 = tmp_path / "file2.txt"
        file2.write_text("x" * 5000)

        handler.load_file_optimized(file1)
        size1 = handler._last_file_size

        handler.load_file_optimized(file2)
        size2 = handler._last_file_size

        assert size2 > size1
        assert size2 == file2.stat().st_size
