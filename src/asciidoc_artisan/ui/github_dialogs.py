"""
===============================================================================
GITHUB DIALOGS - Pop-ups for Pull Requests and Issues
===============================================================================

FILE PURPOSE:
This file creates dialog windows for GitHub operations. When you click
Git → GitHub → Create Pull Request, these dialogs appear.

WHAT THIS FILE CONTAINS:
1. Validation Helper Functions: Reusable code for form validation
2. BaseListDialog: Base class for PR/Issue list views (Template Method Pattern)
3. CreatePullRequestDialog: Form to create a new pull request
4. PullRequestListDialog: Table showing all pull requests
5. CreateIssueDialog: Form to create a new issue
6. IssueListDialog: Table showing all issues

FOR BEGINNERS - WHAT IS GITHUB INTEGRATION?:
GitHub is a website where developers store code and collaborate. This file
lets you manage GitHub features without leaving the editor:
- Create Pull Requests (PRs): Propose code changes
- List PRs: See all pending code reviews
- Create Issues: Report bugs or request features
- List Issues: See all open bugs/feature requests

WHY SEPARATE DIALOGS?:
Each dialog has ONE job (Single Responsibility Principle):
- Create dialogs: Collect user input (title, description, etc.)
- List dialogs: Show data in a table (with filtering and refresh)

DESIGN PATTERN USED:
"Template Method Pattern" - BaseListDialog defines the structure, subclasses
fill in the details. Both PR and Issue lists work the same way, but show
different data. The base class handles common stuff (table, refresh, filtering).

VALIDATION PATTERN:
All input validation uses helper functions to avoid duplication:
- _show_validation_error(): Shows red border on invalid field
- _clear_validation_error(): Removes red border when fixed
- _validate_required_text(): Checks if field is not empty

IMPLEMENTS SPECIFICATIONS:
FR-054 to FR-060 (GitHub CLI Integration features)
See SPECIFICATIONS.md for complete feature list.

USAGE EXAMPLE:
    # Create a pull request
    dialog = CreatePullRequestDialog(current_branch="my-feature")
    if dialog.exec():  # User clicked OK (not Cancel)
        pr_data = dialog.get_pr_data()  # Get form data
        # Send to GitHub CLI worker to actually create the PR
"""

import logging  # For recording events (validation errors, etc.)
from typing import Any, Dict, List, Optional  # Type hints for better code quality

# Qt imports for GUI
from PySide6.QtCore import Qt, QUrl  # Qt constants and URL class
from PySide6.QtGui import QDesktopServices  # For opening URLs in browser
from PySide6.QtWidgets import (
    QCheckBox,  # Checkbox widget (on/off)
    QComboBox,  # Dropdown menu
    QDialog,  # Base class for pop-up windows
    QDialogButtonBox,  # Standard OK/Cancel buttons
    QFormLayout,  # Layout for forms (label: input)
    QHBoxLayout,  # Horizontal layout
    QHeaderView,  # Table header (column titles)
    QLabel,  # Text label
    QLineEdit,  # Single-line text input
    QPlainTextEdit,  # Multi-line text input
    QPushButton,  # Clickable button
    QTableWidget,  # Table with rows and columns
    QTableWidgetItem,  # Single cell in a table
    QVBoxLayout,  # Vertical layout
    QWidget,  # Base class for all UI widgets
)

logger = logging.getLogger(__name__)  # Logger for this file


# === VALIDATION HELPER FUNCTIONS ===
# These functions are reused by all dialogs to validate user input
# Following DRY principle: "Don't Repeat Yourself"


def _show_validation_error(widget: QWidget, widget_type: str) -> None:
    """
    Show Validation Error - Make Widget Border Red.

    WHY THIS EXISTS:
    When user enters invalid data (e.g., empty required field), we need to
    show them what's wrong. A red border is the standard way to indicate errors.

    WHAT IT DOES:
    1. Apply red border CSS style to the widget
    2. Move keyboard focus to the widget (cursor appears there)

    HOW IT WORKS:
    We use Qt's CSS styling system. Each widget type (QLineEdit, QComboBox)
    needs its CSS class name in the style string.

    PARAMETERS:
        widget: The input widget with invalid data (will get red border)
        widget_type: CSS class name ("QLineEdit", "QComboBox", etc.)

    EXAMPLE:
        _show_validation_error(title_input, "QLineEdit")
        # Result: title_input now has red border and keyboard focus
    """
    # Apply CSS style - red 1px border around the widget
    widget.setStyleSheet(f"{widget_type} {{ border: 1px solid red; }}")

    # Move keyboard focus to this widget so user knows where to fix the error
    widget.setFocus()


