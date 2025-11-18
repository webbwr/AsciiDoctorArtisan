"""
Core data models for AsciiDoc Artisan.

This module contains simple data structures used throughout the application:
- GitResult: Result of Git operations
- GitStatus: Git repository status information (v1.9.0+)
- GitHubResult: Result of GitHub CLI operations
- ChatMessage: Single message in Ollama AI chat conversation
- CompletionItem: Auto-complete completion item (v2.0.0+)
- SyntaxError: Syntax checking error with quick fixes (v2.0.0+)
- Template: Document template with variables (v2.0.0+)
- Additional models as needed

These models use Pydantic for runtime validation and type safety (v1.7.0+).
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class GitResult(BaseModel):
    """
    Result of a Git operation execution.

    Used by GitWorker to communicate the outcome of Git commands
    back to the main UI thread.

    Attributes:
        success: True if Git command completed successfully
        stdout: Standard output from Git command
        stderr: Standard error from Git command
        exit_code: Process exit code (None if not executed)
        user_message: Human-readable message for status bar display

    Validation:
        - user_message cannot be empty when provided
        - exit_code must be non-negative if provided

    Example:
        ```python
        # Successful operation
        result = GitResult(
            success=True,
            stdout="On branch main\\nYour branch is up to date",
            stderr="",
            exit_code=0,
            user_message="Git status retrieved successfully"
        )

        # Failed operation
        result = GitResult(
            success=False,
            stdout="",
            stderr="fatal: not a git repository",
            exit_code=128,
            user_message="Not a Git repository"
        )
        ```
    """

    success: bool = Field(..., description="True if operation succeeded")
    stdout: str = Field(default="", description="Standard output from Git command")
    stderr: str = Field(default="", description="Standard error from Git command")
    exit_code: int | None = Field(default=None, description="Process exit code (-1 for errors/cancelled)")
    user_message: str = Field(..., description="Human-readable status message")

    @field_validator("user_message")
    @classmethod
    def validate_user_message(cls, v: str) -> str:
        """Ensure user message is not empty."""
        if not v or not v.strip():
            raise ValueError("user_message cannot be empty")
        return v.strip()

    model_config = {
        "frozen": False,  # Allow mutation for compatibility
        "validate_assignment": True,  # Validate on field assignment
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }


class GitStatus(BaseModel):
    """
    Git repository status information.

    Used by GitWorker to provide real-time repository status updates
    for display in the status bar.

    Attributes:
        branch: Current branch name
        modified_count: Number of modified files (working tree)
        staged_count: Number of staged files (index)
        untracked_count: Number of untracked files
        has_conflicts: Whether merge conflicts exist
        ahead_count: Number of commits ahead of remote
        behind_count: Number of commits behind remote
        is_dirty: Whether working tree has uncommitted changes

    Validation:
        - branch cannot be empty
        - All count fields must be non-negative

    Example:
        ```python
        # Clean repository
        status = GitStatus(
            branch="main",
            modified_count=0,
            staged_count=0,
            untracked_count=0,
            has_conflicts=False,
            ahead_count=0,
            behind_count=0,
            is_dirty=False
        )

        # Dirty repository with changes
        status = GitStatus(
            branch="feature/git-improvements",
            modified_count=3,
            staged_count=1,
            untracked_count=2,
            has_conflicts=False,
            ahead_count=2,
            behind_count=0,
            is_dirty=True
        )
        ```
    """

    branch: str = Field(default="", description="Current branch name")
    modified_count: int = Field(default=0, description="Number of modified files")
    staged_count: int = Field(default=0, description="Number of staged files")
    untracked_count: int = Field(default=0, description="Number of untracked files")
    has_conflicts: bool = Field(default=False, description="Whether conflicts exist")
    ahead_count: int = Field(default=0, description="Commits ahead of remote")
    behind_count: int = Field(default=0, description="Commits behind remote")
    is_dirty: bool = Field(default=False, description="Whether working tree has uncommitted changes")

    @field_validator(
        "modified_count",
        "staged_count",
        "untracked_count",
        "ahead_count",
        "behind_count",
    )
    @classmethod
    def validate_count(cls, v: int) -> int:
        """Ensure count is non-negative."""
        if v < 0:
            raise ValueError("count must be non-negative")
        return v

    model_config = {
        "frozen": False,  # Allow mutation for compatibility
        "validate_assignment": True,  # Validate on field assignment
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }


class GitHubResult(BaseModel):
    """
    Result of a GitHub CLI operation execution.

    Used by GitHubCLIWorker to communicate the outcome of GitHub CLI commands
    back to the main UI thread.

    Attributes:
        success: True if GitHub CLI command completed successfully
        data: Parsed JSON data from GitHub CLI output (None if failed or no JSON)
        error: Error message from GitHub CLI standard error
        user_message: Human-readable message for status bar display
        operation: Operation type (e.g., "pr_create", "issue_list", "repo_view")

    Validation:
        - operation must be one of the allowed operation types
        - user_message cannot be empty when provided
        - data must be present when success=True for most operations

    Example:
        ```python
        # Successful PR creation
        result = GitHubResult(
            success=True,
            data={"number": 42, "url": "https://github.com/user/repo/pull/42"},
            error="",
            user_message="Pull request #42 created successfully",
            operation="pr_create"
        )

        # Failed authentication
        result = GitHubResult(
            success=False,
            data=None,
            error="not logged into any GitHub hosts",
            user_message="Not authenticated. Run 'gh auth login' in terminal.",
            operation="pr_list"
        )
        ```
    """

    success: bool = Field(..., description="True if operation succeeded")
    data: dict[str, Any] | list[dict[str, Any]] | None = Field(
        default=None,
        description="Parsed JSON data from GitHub CLI (dict for single results, list for list operations)",
    )
    error: str = Field(default="", description="Error message from GitHub CLI")
    user_message: str = Field(..., description="Human-readable status message")
    operation: str = Field(..., description="Operation type identifier")

    @field_validator("user_message")
    @classmethod
    def validate_user_message(cls, v: str) -> str:
        """Ensure user message is not empty."""
        if not v or not v.strip():
            raise ValueError("user_message cannot be empty")
        return v.strip()

    @field_validator("operation")
    @classmethod
    def validate_operation(cls, v: str) -> str:
        """Validate operation type is known."""
        allowed_operations = {
            # Specific operations (full names)
            "pr_create",
            "pr_list",
            "issue_create",
            "issue_list",
            "repo_view",
            "repo_info",
            # Generic subcommands (from args[0])
            "pr",
            "issue",
            "repo",
            "gh",
            # Special operations
            "cancelled",
            "unknown",
        }
        if v not in allowed_operations:
            raise ValueError(f"Unknown operation: {v}. Must be one of {allowed_operations}")
        return v

    model_config = {
        "frozen": False,  # Allow mutation for compatibility
        "validate_assignment": True,  # Validate on field assignment
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }


class ChatMessage(BaseModel):
    """
    Single message in an Ollama AI chat conversation.

    Used by OllamaChatWorker and ChatManager to represent both user messages
    and AI responses in the chat history.

    Attributes:
        role: Message sender ("user" or "assistant")
        content: Message text content
        timestamp: Unix timestamp when message was created
        model: Name of Ollama model that generated this message (for assistant messages)
        context_mode: Interaction mode when message was sent

    Validation:
        - role must be "user" or "assistant"
        - content cannot be empty
        - timestamp must be non-negative
        - context_mode must be one of allowed modes

    Example:
        ```python
        import time

        # User message
        user_msg = ChatMessage(
            role="user",
            content="How do I create a table in AsciiDoc?",
            timestamp=time.time(),
            model="gnokit/improve-grammer",
            context_mode="syntax"
        )

        # AI response
        ai_msg = ChatMessage(
            role="assistant",
            content="Here's how to create a table:\\n|===\\n|Header 1 |Header 2\\n|Cell 1   |Cell 2\\n|===",
            timestamp=time.time(),
            model="gnokit/improve-grammer",
            context_mode="syntax"
        )
        ```
    """

    role: str = Field(..., description='Message sender: "user" or "assistant"')
    content: str = Field(..., description="Message text content")
    timestamp: float = Field(..., description="Unix timestamp when message was created")
    model: str = Field(..., description="Ollama model name (e.g., gnokit/improve-grammer)")
    context_mode: str = Field(..., description='Context mode: "document", "syntax", "general", or "editing"')

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Ensure role is either user or assistant."""
        allowed_roles = {"user", "assistant"}
        if v not in allowed_roles:
            raise ValueError(f"role must be one of {allowed_roles}, got '{v}'")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v.strip()

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: float) -> float:
        """Ensure timestamp is non-negative."""
        if v < 0:
            raise ValueError("timestamp must be non-negative")
        return v

    @field_validator("context_mode")
    @classmethod
    def validate_context_mode(cls, v: str) -> str:
        """Validate context mode is known."""
        allowed_modes = {"document", "syntax", "general", "editing"}
        if v not in allowed_modes:
            raise ValueError(f"context_mode must be one of {allowed_modes}, got '{v}'")
        return v

    model_config = {
        "frozen": False,  # Allow mutation for compatibility
        "validate_assignment": True,  # Validate on field assignment
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }


