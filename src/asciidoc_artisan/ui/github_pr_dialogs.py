"""
GitHub Pull Request Dialogs - Create and List PRs.

Extracted from github_dialogs.py for MA principle compliance.
Contains CreatePullRequestDialog and PullRequestListDialog.

Implements FR-054 to FR-056 (Pull Request features).
"""

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
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
from asciidoc_artisan.ui.github_validation import (
    clear_validation_error,
    show_validation_error,
    validate_required_text,
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
        parent: QWidget | None = None,
        current_branch: str = "",
        base_branch: str = "main",
    ) -> None:
        """Initialize create pull request dialog."""
        super().__init__(parent)
        self.current_branch = current_branch
        self.base_branch = base_branch
        self._init_ui()

    def _init_ui(self) -> None:
        """
        Initialize the create pull request UI.

        MA principle: Reduced from 63→19 lines by extracting 4 helpers (70% reduction).
        """
        self.setWindowTitle("Create Pull Request")
        self.setMinimumSize(500, 350)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Add UI components
        form_layout = self._setup_form_fields()
        layout.addLayout(form_layout)

        body_label, self.body_input = self._setup_body_field()
        layout.addWidget(body_label)
        layout.addWidget(self.body_input)

        self.draft_checkbox, required_label = self._setup_dialog_options()
        layout.addWidget(self.draft_checkbox)
        layout.addWidget(required_label)

        button_box = self._setup_action_buttons()
        layout.addWidget(button_box)

    def _setup_form_fields(self) -> QFormLayout:
        """
        Create form fields for PR creation.

        MA principle: Extracted from _init_ui (22 lines).

        Returns:
            QFormLayout with title, base, and head branch fields
        """
        form_layout = QFormLayout()

        # Title field (required)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter a descriptive title for your PR")
        self.title_input.setToolTip("PR title (required)")
        form_layout.addRow("Title:*", self.title_input)

        # Base branch field
        self.base_input = QLineEdit(self.base_branch)
        self.base_input.setToolTip("Target branch for merging (usually 'main' or 'master')")
        form_layout.addRow("Base branch:", self.base_input)

        # Head branch field (current branch)
        self.head_input = QComboBox()
        self.head_input.setEditable(True)
        if self.current_branch:
            self.head_input.addItem(self.current_branch)
            self.head_input.setCurrentText(self.current_branch)
        self.head_input.setToolTip("Source branch containing your changes")
        form_layout.addRow("Head branch:", self.head_input)

        return form_layout

    def _setup_body_field(self) -> tuple[QLabel, QPlainTextEdit]:
        """
        Create description field for PR body.

        MA principle: Extracted from _init_ui (12 lines).

        Returns:
            Tuple of (label, text_edit) for PR description
        """
        body_label = QLabel("Description:")
        body_label.setToolTip("Detailed description of your changes (optional)")

        body_input = QPlainTextEdit()
        body_input.setPlaceholderText(
            "Describe your changes...\n\nWhat does this PR do?\nWhy is this change needed?\nHow has this been tested?"
        )
        body_input.setMinimumHeight(150)
        body_input.setToolTip("Detailed PR description (optional)")

        return body_label, body_input

    def _setup_dialog_options(self) -> tuple[QCheckBox, QLabel]:
        """
        Create dialog options (draft checkbox and required note).

        MA principle: Extracted from _init_ui (8 lines).

        Returns:
            Tuple of (draft_checkbox, required_label)
        """
        draft_checkbox = QCheckBox("Create as draft PR")
        draft_checkbox.setToolTip("Draft PRs can't be merged until marked as ready for review")

        required_label = QLabel("* Required field")
        required_label.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")

        return draft_checkbox, required_label

    def _setup_action_buttons(self) -> QDialogButtonBox:
        """
        Create action buttons for PR creation dialog.

        MA principle: Extracted from _init_ui (6 lines).

        Returns:
            QDialogButtonBox with Create PR and Cancel buttons
        """
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Create PR")
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def _validate_and_accept(self) -> None:
        """Validate inputs and accept dialog if valid."""
        # Validate title is not empty
        if not validate_required_text(self.title_input, "PR title"):
            return

        # Validate base != head
        base = self.base_input.text().strip()
        head = self.head_input.currentText().strip()
        if base == head:
            show_validation_error(self.head_input, "QComboBox")
            logger.warning("Base and head branches cannot be the same")
            return

        clear_validation_error(self.head_input)
        self.accept()

    def get_pr_data(self) -> dict[str, str]:
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
        parent: QWidget | None = None,
        pr_data: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize pull request list dialog."""
        self.pr_data = pr_data or []
        super().__init__(parent, data=pr_data)

    def _get_window_title(self) -> str:
        """Get window title."""
        return "Pull Requests"

    def _get_filter_states(self) -> list[str]:
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
            pr for pr in self.pr_data if state_filter == "all" or pr.get("state", "").lower() == state_filter
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
            author_name = author.get("login", "Unknown") if isinstance(author, dict) else str(author)
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

    def set_pr_data(self, pr_data: list[dict[str, Any]]) -> None:
        """
        Update PR data and refresh table.

        Args:
            pr_data: List of PR dictionaries
        """
        self.pr_data = pr_data
        self._data = pr_data
        self._populate_table()
