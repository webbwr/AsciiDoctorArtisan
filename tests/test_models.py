"""
Tests for core.models module.

Tests all data model classes and their behavior.
"""

import pytest
from asciidoc_artisan.core.models import GitResult


class TestGitResult:
    """Test suite for GitResult model."""

    def test_git_result_creation_success(self):
        """Test creating a successful GitResult."""
        result = GitResult(
            success=True,
            stdout="Successfully committed",
            stderr="",
            exit_code=0,
            user_message="Commit successful"
        )

        assert result.success is True
        assert result.stdout == "Successfully committed"
        assert result.stderr == ""
        assert result.exit_code == 0
        assert result.user_message == "Commit successful"

    def test_git_result_creation_failure(self):
        """Test creating a failed GitResult."""
        result = GitResult(
            success=False,
            stdout="",
            stderr="fatal: not a git repository",
            exit_code=128,
            user_message="Git operation failed"
        )

        assert result.success is False
        assert result.stdout == ""
        assert result.stderr == "fatal: not a git repository"
        assert result.exit_code == 128
        assert result.user_message == "Git operation failed"

    def test_git_result_none_exit_code(self):
        """Test GitResult with None exit code."""
        result = GitResult(
            success=False,
            stdout="",
            stderr="Process not started",
            exit_code=None,
            user_message="Could not start Git"
        )

        assert result.exit_code is None
        assert result.success is False

    def test_git_result_is_named_tuple(self):
        """Test that GitResult behaves as a NamedTuple."""
        result = GitResult(
            success=True,
            stdout="output",
            stderr="",
            exit_code=0,
            user_message="Done"
        )

        # Named tuples are immutable
        with pytest.raises(AttributeError):
            result.success = False

        # Can be unpacked
        success, stdout, stderr, exit_code, user_message = result
        assert success is True
        assert stdout == "output"

    def test_git_result_attribute_access(self):
        """Test accessing GitResult attributes by name."""
        result = GitResult(
            success=True,
            stdout="test output",
            stderr="test error",
            exit_code=1,
            user_message="Test message"
        )

        # Access by attribute name
        assert result.success is True
        assert result.stdout == "test output"
        assert result.stderr == "test error"
        assert result.exit_code == 1
        assert result.user_message == "Test message"

    def test_git_result_indexing(self):
        """Test accessing GitResult fields by index."""
        result = GitResult(
            success=False,
            stdout="out",
            stderr="err",
            exit_code=2,
            user_message="msg"
        )

        # Named tuples support indexing
        assert result[0] is False  # success
        assert result[1] == "out"  # stdout
        assert result[2] == "err"  # stderr
        assert result[3] == 2  # exit_code
        assert result[4] == "msg"  # user_message

    def test_git_result_equality(self):
        """Test GitResult equality comparison."""
        result1 = GitResult(True, "out", "err", 0, "msg")
        result2 = GitResult(True, "out", "err", 0, "msg")
        result3 = GitResult(False, "out", "err", 1, "msg")

        assert result1 == result2
        assert result1 != result3

    def test_git_result_repr(self):
        """Test GitResult string representation."""
        result = GitResult(True, "stdout", "stderr", 0, "message")
        repr_str = repr(result)

        assert "GitResult" in repr_str
        assert "success=True" in repr_str
        assert "stdout='stdout'" in repr_str

    def test_git_result_as_dict(self):
        """Test converting GitResult to dictionary."""
        result = GitResult(True, "out", "err", 0, "msg")
        result_dict = result._asdict()

        assert isinstance(result_dict, dict)
        assert result_dict["success"] is True
        assert result_dict["stdout"] == "out"
        assert result_dict["stderr"] == "err"
        assert result_dict["exit_code"] == 0
        assert result_dict["user_message"] == "msg"

    def test_git_result_fields_attribute(self):
        """Test that GitResult has _fields attribute."""
        assert hasattr(GitResult, "_fields")
        assert GitResult._fields == ("success", "stdout", "stderr", "exit_code", "user_message")

    def test_git_result_with_multiline_output(self):
        """Test GitResult with multiline stdout/stderr."""
        multiline_out = "line1\nline2\nline3"
        multiline_err = "error1\nerror2"

        result = GitResult(
            success=True,
            stdout=multiline_out,
            stderr=multiline_err,
            exit_code=0,
            user_message="Multi-line output"
        )

        assert "\n" in result.stdout
        assert result.stdout.count("\n") == 2
        assert "\n" in result.stderr

    def test_git_result_with_empty_strings(self):
        """Test GitResult with empty stdout/stderr."""
        result = GitResult(
            success=True,
            stdout="",
            stderr="",
            exit_code=0,
            user_message="No output"
        )

        assert result.stdout == ""
        assert result.stderr == ""
        assert len(result.stdout) == 0

    def test_git_result_with_unicode(self):
        """Test GitResult with Unicode characters."""
        result = GitResult(
            success=True,
            stdout="✓ Success 中文",
            stderr="",
            exit_code=0,
            user_message="Unicode test 🚀"
        )

        assert "✓" in result.stdout
        assert "中文" in result.stdout
        assert "🚀" in result.user_message

    def test_git_result_type_annotations(self):
        """Test that GitResult has proper type annotations."""
        assert hasattr(GitResult, "__annotations__")
        annotations = GitResult.__annotations__

        assert "success" in annotations
        assert "stdout" in annotations
        assert "stderr" in annotations
        assert "exit_code" in annotations
        assert "user_message" in annotations