# ============================================================================
# v2.0.0 Models: Auto-Complete, Syntax Checking, Templates
# ============================================================================


class CompletionKind(str, Enum):
    """Type of auto-complete completion item (v2.0.0+)."""

    SYNTAX = "syntax"  # AsciiDoc syntax elements (headings, lists, blocks)
    ATTRIBUTE = "attribute"  # Document attributes (:author:, :version:)
    XREF = "xref"  # Cross-references (<<anchor>>)
    INCLUDE = "include"  # Include paths (include::file[])
    SNIPPET = "snippet"  # Expandable code snippets


class CompletionItem(BaseModel):
    """
    Auto-complete completion item (v2.0.0+).

    Represents a single completion suggestion shown in the auto-complete popup.

    Attributes:
        text: Display text shown in completion list
        kind: Type of completion (syntax, attribute, etc.)
        detail: Short one-line description
        documentation: Full documentation (markdown format)
        insert_text: Text to insert when selected (defaults to text)
        sort_text: Custom sort key (defaults to text)
        filter_text: Custom filter key for matching (defaults to text)
        score: Ranking score (0-100, higher is better)

    Example:
        ```python
        item = CompletionItem(
            text="= Heading",
            kind=CompletionKind.SYNTAX,
            detail="Level 1 heading (document title)",
            documentation="# Level 1 Heading\\n\\nUsed for document title.",
            insert_text="= ",
            score=95.0
        )
        ```
    """

    text: str = Field(..., description="Display text")
    kind: CompletionKind = Field(..., description="Completion type")
    detail: str = Field(default="", description="Short description")
    documentation: str = Field(default="", description="Full documentation (markdown)")
    insert_text: str | None = Field(default=None, description="Text to insert (defaults to text)")
    sort_text: str | None = Field(default=None, description="Custom sort key (defaults to text)")
    filter_text: str | None = Field(default=None, description="Custom filter key (defaults to text)")
    score: float = Field(default=0.0, description="Ranking score (0-100)")

    @field_validator("text", "detail")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Ensure text and detail are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        """Ensure score is in valid range."""
        if not 0 <= v <= 100:
            raise ValueError("score must be between 0 and 100")
        return v

    def model_post_init(self, __context: Any) -> None:
        """Set defaults after initialization."""
        if self.insert_text is None:
            self.insert_text = self.text
        if self.sort_text is None:
            self.sort_text = self.text
        if self.filter_text is None:
            self.filter_text = self.text

    model_config = {
        "frozen": False,
        "validate_assignment": True,
        "str_strip_whitespace": True,
    }


