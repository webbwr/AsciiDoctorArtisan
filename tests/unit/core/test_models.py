"""
Tests for core.models module.

Tests all data model classes and their behavior (Pydantic v2).
"""

import pytest
from pydantic import ValidationError

from asciidoc_artisan.core.models import ChatMessage, GitHubResult, GitResult, GitStatus


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
        assert (
            '"user_message":"Success"' in json_str
            or '"user_message": "Success"' in json_str
        )


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
        assert result.data == {
            "number": 42,
            "url": "https://github.com/user/repo/pull/42",
        }
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


class TestGitStatus:
    """Test suite for GitStatus Pydantic model."""

    def test_git_status_creation(self):
        """Test creating GitStatus with valid data."""
        status = GitStatus(
            branch="main",
            ahead_count=2,
            behind_count=0,
            modified_count=5,
            staged_count=3,
            untracked_count=1,
            has_conflicts=False,
            is_dirty=True,
        )

        assert status.branch == "main"
        assert status.ahead_count == 2
        assert status.behind_count == 0
        assert status.modified_count == 5
        assert status.staged_count == 3
        assert status.untracked_count == 1
        assert status.has_conflicts is False
        assert status.is_dirty is True

    def test_git_status_validation_negative_count(self):
        """Test that negative count is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            GitStatus(
                branch="main",
                ahead_count=-1,  # Should fail
                behind_count=0,
                modified_count=0,
                staged_count=0,
                untracked_count=0,
            )

        errors = exc_info.value.errors()
        assert any("count must be non-negative" in str(e) for e in errors)


class TestChatMessage:
    """Test suite for ChatMessage Pydantic model."""

    def test_chat_message_creation(self):
        """Test creating ChatMessage with valid data."""
        import time

        msg = ChatMessage(
            role="user",
            content="Hello, how are you?",
            timestamp=time.time(),
            model="llama2",
            context_mode="general",
        )

        assert msg.role == "user"
        assert msg.content == "Hello, how are you?"
        assert msg.timestamp > 0
        assert msg.model == "llama2"
        assert msg.context_mode == "general"

    def test_chat_message_validation_invalid_role(self):
        """Test that invalid role is rejected."""
        import time

        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(
                role="invalid",  # Should fail
                content="Hello",
                timestamp=time.time(),
                model="llama2",
                context_mode="general",
            )

        errors = exc_info.value.errors()
        assert any("role must be one of" in str(e) for e in errors)

    def test_chat_message_validation_empty_content(self):
        """Test that empty content is rejected."""
        import time

        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(
                role="user",
                content="",  # Should fail
                timestamp=time.time(),
                model="llama2",
                context_mode="general",
            )

        errors = exc_info.value.errors()
        assert any("content cannot be empty" in str(e) for e in errors)

    def test_chat_message_validation_whitespace_only_content(self):
        """Test that whitespace-only content is rejected."""
        import time

        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(
                role="user",
                content="   ",  # Should fail
                timestamp=time.time(),
                model="llama2",
                context_mode="general",
            )

        errors = exc_info.value.errors()
        assert any("content cannot be empty" in str(e) for e in errors)

    def test_chat_message_validation_negative_timestamp(self):
        """Test that negative timestamp is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(
                role="user",
                content="Hello",
                timestamp=-1.0,  # Should fail
                model="llama2",
                context_mode="general",
            )

        errors = exc_info.value.errors()
        assert any("timestamp must be non-negative" in str(e) for e in errors)

    def test_chat_message_validation_invalid_context_mode(self):
        """Test that invalid context mode is rejected."""
        import time

        with pytest.raises(ValidationError) as exc_info:
            ChatMessage(
                role="user",
                content="Hello",
                timestamp=time.time(),
                model="llama2",
                context_mode="invalid",  # Should fail
            )

        errors = exc_info.value.errors()
        assert any("context_mode must be one of" in str(e) for e in errors)

    def test_chat_message_valid_roles(self):
        """Test all valid role values."""
        import time

        for role in ["user", "assistant"]:
            msg = ChatMessage(
                role=role,
                content="Test message",
                timestamp=time.time(),
                model="llama2",
                context_mode="general",
            )
            assert msg.role == role

    def test_chat_message_valid_context_modes(self):
        """Test all valid context mode values."""
        import time

        for mode in ["document", "syntax", "general", "editing"]:
            msg = ChatMessage(
                role="user",
                content="Test message",
                timestamp=time.time(),
                model="llama2",
                context_mode=mode,
            )
            assert msg.context_mode == mode

    def test_chat_message_content_stripped(self):
        """Test that content is stripped of whitespace."""
        import time

        msg = ChatMessage(
            role="user",
            content="  Hello world  ",
            timestamp=time.time(),
            model="llama2",
            context_mode="general",
        )
        assert msg.content == "Hello world"

    def test_chat_message_as_dict(self):
        """Test converting ChatMessage to dictionary."""
        import time

        timestamp = time.time()
        msg = ChatMessage(
            role="user",
            content="Test",
            timestamp=timestamp,
            model="llama2",
            context_mode="general",
        )
        msg_dict = msg.model_dump()

        assert isinstance(msg_dict, dict)
        assert msg_dict["role"] == "user"
        assert msg_dict["content"] == "Test"
        assert msg_dict["timestamp"] == timestamp
        assert msg_dict["model"] == "llama2"
        assert msg_dict["context_mode"] == "general"


