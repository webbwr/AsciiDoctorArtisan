"""
Info/style rules for AsciiDoc validation (I001-I050).

Extracted from syntax_validators.py for MA principle compliance.
These rules provide suggestions and best practice recommendations.

Error Codes:
- I002: Missing document title
- I003: Missing author/version attributes

Example:
    ```python
    from asciidoc_artisan.core.info_rules import MissingDocumentTitleRule

    rule = MissingDocumentTitleRule()
    errors = rule.validate(context)
    ```
"""

from asciidoc_artisan.core.models import (
    ErrorSeverity,
    QuickFix,
    SyntaxErrorModel,
    TextEdit,
)
from asciidoc_artisan.core.syntax_checker import ValidationContext


class MissingDocumentTitleRule:
    """
    Detect missing document title.

    Error: I002
    Severity: INFO
    Matches: Documents without = Title
    """

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate document has title."""
        errors = []
        lines = context.lines

        has_title = any(line.strip().startswith("= ") for line in lines)

        if not has_title and len(lines) > 5:
            errors.append(
                SyntaxErrorModel(
                    code="I002",
                    severity=ErrorSeverity.INFO,
                    message="Document missing title (= Title)",
                    line=0,
                    column=0,
                    length=0,
                    fixes=[
                        QuickFix(
                            title="Add document title",
                            edits=[
                                TextEdit(
                                    start_line=0,
                                    start_column=0,
                                    end_line=0,
                                    end_column=0,
                                    new_text="= Document Title\n\n",
                                )
                            ],
                        )
                    ],
                )
            )

        return errors


class MissingAuthorVersionRule:
    """
    Detect missing author/version attributes.

    Error: I003
    Severity: INFO
    Matches: Documents without :author: or :version:
    """

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate document has author/version."""
        errors = []
        attrs = context.attributes

        if "author" not in attrs and "version" not in attrs:
            errors.append(
                SyntaxErrorModel(
                    code="I003",
                    severity=ErrorSeverity.INFO,
                    message="Consider adding :author: and :version: attributes",
                    line=0,
                    column=0,
                    length=0,
                    fixes=[
                        QuickFix(
                            title="Add author and version",
                            edits=[
                                TextEdit(
                                    start_line=0,
                                    start_column=0,
                                    end_line=0,
                                    end_column=0,
                                    new_text=":author: Your Name\n:version: 1.0\n\n",
                                )
                            ],
                        )
                    ],
                )
            )

        return errors
