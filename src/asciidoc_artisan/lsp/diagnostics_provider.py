"""
Diagnostics Provider for AsciiDoc LSP.

MA principle: ~180 lines focused on diagnostics/validation logic.

Provides real-time syntax validation using the existing SyntaxChecker.
Converts internal SyntaxErrorModel to LSP Diagnostic format.

Features:
- Leverages existing syntax validation rules
- Converts severity levels to LSP format
- Supports incremental validation
- Quick fix support (future)
"""

import logging

from lsprotocol import types as lsp

from asciidoc_artisan.core.syntax_checker import SyntaxChecker
from asciidoc_artisan.core.syntax_models import ErrorSeverity, SyntaxErrorModel

logger = logging.getLogger(__name__)


class AsciiDocDiagnosticsProvider:
    """
    Provides diagnostics (syntax errors) for AsciiDoc documents.

    Uses the existing SyntaxChecker from core module and converts
    results to LSP Diagnostic format.

    Attributes:
        _checker: SyntaxChecker instance
        _source: Diagnostic source identifier

    Performance: <100ms for 1000-line documents.
    """

    SOURCE_NAME = "asciidoc-artisan"

    def __init__(self) -> None:
        """Initialize diagnostics provider."""
        self._checker = SyntaxChecker()
        logger.info(f"DiagnosticsProvider initialized with {self._checker.get_rules_count()} rules")

    def get_diagnostics(self, text: str) -> list[lsp.Diagnostic]:
        """
        Validate document and return diagnostics.

        Args:
            text: Document text

        Returns:
            List of LSP diagnostics
        """
        try:
            # Run syntax checker
            errors = self._checker.validate(text)

            # Convert to LSP diagnostics
            diagnostics = [self._convert_error(error) for error in errors]

            logger.debug(f"Diagnostics: {len(diagnostics)} issues found")
            return diagnostics

        except Exception as e:
            logger.error(f"Diagnostics failed: {e}", exc_info=True)
            return []

    def get_diagnostics_incremental(self, text: str, changed_lines: list[int]) -> list[lsp.Diagnostic]:
        """
        Validate only changed lines (incremental).

        Args:
            text: Document text
            changed_lines: List of changed line numbers (0-indexed)

        Returns:
            List of LSP diagnostics
        """
        try:
            errors = self._checker.validate_incremental(text, changed_lines)
            return [self._convert_error(error) for error in errors]
        except Exception as e:
            logger.error(f"Incremental diagnostics failed: {e}", exc_info=True)
            return []

    def _convert_error(self, error: SyntaxErrorModel) -> lsp.Diagnostic:
        """
        Convert internal error model to LSP Diagnostic.

        Args:
            error: Internal SyntaxErrorModel

        Returns:
            LSP Diagnostic
        """
        # Map severity
        severity = self._map_severity(error.severity)

        # Create range (end column = start + length)
        range_ = lsp.Range(
            start=lsp.Position(line=error.line, character=error.column),
            end=lsp.Position(line=error.line, character=error.column + error.length),
        )

        # Create diagnostic
        diagnostic = lsp.Diagnostic(
            range=range_,
            message=error.message,
            severity=severity,
            code=error.code,
            source=self.SOURCE_NAME,
        )

        return diagnostic

    def _map_severity(self, severity: ErrorSeverity) -> lsp.DiagnosticSeverity:
        """
        Map internal severity to LSP severity.

        Args:
            severity: Internal ErrorSeverity

        Returns:
            LSP DiagnosticSeverity
        """
        mapping = {
            ErrorSeverity.ERROR: lsp.DiagnosticSeverity.Error,
            ErrorSeverity.WARNING: lsp.DiagnosticSeverity.Warning,
            ErrorSeverity.INFO: lsp.DiagnosticSeverity.Information,
        }
        return mapping.get(severity, lsp.DiagnosticSeverity.Information)

    def get_quick_fixes(self, text: str, diagnostic: lsp.Diagnostic) -> list[lsp.CodeAction]:
        """
        Get quick fixes for a diagnostic (future).

        Args:
            text: Document text
            diagnostic: LSP Diagnostic

        Returns:
            List of code actions (fixes)
        """
        # TODO: Implement quick fix conversion from SyntaxErrorModel.fixes
        return []
