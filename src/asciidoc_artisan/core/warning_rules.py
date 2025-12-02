"""
Warning rules for AsciiDoc validation (W001-W050).

Extracted from syntax_validators.py for MA principle compliance.
These rules detect semantic issues, broken links, and style violations.

Error Codes:
- W001: Broken cross-reference
- W002: Missing include file
- W003: Undefined attribute reference
- W004: Duplicate anchor ID
- W005: Empty heading
- W029: Trailing whitespace

Example:
    ```python
    from asciidoc_artisan.core.warning_rules import BrokenXRefRule

    rule = BrokenXRefRule()
    errors = rule.validate(context)
    ```
"""

import re
from pathlib import Path

from asciidoc_artisan.core.models import (
    ErrorSeverity,
    QuickFix,
    SyntaxErrorModel,
    TextEdit,
)
from asciidoc_artisan.core.syntax_checker import ValidationContext


class BrokenXRefRule:
    """
    Detect broken cross-references.

    Error: W001
    Severity: WARNING
    Matches: <<target>> where target anchor doesn't exist
    """

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate cross-reference targets."""
        errors = []
        lines = context.lines
        anchors = set(context.anchors)

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            xref_pattern = r"<<([^>,]+)"
            for match in re.finditer(xref_pattern, line):
                target = match.group(1).strip()

                if target and target not in anchors:
                    suggestions = [a for a in anchors if target.lower() in a.lower()][:3]

                    fixes = []
                    for suggestion in suggestions:
                        fixes.append(
                            QuickFix(
                                title=f"Change to '{suggestion}'",
                                edits=[
                                    TextEdit(
                                        start_line=i,
                                        start_column=match.start(),
                                        end_line=i,
                                        end_column=match.end(),
                                        new_text=f"<<{suggestion}>>",
                                    )
                                ],
                            )
                        )

                    errors.append(
                        SyntaxErrorModel(
                            code="W001",
                            severity=ErrorSeverity.WARNING,
                            message=f"Broken cross-reference: '{target}' not found",
                            line=i,
                            column=match.start(),
                            length=match.end() - match.start(),
                            fixes=fixes,
                        )
                    )

        return errors


class MissingIncludeRule:
    """
    Detect missing include files.

    Error: W002
    Severity: WARNING
    Matches: include::file[] where file doesn't exist
    """

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate include file paths."""
        errors = []
        lines = context.lines

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            include_pattern = r"include::([^\[]+)\["
            for match in re.finditer(include_pattern, line):
                file_path = match.group(1).strip()

                if not Path(file_path).exists():
                    errors.append(
                        SyntaxErrorModel(
                            code="W002",
                            severity=ErrorSeverity.WARNING,
                            message=f"Include file not found: {file_path}",
                            line=i,
                            column=match.start(),
                            length=match.end() - match.start(),
                            fixes=[],
                        )
                    )

        return errors


class UndefinedAttributeRefRule:
    """
    Detect undefined attribute references.

    Error: W003
    Severity: WARNING
    Matches: {attribute} where :attribute: is not defined
    """

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate attribute references."""
        errors = []
        lines = context.lines
        defined_attrs = set(context.attributes.keys())

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            attr_ref_pattern = r"\{([^}]+)\}"
            for match in re.finditer(attr_ref_pattern, line):
                attr_name = match.group(1).strip()

                if not attr_name or attr_name in ("sp", "nbsp", "zwsp"):
                    continue

                if attr_name not in defined_attrs:
                    errors.append(
                        SyntaxErrorModel(
                            code="W003",
                            severity=ErrorSeverity.WARNING,
                            message=f"Undefined attribute reference: {attr_name}",
                            line=i,
                            column=match.start(),
                            length=match.end() - match.start(),
                            fixes=[
                                QuickFix(
                                    title=f"Define :{attr_name}:",
                                    edits=[
                                        TextEdit(
                                            start_line=0,
                                            start_column=0,
                                            end_line=0,
                                            end_column=0,
                                            new_text=f":{attr_name}: value\n",
                                        )
                                    ],
                                )
                            ],
                        )
                    )

        return errors


class DuplicateAnchorRule:
    """
    Detect duplicate anchor IDs.

    Error: W004
    Severity: WARNING
    Matches: Multiple anchors with same ID
    """

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate anchor uniqueness."""
        errors = []
        lines = context.lines
        seen_anchors: dict[str, int] = {}

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            anchor_pattern = r"\[\[([^\]]+)\]\]|\[#([^\]]+)\]"
            for match in re.finditer(anchor_pattern, line):
                anchor_id = match.group(1) or match.group(2)

                if anchor_id in seen_anchors:
                    first_line = seen_anchors[anchor_id] + 1
                    errors.append(
                        SyntaxErrorModel(
                            code="W004",
                            severity=ErrorSeverity.WARNING,
                            message=f"Duplicate anchor ID: {anchor_id} (first defined on line {first_line})",
                            line=i,
                            column=match.start(),
                            length=match.end() - match.start(),
                            fixes=[
                                QuickFix(
                                    title=f"Rename to '{anchor_id}_2'",
                                    edits=[
                                        TextEdit(
                                            start_line=i,
                                            start_column=match.start(),
                                            end_line=i,
                                            end_column=match.end(),
                                            new_text=f"[[{anchor_id}_2]]",
                                        )
                                    ],
                                )
                            ],
                        )
                    )
                else:
                    seen_anchors[anchor_id] = i

        return errors


class EmptyHeadingRule:
    """
    Detect empty headings.

    Error: W005
    Severity: WARNING
    Matches: == with no text
    """

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate heading content."""
        errors = []
        lines = context.lines

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            heading_match = re.match(r"^(={1,5})\s*$", line)
            if heading_match:
                errors.append(
                    SyntaxErrorModel(
                        code="W005",
                        severity=ErrorSeverity.WARNING,
                        message="Empty heading (no text)",
                        line=i,
                        column=0,
                        length=len(line),
                        fixes=[],
                    )
                )

        return errors


class TrailingWhitespaceRule:
    """
    Detect trailing whitespace.

    Error: W029
    Severity: WARNING (Style)
    Matches: Lines ending with spaces or tabs
    """

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate for trailing whitespace."""
        errors = []
        lines = context.lines

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            if line and line != line.rstrip():
                trailing_len = len(line) - len(line.rstrip())
                errors.append(
                    SyntaxErrorModel(
                        code="W029",
                        severity=ErrorSeverity.WARNING,
                        message=f"Trailing whitespace ({trailing_len} characters)",
                        line=i,
                        column=len(line.rstrip()),
                        length=trailing_len,
                        fixes=[
                            QuickFix(
                                title="Remove trailing whitespace",
                                edits=[
                                    TextEdit(
                                        start_line=i,
                                        start_column=0,
                                        end_line=i,
                                        end_column=len(line),
                                        new_text=line.rstrip() + "\n",
                                    )
                                ],
                            )
                        ],
                    )
                )

        return errors
