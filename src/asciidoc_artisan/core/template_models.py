"""
Template Data Models (v2.0.0+).

Extracted from models.py for MA principle compliance.
Contains models for document templates with variable substitution.
"""

from pydantic import BaseModel, Field, field_validator


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
