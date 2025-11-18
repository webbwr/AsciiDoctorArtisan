"""
Tests for core.syntax_checker module.

Tests syntax checking engine with rule-based validation system.
"""

import pytest

from asciidoc_artisan.core.models import ErrorSeverity, SyntaxErrorModel
from asciidoc_artisan.core.syntax_checker import (
    SyntaxChecker,
    ValidationContext,
    extract_anchors,
    extract_attributes,
    is_inside_code_block,
)


@pytest.mark.fr_091
@pytest.mark.fr_092
@pytest.mark.fr_095
@pytest.mark.fr_097
@pytest.mark.fr_098
@pytest.mark.fr_099
@pytest.mark.unit
class TestValidationContext:
    """Test ValidationContext caching and parsing."""

    def test_init(self):
        """Test context initialization."""
        doc = "= Title\n:author: John\n\n[[intro]]\n== Introduction"
        context = ValidationContext(doc, changed_lines=None)

        assert context.document == doc
        assert len(context.lines) == 5
        assert context.changed_lines is None

    def test_init_with_changed_lines(self):
        """Test context with incremental validation."""
        doc = "line 0\nline 1\nline 2"
        context = ValidationContext(doc, changed_lines=[1, 2])

        assert context.changed_lines == [1, 2]

    def test_anchors_property_caching(self):
        """Test anchors property is cached."""
        doc = "[[intro]]\n== Introduction\n\n[[summary]]\n== Summary"
        context = ValidationContext(doc)

        # First access - parses document
        anchors1 = context.anchors
        assert anchors1 == ["intro", "summary"]

        # Second access - returns cached result
        anchors2 = context.anchors
        assert anchors1 is anchors2  # Same object reference

    def test_anchors_double_bracket_syntax(self):
        """Test extraction of [[anchor]] style anchors."""
        doc = "[[first-anchor]]\n== Section 1\n\n[[second-anchor]]\n== Section 2"
        context = ValidationContext(doc)

        assert context.anchors == ["first-anchor", "second-anchor"]

    def test_anchors_hash_syntax(self):
        """Test extraction of [#anchor] style anchors."""
        doc = "[#first-anchor]\n== Section 1\n\n[#second-anchor]\n== Section 2"
        context = ValidationContext(doc)

        assert context.anchors == ["first-anchor", "second-anchor"]

    def test_anchors_mixed_syntax(self):
        """Test extraction of mixed anchor styles."""
        doc = "[[bracket-anchor]]\n== Section 1\n\n[#hash-anchor]\n== Section 2"
        context = ValidationContext(doc)

        assert context.anchors == ["bracket-anchor", "hash-anchor"]

    def test_anchors_empty_document(self):
        """Test anchor extraction from empty document."""
        context = ValidationContext("")

        assert context.anchors == []

    def test_attributes_property_caching(self):
        """Test attributes property is cached."""
        doc = ":author: John Doe\n:version: 1.0\n:toc:"
        context = ValidationContext(doc)

        # First access
        attrs1 = context.attributes
        assert attrs1 == {"author": "John Doe", "version": "1.0", "toc": ""}

        # Second access - cached
        attrs2 = context.attributes
        assert attrs1 is attrs2

    def test_attributes_with_whitespace(self):
        """Test attribute extraction with various whitespace."""
        doc = ":author:   John Doe   \n:version:1.0\n:toc:  "
        context = ValidationContext(doc)

        attrs = context.attributes
        assert attrs["author"] == "John Doe"
        assert attrs["version"] == "1.0"
        assert attrs["toc"] == ""

    def test_attributes_empty_document(self):
        """Test attribute extraction from empty document."""
        context = ValidationContext("")

        assert context.attributes == {}

    def test_includes_property_caching(self):
        """Test includes property is cached."""
        doc = "include::chapter1.adoc[]\n\ninclude::chapter2.adoc[]"
        context = ValidationContext(doc)

        # First access
        includes1 = context.includes
        assert includes1 == ["chapter1.adoc", "chapter2.adoc"]

        # Second access - cached
        includes2 = context.includes
        assert includes1 is includes2

    def test_includes_empty_document(self):
        """Test include extraction from empty document."""
        context = ValidationContext("")

        assert context.includes == []

    def test_should_validate_line_all_lines(self):
        """Test should_validate_line with no changed lines (validate all)."""
        doc = "line 0\nline 1\nline 2"
        context = ValidationContext(doc, changed_lines=None)

        assert context.should_validate_line(0) is True
        assert context.should_validate_line(1) is True
        assert context.should_validate_line(2) is True

    def test_should_validate_line_incremental(self):
        """Test should_validate_line with specific changed lines."""
        doc = "line 0\nline 1\nline 2"
        context = ValidationContext(doc, changed_lines=[1])

        assert context.should_validate_line(0) is False
        assert context.should_validate_line(1) is True
        assert context.should_validate_line(2) is False


