"""
Tests for macOS APFS File Operations (v2.0.0).

Tests APFS-specific file operations including CoW cloning, atomic writes,
fast directory size calculation, and snapshot creation.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from asciidoc_artisan.core.macos_file_ops import (
    apfs_atomic_write,
    apfs_clone_file,
    apfs_create_snapshot,
    apfs_fast_directory_size,
    is_apfs_filesystem,
    optimize_file_operations_for_macos,
)


@pytest.mark.unit
class TestIsApfsFilesystem:
    """Test APFS filesystem detection."""

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_is_apfs_when_apfs_detected(self, mock_run):
        """Test returns True when APFS is detected."""
        mock_run.return_value = MagicMock(
            stdout="File System Personality: APFS\nVolume Name: Macintosh HD",
            returncode=0,
        )

        result = is_apfs_filesystem("/tmp/test")

        assert result is True
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["diskutil", "info", "/tmp/test"]

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_is_apfs_when_not_apfs(self, mock_run):
        """Test returns False when not APFS."""
        mock_run.return_value = MagicMock(
            stdout="File System Personality: HFS+\nVolume Name: External",
            returncode=0,
        )

        result = is_apfs_filesystem("/Volumes/external")

        assert result is False

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_is_apfs_when_command_fails(self, mock_run):
        """Test returns False when diskutil command fails."""
        mock_run.return_value = MagicMock(
            stdout="",
            returncode=1,
        )

        result = is_apfs_filesystem("/invalid/path")

        assert result is False

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_is_apfs_handles_timeout(self, mock_run):
        """Test handles subprocess timeout gracefully."""
        mock_run.side_effect = subprocess.TimeoutExpired("diskutil", 1)

        result = is_apfs_filesystem("/tmp/test")

        assert result is False

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_is_apfs_handles_file_not_found(self, mock_run):
        """Test handles diskutil not found error."""
        mock_run.side_effect = FileNotFoundError("diskutil not found")

        result = is_apfs_filesystem("/tmp/test")

        assert result is False


@pytest.mark.unit
class TestApfsCloneFile:
    """Test APFS CoW file cloning."""

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_clone_file_success(self, mock_run):
        """Test successful APFS file cloning."""
        mock_run.return_value = MagicMock(returncode=0)

        result = apfs_clone_file("/tmp/source.txt", "/tmp/dest.txt")

        assert result is True
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["cp", "-c", "/tmp/source.txt", "/tmp/dest.txt"]

    @patch("asciidoc_artisan.core.macos_file_ops.shutil.copy2")
    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_clone_file_fallback_to_standard_copy(self, mock_run, mock_copy2):
        """Test fallback to standard copy when clone fails."""
        mock_run.return_value = MagicMock(returncode=1)

        result = apfs_clone_file("/tmp/source.txt", "/tmp/dest.txt")

        assert result is True
        mock_copy2.assert_called_once_with("/tmp/source.txt", "/tmp/dest.txt")

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_clone_file_handles_timeout(self, mock_run):
        """Test handles timeout during clone operation."""
        mock_run.side_effect = subprocess.TimeoutExpired("cp", 5)

        # Should fallback to standard copy, but we'll make that fail too
        with patch("asciidoc_artisan.core.macos_file_ops.shutil.copy2") as mock_copy2:
            mock_copy2.side_effect = Exception("Copy failed")
            result = apfs_clone_file("/tmp/source.txt", "/tmp/dest.txt")

        assert result is False

    @patch("asciidoc_artisan.core.macos_file_ops.shutil.copy2")
    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_clone_file_standard_copy_failure(self, mock_run, mock_copy2):
        """Test returns False when both clone and copy fail."""
        mock_run.return_value = MagicMock(returncode=1)
        mock_copy2.side_effect = Exception("Permission denied")

        result = apfs_clone_file("/tmp/source.txt", "/tmp/dest.txt")

        assert result is False


@pytest.mark.unit
class TestApfsAtomicWrite:
    """Test APFS atomic write operations."""

    def test_atomic_write_small_file_direct(self):
        """Test small file (<4KB) uses direct atomic write."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "small.txt")
            content = "Small content"  # <4KB

            result = apfs_atomic_write(file_path, content)

            assert result is True
            assert os.path.exists(file_path)
            with open(file_path, "r") as f:
                assert f.read() == content

    def test_atomic_write_large_file_with_temp(self):
        """Test large file (>4KB) uses temp file pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "large.txt")
            # Create >4KB content
            content = "x" * 5000

            result = apfs_atomic_write(file_path, content)

            assert result is True
            assert os.path.exists(file_path)
            # Temp file should be cleaned up
            assert not os.path.exists(f"{file_path}.tmp")
            with open(file_path, "r") as f:
                assert f.read() == content

    def test_atomic_write_custom_encoding(self):
        """Test atomic write with custom encoding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "encoded.txt")
            content = "Special chars: ñ, ü, ö"

            result = apfs_atomic_write(file_path, content, encoding="utf-8")

            assert result is True
            with open(file_path, "r", encoding="utf-8") as f:
                assert f.read() == content

    def test_atomic_write_handles_write_error(self):
        """Test handles write errors gracefully."""
        # Try to write to invalid path
        result = apfs_atomic_write("/invalid/path/file.txt", "content")

        assert result is False

    def test_atomic_write_replaces_existing_file(self):
        """Test atomic write replaces existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "replace.txt")

            # Create initial file
            with open(file_path, "w") as f:
                f.write("old content")

            # Overwrite with atomic write
            result = apfs_atomic_write(file_path, "new content")

            assert result is True
            with open(file_path, "r") as f:
                assert f.read() == "new content"


@pytest.mark.unit
class TestApfsFastDirectorySize:
    """Test APFS fast directory size calculation."""

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_directory_size_success(self, mock_run):
        """Test successful directory size calculation."""
        # Mock du output: "1024  /tmp/testdir"
        mock_run.return_value = MagicMock(
            stdout="1024\t/tmp/testdir\n",
            returncode=0,
        )

        result = apfs_fast_directory_size("/tmp/testdir")

        # 1024 KB = 1048576 bytes
        assert result == 1024 * 1024
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["du", "-sk", "/tmp/testdir"]

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_directory_size_command_fails(self, mock_run):
        """Test fallback when du command fails."""
        mock_run.return_value = MagicMock(
            stdout="",
            returncode=1,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file for fallback calculation
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")

            result = apfs_fast_directory_size(tmpdir)

            # Should fallback to Python calculation
            assert result > 0

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_directory_size_handles_timeout(self, mock_run):
        """Test handles subprocess timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("du", 5)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = apfs_fast_directory_size(tmpdir)

            # Should fallback to Python calculation
            assert result >= 0

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_directory_size_invalid_output(self, mock_run):
        """Test handles invalid du output."""
        mock_run.return_value = MagicMock(
            stdout="invalid output",
            returncode=0,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            result = apfs_fast_directory_size(tmpdir)

            # Should fallback to Python calculation
            assert result >= 0

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_directory_size_nonexistent_path(self, mock_run):
        """Test returns 0 for nonexistent path."""
        mock_run.return_value = MagicMock(returncode=1)

        result = apfs_fast_directory_size("/nonexistent/path")

        assert result == 0


@pytest.mark.unit
class TestApfsCreateSnapshot:
    """Test APFS snapshot creation."""

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_create_snapshot_success(self, mock_run):
        """Test successful snapshot creation."""
        # Mock diskutil info and tmutil localsnapshot
        mock_run.side_effect = [
            MagicMock(
                stdout="Volume Name:   Macintosh HD\nAPFS Volume",
                returncode=0,
            ),
            MagicMock(returncode=0),  # tmutil success
        ]

        result = apfs_create_snapshot("/tmp/test", "test_snapshot")

        assert result is True
        # Should call diskutil info and tmutil localsnapshot
        assert mock_run.call_count == 2

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_create_snapshot_auto_generated_name(self, mock_run):
        """Test snapshot with auto-generated name."""
        mock_run.side_effect = [
            MagicMock(
                stdout="Volume Name:   Macintosh HD",
                returncode=0,
            ),
            MagicMock(returncode=0),
        ]

        result = apfs_create_snapshot("/tmp/test")  # No snapshot_name

        assert result is True
        # Check that tmutil was called with auto-generated name
        assert mock_run.call_count == 2
        tmutil_call = mock_run.call_args_list[1][0][0]
        assert "asciidoc_artisan_" in tmutil_call[3]

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_create_snapshot_diskutil_fails(self, mock_run):
        """Test returns False when diskutil fails."""
        mock_run.return_value = MagicMock(returncode=1)

        result = apfs_create_snapshot("/tmp/test", "test_snapshot")

        assert result is False

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_create_snapshot_no_volume_name(self, mock_run):
        """Test returns False when volume name not found."""
        mock_run.return_value = MagicMock(
            stdout="Some output without Volume Name field",
            returncode=0,
        )

        result = apfs_create_snapshot("/tmp/test", "test_snapshot")

        assert result is False

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_create_snapshot_tmutil_fails(self, mock_run):
        """Test returns False when tmutil fails."""
        mock_run.side_effect = [
            MagicMock(
                stdout="Volume Name:   Macintosh HD",
                returncode=0,
            ),
            MagicMock(returncode=1),  # tmutil fails
        ]

        result = apfs_create_snapshot("/tmp/test", "test_snapshot")

        assert result is False

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_create_snapshot_handles_timeout(self, mock_run):
        """Test handles timeout during snapshot creation."""
        mock_run.side_effect = subprocess.TimeoutExpired("tmutil", 5)

        result = apfs_create_snapshot("/tmp/test", "test_snapshot")

        assert result is False


@pytest.mark.unit
class TestOptimizeFileOperationsForMacos:
    """Test macOS file operation optimization configuration."""

    @patch("asciidoc_artisan.core.macos_file_ops.is_apfs_filesystem")
    def test_optimize_when_apfs_detected(self, mock_is_apfs):
        """Test all optimizations enabled when APFS detected."""
        mock_is_apfs.return_value = True

        config = optimize_file_operations_for_macos("/tmp/test")

        assert config["use_apfs_cloning"] is True
        assert config["use_apfs_atomic_write"] is True
        assert config["use_apfs_snapshots"] is True
        assert config["use_fast_directory_size"] is True

    @patch("asciidoc_artisan.core.macos_file_ops.is_apfs_filesystem")
    def test_optimize_when_not_apfs(self, mock_is_apfs):
        """Test all optimizations disabled when not APFS."""
        mock_is_apfs.return_value = False

        config = optimize_file_operations_for_macos("/Volumes/external")

        assert config["use_apfs_cloning"] is False
        assert config["use_apfs_atomic_write"] is False
        assert config["use_apfs_snapshots"] is False
        assert config["use_fast_directory_size"] is False

    @patch("asciidoc_artisan.core.macos_file_ops.is_apfs_filesystem")
    def test_optimize_returns_dict(self, mock_is_apfs):
        """Test returns dictionary with all expected keys."""
        mock_is_apfs.return_value = True

        config = optimize_file_operations_for_macos("/tmp/test")

        assert isinstance(config, dict)
        assert len(config) == 4
        assert all(isinstance(v, bool) for v in config.values())


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_apfs_clone_with_special_chars_in_path(self, mock_run):
        """Test cloning with special characters in path."""
        mock_run.return_value = MagicMock(returncode=0)

        result = apfs_clone_file("/tmp/file with spaces.txt", "/tmp/dest & copy.txt")

        assert result is True

    def test_atomic_write_empty_content(self):
        """Test atomic write with empty content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "empty.txt")

            result = apfs_atomic_write(file_path, "")

            assert result is True
            assert os.path.exists(file_path)
            with open(file_path, "r") as f:
                assert f.read() == ""

    @patch("asciidoc_artisan.core.macos_file_ops.subprocess.run")
    def test_directory_size_empty_directory(self, mock_run):
        """Test directory size for empty directory."""
        mock_run.return_value = MagicMock(
            stdout="0\t/tmp/empty\n",
            returncode=0,
        )

        result = apfs_fast_directory_size("/tmp/empty")

        assert result == 0