def _clear_validation_error(widget: QWidget) -> None:
    """
    Clear Validation Error - Remove Red Border.

    WHY THIS EXISTS:
    After user fixes the error, we need to remove the red border.
    Otherwise, it stays red even after fixing!

    WHAT IT DOES:
    Remove all custom CSS styling from the widget (returns to default look)

    PARAMETERS:
        widget: The input widget to clear styling from

    EXAMPLE:
        _clear_validation_error(title_input)
        # Result: title_input returns to normal appearance
    """
    # Empty string = remove all custom styles, use default
    widget.setStyleSheet("")


def _validate_required_text(widget: QLineEdit, field_name: str) -> bool:
    """
    Validate Required Text Field - Check If Not Empty.

    WHY THIS EXISTS:
    Many fields are required (e.g., PR title, Issue title). This function
    checks if user entered something, and shows an error if they didn't.

    WHAT IT DOES:
    1. Get text from the widget
    2. Strip whitespace (remove spaces from beginning/end)
    3. If empty: Show red border + log warning, return False
    4. If not empty: Clear red border, return True

    WHY .strip()?:
    "   " (just spaces) should count as empty. .strip() removes leading/trailing
    whitespace, so "   " becomes "" (empty string).

    PARAMETERS:
        widget: QLineEdit to check (text input box)
        field_name: Name of field for logging ("PR title", "Issue title", etc.)

    RETURNS:
        True if field has text (valid)
        False if field is empty (invalid)

    USAGE PATTERN:
        if not _validate_required_text(self.title_input, "PR title"):
            return  # Don't submit form, user needs to fix error

    TECHNICAL NOTE:
    This follows the "validation guard" pattern - check for errors first,
    return early if found. This avoids deep nesting (if valid: if valid: if valid:)
    """
    # Get text from input and remove leading/trailing spaces
    text = widget.text().strip()

    # Check if empty
    if not text:
        # Empty! Show error and return False
        _show_validation_error(widget, "QLineEdit")
        logger.warning(f"{field_name} is required")
        return False  # Validation failed

    # Not empty! Clear any previous error and return True
    _clear_validation_error(widget)
    return True  # Validation passed


class BaseListDialog(QDialog):
    """
    Base class for GitHub list dialogs (PRs and Issues).

    Provides common functionality:
    - Table widget with filtering
    - Refresh button
    - Double-click to open in browser
    - State filter dropdown

    Subclasses must implement:
    - _get_window_title() -> str
    - _get_filter_states() -> List[str]
    - _get_data_attribute_name() -> str
    - _get_tooltip_prefix() -> str
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        data: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Initialize base list dialog."""
        super().__init__(parent)
        self._data = data or []
        self._init_ui()
        self._populate_table()

    def _get_window_title(self) -> str:
        """Get window title. Subclasses must override."""
        raise NotImplementedError

    def _get_filter_states(self) -> List[str]:
        """Get filter state options. Subclasses must override."""
        raise NotImplementedError

    def _get_data_attribute_name(self) -> str:
        """Get data attribute name. Subclasses must override."""
        raise NotImplementedError

    def _get_tooltip_prefix(self) -> str:
        """Get tooltip prefix (e.g., 'pull requests', 'issues'). Subclasses must override."""
        raise NotImplementedError

    def _init_ui(self) -> None:
        """Initialize the list dialog UI."""
        self.setWindowTitle(self._get_window_title())
        self.setMinimumSize(700, 400)
        self.setModal(False)

        layout = QVBoxLayout(self)

        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("State:"))

        self.state_filter = QComboBox()
        self.state_filter.addItems(self._get_filter_states())
        self.state_filter.setCurrentText(self._get_filter_states()[0])
        self.state_filter.setToolTip(f"Filter {self._get_tooltip_prefix()} by state")
        self.state_filter.currentTextChanged.connect(self._filter_changed)
        filter_layout.addWidget(self.state_filter)

        filter_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setToolTip(f"Reload {self._get_tooltip_prefix()} from GitHub")
        refresh_btn.clicked.connect(self._refresh_clicked)
        filter_layout.addWidget(refresh_btn)

        layout.addLayout(filter_layout)

        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Number", "Title", "Author", "Status", "Created", "URL"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self._row_double_clicked)
        self.table.setToolTip(
            f"Double-click to open {self._get_tooltip_prefix()[:-1]} in browser"
        )

        # Configure column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Number
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Title
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Author
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Created
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # URL

        layout.addWidget(self.table)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)

    def _populate_table(self) -> None:
        """Populate table with current data. Subclasses can override."""
        raise NotImplementedError

    def _filter_changed(self, state: str) -> None:
        """Handle filter state change. Subclasses can override."""
        logger.debug(f"Filter changed to: {state}")
        self._populate_table()

    def _refresh_clicked(self) -> None:
        """Handle refresh button click. Subclasses can override."""
        logger.debug("Refresh clicked")
        # Emit signal or trigger refresh logic
        # Subclasses should override or connect to handler

    def _row_double_clicked(self, index: Any) -> None:
        """Handle row double-click to open in browser. Subclasses can override."""
        row = index.row()
        url_item = self.table.item(row, 5)  # URL column
        if url_item:
            url = url_item.text()
            QDesktopServices.openUrl(QUrl(url))
            logger.info(f"Opening {self._get_tooltip_prefix()[:-1]} in browser: {url}")