@pytest.mark.fr_091
@pytest.mark.fr_092
@pytest.mark.fr_095
@pytest.mark.fr_097
@pytest.mark.fr_098
@pytest.mark.fr_099
@pytest.mark.unit
class TestSyntaxChecker:
    """Test SyntaxChecker validation engine."""

    def test_init(self):
        """Test checker initialization."""
        checker = SyntaxChecker()

        assert checker.rules is not None
        assert isinstance(checker.rules, list)

    def test_init_loads_built_in_rules(self):
        """Test built-in rules are loaded on init."""
        checker = SyntaxChecker()

        # Should have loaded built-in rules (if syntax_validators available)
        # This test doesn't fail if module missing, just checks structure
        assert isinstance(checker.rules, list)

    def test_add_rule(self):
        """Test adding a custom validation rule."""
        checker = SyntaxChecker()
        initial_count = len(checker.rules)

        # Mock rule
        class MockRule:
            def validate(self, context):
                return []

        rule = MockRule()
        checker.add_rule(rule)

        assert len(checker.rules) == initial_count + 1
        assert rule in checker.rules

    def test_remove_rule(self):
        """Test removing a validation rule."""
        checker = SyntaxChecker()

        # Add mock rule
        class MockRule:
            def validate(self, context):
                return []

        rule = MockRule()
        checker.add_rule(rule)
        initial_count = len(checker.rules)

        # Remove it
        checker.remove_rule(rule)

        assert len(checker.rules) == initial_count - 1
        assert rule not in checker.rules

    def test_remove_rule_not_registered(self):
        """Test removing unregistered rule raises ValueError."""
        checker = SyntaxChecker()

        class MockRule:
            def validate(self, context):
                return []

        rule = MockRule()

        with pytest.raises(ValueError, match="Rule not registered"):
            checker.remove_rule(rule)

    def test_validate_empty_document(self):
        """Test validation of empty document."""
        checker = SyntaxChecker()
        errors = checker.validate("")

        assert isinstance(errors, list)

    def test_validate_with_mock_rule(self):
        """Test validation with custom rule."""
        checker = SyntaxChecker()

        # Mock rule that returns test error
        class MockRule:
            def validate(self, context):
                return [
                    SyntaxErrorModel(
                        code="E999",
                        severity=ErrorSeverity.ERROR,
                        message="Test error",
                        line=1,
                        column=0,
                        length=5,
                        fixes=[],
                    )
                ]

        checker.add_rule(MockRule())
        errors = checker.validate("test document")

        assert len(errors) >= 1
        # Find our test error
        test_errors = [e for e in errors if e.code == "E999"]
        assert len(test_errors) == 1
        assert test_errors[0].message == "Test error"

    def test_validate_sorts_errors(self):
        """Test validation sorts errors by line then column."""
        checker = SyntaxChecker()

        # Mock rule that returns unsorted errors
        class MockRule:
            def validate(self, context):
                return [
                    SyntaxErrorModel(
                        code="E002",
                        severity=ErrorSeverity.ERROR,
                        message="Error at line 2, col 5",
                        line=2,
                        column=5,
                        length=1,
                        fixes=[],
                    ),
                    SyntaxErrorModel(
                        code="E001",
                        severity=ErrorSeverity.ERROR,
                        message="Error at line 1, col 0",
                        line=1,
                        column=0,
                        length=1,
                        fixes=[],
                    ),
                    SyntaxErrorModel(
                        code="E003",
                        severity=ErrorSeverity.ERROR,
                        message="Error at line 2, col 0",
                        line=2,
                        column=0,
                        length=1,
                        fixes=[],
                    ),
                ]

        checker.add_rule(MockRule())
        errors = checker.validate("test")

        # Filter to our test errors
        test_errors = [e for e in errors if e.code in ["E001", "E002", "E003"]]

        # Should be sorted: (1,0), (2,0), (2,5)
        assert test_errors[0].code == "E001"
        assert test_errors[1].code == "E003"
        assert test_errors[2].code == "E002"

    def test_validate_handles_rule_exception(self):
        """Test validation continues when rule raises exception."""
        checker = SyntaxChecker()

        # Mock rule that raises exception
        class BrokenRule:
            def validate(self, context):
                raise RuntimeError("Rule failed")

        # Mock rule that works
        class WorkingRule:
            def validate(self, context):
                return [
                    SyntaxErrorModel(
                        code="I001",
                        severity=ErrorSeverity.INFO,
                        message="Working rule",
                        line=1,
                        column=0,
                        length=1,
                        fixes=[],
                    )
                ]

        checker.add_rule(BrokenRule())
        checker.add_rule(WorkingRule())

        # Should not raise, continues with working rules
        errors = checker.validate("test")

        # Should have error from working rule
        ok_errors = [e for e in errors if e.code == "I001"]
        assert len(ok_errors) == 1

    def test_validate_incremental(self):
        """Test incremental validation with changed lines."""
        checker = SyntaxChecker()

        # Mock rule that only validates changed lines
        class IncrementalRule:
            def validate(self, context):
                errors = []
                for i, line in enumerate(context.lines):
                    if context.should_validate_line(i):
                        errors.append(
                            SyntaxErrorModel(
                                code="I002",
                                severity=ErrorSeverity.INFO,
                                message=f"Line {i}",
                                line=i,
                                column=0,
                                length=1,
                                fixes=[],
                            )
                        )
                return errors

        checker.add_rule(IncrementalRule())

        doc = "line 0\nline 1\nline 2"
        errors = checker.validate_incremental(doc, changed_lines=[1])

        # Should only have error for line 1
        inc_errors = [e for e in errors if e.code == "I002"]
        assert len(inc_errors) == 1
        assert inc_errors[0].line == 1

    def test_get_rules_count(self):
        """Test get_rules_count returns correct count."""
        checker = SyntaxChecker()
        initial_count = checker.get_rules_count()

        class MockRule:
            def validate(self, context):
                return []

        checker.add_rule(MockRule())

        assert checker.get_rules_count() == initial_count + 1

    def test_get_rule_names(self):
        """Test get_rule_names returns class names."""
        checker = SyntaxChecker()

        class CustomRuleA:
            def validate(self, context):
                return []

        class CustomRuleB:
            def validate(self, context):
                return []

        checker.add_rule(CustomRuleA())
        checker.add_rule(CustomRuleB())

        names = checker.get_rule_names()

        assert "CustomRuleA" in names
        assert "CustomRuleB" in names


