"""
Unit tests for GitHub dialog classes.

Tests UI dialogs for creating/viewing pull requests and issues.
Uses pytest-qt (qtbot) for Qt widget testing.

UPDATED: Comprehensive coverage from ~56% to 90%+ including validation helpers,
state filtering, author variants, missing data handling, and UI interactions.
"""

from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QDialog, QLineEdit, QPushButton

from asciidoc_artisan.ui.github_dialogs import (
    CreateIssueDialog,
    CreatePullRequestDialog,
    IssueListDialog,
    PullRequestListDialog,
    _clear_validation_error,
    _show_validation_error,
    _validate_required_text,
)

# === VALIDATION HELPER TESTS ===


@pytest.mark.fr_034
@pytest.mark.fr_035
@pytest.mark.fr_036
@pytest.mark.fr_037
@pytest.mark.fr_038
@pytest.mark.unit
class TestValidationHelpers:
    """Test validation helper functions."""

    def test_show_validation_error_applies_red_border(self, qtbot):
        """Test _show_validation_error applies red border to widget."""
        widget = QLineEdit()
        qtbot.addWidget(widget)

        _show_validation_error(widget, "QLineEdit")

        # Verify red border applied
        assert "border: 1px solid red" in widget.styleSheet()

    def test_show_validation_error_sets_focus(self, qtbot):
        """Test _show_validation_error sets focus to widget."""
        widget = QLineEdit()
        qtbot.addWidget(widget)
        widget.show()

        _show_validation_error(widget, "QLineEdit")

        # Verify focus set (need to process events for focus to take effect)
        qtbot.wait(10)
        assert widget.hasFocus()

    def test_clear_validation_error_removes_styling(self, qtbot):
        """Test _clear_validation_error removes custom styling."""
        widget = QLineEdit()
        qtbot.addWidget(widget)

        # First apply error styling
        widget.setStyleSheet("QLineEdit { border: 1px solid red; }")
        assert widget.styleSheet() != ""

        # Clear error
        _clear_validation_error(widget)

        # Verify styling removed
        assert widget.styleSheet() == ""

    @patch("asciidoc_artisan.ui.github_dialogs.logger")
    def test_validate_required_text_empty_string(self, mock_logger, qtbot):
        """Test _validate_required_text rejects empty string."""
        widget = QLineEdit()
        qtbot.addWidget(widget)
        widget.setText("")

        result = _validate_required_text(widget, "Test Field")

        assert result is False
        assert "border: 1px solid red" in widget.styleSheet()
        mock_logger.warning.assert_called_once_with("Test Field is required")

    @patch("asciidoc_artisan.ui.github_dialogs.logger")
    def test_validate_required_text_whitespace_only(self, mock_logger, qtbot):
        """Test _validate_required_text rejects whitespace-only string."""
        widget = QLineEdit()
        qtbot.addWidget(widget)
        widget.setText("   ")

        result = _validate_required_text(widget, "Test Field")

        assert result is False
        assert "border: 1px solid red" in widget.styleSheet()
        mock_logger.warning.assert_called_once_with("Test Field is required")

    def test_validate_required_text_valid_input(self, qtbot):
        """Test _validate_required_text accepts valid text."""
        widget = QLineEdit()
        qtbot.addWidget(widget)
        widget.setText("Valid text")

        result = _validate_required_text(widget, "Test Field")

        assert result is True
        assert widget.styleSheet() == ""

    def test_validate_required_text_clears_previous_error(self, qtbot):
        """Test _validate_required_text clears previous error styling."""
        widget = QLineEdit()
        qtbot.addWidget(widget)

        # First fail validation
        widget.setText("")
        _validate_required_text(widget, "Test Field")
        assert widget.styleSheet() != ""

        # Then pass validation
        widget.setText("Valid text")
        result = _validate_required_text(widget, "Test Field")

        assert result is True
        assert widget.styleSheet() == ""


# === CREATE PULL REQUEST DIALOG TESTS ===


