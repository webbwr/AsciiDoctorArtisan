"""
Unit tests for GitHub dialog classes.

Tests UI dialogs for creating/viewing pull requests and issues.
Uses pytest-qt (qtbot) for Qt widget testing.

UPDATED: Fixed API mismatches to align with actual dialog implementation.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from PySide6.QtWidgets import QPushButton

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

        # Check for title field (actual name: title_input)
        assert hasattr(dialog, "title_input")

        # Check for base branch field (actual name: base_input)
        assert hasattr(dialog, "base_input")

        # Check for head branch field (actual name: head_input)
        assert hasattr(dialog, "head_input")

        # Check for body field (actual name: body_input)
        assert hasattr(dialog, "body_input")

        # Check for draft checkbox
        assert hasattr(dialog, "draft_checkbox")

    def test_dialog_validation_empty_title(self, qtbot):
        """Test dialog validation rejects empty title."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Clear title field
        dialog.title_input.clear()

        # Call internal validation (simulates user clicking OK)
        dialog._validate_and_accept()

        # Should not accept dialog (validation failed)
        assert dialog.result() != QDialog.Accepted

    def test_dialog_validation_valid_input(self, qtbot):
        """Test dialog accepts with valid input."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Set valid title
        dialog.title_input.setText("Test PR Title")
        dialog.base_input.setText("main")
        dialog.head_input.setCurrentText("feature-branch")

        # Call internal validation
        dialog._validate_and_accept()

        # Should accept dialog
        assert dialog.result() == QDialog.Accepted

    def test_dialog_get_pr_data(self, qtbot):
        """Test retrieving data from dialog."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Set some test data
        dialog.title_input.setText("Test PR")
        dialog.body_input.setPlainText("Test description")
        dialog.base_input.setText("main")
        dialog.head_input.setCurrentText("feature")
        dialog.draft_checkbox.setChecked(True)

        # Get data (use correct method name: get_pr_data)
        data = dialog.get_pr_data()

        # Verify data structure
        assert "title" in data
        assert data["title"] == "Test PR"
        assert "body" in data
        assert data["body"] == "Test description"
        assert "base" in data
        assert data["base"] == "main"
        assert "head" in data
        assert data["head"] == "feature"
        assert "draft" in data
        assert data["draft"] == "true"

    def test_dialog_base_not_equal_head(self, qtbot):
        """Test validation ensures base branch != head branch."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Set required title
        dialog.title_input.setText("Test PR")

        # Set same branch for base and head
        dialog.base_input.setText("main")
        dialog.head_input.setCurrentText("main")

        # Call internal validation
        dialog._validate_and_accept()

        # Validation should fail (base == head)
        assert dialog.result() != QDialog.Accepted

    def test_dialog_cancel_button(self, qtbot):
        """Test cancel button rejects dialog."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Reject dialog (simulates cancel button)
        dialog.reject()

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

    def test_dialog_has_table_widget(self, qtbot):
        """Test dialog has table widget for PRs."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        # Check for table widget (actual name: pr_table)
        assert hasattr(dialog, "pr_table")

    def test_dialog_set_pr_data(self, qtbot):
        """Test populating dialog with PR data."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        # Test data (both "open" so they pass the default filter)
        test_prs = [
            {
                "number": 42,
                "title": "Test PR 1",
                "author": {"login": "testuser"},
                "state": "open",
                "createdAt": "2025-10-01",
                "url": "https://github.com/test/repo/pull/42",
            },
            {
                "number": 41,
                "title": "Test PR 2",
                "author": {"login": "testuser2"},
                "state": "open",  # Changed to "open" to pass default filter
                "createdAt": "2025-09-15",
                "url": "https://github.com/test/repo/pull/41",
            },
        ]

        # Populate (use correct method name: set_pr_data)
        dialog.set_pr_data(test_prs)

        # Verify table populated (both PRs are "open" so both show)
        assert dialog.pr_table.rowCount() == 2

    def test_dialog_state_filter(self, qtbot):
        """Test state filter for PRs (open, closed, merged)."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        # Check for state filter combo (actual name: state_filter)
        assert hasattr(dialog, "state_filter")

    def test_dialog_refresh_button(self, qtbot):
        """Test refresh button exists and is clickable."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        # Refresh button exists as local variable, check via findChildren
        buttons = dialog.findChildren(QPushButton)
        refresh_buttons = [btn for btn in buttons if "refresh" in btn.text().lower()]
        assert len(refresh_buttons) > 0

    def test_dialog_empty_state(self, qtbot):
        """Test dialog handles empty PR list."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        # Set empty data
        dialog.set_pr_data([])

        # Should show 1 row with "No pull requests found" message
        assert dialog.pr_table.rowCount() == 1
        # Verify it's the "no data" message
        item = dialog.pr_table.item(0, 0)
        assert item is not None
        assert "no pull request" in item.text().lower()


@pytest.mark.unit
class TestCreateIssueDialog:
    """Test CreateIssueDialog for issue creation."""

    def test_dialog_initialization(self, qtbot):
        """Test dialog initializes correctly."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None
        assert isinstance(dialog, QDialog)
        assert dialog.windowTitle() == "Create Issue"

    def test_dialog_has_required_fields(self, qtbot):
        """Test dialog has all required input fields."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Check for title field (actual name: title_input)
        assert hasattr(dialog, "title_input")

        # Check for body field (actual name: body_input)
        assert hasattr(dialog, "body_input")

        # Check for labels field (actual name: labels_input)
        assert hasattr(dialog, "labels_input")

    def test_dialog_validation_empty_title(self, qtbot):
        """Test dialog validation rejects empty title."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Clear title field
        dialog.title_input.clear()

        # Call internal validation
        dialog._validate_and_accept()

        # Should not accept dialog
        assert dialog.result() != QDialog.Accepted

    def test_dialog_validation_valid_input(self, qtbot):
        """Test dialog accepts with valid input."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Set valid title
        dialog.title_input.setText("Test Issue Title")

        # Call internal validation
        dialog._validate_and_accept()

        # Should accept dialog
        assert dialog.result() == QDialog.Accepted

    def test_dialog_get_issue_data(self, qtbot):
        """Test retrieving data from dialog."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Set some test data
        dialog.title_input.setText("Test Issue")
        dialog.body_input.setPlainText("Test description")
        dialog.labels_input.setText("bug, enhancement")

        # Get data (use correct method name: get_issue_data)
        data = dialog.get_issue_data()

        # Verify data structure
        assert "title" in data
        assert data["title"] == "Test Issue"
        assert "body" in data
        assert data["body"] == "Test description"
        assert "labels" in data
        assert data["labels"] == "bug, enhancement"

    def test_dialog_optional_fields(self, qtbot):
        """Test dialog accepts with only required fields."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Set only title (required)
        dialog.title_input.setText("Minimum Issue")
        # Leave body and labels empty

        # Get data
        data = dialog.get_issue_data()

        # Should have title, empty body and labels
        assert data["title"] == "Minimum Issue"
        assert data["body"] == ""
        assert data["labels"] == ""

    def test_dialog_cancel_button(self, qtbot):
        """Test cancel button rejects dialog."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Reject dialog (simulates cancel button)
        dialog.reject()

        assert dialog.result() == QDialog.Rejected


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

    def test_dialog_has_table_widget(self, qtbot):
        """Test dialog has table widget for issues."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Check for table widget (actual name: issue_table)
        assert hasattr(dialog, "issue_table")

    def test_dialog_set_issue_data(self, qtbot):
        """Test populating dialog with issue data."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Test data (both "open" so they pass the default filter)
        test_issues = [
            {
                "number": 15,
                "title": "Test Issue 1",
                "author": {"login": "testuser"},
                "state": "open",
                "createdAt": "2025-10-01",
                "url": "https://github.com/test/repo/issues/15",
            },
            {
                "number": 14,
                "title": "Test Issue 2",
                "author": {"login": "testuser2"},
                "state": "open",  # Changed to "open" to pass default filter
                "createdAt": "2025-09-15",
                "url": "https://github.com/test/repo/issues/14",
            },
        ]

        # Populate (use correct method name: set_issue_data)
        dialog.set_issue_data(test_issues)

        # Verify table populated (both issues are "open" so both show)
        assert dialog.issue_table.rowCount() == 2

    def test_dialog_state_filter(self, qtbot):
        """Test state filter for issues (open, closed)."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Check for state filter combo (actual name: state_filter)
        assert hasattr(dialog, "state_filter")

    def test_dialog_refresh_button(self, qtbot):
        """Test refresh button exists and is clickable."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Refresh button exists as local variable, check via findChildren
        from PySide6.QtWidgets import QPushButton

        buttons = dialog.findChildren(QPushButton)
        refresh_buttons = [btn for btn in buttons if "refresh" in btn.text().lower()]
        assert len(refresh_buttons) > 0

    def test_dialog_empty_state(self, qtbot):
        """Test dialog handles empty issue list."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Set empty data
        dialog.set_issue_data([])

        # Should show 1 row with "No issues found" message
        assert dialog.issue_table.rowCount() == 1
        # Verify it's the "no data" message
        item = dialog.issue_table.item(0, 0)
        assert item is not None
        assert "no issue" in item.text().lower()


@pytest.mark.unit
class TestDialogIntegration:
    """Test cross-dialog integration scenarios."""

    def test_all_dialogs_import(self):
        """Test all dialog classes can be imported."""
        assert CreatePullRequestDialog is not None
        assert PullRequestListDialog is not None
        assert CreateIssueDialog is not None
        assert IssueListDialog is not None

    def test_all_dialogs_instantiate(self, qtbot):
        """Test all dialog classes can be instantiated."""
        pr_create = CreatePullRequestDialog()
        qtbot.addWidget(pr_create)
        assert pr_create is not None

        pr_list = PullRequestListDialog()
        qtbot.addWidget(pr_list)
        assert pr_list is not None

        issue_create = CreateIssueDialog()
        qtbot.addWidget(issue_create)
        assert issue_create is not None

        issue_list = IssueListDialog()
        qtbot.addWidget(issue_list)
        assert issue_list is not None
