"""
GitHub UI Dialogs - Pull Request and Issue management dialogs.

This module contains QDialog subclasses for GitHub CLI integration:
- CreatePullRequestDialog: Create new pull requests
- PullRequestListDialog: Browse and manage pull requests
- CreateIssueDialog: Create new issues
- IssueListDialog: Browse and manage issues

Implements FR-054 to FR-060: GitHub CLI integration features.

Usage Example:
    ```python
    from asciidoc_artisan.ui.github_dialogs import CreatePullRequestDialog

    dialog = CreatePullRequestDialog(current_branch="feature-x")
    if dialog.exec():
        pr_data = dialog.get_pr_data()
        # Create PR with pr_data
    ```
"""

import logging
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


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
        title = self.title_input.text().strip()
        if not title:
            # Show error in title field
            self.title_input.setStyleSheet("QLineEdit { border: 1px solid red; }")
            self.title_input.setFocus()
            logger.warning("PR title is required")
            return

        # Clear error styling
        self.title_input.setStyleSheet("")

        # Validate base != head
        base = self.base_input.text().strip()
        head = self.head_input.currentText().strip()
        if base == head:
            self.head_input.setStyleSheet("QComboBox { border: 1px solid red; }")
            logger.warning("Base and head branches cannot be the same")
            return

        self.head_input.setStyleSheet("")
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


class PullRequestListDialog(QDialog):
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
        pr_data: Optional[List[Dict]] = None,
    ) -> None:
        """Initialize pull request list dialog."""
        super().__init__(parent)
        self.pr_data = pr_data or []
        self._init_ui()
        self._populate_table()

    def _init_ui(self) -> None:
        """Initialize the pull request list UI."""
        self.setWindowTitle("Pull Requests")
        self.setMinimumSize(700, 400)
        self.setModal(False)

        layout = QVBoxLayout(self)

        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("State:"))

        self.state_filter = QComboBox()
        self.state_filter.addItems(["Open", "Closed", "Merged", "All"])
        self.state_filter.setCurrentText("Open")
        self.state_filter.setToolTip("Filter pull requests by state")
        self.state_filter.currentTextChanged.connect(self._filter_changed)
        filter_layout.addWidget(self.state_filter)

        filter_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setToolTip("Reload pull requests from GitHub")
        refresh_btn.clicked.connect(self._refresh_clicked)
        filter_layout.addWidget(refresh_btn)

        layout.addLayout(filter_layout)

        # PR table
        self.pr_table = QTableWidget()
        self.pr_table.setColumnCount(6)
        self.pr_table.setHorizontalHeaderLabels(
            ["Number", "Title", "Author", "Status", "Created", "URL"]
        )
        self.pr_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.pr_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.pr_table.doubleClicked.connect(self._row_double_clicked)
        self.pr_table.setToolTip("Double-click to open PR in browser")

        # Configure column widths
        header = self.pr_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Number
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Title
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Author
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Created
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # URL

        layout.addWidget(self.pr_table)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)

    def _populate_table(self) -> None:
        """Populate the PR table with current data."""
        self.pr_table.setRowCount(0)

        if not self.pr_data:
            # Show "no data" message
            self.pr_table.setRowCount(1)
            item = QTableWidgetItem("No pull requests found")
            item.setTextAlignment(Qt.AlignCenter)
            self.pr_table.setSpan(0, 0, 1, 6)
            self.pr_table.setItem(0, 0, item)
            return

        # Filter by selected state
        state_filter = self.state_filter.currentText().lower()
        filtered_prs = [
            pr
            for pr in self.pr_data
            if state_filter == "all" or pr.get("state", "").lower() == state_filter
        ]

        self.pr_table.setRowCount(len(filtered_prs))

        for row, pr in enumerate(filtered_prs):
            # PR Number
            number_item = QTableWidgetItem(f"#{pr.get('number', 'N/A')}")
            self.pr_table.setItem(row, 0, number_item)

            # Title
            title_item = QTableWidgetItem(pr.get("title", "Untitled"))
            self.pr_table.setItem(row, 1, title_item)

            # Author
            author = pr.get("author", {})
            author_name = (
                author.get("login", "Unknown")
                if isinstance(author, dict)
                else str(author)
            )
            author_item = QTableWidgetItem(author_name)
            self.pr_table.setItem(row, 2, author_item)

            # Status
            status = pr.get("state", "unknown").capitalize()
            status_item = QTableWidgetItem(status)
            self.pr_table.setItem(row, 3, status_item)

            # Created date
            created = pr.get("createdAt", "Unknown")
            created_item = QTableWidgetItem(created)
            self.pr_table.setItem(row, 4, created_item)

            # URL
            url = pr.get("url", "")
            url_item = QTableWidgetItem(url)
            self.pr_table.setItem(row, 5, url_item)

    def _filter_changed(self, _text: str) -> None:
        """Handle state filter change."""
        self._populate_table()

    def _refresh_clicked(self) -> None:
        """Handle refresh button click."""
        # Emit signal or call callback to reload data
        logger.info("Refresh button clicked - parent should reload PR data")

    def _row_double_clicked(self, index) -> None:
        """Handle row double-click to open PR in browser."""
        row = index.row()
        url_item = self.pr_table.item(row, 5)
        if url_item:
            url = url_item.text()
            if url:
                QDesktopServices.openUrl(QUrl(url))
                logger.info(f"Opening PR in browser: {url}")

    def set_pr_data(self, pr_data: List[Dict]) -> None:
        """
        Update PR data and refresh table.

        Args:
            pr_data: List of PR dictionaries
        """
        self.pr_data = pr_data
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
        title = self.title_input.text().strip()
        if not title:
            # Show error in title field
            self.title_input.setStyleSheet("QLineEdit { border: 1px solid red; }")
            self.title_input.setFocus()
            logger.warning("Issue title is required")
            return

        # Clear error styling
        self.title_input.setStyleSheet("")
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


