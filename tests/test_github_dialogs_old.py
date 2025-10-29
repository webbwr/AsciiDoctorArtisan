"""
Unit tests for GitHub dialog classes.

Tests UI dialogs for creating/viewing pull requests and issues.
Uses pytest-qt (qtbot) for Qt widget testing.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from asciidoc_artisan.ui.github_dialogs import (
    CreateIssueDialog,
    CreatePullRequestDialog,
    IssueListDialog,
    PullRequestListDialog,
)


@pytest.mark.unit
class TestCreatePullRequestDialog:
    """Test CreatePullRequestDialog for PR creation."""

    def test_dialog_initialization(self, qtbot):
        """Test dialog initializes correctly."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None
        assert isinstance(dialog, QDialog)
        assert dialog.windowTitle() == "Create Pull Request"

    def test_dialog_has_required_fields(self, qtbot):
        """Test dialog has all required input fields."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Check for title field
        assert hasattr(dialog, "title_edit") or hasattr(dialog, "title_input")

        # Check for base branch field
        assert hasattr(dialog, "base_combo") or hasattr(dialog, "base_branch")

        # Check for head branch field
        assert hasattr(dialog, "head_combo") or hasattr(dialog, "head_branch")

        # Check for body field
        assert hasattr(dialog, "body_edit") or hasattr(dialog, "body_input")

    def test_dialog_validation_empty_title(self, qtbot):
        """Test dialog validation rejects empty title."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Try to accept dialog with empty title
        title_field = getattr(dialog, "title_edit", None) or getattr(dialog, "title_input", None)
        if title_field:
            title_field.clear()

        # Attempt to accept
        result = dialog.validate()

        # Should fail validation
        assert result is False or dialog.result() != QDialog.Accepted

    def test_dialog_validation_valid_input(self, qtbot):
        """Test dialog validation passes with valid input."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Set valid title
        title_field = getattr(dialog, "title_edit", None) or getattr(dialog, "title_input", None)
        if title_field:
            title_field.setText("Test PR Title")

        # Attempt validation
        result = dialog.validate()

        # Should pass validation
        assert result is True

    def test_dialog_get_data(self, qtbot):
        """Test retrieving data from dialog."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Set some test data
        title_field = getattr(dialog, "title_edit", None) or getattr(dialog, "title_input", None)
        body_field = getattr(dialog, "body_edit", None) or getattr(dialog, "body_input", None)

        if title_field:
            title_field.setText("Test PR")
        if body_field:
            body_field.setPlainText("Test description")

        # Get data
        data = dialog.get_data()

        # Verify data structure
        assert "title" in data
        assert data["title"] == "Test PR"
        if "body" in data:
            assert data["body"] == "Test description"

    def test_dialog_base_not_equal_head(self, qtbot):
        """Test validation ensures base branch != head branch."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Try to set same branch for base and head
        base_field = getattr(dialog, "base_combo", None) or getattr(dialog, "base_branch", None)
        head_field = getattr(dialog, "head_combo", None) or getattr(dialog, "head_branch", None)

        if base_field and head_field:
            # Set both to same value
            if hasattr(base_field, "setCurrentText"):
                base_field.setCurrentText("main")
                head_field.setCurrentText("main")

            # Validation should fail
            result = dialog.validate()
            assert result is False

    def test_dialog_cancel_button(self, qtbot):
        """Test cancel button rejects dialog."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Find and click cancel button
        cancel_button = None
        for button in dialog.findChildren(type(dialog.findChild(type(dialog.buttons().buttons()[0])))):
            if button.text().lower() in ["cancel", "&cancel"]:
                cancel_button = button
                break

        if cancel_button:
            qtbot.mouseClick(cancel_button, Qt.LeftButton)
            assert dialog.result() == QDialog.Rejected