class CompletionContext(BaseModel):
    """
    Context for auto-complete request (v2.0.0+).

    Contains information about the current editor state needed to
    provide relevant completions.

    Attributes:
        line: Current line text
        line_number: Line number (0-indexed)
        column: Cursor column position (0-indexed)
        prefix: Text before cursor on current line
        trigger_char: Character that triggered completion (:, [, etc.)
        manual: True if manually triggered with Ctrl+Space

    Example:
        ```python
        context = CompletionContext(
            line="== Introduction",
            line_number=5,
            column=15,
            prefix="== Introduction",
            trigger_char=None,
            manual=False
        )
        ```
    """

    line: str = Field(..., description="Current line text")
    line_number: int = Field(..., description="Line number (0-indexed)")
    column: int = Field(..., description="Cursor column (0-indexed)")
    prefix: str = Field(..., description="Text before cursor on current line")
    trigger_char: str | None = Field(default=None, description="Character that triggered completion")
    manual: bool = Field(default=False, description="Manually triggered with Ctrl+Space")

    @field_validator("line_number", "column")
    @classmethod
    def validate_non_negative(cls, v: int) -> int:
        """Ensure line_number and column are non-negative."""
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v

    @property
    def word_before_cursor(self) -> str:
        """Extract word before cursor."""
        words = self.prefix.split()
        return words[-1] if words else ""

    model_config = {
        "frozen": False,
        "validate_assignment": True,
        "str_strip_whitespace": True,
    }


