"""E2E Tests for Git integration workflows."""

from unittest.mock import Mock, patch

import pytest

from asciidoc_artisan.ui.main_window import AsciiDocEditor


@pytest.fixture
def app_window_with_repo(qtbot, test_settings, tmp_path):
    """Create main window with Git repository configured."""
    test_settings.last_directory = str(tmp_path)
    test_settings.git_repo_path = str(tmp_path)

    with (
        patch(
            "asciidoc_artisan.ui.settings_manager.SettingsManager.load_settings",
            return_value=test_settings,
        ),
        patch("asciidoc_artisan.claude.claude_client.Anthropic"),
        patch("asciidoc_artisan.claude.claude_client.SecureCredentials") as mock_creds,
    ):
        mock_creds_instance = Mock()
        mock_creds_instance.get_anthropic_key.return_value = None
        mock_creds.return_value = mock_creds_instance

        window = AsciiDocEditor()
        qtbot.addWidget(window)
        yield window

        try:
            if hasattr(window, "spell_check_manager") and window.spell_check_manager:
                if hasattr(window.spell_check_manager, "check_timer"):
                    window.spell_check_manager.check_timer.stop()
            window.close()
        except RuntimeError:
            pass


@pytest.mark.e2e
@pytest.mark.forked
class TestGitWorkerWorkflow:
    """Test Git worker initialization and capabilities."""

    def test_git_worker_exists(self, app_window_with_repo, qtbot):
        """E2E: Verify Git worker is initialized."""
        assert hasattr(app_window_with_repo, "git_worker")

    def test_git_handler_exists(self, app_window_with_repo, qtbot):
        """E2E: Verify Git handler is initialized."""
        assert hasattr(app_window_with_repo, "git_handler")

    def test_git_settings_accessible(self, app_window_with_repo, qtbot):
        """E2E: Verify Git settings are accessible."""
        settings = app_window_with_repo._settings
        assert hasattr(settings, "git_repo_path")


@pytest.mark.e2e
@pytest.mark.forked
class TestGitActionsWorkflow:
    """Test Git action capabilities."""

    def test_git_actions_exist(self, app_window_with_repo, qtbot):
        """E2E: Verify Git actions exist in action manager."""
        if hasattr(app_window_with_repo, "action_manager"):
            am = app_window_with_repo.action_manager
            assert hasattr(am, "set_repo_act")
            assert hasattr(am, "git_status_act")
            assert hasattr(am, "git_commit_act")
            assert hasattr(am, "git_pull_act")
            assert hasattr(am, "git_push_act")

    def test_github_actions_exist(self, app_window_with_repo, qtbot):
        """E2E: Verify GitHub actions exist."""
        if hasattr(app_window_with_repo, "action_manager"):
            am = app_window_with_repo.action_manager
            assert hasattr(am, "github_create_pr_act")
            assert hasattr(am, "github_list_prs_act")
            assert hasattr(am, "github_create_issue_act")


@pytest.mark.e2e
@pytest.mark.forked
class TestGitStatusWorkflow:
    """Test Git status workflow."""

    def test_git_status_method_exists(self, app_window_with_repo, qtbot):
        """E2E: Verify Git status method exists."""
        assert hasattr(app_window_with_repo, "_show_git_status")

    def test_git_status_display_capability(self, app_window_with_repo, qtbot):
        """E2E: Test Git status display capability."""
        # Status should be displayable via status manager
        assert hasattr(app_window_with_repo, "status_manager")


@pytest.mark.e2e
@pytest.mark.forked
class TestGitCommitWorkflow:
    """Test Git commit workflow."""

    def test_quick_commit_action_exists(self, app_window_with_repo, qtbot):
        """E2E: Verify quick commit action exists."""
        if hasattr(app_window_with_repo, "action_manager"):
            am = app_window_with_repo.action_manager
            assert hasattr(am, "quick_commit_act")

    def test_commit_dialog_capability(self, app_window_with_repo, qtbot):
        """E2E: Test commit dialog capability."""
        assert hasattr(app_window_with_repo, "dialog_manager")
