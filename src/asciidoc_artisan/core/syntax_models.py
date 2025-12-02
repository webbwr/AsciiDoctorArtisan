"""
Syntax Checking Data Models (v2.0.0+).

Extracted from models.py for MA principle compliance.
Contains models for syntax validation and quick fixes.
"""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


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
