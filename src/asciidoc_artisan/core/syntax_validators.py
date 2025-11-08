"""
Syntax validation rules for AsciiDoc Artisan (v2.0.0+).

This module provides validation rules for detecting syntax errors, semantic
issues, and style violations in AsciiDoc documents.

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

import re
from typing import TYPE_CHECKING, List

from asciidoc_artisan.core.models import (
    ErrorSeverity,
    QuickFix,
    SyntaxErrorModel,
    TextEdit,
)
from asciidoc_artisan.core.syntax_checker import ValidationContext

if TYPE_CHECKING:
    from asciidoc_artisan.core.syntax_checker import ValidationRule


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

    def validate(self, context: ValidationContext) -> List[SyntaxErrorModel]:
        """Validate for unclosed blocks."""
        errors = []
        lines = context.lines

        for block_type, (start_pattern, end_pattern) in self.BLOCK_PATTERNS.items():
            # Find all block starts
            for i, line in enumerate(lines):
                if not context.should_validate_line(i):
                    continue

                if re.search(start_pattern, line):
                    # Look for closing delimiter
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

    def validate(self, context: ValidationContext) -> List[SyntaxErrorModel]:
        """Validate attribute syntax."""
        errors = []
        lines = context.lines

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            # Match lines starting with : but missing closing :
            if line.strip().startswith(":") and not line.strip().endswith(":"):
                # Check if it's actually an attribute definition attempt
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

    def validate(self, context: ValidationContext) -> List[SyntaxErrorModel]:
        """Validate cross-reference syntax."""
        errors = []
        lines = context.lines

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            # Find << without matching >>
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


class BrokenXRefRule:
    """
    Detect broken cross-references.

    Error: W001
    Severity: WARNING
    Matches: <<target>> where target anchor doesn't exist
    """

    def validate(self, context: ValidationContext) -> List[SyntaxErrorModel]:
        """Validate cross-reference targets."""
        errors = []
        lines = context.lines
        anchors = set(context.anchors)

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            # Find all cross-references
            xref_pattern = r"<<([^>,]+)"
            for match in re.finditer(xref_pattern, line):
                target = match.group(1).strip()

                if target and target not in anchors:
                    # Suggest similar anchors (simple substring matching)
                    suggestions = [a for a in anchors if target.lower() in a.lower()][
                        :3
                    ]

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

    def validate(self, context: ValidationContext) -> List[SyntaxErrorModel]:
        """Validate include file paths."""
        errors = []
        lines = context.lines

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            # Find include directives
            include_pattern = r"include::([^\[]+)\["
            for match in re.finditer(include_pattern, line):
                file_path = match.group(1).strip()

                # Check if file exists (basic check, may need path resolution)
                from pathlib import Path

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

    def validate(self, context: ValidationContext) -> List[SyntaxErrorModel]:
        """Validate attribute references."""
        errors = []
        lines = context.lines
        defined_attrs = set(context.attributes.keys())

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            # Find attribute references {attr}
            attr_ref_pattern = r"\{([^}]+)\}"
            for match in re.finditer(attr_ref_pattern, line):
                attr_name = match.group(1).strip()

                # Skip built-in attributes and empty references
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

    def validate(self, context: ValidationContext) -> List[SyntaxErrorModel]:
        """Validate anchor uniqueness."""
        errors = []
        lines = context.lines
        seen_anchors: dict[str, int] = {}

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            # Find anchors
            anchor_pattern = r"\[\[([^\]]+)\]\]|\[#([^\]]+)\]"
            for match in re.finditer(anchor_pattern, line):
                anchor_id = match.group(1) or match.group(2)

                if anchor_id in seen_anchors:
                    errors.append(
                        SyntaxErrorModel(
                            code="W004",
                            severity=ErrorSeverity.WARNING,
                            message=f"Duplicate anchor ID: {anchor_id} (first defined on line {seen_anchors[anchor_id] + 1})",
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

    def validate(self, context: ValidationContext) -> List[SyntaxErrorModel]:
        """Validate heading content."""
        errors = []
        lines = context.lines

        for i, line in enumerate(lines):
            if not context.should_validate_line(i):
                continue

            # Match heading lines
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

    def validate(self, context: ValidationContext) -> List[SyntaxErrorModel]:
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


class MissingDocumentTitleRule:
    """
    Detect missing document title.

    Error: I002
    Severity: INFO
    Matches: Documents without = Title
    """

    def validate(self, context: ValidationContext) -> List[SyntaxErrorModel]:
        """Validate document has title."""
        errors = []
        lines = context.lines

        # Check if document has level 1 heading
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

    def validate(self, context: ValidationContext) -> List[SyntaxErrorModel]:
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


# Registry of all validation rules
BUILT_IN_RULES: list["ValidationRule"] = [
    UnclosedBlockRule(),
    InvalidAttributeRule(),
    MalformedXRefRule(),
    BrokenXRefRule(),
    MissingIncludeRule(),
    UndefinedAttributeRefRule(),
    DuplicateAnchorRule(),
    EmptyHeadingRule(),
    TrailingWhitespaceRule(),
    MissingDocumentTitleRule(),
    MissingAuthorVersionRule(),
]
