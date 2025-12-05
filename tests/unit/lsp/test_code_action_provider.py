"""
Tests for AsciiDoc LSP code action provider.

Tests cover:
- Quick fix conversion from internal QuickFix to LSP CodeAction
- Diagnostic key generation
- Cache management
"""

import pytest
from lsprotocol import types as lsp

from asciidoc_artisan.core.syntax_models import QuickFix, TextEdit
from asciidoc_artisan.lsp.code_action_provider import AsciiDocCodeActionProvider


@pytest.fixture
def provider() -> AsciiDocCodeActionProvider:
    """Create code action provider instance."""
    return AsciiDocCodeActionProvider()


class TestQuickFixStorage:
    """Test storing and retrieving quick fixes."""

    def test_store_fixes(self, provider: AsciiDocCodeActionProvider) -> None:
        """Test storing fixes for a diagnostic."""
        fix = QuickFix(
            title="Fix typo",
            edits=[TextEdit(start_line=0, start_column=5, end_line=0, end_column=8, new_text="the")],
        )
        provider.store_fixes("0:5:typo", [fix])

        assert "0:5:typo" in provider._diagnostic_fixes

    def test_store_empty_fixes_not_stored(self, provider: AsciiDocCodeActionProvider) -> None:
        """Test that empty fix list is not stored."""
        provider.store_fixes("0:0:empty", [])

        assert "0:0:empty" not in provider._diagnostic_fixes

    def test_clear_cache(self, provider: AsciiDocCodeActionProvider) -> None:
        """Test clearing the diagnostic fixes cache."""
        fix = QuickFix(
            title="Fix",
            edits=[TextEdit(start_line=0, start_column=0, end_line=0, end_column=1, new_text="x")],
        )
        provider.store_fixes("0:0:test", [fix])
        provider.clear_cache()

        assert len(provider._diagnostic_fixes) == 0


class TestCodeActionGeneration:
    """Test code action generation from diagnostics."""

    def test_get_code_actions_with_fixes(self, provider: AsciiDocCodeActionProvider) -> None:
        """Test generating code actions for diagnostics with fixes."""
        fix = QuickFix(
            title="Replace 'teh' with 'the'",
            edits=[TextEdit(start_line=0, start_column=5, end_line=0, end_column=8, new_text="the")],
        )
        provider.store_fixes("0:5:typo", [fix])

        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=0, character=5),
                end=lsp.Position(line=0, character=8),
            ),
            message="Typo",
            code="typo",
            source="asciidoc-artisan",
        )
        context = lsp.CodeActionContext(diagnostics=[diagnostic])

        actions = provider.get_code_actions(
            "file:///test.adoc",
            lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=0, character=10),
            ),
            context,
        )

        assert len(actions) == 1
        assert actions[0].title == "Replace 'teh' with 'the'"
        assert actions[0].kind == lsp.CodeActionKind.QuickFix

    def test_get_code_actions_no_fixes(self, provider: AsciiDocCodeActionProvider) -> None:
        """Test no actions when no fixes stored."""
        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=0, character=5),
            ),
            message="Error",
            code="error",
            source="asciidoc-artisan",
        )
        context = lsp.CodeActionContext(diagnostics=[diagnostic])

        actions = provider.get_code_actions(
            "file:///test.adoc",
            lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=0, character=10),
            ),
            context,
        )

        assert len(actions) == 0

    def test_ignore_other_sources(self, provider: AsciiDocCodeActionProvider) -> None:
        """Test diagnostics from other sources are ignored."""
        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=0, character=5),
            ),
            message="Error",
            source="other-tool",
        )
        context = lsp.CodeActionContext(diagnostics=[diagnostic])

        actions = provider.get_code_actions(
            "file:///test.adoc",
            lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=0, character=10),
            ),
            context,
        )

        assert len(actions) == 0


class TestCodeActionFormat:
    """Test code action format and content."""

    def test_code_action_has_workspace_edit(self, provider: AsciiDocCodeActionProvider) -> None:
        """Test code action includes workspace edit."""
        fix = QuickFix(
            title="Fix",
            edits=[TextEdit(start_line=1, start_column=0, end_line=1, end_column=4, new_text="test")],
        )
        provider.store_fixes("1:0:fix", [fix])

        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=1, character=0),
                end=lsp.Position(line=1, character=4),
            ),
            message="Fix needed",
            code="fix",
            source="asciidoc-artisan",
        )
        context = lsp.CodeActionContext(diagnostics=[diagnostic])

        actions = provider.get_code_actions(
            "file:///test.adoc",
            lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=2, character=0),
            ),
            context,
        )

        assert len(actions) == 1
        assert actions[0].edit is not None
        assert "file:///test.adoc" in actions[0].edit.changes

    def test_single_edit_is_preferred(self, provider: AsciiDocCodeActionProvider) -> None:
        """Test single edit actions are marked as preferred."""
        fix = QuickFix(
            title="Quick fix",
            edits=[TextEdit(start_line=0, start_column=0, end_line=0, end_column=1, new_text="x")],
        )
        provider.store_fixes("0:0:test", [fix])

        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=0, character=1),
            ),
            message="Test",
            code="test",
            source="asciidoc-artisan",
        )
        context = lsp.CodeActionContext(diagnostics=[diagnostic])

        actions = provider.get_code_actions(
            "file:///test.adoc",
            lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=0, character=1),
            ),
            context,
        )

        assert actions[0].is_preferred is True

    def test_empty_edits_skipped(self, provider: AsciiDocCodeActionProvider) -> None:
        """Test fixes with no edits are skipped."""
        fix = QuickFix(title="No edits", edits=[])
        provider.store_fixes("0:0:empty", [fix])

        diagnostic = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=0, character=1),
            ),
            message="Test",
            code="empty",
            source="asciidoc-artisan",
        )
        context = lsp.CodeActionContext(diagnostics=[diagnostic])

        actions = provider.get_code_actions(
            "file:///test.adoc",
            lsp.Range(
                start=lsp.Position(line=0, character=0),
                end=lsp.Position(line=0, character=1),
            ),
            context,
        )

        assert len(actions) == 0