class CreatePullRequestDialog(QDialog):
    """
    Dialog for creating a new GitHub pull request.

    Allows users to:
    - Enter PR title (required)
    - Write PR body/description (optional)
    - Select base branch (default: main)
    - Select head branch (current branch pre-selected)
    - Mark PR as draft

    Args:
        parent: Parent QWidget (optional)
        current_branch: Current Git branch to use as head (default)
        base_branch: Default base branch (default: "main")

    Example:
        ```python
        dialog = CreatePullRequestDialog(current_branch="feature-x")
        if dialog.exec():
            pr_data = dialog.get_pr_data()
            # pr_data = {"title": "...", "body": "...", ...}
        ```
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        current_branch: str = "",
        base_branch: str = "main",
    ) -> None:
        """Initialize create pull request dialog."""
        super().__init__(parent)
        self.current_branch = current_branch
        self.base_branch = base_branch
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the create pull request UI."""
        self.setWindowTitle("Create Pull Request")
        self.setMinimumSize(500, 350)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Form layout for input fields
        form_layout = QFormLayout()

        # Title field (required)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter a descriptive title for your PR")
        self.title_input.setToolTip("PR title (required)")
        form_layout.addRow("Title:*", self.title_input)

        # Base branch field
        self.base_input = QLineEdit(self.base_branch)
        self.base_input.setToolTip(
            "Target branch for merging (usually 'main' or 'master')"
        )
        form_layout.addRow("Base branch:", self.base_input)

        # Head branch field (current branch)
        self.head_input = QComboBox()
        self.head_input.setEditable(True)
        if self.current_branch:
            self.head_input.addItem(self.current_branch)
            self.head_input.setCurrentText(self.current_branch)
        self.head_input.setToolTip("Source branch containing your changes")
        form_layout.addRow("Head branch:", self.head_input)

        layout.addLayout(form_layout)

        # Body field (optional)
        body_label = QLabel("Description:")
        body_label.setToolTip("Detailed description of your changes (optional)")
        layout.addWidget(body_label)

        self.body_input = QPlainTextEdit()
        self.body_input.setPlaceholderText(
            "Describe your changes...\n\n"
            "What does this PR do?\n"
            "Why is this change needed?\n"
            "How has this been tested?"
        )
        self.body_input.setMinimumHeight(150)
        self.body_input.setToolTip("Detailed PR description (optional)")
        layout.addWidget(self.body_input)

        # Draft PR checkbox
        self.draft_checkbox = QCheckBox("Create as draft PR")
        self.draft_checkbox.setToolTip(
            "Draft PRs can't be merged until marked as ready for review"
        )
        layout.addWidget(self.draft_checkbox)

        # Required field note
        required_label = QLabel("* Required field")
        required_label.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        layout.addWidget(required_label)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Create PR")
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _validate_and_accept(self) -> None:
        """Validate inputs and accept dialog if valid."""
        # Validate title is not empty
        if not _validate_required_text(self.title_input, "PR title"):
            return

        # Validate base != head
        base = self.base_input.text().strip()
        head = self.head_input.currentText().strip()
        if base == head:
            _show_validation_error(self.head_input, "QComboBox")
            logger.warning("Base and head branches cannot be the same")
            return

        _clear_validation_error(self.head_input)
        self.accept()

    def get_pr_data(self) -> Dict[str, str]:
        """
        Get PR data from dialog inputs.

        Returns:
            Dictionary with PR data:
                - title: PR title (required)
                - body: PR description (optional)
                - base: Target branch
                - head: Source branch
                - draft: "true" or "false"
        """
        return {
            "title": self.title_input.text().strip(),
            "body": self.body_input.toPlainText().strip(),
            "base": self.base_input.text().strip(),
            "head": self.head_input.currentText().strip(),
            "draft": "true" if self.draft_checkbox.isChecked() else "false",
        }