@pytest.mark.fr_034
@pytest.mark.fr_035
@pytest.mark.fr_036
@pytest.mark.fr_037
@pytest.mark.fr_038
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

    @pytest.mark.parametrize(
        "title,base,head,expected_accepted,test_id",
        [
            ("", "main", "feature-branch", False, "empty_title"),
            ("Test PR Title", "main", "feature-branch", True, "valid_input"),
        ],
    )
    def test_dialog_validation(
        self, qtbot, title, base, head, expected_accepted, test_id
    ):
        """Test dialog validation with various inputs.

        Parametrized test covering:
        - Empty title (rejected)
        - Valid input (accepted)
        """
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        # Set input values
        if title:
            dialog.title_input.setText(title)
        else:
            dialog.title_input.clear()

        dialog.base_input.setText(base)
        dialog.head_input.setCurrentText(head)

        # Call internal validation
        dialog._validate_and_accept()

        # Check expected result
        if expected_accepted:
            assert dialog.result() == QDialog.Accepted
        else:
            assert dialog.result() != QDialog.Accepted

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

    def test_dialog_initialization_with_current_branch(self, qtbot):
        """Test dialog initializes with current branch parameter."""
        dialog = CreatePullRequestDialog(current_branch="feature-123")
        qtbot.addWidget(dialog)

        assert dialog.current_branch == "feature-123"
        assert dialog.head_input.currentText() == "feature-123"

    def test_dialog_initialization_with_base_branch(self, qtbot):
        """Test dialog initializes with base branch parameter."""
        dialog = CreatePullRequestDialog(base_branch="develop")
        qtbot.addWidget(dialog)

        assert dialog.base_branch == "develop"
        assert dialog.base_input.text() == "develop"

    def test_dialog_initialization_with_both_branches(self, qtbot):
        """Test dialog initializes with both branch parameters."""
        dialog = CreatePullRequestDialog(
            current_branch="feature-xyz", base_branch="staging"
        )
        qtbot.addWidget(dialog)

        assert dialog.current_branch == "feature-xyz"
        assert dialog.base_branch == "staging"
        assert dialog.head_input.currentText() == "feature-xyz"
        assert dialog.base_input.text() == "staging"

    def test_dialog_modal_setting(self, qtbot):
        """Test dialog is modal."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog.isModal() is True

    def test_dialog_minimum_size(self, qtbot):
        """Test dialog has minimum size."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog.minimumSize().width() >= 500
        assert dialog.minimumSize().height() >= 350

    def test_title_input_placeholder(self, qtbot):
        """Test title input has placeholder text."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog.title_input.placeholderText() != ""
        assert "title" in dialog.title_input.placeholderText().lower()

    def test_title_input_tooltip(self, qtbot):
        """Test title input has tooltip."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog.title_input.toolTip() != ""
        assert "required" in dialog.title_input.toolTip().lower()

    def test_base_input_tooltip(self, qtbot):
        """Test base input has tooltip."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog.base_input.toolTip() != ""

    def test_head_input_tooltip(self, qtbot):
        """Test head input has tooltip."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog.head_input.toolTip() != ""

    def test_body_input_placeholder(self, qtbot):
        """Test body input has placeholder text."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog.body_input.placeholderText() != ""

    def test_body_input_tooltip(self, qtbot):
        """Test body input has tooltip."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog.body_input.toolTip() != ""

    def test_draft_checkbox_tooltip(self, qtbot):
        """Test draft checkbox has tooltip."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog.draft_checkbox.toolTip() != ""
        assert "draft" in dialog.draft_checkbox.toolTip().lower()

    def test_draft_checkbox_default_unchecked(self, qtbot):
        """Test draft checkbox is unchecked by default."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog.draft_checkbox.isChecked() is False

    def test_draft_checkbox_checked_state(self, qtbot):
        """Test draft checkbox checked state in data."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        dialog.title_input.setText("Test PR")
        dialog.draft_checkbox.setChecked(True)

        data = dialog.get_pr_data()
        assert data["draft"] == "true"

    def test_draft_checkbox_unchecked_state(self, qtbot):
        """Test draft checkbox unchecked state in data."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        dialog.title_input.setText("Test PR")
        dialog.draft_checkbox.setChecked(False)

        data = dialog.get_pr_data()
        assert data["draft"] == "false"

    @patch("asciidoc_artisan.ui.github_dialogs.logger")
    def test_validation_whitespace_title(self, mock_logger, qtbot):
        """Test validation rejects title with only whitespace."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        dialog.title_input.setText("   ")
        dialog.base_input.setText("main")
        dialog.head_input.setCurrentText("feature")

        dialog._validate_and_accept()

        assert dialog.result() != QDialog.Accepted
        mock_logger.warning.assert_called_with("PR title is required")

    @patch("asciidoc_artisan.ui.github_dialogs.logger")
    def test_validation_same_branches_logs_warning(self, mock_logger, qtbot):
        """Test validation logs warning when base == head."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        dialog.title_input.setText("Test PR")
        dialog.base_input.setText("main")
        dialog.head_input.setCurrentText("main")

        dialog._validate_and_accept()

        assert dialog.result() != QDialog.Accepted
        mock_logger.warning.assert_called_with(
            "Base and head branches cannot be the same"
        )

    def test_validation_same_branches_shows_error(self, qtbot):
        """Test validation shows error styling when base == head."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        dialog.title_input.setText("Test PR")
        dialog.base_input.setText("main")
        dialog.head_input.setCurrentText("main")

        dialog._validate_and_accept()

        # Verify error styling applied to head_input
        assert "border: 1px solid red" in dialog.head_input.styleSheet()

    def test_validation_whitespace_stripped_in_data(self, qtbot):
        """Test whitespace is stripped from all fields in get_pr_data."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        dialog.title_input.setText("  Test PR  ")
        dialog.body_input.setPlainText("  Test body  ")
        dialog.base_input.setText("  main  ")
        dialog.head_input.setCurrentText("  feature  ")

        data = dialog.get_pr_data()

        assert data["title"] == "Test PR"
        assert data["body"] == "Test body"
        assert data["base"] == "main"
        assert data["head"] == "feature"

    def test_head_input_is_editable(self, qtbot):
        """Test head input combo box is editable."""
        dialog = CreatePullRequestDialog()
        qtbot.addWidget(dialog)

        assert dialog.head_input.isEditable() is True


