"""
Tests for core.models module.

Tests all data model classes and their behavior (Pydantic v2).
"""

import pytest
from pydantic import ValidationError

from asciidoc_artisan.core.models import GitHubResult, GitResult


class TestGitResult:
    """Test suite for GitResult Pydantic model."""

    def test_git_result_creation_success(self):
        """Test creating a successful GitResult."""
        result = GitResult(
            success=True,
            stdout="Successfully committed",
            stderr="",
            exit_code=0,
            user_message="Commit successful",
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
            user_message="Git operation failed",
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
            user_message="Could not start Git",
        )

        assert result.exit_code is None
        assert result.success is False

    def test_git_result_is_pydantic_model(self):
        """Test that GitResult is a Pydantic BaseModel."""
        result = GitResult(
            success=True,
            stdout="output",
            stderr="",
            exit_code=0,
            user_message="Done",
        )

        # Pydantic models are mutable (unless frozen=True)
        result.success = False
        assert result.success is False

    def test_git_result_attribute_access(self):
        """Test accessing GitResult attributes by name."""
        result = GitResult(
            success=True,
            stdout="test output",
            stderr="test error",
            exit_code=1,
            user_message="Test message",
        )

        # Access by attribute name
        assert result.success is True
        assert result.stdout == "test output"
        assert result.stderr == "test error"
        assert result.exit_code == 1
        assert result.user_message == "Test message"

    def test_git_result_validation_empty_message(self):
        """Test that empty user_message is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            GitResult(
                success=True,
                stdout="out",
                stderr="",
                exit_code=0,
                user_message="",  # Should fail validation
            )

        errors = exc_info.value.errors()
        assert any("user_message" in str(e) for e in errors)

    def test_git_result_validation_whitespace_stripped(self):
        """Test that user_message whitespace is stripped."""
        result = GitResult(
            success=True,
            stdout="out",
            stderr="",
            exit_code=0,
            user_message="  Message with spaces  ",
        )

        assert result.user_message == "Message with spaces"

    def test_git_result_equality(self):
        """Test GitResult equality comparison."""
        result1 = GitResult(
            success=True,
            stdout="out",
            stderr="err",
            exit_code=0,
            user_message="msg",
        )
        result2 = GitResult(
            success=True,
            stdout="out",
            stderr="err",
            exit_code=0,
            user_message="msg",
        )
        result3 = GitResult(
            success=False,
            stdout="out",
            stderr="err",
            exit_code=1,
            user_message="msg",
        )

        assert result1 == result2
        assert result1 != result3

    def test_git_result_repr(self):
        """Test GitResult string representation."""
        result = GitResult(
            success=True,
            stdout="stdout",
            stderr="stderr",
            exit_code=0,
            user_message="message",
        )
        repr_str = repr(result)

        assert "GitResult" in repr_str
        assert "success=True" in repr_str

    def test_git_result_as_dict(self):
        """Test converting GitResult to dictionary using model_dump()."""
        result = GitResult(
            success=True,
            stdout="out",
            stderr="err",
            exit_code=0,
            user_message="msg",
        )
        result_dict = result.model_dump()

        assert isinstance(result_dict, dict)
        assert result_dict["success"] is True
        assert result_dict["stdout"] == "out"
        assert result_dict["stderr"] == "err"
        assert result_dict["exit_code"] == 0
        assert result_dict["user_message"] == "msg"

    def test_git_result_model_fields(self):
        """Test that GitResult has model_fields attribute (Pydantic v2)."""
        assert hasattr(GitResult, "model_fields")
        field_names = set(GitResult.model_fields.keys())
        assert field_names == {
            "success",
            "stdout",
            "stderr",
            "exit_code",
            "user_message",
        }

    def test_git_result_with_multiline_output(self):
        """Test GitResult with multiline stdout/stderr."""
        multiline_out = "line1\nline2\nline3"
        multiline_err = "error1\nerror2"

        result = GitResult(
            success=False,
            stdout=multiline_out,
            stderr=multiline_err,
            exit_code=1,
            user_message="Multi-line error",
        )

        assert "\n" in result.stdout
        assert "\n" in result.stderr
        assert result.stdout.count("\n") == 2
        assert result.stderr.count("\n") == 1

    def test_git_result_with_empty_strings(self):
        """Test GitResult with empty stdout/stderr (but valid user_message)."""
        result = GitResult(
            success=True,
            stdout="",
            stderr="",
            exit_code=0,
            user_message="No output",  # Valid message
        )

        assert result.stdout == ""
        assert result.stderr == ""
        assert result.user_message == "No output"

    def test_git_result_with_unicode(self):
        """Test GitResult with Unicode characters."""
        unicode_msg = "Commit with émojis 🎉 and ñoñó"

        result = GitResult(
            success=True,
            stdout="",
            stderr="",
            exit_code=0,
            user_message=unicode_msg,
        )

        assert result.user_message == unicode_msg

    def test_git_result_type_annotations(self):
        """Test that GitResult fields have correct type annotations."""
        fields = GitResult.model_fields
        assert fields["success"].annotation == bool
        assert fields["stdout"].annotation == str
        assert fields["stderr"].annotation == str
        # exit_code is Optional[int]
        assert fields["user_message"].annotation == str

    def test_git_result_default_values(self):
        """Test GitResult with default values for optional fields."""
        result = GitResult(success=True, user_message="Success")

        assert result.success is True
        assert result.stdout == ""  # Default
        assert result.stderr == ""  # Default
        assert result.exit_code is None  # Default
        assert result.user_message == "Success"

    def test_git_result_json_serialization(self):
        """Test GitResult JSON serialization."""
        result = GitResult(
            success=True,
            stdout="output",
            stderr="",
            exit_code=0,
            user_message="Success",
        )

        json_str = result.model_dump_json()
        assert isinstance(json_str, str)
        assert '"success":true' in json_str or '"success": true' in json_str
        assert '"user_message":"Success"' in json_str or '"user_message": "Success"' in json_str


class TestGitHubResult:
    """Test suite for GitHubResult Pydantic model."""

    def test_github_result_creation_success(self):
        """Test creating a successful GitHubResult."""
        result = GitHubResult(
            success=True,
            data={"number": 42, "url": "https://github.com/user/repo/pull/42"},
            error="",
            user_message="PR #42 created successfully",
            operation="pr_create",
        )

        assert result.success is True
        assert result.data == {"number": 42, "url": "https://github.com/user/repo/pull/42"}
        assert result.error == ""
        assert result.user_message == "PR #42 created successfully"
        assert result.operation == "pr_create"

    def test_github_result_creation_failure(self):
        """Test creating a failed GitHubResult."""
        result = GitHubResult(
            success=False,
            data=None,
            error="not logged into any GitHub hosts",
            user_message="Not authenticated. Run 'gh auth login' in terminal.",
            operation="pr_list",
        )

        assert result.success is False
        assert result.data is None
        assert result.error == "not logged into any GitHub hosts"

    def test_github_result_validation_empty_message(self):
        """Test that empty user_message is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            GitHubResult(
                success=True,
                data={},
                error="",
                user_message="",  # Should fail
                operation="pr_create",
            )

        errors = exc_info.value.errors()
        assert any("user_message" in str(e) for e in errors)

    def test_github_result_validation_invalid_operation(self):
        """Test that invalid operation type is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            GitHubResult(
                success=True,
                data={},
                error="",
                user_message="Done",
                operation="invalid_op",  # Should fail
            )

        errors = exc_info.value.errors()
        assert any("operation" in str(e) for e in errors)

    def test_github_result_valid_operations(self):
        """Test all valid operation types."""
        valid_ops = ["pr_create", "pr_list", "issue_create", "issue_list", "repo_view"]

        for op in valid_ops:
            result = GitHubResult(
                success=True,
                data={},
                error="",
                user_message="Test",
                operation=op,
            )
            assert result.operation == op

    def test_github_result_as_dict(self):
        """Test converting GitHubResult to dictionary."""
        result = GitHubResult(
            success=True,
            data={"key": "value"},
            error="",
            user_message="Success",
            operation="repo_view",
        )
        result_dict = result.model_dump()

        assert isinstance(result_dict, dict)
        assert result_dict["success"] is True
        assert result_dict["data"] == {"key": "value"}
        assert result_dict["operation"] == "repo_view"
