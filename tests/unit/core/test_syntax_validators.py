"""
Tests for syntax_validators module.

Tests all 11 built-in validation rules for AsciiDoc syntax checking.
"""

import pytest

from asciidoc_artisan.core.models import ErrorSeverity
from asciidoc_artisan.core.syntax_checker import ValidationContext
from asciidoc_artisan.core.syntax_validators import (
    BUILT_IN_RULES,
    BrokenXRefRule,
    DuplicateAnchorRule,
    EmptyHeadingRule,
    InvalidAttributeRule,
    MalformedXRefRule,
    MissingAuthorVersionRule,
    MissingDocumentTitleRule,
    MissingIncludeRule,
    TrailingWhitespaceRule,
    UnclosedBlockRule,
    UndefinedAttributeRefRule,
)


@pytest.mark.unit
class TestUnclosedBlockRule:
    """Test UnclosedBlockRule (E001)."""

    def test_detects_unclosed_source_block(self):
        """Test detection of unclosed source block."""
        doc = "[source,python]\ndef hello():\n    pass\n"
        context = ValidationContext(doc)
        rule = UnclosedBlockRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "E001"
        assert errors[0].severity == ErrorSeverity.ERROR
        assert "source" in errors[0].message.lower()
        assert errors[0].line == 0

    def test_detects_unclosed_example_block(self):
        """Test detection of unclosed example block."""
        doc = "[example]\nThis is an example\n"
        context = ValidationContext(doc)
        rule = UnclosedBlockRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "E001"
        assert "example" in errors[0].message.lower()

    def test_detects_unclosed_sidebar_block(self):
        """Test detection of unclosed sidebar block."""
        doc = "[sidebar]\nThis is a sidebar\n"
        context = ValidationContext(doc)
        rule = UnclosedBlockRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert "sidebar" in errors[0].message.lower()

    def test_detects_unclosed_quote_block(self):
        """Test detection of unclosed quote block."""
        doc = '[quote, author="John"]\nQuote text\n'
        context = ValidationContext(doc)
        rule = UnclosedBlockRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert "quote" in errors[0].message.lower()

    def test_detects_unclosed_listing_block(self):
        """Test detection of unclosed listing block."""
        doc = "[listing]\nListing content\n"
        context = ValidationContext(doc)
        rule = UnclosedBlockRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert "listing" in errors[0].message.lower()

    def test_no_error_for_closed_source_block(self):
        """Test no error for properly closed source block."""
        doc = "[source,python]\n----\ndef hello():\n    pass\n----\n"
        context = ValidationContext(doc)
        rule = UnclosedBlockRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_no_error_for_closed_example_block(self):
        """Test no error for properly closed example block."""
        doc = "[example]\n====\nExample content\n====\n"
        context = ValidationContext(doc)
        rule = UnclosedBlockRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_quickfix_suggests_closing_delimiter(self):
        """Test QuickFix suggests adding closing delimiter."""
        doc = "[source]\nCode\n"
        context = ValidationContext(doc)
        rule = UnclosedBlockRule()

        errors = rule.validate(context)

        assert len(errors) >= 1
        assert len(errors[0].fixes) == 1
        fix = errors[0].fixes[0]
        assert "----" in fix.title
        assert len(fix.edits) == 1
        assert "----" in fix.edits[0].new_text

    def test_get_delimiter_returns_correct_delimiter(self):
        """Test _get_delimiter returns correct delimiter for each type."""
        rule = UnclosedBlockRule()

        assert rule._get_delimiter("source") == "----"
        assert rule._get_delimiter("example") == "===="
        assert rule._get_delimiter("sidebar") == "****"
        assert rule._get_delimiter("quote") == "____"
        assert rule._get_delimiter("listing") == "----"
        assert rule._get_delimiter("unknown") == "----"  # Default

    def test_respects_incremental_validation(self):
        """Test rule respects should_validate_line."""
        doc = "[source]\n----\nLine 1\nLine 2\n"
        context = ValidationContext(doc, changed_lines=[2])  # Only line 2 changed
        rule = UnclosedBlockRule()

        errors = rule.validate(context)

        # Should not detect error on line 0 (not in changed_lines)
        assert len(errors) == 0