@pytest.mark.fr_034
@pytest.mark.fr_035
@pytest.mark.fr_036
@pytest.mark.fr_037
@pytest.mark.fr_038
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

    def test_dialog_not_modal(self, qtbot):
        """Test dialog is not modal."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        assert dialog.isModal() is False

    def test_dialog_minimum_size(self, qtbot):
        """Test dialog has minimum size."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        assert dialog.minimumSize().width() >= 700
        assert dialog.minimumSize().height() >= 400

    @pytest.mark.parametrize(
        "state_filter,pr_state,should_show",
        [
            ("Open", "open", True),
            ("Open", "closed", False),
            ("Open", "merged", False),
            ("Closed", "closed", True),
            ("Closed", "open", False),
            ("Closed", "merged", False),
            ("Merged", "merged", True),
            ("Merged", "open", False),
            ("Merged", "closed", False),
            ("All", "open", True),
            ("All", "closed", True),
            ("All", "merged", True),
        ],
    )
    def test_state_filter_behavior(self, qtbot, state_filter, pr_state, should_show):
        """Test state filter shows/hides PRs correctly."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        test_pr = {
            "number": 1,
            "title": "Test PR",
            "author": {"login": "testuser"},
            "state": pr_state,
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/pull/1",
        }

        dialog.set_pr_data([test_pr])
        dialog.state_filter.setCurrentText(state_filter)

        # Should show 1 row if should_show, 0 rows otherwise
        expected_rows = 1 if should_show else 0
        assert dialog.pr_table.rowCount() == expected_rows

    def test_state_filter_default_is_open(self, qtbot):
        """Test default state filter is 'Open'."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        assert dialog.state_filter.currentText() == "Open"

    def test_state_filter_has_all_states(self, qtbot):
        """Test state filter has all expected states."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        states = [
            dialog.state_filter.itemText(i) for i in range(dialog.state_filter.count())
        ]
        assert "Open" in states
        assert "Closed" in states
        assert "Merged" in states
        assert "All" in states

    def test_state_filter_tooltip(self, qtbot):
        """Test state filter has tooltip."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        assert dialog.state_filter.toolTip() != ""
        assert "filter" in dialog.state_filter.toolTip().lower()

    @patch("asciidoc_artisan.ui.github_dialogs.logger")
    def test_filter_changed_logs_debug(self, mock_logger, qtbot):
        """Test filter change logs debug message."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        dialog.state_filter.setCurrentText("Closed")

        mock_logger.debug.assert_called_with("Filter changed to: Closed")

    @patch("asciidoc_artisan.ui.github_dialogs.QDesktopServices.openUrl")
    @patch("asciidoc_artisan.ui.github_dialogs.logger")
    def test_double_click_opens_url(self, mock_logger, mock_open_url, qtbot):
        """Test double-clicking row opens URL in browser."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        test_pr = {
            "number": 42,
            "title": "Test PR",
            "author": {"login": "testuser"},
            "state": "open",
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/pull/42",
        }

        dialog.set_pr_data([test_pr])

        # Simulate double-click on row 0
        index = dialog.pr_table.model().index(0, 0)
        dialog._row_double_clicked(index)

        # Verify URL opened
        mock_open_url.assert_called_once()
        args = mock_open_url.call_args[0]
        assert isinstance(args[0], QUrl)
        assert args[0].toString() == "https://github.com/test/repo/pull/42"

        # Verify logging
        mock_logger.info.assert_called_once()
        assert "Opening pull request in browser" in mock_logger.info.call_args[0][0]

    @patch("asciidoc_artisan.ui.github_dialogs.logger")
    def test_refresh_button_clicked_logs_debug(self, mock_logger, qtbot):
        """Test refresh button click logs debug message."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        # Find and click refresh button
        buttons = dialog.findChildren(QPushButton)
        refresh_btn = next(btn for btn in buttons if "refresh" in btn.text().lower())

        qtbot.mouseClick(refresh_btn, Qt.LeftButton)

        mock_logger.debug.assert_called_with("Refresh clicked")

    @pytest.mark.parametrize(
        "author_data,expected_name",
        [
            ({"login": "user123"}, "user123"),
            ({"login": "alice"}, "alice"),
            ({}, "Unknown"),
            ({"name": "Alice"}, "Unknown"),  # Missing "login" key
            ("stringuser", "stringuser"),
            ("bob", "bob"),
        ],
    )
    def test_author_field_variants(self, qtbot, author_data, expected_name):
        """Test author field handles dict with login, dict without login, and string."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        test_pr = {
            "number": 1,
            "title": "Test PR",
            "author": author_data,
            "state": "open",
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/pull/1",
        }

        dialog.set_pr_data([test_pr])

        # Check author column (column 2)
        author_item = dialog.pr_table.item(0, 2)
        assert author_item.text() == expected_name

    def test_missing_number_field(self, qtbot):
        """Test missing number field defaults to 'N/A'."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        test_pr = {
            "title": "Test PR",
            "author": {"login": "testuser"},
            "state": "open",
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/pull/1",
        }

        dialog.set_pr_data([test_pr])

        number_item = dialog.pr_table.item(0, 0)
        assert number_item.text() == "#N/A"

    def test_missing_title_field(self, qtbot):
        """Test missing title field defaults to 'Untitled'."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        test_pr = {
            "number": 1,
            "author": {"login": "testuser"},
            "state": "open",
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/pull/1",
        }

        dialog.set_pr_data([test_pr])

        title_item = dialog.pr_table.item(0, 1)
        assert title_item.text() == "Untitled"

    def test_missing_state_field(self, qtbot):
        """Test missing state field defaults to 'unknown'."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        test_pr = {
            "number": 1,
            "title": "Test PR",
            "author": {"login": "testuser"},
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/pull/1",
        }

        # Set filter to "All" so PR shows up even without state field
        dialog.state_filter.setCurrentText("All")
        dialog.set_pr_data([test_pr])

        status_item = dialog.pr_table.item(0, 3)
        assert status_item.text() == "Unknown"

    def test_missing_created_at_field(self, qtbot):
        """Test missing createdAt field defaults to 'Unknown'."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        test_pr = {
            "number": 1,
            "title": "Test PR",
            "author": {"login": "testuser"},
            "state": "open",
            "url": "https://github.com/test/repo/pull/1",
        }

        dialog.set_pr_data([test_pr])

        created_item = dialog.pr_table.item(0, 4)
        assert created_item.text() == "Unknown"

    def test_missing_url_field(self, qtbot):
        """Test missing url field defaults to empty string."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        test_pr = {
            "number": 1,
            "title": "Test PR",
            "author": {"login": "testuser"},
            "state": "open",
            "createdAt": "2025-10-01",
        }

        dialog.set_pr_data([test_pr])

        url_item = dialog.pr_table.item(0, 5)
        assert url_item.text() == ""

    def test_table_column_count(self, qtbot):
        """Test table has correct number of columns."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        assert dialog.pr_table.columnCount() == 6

    def test_table_column_headers(self, qtbot):
        """Test table has correct column headers."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        expected_headers = ["Number", "Title", "Author", "Status", "Created", "URL"]
        for i, header in enumerate(expected_headers):
            assert dialog.pr_table.horizontalHeaderItem(i).text() == header

    def test_table_tooltip(self, qtbot):
        """Test table has tooltip."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        assert dialog.pr_table.toolTip() != ""
        assert "double-click" in dialog.pr_table.toolTip().lower()

    def test_backward_compatibility_pr_table_property(self, qtbot):
        """Test pr_table property returns table widget."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        assert dialog.pr_table is dialog.table
        assert dialog.pr_table is not None

    def test_empty_state_table_span(self, qtbot):
        """Test empty state message spans all columns."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        dialog.set_pr_data([])

        # Verify span covers all 6 columns
        assert dialog.pr_table.rowSpan(0, 0) == 1
        assert dialog.pr_table.columnSpan(0, 0) == 6

    def test_empty_state_centered(self, qtbot):
        """Test empty state message is centered."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        dialog.set_pr_data([])

        item = dialog.pr_table.item(0, 0)
        assert item.textAlignment() == Qt.AlignCenter

    def test_get_data_attribute_name(self, qtbot):
        """Test _get_data_attribute_name returns correct attribute name."""
        dialog = PullRequestListDialog()
        qtbot.addWidget(dialog)

        assert dialog._get_data_attribute_name() == "pr_data"


@pytest.mark.fr_034
@pytest.mark.fr_035
@pytest.mark.fr_036
@pytest.mark.fr_037
@pytest.mark.fr_038
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

    @pytest.mark.parametrize(
        "title,expected_accepted,test_id",
        [
            ("", False, "empty_title"),
            ("Test Issue Title", True, "valid_input"),
        ],
    )
    def test_dialog_validation(self, qtbot, title, expected_accepted, test_id):
        """Test dialog validation with various inputs.

        Parametrized test covering:
        - Empty title (rejected)
        - Valid input (accepted)
        """
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        # Set input value
        if title:
            dialog.title_input.setText(title)
        else:
            dialog.title_input.clear()

        # Call internal validation
        dialog._validate_and_accept()

        # Check expected result
        if expected_accepted:
            assert dialog.result() == QDialog.Accepted
        else:
            assert dialog.result() != QDialog.Accepted

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

    def test_dialog_modal_setting(self, qtbot):
        """Test dialog is modal."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        assert dialog.isModal() is True

    def test_dialog_minimum_size(self, qtbot):
        """Test dialog has minimum size."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        assert dialog.minimumSize().width() >= 500
        assert dialog.minimumSize().height() >= 350

    def test_title_input_placeholder(self, qtbot):
        """Test title input has placeholder text."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        assert dialog.title_input.placeholderText() != ""
        assert "title" in dialog.title_input.placeholderText().lower()

    def test_title_input_tooltip(self, qtbot):
        """Test title input has tooltip."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        assert dialog.title_input.toolTip() != ""
        assert "required" in dialog.title_input.toolTip().lower()

    def test_labels_input_placeholder(self, qtbot):
        """Test labels input has placeholder text."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        assert dialog.labels_input.placeholderText() != ""

    def test_labels_input_tooltip(self, qtbot):
        """Test labels input has tooltip."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        assert dialog.labels_input.toolTip() != ""
        assert "label" in dialog.labels_input.toolTip().lower()

    def test_body_input_placeholder(self, qtbot):
        """Test body input has placeholder text."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        assert dialog.body_input.placeholderText() != ""

    def test_body_input_tooltip(self, qtbot):
        """Test body input has tooltip."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        assert dialog.body_input.toolTip() != ""

    @patch("asciidoc_artisan.ui.github_dialogs.logger")
    def test_validation_whitespace_title(self, mock_logger, qtbot):
        """Test validation rejects title with only whitespace."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        dialog.title_input.setText("   ")

        dialog._validate_and_accept()

        assert dialog.result() != QDialog.Accepted
        mock_logger.warning.assert_called_with("Issue title is required")

    def test_validation_whitespace_stripped_in_data(self, qtbot):
        """Test whitespace is stripped from all fields in get_issue_data."""
        dialog = CreateIssueDialog()
        qtbot.addWidget(dialog)

        dialog.title_input.setText("  Test Issue  ")
        dialog.body_input.setPlainText("  Test body  ")
        dialog.labels_input.setText("  bug, feature  ")

        data = dialog.get_issue_data()

        assert data["title"] == "Test Issue"
        assert data["body"] == "Test body"
        assert data["labels"] == "bug, feature"


