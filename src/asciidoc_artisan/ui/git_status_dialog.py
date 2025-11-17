"""
Git Status Dialog - Show detailed Git repository status.

This dialog provides a detailed view of Git repository status with:
- Current branch name
- Modified files list
- Staged files list
- Untracked files list
- Stage/Unstage buttons
- Refresh functionality

Implements v1.9.0 Git Status Command feature.
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from .main_window import AsciiDocEditor


class GitStatusDialog(QDialog):
    """
    Dialog showing detailed Git repository status.

    Displays modified, staged, and untracked files with file-level details
    including line change counts (additions/deletions).

    Signals:
        refresh_requested: Emitted when user clicks Refresh button
        stage_all_requested: Emitted when user clicks Stage All button
        unstage_all_requested: Emitted when user clicks Unstage All button
    """

    refresh_requested = Signal()
    stage_all_requested = Signal()
    unstage_all_requested = Signal()

    def __init__(self, parent: "AsciiDocEditor") -> None:
        """
        Initialize Git Status Dialog.

        Args:
            parent: Parent window (AsciiDocEditor)
        """
        super().__init__(parent)

        self.setWindowTitle("Git Status")
        self.setModal(False)  # Non-modal dialog
        self.resize(800, 600)

        # Create UI
        self._create_ui()

        logger.debug("Git Status Dialog initialized")

    def _create_ui(self) -> None:
        """Create the dialog UI components."""
        layout = QVBoxLayout(self)

        # Branch label at top
        self.branch_label = QLabel("Branch: --")
        self.branch_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.branch_label)

        # Tab widget for different file categories
        self.tab_widget = QTabWidget()

        # Modified files tab
        self.modified_table = self._create_file_table()
        self.tab_widget.addTab(self.modified_table, "Modified (0)")

        # Staged files tab
        self.staged_table = self._create_file_table()
        self.tab_widget.addTab(self.staged_table, "Staged (0)")

        # Untracked files tab
        self.untracked_table = self._create_file_table()
        self.tab_widget.addTab(self.untracked_table, "Untracked (0)")

        layout.addWidget(self.tab_widget)

        # Button row at bottom
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setToolTip("Refresh Git status")
        self.refresh_button.clicked.connect(self.refresh_requested.emit)
        button_layout.addWidget(self.refresh_button)

        self.stage_all_button = QPushButton("Stage All")
        self.stage_all_button.setToolTip("Stage all modified and untracked files")
        self.stage_all_button.clicked.connect(self.stage_all_requested.emit)
        button_layout.addWidget(self.stage_all_button)

        self.unstage_all_button = QPushButton("Unstage All")
        self.unstage_all_button.setToolTip("Unstage all staged files")
        self.unstage_all_button.clicked.connect(self.unstage_all_requested.emit)
        button_layout.addWidget(self.unstage_all_button)

        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _create_file_table(self) -> QTableWidget:
        """
        Create a table widget for displaying file status.

        Returns:
            QTableWidget configured for file status display
        """
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Status", "File", "Lines"])
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Alternating row colors for readability
        table.setAlternatingRowColors(True)

        return table

    def populate_status(
        self,
        branch: str,
        modified_files: list[dict[str, str]],
        staged_files: list[dict[str, str]],
        untracked_files: list[dict[str, str]],
    ) -> None:
        """
        Populate dialog with Git status data.

        Args:
            branch: Current branch name
            modified_files: List of modified file dicts with keys: path, status, lines_added, lines_deleted
            staged_files: List of staged file dicts (same format)
            untracked_files: List of untracked file dicts (path only)

        Example:
            >>> dialog.populate_status(
            ...     branch="main",
            ...     modified_files=[{"path": "README.md", "status": "M", "lines_added": "5", "lines_deleted": "2"}],
            ...     staged_files=[{"path": "src/main.py", "status": "M", "lines_added": "10", "lines_deleted": "0"}],
            ...     untracked_files=[{"path": "new_file.txt"}]
            ... )
        """
        # Update branch label
        self.branch_label.setText(f"Branch: {branch}")

        # Populate modified files table
        self._populate_table(self.modified_table, modified_files, show_lines=True)
        self.tab_widget.setTabText(0, f"Modified ({len(modified_files)})")

        # Populate staged files table
        self._populate_table(self.staged_table, staged_files, show_lines=True)
        self.tab_widget.setTabText(1, f"Staged ({len(staged_files)})")

        # Populate untracked files table
        self._populate_table(self.untracked_table, untracked_files, show_lines=False)
        self.tab_widget.setTabText(2, f"Untracked ({len(untracked_files)})")

        logger.debug(
            f"Git status populated: {len(modified_files)} modified, "
            f"{len(staged_files)} staged, {len(untracked_files)} untracked"
        )

    def _populate_table(
        self, table: QTableWidget, files: list[dict[str, str]], show_lines: bool
    ) -> None:
        """
        Populate a table widget with file data.

        Args:
            table: Table widget to populate
            files: List of file dictionaries
            show_lines: Whether to show line change counts
        """
        table.setRowCount(len(files))

        for row, file_data in enumerate(files):
            # Status column
            status = file_data.get("status", "?")
            status_item = QTableWidgetItem(self._format_status(status))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, status_item)

            # File path column
            path = file_data.get("path", "")
            path_item = QTableWidgetItem(path)
            table.setItem(row, 1, path_item)

            # Lines changed column
            if show_lines:
                lines_added = file_data.get("lines_added", "0")
                lines_deleted = file_data.get("lines_deleted", "0")
                lines_text = f"+{lines_added} -{lines_deleted}"
                lines_item = QTableWidgetItem(lines_text)
                lines_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Color code: green for additions, red for deletions
                if int(lines_added) > int(lines_deleted):
                    lines_item.setForeground(Qt.GlobalColor.darkGreen)
                elif int(lines_deleted) > int(lines_added):
                    lines_item.setForeground(Qt.GlobalColor.darkRed)

                table.setItem(row, 2, lines_item)
            else:
                # Untracked files don't have line counts
                table.setItem(row, 2, QTableWidgetItem("--"))

    def _format_status(self, status: str) -> str:
        """
        Format Git status code into readable text.

        Args:
            status: Git status code (M, A, D, R, C, U, ?)

        Returns:
            Formatted status string

        Status codes:
            M = Modified
            A = Added
            D = Deleted
            R = Renamed
            C = Copied
            U = Unmerged (conflict)
            ? = Untracked
        """
        status_map = {
            "M": "Modified",
            "A": "Added",
            "D": "Deleted",
            "R": "Renamed",
            "C": "Copied",
            "U": "Conflict",
            "?": "Untracked",
        }
        return status_map.get(status, status)

    def clear_status(self) -> None:
        """Clear all status data from dialog."""
        self.branch_label.setText("Branch: --")
        self.modified_table.setRowCount(0)
        self.staged_table.setRowCount(0)
        self.untracked_table.setRowCount(0)
        self.tab_widget.setTabText(0, "Modified (0)")
        self.tab_widget.setTabText(1, "Staged (0)")
        self.tab_widget.setTabText(2, "Untracked (0)")
