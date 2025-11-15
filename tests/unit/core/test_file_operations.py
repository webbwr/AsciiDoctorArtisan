"""
Unit tests for file operations and data integrity.
"""

import tempfile
from pathlib import Path

import pytest

from asciidoc_artisan.core import atomic_save_json, atomic_save_text, sanitize_path



@pytest.mark.fr_007
@pytest.mark.fr_068
@pytest.mark.fr_069
@pytest.mark.unit
class TestFileOperations:
    """Test file I/O operations for data integrity.

    FR-007: Save Files
    FR-069: Atomic Writes
    """

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

            file_path.write_text("Original content", encoding="utf-8")
            assert file_path.read_text(encoding="utf-8") == "Original content"

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
                "nested": {"key": "value"},
            }

            result = atomic_save_json(file_path, data)

            assert result is True
            assert file_path.exists()

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

            assert "  " in content
            assert "\\n" in repr(content)

    def test_atomic_save_text_none_path(self):
        """Test atomic_save_text handles None path."""
        result = atomic_save_text(None, "content")
        assert result is False

    def test_atomic_save_json_none_path(self):
        """Test atomic_save_json handles None path."""
        result = atomic_save_json(None, {"key": "value"})
        assert result is False

    def test_atomic_save_text_write_error(self):
        """Test atomic_save_text handles write errors gracefully."""
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a read-only directory
            readonly_dir = Path(tmpdir) / "readonly"
            readonly_dir.mkdir()
            os.chmod(readonly_dir, 0o444)  # Read-only

            invalid_path = readonly_dir / "test.txt"
            result = atomic_save_text(invalid_path, "content")
            assert result is False

            # Cleanup: restore permissions
            os.chmod(readonly_dir, 0o755)

    def test_atomic_save_json_write_error(self):
        """Test atomic_save_json handles write errors gracefully."""
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a read-only directory
            readonly_dir = Path(tmpdir) / "readonly"
            readonly_dir.mkdir()
            os.chmod(readonly_dir, 0o444)  # Read-only

            invalid_path = readonly_dir / "test.json"
            result = atomic_save_json(invalid_path, {"key": "value"})
            assert result is False

            # Cleanup: restore permissions
            os.chmod(readonly_dir, 0o755)


@pytest.mark.fr_070
@pytest.mark.security
@pytest.mark.unit
class TestPathSanitization:
    """Test path sanitization security features.

    FR-070: Path Sanitization
    Security requirement: Prevent directory traversal attacks
    """

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
        # SECURITY TEST: Verify Issue #8 fix - paths with '..' are blocked BEFORE resolve()
        dangerous_paths = [
            "../../../etc/passwd",
            "test/../../secret",
            "/home/../etc/shadow",
            "../../etc/passwd",
            "/tmp/../../../etc/passwd",
            "/home/user/../../etc/passwd",
        ]

        for dangerous_path in dangerous_paths:
            result = sanitize_path(dangerous_path)
            # After fix, all paths with '..' should be blocked (return None)
            assert result is None, f"Dangerous path not blocked: {dangerous_path}"

    def test_sanitize_path_handles_path_objects(self):
        """Test sanitize_path accepts Path objects."""
        path = Path.home() / "test.txt"
        result = sanitize_path(path)

        assert result is not None
        assert isinstance(result, Path)

    def test_sanitize_path_rejects_parent_traversal(self):
        """Test sanitize_path detects and rejects parent directory traversal."""
        # SECURITY TEST: This path contains '..' and should be blocked
        dangerous_path = "/home/user/documents/../../etc/passwd"
        result = sanitize_path(dangerous_path)
        # After fix, should be blocked (return None)
        assert result is None, f"Parent traversal not blocked: {dangerous_path}"

    def test_sanitize_path_invalid_input(self):
        """Test sanitize_path handles invalid input gracefully."""
        # Test with invalid types that will cause exception
        result = sanitize_path("\x00invalid")  # Null byte in path
        # Should return None on error
        assert result is None or isinstance(result, Path)

    def test_sanitize_path_blocks_dotdot_in_parts(self):
        """Test sanitize_path blocks paths with '..' in parts before resolution."""
        # SECURITY TEST: Verify '..' is detected in path.parts BEFORE resolve()
        test_path = "/some/path/../with/dotdot"
        result = sanitize_path(test_path)
        # Should return None because '..' is detected before resolve()
        assert result is None

    def test_sanitize_path_with_allowed_base(self):
        """Test sanitize_path with allowed_base parameter."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            safe_file = base_dir / "subdir" / "file.txt"
            outside_file = Path("/etc/passwd")

            # Path within allowed base should be accepted
            result = sanitize_path(str(safe_file), allowed_base=base_dir)
            assert result is not None
            assert result == safe_file.resolve()

            # Path outside allowed base should be rejected
            result = sanitize_path(str(outside_file), allowed_base=base_dir)
            assert result is None

    def test_sanitize_path_traversal_with_allowed_base(self):
        """Test sanitize_path blocks traversal even with allowed_base."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            # Try to escape using '..'
            dangerous_path = str(base_dir / ".." / ".." / "etc" / "passwd")

            result = sanitize_path(dangerous_path, allowed_base=base_dir)
            # Should be blocked due to '..' in path
            assert result is None

    def test_atomic_save_text_cleanup_on_exception(self):
        """Test atomic_save_text cleans up temp file when exception occurs."""
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            temp_path = file_path.with_suffix(file_path.suffix + ".tmp")

            # Create a mock that allows write_text but fails on replace
            def mock_replace(self, target):
                # Create the temp file so cleanup path is triggered
                self.write_text("temp content")
                raise PermissionError("Mock error during replace")

            with patch.object(Path, "replace", mock_replace):
                result = atomic_save_text(file_path, "test content")

                # Operation should fail
                assert result is False

                # Temp file should be cleaned up (line 114)
                assert not temp_path.exists()

    def test_atomic_save_json_cleanup_on_exception(self):
        """Test atomic_save_json cleans up temp file when exception occurs."""
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            temp_path = file_path.with_suffix(file_path.suffix + ".tmp")

            # Create a mock that allows write_text but fails on replace
            def mock_replace(self, target):
                # Create the temp file so cleanup path is triggered
                self.write_text('{"test": "content"}')
                raise PermissionError("Mock error during replace")

            with patch.object(Path, "replace", mock_replace):
                result = atomic_save_json(file_path, {"key": "value"})

                # Operation should fail
                assert result is False

                # Temp file should be cleaned up (line 166)
                assert not temp_path.exists()