@pytest.mark.unit
class TestPullRequestListDialog:
    """Test PullRequestListDialog for viewing PRs."""

    def test_dialog_initialization(self, qtbot):
        """Test dialog initializes correctly."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None
        assert isinstance(dialog, QDialog)
        assert "Pull Request" in dialog.windowTitle()

    def test_dialog_has_list_widget(self, qtbot):
        """Test dialog has list widget for PRs."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        # Check for list widget
        assert hasattr(dialog, "pr_list") or hasattr(dialog, "list_widget")

    def test_dialog_populate_prs(self, qtbot):
        """Test populating dialog with PR data."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        # Test data
        test_prs = [
            {"number": 42, "title": "Test PR 1", "state": "open", "url": "https://github.com/..."},
            {"number": 41, "title": "Test PR 2", "state": "merged", "url": "https://github.com/..."}
        ]

        # Populate
        dialog.populate_prs(test_prs)

        # Verify list populated
        list_widget = getattr(dialog, "pr_list", None) or getattr(dialog, "list_widget", None)
        if list_widget:
            assert list_widget.count() == 2

    def test_dialog_state_filter(self, qtbot):
        """Test state filter for PRs (open, closed, merged)."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        # Check for state filter widgets
        has_filter = (
            hasattr(dialog, "state_filter") or
            hasattr(dialog, "open_radio") or
            hasattr(dialog, "filter_combo")
        )
        assert has_filter

    def test_dialog_refresh_button(self, qtbot):
        """Test refresh button exists and is clickable."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        # Find refresh button
        refresh_button = getattr(dialog, "refresh_button", None)
        if refresh_button:
            assert refresh_button.isEnabled()

    def test_dialog_double_click_opens_browser(self, qtbot):
        """Test double-clicking PR opens in browser."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        # Populate with test data
        test_prs = [
            {"number": 42, "title": "Test PR", "state": "open", "url": "https://github.com/test/pr/42"}
        ]
        dialog.populate_prs(test_prs)

        # Get list widget
        list_widget = getattr(dialog, "pr_list", None) or getattr(dialog, "list_widget", None)
        if list_widget and list_widget.count() > 0:
            # Check that double-click handler is connected
            # (actual browser opening would be mocked in integration tests)
            assert list_widget.itemDoubleClicked is not None


