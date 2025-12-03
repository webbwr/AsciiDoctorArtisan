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
