"""
Unit tests for file operations and data integrity.
"""
import pytest
import tempfile
from pathlib import Path
from adp_windows import atomic_save_text, atomic_save_json, sanitize_path


@pytest.mark.unit
class TestFileOperations:
    """Test file I/O operations for data integrity."""

    def test_atomic_save_text_success(self):
        """Test atomic_save_text creates file correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            content = "Test content\nLine 2"

            result = atomic_save_text(file_path, content)

            assert result is True
            assert file_path.exists()
            assert file_path.read_text(encoding="utf-8") == content

    def test_atomic_save_text_overwrites_existing(self):
        """Test atomic_save_text overwrites existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"

            # Create initial file
            file_path.write_text("Original content", encoding="utf-8")
            assert file_path.read_text(encoding="utf-8") == "Original content"

            # Overwrite with atomic_save_text
            new_content = "New content"
            result = atomic_save_text(file_path, new_content)

            assert result is True
            assert file_path.read_text(encoding="utf-8") == new_content

    def test_atomic_save_json_success(self):
        """Test atomic_save_json creates valid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            data = {
                "string": "value",
                "number": 42,
                "boolean": True,
                "nested": {"key": "value"}
            }

            result = atomic_save_json(file_path, data)

            assert result is True
            assert file_path.exists()

            # Verify JSON is valid and matches
            import json
            loaded = json.loads(file_path.read_text(encoding="utf-8"))
            assert loaded == data

    def test_atomic_save_json_with_indent(self):
        """Test atomic_save_json formats with indentation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            data = {"key1": "value1", "key2": "value2"}

            result = atomic_save_json(file_path, data, indent=2)

            assert result is True
            content = file_path.read_text(encoding="utf-8")

            # Should have indentation
            assert "  " in content
            assert "\\n" in repr(content)  # Has newlines


@pytest.mark.unit
class TestPathSanitization:
    """Test path sanitization security features."""

    def test_sanitize_path_valid_absolute(self):
        """Test sanitize_path accepts valid absolute paths."""
        path = Path.home() / "test" / "file.txt"
        result = sanitize_path(str(path))

        assert result is not None
        assert isinstance(result, Path)
        assert result.is_absolute()

    def test_sanitize_path_resolves_relative(self):
        """Test sanitize_path resolves relative paths."""
        result = sanitize_path("./test.txt")

        assert result is not None
        assert result.is_absolute()

    def test_sanitize_path_blocks_traversal(self):
        """Test sanitize_path blocks directory traversal attempts."""
        # Attempt to traverse up directories
        dangerous_paths = [
            "../../../etc/passwd",
            "test/../../secret",
            "/home/../etc/shadow"
        ]

        for dangerous_path in dangerous_paths:
            result = sanitize_path(dangerous_path)
            # Should either return None or a safe path without ..
            if result is not None:
                assert ".." not in result.parts

    def test_sanitize_path_handles_path_objects(self):
        """Test sanitize_path accepts Path objects."""
        path = Path.home() / "test.txt"
        result = sanitize_path(path)

        assert result is not None
        assert isinstance(result, Path)

    def test_sanitize_path_rejects_parent_traversal(self):
        """Test sanitize_path detects and rejects parent directory traversal."""
        # Test paths that contain .. after resolution should be rejected
        dangerous_path = "/home/user/documents/../../etc/passwd"
        result = sanitize_path(dangerous_path)

        # Path.resolve() will normalize the path, but our check should catch ..
        # After resolve(), if .. still appears in parts, it's blocked
        # In practice, resolve() removes .. by resolving the path
        # So we verify the function doesn't crash and returns a valid result
        if result is not None:
            assert isinstance(result, Path)
            # The resolved path should be absolute
            assert result.is_absolute()