class IssueListDialog(QDialog):
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
        issue_data: Optional[List[Dict]] = None,
    ) -> None:
        """Initialize issue list dialog."""
        super().__init__(parent)
        self.issue_data = issue_data or []
        self._init_ui()
        self._populate_table()

    def _init_ui(self) -> None:
        """Initialize the issue list UI."""
        self.setWindowTitle("Issues")
        self.setMinimumSize(700, 400)
        self.setModal(False)

        layout = QVBoxLayout(self)

        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("State:"))

        self.state_filter = QComboBox()
        self.state_filter.addItems(["Open", "Closed", "All"])
        self.state_filter.setCurrentText("Open")
        self.state_filter.setToolTip("Filter issues by state")
        self.state_filter.currentTextChanged.connect(self._filter_changed)
        filter_layout.addWidget(self.state_filter)

        filter_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setToolTip("Reload issues from GitHub")
        refresh_btn.clicked.connect(self._refresh_clicked)
        filter_layout.addWidget(refresh_btn)

        layout.addLayout(filter_layout)

        # Issue table
        self.issue_table = QTableWidget()
        self.issue_table.setColumnCount(6)
        self.issue_table.setHorizontalHeaderLabels(
            ["Number", "Title", "Author", "Status", "Created", "URL"]
        )
        self.issue_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.issue_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.issue_table.doubleClicked.connect(self._row_double_clicked)
        self.issue_table.setToolTip("Double-click to open issue in browser")

        # Configure column widths
        header = self.issue_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Number
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Title
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Author
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Created
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # URL

        layout.addWidget(self.issue_table)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)

    def _populate_table(self) -> None:
        """Populate the issue table with current data."""
        self.issue_table.setRowCount(0)

        if not self.issue_data:
            # Show "no data" message
            self.issue_table.setRowCount(1)
            item = QTableWidgetItem("No issues found")
            item.setTextAlignment(Qt.AlignCenter)
            self.issue_table.setSpan(0, 0, 1, 6)
            self.issue_table.setItem(0, 0, item)
            return

        # Filter by selected state
        state_filter = self.state_filter.currentText().lower()
        filtered_issues = [
            issue
            for issue in self.issue_data
            if state_filter == "all" or issue.get("state", "").lower() == state_filter
        ]

        self.issue_table.setRowCount(len(filtered_issues))

        for row, issue in enumerate(filtered_issues):
            # Issue Number
            number_item = QTableWidgetItem(f"#{issue.get('number', 'N/A')}")
            self.issue_table.setItem(row, 0, number_item)

            # Title
            title_item = QTableWidgetItem(issue.get("title", "Untitled"))
            self.issue_table.setItem(row, 1, title_item)

            # Author
            author = issue.get("author", {})
            author_name = (
                author.get("login", "Unknown")
                if isinstance(author, dict)
                else str(author)
            )
            author_item = QTableWidgetItem(author_name)
            self.issue_table.setItem(row, 2, author_item)

            # Status
            status = issue.get("state", "unknown").capitalize()
            status_item = QTableWidgetItem(status)
            self.issue_table.setItem(row, 3, status_item)

            # Created date
            created = issue.get("createdAt", "Unknown")
            created_item = QTableWidgetItem(created)
            self.issue_table.setItem(row, 4, created_item)

            # URL
            url = issue.get("url", "")
            url_item = QTableWidgetItem(url)
            self.issue_table.setItem(row, 5, url_item)

    def _filter_changed(self, _text: str) -> None:
        """Handle state filter change."""
        self._populate_table()

    def _refresh_clicked(self) -> None:
        """Handle refresh button click."""
        # Emit signal or call callback to reload data
        logger.info("Refresh button clicked - parent should reload issue data")

    def _row_double_clicked(self, index) -> None:
        """Handle row double-click to open issue in browser."""
        row = index.row()
        url_item = self.issue_table.item(row, 5)
        if url_item:
            url = url_item.text()
            if url:
                QDesktopServices.openUrl(QUrl(url))
                logger.info(f"Opening issue in browser: {url}")

    def set_issue_data(self, issue_data: List[Dict]) -> None:
        """
        Update issue data and refresh table.

        Args:
            issue_data: List of issue dictionaries
        """
        self.issue_data = issue_data
        self._populate_table()