class PullRequestListDialog(BaseListDialog):
    """
    Dialog for browsing and managing pull requests.

    Displays a table of pull requests with:
    - PR number and title
    - Author
    - Status (Open/Closed/Merged)
    - Creation date
    - URL

    Features:
    - Filter by state (Open/Closed/Merged/All)
    - Refresh button to reload data
    - Double-click to open PR in browser
    - Copy URL to clipboard

    Args:
        parent: Parent QWidget (optional)
        pr_data: List of PR dictionaries (optional)

    Example:
        ```python
        dialog = PullRequestListDialog(pr_data=prs)
        dialog.exec()
        ```
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        pr_data: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Initialize pull request list dialog."""
        self.pr_data = pr_data or []
        super().__init__(parent, data=pr_data)

    def _get_window_title(self) -> str:
        """Get window title."""
        return "Pull Requests"

    def _get_filter_states(self) -> List[str]:
        """Get filter state options."""
        return ["Open", "Closed", "Merged", "All"]

    def _get_data_attribute_name(self) -> str:
        """Get data attribute name."""
        return "pr_data"

    def _get_tooltip_prefix(self) -> str:
        """Get tooltip prefix."""
        return "pull requests"

    @property
    def pr_table(self) -> Any:
        """Backward compatibility alias for table attribute."""
        return self.table

    def _populate_table(self) -> None:
        """Populate the PR table with current data."""
        self.table.setRowCount(0)

        if not self.pr_data:
            # Show "no data" message
            self.table.setRowCount(1)
            item = QTableWidgetItem("No pull requests found")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setSpan(0, 0, 1, 6)
            self.table.setItem(0, 0, item)
            return

        # Filter by selected state
        state_filter = self.state_filter.currentText().lower()
        filtered_prs = [
            pr
            for pr in self.pr_data
            if state_filter == "all" or pr.get("state", "").lower() == state_filter
        ]

        self.table.setRowCount(len(filtered_prs))

        for row, pr in enumerate(filtered_prs):
            # PR Number
            number_item = QTableWidgetItem(f"#{pr.get('number', 'N/A')}")
            self.table.setItem(row, 0, number_item)

            # Title
            title_item = QTableWidgetItem(pr.get("title", "Untitled"))
            self.table.setItem(row, 1, title_item)

            # Author
            author = pr.get("author", {})
            author_name = (
                author.get("login", "Unknown")
                if isinstance(author, dict)
                else str(author)
            )
            author_item = QTableWidgetItem(author_name)
            self.table.setItem(row, 2, author_item)

            # Status
            status = pr.get("state", "unknown").capitalize()
            status_item = QTableWidgetItem(status)
            self.table.setItem(row, 3, status_item)

            # Created date
            created = pr.get("createdAt", "Unknown")
            created_item = QTableWidgetItem(created)
            self.table.setItem(row, 4, created_item)

            # URL
            url = pr.get("url", "")
            url_item = QTableWidgetItem(url)
            self.table.setItem(row, 5, url_item)

    def set_pr_data(self, pr_data: List[Dict[str, Any]]) -> None:
        """
        Update PR data and refresh table.

        Args:
            pr_data: List of PR dictionaries
        """
        self.pr_data = pr_data
        self._data = pr_data
        self._populate_table()


