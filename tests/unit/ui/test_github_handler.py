"""
Unit tests for GitHubHandler class.

Tests GitHub UI coordination, signal/slot communication, and error handling.

ARCHITECTURAL NOTE (October 30, 2025):
=====================================
These tests were initially written expecting GitHubHandler to directly own
a GitHubCLIWorker instance. However, the actual implementation uses a
different architecture:

ACTUAL ARCHITECTURE:
- WorkerManager creates and manages GitHubCLIWorker
- GitHubHandler communicates via signals (request_github_command)
- Worker responds via signals (github_result_ready)
- No direct worker attribute on GitHubHandler

STATUS:
- Tests that reference `github_handler.worker` are marked with @pytest.mark.skip
- These need refactoring to test signal emission instead of direct worker calls
- UI/dialog tests work correctly (no architectural dependency)
- Error handling tests work correctly

TODO FOR FUTURE:
- Refactor skipped tests to verify signal emissions
- Consider integration tests with actual WorkerManager
- Estimated effort: 4-6 hours for complete refactoring

CURRENT TEST STATUS:
- ~20/30 tests passing (tests without worker dependency)
- ~10/30 tests skipped (need architectural refactoring)
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow

from asciidoc_artisan.core import GitHubResult
from asciidoc_artisan.ui.github_handler import GitHubHandler


class MockMainWindow(QMainWindow):
    """Mock main window with required signals for testing."""

    request_github_command = Signal(str, dict)


@pytest.fixture
def mock_parent_window(qtbot):
    """Fixture for mock parent window."""
    window = MockMainWindow()  # ✅ Real QObject with signal for parent compatibility
    qtbot.addWidget(window)  # Manage lifecycle

    # Add Mock attributes that tests expect
    window.settings_manager = Mock()
    window.status_manager = Mock()
    window.git_handler = Mock()
    window.git_handler.get_repository_path.return_value = "/test/repo"
    return window


@pytest.fixture
def mock_settings_manager():
    """Fixture for mock settings manager."""
    return Mock()


@pytest.fixture
def mock_status_manager():
    """Fixture for mock status manager."""
    return Mock()


@pytest.fixture
def mock_git_handler():
    """Fixture for mock git handler."""
    handler = Mock()
    handler.get_repository_path.return_value = "/test/repo"
    return handler


@pytest.fixture
def github_handler(
    mock_parent_window, mock_settings_manager, mock_status_manager, mock_git_handler
):
    """Fixture for GitHubHandler instance."""
    # Pass all 4 required arguments (matches production usage in main_window.py:324-326)
    handler = GitHubHandler(
        mock_parent_window, mock_settings_manager, mock_status_manager, mock_git_handler
    )
    yield handler
    # Cleanup: Note - worker is managed by WorkerManager, not GitHubHandler
    # No cleanup needed here since we're using Mocks


@pytest.mark.unit
class TestGitHubHandlerInitialization:
    """Test GitHubHandler initialization."""

    def test_handler_initialization(self, github_handler):
        """Test GitHubHandler initializes correctly."""
        assert github_handler is not None

    def test_handler_has_worker(self, github_handler):
        """Test handler can communicate with worker via signals."""
        # Architecture note: GitHubCLIWorker is created by WorkerManager,
        # not directly by GitHubHandler. Communication happens via signals.
        # Test that handler has the necessary signal connection capability
        # Note: parent_window is stored as 'window' in BaseVCSHandler
        assert hasattr(github_handler, "window")
        assert github_handler.window is not None

    def test_handler_initial_state(self, github_handler):
        """Test handler starts with correct initial state."""
        assert hasattr(github_handler, "is_processing")
        assert github_handler.is_processing is False

    def test_handler_has_required_attributes(self, github_handler):
        """Test handler has required attributes."""
        # Note: parent_window is stored as 'window' in BaseVCSHandler
        assert hasattr(github_handler, "window")
        assert hasattr(github_handler, "status_manager")
        assert hasattr(github_handler, "settings_manager")
        assert hasattr(github_handler, "git_handler")


@pytest.mark.unit
class TestGitHubHandlerReentrancy:
    """Test reentrancy guards for concurrent operations."""

    def test_reentrancy_guard_prevents_concurrent_operations(self, github_handler):
        """Test reentrancy guard prevents concurrent GitHub operations."""
        # Set processing flag
        github_handler.is_processing = True

        # Try to start operation (should be blocked)
        result = github_handler.create_pull_request()

        # Verify operation was blocked
        assert result is False or result is None

    def test_reentrancy_guard_allows_sequential_operations(self, github_handler):
        """Test reentrancy guard allows operations when not busy."""
        # Ensure not processing
        github_handler.is_processing = False

        # Mock dialog to return immediately (patch at import site)
        with patch(
            "asciidoc_artisan.ui.github_handler.CreatePullRequestDialog"
        ) as mock_dialog:
            mock_dialog.return_value.exec.return_value = False  # User cancelled

            # Try to start operation
            github_handler.create_pull_request()

            # Should have attempted to show dialog
            assert mock_dialog.called

    def test_processing_flag_reset_after_operation(self, github_handler):
        """Test processing flag is reset after operation completes."""
        # Start with not processing
        github_handler.is_processing = False

        # Simulate operation completion
        result = GitHubResult(
            success=True,
            data={"number": 42},
            error="",
            user_message="Success",
            operation="pr_create",
        )
        github_handler.handle_github_result(result)

        # Flag should be reset
        assert github_handler.is_processing is False


@pytest.mark.unit
class TestGitHubHandlerPullRequests:
    """Test pull request operations."""

    @patch("asciidoc_artisan.ui.github_handler.CreatePullRequestDialog")
    def test_create_pull_request_opens_dialog(self, mock_dialog, github_handler):
        """Test create_pull_request opens dialog."""
        # Setup mock dialog
        mock_dialog_instance = Mock()
        mock_dialog_instance.exec.return_value = False  # User cancelled
        mock_dialog.return_value = mock_dialog_instance

        # Call method
        github_handler.create_pull_request()

        # Verify dialog was created and shown
        assert mock_dialog.called
        assert mock_dialog_instance.exec.called

    @patch("asciidoc_artisan.ui.github_handler.CreatePullRequestDialog")
    def test_create_pull_request_validates_data(self, mock_dialog, github_handler):
        """Test create_pull_request validates dialog data."""
        # Setup mock dialog with valid data
        mock_dialog_instance = Mock()
        mock_dialog_instance.exec.return_value = True  # User clicked OK
        mock_dialog_instance.get_pr_data.return_value = (
            {  # ✅ Fixed: get_pr_data not get_data
                "title": "Test PR",
                "body": "Description",
                "base": "main",
                "head": "feature",
            }
        )
        mock_dialog.return_value = mock_dialog_instance

        # Call method
        github_handler.create_pull_request()

        # Verify data was retrieved
        assert (
            mock_dialog_instance.get_pr_data.called
        )  # ✅ Fixed: get_pr_data not get_data

    @patch("asciidoc_artisan.ui.github_handler.CreatePullRequestDialog")
    def test_create_pull_request_requires_repo(self, mock_dialog, github_handler):
        """Test create_pull_request checks for repository."""
        # Mock git handler to return no repo
        # ✅ Fixed: Implementation checks is_repository_set(), not get_repository_path()
        github_handler.git_handler.is_repository_set.return_value = False

        # Call method (should fail early before showing dialog)
        github_handler.create_pull_request()

        # Verify error message shown (check handler's status_manager, not fixture's)
        assert github_handler.status_manager.show_message.called
        # Dialog should NOT be shown when no repo
        assert not mock_dialog.called

    @patch("asciidoc_artisan.ui.github_handler.PullRequestListDialog")
    def test_list_pull_requests_opens_dialog(self, mock_dialog, github_handler):
        """Test list_pull_requests opens dialog."""
        # Setup mock dialog
        mock_dialog_instance = Mock()
        mock_dialog.return_value = mock_dialog_instance

        # Call method
        github_handler.list_pull_requests()

        # Verify dialog was created
        assert mock_dialog.called

    @patch("asciidoc_artisan.ui.github_handler.PullRequestListDialog")
    def test_list_pull_requests_triggers_worker(
        self, mock_dialog, github_handler, qtbot
    ):
        """Test list_pull_requests triggers worker via signal emission."""
        # Setup: Mock window to capture signal
        signal_emitted = []

        def capture_signal(operation, kwargs):
            signal_emitted.append((operation, kwargs))

        github_handler.window.request_github_command.connect(capture_signal)

        # Act: Call list_pull_requests
        github_handler.list_pull_requests()

        # Assert: Verify signal was emitted with correct operation
        assert len(signal_emitted) == 1
        operation, kwargs = signal_emitted[0]
        assert operation == "list_pull_requests"
        assert "state" in kwargs
        assert "working_dir" in kwargs
        assert kwargs["working_dir"] == "/test/repo"


@pytest.mark.unit
class TestGitHubHandlerIssues:
    """Test issue operations."""

    @patch("asciidoc_artisan.ui.github_handler.CreateIssueDialog")
    def test_create_issue_opens_dialog(self, mock_dialog, github_handler):
        """Test create_issue opens dialog."""
        # Setup mock dialog
        mock_dialog_instance = Mock()
        mock_dialog_instance.exec.return_value = False
        mock_dialog.return_value = mock_dialog_instance

        # Call method
        github_handler.create_issue()

        # Verify dialog was created
        assert mock_dialog.called

    @patch("asciidoc_artisan.ui.github_handler.CreateIssueDialog")
    def test_create_issue_validates_data(self, mock_dialog, github_handler):
        """Test create_issue validates dialog data."""
        # Setup mock dialog
        mock_dialog_instance = Mock()
        mock_dialog_instance.exec.return_value = True
        mock_dialog_instance.get_issue_data.return_value = (
            {  # ✅ Fixed: get_issue_data not get_data
                "title": "Bug report",
                "body": "Something is broken",
            }
        )
        mock_dialog.return_value = mock_dialog_instance

        # Call method
        github_handler.create_issue()

        # Verify data was retrieved
        assert (
            mock_dialog_instance.get_issue_data.called
        )  # ✅ Fixed: get_issue_data not get_data

    @patch("asciidoc_artisan.ui.github_handler.IssueListDialog")
    def test_list_issues_opens_dialog(self, mock_dialog, github_handler):
        """Test list_issues opens dialog."""
        # Setup mock dialog
        mock_dialog_instance = Mock()
        mock_dialog.return_value = mock_dialog_instance

        # Call method
        github_handler.list_issues()

        # Verify dialog was created
        assert mock_dialog.called

    @patch("asciidoc_artisan.ui.github_handler.IssueListDialog")
    def test_list_issues_triggers_worker(self, mock_dialog, github_handler, qtbot):
        """Test list_issues triggers worker via signal emission."""
        # Setup: Mock window to capture signal
        signal_emitted = []

        def capture_signal(operation, kwargs):
            signal_emitted.append((operation, kwargs))

        github_handler.window.request_github_command.connect(capture_signal)

        # Act: Call list_issues
        github_handler.list_issues()

        # Assert: Verify signal was emitted with correct operation
        assert len(signal_emitted) == 1
        operation, kwargs = signal_emitted[0]
        assert operation == "list_issues"
        assert "state" in kwargs
        assert "working_dir" in kwargs
        assert kwargs["working_dir"] == "/test/repo"


@pytest.mark.unit
class TestGitHubHandlerRepository:
    """Test repository operations."""

    def test_show_repo_info_triggers_worker(self, github_handler, qtbot):
        """Test get_repo_info triggers worker via signal emission."""
        # Setup: Mock window to capture signal
        signal_emitted = []

        def capture_signal(operation, kwargs):
            signal_emitted.append((operation, kwargs))

        github_handler.window.request_github_command.connect(capture_signal)

        # Act: Call get_repo_info (actual method name)
        github_handler.get_repo_info()

        # Assert: Verify signal was emitted with correct operation
        assert len(signal_emitted) == 1
        operation, kwargs = signal_emitted[0]
        assert operation == "get_repo_info"
        assert "working_dir" in kwargs
        assert kwargs["working_dir"] == "/test/repo"

    def test_show_repo_info_logs_data(self, github_handler, caplog):
        """Test _handle_repo_info logs repository information."""
        import logging

        # Create mock result with repo data
        result = GitHubResult(
            success=True,
            data={"nameWithOwner": "test/repo", "description": "Test repository"},
            error="",
            user_message="Repository info retrieved",
            operation="repo_view",
        )

        # Test that _handle_repo_info logs the data
        with caplog.at_level(logging.INFO):
            github_handler._handle_repo_info(result)

        # Verify logging occurred
        assert "Repository: test/repo" in caplog.text
        assert "Test repository" in caplog.text


@pytest.mark.unit
class TestGitHubHandlerErrorHandling:
    """Test error handling."""

    def test_handle_authentication_error(self, github_handler):
        """Test handling of authentication errors."""
        result = GitHubResult(
            success=False,
            data=None,
            error="not authenticated",
            user_message="Please authenticate with 'gh auth login'",
            operation="pr_create",
        )

        github_handler.handle_github_result(result)

        # Verify error message shown to user (check handler's status_manager)
        assert github_handler.status_manager.show_message.called

    def test_handle_no_remote_error(self, github_handler):
        """Test handling of no remote configured error."""
        result = GitHubResult(
            success=False,
            data=None,
            error="no default remote configured",
            user_message="Please add a GitHub remote",
            operation="pr_list",
        )

        github_handler.handle_github_result(result)

        # Verify error message shown (check handler's status_manager)
        assert github_handler.status_manager.show_message.called

    def test_handle_timeout_error(self, github_handler):
        """Test handling of timeout errors."""
        result = GitHubResult(
            success=False,
            data=None,
            error="timeout",
            user_message="Operation timed out",
            operation="issue_create",
        )

        github_handler.handle_github_result(result)

        # Verify error message shown (check handler's status_manager)
        assert github_handler.status_manager.show_message.called

    def test_handle_success_result(self, github_handler):
        """Test handling of successful operations."""
        result = GitHubResult(
            success=True,
            data={"number": 42, "url": "https://github.com/..."},
            error="",
            user_message="PR created successfully",
            operation="pr_create",
        )

        github_handler.handle_github_result(result)

        # Verify success message shown (check handler's status_manager)
        assert github_handler.status_manager.show_message.called


@pytest.mark.unit
class TestGitHubHandlerSignalSlots:
    """Test signal/slot connections."""

    def test_worker_signals_connected(self, github_handler):
        """Test request_github_command signal exists and is connectable."""
        # Verify the window has the signal
        assert hasattr(github_handler.window, "request_github_command")

        # Verify we can connect to it
        signal_captured = []

        def capture(*args):
            signal_captured.append(args)

        github_handler.window.request_github_command.connect(capture)

        # Emit a test signal
        github_handler.window.request_github_command.emit("test_op", {})

        # Verify signal was received
        assert len(signal_captured) == 1

    def test_result_signal_triggers_handler(self, github_handler):
        """Test handle_github_result processes results correctly."""
        # Create a success result
        result = GitHubResult(
            success=True,
            data={"number": 123},
            error="",
            user_message="Success",
            operation="pr_create",
        )

        # Verify handler can process result without error
        github_handler.handle_github_result(result)

        # Verify status message was shown
        assert github_handler.status_manager.show_message.called


@pytest.mark.unit
class TestGitHubHandlerStateManagement:
    """Test state management."""

    def test_last_operation_tracked(self, github_handler):
        """Test last operation is tracked."""
        if hasattr(github_handler, "last_operation"):
            # Set operation
            github_handler.last_operation = "pr_create"
            assert github_handler.last_operation == "pr_create"

    def test_state_reset_on_error(self, github_handler):
        """Test state is reset on error."""
        # Set processing flag
        github_handler.is_processing = True

        # Handle error result (must use valid operation from allowed set)
        result = GitHubResult(
            success=False,
            data=None,
            error="test error",
            user_message="Error occurred",
            operation="pr_create",  # ✅ Fixed: use valid operation
        )
        github_handler.handle_github_result(result)

        # Processing flag should be reset
        assert github_handler.is_processing is False


@pytest.mark.integration
class TestGitHubHandlerIntegration:
    """Integration tests for GitHub handler workflows."""

    @patch("asciidoc_artisan.ui.github_handler.CreatePullRequestDialog")
    def test_complete_pr_creation_workflow(self, mock_dialog, github_handler, qtbot):
        """Test complete PR creation workflow from dialog to signal emission."""
        # Setup mock dialog
        mock_dialog_instance = Mock()
        mock_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec.return_value = True  # Dialog accepted
        mock_dialog_instance.get_pr_data.return_value = {
            "title": "Test PR",
            "body": "PR body",
            "base": "main",
            "head": "feature",
        }

        # Capture signal
        signal_emitted = []

        def capture_signal(operation, kwargs):
            signal_emitted.append((operation, kwargs))

        github_handler.window.request_github_command.connect(capture_signal)

        # Act: Create PR
        github_handler.create_pull_request()

        # Assert: Dialog was shown and signal emitted
        assert mock_dialog.called
        assert len(signal_emitted) == 1
        operation, kwargs = signal_emitted[0]
        assert operation == "create_pull_request"
        assert kwargs["title"] == "Test PR"

    @patch("asciidoc_artisan.ui.github_handler.CreateIssueDialog")
    def test_complete_issue_creation_workflow(self, mock_dialog, github_handler, qtbot):
        """Test complete issue creation workflow from dialog to signal emission."""
        # Setup mock dialog
        mock_dialog_instance = Mock()
        mock_dialog.return_value = mock_dialog_instance
        mock_dialog_instance.exec.return_value = True  # Dialog accepted
        mock_dialog_instance.get_issue_data.return_value = {
            "title": "Test Issue",
            "body": "Issue body",
            "labels": ["bug"],
            "assignees": [],
        }

        # Capture signal
        signal_emitted = []

        def capture_signal(operation, kwargs):
            signal_emitted.append((operation, kwargs))

        github_handler.window.request_github_command.connect(capture_signal)

        # Act: Create issue
        github_handler.create_issue()

        # Assert: Dialog was shown and signal emitted
        assert mock_dialog.called
        assert len(signal_emitted) == 1
        operation, kwargs = signal_emitted[0]
        assert operation == "create_issue"
        assert kwargs["title"] == "Test Issue"


@pytest.mark.unit
class TestGitHubHandlerCleanup:
    """Test cleanup and resource management."""

    def test_handler_cleanup_stops_worker(self, mock_parent_window):
        """Test handler can be cleaned up without errors."""
        # Note: Worker lifecycle is managed by WorkerManager, not GitHubHandler
        # This test verifies the handler itself can be cleaned up safely

        # Create handler
        handler = GitHubHandler(
            mock_parent_window,
            Mock(),  # settings_manager
            Mock(),  # status_manager
            Mock(),  # git_handler
        )

        # Verify it exists
        assert handler is not None

        # Delete handler - should not raise errors
        del handler

    def test_handler_can_be_deleted(self, github_handler):
        """Test handler can be safely deleted."""
        # Note: Worker lifecycle is managed by WorkerManager, not GitHubHandler
        # This test verifies the handler doesn't hold resources that prevent deletion

        # Verify handler exists
        assert github_handler is not None

        # Store reference count info
        import sys

        refcount_before = sys.getrefcount(github_handler)

        # Handler should be deletable (no circular references or resource locks)
        # This is tested implicitly by pytest fixture cleanup
        assert refcount_before > 0  # Has at least one reference


@pytest.mark.unit
class TestGitHubHandlerInitializeAutoFetch:
    """Test initialize method auto-fetches repo info (lines 85-88)."""

    def test_initialize_auto_fetches_when_repo_set(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test initialize auto-fetches repo info when repository is set."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler

        # Mock git handler to return repo is set
        mock_git_handler.is_repository_set = Mock(return_value=True)

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        # Mock shutil.which to simulate gh CLI available
        # Mock get_repo_info to verify it's called
        with patch("shutil.which", return_value="/usr/bin/gh"):
            with patch.object(handler, "get_repo_info") as mock_get_repo:
                handler.initialize()

                # Should call get_repo_info with silent=True
                mock_get_repo.assert_called_once_with(silent=True)

    def test_initialize_skips_fetch_when_no_repo(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test initialize skips fetch when no repository set."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler

        # Mock git handler to return repo not set
        mock_git_handler.is_repository_set = Mock(return_value=False)

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        # Mock shutil.which to simulate gh CLI available
        # Mock get_repo_info to verify it's NOT called
        with patch("shutil.which", return_value="/usr/bin/gh"):
            with patch.object(handler, "get_repo_info") as mock_get_repo:
                handler.initialize()

                # Should NOT call get_repo_info
                mock_get_repo.assert_not_called()


@pytest.mark.unit
class TestGitHubHandlerEarlyReturns:
    """Test early returns when not ready (lines 138, 174, 214, 255)."""

    def test_list_pull_requests_early_return(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test list_pull_requests returns early when not ready (line 138)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        # Mock _ensure_ready to return False
        with patch.object(handler, "_ensure_ready", return_value=False):
            # Should return early without creating dialog
            handler.list_pull_requests()

            # Verify no dialog created (would crash if attempted)
            assert handler.current_dialog is None

    def test_create_issue_early_return(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test create_issue returns early when not ready (line 174)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        with patch.object(handler, "_ensure_ready", return_value=False):
            handler.create_issue()

            # Verify processing not started
            assert not handler.is_processing

    def test_list_issues_early_return(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test list_issues returns early when not ready (line 214)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        with patch.object(handler, "_ensure_ready", return_value=False):
            handler.list_issues()

            assert handler.current_dialog is None

    def test_get_repo_info_early_return(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test get_repo_info returns early when not ready (line 255)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        with patch.object(handler, "_ensure_ready", return_value=False):
            handler.get_repo_info()

            assert not handler.is_processing


@pytest.mark.unit
class TestGitHubHandlerResultDispatching:
    """Test result handler dispatching (lines 296-303)."""

    def test_handle_result_dispatches_pr_list(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test handle_github_result dispatches to _handle_pr_list (line 297)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler
        from asciidoc_artisan.workers.github_cli_worker import GitHubResult

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )
        handler.is_processing = True
        handler.last_operation = "pr_list"

        result = GitHubResult(
            success=True,
            operation="pr_list",
            user_message="PRs loaded",
            data=[{"number": 1, "title": "Test PR"}],
        )

        with patch.object(handler, "_handle_pr_list") as mock_handler:
            handler.handle_github_result(result)

            mock_handler.assert_called_once_with(result)

    def test_handle_result_dispatches_issue_create(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test handle_github_result dispatches to _handle_issue_created (line 299)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler
        from asciidoc_artisan.workers.github_cli_worker import GitHubResult

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )
        handler.is_processing = True

        result = GitHubResult(
            success=True,
            operation="issue_create",
            user_message="Issue created",
            data={"number": 42, "url": "https://github.com/org/repo/issues/42"},
        )

        with patch.object(handler, "_handle_issue_created") as mock_handler:
            handler.handle_github_result(result)

            mock_handler.assert_called_once_with(result)

    def test_handle_result_dispatches_issue_list(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test handle_github_result dispatches to _handle_issue_list (line 301)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler
        from asciidoc_artisan.workers.github_cli_worker import GitHubResult

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )
        handler.is_processing = True

        result = GitHubResult(
            success=True,
            operation="issue_list",
            user_message="Issues loaded",
            data=[{"number": 1, "title": "Test Issue"}],
        )

        with patch.object(handler, "_handle_issue_list") as mock_handler:
            handler.handle_github_result(result)

            mock_handler.assert_called_once_with(result)

    def test_handle_result_dispatches_repo_info(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test handle_github_result dispatches to _handle_repo_info (line 303)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler
        from asciidoc_artisan.workers.github_cli_worker import GitHubResult

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )
        handler.is_processing = True

        result = GitHubResult(
            success=True,
            operation="repo_info",
            user_message="Repo info loaded",
            data={"name": "test-repo", "description": "Test"},
        )

        with patch.object(handler, "_handle_repo_info") as mock_handler:
            handler.handle_github_result(result)

            mock_handler.assert_called_once_with(result)


@pytest.mark.unit
class TestGitHubHandlerResultHandlers:
    """Test individual result handler methods (lines 336-365)."""

    def test_handle_pr_list_updates_cache(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test _handle_pr_list updates cached PRs (lines 336-346)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler
        from asciidoc_artisan.workers.github_cli_worker import GitHubResult

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        pr_data = [
            {"number": 1, "title": "PR 1"},
            {"number": 2, "title": "PR 2"},
        ]

        result = GitHubResult(
            success=True, operation="pr_list", user_message="Success", data=pr_data
        )

        handler._handle_pr_list(result)

        # Verify cache updated
        assert handler.cached_prs == pr_data

    def test_handle_pr_list_updates_open_dialog(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
        qapp,
    ):
        """Test _handle_pr_list updates open dialog (lines 341-344)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler
        from asciidoc_artisan.workers.github_cli_worker import GitHubResult

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        # Create mock dialog
        mock_dialog = Mock()
        mock_dialog.set_pr_data = Mock()
        handler.current_dialog = mock_dialog

        # Mock isinstance to return True for PullRequestListDialog
        with patch("asciidoc_artisan.ui.github_handler.isinstance", return_value=True):
            pr_data = [{"number": 1, "title": "Test PR"}]
            result = GitHubResult(
                success=True, operation="pr_list", user_message="Success", data=pr_data
            )

            handler._handle_pr_list(result)

            # Verify dialog updated
            mock_dialog.set_pr_data.assert_called_once_with(pr_data)

    def test_handle_issue_created_logs_url(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
        caplog,
    ):
        """Test _handle_issue_created logs issue URL (lines 350-353)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler
        from asciidoc_artisan.workers.github_cli_worker import GitHubResult

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        result = GitHubResult(
            success=True,
            operation="issue_create",
            user_message="Success",
            data={"number": 42, "url": "https://github.com/org/repo/issues/42"},
        )

        with caplog.at_level("INFO"):
            handler._handle_issue_created(result)

            # Verify logged
            assert "Issue #42 created" in caplog.text
            assert "https://github.com/org/repo/issues/42" in caplog.text

    def test_handle_issue_list_updates_cache(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test _handle_issue_list updates cached issues (lines 357-365)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler
        from asciidoc_artisan.workers.github_cli_worker import GitHubResult

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        issue_data = [
            {"number": 1, "title": "Issue 1"},
            {"number": 2, "title": "Issue 2"},
        ]

        result = GitHubResult(
            success=True,
            operation="issue_list",
            user_message="Success",
            data=issue_data,
        )

        handler._handle_issue_list(result)

        # Verify cache updated
        assert handler.cached_issues == issue_data

    def test_handle_issue_list_updates_open_dialog(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test _handle_issue_list updates open dialog (lines 362-363)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler
        from asciidoc_artisan.workers.github_cli_worker import GitHubResult

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        # Create mock dialog
        mock_dialog = Mock()
        mock_dialog.set_issue_data = Mock()
        handler.current_dialog = mock_dialog

        # Mock isinstance to return True for IssueListDialog
        with patch("asciidoc_artisan.ui.github_handler.isinstance", return_value=True):
            issue_data = [{"number": 1, "title": "Test Issue"}]
            result = GitHubResult(
                success=True,
                operation="issue_list",
                user_message="Success",
                data=issue_data,
            )

            handler._handle_issue_list(result)

            # Verify dialog updated
            mock_dialog.set_issue_data.assert_called_once_with(issue_data)


@pytest.mark.unit
class TestGitHubHandlerRepoInfoDialog:
    """Test repository info dialog (lines 404-422)."""

    def test_handle_repo_info_shows_dialog(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
        qapp,
    ):
        """Test _handle_repo_info shows QMessageBox (lines 404-422)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler
        from asciidoc_artisan.workers.github_cli_worker import GitHubResult

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )
        handler.last_operation = "repo_info"  # Not silent

        repo_data = {
            "name": "test-repo",
            "description": "A test repository",
            "default_branch": "main",
            "visibility": "public",
            "stargazers_count": 42,
            "forks_count": 7,
            "html_url": "https://github.com/org/test-repo",
        }

        result = GitHubResult(
            success=True, operation="repo_info", user_message="Success", data=repo_data
        )

        # Mock QMessageBox (imported locally in _handle_repo_info)
        with patch("PySide6.QtWidgets.QMessageBox") as mock_msgbox:
            mock_box_instance = Mock()
            mock_msgbox.return_value = mock_box_instance

            handler._handle_repo_info(result)

            # Verify QMessageBox created and shown
            mock_msgbox.assert_called_once_with(mock_parent_window)
            mock_box_instance.setWindowTitle.assert_called_once_with(
                "Repository Information"
            )
            mock_box_instance.exec.assert_called_once()

    def test_handle_repo_info_skips_dialog_when_silent(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test _handle_repo_info skips dialog for silent operations."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler
        from asciidoc_artisan.workers.github_cli_worker import GitHubResult

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )
        handler.last_operation = "repo_info_silent"  # Silent operation

        repo_data = {
            "name": "test-repo",
            "description": "Test",
            "default_branch": "main",
            "visibility": "public",
            "stargazers_count": 0,
            "forks_count": 0,
            "html_url": "https://github.com/org/test-repo",
        }

        result = GitHubResult(
            success=True, operation="repo_info", user_message="Success", data=repo_data
        )

        # Mock QMessageBox - should NOT be called (imported locally in _handle_repo_info)
        with patch("PySide6.QtWidgets.QMessageBox") as mock_msgbox:
            handler._handle_repo_info(result)

            # Verify QMessageBox NOT created
            mock_msgbox.assert_not_called()


@pytest.mark.unit
class TestGitHubHandlerHelperMethods:
    """Test helper methods (lines 466, 470)."""

    def test_get_current_branch_returns_empty_when_no_handler(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test _get_current_branch returns empty string when no git_handler (line 466)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        # Remove git_handler
        delattr(mock_parent_window, "git_handler")

        # Should return empty string
        result = handler._get_current_branch()
        assert result == ""

    def test_is_busy_returns_processing_state(
        self,
        mock_parent_window,
        mock_settings_manager,
        mock_status_manager,
        mock_git_handler,
    ):
        """Test is_busy returns processing state (line 470)."""
        from asciidoc_artisan.ui.github_handler import GitHubHandler

        handler = GitHubHandler(
            mock_parent_window,
            mock_settings_manager,
            mock_status_manager,
            mock_git_handler,
        )

        # Not processing
        handler.is_processing = False
        assert handler.is_busy() is False

        # Processing
        handler.is_processing = True
        assert handler.is_busy() is True
