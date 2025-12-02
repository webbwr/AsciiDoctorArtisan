"""
GitHub Issue Dialogs - Create and List Issues.

Extracted from github_dialogs.py for MA principle compliance.
Contains CreateIssueDialog and IssueListDialog.

Implements FR-057 to FR-060 (Issue features).
"""

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from asciidoc_artisan.ui.github_base_dialog import BaseListDialog
from asciidoc_artisan.ui.github_validation import validate_required_text

logger = logging.getLogger(__name__)


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

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize create issue dialog."""
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """
        Initialize the create issue UI.

        MA principle: Reduced from 57→19 lines by extracting 4 helpers (67% reduction).
        """
        self.setWindowTitle("Create Issue")
        self.setMinimumSize(500, 350)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Add UI components
        form_layout = self._setup_form_fields()
        layout.addLayout(form_layout)

        body_label, self.body_input = self._setup_body_field()
        layout.addWidget(body_label)
        layout.addWidget(self.body_input)

        required_label = self._setup_required_note()
        layout.addWidget(required_label)

        button_box = self._setup_action_buttons()
        layout.addWidget(button_box)

    def _setup_form_fields(self) -> QFormLayout:
        """
        Create form fields for issue creation.

        MA principle: Extracted from _init_ui (15 lines).

        Returns:
            QFormLayout with title and labels fields
        """
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
            "Comma-separated labels (optional)\nCommon labels: bug, enhancement, documentation, question"
        )
        form_layout.addRow("Labels:", self.labels_input)

        return form_layout

    def _setup_body_field(self) -> tuple[QLabel, QPlainTextEdit]:
        """
        Create description field for issue body.

        MA principle: Extracted from _init_ui (17 lines).

        Returns:
            Tuple of (label, text_edit) for issue description
        """
        body_label = QLabel("Description:")
        body_label.setToolTip("Detailed description of the issue (optional)")

        body_input = QPlainTextEdit()
        body_input.setPlaceholderText(
            "Describe the issue...\n\n"
            "What is the problem?\n"
            "What is the expected behavior?\n"
            "Steps to reproduce (if bug):\n"
            "1. \n"
            "2. \n"
            "3. "
        )
        body_input.setMinimumHeight(150)
        body_input.setToolTip("Detailed issue description (optional)")

        return body_label, body_input

    def _setup_required_note(self) -> QLabel:
        """
        Create required field note label.

        MA principle: Extracted from _init_ui (4 lines).

        Returns:
            QLabel with required field note styling
        """
        required_label = QLabel("* Required field")
        required_label.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        return required_label

    def _setup_action_buttons(self) -> QDialogButtonBox:
        """
        Create action buttons for issue creation dialog.

        MA principle: Extracted from _init_ui (6 lines).

        Returns:
            QDialogButtonBox with Create Issue and Cancel buttons
        """
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Create Issue")
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def _validate_and_accept(self) -> None:
        """Validate inputs and accept dialog if valid."""
        # Validate title is not empty
        if not validate_required_text(self.title_input, "Issue title"):
            return

        self.accept()

    def get_issue_data(self) -> dict[str, str]:
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
        parent: QWidget | None = None,
        issue_data: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize issue list dialog."""
        self.issue_data = issue_data or []
        super().__init__(parent, data=issue_data)

    def _get_window_title(self) -> str:
        """Get window title."""
        return "Issues"

    def _get_filter_states(self) -> list[str]:
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
            author_name = author.get("login", "Unknown") if isinstance(author, dict) else str(author)
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

    def set_issue_data(self, issue_data: list[dict[str, Any]]) -> None:
        """
        Update issue data and refresh table.

        Args:
            issue_data: List of issue dictionaries
        """
        self.issue_data = issue_data
        self._data = issue_data
        self._populate_table()