class CreateIssueDialog(QDialog):
    """
    Dialog for creating a new GitHub issue.

    Allows users to:
    - Enter issue title (required)
    - Write issue body/description (optional)
    - Add labels (comma-separated, optional)

    Args:
        parent: Parent QWidget (optional)

    Example:
        ```python
        dialog = CreateIssueDialog()
        if dialog.exec():
            issue_data = dialog.get_issue_data()
            # issue_data = {"title": "...", "body": "...", "labels": "..."}
        ```
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize create issue dialog."""
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the create issue UI."""
        self.setWindowTitle("Create Issue")
        self.setMinimumSize(500, 350)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Form layout for input fields
        form_layout = QFormLayout()

        # Title field (required)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter a brief, descriptive title")
        self.title_input.setToolTip("Issue title (required)")
        form_layout.addRow("Title:*", self.title_input)

        # Labels field (optional)
        self.labels_input = QLineEdit()
        self.labels_input.setPlaceholderText("bug, enhancement, documentation")
        self.labels_input.setToolTip(
            "Comma-separated labels (optional)\n"
            "Common labels: bug, enhancement, documentation, question"
        )
        form_layout.addRow("Labels:", self.labels_input)

        layout.addLayout(form_layout)

        # Body field (optional)
        body_label = QLabel("Description:")
        body_label.setToolTip("Detailed description of the issue (optional)")
        layout.addWidget(body_label)

        self.body_input = QPlainTextEdit()
        self.body_input.setPlaceholderText(
            "Describe the issue...\n\n"
            "What is the problem?\n"
            "What is the expected behavior?\n"
            "Steps to reproduce (if bug):\n"
            "1. \n"
            "2. \n"
            "3. "
        )
        self.body_input.setMinimumHeight(150)
        self.body_input.setToolTip("Detailed issue description (optional)")
        layout.addWidget(self.body_input)

        # Required field note
        required_label = QLabel("* Required field")
        required_label.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        layout.addWidget(required_label)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Create Issue")
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _validate_and_accept(self) -> None:
        """Validate inputs and accept dialog if valid."""
        # Validate title is not empty
        if not _validate_required_text(self.title_input, "Issue title"):
            return

        self.accept()

    def get_issue_data(self) -> Dict[str, str]:
        """
        Get issue data from dialog inputs.

        Returns:
            Dictionary with issue data:
                - title: Issue title (required)
                - body: Issue description (optional)
                - labels: Comma-separated labels (optional)
        """
        return {
            "title": self.title_input.text().strip(),
            "body": self.body_input.toPlainText().strip(),
            "labels": self.labels_input.text().strip(),
        }


class IssueListDialog(BaseListDialog):
    """
    Dialog for browsing and managing issues.

    Displays a table of issues with:
    - Issue number and title
    - Author
    - Status (Open/Closed)
    - Creation date
    - URL

    Features:
    - Filter by state (Open/Closed/All)
    - Refresh button to reload data
    - Double-click to open issue in browser
    - Copy URL to clipboard

    Args:
        parent: Parent QWidget (optional)
        issue_data: List of issue dictionaries (optional)

    Example:
        ```python
        dialog = IssueListDialog(issue_data=issues)
        dialog.exec()
        ```
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        issue_data: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Initialize issue list dialog."""
        self.issue_data = issue_data or []
        super().__init__(parent, data=issue_data)

    def _get_window_title(self) -> str:
        """Get window title."""
        return "Issues"

    def _get_filter_states(self) -> List[str]:
        """Get filter state options."""
        return ["Open", "Closed", "All"]

    def _get_data_attribute_name(self) -> str:
        """Get data attribute name."""
        return "issue_data"

    def _get_tooltip_prefix(self) -> str:
        """Get tooltip prefix."""
        return "issues"

    @property
    def issue_table(self) -> Any:
        """Backward compatibility alias for table attribute."""
        return self.table

    def _populate_table(self) -> None:
        """Populate the issue table with current data."""
        self.table.setRowCount(0)

        if not self.issue_data:
            # Show "no data" message
            self.table.setRowCount(1)
            item = QTableWidgetItem("No issues found")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setSpan(0, 0, 1, 6)
            self.table.setItem(0, 0, item)
            return

        # Filter by selected state
        state_filter = self.state_filter.currentText().lower()
        filtered_issues = [
            issue
            for issue in self.issue_data
            if state_filter == "all" or issue.get("state", "").lower() == state_filter
        ]

        self.table.setRowCount(len(filtered_issues))

        for row, issue in enumerate(filtered_issues):
            # Issue Number
            number_item = QTableWidgetItem(f"#{issue.get('number', 'N/A')}")
            self.table.setItem(row, 0, number_item)

            # Title
            title_item = QTableWidgetItem(issue.get("title", "Untitled"))
            self.table.setItem(row, 1, title_item)

            # Author
            author = issue.get("author", {})
            author_name = (
                author.get("login", "Unknown")
                if isinstance(author, dict)
                else str(author)
            )
            author_item = QTableWidgetItem(author_name)
            self.table.setItem(row, 2, author_item)

            # Status
            status = issue.get("state", "unknown").capitalize()
            status_item = QTableWidgetItem(status)
            self.table.setItem(row, 3, status_item)

            # Created date
            created = issue.get("createdAt", "Unknown")
            created_item = QTableWidgetItem(created)
            self.table.setItem(row, 4, created_item)

            # URL
            url = issue.get("url", "")
            url_item = QTableWidgetItem(url)
            self.table.setItem(row, 5, url_item)

    def set_issue_data(self, issue_data: List[Dict[str, Any]]) -> None:
        """
        Update issue data and refresh table.

        Args:
            issue_data: List of issue dictionaries
        """
        self.issue_data = issue_data
        self._data = issue_data
        self._populate_table()