class ErrorSeverity(str, Enum):
    """Severity level for syntax errors (v2.0.0+)."""

    ERROR = "error"  # Red - breaks document rendering
    WARNING = "warning"  # Yellow - semantic issues
    INFO = "info"  # Blue - style suggestions


class TextEdit(BaseModel):
    """
    Single text edit operation for quick fixes (v2.0.0+).

    Represents a change to be applied to the document.

    Attributes:
        start_line: Start line (0-indexed)
        start_column: Start column (0-indexed)
        end_line: End line (0-indexed)
        end_column: End column (0-indexed)
        new_text: Replacement text

    Example:
        ```python
        edit = TextEdit(
            start_line=10,
            start_column=0,
            end_line=10,
            end_column=5,
            new_text="= Heading"
        )
        ```
    """

    start_line: int = Field(..., description="Start line (0-indexed)")
    start_column: int = Field(..., description="Start column (0-indexed)")
    end_line: int = Field(..., description="End line (0-indexed)")
    end_column: int = Field(..., description="End column (0-indexed)")
    new_text: str = Field(..., description="Replacement text")

    @field_validator("start_line", "start_column", "end_line", "end_column")
    @classmethod
    def validate_non_negative(cls, v: int) -> int:
        """Ensure positions are non-negative."""
        if v < 0:
            raise ValueError("Position must be non-negative")
        return v

    model_config = {
        "frozen": False,
        "validate_assignment": True,
        "str_strip_whitespace": True,
    }


