"""Tests for ui.ui_state_manager module."""

from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_editor(qapp):
    """Create a mock editor with all required attributes for UIStateManager."""
    editor = Mock()

    # Action manager with all actions
    editor.action_manager = Mock()

    # Save actions
    editor.action_manager.save_act = Mock()
    editor.action_manager.save_as_act = Mock()

    # Export actions
    editor.action_manager.save_as_adoc_act = Mock()
    editor.action_manager.save_as_md_act = Mock()
    editor.action_manager.save_as_docx_act = Mock()
    editor.action_manager.save_as_html_act = Mock()
    editor.action_manager.save_as_pdf_act = Mock()

    # Git actions
    editor.action_manager.git_commit_act = Mock()
    editor.action_manager.git_pull_act = Mock()
    editor.action_manager.git_push_act = Mock()

    # Convert action
    editor.action_manager.convert_paste_act = Mock()

    # File operations manager
    editor.file_operations_manager = Mock()
    editor.file_operations_manager._is_processing_pandoc = False

    # Processing states
    editor._is_processing_git = False

    # Settings
    editor._settings = Mock()
    editor._settings.git_repo_path = "/path/to/repo"
    editor._settings.ollama_enabled = False
    editor._settings.ollama_model = None

    # Status manager
    editor.status_manager = Mock()
    editor.status_manager.set_ai_model = Mock()

    return editor


@pytest.mark.unit
class TestUIStateManagerBasics:
    """Test suite for UIStateManager basic functionality."""

    def test_import(self):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        assert UIStateManager is not None

    def test_creation(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)
        assert manager is not None

    def test_stores_editor_reference(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)
        assert manager.editor == mock_editor

    def test_has_update_methods(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)
        assert hasattr(manager, "update_ui_state")
        assert hasattr(manager, "update_ai_status_bar")
        assert callable(manager.update_ui_state)
        assert callable(manager.update_ai_status_bar)