@pytest.mark.unit
class TestCompletionItem:
    """Test CompletionItem model (v2.0.0+ auto-complete)."""

    def test_completion_item_creation(self):
        """Test creating a CompletionItem."""
        from asciidoc_artisan.core.models import CompletionItem, CompletionKind

        item = CompletionItem(
            text="= Heading",
            kind=CompletionKind.SYNTAX,
            detail="Level 1 heading",
            score=95.0,
        )

        assert item.text == "= Heading"
        assert item.kind == CompletionKind.SYNTAX
        assert item.detail == "Level 1 heading"
        assert item.score == 95.0

    def test_completion_item_validation_empty_text(self):
        """Test CompletionItem validates empty text (lines 417-419)."""
        from asciidoc_artisan.core.models import CompletionItem, CompletionKind

        with pytest.raises(ValueError, match="Field cannot be empty"):
            CompletionItem(text="", kind=CompletionKind.SYNTAX, detail="Test")

    def test_completion_item_validation_whitespace_text(self):
        """Test CompletionItem validates whitespace-only text (lines 417-419)."""
        from asciidoc_artisan.core.models import CompletionItem, CompletionKind

        with pytest.raises(ValueError, match="Field cannot be empty"):
            CompletionItem(text="   ", kind=CompletionKind.SYNTAX, detail="Test")

    def test_completion_item_validation_empty_detail(self):
        """Test CompletionItem validates empty detail (lines 417-419)."""
        from asciidoc_artisan.core.models import CompletionItem, CompletionKind

        with pytest.raises(ValueError, match="Field cannot be empty"):
            CompletionItem(text="Test", kind=CompletionKind.SYNTAX, detail="")

    def test_completion_item_validation_score_too_low(self):
        """Test CompletionItem validates score below 0 (lines 425-427)."""
        from asciidoc_artisan.core.models import CompletionItem, CompletionKind

        with pytest.raises(ValueError, match="score must be between 0 and 100"):
            CompletionItem(
                text="Test", kind=CompletionKind.SYNTAX, detail="Detail", score=-1.0
            )

    def test_completion_item_validation_score_too_high(self):
        """Test CompletionItem validates score above 100 (lines 425-427)."""
        from asciidoc_artisan.core.models import CompletionItem, CompletionKind

        with pytest.raises(ValueError, match="score must be between 0 and 100"):
            CompletionItem(
                text="Test", kind=CompletionKind.SYNTAX, detail="Detail", score=101.0
            )

    def test_completion_item_post_init_defaults(self):
        """Test CompletionItem sets default values in post_init (lines 431-436)."""
        from asciidoc_artisan.core.models import CompletionItem, CompletionKind

        item = CompletionItem(text="= Heading", kind=CompletionKind.SYNTAX, detail="Desc")

        # Defaults should be set to text value
        assert item.insert_text == "= Heading"
        assert item.sort_text == "= Heading"
        assert item.filter_text == "= Heading"

    def test_completion_item_post_init_preserves_custom_values(self):
        """Test CompletionItem preserves custom values in post_init (lines 431-436)."""
        from asciidoc_artisan.core.models import CompletionItem, CompletionKind

        item = CompletionItem(
            text="= Heading",
            kind=CompletionKind.SYNTAX,
            detail="Desc",
            insert_text="=",  # Will be stripped due to str_strip_whitespace
            sort_text="AAA",
            filter_text="heading",
        )

        # Custom values should be preserved (note: trailing whitespace stripped)
        assert item.insert_text == "="
        assert item.sort_text == "AAA"
        assert item.filter_text == "heading"