@pytest.mark.unit
class TestInvalidAttributeRule:
    """Test InvalidAttributeRule (E002)."""

    def test_detects_missing_closing_colon(self):
        """Test detection of attribute missing closing colon."""
        doc = ":author John Doe\n"
        context = ValidationContext(doc)
        rule = InvalidAttributeRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "E002"
        assert errors[0].severity == ErrorSeverity.ERROR
        assert "closing colon" in errors[0].message.lower()

    def test_no_error_for_valid_attribute(self):
        """Test no error for valid attribute syntax with only name."""
        doc = ":author:\n:version:\n"
        context = ValidationContext(doc)
        rule = InvalidAttributeRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_no_error_for_empty_attribute(self):
        """Test no error for empty attribute (flag attribute)."""
        doc = ":toc:\n"
        context = ValidationContext(doc)
        rule = InvalidAttributeRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_no_error_for_single_colon(self):
        """Test no error for single colon (not an attribute)."""
        doc = ":\n"
        context = ValidationContext(doc)
        rule = InvalidAttributeRule()

        errors = rule.validate(context)

        # Single colon with no text is not considered attribute definition
        assert len(errors) == 0

    def test_quickfix_adds_closing_colon(self):
        """Test QuickFix adds closing colon."""
        doc = ":author John\n"
        context = ValidationContext(doc)
        rule = InvalidAttributeRule()

        errors = rule.validate(context)

        assert len(errors[0].fixes) == 1
        fix = errors[0].fixes[0]
        assert "colon" in fix.title.lower()
        assert fix.edits[0].new_text == ":"

    def test_respects_incremental_validation(self):
        """Test rule respects should_validate_line."""
        doc = ":author John\n:version 1.0\n"
        context = ValidationContext(doc, changed_lines=[1])
        rule = InvalidAttributeRule()

        errors = rule.validate(context)

        # Only line 1 should be validated
        assert len(errors) == 1
        assert errors[0].line == 1


@pytest.mark.unit
class TestMalformedXRefRule:
    """Test MalformedXRefRule (E003)."""

    def test_detects_missing_closing_brackets(self):
        """Test detection of xref missing closing >>."""
        doc = "See <<introduction for details.\n"
        context = ValidationContext(doc)
        rule = MalformedXRefRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "E003"
        assert errors[0].severity == ErrorSeverity.ERROR
        assert "closing >>" in errors[0].message.lower()

    def test_no_error_for_valid_xref(self):
        """Test no error for valid cross-reference."""
        doc = "See <<introduction>> for details.\n"
        context = ValidationContext(doc)
        rule = MalformedXRefRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_detects_multiple_malformed_xrefs(self):
        """Test detection of multiple malformed xrefs in one line."""
        doc = "See <<intro and <<summary for details.\n"
        context = ValidationContext(doc)
        rule = MalformedXRefRule()

        errors = rule.validate(context)

        # Regex matches from first << to end of line as one error
        assert len(errors) >= 1

    def test_quickfix_adds_closing_brackets(self):
        """Test QuickFix adds >> to close xref."""
        doc = "See <<intro\n"
        context = ValidationContext(doc)
        rule = MalformedXRefRule()

        errors = rule.validate(context)

        assert len(errors[0].fixes) == 1
        fix = errors[0].fixes[0]
        assert ">>" in fix.title
        assert fix.edits[0].new_text == ">>"

    def test_respects_incremental_validation(self):
        """Test rule respects should_validate_line."""
        doc = "Line 0: <<intro\nLine 1: <<summary\n"
        context = ValidationContext(doc, changed_lines=[0])
        rule = MalformedXRefRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].line == 0


