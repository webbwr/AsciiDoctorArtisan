"""
Code Action Provider for AsciiDoc LSP.

MA principle: ~150 lines focused on quick fix conversion.

Converts internal QuickFix models to LSP CodeAction format.
Leverages existing diagnostics with fixes from SyntaxChecker.
"""

import logging

from lsprotocol import types as lsp

from asciidoc_artisan.core.syntax_models import QuickFix, TextEdit

logger = logging.getLogger(__name__)


class AsciiDocCodeActionProvider:
    """
    Provides code actions (quick fixes) for AsciiDoc diagnostics.

    Converts internal QuickFix from SyntaxErrorModel.fixes to LSP format.
    Performance: <10ms per diagnostic.
    """

    SOURCE_NAME = "asciidoc-artisan"

    def __init__(self) -> None:
        """Initialize code action provider."""
        self._diagnostic_fixes: dict[str, list[QuickFix]] = {}

    def store_fixes(self, diagnostic_key: str, fixes: list[QuickFix]) -> None:
        """Store fixes for a diagnostic (keyed by line:column:code)."""
        if fixes:
            self._diagnostic_fixes[diagnostic_key] = fixes

    def get_code_actions(
        self,
        uri: str,
        range_: lsp.Range,
        context: lsp.CodeActionContext,
    ) -> list[lsp.CodeAction]:
        """
        Get code actions for diagnostics in range.

        Args:
            uri: Document URI
            range_: Selected range
            context: Code action context with diagnostics

        Returns:
            List of code actions
        """
        actions: list[lsp.CodeAction] = []

        for diagnostic in context.diagnostics:
            if diagnostic.source != self.SOURCE_NAME:
                continue

            key = self._make_key(diagnostic)
            fixes = self._diagnostic_fixes.get(key, [])

            for fix in fixes:
                action = self._convert_fix_to_action(fix, diagnostic, uri)
                if action:
                    actions.append(action)

        return actions

    def _make_key(self, diagnostic: lsp.Diagnostic) -> str:
        """Create lookup key for diagnostic."""
        return f"{diagnostic.range.start.line}:{diagnostic.range.start.character}:{diagnostic.code}"

    def _convert_fix_to_action(
        self,
        fix: QuickFix,
        diagnostic: lsp.Diagnostic,
        uri: str,
    ) -> lsp.CodeAction | None:
        """Convert internal QuickFix to LSP CodeAction."""
        if not fix.edits:
            return None

        text_edits = [self._convert_edit(edit) for edit in fix.edits]

        return lsp.CodeAction(
            title=fix.title,
            kind=lsp.CodeActionKind.QuickFix,
            diagnostics=[diagnostic],
            edit=lsp.WorkspaceEdit(changes={uri: text_edits}),
            is_preferred=len(fix.edits) == 1,
        )

    def _convert_edit(self, edit: TextEdit) -> lsp.TextEdit:
        """Convert internal TextEdit to LSP TextEdit."""
        if isinstance(edit, TextEdit):
            return lsp.TextEdit(
                range=lsp.Range(
                    start=lsp.Position(line=edit.start_line, character=edit.start_column),
                    end=lsp.Position(line=edit.end_line, character=edit.end_column),
                ),
                new_text=edit.new_text,
            )
        return lsp.TextEdit(
            range=lsp.Range(start=lsp.Position(0, 0), end=lsp.Position(0, 0)),
            new_text="",
        )

    def clear_cache(self) -> None:
        """Clear the diagnostic fixes cache."""
        self._diagnostic_fixes.clear()
