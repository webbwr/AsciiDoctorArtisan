"""Tests for ui.ui_state_manager module."""

import pytest
from unittest.mock import Mock, patch


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

    @patch("asciidoc_artisan.ui.ui_state_manager.PANDOC_AVAILABLE", True)
    def test_pandoc_exports_enabled_when_pandoc_available(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager
        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # Pandoc-dependent exports should be enabled
        mock_editor.action_manager.save_as_md_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.save_as_docx_act.setEnabled.assert_called_with(True)
        mock_editor.action_manager.save_as_pdf_act.setEnabled.assert_called_with(True)

    @patch("asciidoc_artisan.ui.ui_state_manager.PANDOC_AVAILABLE", False)
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

    @patch("asciidoc_artisan.ui.ui_state_manager.PANDOC_AVAILABLE", True)
    def test_convert_paste_enabled_when_pandoc_available_and_not_processing(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager
        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # Convert paste should be enabled
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called_with(True)

    @patch("asciidoc_artisan.ui.ui_state_manager.PANDOC_AVAILABLE", False)
    def test_convert_paste_disabled_when_pandoc_unavailable(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager
        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = False
        manager.update_ui_state()

        # Convert paste should be disabled without Pandoc
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called_with(False)

    @patch("asciidoc_artisan.ui.ui_state_manager.PANDOC_AVAILABLE", True)
    def test_convert_paste_disabled_when_processing_pandoc(self, mock_editor):
        from asciidoc_artisan.ui.ui_state_manager import UIStateManager
        manager = UIStateManager(mock_editor)

        mock_editor.file_operations_manager._is_processing_pandoc = True
        manager.update_ui_state()

        # Convert paste should be disabled during processing
        mock_editor.action_manager.convert_paste_act.setEnabled.assert_called_with(False)


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