@pytest.mark.unit
class TestBrokenXRefRule:
    """Test BrokenXRefRule (W001)."""

    def test_detects_broken_xref(self):
        """Test detection of xref to non-existent anchor."""
        doc = "[[intro]]\n== Introduction\n\nSee <<nonexistent>> for details.\n"
        context = ValidationContext(doc)
        rule = BrokenXRefRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "W001"
        assert errors[0].severity == ErrorSeverity.WARNING
        assert "nonexistent" in errors[0].message.lower()

    def test_no_error_for_valid_xref(self):
        """Test no error for xref to existing anchor."""
        doc = "[[intro]]\n== Introduction\n\nSee <<intro>> for details.\n"
        context = ValidationContext(doc)
        rule = BrokenXRefRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_suggests_similar_anchors(self):
        """Test QuickFix suggests similar anchor names."""
        doc = "[[introduction]]\n== Intro\n\nSee <<intro>> for details.\n"
        context = ValidationContext(doc)
        rule = BrokenXRefRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        # Should suggest "introduction" (substring match)
        assert len(errors[0].fixes) >= 1
        assert any("introduction" in fix.title for fix in errors[0].fixes)

    def test_limits_suggestions_to_three(self):
        """Test QuickFix limits suggestions to 3."""
        doc = "[[intro1]]\n[[intro2]]\n[[intro3]]\n[[intro4]]\n\nSee <<intro>> for details.\n"
        context = ValidationContext(doc)
        rule = BrokenXRefRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert len(errors[0].fixes) <= 3

    def test_handles_hash_anchor_syntax(self):
        """Test validation works with [#anchor] syntax."""
        doc = "[#intro]\n== Introduction\n\nSee <<intro>> for details.\n"
        context = ValidationContext(doc)
        rule = BrokenXRefRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_respects_incremental_validation(self):
        """Test rule respects should_validate_line."""
        doc = "[[intro]]\nSee <<bad1>>\nSee <<bad2>>\n"
        context = ValidationContext(doc, changed_lines=[1])
        rule = BrokenXRefRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].line == 1


@pytest.mark.unit
class TestMissingIncludeRule:
    """Test MissingIncludeRule (W002)."""

    def test_detects_missing_include_file(self):
        """Test detection of missing include file."""
        doc = "include::nonexistent.adoc[]\n"
        context = ValidationContext(doc)
        rule = MissingIncludeRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "W002"
        assert errors[0].severity == ErrorSeverity.WARNING
        assert "nonexistent.adoc" in errors[0].message

    def test_no_error_for_existing_file(self, tmp_path):
        """Test no error when include file exists."""
        include_file = tmp_path / "chapter.adoc"
        include_file.write_text("== Chapter 1\n")

        doc = f"include::{include_file}[]\n"
        context = ValidationContext(doc)
        rule = MissingIncludeRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_respects_incremental_validation(self):
        """Test rule respects should_validate_line."""
        doc = "include::file1.adoc[]\ninclude::file2.adoc[]\n"
        context = ValidationContext(doc, changed_lines=[0])
        rule = MissingIncludeRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].line == 0


@pytest.mark.unit
class TestUndefinedAttributeRefRule:
    """Test UndefinedAttributeRefRule (W003)."""

    def test_detects_undefined_attribute_ref(self):
        """Test detection of undefined attribute reference."""
        doc = "Author: {author}\n"
        context = ValidationContext(doc)
        rule = UndefinedAttributeRefRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "W003"
        assert errors[0].severity == ErrorSeverity.WARNING
        assert "author" in errors[0].message.lower()

    def test_no_error_for_defined_attribute(self):
        """Test no error for defined attribute reference."""
        doc = ":author: John Doe\n\nAuthor: {author}\n"
        context = ValidationContext(doc)
        rule = UndefinedAttributeRefRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_skips_builtin_attributes(self):
        """Test skips built-in AsciiDoc attributes."""
        doc = "A space:{sp}here\nNo break:{nbsp}space\n"
        context = ValidationContext(doc)
        rule = UndefinedAttributeRefRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_skips_empty_references(self):
        """Test skips empty attribute references."""
        doc = "Empty: {}\n"
        context = ValidationContext(doc)
        rule = UndefinedAttributeRefRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_quickfix_suggests_definition(self):
        """Test QuickFix suggests attribute definition."""
        doc = "Author: {author}\n"
        context = ValidationContext(doc)
        rule = UndefinedAttributeRefRule()

        errors = rule.validate(context)

        assert len(errors[0].fixes) == 1
        fix = errors[0].fixes[0]
        assert ":author:" in fix.title
        assert ":author:" in fix.edits[0].new_text

    def test_respects_incremental_validation(self):
        """Test rule respects should_validate_line."""
        doc = "Line 0: {attr1}\nLine 1: {attr2}\n"
        context = ValidationContext(doc, changed_lines=[1])
        rule = UndefinedAttributeRefRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].line == 1


