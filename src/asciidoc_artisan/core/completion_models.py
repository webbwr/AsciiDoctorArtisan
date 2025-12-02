"""
Auto-Complete Data Models (v2.0.0+).

Extracted from models.py for MA principle compliance.
Contains models for the auto-complete feature.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


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