class QuickFix(BaseModel):
    """
    Quick fix suggestion for syntax error (v2.0.0+).

    Provides a one-click fix for a detected syntax error.

    Attributes:
        title: Human-readable fix description
        edits: List of text edits to apply

    Example:
        ```python
        fix = QuickFix(
            title="Add closing delimiter",
            edits=[
                TextEdit(
                    start_line=10,
                    start_column=0,
                    end_line=10,
                    end_column=0,
                    new_text="----\\n"
                )
            ]
        )
        ```
    """

    title: str = Field(..., description="Fix description")
    edits: list[TextEdit] = Field(default_factory=list, description="Text edits to apply")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Ensure title is not empty."""
        if not v or not v.strip():
            raise ValueError("title cannot be empty")
        return v.strip()

    model_config = {
        "frozen": False,
        "validate_assignment": True,
        "str_strip_whitespace": True,
    }


class SyntaxErrorModel(BaseModel):
    """
    Syntax error with position and quick fixes (v2.0.0+).

    Represents a detected syntax, semantic, or style issue in the document.
    Named SyntaxErrorModel to avoid conflict with Python's built-in SyntaxError.

    Attributes:
        code: Error code (E001, W001, I001)
        severity: Error severity level
        message: Human-readable error message
        line: Line number (0-indexed)
        column: Column number (0-indexed)
        length: Error span length in characters
        fixes: List of suggested quick fixes

    Example:
        ```python
        error = SyntaxErrorModel(
            code="E001",
            severity=ErrorSeverity.ERROR,
            message="Unclosed source block (missing closing delimiter)",
            line=10,
            column=0,
            length=20,
            fixes=[
                QuickFix(
                    title="Add closing delimiter",
                    edits=[TextEdit(...)]
                )
            ]
        )
        ```
    """

    code: str = Field(..., description="Error code (E001, W001, I001)")
    severity: ErrorSeverity = Field(..., description="Error severity level")
    message: str = Field(..., description="Human-readable error message")
    line: int = Field(..., description="Line number (0-indexed)")
    column: int = Field(..., description="Column number (0-indexed)")
    length: int = Field(..., description="Error span length")
    fixes: list[QuickFix] = Field(default_factory=list, description="Quick fix suggestions")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Ensure error code follows pattern E###, W###, or I###."""
        if not v or len(v) != 4:
            raise ValueError("code must be 4 characters (e.g., E001, W001, I001)")
        if v[0] not in ("E", "W", "I"):
            raise ValueError("code must start with E, W, or I")
        if not v[1:].isdigit():
            raise ValueError("code must end with 3 digits")
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Ensure message is not empty."""
        if not v or not v.strip():
            raise ValueError("message cannot be empty")
        return v.strip()

    @field_validator("line", "column", "length")
    @classmethod
    def validate_non_negative(cls, v: int) -> int:
        """Ensure positions are non-negative."""
        if v < 0:
            raise ValueError("Position must be non-negative")
        return v

    model_config = {
        "frozen": False,
        "validate_assignment": True,
        "str_strip_whitespace": True,
    }


class TemplateVariable(BaseModel):
    """
    Template variable definition (v2.0.0+).

    Defines a variable that can be substituted in a template.

    Attributes:
        name: Variable name (used in {{name}} syntax)
        description: Help text shown to user
        required: True if variable must be provided
        default: Default value if not provided
        type: Variable type (string, boolean, number)

    Example:
        ```python
        var = TemplateVariable(
            name="title",
            description="Document title",
            required=True,
            default=None,
            type="string"
        )
        ```
    """

    name: str = Field(..., description="Variable name")
    description: str = Field(..., description="Help text")
    required: bool = Field(default=False, description="Required variable")
    default: str | None = Field(default=None, description="Default value")
    type: str = Field(default="string", description="Variable type")

    @field_validator("name", "description")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Ensure name and description are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Ensure type is valid."""
        allowed_types = {"string", "boolean", "number"}
        if v not in allowed_types:
            raise ValueError(f"type must be one of {allowed_types}")
        return v

    model_config = {
        "frozen": False,
        "validate_assignment": True,
        "str_strip_whitespace": True,
    }


class Template(BaseModel):
    """
    Document template with variables (v2.0.0+).

    Represents a reusable document template with variable substitution.

    Attributes:
        name: Template name
        category: Template category (article, book, report, etc.)
        description: Short description
        author: Template author
        version: Template version
        variables: List of variable definitions
        content: Template content (after YAML front matter)
        file_path: Source file path (optional)

    Example:
        ```python
        template = Template(
            name="Technical Article",
            category="article",
            description="Short technical article with abstract",
            author="AsciiDoc Artisan",
            version="1.0",
            variables=[
                TemplateVariable(name="title", description="Article title", required=True),
                TemplateVariable(name="author", description="Author name", default="Anonymous"),
            ],
            content="= {{title}}\\n{{author}}\\n...",
            file_path="/path/to/article.adoc"
        )
        ```
    """

    name: str = Field(..., description="Template name")
    category: str = Field(..., description="Template category")
    description: str = Field(..., description="Short description")
    author: str = Field(default="", description="Template author")
    version: str = Field(default="1.0", description="Template version")
    variables: list[TemplateVariable] = Field(default_factory=list, description="Variable definitions")
    content: str = Field(default="", description="Template content")
    file_path: str | None = Field(default=None, description="Source file path")

    @field_validator("name", "category", "description")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Ensure required fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    model_config = {
        "frozen": False,
        "validate_assignment": True,
        "str_strip_whitespace": True,
    }