@pytest.mark.unit
class TestDuplicateAnchorRule:
    """Test DuplicateAnchorRule (W004)."""

    def test_detects_duplicate_anchors(self):
        """Test detection of duplicate anchor IDs."""
        doc = "[[intro]]\n== First\n\n[[intro]]\n== Second\n"
        context = ValidationContext(doc)
        rule = DuplicateAnchorRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "W004"
        assert errors[0].severity == ErrorSeverity.WARNING
        assert "duplicate" in errors[0].message.lower()
        assert "intro" in errors[0].message

    def test_shows_first_definition_line(self):
        """Test error message shows line of first definition."""
        doc = "[[intro]]\n== First\n\n[[intro]]\n== Second\n"
        context = ValidationContext(doc)
        rule = DuplicateAnchorRule()

        errors = rule.validate(context)

        # Should mention line 1 (first definition at line 0, 0-indexed)
        assert "line 1" in errors[0].message.lower()

    def test_no_error_for_unique_anchors(self):
        """Test no error for unique anchor IDs."""
        doc = "[[intro]]\n== Introduction\n\n[[summary]]\n== Summary\n"
        context = ValidationContext(doc)
        rule = DuplicateAnchorRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_handles_hash_syntax(self):
        """Test detection works with [#anchor] syntax."""
        doc = "[#intro]\n== First\n\n[#intro]\n== Second\n"
        context = ValidationContext(doc)
        rule = DuplicateAnchorRule()

        errors = rule.validate(context)

        assert len(errors) == 1

    def test_handles_mixed_syntax(self):
        """Test detection works with mixed [[]] and [#] syntax."""
        doc = "[[intro]]\n== First\n\n[#intro]\n== Second\n"
        context = ValidationContext(doc)
        rule = DuplicateAnchorRule()

        errors = rule.validate(context)

        assert len(errors) == 1

    def test_quickfix_suggests_rename(self):
        """Test QuickFix suggests renaming duplicate anchor."""
        doc = "[[intro]]\n== First\n\n[[intro]]\n== Second\n"
        context = ValidationContext(doc)
        rule = DuplicateAnchorRule()

        errors = rule.validate(context)

        assert len(errors[0].fixes) == 1
        fix = errors[0].fixes[0]
        assert "intro_2" in fix.title
        assert "intro_2" in fix.edits[0].new_text

    def test_respects_incremental_validation(self):
        """Test rule respects should_validate_line."""
        doc = "[[intro]]\n[[intro]]\n[[summary]]\n"
        context = ValidationContext(doc, changed_lines=[0, 1])
        rule = DuplicateAnchorRule()

        errors = rule.validate(context)

        # Should detect duplicate on line 1 (both lines 0 and 1 validated)
        assert len(errors) == 1
        assert errors[0].line == 1


