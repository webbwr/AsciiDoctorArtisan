"""
Tests for AsciiDoc LSP diagnostics provider.

Tests cover:
- Syntax validation using existing SyntaxChecker
- Conversion to LSP Diagnostic format
- Severity mapping
- Incremental validation
"""

import pytest
from lsprotocol import types as lsp

from asciidoc_artisan.lsp.diagnostics_provider import AsciiDocDiagnosticsProvider


@pytest.fixture
def provider() -> AsciiDocDiagnosticsProvider:
    """Create diagnostics provider instance."""
    return AsciiDocDiagnosticsProvider()


class TestDiagnosticsProvider:
    """Test diagnostics provider."""

    def test_provider_initialization(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test provider initializes with rules."""
        # Should have syntax checker with rules
        assert provider._checker is not None
        assert provider._checker.get_rules_count() > 0

    def test_valid_document_no_diagnostics(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test valid document returns no errors."""
        text = """= Document Title
Author Name

== Introduction

This is a valid AsciiDoc document.
"""
        diagnostics = provider.get_diagnostics(text)

        # Valid document should have few or no errors
        # (some style warnings may be present)
        error_diagnostics = [d for d in diagnostics if d.severity == lsp.DiagnosticSeverity.Error]
        assert len(error_diagnostics) == 0

    def test_diagnostic_structure(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test diagnostics have correct LSP structure."""
        text = "= Title\n"

        diagnostics = provider.get_diagnostics(text)

        # Each diagnostic should have required fields
        for diag in diagnostics:
            assert hasattr(diag, "range")
            assert hasattr(diag, "message")
            assert hasattr(diag, "severity")
            assert hasattr(diag, "source")
            assert diag.source == "asciidoc-artisan"

    def test_diagnostic_range(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test diagnostic range is valid."""
        text = "= Title\n"

        diagnostics = provider.get_diagnostics(text)

        for diag in diagnostics:
            # Range should have valid positions
            assert diag.range.start.line >= 0
            assert diag.range.start.character >= 0
            assert diag.range.end.line >= diag.range.start.line


class TestSeverityMapping:
    """Test severity level mapping."""

    def test_error_severity(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test ERROR maps to LSP Error."""
        from asciidoc_artisan.core.syntax_models import ErrorSeverity

        severity = provider._map_severity(ErrorSeverity.ERROR)
        assert severity == lsp.DiagnosticSeverity.Error

    def test_warning_severity(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test WARNING maps to LSP Warning."""
        from asciidoc_artisan.core.syntax_models import ErrorSeverity

        severity = provider._map_severity(ErrorSeverity.WARNING)
        assert severity == lsp.DiagnosticSeverity.Warning

    def test_info_severity(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test INFO maps to LSP Information."""
        from asciidoc_artisan.core.syntax_models import ErrorSeverity

        severity = provider._map_severity(ErrorSeverity.INFO)
        assert severity == lsp.DiagnosticSeverity.Information


class TestIncrementalValidation:
    """Test incremental validation."""

    def test_incremental_validation(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test incremental validation for changed lines."""
        text = """= Title

Line 1
Line 2
Line 3
"""
        # Validate only lines 2 and 3
        diagnostics = provider.get_diagnostics_incremental(text, [2, 3])

        # Should return list (may be empty for valid content)
        assert isinstance(diagnostics, list)


class TestErrorHandling:
    """Test error handling."""

    def test_empty_document(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test handling of empty document."""
        diagnostics = provider.get_diagnostics("")

        # Should not crash
        assert isinstance(diagnostics, list)

    def test_malformed_document(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test handling of malformed document."""
        text = "= Title without newline"

        diagnostics = provider.get_diagnostics(text)

        # Should not crash, may return warnings
        assert isinstance(diagnostics, list)


class TestQuickFixes:
    """Test quick fix functionality."""

    def test_get_quick_fixes_no_cache(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test quick fixes returns empty when no errors cached."""
        # Create a mock diagnostic
        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=0, character=10),
            ),
            message="Test error",
            code="E001",
        )

        # No diagnostics run yet, cache is empty
        fixes = provider.get_quick_fixes("file:///test.adoc", diagnostic)
        assert fixes == []

    def test_get_quick_fixes_no_matching_error(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test quick fixes returns empty when no matching error."""
        # Run diagnostics to populate cache
        text = "= Title\n"
        provider.get_diagnostics(text)

        # Create a diagnostic that doesn't match any cached error
        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=99, character=0),
                end=lsp.Position(line=99, character=10),
            ),
            message="Non-existent error",
            code="X999",
        )

        fixes = provider.get_quick_fixes("file:///test.adoc", diagnostic)
        assert fixes == []

    def test_find_matching_error(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test finding matching error in cache."""
        from asciidoc_artisan.core.syntax_models import ErrorSeverity, SyntaxErrorModel

        # Manually populate cache
        error = SyntaxErrorModel(
            code="E001",
            severity=ErrorSeverity.ERROR,
            message="Test error",
            line=5,
            column=0,
            length=10,
            fixes=[],
        )
        provider._errors_cache = [error]

        # Create matching diagnostic
        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=5, character=0),
                end=lsp.Position(line=5, character=10),
            ),
            message="Test error",
            code="E001",
        )

        match = provider._find_matching_error(diagnostic)
        assert match is not None
        assert match.code == "E001"
        assert match.line == 5

    def test_find_matching_error_no_match(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test no match when error doesn't exist."""
        from asciidoc_artisan.core.syntax_models import ErrorSeverity, SyntaxErrorModel

        # Manually populate cache
        error = SyntaxErrorModel(
            code="E001",
            severity=ErrorSeverity.ERROR,
            message="Test error",
            line=5,
            column=0,
            length=10,
            fixes=[],
        )
        provider._errors_cache = [error]

        # Create non-matching diagnostic (different line)
        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=10, character=0),
                end=lsp.Position(line=10, character=10),
            ),
            message="Test error",
            code="E001",
        )

        match = provider._find_matching_error(diagnostic)
        assert match is None

    def test_convert_quick_fix(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test converting QuickFix to LSP CodeAction."""
        from asciidoc_artisan.core.syntax_models import QuickFix, TextEdit

        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=5, character=0),
                end=lsp.Position(line=5, character=10),
            ),
            message="Test error",
            code="E001",
        )

        fix = QuickFix(
            title="Add closing delimiter",
            edits=[
                TextEdit(
                    start_line=5,
                    start_column=10,
                    end_line=5,
                    end_column=10,
                    new_text="----",  # Note: str_strip_whitespace strips trailing newlines
                )
            ],
        )

        action = provider._convert_quick_fix("file:///test.adoc", diagnostic, fix)

        assert action is not None
        assert action.title == "Add closing delimiter"
        assert action.kind == lsp.CodeActionKind.QuickFix
        assert action.diagnostics == [diagnostic]
        assert action.edit is not None
        assert action.edit.changes is not None
        assert "file:///test.adoc" in action.edit.changes

        # Verify text edit
        edits = action.edit.changes["file:///test.adoc"]
        assert len(edits) == 1
        assert edits[0].new_text == "----"
        assert edits[0].range.start.line == 5
        assert edits[0].range.start.character == 10

    def test_get_quick_fixes_with_fixes(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test getting quick fixes for error with fixes."""
        from asciidoc_artisan.core.syntax_models import (
            ErrorSeverity,
            QuickFix,
            SyntaxErrorModel,
            TextEdit,
        )

        # Create error with fixes
        fix = QuickFix(
            title="Fix the issue",
            edits=[
                TextEdit(
                    start_line=5,
                    start_column=0,
                    end_line=5,
                    end_column=5,
                    new_text="fixed",
                )
            ],
        )
        error = SyntaxErrorModel(
            code="E001",
            severity=ErrorSeverity.ERROR,
            message="Test error",
            line=5,
            column=0,
            length=5,
            fixes=[fix],
        )
        provider._errors_cache = [error]

        # Create matching diagnostic
        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=5, character=0),
                end=lsp.Position(line=5, character=5),
            ),
            message="Test error",
            code="E001",
        )

        actions = provider.get_quick_fixes("file:///test.adoc", diagnostic)

        assert len(actions) == 1
        assert actions[0].title == "Fix the issue"
        assert actions[0].kind == lsp.CodeActionKind.QuickFix

    def test_diagnostics_cache_population(self, provider: AsciiDocDiagnosticsProvider) -> None:
        """Test that get_diagnostics populates the cache."""
        # Initially cache should be empty
        assert provider._errors_cache == []

        # Run diagnostics
        text = "= Title\n\nSome content."
        provider.get_diagnostics(text)

        # Cache should be a list (may be empty for valid content)
        assert isinstance(provider._errors_cache, list)
