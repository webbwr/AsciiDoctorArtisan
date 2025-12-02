"""
Syntax validation rules for AsciiDoc Artisan (v2.0.0+).

This module provides validation rules for detecting syntax errors, semantic
issues, and style violations in AsciiDoc documents.

MA principle: Reduced from 621→95 lines by extracting rule modules.

Error Codes:
- E001-E050: Syntax errors (breaks document rendering)
- W001-W050: Warnings (semantic issues, broken links)
- I001-I050: Info/Style (suggestions, best practices)

Each validator implements the ValidationRule protocol and returns a list
of SyntaxErrorModel objects.

Example:
    ```python
    from asciidoc_artisan.core.syntax_validators import UnclosedBlockRule
    from asciidoc_artisan.core.syntax_checker import ValidationContext

    rule = UnclosedBlockRule()
    context = ValidationContext(document="[source]\\nNo closing delimiter")
    errors = rule.validate(context)
    # Returns: [SyntaxErrorModel(code="E001", ...)]
    ```
"""

from typing import TYPE_CHECKING

# Import info rules (I00x)
from asciidoc_artisan.core.info_rules import (
    MissingAuthorVersionRule,
    MissingDocumentTitleRule,
)

# Import syntax error rules (E00x)
from asciidoc_artisan.core.syntax_error_rules import (
    InvalidAttributeRule,
    MalformedXRefRule,
    UnclosedBlockRule,
)

# Import warning rules (W00x)
from asciidoc_artisan.core.warning_rules import (
    BrokenXRefRule,
    DuplicateAnchorRule,
    EmptyHeadingRule,
    MissingIncludeRule,
    TrailingWhitespaceRule,
    UndefinedAttributeRefRule,
)

if TYPE_CHECKING:
    from asciidoc_artisan.core.syntax_checker import ValidationRule

# Re-export all rules for backward compatibility
__all__ = [
    # Syntax errors (E00x)
    "UnclosedBlockRule",
    "InvalidAttributeRule",
    "MalformedXRefRule",
    # Warnings (W00x)
    "BrokenXRefRule",
    "MissingIncludeRule",
    "UndefinedAttributeRefRule",
    "DuplicateAnchorRule",
    "EmptyHeadingRule",
    "TrailingWhitespaceRule",
    # Info (I00x)
    "MissingDocumentTitleRule",
    "MissingAuthorVersionRule",
    # Registry
    "BUILT_IN_RULES",
]

# Registry of all validation rules
BUILT_IN_RULES: list["ValidationRule"] = [
    # Syntax errors (E00x)
    UnclosedBlockRule(),
    InvalidAttributeRule(),
    MalformedXRefRule(),
    # Warnings (W00x)
    BrokenXRefRule(),
    MissingIncludeRule(),
    UndefinedAttributeRefRule(),
    DuplicateAnchorRule(),
    EmptyHeadingRule(),
    TrailingWhitespaceRule(),
    # Info (I00x)
    MissingDocumentTitleRule(),
    MissingAuthorVersionRule(),
]