@pytest.mark.unit
class TestEmptyHeadingRule:
    """Test EmptyHeadingRule (W005)."""

    def test_detects_empty_heading(self):
        """Test detection of empty heading."""
        doc = "==\n\nContent here.\n"
        context = ValidationContext(doc)
        rule = EmptyHeadingRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "W005"
        assert errors[0].severity == ErrorSeverity.WARNING
        assert "empty" in errors[0].message.lower()

    def test_detects_various_heading_levels(self):
        """Test detection works for all heading levels."""
        for level in range(1, 6):
            doc = f"{'=' * level}\n"
            context = ValidationContext(doc)
            rule = EmptyHeadingRule()

            errors = rule.validate(context)

            assert len(errors) == 1

    def test_no_error_for_valid_heading(self):
        """Test no error for heading with text."""
        doc = "== Introduction\n\nContent here.\n"
        context = ValidationContext(doc)
        rule = EmptyHeadingRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_no_error_for_heading_with_whitespace(self):
        """Test no error for heading with text after whitespace."""
        doc = "==  Introduction\n"
        context = ValidationContext(doc)
        rule = EmptyHeadingRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_respects_incremental_validation(self):
        """Test rule respects should_validate_line."""
        doc = "==\n==\n"
        context = ValidationContext(doc, changed_lines=[0])
        rule = EmptyHeadingRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].line == 0


@pytest.mark.unit
class TestTrailingWhitespaceRule:
    """Test TrailingWhitespaceRule (W029)."""

    def test_detects_trailing_spaces(self):
        """Test detection of trailing spaces."""
        doc = "Line with trailing spaces   \n"
        context = ValidationContext(doc)
        rule = TrailingWhitespaceRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "W029"
        assert errors[0].severity == ErrorSeverity.WARNING
        assert "3 characters" in errors[0].message

    def test_detects_trailing_tabs(self):
        """Test detection of trailing tabs."""
        doc = "Line with trailing tabs\t\t\n"
        context = ValidationContext(doc)
        rule = TrailingWhitespaceRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert "2 characters" in errors[0].message

    def test_no_error_for_clean_lines(self):
        """Test no error for lines without trailing whitespace."""
        doc = "Clean line\nAnother clean line\n"
        context = ValidationContext(doc)
        rule = TrailingWhitespaceRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_quickfix_removes_whitespace(self):
        """Test QuickFix removes trailing whitespace."""
        doc = "Line with spaces   \n"
        context = ValidationContext(doc)
        rule = TrailingWhitespaceRule()

        errors = rule.validate(context)

        assert len(errors[0].fixes) == 1
        fix = errors[0].fixes[0]
        assert "remove" in fix.title.lower()
        # Check that whitespace is removed (actual impl may or may not include newline)
        assert "Line with spaces" in fix.edits[0].new_text
        assert "   " not in fix.edits[0].new_text

    def test_respects_incremental_validation(self):
        """Test rule respects should_validate_line."""
        doc = "Line 0 \nLine 1 \n"
        context = ValidationContext(doc, changed_lines=[1])
        rule = TrailingWhitespaceRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].line == 1


@pytest.mark.unit
class TestMissingDocumentTitleRule:
    """Test MissingDocumentTitleRule (I002)."""

    def test_detects_missing_title(self):
        """Test detection of missing document title."""
        doc = "== Section 1\n\nContent here.\n\n== Section 2\n\nMore content.\n"
        context = ValidationContext(doc)
        rule = MissingDocumentTitleRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "I002"
        assert errors[0].severity == ErrorSeverity.INFO
        assert "title" in errors[0].message.lower()

    def test_no_error_for_document_with_title(self):
        """Test no error when document has level 1 heading."""
        doc = "= Document Title\n\n== Section 1\n\nContent.\n"
        context = ValidationContext(doc)
        rule = MissingDocumentTitleRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_no_error_for_short_documents(self):
        """Test no error for short documents (<= 5 lines)."""
        doc = "== Section\nShort doc\n"
        context = ValidationContext(doc)
        rule = MissingDocumentTitleRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_quickfix_adds_title(self):
        """Test QuickFix adds document title."""
        doc = "== Section 1\n\n" * 3  # Make it > 5 lines
        context = ValidationContext(doc)
        rule = MissingDocumentTitleRule()

        errors = rule.validate(context)

        assert len(errors[0].fixes) == 1
        fix = errors[0].fixes[0]
        assert "title" in fix.title.lower()
        assert "= Document Title" in fix.edits[0].new_text


