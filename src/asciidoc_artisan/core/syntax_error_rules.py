"""
Syntax error rules for AsciiDoc validation (E001-E050).

Extracted from syntax_validators.py for MA principle compliance.
These rules detect critical syntax errors that break document rendering.

Error Codes:
- E001: Unclosed block delimiter
- E002: Invalid attribute syntax
- E003: Malformed cross-reference

Example:
    ```python
    from asciidoc_artisan.core.syntax_error_rules import UnclosedBlockRule

    rule = UnclosedBlockRule()
    errors = rule.validate(context)
    ```
"""

import re

from asciidoc_artisan.core.models import (
    ErrorSeverity,
    QuickFix,
    SyntaxErrorModel,
    TextEdit,
)
from asciidoc_artisan.core.syntax_checker import ValidationContext


class UnclosedBlockRule:
    """
    Detect unclosed block delimiters.

    Error: E001
    Severity: ERROR
    Matches: [source], [example], [sidebar], [quote] without closing delimiter
    """

    BLOCK_PATTERNS = {
        "source": (r"\[source[^\]]*\]", r"^-{4,}$"),
        "example": (r"\[example\]", r"^={4,}$"),
        "sidebar": (r"\[sidebar\]", r"^\*{4,}$"),
        "quote": (r"\[quote[^\]]*\]", r"^_{4,}$"),
        "listing": (r"\[listing\]", r"^-{4,}$"),
    }

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate for unclosed blocks."""
        errors = []
        lines = context.lines

        for block_type, (start_pattern, end_pattern) in self.BLOCK_PATTERNS.items():
            for i, line in enumerate(lines):
                if not context.should_validate_line(i):
                    continue

                if re.search(start_pattern, line):
                    found_close = False
                    for j in range(i + 1, len(lines)):
                        if re.match(end_pattern, lines[j]):
                            found_close = True
                            break

                    if not found_close:
                        delimiter = self._get_delimiter(block_type)
                        errors.append(
                            SyntaxErrorModel(
                                code="E001",
                                severity=ErrorSeverity.ERROR,
                                message=f"Unclosed {block_type} block (missing closing delimiter)",
                                line=i,
                                column=0,
                                length=len(line),
                                fixes=[
                                    QuickFix(
                                        title=f"Add closing delimiter ({delimiter})",
                                        edits=[
                                            TextEdit(
                                                start_line=i + 1,
                                                start_column=0,
                                                end_line=i + 1,
                                                end_column=0,
                                                new_text=f"{delimiter}\n",
                                            )
                                        ],
                                    )
                                ],
                            )
                        )

        return errors

    def _get_delimiter(self, block_type: str) -> str:
        """Get closing delimiter for block type."""
        delimiters = {
            "source": "----",
            "example": "====",
            "sidebar": "****",
            "quote": "____",
            "listing": "----",
        }
        return delimiters.get(block_type, "----")


class InvalidAttributeRule:
    """
    Detect invalid attribute syntax.

    Error: E002
    Severity: ERROR
    Matches: Attribute definitions missing closing colon
    """

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate attribute syntax."""
        errors = []
        lines = context.lines

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            if line.strip().startswith(":") and not line.strip().endswith(":"):
                if " " in line or len(line.strip()) > 1:
                    errors.append(
                        SyntaxErrorModel(
                            code="E002",
                            severity=ErrorSeverity.ERROR,
                            message="Invalid attribute syntax (missing closing colon)",
                            line=i,
                            column=0,
                            length=len(line),
                            fixes=[
                                QuickFix(
                                    title="Add closing colon",
                                    edits=[
                                        TextEdit(
                                            start_line=i,
                                            start_column=len(line.rstrip()),
                                            end_line=i,
                                            end_column=len(line.rstrip()),
                                            new_text=":",
                                        )
                                    ],
                                )
                            ],
                        )
                    )

        return errors


class MalformedXRefRule:
    """
    Detect malformed cross-references.

    Error: E003
    Severity: ERROR
    Matches: <<target without closing >>
    """

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate cross-reference syntax."""
        errors = []
        lines = context.lines

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            matches = re.finditer(r"<<([^>]*?)(?:>>|$)", line)
            for match in matches:
                if not match.group(0).endswith(">>"):
                    errors.append(
                        SyntaxErrorModel(
                            code="E003",
                            severity=ErrorSeverity.ERROR,
                            message="Malformed cross-reference (missing closing >>)",
                            line=i,
                            column=match.start(),
                            length=len(match.group(0)),
                            fixes=[
                                QuickFix(
                                    title="Add closing >>",
                                    edits=[
                                        TextEdit(
                                            start_line=i,
                                            start_column=match.end(),
                                            end_line=i,
                                            end_column=match.end(),
                                            new_text=">>",
                                        )
                                    ],
                                )
                            ],
                        )
                    )

        return errors
