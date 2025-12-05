"""
Diagnostics Provider for AsciiDoc LSP.

MA principle: ~180 lines focused on diagnostics/validation logic.

Provides real-time syntax validation using the existing SyntaxChecker.
Converts internal SyntaxErrorModel to LSP Diagnostic format.

Features:
- Leverages existing syntax validation rules
- Converts severity levels to LSP format
- Supports incremental validation
- Quick fix support with TextEdit conversion
"""

import logging

from lsprotocol import types as lsp

from asciidoc_artisan.core.syntax_checker import SyntaxChecker
from asciidoc_artisan.core.syntax_models import (
    ErrorSeverity,
    QuickFix,
    SyntaxErrorModel,
)

logger = logging.getLogger(__name__)


class AsciiDocDiagnosticsProvider:
    """
    Provides diagnostics (syntax errors) for AsciiDoc documents.

    Uses the existing SyntaxChecker from core module and converts
    results to LSP Diagnostic format.

    Attributes:
        _checker: SyntaxChecker instance
        _errors_cache: Cache of SyntaxErrorModel for quick fix lookup

    Performance: <100ms for 1000-line documents.
    """

    SOURCE_NAME = "asciidoc-artisan"

    def __init__(self) -> None:
        """Initialize diagnostics provider."""
        self._checker = SyntaxChecker()
        self._errors_cache: list[SyntaxErrorModel] = []
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

            # Cache errors for quick fix lookup
            self._errors_cache = errors

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

    def get_quick_fixes(self, uri: str, diagnostic: lsp.Diagnostic) -> list[lsp.CodeAction]:
        """
        Get quick fixes for a diagnostic.

        Finds the matching cached error and converts its QuickFix objects
        to LSP CodeAction format.

        Args:
            uri: Document URI for workspace edit
            diagnostic: LSP Diagnostic to find fixes for

        Returns:
            List of code actions (quick fixes)
        """
        try:
            # Find matching error in cache by code and position
            matching_error = self._find_matching_error(diagnostic)
            if not matching_error or not matching_error.fixes:
                return []

            # Convert each QuickFix to LSP CodeAction
            actions: list[lsp.CodeAction] = []
            for fix in matching_error.fixes:
                action = self._convert_quick_fix(uri, diagnostic, fix)
                if action:
                    actions.append(action)

            logger.debug(f"Quick fixes: {len(actions)} actions for {diagnostic.code}")
            return actions

        except Exception as e:
            logger.error(f"Quick fix lookup failed: {e}", exc_info=True)
            return []

    def _find_matching_error(self, diagnostic: lsp.Diagnostic) -> SyntaxErrorModel | None:
        """
        Find cached error matching the diagnostic.

        Args:
            diagnostic: LSP Diagnostic to match

        Returns:
            Matching SyntaxErrorModel or None
        """
        for error in self._errors_cache:
            # Match by code and line position
            if error.code == diagnostic.code and error.line == diagnostic.range.start.line:
                return error
        return None

    def _convert_quick_fix(self, uri: str, diagnostic: lsp.Diagnostic, fix: QuickFix) -> lsp.CodeAction | None:
        """
        Convert QuickFix to LSP CodeAction.

        Args:
            uri: Document URI
            diagnostic: Associated diagnostic
            fix: QuickFix to convert

        Returns:
            LSP CodeAction or None on error
        """
        try:
            # Convert TextEdit list to LSP TextEdit list
            text_edits: list[lsp.TextEdit] = []
            for edit in fix.edits:
                lsp_edit = lsp.TextEdit(
                    range=lsp.Range(
                        start=lsp.Position(line=edit.start_line, character=edit.start_column),
                        end=lsp.Position(line=edit.end_line, character=edit.end_column),
                    ),
                    new_text=edit.new_text,
                )
                text_edits.append(lsp_edit)

            # Create workspace edit with document changes
            workspace_edit = lsp.WorkspaceEdit(changes={uri: text_edits})

            # Create code action
            return lsp.CodeAction(
                title=fix.title,
                kind=lsp.CodeActionKind.QuickFix,
                diagnostics=[diagnostic],
                edit=workspace_edit,
            )

        except Exception as e:
            logger.error(f"Quick fix conversion failed: {e}", exc_info=True)
            return None