@pytest.mark.unit
class TestCompletionContext:
    """Test CompletionContext model (v2.0.0+ auto-complete)."""

    def test_completion_context_creation(self):
        """Test creating a CompletionContext."""
        from asciidoc_artisan.core.models import CompletionContext

        context = CompletionContext(
            line="= Heading", prefix="= ", line_number=0, column=2
        )

        assert context.line == "= Heading"
        assert context.prefix == "="  # Trailing whitespace stripped by str_strip_whitespace
        assert context.line_number == 0
        assert context.column == 2

    def test_completion_context_validation_negative_line(self):
        """Test CompletionContext validates negative line_number (lines 488-490)."""
        from asciidoc_artisan.core.models import CompletionContext

        with pytest.raises(ValueError, match="Value must be non-negative"):
            CompletionContext(line="Test", prefix="", line_number=-1, column=0)

    def test_completion_context_validation_negative_column(self):
        """Test CompletionContext validates negative column (lines 488-490)."""
        from asciidoc_artisan.core.models import CompletionContext

        with pytest.raises(ValueError, match="Value must be non-negative"):
            CompletionContext(line="Test", prefix="", line_number=0, column=-1)

    def test_completion_context_word_before_cursor(self):
        """Test CompletionContext.word_before_cursor property (lines 495-496)."""
        from asciidoc_artisan.core.models import CompletionContext

        context = CompletionContext(
            line="= This is heading", prefix="= This is ", line_number=0, column=10
        )

        assert context.word_before_cursor == "is"

    def test_completion_context_word_before_cursor_empty(self):
        """Test CompletionContext.word_before_cursor with empty prefix (lines 495-496)."""
        from asciidoc_artisan.core.models import CompletionContext

        context = CompletionContext(line="Test", prefix="", line_number=0, column=0)

        assert context.word_before_cursor == ""


@pytest.mark.unit
class TestTextEdit:
    """Test TextEdit model (v2.0.0+ quick fixes)."""

    def test_text_edit_creation(self):
        """Test creating a TextEdit."""
        from asciidoc_artisan.core.models import TextEdit

        edit = TextEdit(
            start_line=0, start_column=0, end_line=0, end_column=5, new_text="= Heading"
        )

        assert edit.start_line == 0
        assert edit.start_column == 0
        assert edit.end_line == 0
        assert edit.end_column == 5
        assert edit.new_text == "= Heading"

    def test_text_edit_validation_negative_positions(self):
        """Test TextEdit validates negative positions (lines 548-550)."""
        from asciidoc_artisan.core.models import TextEdit

        with pytest.raises(ValueError, match="Position must be non-negative"):
            TextEdit(
                start_line=-1, start_column=0, end_line=0, end_column=0, new_text="Test"
            )


@pytest.mark.unit
class TestQuickFix:
    """Test QuickFix model (v2.0.0+ quick fixes)."""

    def test_quick_fix_creation(self):
        """Test creating a QuickFix."""
        from asciidoc_artisan.core.models import QuickFix, TextEdit

        fix = QuickFix(
            title="Add closing delimiter",
            edits=[
                TextEdit(
                    start_line=0,
                    start_column=0,
                    end_line=0,
                    end_column=0,
                    new_text="----\n",
                )
            ],
        )

        assert fix.title == "Add closing delimiter"
        assert len(fix.edits) == 1

    def test_quick_fix_validation_empty_title(self):
        """Test QuickFix validates empty title (lines 595-597)."""
        from asciidoc_artisan.core.models import QuickFix

        with pytest.raises(ValueError, match="title cannot be empty"):
            QuickFix(title="", edits=[])