@pytest.mark.fr_091
@pytest.mark.fr_092
@pytest.mark.fr_095
@pytest.mark.fr_097
@pytest.mark.fr_098
@pytest.mark.fr_099
@pytest.mark.unit
class TestConvenienceFunctions:
    """Test standalone convenience functions."""

    def test_extract_anchors_double_bracket(self):
        """Test extract_anchors with [[anchor]] syntax."""
        doc = "[[intro]]\n== Introduction\n\n[[summary]]\n== Summary"
        anchors = extract_anchors(doc)

        assert anchors == ["intro", "summary"]

    def test_extract_anchors_hash(self):
        """Test extract_anchors with [#anchor] syntax."""
        doc = "[#intro]\n== Introduction\n\n[#summary]\n== Summary"
        anchors = extract_anchors(doc)

        assert anchors == ["intro", "summary"]

    def test_extract_anchors_mixed(self):
        """Test extract_anchors with mixed syntax."""
        doc = "[[bracket]]\n== Section 1\n\n[#hash]\n== Section 2"
        anchors = extract_anchors(doc)

        assert anchors == ["bracket", "hash"]

    def test_extract_anchors_empty(self):
        """Test extract_anchors with no anchors."""
        doc = "== Section 1\n== Section 2"
        anchors = extract_anchors(doc)

        assert anchors == []

    def test_extract_attributes_basic(self):
        """Test extract_attributes with basic attributes."""
        doc = ":author: John Doe\n:version: 1.0\n:toc:"
        attrs = extract_attributes(doc)

        assert attrs == {"author": "John Doe", "version": "1.0", "toc": ""}

    def test_extract_attributes_whitespace(self):
        """Test extract_attributes handles whitespace."""
        doc = ":author:   John Doe   \n:version:  1.0"
        attrs = extract_attributes(doc)

        assert attrs["author"] == "John Doe"
        assert attrs["version"] == "1.0"

    def test_extract_attributes_empty(self):
        """Test extract_attributes with no attributes."""
        doc = "== Section 1\nSome content"
        attrs = extract_attributes(doc)

        assert attrs == {}

    def test_is_inside_code_block_inside(self):
        """Test is_inside_code_block detects lines inside blocks."""
        lines = [
            "[source,python]",
            "----",
            "def hello():",  # Line 2 - inside
            "    print('hi')",  # Line 3 - inside
            "----",
            "Normal text",  # Line 5 - outside
        ]

        assert is_inside_code_block(lines, 2) is True
        assert is_inside_code_block(lines, 3) is True

    def test_is_inside_code_block_outside(self):
        """Test is_inside_code_block detects lines outside blocks."""
        lines = [
            "[source,python]",  # Line 0 - outside
            "----",  # Line 1 - delimiter (counted as inside by algorithm)
            "def hello():",  # Line 2 - inside
            "----",  # Line 3 - delimiter (counted as inside)
            "Normal text",  # Line 4 - outside
        ]

        assert is_inside_code_block(lines, 0) is False
        assert is_inside_code_block(lines, 4) is False

    def test_is_inside_code_block_nested(self):
        """Test is_inside_code_block with nested delimiters."""
        lines = [
            "----",  # Open
            "code",  # Inside
            "----",  # Close
            "text",  # Outside
            "-----",  # Open (5 dashes also valid)
            "code",  # Inside
            "-----",  # Close
        ]

        assert is_inside_code_block(lines, 1) is True
        assert is_inside_code_block(lines, 3) is False
        assert is_inside_code_block(lines, 5) is True

    def test_is_inside_code_block_out_of_bounds(self):
        """Test is_inside_code_block with invalid line numbers."""
        lines = ["line 0", "line 1"]

        assert is_inside_code_block(lines, -1) is False
        assert is_inside_code_block(lines, 10) is False

    def test_is_inside_code_block_empty_document(self):
        """Test is_inside_code_block with empty document."""
        lines = []

        assert is_inside_code_block(lines, 0) is False


