"""Tests for ui.git_handler module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QStatusBar
import subprocess


@pytest.fixture
def main_window(qapp):
    """Create main window with required attributes."""
    window = QMainWindow()
    window.status_bar = QStatusBar()
    window.setStatusBar(window.status_bar)
    window._unsaved_changes = False
    window.request_git_command = Mock()
    window.request_git_status = Mock()
    return window


@pytest.fixture
def mock_managers(qapp):
    """Create mock settings_manager and status_manager for GitHandler."""
    settings_manager = Mock()
    status_manager = Mock()

    # Mock settings object
    settings = Mock()
    settings.git_repo_path = None
    settings.last_directory = "/home/user"
    settings_manager.load_settings.return_value = settings

    return settings_manager, status_manager


class TestGitHandler:
    """Test suite for GitHandler."""

    def test_import(self):
        from asciidoc_artisan.ui.git_handler import GitHandler
        assert GitHandler is not None

    def test_creation(self, main_window, mock_managers):
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers
        handler = GitHandler(main_window, settings_manager, status_manager)
        assert handler is not None

    def test_has_git_methods(self, main_window, mock_managers):
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers
        handler = GitHandler(main_window, settings_manager, status_manager)
        git_methods = [m for m in dir(handler) if any(x in m.lower() for x in ["commit", "push", "pull", "git"])]
        assert len(git_methods) > 0

    # Initialization Tests

    def test_initialize_with_valid_repo(self, main_window, mock_managers):
        """Test initialization with valid Git repository."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        # Set up valid repo path
        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        with patch.object(Path, 'is_dir', return_value=True):
            handler = GitHandler(main_window, settings_manager, status_manager)
            handler.initialize()

        # Should load repo from settings
        assert settings_manager.load_settings.called

    def test_initialize_without_repo(self, main_window, mock_managers):
        """Test initialization without configured repository."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        # No repo configured
        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = None

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.initialize()

        # Should complete without error
        assert handler is not None

    # Repository Tests

    def test_get_repository_path_set(self, main_window, mock_managers):
        """Test getting repository path when set."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        path = handler.get_repository_path()

        assert path == "/home/user/repo"

    def test_get_repository_path_not_set(self, main_window, mock_managers):
        """Test getting repository path when not set."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = None

        handler = GitHandler(main_window, settings_manager, status_manager)
        path = handler.get_repository_path()

        assert path is None

    def test_is_repository_set_true(self, main_window, mock_managers):
        """Test is_repository_set returns True when repo is set."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)

        assert handler.is_repository_set() is True

    def test_is_repository_set_false(self, main_window, mock_managers):
        """Test is_repository_set returns False when repo not set."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = None

        handler = GitHandler(main_window, settings_manager, status_manager)

        assert handler.is_repository_set() is False

    # Git Operation Tests

    def test_commit_changes_no_repo(self, main_window, mock_managers):
        """Test commit_changes shows message when no repo set."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = None

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.commit_changes()

        # Should show message to user
        status_manager.show_message.assert_called_once()

    def test_pull_changes(self, main_window, mock_managers):
        """Test pull_changes triggers Git pull."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)

        # Mock the signal
        handler.git_operation_started = Mock()

        handler.pull_changes()

        # Should emit signal to worker
        main_window.request_git_command.emit.assert_called_once()
        args = main_window.request_git_command.emit.call_args[0]
        assert args[0] == ["git", "pull"]

    def test_push_changes(self, main_window, mock_managers):
        """Test push_changes triggers Git push."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)

        # Mock the signal
        handler.git_operation_started = Mock()

        handler.push_changes()

        # Should emit signal to worker
        main_window.request_git_command.emit.assert_called_once()
        args = main_window.request_git_command.emit.call_args[0]
        assert args[0] == ["git", "push"]

    def test_quick_commit(self, main_window, mock_managers):
        """Test quick_commit with inline message (v1.9.0)."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)

        # Mock the signal
        handler.git_operation_started = Mock()

        handler.quick_commit("Fix bug in parser")

        # Should stage files first (git add .)
        main_window.request_git_command.emit.assert_called_once()
        args = main_window.request_git_command.emit.call_args[0]
        assert args[0] == ["git", "add", "."]

        # Should set pending message
        assert handler.pending_commit_message == "Fix bug in parser"

    def test_quick_commit_empty_message(self, main_window, mock_managers):
        """Test quick_commit with empty message does nothing."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.quick_commit("")

        # Should not emit signal
        main_window.request_git_command.emit.assert_not_called()

    # State Management Tests

    def test_is_busy_true(self, main_window, mock_managers):
        """Test is_busy returns True during operation."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.is_processing = True

        assert handler.is_busy() is True

    def test_is_busy_false(self, main_window, mock_managers):
        """Test is_busy returns False when idle."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.is_processing = False

        assert handler.is_busy() is False

    # Result Handling Tests

    def test_handle_git_result_commit_staging_success(self, main_window, mock_managers):
        """Test handling successful git add (staging for commit)."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        from asciidoc_artisan.core import GitResult
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.last_operation = "commit"
        handler.pending_commit_message = "Test commit"

        result = GitResult(
            success=True,
            user_message="Changes staged",
            command=["git", "add", "."],
            stdout="",
            stderr="",
            returncode=0,
        )

        handler.handle_git_result(result)

        # Should proceed to commit step
        assert main_window.request_git_command.emit.called
        args = main_window.request_git_command.emit.call_args[0]
        assert "commit" in args[0]

    def test_handle_git_result_final_success(self, main_window, mock_managers):
        """Test handling final operation success."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        from asciidoc_artisan.core import GitResult
        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.last_operation = "pull"
        handler.is_processing = True

        # Mock the signal
        handler.git_operation_completed = Mock()

        result = GitResult(
            success=True,
            user_message="Pull completed successfully",
            command=["git", "pull"],
            stdout="Already up to date",
            stderr="",
            returncode=0,
        )

        handler.handle_git_result(result)

        # Should show success message
        status_manager.show_message.assert_called_once()
        assert status_manager.show_message.call_args[0][0] == "info"

        # Should clear processing flag
        assert handler.is_processing is False

    def test_handle_git_result_failure(self, main_window, mock_managers):
        """Test handling operation failure."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        from asciidoc_artisan.core import GitResult
        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.last_operation = "push"
        handler.is_processing = True

        # Mock the signal
        handler.git_operation_completed = Mock()

        result = GitResult(
            success=False,
            user_message="Push failed: Authentication required",
            command=["git", "push"],
            stdout="",
            stderr="fatal: Authentication failed",
            returncode=128,
        )

        handler.handle_git_result(result)

        # Should show error message
        status_manager.show_message.assert_called_once()
        assert status_manager.show_message.call_args[0][0] == "critical"

        # Should clear processing flag
        assert handler.is_processing is False

    # Branch Info Tests

    @patch('subprocess.run')
    def test_get_current_branch_success(self, mock_run, main_window, mock_managers):
        """Test getting current branch name."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # Mock subprocess result
        mock_run.return_value = Mock(returncode=0, stdout="main\n")

        handler = GitHandler(main_window, settings_manager, status_manager)
        branch = handler.get_current_branch()

        assert branch == "main"

    @patch('subprocess.run')
    def test_get_current_branch_detached_head(self, mock_run, main_window, mock_managers):
        """Test getting branch name for detached HEAD."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # Mock subprocess results for detached HEAD
        mock_run.side_effect = [
            Mock(returncode=0, stdout=""),  # --show-current returns empty
            Mock(returncode=0, stdout="abc123\n"),  # rev-parse returns hash
        ]

        handler = GitHandler(main_window, settings_manager, status_manager)
        branch = handler.get_current_branch()

        assert "detached" in branch.lower()
        assert "abc123" in branch

    def test_get_current_branch_no_repo(self, main_window, mock_managers):
        """Test getting branch when no repo is set."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = None

        handler = GitHandler(main_window, settings_manager, status_manager)
        branch = handler.get_current_branch()

        assert branch == ""

    # Status Refresh Tests (v1.9.0)

    def test_start_status_refresh(self, main_window, mock_managers):
        """Test starting periodic Git status refresh."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.start_status_refresh()

        # Should enable refresh and start timer
        assert handler.status_refresh_enabled is True
        assert handler.status_timer.isActive()

    def test_stop_status_refresh(self, main_window, mock_managers):
        """Test stopping periodic Git status refresh."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.start_status_refresh()
        assert handler.status_timer.isActive()

        handler.stop_status_refresh()

        # Should disable refresh and stop timer
        assert handler.status_refresh_enabled is False
        assert not handler.status_timer.isActive()

    def test_refresh_git_status(self, main_window, mock_managers):
        """Test requesting Git status update."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler._refresh_git_status()

        # Should emit signal to request status
        main_window.request_git_status.emit.assert_called_once_with("/home/user/repo")

    def test_refresh_git_status_while_busy(self, main_window, mock_managers):
        """Test status refresh skipped when Git operation in progress."""
        from asciidoc_artisan.ui.git_handler import GitHandler
        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.is_processing = True  # Busy with Git operation

        handler._refresh_git_status()

        # Should NOT emit signal when busy
        main_window.request_git_status.emit.assert_not_called()