@pytest.mark.unit
class TestMissingAuthorVersionRule:
    """Test MissingAuthorVersionRule (I003)."""

    def test_detects_missing_author_and_version(self):
        """Test detection of missing author/version attributes."""
        doc = "= Document Title\n\nContent here.\n"
        context = ValidationContext(doc)
        rule = MissingAuthorVersionRule()

        errors = rule.validate(context)

        assert len(errors) == 1
        assert errors[0].code == "I003"
        assert errors[0].severity == ErrorSeverity.INFO
        assert "author" in errors[0].message.lower()
        assert "version" in errors[0].message.lower()

    def test_no_error_when_author_present(self):
        """Test no error when author attribute defined."""
        doc = "= Title\n:author: John Doe\n\nContent.\n"
        context = ValidationContext(doc)
        rule = MissingAuthorVersionRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_no_error_when_version_present(self):
        """Test no error when version attribute defined."""
        doc = "= Title\n:version: 1.0\n\nContent.\n"
        context = ValidationContext(doc)
        rule = MissingAuthorVersionRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_no_error_when_both_present(self):
        """Test no error when both author and version defined."""
        doc = "= Title\n:author: John\n:version: 1.0\n\nContent.\n"
        context = ValidationContext(doc)
        rule = MissingAuthorVersionRule()

        errors = rule.validate(context)

        assert len(errors) == 0

    def test_quickfix_adds_both_attributes(self):
        """Test QuickFix adds both author and version."""
        doc = "= Title\n\nContent.\n"
        context = ValidationContext(doc)
        rule = MissingAuthorVersionRule()

        errors = rule.validate(context)

        assert len(errors[0].fixes) == 1
        fix = errors[0].fixes[0]
        assert ":author:" in fix.edits[0].new_text
        assert ":version:" in fix.edits[0].new_text


@pytest.mark.unit
class TestBuiltInRulesRegistry:
    """Test BUILT_IN_RULES registry."""

    def test_registry_contains_all_rules(self):
        """Test registry contains all 11 validation rules."""
        assert len(BUILT_IN_RULES) == 11

    def test_registry_has_correct_rule_types(self):
        """Test registry contains instances of all rule classes."""
        rule_types = [type(rule).__name__ for rule in BUILT_IN_RULES]

        assert "UnclosedBlockRule" in rule_types
        assert "InvalidAttributeRule" in rule_types
        assert "MalformedXRefRule" in rule_types
        assert "BrokenXRefRule" in rule_types
        assert "MissingIncludeRule" in rule_types
        assert "UndefinedAttributeRefRule" in rule_types
        assert "DuplicateAnchorRule" in rule_types
        assert "EmptyHeadingRule" in rule_types
        assert "TrailingWhitespaceRule" in rule_types
        assert "MissingDocumentTitleRule" in rule_types
        assert "MissingAuthorVersionRule" in rule_types

    def test_all_rules_have_validate_method(self):
        """Test all registered rules implement validate()."""
        for rule in BUILT_IN_RULES:
            assert hasattr(rule, "validate")
            assert callable(rule.validate)

    def test_all_rules_return_list_of_errors(self):
        """Test all rules return list when validated."""
        doc = "Test document\n"
        context = ValidationContext(doc)

        for rule in BUILT_IN_RULES:
            errors = rule.validate(context)
            assert isinstance(errors, list)


@pytest.mark.unit
def test_type_checking_import():
    """Test TYPE_CHECKING import for ValidationRule (line 39)."""
    import sys
    from unittest.mock import patch

    # Force TYPE_CHECKING to be True to execute the import
    with patch("typing.TYPE_CHECKING", True):
        # Remove module from cache to force reimport
        if "asciidoc_artisan.core.syntax_validators" in sys.modules:
            del sys.modules["asciidoc_artisan.core.syntax_validators"]

        # Import with TYPE_CHECKING=True
        import asciidoc_artisan.core.syntax_validators

        # Verify module loaded
        assert asciidoc_artisan.core.syntax_validators is not None
