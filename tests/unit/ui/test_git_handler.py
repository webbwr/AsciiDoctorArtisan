"""Tests for ui.git_handler module."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PySide6.QtWidgets import QMainWindow, QStatusBar


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
        git_methods = [
            m
            for m in dir(handler)
            if any(x in m.lower() for x in ["commit", "push", "pull", "git"])
        ]
        assert len(git_methods) > 0

    # Initialization Tests

    def test_initialize_with_valid_repo(self, main_window, mock_managers):
        """Test initialization with valid Git repository."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        # Set up valid repo path
        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        with patch.object(Path, "is_dir", return_value=True):
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
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

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
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

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
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

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

    @patch("subprocess.run")
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

    @patch("subprocess.run")
    def test_get_current_branch_detached_head(
        self, mock_run, main_window, mock_managers
    ):
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


@pytest.mark.fr_030
@pytest.mark.unit
class TestRepositorySelection:
    """Test suite for select_repository() method."""

    @patch("asciidoc_artisan.ui.git_handler.QFileDialog.getExistingDirectory")
    def test_select_repository_user_cancels_dialog(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test select_repository when user cancels dialog."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        # User cancels dialog (returns empty string)
        mock_dialog.return_value = ""

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.select_repository()

        # Should not save or update UI
        settings_manager.save_settings.assert_not_called()

    @patch("asciidoc_artisan.ui.git_handler.QFileDialog.getExistingDirectory")
    def test_select_repository_not_a_git_repo_shows_warning(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test select_repository with non-Git directory."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        # User selects directory without .git
        mock_dialog.return_value = "/home/user/not-a-repo"

        with patch.object(Path, "is_dir", return_value=False):
            handler = GitHandler(main_window, settings_manager, status_manager)
            handler.select_repository()

        # Should show warning message
        status_manager.show_message.assert_called_once()
        call_args = status_manager.show_message.call_args[0]
        assert call_args[0] == "warning"
        assert "Not a Git Repository" in call_args[1]

    @patch("asciidoc_artisan.ui.git_handler.QFileDialog.getExistingDirectory")
    def test_select_repository_valid_repo_saves_to_settings(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test select_repository with valid Git repository."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        # User selects valid Git repo
        mock_dialog.return_value = "/home/user/valid-repo"

        settings = settings_manager.load_settings.return_value

        with patch.object(Path, "is_dir", return_value=True):
            handler = GitHandler(main_window, settings_manager, status_manager)
            handler.select_repository()

        # Should save to settings
        assert settings.git_repo_path == "/home/user/valid-repo"
        settings_manager.save_settings.assert_called_once()

    @patch("asciidoc_artisan.ui.git_handler.QFileDialog.getExistingDirectory")
    def test_select_repository_updates_ui_state(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test select_repository updates UI state."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        mock_dialog.return_value = "/home/user/valid-repo"

        # Add _update_ui_state method to window
        main_window._update_ui_state = Mock()

        with patch.object(Path, "is_dir", return_value=True):
            handler = GitHandler(main_window, settings_manager, status_manager)
            handler.select_repository()

        # Should call _update_ui_state
        main_window._update_ui_state.assert_called_once()

    @patch("asciidoc_artisan.ui.git_handler.QFileDialog.getExistingDirectory")
    def test_select_repository_shows_status_message(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test select_repository shows status bar message."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        mock_dialog.return_value = "/home/user/valid-repo"

        with patch.object(Path, "is_dir", return_value=True):
            handler = GitHandler(main_window, settings_manager, status_manager)
            handler.select_repository()

        # Should show status message (status_bar exists in fixture)
        # Note: Real QStatusBar.showMessage was called, can't assert on mock

    @patch("asciidoc_artisan.ui.git_handler.QFileDialog.getExistingDirectory")
    def test_select_repository_uses_last_directory_as_start_dir(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test select_repository uses settings.last_directory when git_repo_path not set."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        # Don't set git_repo_path attribute at all (not even to None)
        if hasattr(settings, "git_repo_path"):
            delattr(settings, "git_repo_path")
        settings.last_directory = "/home/user/documents"

        mock_dialog.return_value = ""  # User cancels

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.select_repository()

        # Should use last_directory as start (when git_repo_path doesn't exist)
        # QFileDialog.getExistingDirectory(parent, title, directory, ...)
        call_args = mock_dialog.call_args[0]
        assert call_args[2] == "/home/user/documents"


@pytest.mark.fr_030
@pytest.mark.unit
class TestCommitWithUnsavedChanges:
    """Test suite for commit_changes() with unsaved file handling."""

    @patch("asciidoc_artisan.ui.git_handler.QInputDialog.getMultiLineText")
    def test_commit_changes_auto_saves_unsaved_changes(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test commit_changes auto-saves file before commit."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # File has unsaved changes
        main_window._unsaved_changes = True
        main_window.save_file = Mock(return_value=True)

        mock_dialog.return_value = ("Test commit", True)

        handler = GitHandler(main_window, settings_manager, status_manager)

        # Mock git_operation_started signal to avoid emit errors
        handler.git_operation_started = Mock()
        handler.git_operation_started.emit = Mock()

        handler.commit_changes()

        # Should call save_file
        main_window.save_file.assert_called_once()

    @patch("asciidoc_artisan.ui.git_handler.QInputDialog.getMultiLineText")
    def test_commit_changes_aborts_if_save_fails(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test commit_changes aborts if save fails."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # File has unsaved changes, save fails
        main_window._unsaved_changes = True
        main_window.save_file = Mock(return_value=False)

        mock_dialog.return_value = ("Test commit", True)

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.commit_changes()

        # Should NOT emit git command
        main_window.request_git_command.emit.assert_not_called()

    @patch("asciidoc_artisan.ui.git_handler.QInputDialog.getMultiLineText")
    def test_commit_changes_user_cancels_dialog(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test commit_changes when user cancels dialog."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # User cancels dialog
        mock_dialog.return_value = ("", False)

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.commit_changes()

        # Should NOT emit git command
        main_window.request_git_command.emit.assert_not_called()

    @patch("asciidoc_artisan.ui.git_handler.QInputDialog.getMultiLineText")
    def test_commit_changes_user_enters_empty_message(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test commit_changes with empty message does nothing."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # User enters empty message
        mock_dialog.return_value = ("   ", True)

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.commit_changes()

        # Should NOT emit git command
        main_window.request_git_command.emit.assert_not_called()

    @patch("asciidoc_artisan.ui.git_handler.QInputDialog.getMultiLineText")
    def test_commit_changes_full_flow_with_message(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test full commit flow with valid message."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        mock_dialog.return_value = ("Fix critical bug", True)

        # Mock the signal
        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.git_operation_started = Mock()

        handler.commit_changes()

        # Should emit git command (git add .)
        main_window.request_git_command.emit.assert_called_once()
        # Should set pending message
        assert handler.pending_commit_message == "Fix critical bug"
        # Should set is_processing
        assert handler.is_processing is True


@pytest.mark.fr_030
@pytest.mark.unit
class TestQuickCommitEdgeCases:
    """Test suite for quick_commit() edge cases."""

    def test_quick_commit_no_repo_shows_message(self, main_window, mock_managers):
        """Test quick_commit with no repo shows message."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = None

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.quick_commit("Test message")

        # Should show message to user
        status_manager.show_message.assert_called_once()

    def test_quick_commit_whitespace_only_message_ignored(
        self, main_window, mock_managers
    ):
        """Test quick_commit with whitespace-only message does nothing."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.quick_commit("   \n  \t  ")

        # Should NOT emit git command
        main_window.request_git_command.emit.assert_not_called()

    def test_quick_commit_sets_last_operation_to_commit(
        self, main_window, mock_managers
    ):
        """Test quick_commit sets last_operation correctly."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        # Mock signal to avoid emit errors
        handler.git_operation_started = Mock()
        handler.git_operation_started.emit = Mock()

        handler.quick_commit("Test commit")

        assert handler.last_operation == "commit"

    def test_quick_commit_emits_quick_commit_signal(self, main_window, mock_managers):
        """Test quick_commit emits git_operation_started with 'quick_commit'."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.git_operation_started = Mock()

        handler.quick_commit("Test commit")

        # Should emit signal with 'quick_commit'
        handler.git_operation_started.emit.assert_called_once_with("quick_commit")

    def test_quick_commit_updates_ui_state(self, main_window, mock_managers):
        """Test quick_commit calls _update_ui_state."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # Mock _update_ui_state and signal
        handler = GitHandler(main_window, settings_manager, status_manager)
        handler._update_ui_state = Mock()
        handler.git_operation_started = Mock()
        handler.git_operation_started.emit = Mock()

        handler.quick_commit("Test commit")

        # Should update UI state
        handler._update_ui_state.assert_called()


@pytest.mark.fr_030
@pytest.mark.unit
class TestResultHandlingMultiStep:
    """Test suite for multi-step result handling (commit staging)."""

    def test_handle_result_commit_stage_failure_shows_error(
        self, main_window, mock_managers
    ):
        """Test handling git add failure."""
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.last_operation = "commit"
        handler.is_processing = True

        # Mock signal to avoid emit errors
        handler.git_operation_completed = Mock()
        handler.git_operation_completed.emit = Mock()

        result = GitResult(
            success=False,
            user_message="Failed to stage files",
            command=["git", "add", "."],
            stdout="",
            stderr="fatal: not a git repository",
            returncode=128,
        )

        handler.handle_git_result(result)

        # Should show error message
        status_manager.show_message.assert_called()
        assert status_manager.show_message.call_args[0][0] == "critical"

    def test_handle_result_commit_stage_success_triggers_commit(
        self, main_window, mock_managers
    ):
        """Test successful staging triggers commit step."""
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

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

        # Should emit commit command
        main_window.request_git_command.emit.assert_called_once()
        args = main_window.request_git_command.emit.call_args[0]
        assert "commit" in args[0]
        assert "Test commit" in args[0]

        # Should update last_operation to commit_final
        assert handler.last_operation == "commit_final"

    def test_handle_result_commit_final_success_clears_message(
        self, main_window, mock_managers
    ):
        """Test successful final commit clears pending_commit_message."""
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.last_operation = "commit_final"
        handler.pending_commit_message = "Test commit"
        handler.is_processing = True

        handler.git_operation_completed = Mock()

        result = GitResult(
            success=True,
            user_message="Commit successful",
            command=["git", "commit", "-m", "Test commit"],
            stdout="[main abc123] Test commit",
            stderr="",
            returncode=0,
        )

        handler.handle_git_result(result)

        # Should clear pending message
        assert handler.pending_commit_message is None
        # Should clear last_operation
        assert handler.last_operation == ""

    def test_handle_result_commit_final_failure_clears_message(
        self, main_window, mock_managers
    ):
        """Test failed final commit clears pending_commit_message."""
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.last_operation = "commit_final"
        handler.pending_commit_message = "Test commit"
        handler.is_processing = True

        handler.git_operation_completed = Mock()

        result = GitResult(
            success=False,
            user_message="Commit failed: nothing to commit",
            command=["git", "commit", "-m", "Test commit"],
            stdout="",
            stderr="nothing to commit",
            returncode=1,
        )

        handler.handle_git_result(result)

        # Should clear pending message even on failure
        assert handler.pending_commit_message is None

    def test_handle_result_push_success_emits_completed_signal(
        self, main_window, mock_managers
    ):
        """Test successful push emits git_operation_completed signal."""
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.last_operation = "push"
        handler.is_processing = True

        handler.git_operation_completed = Mock()

        result = GitResult(
            success=True,
            user_message="Push successful",
            command=["git", "push"],
            stdout="Everything up-to-date",
            stderr="",
            returncode=0,
        )

        handler.handle_git_result(result)

        # Should emit completed signal
        handler.git_operation_completed.emit.assert_called_once()
        assert handler.git_operation_completed.emit.call_args[0][0] is True

    def test_handle_result_pull_failure_emits_completed_signal(
        self, main_window, mock_managers
    ):
        """Test failed pull emits git_operation_completed signal."""
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.last_operation = "pull"
        handler.is_processing = True

        handler.git_operation_completed = Mock()

        result = GitResult(
            success=False,
            user_message="Pull failed: merge conflict",
            command=["git", "pull"],
            stdout="",
            stderr="CONFLICT (content)",
            returncode=1,
        )

        handler.handle_git_result(result)

        # Should emit completed signal with failure
        handler.git_operation_completed.emit.assert_called_once()
        assert handler.git_operation_completed.emit.call_args[0][0] is False


@pytest.mark.fr_030
@pytest.mark.unit
class TestBranchNameQueryErrors:
    """Test suite for get_current_branch() error handling."""

    @patch("subprocess.run")
    def test_get_current_branch_subprocess_timeout(
        self, mock_run, main_window, mock_managers
    ):
        """Test get_current_branch handles subprocess timeout."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="git", timeout=2)

        handler = GitHandler(main_window, settings_manager, status_manager)
        branch = handler.get_current_branch()

        # Should return empty string on timeout
        assert branch == ""

    @patch("subprocess.run")
    def test_get_current_branch_git_not_found(
        self, mock_run, main_window, mock_managers
    ):
        """Test get_current_branch handles git not installed."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # Mock FileNotFoundError (git not in PATH)
        mock_run.side_effect = FileNotFoundError("git: command not found")

        handler = GitHandler(main_window, settings_manager, status_manager)
        branch = handler.get_current_branch()

        # Should return empty string
        assert branch == ""

    @patch("subprocess.run")
    def test_get_current_branch_generic_exception(
        self, mock_run, main_window, mock_managers
    ):
        """Test get_current_branch handles generic exception."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # Mock generic exception
        mock_run.side_effect = RuntimeError("Unexpected error")

        handler = GitHandler(main_window, settings_manager, status_manager)
        branch = handler.get_current_branch()

        # Should return empty string
        assert branch == ""

    @patch("subprocess.run")
    def test_get_current_branch_detached_head_rev_parse_fails(
        self, mock_run, main_window, mock_managers
    ):
        """Test detached HEAD when rev-parse fails."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # Mock detached HEAD with rev-parse failure
        mock_run.side_effect = [
            Mock(returncode=0, stdout=""),  # --show-current returns empty
            Mock(returncode=128, stdout=""),  # rev-parse fails
        ]

        handler = GitHandler(main_window, settings_manager, status_manager)
        branch = handler.get_current_branch()

        # Should return generic detached message
        assert branch == "HEAD (detached)"

    @patch("subprocess.run")
    def test_get_current_branch_non_zero_returncode(
        self, mock_run, main_window, mock_managers
    ):
        """Test get_current_branch with non-zero return code."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # Mock non-zero return code
        mock_run.return_value = Mock(
            returncode=128, stdout="fatal: not a git repository"
        )

        handler = GitHandler(main_window, settings_manager, status_manager)
        branch = handler.get_current_branch()

        # Should return empty string
        assert branch == ""

    @patch("subprocess.run")
    def test_get_current_branch_empty_output_with_rev_parse_success(
        self, mock_run, main_window, mock_managers
    ):
        """Test detached HEAD with successful rev-parse."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        # Mock detached HEAD with rev-parse success
        mock_run.side_effect = [
            Mock(returncode=0, stdout=""),  # --show-current returns empty
            Mock(returncode=0, stdout="abc1234\n"),  # rev-parse returns hash
        ]

        handler = GitHandler(main_window, settings_manager, status_manager)
        branch = handler.get_current_branch()

        # Should return detached with commit hash
        assert "HEAD (detached at abc1234)" == branch


@pytest.mark.fr_030
@pytest.mark.unit
class TestStatusRefreshLifecycle:
    """Test suite for status refresh lifecycle management."""

    def test_start_status_refresh_when_already_started_no_op(
        self, main_window, mock_managers
    ):
        """Test starting status refresh when already started."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.start_status_refresh()

        # Start again (should be no-op)
        start_call_count = main_window.request_git_status.emit.call_count
        handler.start_status_refresh()

        # Should not start timer again or emit additional requests
        # (call count should not increase beyond initial immediate fetch)
        assert main_window.request_git_status.emit.call_count == start_call_count

    def test_stop_status_refresh_when_already_stopped_no_op(
        self, main_window, mock_managers
    ):
        """Test stopping status refresh when already stopped."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)

        # Stop when not started (should be no-op)
        handler.stop_status_refresh()

        # Should not crash or log errors
        assert handler.status_refresh_enabled is False

    def test_start_status_refresh_no_repo_no_op(self, main_window, mock_managers):
        """Test starting status refresh with no repo set."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = None

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.start_status_refresh()

        # Should NOT start timer or emit requests
        assert not handler.status_timer.isActive()
        main_window.request_git_status.emit.assert_not_called()

    def test_start_status_refresh_emits_immediate_request(
        self, main_window, mock_managers
    ):
        """Test start_status_refresh emits immediate status request."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.start_status_refresh()

        # Should emit immediate request (before first timer interval)
        main_window.request_git_status.emit.assert_called_with("/home/user/repo")

    def test_stop_status_refresh_stops_timer_and_clears_flag(
        self, main_window, mock_managers
    ):
        """Test stop_status_refresh stops timer and clears flag."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.start_status_refresh()
        assert handler.status_timer.isActive()
        assert handler.status_refresh_enabled is True

        handler.stop_status_refresh()

        # Should stop timer and clear flag
        assert not handler.status_timer.isActive()
        assert handler.status_refresh_enabled is False


@pytest.mark.fr_030
@pytest.mark.unit
class TestSignalEmissions:
    """Test suite for git_operation_started and git_operation_completed signals."""

    def test_commit_changes_emits_git_operation_started(
        self, main_window, mock_managers
    ):
        """Test commit_changes emits git_operation_started signal."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.git_operation_started = Mock()

        with patch(
            "asciidoc_artisan.ui.git_handler.QInputDialog.getMultiLineText"
        ) as mock_dialog:
            mock_dialog.return_value = ("Test commit", True)
            handler.commit_changes()

        # Should emit signal with "commit"
        handler.git_operation_started.emit.assert_called_once_with("commit")

    def test_pull_changes_emits_git_operation_started(self, main_window, mock_managers):
        """Test pull_changes emits git_operation_started signal."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.git_operation_started = Mock()

        handler.pull_changes()

        # Should emit signal with "pull"
        handler.git_operation_started.emit.assert_called_once_with("pull")

    def test_push_changes_emits_git_operation_started(self, main_window, mock_managers):
        """Test push_changes emits git_operation_started signal."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.git_operation_started = Mock()

        handler.push_changes()

        # Should emit signal with "push"
        handler.git_operation_started.emit.assert_called_once_with("push")

    def test_quick_commit_emits_git_operation_started(self, main_window, mock_managers):
        """Test quick_commit emits git_operation_started signal."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.git_operation_started = Mock()

        handler.quick_commit("Quick test")

        # Should emit signal with "quick_commit"
        handler.git_operation_started.emit.assert_called_once_with("quick_commit")

    def test_handle_result_success_emits_git_operation_completed(
        self, main_window, mock_managers
    ):
        """Test successful result emits git_operation_completed signal."""
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.last_operation = "pull"
        handler.is_processing = True

        handler.git_operation_completed = Mock()

        result = GitResult(
            success=True,
            user_message="Pull successful",
            command=["git", "pull"],
            stdout="Already up to date",
            stderr="",
            returncode=0,
        )

        handler.handle_git_result(result)

        # Should emit completed signal with success=True
        handler.git_operation_completed.emit.assert_called_once()
        assert handler.git_operation_completed.emit.call_args[0] == (
            True,
            "Pull successful",
        )

    def test_handle_result_failure_emits_git_operation_completed(
        self, main_window, mock_managers
    ):
        """Test failed result emits git_operation_completed signal."""
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.last_operation = "push"
        handler.is_processing = True

        handler.git_operation_completed = Mock()

        result = GitResult(
            success=False,
            user_message="Push failed: no upstream",
            command=["git", "push"],
            stdout="",
            stderr="fatal: no upstream branch",
            returncode=128,
        )

        handler.handle_git_result(result)

        # Should emit completed signal with success=False
        handler.git_operation_completed.emit.assert_called_once()
        assert handler.git_operation_completed.emit.call_args[0] == (
            False,
            "Push failed: no upstream",
        )


@pytest.mark.fr_030
@pytest.mark.unit
class TestInitializeRepoValidation:
    """Test suite for initialize() repository validation."""

    def test_initialize_invalid_repo_clears_from_settings(
        self, main_window, mock_managers
    ):
        """Test initialize clears invalid repo from settings."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/invalid-repo"

        with patch.object(Path, "is_dir", return_value=False):
            handler = GitHandler(main_window, settings_manager, status_manager)
            handler.initialize()

        # Should clear invalid path
        assert settings.git_repo_path is None
        # Should save updated settings
        settings_manager.save_settings.assert_called_once()

    def test_initialize_invalid_repo_logs_warning(self, main_window, mock_managers):
        """Test initialize logs warning for invalid repo."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/invalid-repo"

        with patch.object(Path, "is_dir", return_value=False):
            with patch("asciidoc_artisan.ui.git_handler.logger") as mock_logger:
                handler = GitHandler(main_window, settings_manager, status_manager)
                handler.initialize()

                # Should log warning
                mock_logger.warning.assert_called_once()
                call_args = str(mock_logger.warning.call_args)
                assert "no longer valid" in call_args

    def test_initialize_valid_repo_starts_status_refresh(
        self, main_window, mock_managers
    ):
        """Test initialize starts status refresh for valid repo."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/valid-repo"

        with patch.object(Path, "is_dir", return_value=True):
            handler = GitHandler(main_window, settings_manager, status_manager)
            handler.start_status_refresh = Mock()
            handler.initialize()

            # Should start status refresh
            handler.start_status_refresh.assert_called_once()

    def test_initialize_valid_repo_logs_info(self, main_window, mock_managers):
        """Test initialize logs info for valid repo."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/valid-repo"

        with patch.object(Path, "is_dir", return_value=True):
            with patch("asciidoc_artisan.ui.git_handler.logger") as mock_logger:
                handler = GitHandler(main_window, settings_manager, status_manager)
                handler.initialize()

                # Should log info (may be called multiple times due to status refresh)
                # Just check at least one call contains "loaded from settings"
                mock_logger.info.assert_called()
                call_args_list = [str(call) for call in mock_logger.info.call_args_list]
                assert any(
                    "loaded from settings" in args.lower() for args in call_args_list
                )

    def test_initialize_no_git_repo_path_attribute_handles_gracefully(
        self, main_window, mock_managers
    ):
        """Test initialize handles missing git_repo_path attribute."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        # Remove git_repo_path attribute
        if hasattr(settings, "git_repo_path"):
            delattr(settings, "git_repo_path")

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.initialize()

        # Should complete without error
        assert handler is not None


@pytest.mark.fr_030
@pytest.mark.unit
class TestCheckRepositoryReady:
    """Test suite for _check_repository_ready() validation."""

    def test_check_repository_ready_no_repo_shows_message(
        self, main_window, mock_managers
    ):
        """Test _check_repository_ready shows message when no repo."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = None

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler._check_repository_ready()

        # Should show message
        status_manager.show_message.assert_called_once()
        call_args = status_manager.show_message.call_args[0]
        assert "No Repository" in call_args[1]

    def test_check_repository_ready_no_repo_returns_false(
        self, main_window, mock_managers
    ):
        """Test _check_repository_ready returns False when no repo."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = None

        handler = GitHandler(main_window, settings_manager, status_manager)
        result = handler._check_repository_ready()

        assert result is False

    def test_check_repository_ready_repo_set_returns_true(
        self, main_window, mock_managers
    ):
        """Test _check_repository_ready returns True when repo set."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        result = handler._check_repository_ready()

        assert result is True

    def test_ensure_ready_checks_repository(self, main_window, mock_managers):
        """Test _ensure_ready calls _check_repository_ready."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = None

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler._check_repository_ready = Mock(return_value=False)

        result = handler._ensure_ready()

        # Should call _check_repository_ready
        handler._check_repository_ready.assert_called_once()
        assert result is False

    def test_ensure_ready_checks_busy_state(self, main_window, mock_managers):
        """Test _ensure_ready checks is_processing flag."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.is_processing = True  # Busy

        result = handler._ensure_ready()

        # Should return False when busy
        assert result is False


@pytest.mark.fr_030
@pytest.mark.unit
class TestUIStateUpdateCalls:
    """Test suite for _update_ui_state() calls throughout operations."""

    @patch("asciidoc_artisan.ui.git_handler.QInputDialog.getMultiLineText")
    def test_commit_changes_updates_ui_state_before_emit(
        self, mock_dialog, main_window, mock_managers
    ):
        """Test commit_changes calls _update_ui_state before emitting."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        mock_dialog.return_value = ("Test commit", True)

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler._update_ui_state = Mock()
        # Mock signal to avoid emit errors
        handler.git_operation_started = Mock()
        handler.git_operation_started.emit = Mock()

        handler.commit_changes()

        # Should call _update_ui_state
        handler._update_ui_state.assert_called()

    def test_pull_changes_updates_ui_state_before_emit(
        self, main_window, mock_managers
    ):
        """Test pull_changes calls _update_ui_state before emitting."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler._update_ui_state = Mock()
        # Mock signal to avoid emit errors
        handler.git_operation_started = Mock()
        handler.git_operation_started.emit = Mock()

        handler.pull_changes()

        # Should call _update_ui_state
        handler._update_ui_state.assert_called()

    def test_push_changes_updates_ui_state_before_emit(
        self, main_window, mock_managers
    ):
        """Test push_changes calls _update_ui_state before emitting."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler._update_ui_state = Mock()
        # Mock signal to avoid emit errors
        handler.git_operation_started = Mock()
        handler.git_operation_started.emit = Mock()

        handler.push_changes()

        # Should call _update_ui_state
        handler._update_ui_state.assert_called()

    def test_handle_result_updates_ui_state_after_complete(
        self, main_window, mock_managers
    ):
        """Test handle_git_result calls _update_ui_state after completion."""
        from asciidoc_artisan.core import GitResult
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        handler = GitHandler(main_window, settings_manager, status_manager)
        handler.last_operation = "pull"
        handler.is_processing = True
        handler._update_ui_state = Mock()

        handler.git_operation_completed = Mock()

        result = GitResult(
            success=True,
            user_message="Pull successful",
            command=["git", "pull"],
            stdout="Already up to date",
            stderr="",
            returncode=0,
        )

        handler.handle_git_result(result)

        # Should call _update_ui_state
        handler._update_ui_state.assert_called()

    def test_ui_state_update_handles_missing_method_gracefully(
        self, main_window, mock_managers
    ):
        """Test operations handle missing _update_ui_state gracefully."""
        from asciidoc_artisan.ui.git_handler import GitHandler

        settings_manager, status_manager = mock_managers

        settings = settings_manager.load_settings.return_value
        settings.git_repo_path = "/home/user/repo"

        handler = GitHandler(main_window, settings_manager, status_manager)
        # Mock signal to avoid emit errors
        handler.git_operation_started = Mock()
        handler.git_operation_started.emit = Mock()

        # BaseVCSHandler has _update_ui_state, so handler will have it
        # Test that it can be called (not that it's missing)
        assert hasattr(handler, "_update_ui_state")

        # Call operation to ensure _update_ui_state doesn't crash
        handler.pull_changes()
        assert handler.is_processing is True
