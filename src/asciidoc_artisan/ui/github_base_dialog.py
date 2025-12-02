"""
GitHub Base List Dialog - Template Method Pattern for List Views.

Extracted from github_dialogs.py for MA principle compliance.
Provides common functionality for PR and Issue list dialogs.
"""

import logging
from typing import Any

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


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
        parent: QWidget | None = None,
        data: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize base list dialog."""
        super().__init__(parent)
        self._data = data or []
        self._init_ui()
        self._populate_table()

    def _get_window_title(self) -> str:
        """Get window title. Subclasses must override."""
        raise NotImplementedError

    def _get_filter_states(self) -> list[str]:
        """Get filter state options. Subclasses must override."""
        raise NotImplementedError

    def _get_data_attribute_name(self) -> str:
        """Get data attribute name. Subclasses must override."""
        raise NotImplementedError

    def _get_tooltip_prefix(self) -> str:
        """Get tooltip prefix (e.g., 'pull requests', 'issues'). Subclasses must override."""
        raise NotImplementedError

    def _init_ui(self) -> None:
        """
        Initialize the list dialog UI.

        MA principle: Reduced from 54→15 lines by extracting 3 helpers (72% reduction).
        """
        self.setWindowTitle(self._get_window_title())
        self.setMinimumSize(700, 400)
        self.setModal(False)

        layout = QVBoxLayout(self)

        # Add UI components
        filter_layout = self._setup_filter_controls()
        layout.addLayout(filter_layout)

        self.table = self._setup_table_widget()
        layout.addWidget(self.table)

        button_box = self._setup_dialog_buttons()
        layout.addWidget(button_box)

    def _setup_filter_controls(self) -> QHBoxLayout:
        """
        Create filter controls for the dialog.

        MA principle: Extracted from _init_ui (22 lines).

        Returns:
            QHBoxLayout with filter controls
        """
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

        return filter_layout

    def _setup_table_widget(self) -> QTableWidget:
        """
        Create and configure table widget.

        MA principle: Extracted from _init_ui (18 lines).

        Returns:
            Configured QTableWidget
        """
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Number", "Title", "Author", "Status", "Created", "URL"])
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.doubleClicked.connect(self._row_double_clicked)
        table.setToolTip(f"Double-click to open {self._get_tooltip_prefix()[:-1]} in browser")

        # Configure column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Number
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Title
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Author
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Created
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # URL

        return table

    def _setup_dialog_buttons(self) -> QDialogButtonBox:
        """
        Create dialog button box.

        MA principle: Extracted from _init_ui (4 lines).

        Returns:
            QDialogButtonBox with close button
        """
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        return button_box

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