@pytest.mark.fr_034
@pytest.mark.fr_035
@pytest.mark.fr_036
@pytest.mark.fr_037
@pytest.mark.fr_038
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

    def test_dialog_not_modal(self, qtbot):
        """Test dialog is not modal."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        assert dialog.isModal() is False

    def test_dialog_minimum_size(self, qtbot):
        """Test dialog has minimum size."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        assert dialog.minimumSize().width() >= 700
        assert dialog.minimumSize().height() >= 400

    @pytest.mark.parametrize(
        "state_filter,issue_state,should_show",
        [
            ("Open", "open", True),
            ("Open", "closed", False),
            ("Closed", "closed", True),
            ("Closed", "open", False),
            ("All", "open", True),
            ("All", "closed", True),
        ],
    )
    def test_state_filter_behavior(self, qtbot, state_filter, issue_state, should_show):
        """Test state filter shows/hides issues correctly."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        test_issue = {
            "number": 1,
            "title": "Test Issue",
            "author": {"login": "testuser"},
            "state": issue_state,
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/issues/1",
        }

        dialog.set_issue_data([test_issue])
        dialog.state_filter.setCurrentText(state_filter)

        # Should show 1 row if should_show, 0 rows otherwise
        expected_rows = 1 if should_show else 0
        assert dialog.issue_table.rowCount() == expected_rows

    def test_state_filter_default_is_open(self, qtbot):
        """Test default state filter is 'Open'."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        assert dialog.state_filter.currentText() == "Open"

    def test_state_filter_has_all_states(self, qtbot):
        """Test state filter has all expected states."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        states = [
            dialog.state_filter.itemText(i) for i in range(dialog.state_filter.count())
        ]
        assert "Open" in states
        assert "Closed" in states
        assert "All" in states

    def test_state_filter_tooltip(self, qtbot):
        """Test state filter has tooltip."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        assert dialog.state_filter.toolTip() != ""
        assert "filter" in dialog.state_filter.toolTip().lower()

    @patch("asciidoc_artisan.ui.github_dialogs.logger")
    def test_filter_changed_logs_debug(self, mock_logger, qtbot):
        """Test filter change logs debug message."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        dialog.state_filter.setCurrentText("Closed")

        mock_logger.debug.assert_called_with("Filter changed to: Closed")

    @patch("asciidoc_artisan.ui.github_dialogs.QDesktopServices.openUrl")
    @patch("asciidoc_artisan.ui.github_dialogs.logger")
    def test_double_click_opens_url(self, mock_logger, mock_open_url, qtbot):
        """Test double-clicking row opens URL in browser."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        test_issue = {
            "number": 15,
            "title": "Test Issue",
            "author": {"login": "testuser"},
            "state": "open",
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/issues/15",
        }

        dialog.set_issue_data([test_issue])

        # Simulate double-click on row 0
        index = dialog.issue_table.model().index(0, 0)
        dialog._row_double_clicked(index)

        # Verify URL opened
        mock_open_url.assert_called_once()
        args = mock_open_url.call_args[0]
        assert isinstance(args[0], QUrl)
        assert args[0].toString() == "https://github.com/test/repo/issues/15"

        # Verify logging
        mock_logger.info.assert_called_once()
        assert "Opening issue in browser" in mock_logger.info.call_args[0][0]

    @patch("asciidoc_artisan.ui.github_dialogs.logger")
    def test_refresh_button_clicked_logs_debug(self, mock_logger, qtbot):
        """Test refresh button click logs debug message."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        # Find and click refresh button
        buttons = dialog.findChildren(QPushButton)
        refresh_btn = next(btn for btn in buttons if "refresh" in btn.text().lower())

        qtbot.mouseClick(refresh_btn, Qt.LeftButton)

        mock_logger.debug.assert_called_with("Refresh clicked")

    @pytest.mark.parametrize(
        "author_data,expected_name",
        [
            ({"login": "user123"}, "user123"),
            ({"login": "alice"}, "alice"),
            ({}, "Unknown"),
            ({"name": "Alice"}, "Unknown"),  # Missing "login" key
            ("stringuser", "stringuser"),
            ("bob", "bob"),
        ],
    )
    def test_author_field_variants(self, qtbot, author_data, expected_name):
        """Test author field handles dict with login, dict without login, and string."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        test_issue = {
            "number": 1,
            "title": "Test Issue",
            "author": author_data,
            "state": "open",
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/issues/1",
        }

        dialog.set_issue_data([test_issue])

        # Check author column (column 2)
        author_item = dialog.issue_table.item(0, 2)
        assert author_item.text() == expected_name

    def test_missing_number_field(self, qtbot):
        """Test missing number field defaults to 'N/A'."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        test_issue = {
            "title": "Test Issue",
            "author": {"login": "testuser"},
            "state": "open",
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/issues/1",
        }

        dialog.set_issue_data([test_issue])

        number_item = dialog.issue_table.item(0, 0)
        assert number_item.text() == "#N/A"

    def test_missing_title_field(self, qtbot):
        """Test missing title field defaults to 'Untitled'."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        test_issue = {
            "number": 1,
            "author": {"login": "testuser"},
            "state": "open",
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/issues/1",
        }

        dialog.set_issue_data([test_issue])

        title_item = dialog.issue_table.item(0, 1)
        assert title_item.text() == "Untitled"

    def test_missing_state_field(self, qtbot):
        """Test missing state field defaults to 'unknown'."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        test_issue = {
            "number": 1,
            "title": "Test Issue",
            "author": {"login": "testuser"},
            "createdAt": "2025-10-01",
            "url": "https://github.com/test/repo/issues/1",
        }

        # Set filter to "All" so issue shows up even without state field
        dialog.state_filter.setCurrentText("All")
        dialog.set_issue_data([test_issue])

        status_item = dialog.issue_table.item(0, 3)
        assert status_item.text() == "Unknown"

    def test_missing_created_at_field(self, qtbot):
        """Test missing createdAt field defaults to 'Unknown'."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        test_issue = {
            "number": 1,
            "title": "Test Issue",
            "author": {"login": "testuser"},
            "state": "open",
            "url": "https://github.com/test/repo/issues/1",
        }

        dialog.set_issue_data([test_issue])

        created_item = dialog.issue_table.item(0, 4)
        assert created_item.text() == "Unknown"

    def test_missing_url_field(self, qtbot):
        """Test missing url field defaults to empty string."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        test_issue = {
            "number": 1,
            "title": "Test Issue",
            "author": {"login": "testuser"},
            "state": "open",
            "createdAt": "2025-10-01",
        }

        dialog.set_issue_data([test_issue])

        url_item = dialog.issue_table.item(0, 5)
        assert url_item.text() == ""

    def test_table_column_count(self, qtbot):
        """Test table has correct number of columns."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        assert dialog.issue_table.columnCount() == 6

    def test_table_column_headers(self, qtbot):
        """Test table has correct column headers."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        expected_headers = ["Number", "Title", "Author", "Status", "Created", "URL"]
        for i, header in enumerate(expected_headers):
            assert dialog.issue_table.horizontalHeaderItem(i).text() == header

    def test_table_tooltip(self, qtbot):
        """Test table has tooltip."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        assert dialog.issue_table.toolTip() != ""
        assert "double-click" in dialog.issue_table.toolTip().lower()

    def test_backward_compatibility_issue_table_property(self, qtbot):
        """Test issue_table property returns table widget."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        assert dialog.issue_table is dialog.table
        assert dialog.issue_table is not None

    def test_empty_state_table_span(self, qtbot):
        """Test empty state message spans all columns."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        dialog.set_issue_data([])

        # Verify span covers all 6 columns
        assert dialog.issue_table.rowSpan(0, 0) == 1
        assert dialog.issue_table.columnSpan(0, 0) == 6

    def test_empty_state_centered(self, qtbot):
        """Test empty state message is centered."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        dialog.set_issue_data([])

        item = dialog.issue_table.item(0, 0)
        assert item.textAlignment() == Qt.AlignCenter

    def test_get_data_attribute_name(self, qtbot):
        """Test _get_data_attribute_name returns correct attribute name."""
        dialog = IssueListDialog()
        qtbot.addWidget(dialog)

        assert dialog._get_data_attribute_name() == "issue_data"


@pytest.mark.fr_034
@pytest.mark.fr_035
@pytest.mark.fr_036
@pytest.mark.fr_037
@pytest.mark.fr_038
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