@pytest.mark.unit
class TestSyntaxErrorModel:
    """Test SyntaxErrorModel (v2.0.0+ syntax checking)."""

    def test_syntax_error_model_creation(self):
        """Test creating a SyntaxErrorModel."""
        from asciidoc_artisan.core.models import ErrorSeverity, SyntaxErrorModel

        error = SyntaxErrorModel(
            code="E001",
            severity=ErrorSeverity.ERROR,
            message="Missing closing delimiter",
            line=10,
            column=5,
            length=4,
        )

        assert error.code == "E001"
        assert error.severity == ErrorSeverity.ERROR
        assert error.message == "Missing closing delimiter"
        assert error.line == 10

    def test_syntax_error_model_validation_invalid_code_length(self):
        """Test SyntaxErrorModel validates code length (lines 655-661)."""
        from asciidoc_artisan.core.models import ErrorSeverity, SyntaxErrorModel

        with pytest.raises(ValueError, match="code must be 4 characters"):
            SyntaxErrorModel(
                code="E1",
                severity=ErrorSeverity.ERROR,
                message="Test",
                line=0,
                column=0,
                length=1,
            )

    def test_syntax_error_model_validation_invalid_code_prefix(self):
        """Test SyntaxErrorModel validates code prefix (lines 655-661)."""
        from asciidoc_artisan.core.models import ErrorSeverity, SyntaxErrorModel

        with pytest.raises(ValueError, match="code must start with E, W, or I"):
            SyntaxErrorModel(
                code="X001",
                severity=ErrorSeverity.ERROR,
                message="Test",
                line=0,
                column=0,
                length=1,
            )

    def test_syntax_error_model_validation_invalid_code_suffix(self):
        """Test SyntaxErrorModel validates code suffix (lines 655-661)."""
        from asciidoc_artisan.core.models import ErrorSeverity, SyntaxErrorModel

        with pytest.raises(ValueError, match="code must end with 3 digits"):
            SyntaxErrorModel(
                code="E00X",
                severity=ErrorSeverity.ERROR,
                message="Test",
                line=0,
                column=0,
                length=1,
            )

    def test_syntax_error_model_validation_empty_message(self):
        """Test SyntaxErrorModel validates empty message (lines 667-669)."""
        from asciidoc_artisan.core.models import ErrorSeverity, SyntaxErrorModel

        with pytest.raises(ValueError, match="message cannot be empty"):
            SyntaxErrorModel(
                code="E001",
                severity=ErrorSeverity.ERROR,
                message="",
                line=0,
                column=0,
                length=1,
            )

    def test_syntax_error_model_validation_negative_position(self):
        """Test SyntaxErrorModel validates negative positions (lines 675-677)."""
        from asciidoc_artisan.core.models import ErrorSeverity, SyntaxErrorModel

        with pytest.raises(ValueError, match="Position must be non-negative"):
            SyntaxErrorModel(
                code="E001",
                severity=ErrorSeverity.ERROR,
                message="Test",
                line=-1,
                column=0,
                length=1,
            )


@pytest.mark.unit
class TestTemplateVariable:
    """Test TemplateVariable model (v2.0.0+ templates)."""

    def test_template_variable_creation(self):
        """Test creating a TemplateVariable."""
        from asciidoc_artisan.core.models import TemplateVariable

        var = TemplateVariable(
            name="title", description="Document title", required=True, type="string"
        )

        assert var.name == "title"
        assert var.description == "Document title"
        assert var.required is True
        assert var.type == "string"

    def test_template_variable_validation_empty_name(self):
        """Test TemplateVariable validates empty name (lines 721-723)."""
        from asciidoc_artisan.core.models import TemplateVariable

        with pytest.raises(ValueError, match="Field cannot be empty"):
            TemplateVariable(name="", description="Test")

    def test_template_variable_validation_empty_description(self):
        """Test TemplateVariable validates empty description (lines 721-723)."""
        from asciidoc_artisan.core.models import TemplateVariable

        with pytest.raises(ValueError, match="Field cannot be empty"):
            TemplateVariable(name="test", description="")

    def test_template_variable_validation_invalid_type(self):
        """Test TemplateVariable validates invalid type (lines 729-732)."""
        from asciidoc_artisan.core.models import TemplateVariable

        with pytest.raises(ValueError, match="type must be one of"):
            TemplateVariable(name="test", description="Test", type="invalid")


@pytest.mark.unit
class TestTemplate:
    """Test Template model (v2.0.0+ templates)."""

    def test_template_creation(self):
        """Test creating a Template."""
        from asciidoc_artisan.core.models import Template

        template = Template(
            name="Article", category="Document", description="Standard article template"
        )

        assert template.name == "Article"
        assert template.category == "Document"
        assert template.description == "Standard article template"

    def test_template_validation_empty_name(self):
        """Test Template validates empty name (lines 790-792)."""
        from asciidoc_artisan.core.models import Template

        with pytest.raises(ValueError, match="Field cannot be empty"):
            Template(name="", category="Test", description="Test")

    def test_template_validation_empty_category(self):
        """Test Template validates empty category (lines 790-792)."""
        from asciidoc_artisan.core.models import Template

        with pytest.raises(ValueError, match="Field cannot be empty"):
            Template(name="Test", category="", description="Test")

    def test_template_validation_empty_description(self):
        """Test Template validates empty description (lines 790-792)."""
        from asciidoc_artisan.core.models import Template

        with pytest.raises(ValueError, match="Field cannot be empty"):
            Template(name="Test", category="Test", description="")