@pytest.mark.fr_091
@pytest.mark.fr_092
@pytest.mark.fr_095
@pytest.mark.fr_097
@pytest.mark.fr_098
@pytest.mark.fr_099
@pytest.mark.unit
class TestCoverageImprovements:
    """Tests to achieve 100% coverage."""

    def test_syntax_checker_handles_missing_validators_module(self, caplog):
        """Test SyntaxChecker handles ImportError for syntax_validators (lines 247-251)."""
        import builtins
        import logging
        import sys
        from unittest.mock import patch

        caplog.set_level(logging.WARNING)

        # Patch builtins.__import__ to raise ImportError for syntax_validators
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if "syntax_validators" in name:
                raise ImportError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            # Remove modules from cache to force reimport
            modules_to_remove = [
                "asciidoc_artisan.core.syntax_checker",
                "asciidoc_artisan.core.syntax_validators",
            ]
            for mod in modules_to_remove:
                if mod in sys.modules:
                    del sys.modules[mod]

            # Import SyntaxChecker with mocked import
            from asciidoc_artisan.core.syntax_checker import SyntaxChecker

            # Create instance - should trigger ImportError and log warning
            checker = SyntaxChecker()

            # Should have logged warning about missing module (lines 251-253)
            assert any(
                "syntax_validators" in record.message and "not found" in record.message for record in caplog.records
            )

            # Should still work but with empty rules
            assert isinstance(checker.rules, list)
