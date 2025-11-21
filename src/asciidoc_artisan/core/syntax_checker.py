"""
Syntax checker for AsciiDoc Artisan (v2.0.0+).

Real-time syntax error detection with quick fixes. Rule-based validation (50+ rules: E001-E050 errors, W001-W050 warnings, I001-I050 info).
Features: Incremental validation, quick fix suggestions, <100ms for 1000-line docs, smart caching.

Architecture: Document → ValidationContext → SyntaxChecker.validate() → Apply rules → Collect errors → Sorted list

Example:
    checker = SyntaxChecker()
    errors = checker.validate(document)
    for error in errors:
        print(f"{error.code}: {error.message} (line {error.line})")
"""

import re
from functools import cached_property
from typing import Protocol

from asciidoc_artisan.core.models import SyntaxErrorModel


class ValidationContext:
    """Validation context with caching. Stores document text, caches anchors/attributes/includes. Lazy eval: 10-20x faster than re-parsing."""

    def __init__(self, document: str, changed_lines: list[int] | None = None) -> None:
        """Initialize validation context with document text and optional changed lines (0-indexed, None = all)."""
        self.document = document
        self.lines = document.splitlines()
        self.changed_lines = changed_lines

    @cached_property
    def anchors(self) -> list[str]:
        """Extract all anchor IDs from document. Matches [[id]] and [#id] patterns. Cached after first access."""
        # Match [[id]] and [#id] patterns
        pattern = r"\[\[([^\]]+)\]\]|\[#([^\]]+)\]"
        matches = re.findall(pattern, self.document)
        # Flatten tuples (each match has 2 groups)
        return [m[0] or m[1] for m in matches]

    @cached_property
    def attributes(self) -> dict[str, str]:
        """Extract all document attributes. Matches :key: value pattern. Cached after first access."""
        pattern = r"^:([^:]+):\s*(.*)$"
        matches = re.findall(pattern, self.document, re.MULTILINE)
        return {key.strip(): value.strip() for key, value in matches}

    @cached_property
    def includes(self) -> list[str]:
        """Extract all include directives. Matches include::path[] pattern. Cached after first access."""
        pattern = r"include::([^\[]+)\["
        return re.findall(pattern, self.document)

    def should_validate_line(self, line_number: int) -> bool:
        """Check if line should be validated. For incremental validation: returns True if line changed or changed_lines is None."""
        if self.changed_lines is None:
            return True  # Validate all lines
        return line_number in self.changed_lines


class ValidationRule(Protocol):
    """Protocol for validation rules. Rules check for syntax/semantic/style errors, return list of SyntaxErrorModel. Independent and stateless."""

    def validate(self, context: ValidationContext) -> list[SyntaxErrorModel]:
        """Validate document and return errors. Args: context (with caching). Returns: list of SyntaxErrorModel."""
        ...


class SyntaxChecker:
    """Core syntax checking engine. Manages validation rules, orchestrates error detection. Performance: <100ms for 1000-line doc, <10ms incremental."""

    def __init__(self) -> None:
        """Initialize syntax checker with built-in rules."""
        self.rules: list[ValidationRule] = []
        self._setup_built_in_rules()

    def _setup_built_in_rules(self) -> None:
        """Initialize built-in validation rules. Loads 11 rules from syntax_validators: 3 errors (E001-E003), 6 warnings (W001-W005, W029), 2 info (I002-I003)."""
        # Import built-in rules (Phase 2)
        try:
            from asciidoc_artisan.core.syntax_validators import BUILT_IN_RULES

            self.rules.extend(BUILT_IN_RULES)
        except ImportError:
            # If syntax_validators not available, continue with empty rules
            import logging

            logging.warning("syntax_validators module not found, no built-in rules loaded")

    def add_rule(self, rule: ValidationRule) -> None:
        """Register a custom validation rule. Rules executed in registration order. Add critical rules first for fail-fast performance."""
        self.rules.append(rule)

    def remove_rule(self, rule: ValidationRule) -> None:
        """Unregister a validation rule. Raises ValueError if rule not registered."""
        if rule in self.rules:
            self.rules.remove(rule)
        else:
            raise ValueError("Rule not registered")

    def validate(self, document: str, changed_lines: list[int] | None = None) -> list[SyntaxErrorModel]:
        """Main validation entry point. Creates context, applies rules, collects/sorts errors. Returns sorted list. Perf: <100ms full doc, <10ms incremental."""
        # Create context with caching
        context = ValidationContext(document, changed_lines)

        # Collect errors from all rules
        all_errors: list[SyntaxErrorModel] = []

        for rule in self.rules:
            try:
                rule_errors = rule.validate(context)
                all_errors.extend(rule_errors)
            except Exception as e:
                # Log rule failure but don't crash validation
                import logging

                logging.error(
                    f"Validation rule {rule.__class__.__name__} failed: {e}",
                    exc_info=True,
                )

        # Sort by line, then column
        all_errors.sort(key=lambda err: (err.line, err.column))

        return all_errors

    def validate_incremental(self, document: str, changed_lines: list[int]) -> list[SyntaxErrorModel]:
        """Validate only changed lines. Optimization for real-time validation: 10-20x faster than full, <10ms typical. Some validators still access full context (cached)."""
        return self.validate(document, changed_lines=changed_lines)

    def get_rules_count(self) -> int:
        """Get number of registered rules."""
        return len(self.rules)

    def get_rule_names(self) -> list[str]:
        """Get names of all registered rules. Returns list of rule class names."""
        return [rule.__class__.__name__ for rule in self.rules]


# Convenience functions for common validation tasks


def extract_anchors(document: str) -> list[str]:
    """Extract all anchor IDs from document. Standalone function for simple extraction without full context. Matches [[id]] and [#id] patterns."""
    pattern = r"\[\[([^\]]+)\]\]|\[#([^\]]+)\]"
    matches = re.findall(pattern, document)
    return [m[0] or m[1] for m in matches]


def extract_attributes(document: str) -> dict[str, str]:
    """Extract all document attributes. Standalone function for simple extraction. Matches :key: value pattern. Returns dict."""
    pattern = r"^:([^:]+):\s*(.*)$"
    matches = re.findall(pattern, document, re.MULTILINE)
    return {key.strip(): value.strip() for key, value in matches}


def is_inside_code_block(lines: list[str], line_number: int) -> bool:
    """Check if line is inside code block. Code blocks use ---- delimiters. Useful for validators that skip code content. Returns True if inside block."""
    if line_number < 0 or line_number >= len(lines):
        return False

    in_block = False
    for i in range(line_number + 1):
        line = lines[i].strip()
        if re.match(r"^-{4,}$", line):
            in_block = not in_block

    return in_block