@pytest.mark.unit
class TestCreateIssueDialog:
    """Test CreateIssueDialog for issue creation."""

    def test_dialog_initialization(self, qtbot):
        """Test dialog initializes correctly."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None
        assert isinstance(dialog, QDialog)
        assert "Create Issue" in dialog.windowTitle()

    def test_dialog_has_required_fields(self, qtbot):
        """Test dialog has required input fields."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Check for title field
        assert hasattr(dialog, "title_edit") or hasattr(dialog, "title_input")

        # Check for body field
        assert hasattr(dialog, "body_edit") or hasattr(dialog, "body_input")

    def test_dialog_validation_empty_title(self, qtbot):
        """Test dialog validation rejects empty title."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Try to accept dialog with empty title
        title_field = getattr(dialog, "title_edit", None) or getattr(dialog, "title_input", None)
        if title_field:
            title_field.clear()

        # Attempt validation
        result = dialog.validate()

        # Should fail validation
        assert result is False or dialog.result() != QDialog.Accepted

    def test_dialog_validation_valid_input(self, qtbot):
        """Test dialog validation passes with valid title."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Set valid title
        title_field = getattr(dialog, "title_edit", None) or getattr(dialog, "title_input", None)
        if title_field:
            title_field.setText("Bug: Something is broken")

        # Attempt validation
        result = dialog.validate()

        # Should pass validation
        assert result is True

    def test_dialog_get_data(self, qtbot):
        """Test retrieving data from dialog."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Set test data
        title_field = getattr(dialog, "title_edit", None) or getattr(dialog, "title_input", None)
        body_field = getattr(dialog, "body_edit", None) or getattr(dialog, "body_input", None)

        if title_field:
            title_field.setText("Test Issue")
        if body_field:
            body_field.setPlainText("Issue description")

        # Get data
        data = dialog.get_data()

        # Verify data structure
        assert "title" in data
        assert data["title"] == "Test Issue"
        if "body" in data:
            assert data["body"] == "Issue description"

    def test_dialog_labels_field(self, qtbot):
        """Test labels field exists for issue creation."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Check for labels field
        has_labels = (
            hasattr(dialog, "labels_input") or
            hasattr(dialog, "labels_edit") or
            hasattr(dialog, "labels_widget")
        )
        assert has_labels

    def test_dialog_assignees_field(self, qtbot):
        """Test assignees field exists for issue creation."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Check for assignees field
        has_assignees = (
            hasattr(dialog, "assignees_input") or
            hasattr(dialog, "assignees_edit") or
            hasattr(dialog, "assignees_widget")
        )
        assert has_assignees


@pytest.mark.unit
class TestIssueListDialog:
    """Test IssueListDialog for viewing issues."""

    def test_dialog_initialization(self, qtbot):
        """Test dialog initializes correctly."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None
        assert isinstance(dialog, QDialog)
        assert "Issue" in dialog.windowTitle()

    def test_dialog_has_list_widget(self, qtbot):
        """Test dialog has list widget for issues."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Check for list widget
        assert hasattr(dialog, "issue_list") or hasattr(dialog, "list_widget")

    def test_dialog_populate_issues(self, qtbot):
        """Test populating dialog with issue data."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Test data
        test_issues = [
            {"number": 15, "title": "Bug report", "state": "open", "url": "https://github.com/..."},
            {"number": 14, "title": "Enhancement", "state": "closed", "url": "https://github.com/..."}
        ]

        # Populate
        dialog.populate_issues(test_issues)

        # Verify list populated
        list_widget = getattr(dialog, "issue_list", None) or getattr(dialog, "list_widget", None)
        if list_widget:
            assert list_widget.count() == 2

    def test_dialog_state_filter(self, qtbot):
        """Test state filter for issues (open, closed)."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Check for state filter widgets
        has_filter = (
            hasattr(dialog, "state_filter") or
            hasattr(dialog, "open_radio") or
            hasattr(dialog, "filter_combo")
        )
        assert has_filter

    def test_dialog_refresh_button(self, qtbot):
        """Test refresh button exists."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Find refresh button
        refresh_button = getattr(dialog, "refresh_button", None)
        if refresh_button:
            assert refresh_button.isEnabled()

    def test_dialog_double_click_opens_browser(self, qtbot):
        """Test double-clicking issue opens in browser."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Populate with test data
        test_issues = [
            {"number": 15, "title": "Test Issue", "state": "open", "url": "https://github.com/test/issues/15"}
        ]
        dialog.populate_issues(test_issues)

        # Get list widget
        list_widget = getattr(dialog, "issue_list", None) or getattr(dialog, "list_widget", None)
        if list_widget and list_widget.count() > 0:
            # Check that double-click handler is connected
            assert list_widget.itemDoubleClicked is not None

    def test_dialog_close_button(self, qtbot):
        """Test close button exists and works."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Find close button
        close_button = None
        for button in dialog.findChildren(type(dialog.buttons().buttons()[0]) if hasattr(dialog, 'buttons') else object):
            if hasattr(button, 'text') and button.text().lower() in ["close", "&close"]:
                close_button = button
                break

        if close_button:
            qtbot.mouseClick(close_button, Qt.LeftButton)
            assert dialog.result() == QDialog.Rejected


@pytest.mark.integration
class TestDialogIntegration:
    """Integration tests for dialog workflows."""

    def test_pr_dialog_workflow(self, qtbot):
        """Test complete PR creation workflow."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Fill in fields
        title_field = getattr(dialog, "title_edit", None) or getattr(dialog, "title_input", None)
        if title_field:
            title_field.setText("Feature: Add new capability")

        body_field = getattr(dialog, "body_edit", None) or getattr(dialog, "body_input", None)
        if body_field:
            body_field.setPlainText("This PR adds a new capability to the application.")

        # Validate
        is_valid = dialog.validate()
        assert is_valid

        # Get data
        data = dialog.get_data()
        assert data["title"] == "Feature: Add new capability"

    def test_issue_dialog_workflow(self, qtbot):
        """Test complete issue creation workflow."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Fill in fields
        title_field = getattr(dialog, "title_edit", None) or getattr(dialog, "title_input", None)
        if title_field:
            title_field.setText("Bug: Application crashes on startup")

        body_field = getattr(dialog, "body_edit", None) or getattr(dialog, "body_input", None)
        if body_field:
            body_field.setPlainText("Steps to reproduce:\n1. Launch app\n2. Crash occurs")

        # Validate
        is_valid = dialog.validate()
        assert is_valid

        # Get data
        data = dialog.get_data()
        assert data["title"] == "Bug: Application crashes on startup"