@pytest.mark.unit
class TestSaveActionsState:
    """Test suite for save/save-as action state management."""

    def test_save_actions_enabled_when_not_processing(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # Save actions should be enabled
        mock_editor.action_manager.save_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.save_as_act.setEnabled.assert_called_with(True)

    def test_save_actions_disabled_when_processing_pandoc(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = True
        manager.update_ui_state()

        # Save actions should be disabled
        mock_editor.action_manager.save_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.save_as_act.setEnabled.assert_called_with(False)


@pytest.mark.unit
class TestExportActionsState:
    """Test suite for export action state management."""

    def test_export_actions_enabled_when_not_processing(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # AsciiDoc export should always be enabled when not processing
        mock_editor.action_manager.save_as_adoc_act.setEnabled.assert_called_with(True)
        # HTML export doesn't require Pandoc
        mock_editor.action_manager.save_as_html_act.setEnabled.assert_called_with(True)

    def test_export_actions_disabled_when_processing_pandoc(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = True
        manager.update_ui_state()

        # All export actions should be disabled
        mock_editor.action_manager.save_as_adoc_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.save_as_html_act.setEnabled.assert_called_with(False)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_pandoc_exports_enabled_when_pandoc_available(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # Pandoc-dependent exports should be enabled
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.save_as_docx_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.save_as_pdf_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=False
    )
    def test_pandoc_exports_disabled_when_pandoc_unavailable(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # Pandoc-dependent exports should be disabled
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.save_as_docx_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.save_as_pdf_act.setEnabled.assert_called_with(False)


@pytest.mark.unit
class TestGitActionsState:
    """Test suite for Git action state management."""

    def test_git_actions_enabled_when_repo_and_not_processing(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.git_repo_path = "/path/to/repo"
        mock_editor._is_processing_git = False
        manager.update_ui_state()

        # Git actions should be enabled
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.git_pull_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.git_push_act.setEnabled.assert_called_with(True)

    def test_git_actions_disabled_when_processing_git(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.git_repo_path = "/path/to/repo"
        mock_editor._is_processing_git = True
        manager.update_ui_state()

        # Git actions should be disabled during processing
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.git_pull_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.git_push_act.setEnabled.assert_called_with(False)

    def test_git_actions_disabled_when_no_repo(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.git_repo_path = None
        mock_editor._is_processing_git = False
        manager.update_ui_state()

        # Git actions should be disabled without repo
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.git_pull_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.git_push_act.setEnabled.assert_called_with(False)

    def test_git_actions_disabled_when_empty_repo_path(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.git_repo_path = ""
        mock_editor._is_processing_git = False
        manager.update_ui_state()

        # Git actions should be disabled with empty path
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(False)


@pytest.mark.unit
class TestConvertPasteAction:
    """Test suite for convert and paste action state."""

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_convert_paste_enabled_when_pandoc_available_and_not_processing(
        self, mock_editor
    ):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # Convert paste should be enabled
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=False
    )
    def test_convert_paste_disabled_when_pandoc_unavailable(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # Convert paste should be disabled without Pandoc
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called_with(
            False
        )

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_convert_paste_disabled_when_processing_pandoc(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = True
        manager.update_ui_state()

        # Convert paste should be disabled during processing
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called_with(
            False
        )


@pytest.mark.unit
class TestAIStatusBar:
    """Test suite for AI status bar updates."""

    def test_shows_pandoc_when_ollama_disabled(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.ollama_enabled = False
        manager.update_ai_status_bar()

        # Should show Pandoc as conversion method
        mock_editor.status_manager.set_ai_model.assert_called_with("Pandoc")

    def test_shows_ollama_model_when_enabled(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.ollama_enabled = True
        mock_editor._settings.ollama_model = "llama2"
        manager.update_ai_status_bar()

        # Should show Ollama model name
        mock_editor.status_manager.set_ai_model.assert_called_with("llama2")

    def test_shows_pandoc_when_ollama_enabled_but_no_model(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.ollama_enabled = True
        mock_editor._settings.ollama_model = None
        manager.update_ai_status_bar()

        # Should show Pandoc when no model selected
        mock_editor.status_manager.set_ai_model.assert_called_with("Pandoc")

    def test_shows_pandoc_when_ollama_enabled_but_empty_model(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.ollama_enabled = True
        mock_editor._settings.ollama_model = ""
        manager.update_ai_status_bar()

        # Should show Pandoc when model name is empty
        mock_editor.status_manager.set_ai_model.assert_called_with("Pandoc")


@pytest.mark.unit
class TestUpdateUIStateIntegration:
    """Test suite for update_ui_state integration."""

    def test_update_ui_state_calls_update_ai_status_bar(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        with patch.object(manager, "update_ai_status_bar") as mock_update_ai:
            manager.update_ui_state()
            mock_update_ai.assert_called_once()

    def test_update_ui_state_updates_all_action_groups(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        manager.update_ui_state()

        # Verify all action groups were updated
        mock_editor.action_manager.save_act.setEnabled.assert_called()
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called()
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called()
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called()


@pytest.mark.unit
class TestCheckPandocAvailability:
    """Test suite for check_pandoc_availability method."""

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_returns_true_when_pandoc_available(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        result = manager.check_pandoc_availability("Test operation")

        # Should return True and not show error
        assert result is True
        mock_editor.status_manager.show_message.assert_not_called()

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=False
    )
    def test_returns_false_when_pandoc_unavailable(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        result = manager.check_pandoc_availability("Test operation")

        # Should return False
        assert result is False

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=False
    )
    def test_shows_error_dialog_when_unavailable(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        manager.check_pandoc_availability("Test operation")

        # Should show critical error dialog
        mock_editor.status_manager.show_message.assert_called_once()
        call_args = mock_editor.status_manager.show_message.call_args
        assert call_args[0][0] == "critical"

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=False
    )
    def test_error_message_includes_context(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        context = "Exporting to DOCX"
        manager.check_pandoc_availability(context)

        # Error message should include context
        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert context in call_args

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=False
    )
    def test_error_message_includes_installation_instructions(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        manager.check_pandoc_availability("Test")

        # Should include installation instructions
        call_args = str(mock_editor.status_manager.show_message.call_args)
        assert "https://pandoc.org" in call_args
        assert "pip install pypandoc" in call_args


@pytest.mark.unit
class TestConcurrentProcessingStates:
    """Test suite for concurrent Git and Pandoc processing."""

    def test_both_processing_disables_all_actions(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Both processing active
        mock_editor._is_processing_git = True
        mock_editor.file_operations_manager._is_processing_pandoc = True
        mock_editor._settings.git_repo_path = "/path/to/repo"
        manager.update_ui_state()

        # Save actions disabled
        mock_editor.action_manager.save_act.setEnabled.assert_called_with(False)
        # Git actions disabled
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(False)
        # Export actions disabled
        mock_editor.action_manager.save_as_adoc_act.setEnabled.assert_called_with(False)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_git_processing_does_not_affect_export_actions(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Only Git processing
        mock_editor._is_processing_git = True
        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # Export actions should still be enabled (Pandoc not processing)
        mock_editor.action_manager.save_as_adoc_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(True)

    def test_pandoc_processing_does_not_affect_git_actions(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Only Pandoc processing
        mock_editor._is_processing_git = False
        mock_editor.file_operations_manager._is_processing_pandoc = True
        mock_editor._settings.git_repo_path = "/path/to/repo"
        manager.update_ui_state()

        # Git actions should still be enabled (repo available, not processing Git)
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.git_pull_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_processing_states_are_independent(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Neither processing
        mock_editor._is_processing_git = False
        mock_editor.file_operations_manager._is_processing_pandoc = False
        mock_editor._settings.git_repo_path = "/path/to/repo"
        manager.update_ui_state()

        # Both Git and export should be enabled
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_actions_reenable_when_both_processing_complete(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.git_repo_path = "/path/to/repo"

        # Start with both processing
        mock_editor._is_processing_git = True
        mock_editor.file_operations_manager._is_processing_pandoc = True
        manager.update_ui_state()

        # Complete processing
        mock_editor._is_processing_git = False
        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # All actions should be re-enabled
        mock_editor.action_manager.save_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(True)


@pytest.mark.unit
class TestAllExportActions:
    """Test suite for individual export action requirements."""

    def test_asciidoc_export_always_enabled_no_pandoc_required(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Not processing, regardless of Pandoc
        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # AsciiDoc export should be enabled (doesn't need Pandoc)
        mock_editor.action_manager.save_as_adoc_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_markdown_export_requires_pandoc(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # Markdown export enabled with Pandoc
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_docx_export_requires_pandoc(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # DOCX export enabled with Pandoc
        mock_editor.action_manager.save_as_docx_act.setEnabled.assert_called_with(True)

    def test_html_export_does_not_require_pandoc(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # HTML export should be enabled (uses asciidoc3)
        mock_editor.action_manager.save_as_html_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_pdf_export_requires_pandoc(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # PDF export enabled with Pandoc
        mock_editor.action_manager.save_as_pdf_act.setEnabled.assert_called_with(True)


@pytest.mark.unit
class TestActionStateTransitions:
    """Test suite for action state transitions."""

    def test_save_action_transitions_disabled_to_enabled(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Start disabled (processing)
        mock_editor.file_operations_manager._is_processing_pandoc = True
        manager.update_ui_state()
        mock_editor.action_manager.save_act.setEnabled.assert_called_with(False)

        # Transition to enabled
        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()
        mock_editor.action_manager.save_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_export_action_transitions_disabled_to_enabled(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Start disabled
        mock_editor.file_operations_manager._is_processing_pandoc = True
        manager.update_ui_state()

        # Transition to enabled
        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(True)

    def test_git_action_transitions_disabled_to_enabled(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.git_repo_path = "/path/to/repo"

        # Start disabled
        mock_editor._is_processing_git = True
        manager.update_ui_state()
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(False)

        # Transition to enabled
        mock_editor._is_processing_git = False
        manager.update_ui_state()
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_convert_paste_transitions_disabled_to_enabled(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Start disabled
        mock_editor.file_operations_manager._is_processing_pandoc = True
        manager.update_ui_state()
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called_with(
            False
        )

        # Transition to enabled
        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_all_actions_transition_together_on_update(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.git_repo_path = "/path/to/repo"

        # Both processing
        mock_editor._is_processing_git = True
        mock_editor.file_operations_manager._is_processing_pandoc = True
        manager.update_ui_state()

        # Neither processing
        mock_editor._is_processing_git = False
        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # All should transition to enabled
        mock_editor.action_manager.save_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(True)


@pytest.mark.unit
class TestGitRepoPathEdgeCases:
    """Test suite for Git repo path edge cases."""

    def test_repo_path_with_whitespace_only_enables_git(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.git_repo_path = "   "
        mock_editor._is_processing_git = False
        manager.update_ui_state()

        # Git actions enabled (bool("   ") is True)
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)

    def test_repo_path_with_special_characters_enables_git(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.git_repo_path = "/path/with/特殊字符/@#$%"
        mock_editor._is_processing_git = False
        manager.update_ui_state()

        # Git actions enabled with special chars (valid path)
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)

    def test_repo_path_none_vs_empty_both_disable(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._is_processing_git = False

        # Test None
        mock_editor._settings.git_repo_path = None
        manager.update_ui_state()
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(False)

        # Test empty string
        mock_editor._settings.git_repo_path = ""
        manager.update_ui_state()
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(False)

    def test_changing_repo_path_updates_git_actions(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._is_processing_git = False

        # Start with no repo
        mock_editor._settings.git_repo_path = None
        manager.update_ui_state()
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(False)

        # Add repo
        mock_editor._settings.git_repo_path = "/path/to/repo"
        manager.update_ui_state()
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)

    def test_invalid_repo_path_still_enables_actions(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # UIStateManager only checks bool(path), not validity
        mock_editor._settings.git_repo_path = "/nonexistent/invalid/path"
        mock_editor._is_processing_git = False
        manager.update_ui_state()

        # Actions enabled (validity checked elsewhere)
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)


@pytest.mark.unit
class TestOllamaModelEdgeCases:
    """Test suite for Ollama model name edge cases."""

    def test_model_name_with_whitespace_only_displays_as_is(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.ollama_enabled = True
        mock_editor._settings.ollama_model = "   "
        manager.update_ai_status_bar()

        # Displays model as-is (bool("   ") is True, no stripping)
        mock_editor.status_manager.set_ai_model.assert_called_with("   ")

    def test_model_name_with_special_characters_displays_correctly(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        model = "llama-2-special@v1.0"
        mock_editor._settings.ollama_enabled = True
        mock_editor._settings.ollama_model = model
        manager.update_ai_status_bar()

        # Should display model name as-is
        mock_editor.status_manager.set_ai_model.assert_called_with(model)

    def test_very_long_model_name_displays_correctly(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        model = "a" * 100  # Very long model name
        mock_editor._settings.ollama_enabled = True
        mock_editor._settings.ollama_model = model
        manager.update_ai_status_bar()

        # Should display full model name
        mock_editor.status_manager.set_ai_model.assert_called_with(model)

    def test_model_name_none_vs_empty_both_show_pandoc(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.ollama_enabled = True

        # Test None
        mock_editor._settings.ollama_model = None
        manager.update_ai_status_bar()
        mock_editor.status_manager.set_ai_model.assert_called_with("Pandoc")

        # Test empty string
        mock_editor._settings.ollama_model = ""
        manager.update_ai_status_bar()
        mock_editor.status_manager.set_ai_model.assert_called_with("Pandoc")


@pytest.mark.unit
class TestMultipleUpdateCalls:
    """Test suite for multiple rapid update_ui_state calls."""

    def test_rapid_successive_update_ui_state_calls(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Call update_ui_state 10 times rapidly
        for _ in range(10):
            manager.update_ui_state()

        # Should handle all calls without error
        assert mock_editor.action_manager.save_act.setEnabled.call_count == 10

    def test_update_ui_state_idempotent_same_state_same_result(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False

        # Call twice with same state
        manager.update_ui_state()
        first_call = mock_editor.action_manager.save_act.setEnabled.call_args

        manager.update_ui_state()
        second_call = mock_editor.action_manager.save_act.setEnabled.call_args

        # Should produce same result
        assert first_call == second_call

    def test_ai_status_bar_updates_on_each_call(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.ollama_enabled = False

        # Call 5 times
        for _ in range(5):
            manager.update_ui_state()

        # AI status bar should update each time
        assert mock_editor.status_manager.set_ai_model.call_count == 5

    def test_action_states_consistent_across_multiple_calls(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        mock_editor._settings.git_repo_path = "/path/to/repo"
        mock_editor._is_processing_git = False

        # Multiple calls should produce consistent results
        for _ in range(3):
            manager.update_ui_state()
            # Save enabled
            mock_editor.action_manager.save_act.setEnabled.assert_called_with(True)
            # Git enabled
            mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(
                True
            )


@pytest.mark.unit
class TestActionManagerCalls:
    """Test suite for verifying all action manager method calls."""

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_verifies_all_save_action_calls(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        manager.update_ui_state()

        # Verify both save actions called
        mock_editor.action_manager.save_act.setEnabled.assert_called_once()
        mock_editor.action_manager.save_as_act.setEnabled.assert_called_once()

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_verifies_all_export_action_calls(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        manager.update_ui_state()

        # Verify all 5 export actions called
        mock_editor.action_manager.save_as_adoc_act.setEnabled.assert_called_once()
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_once()
        mock_editor.action_manager.save_as_docx_act.setEnabled.assert_called_once()
        mock_editor.action_manager.save_as_html_act.setEnabled.assert_called_once()
        mock_editor.action_manager.save_as_pdf_act.setEnabled.assert_called_once()

    def test_verifies_all_git_action_calls(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        manager.update_ui_state()

        # Verify all 3 Git actions called
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_once()
        mock_editor.action_manager.git_pull_act.setEnabled.assert_called_once()
        mock_editor.action_manager.git_push_act.setEnabled.assert_called_once()

    def test_verifies_convert_paste_action_call(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        manager.update_ui_state()

        # Verify convert paste action called
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called_once()

    def test_verifies_no_extra_action_calls_on_single_update(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        manager.update_ui_state()

        # All actions called exactly once
        assert mock_editor.action_manager.save_act.setEnabled.call_count == 1
        assert mock_editor.action_manager.git_commit_act.setEnabled.call_count == 1
        assert mock_editor.status_manager.set_ai_model.call_count == 1


@pytest.mark.unit
class TestProcessingStateCombinations:
    """Test suite for all combinations of processing states."""

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_no_processing_all_actions_enabled(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # No processing, repo available
        mock_editor._is_processing_git = False
        mock_editor.file_operations_manager._is_processing_pandoc = False
        mock_editor._settings.git_repo_path = "/path/to/repo"
        manager.update_ui_state()

        # All actions enabled
        mock_editor.action_manager.save_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_only_git_processing_only_git_actions_disabled(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Only Git processing
        mock_editor._is_processing_git = True
        mock_editor.file_operations_manager._is_processing_pandoc = False
        mock_editor._settings.git_repo_path = "/path/to/repo"
        manager.update_ui_state()

        # Git actions disabled
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(False)
        # Others enabled
        mock_editor.action_manager.save_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_only_pandoc_processing_only_pandoc_actions_disabled(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Only Pandoc processing
        mock_editor._is_processing_git = False
        mock_editor.file_operations_manager._is_processing_pandoc = True
        mock_editor._settings.git_repo_path = "/path/to/repo"
        manager.update_ui_state()

        # Pandoc-dependent actions disabled
        mock_editor.action_manager.save_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(False)
        # Git actions enabled
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(True)

    @patch(
        "asciidoc_artisan.ui.ui_state_manager.is_pandoc_available", return_value=True
    )
    def test_both_processing_all_relevant_actions_disabled(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Both processing
        mock_editor._is_processing_git = True
        mock_editor.file_operations_manager._is_processing_pandoc = True
        mock_editor._settings.git_repo_path = "/path/to/repo"
        manager.update_ui_state()

        # All actions disabled
        mock_editor.action_manager.save_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.git_commit_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(False)
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called_with(
            False
        )


@pytest.mark.unit
class TestUpdateAIStatusBarIndependently:
    """Test suite for calling update_ai_status_bar independently."""

    def test_can_be_called_independently_of_update_ui_state(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.ollama_enabled = False

        # Call directly without update_ui_state
        manager.update_ai_status_bar()

        # Should work fine
        mock_editor.status_manager.set_ai_model.assert_called_once_with("Pandoc")

    def test_updates_status_manager_correctly(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        model = "custom-model"
        mock_editor._settings.ollama_enabled = True
        mock_editor._settings.ollama_model = model

        manager.update_ai_status_bar()

        # Should update with correct model
        mock_editor.status_manager.set_ai_model.assert_called_once_with(model)

    def test_handles_none_settings_gracefully(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        # Settings all None
        mock_editor._settings.ollama_enabled = None
        mock_editor._settings.ollama_model = None

        # Should not crash
        manager.update_ai_status_bar()

        # Should default to Pandoc
        mock_editor.status_manager.set_ai_model.assert_called_once_with("Pandoc")

    def test_multiple_calls_update_status_each_time(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager

        manager = UIStateManager(mock_editor)

        mock_editor._settings.ollama_enabled = False

        # Call 3 times
        for _ in range(3):
            manager.update_ai_status_bar()

        # Should update 3 times
        assert mock_editor.status_manager.set_ai_model.call_count == 3
