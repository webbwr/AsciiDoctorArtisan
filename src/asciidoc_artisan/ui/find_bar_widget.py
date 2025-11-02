"""
Find Bar Widget - Quick find toolbar for AsciiDoc Artisan.

This module provides a non-modal find bar that appears at the bottom of the
editor for quick text searches. Triggered by Ctrl+F.

Features:
- Live search as you type
- Find next/previous buttons
- Match counter (e.g., "5 of 23")
- Case sensitivity toggle
- Close button or Esc to hide
- Preserves search history

Example:
    >>> find_bar = FindBarWidget(parent)
    >>> find_bar.search_requested.connect(on_search)
    >>> find_bar.show_and_focus()
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

logger = logging.getLogger(__name__)


class FindBarWidget(QWidget):
    """
    Non-modal find bar for quick text searches.

    This widget appears at the bottom of the editor and provides
    quick search functionality without blocking the UI.

    Signals:
        search_requested(str, bool): Emitted when search parameters change
            - str: search text
            - bool: case sensitive
        find_next_requested(): Emitted when user clicks Find Next
        find_previous_requested(): Emitted when user clicks Find Previous
        closed(): Emitted when find bar is closed

    Example:
        >>> find_bar = FindBarWidget(parent)
        >>> find_bar.search_requested.connect(lambda text, case: print(f"Search: {text}"))
        >>> find_bar.show_and_focus()
    """

    # Signals
    search_requested = Signal(str, bool)  # (search_text, case_sensitive)
    find_next_requested = Signal()
    find_previous_requested = Signal()
    closed = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize FindBarWidget.

        Args:
            parent: Parent widget (usually main window)
        """
        super().__init__(parent)
        self._current_match = 0
        self._total_matches = 0
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # Close button
        self._close_btn = QPushButton("×")
        self._close_btn.setFixedSize(24, 24)
        self._close_btn.setToolTip("Close (Esc)")
        self._close_btn.setStyleSheet(
            """
            QPushButton {
                border: 1px solid #555;
                background-color: transparent;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444;
            }
            """
        )
        layout.addWidget(self._close_btn)

        # Label
        label = QLabel("Find:")
        layout.addWidget(label)

        # Search input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search text...")
        self._search_input.setMinimumWidth(250)
        layout.addWidget(self._search_input)

        # Match counter label
        self._counter_label = QLabel("No matches")
        self._counter_label.setMinimumWidth(80)
        self._counter_label.setStyleSheet("color: #888;")
        layout.addWidget(self._counter_label)

        # Previous button
        self._prev_btn = QPushButton("Previous")
        self._prev_btn.setToolTip("Find Previous (Shift+F3)")
        layout.addWidget(self._prev_btn)

        # Next button
        self._next_btn = QPushButton("Next")
        self._next_btn.setToolTip("Find Next (F3)")
        layout.addWidget(self._next_btn)

        # Case sensitive checkbox
        self._case_checkbox = QCheckBox("Match case")
        layout.addWidget(self._case_checkbox)

        # Stretch to push everything left
        layout.addStretch()

        # Set background color to distinguish from editor
        self.setStyleSheet(
            """
            FindBarWidget {
                background-color: #2b2b2b;
                border-top: 1px solid #555;
            }
            """
        )

        # Initially hidden
        self.hide()

    def _connect_signals(self) -> None:
        """Connect internal signal handlers."""
        self._close_btn.clicked.connect(self._on_close)
        self._search_input.textChanged.connect(self._on_search_text_changed)
        self._search_input.returnPressed.connect(self._on_return_pressed)
        self._case_checkbox.toggled.connect(self._on_case_toggled)
        self._prev_btn.clicked.connect(self._on_previous_clicked)
        self._next_btn.clicked.connect(self._on_next_clicked)

    def _on_close(self) -> None:
        """Handle close button click."""
        self.hide()
        self.closed.emit()
        logger.debug("Find bar closed")

    def _on_search_text_changed(self, text: str) -> None:
        """Handle search text changes (live search)."""
        case_sensitive = self._case_checkbox.isChecked()
        self.search_requested.emit(text, case_sensitive)
        logger.debug(f"Search text changed: '{text}' (case_sensitive={case_sensitive})")

    def _on_case_toggled(self, checked: bool) -> None:
        """Handle case sensitivity toggle."""
        text = self._search_input.text()
        self.search_requested.emit(text, checked)
        logger.debug(f"Case sensitivity toggled: {checked}")

    def _on_return_pressed(self) -> None:
        """Handle Enter key in search input (find next)."""
        self.find_next_requested.emit()

    def _on_previous_clicked(self) -> None:
        """Handle Previous button click."""
        self.find_previous_requested.emit()
        logger.debug("Find previous requested")

    def _on_next_clicked(self) -> None:
        """Handle Next button click."""
        self.find_next_requested.emit()
        logger.debug("Find next requested")

    def keyPressEvent(self, event) -> None:
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            self._on_close()
            event.accept()
        else:
            super().keyPressEvent(event)

    def show_and_focus(self) -> None:
        """
        Show the find bar and focus the search input.

        This is the recommended way to activate the find bar.
        """
        self.show()
        self._search_input.setFocus()
        self._search_input.selectAll()  # Select existing text for easy replacement
        logger.debug("Find bar shown and focused")

    def get_search_text(self) -> str:
        """
        Get current search text.

        Returns:
            Current search text
        """
        return self._search_input.text()

    def set_search_text(self, text: str) -> None:
        """
        Set search text programmatically.

        Args:
            text: Text to set in search input
        """
        self._search_input.setText(text)

    def is_case_sensitive(self) -> bool:
        """
        Check if case-sensitive search is enabled.

        Returns:
            True if case-sensitive, False otherwise
        """
        return self._case_checkbox.isChecked()

    def set_case_sensitive(self, enabled: bool) -> None:
        """
        Set case sensitivity.

        Args:
            enabled: True for case-sensitive, False otherwise
        """
        self._case_checkbox.setChecked(enabled)

    def update_match_count(self, current: int, total: int) -> None:
        """
        Update the match counter display.

        Args:
            current: Current match index (1-indexed, 0 if no matches)
            total: Total number of matches

        Example:
            >>> find_bar.update_match_count(5, 23)
            # Displays: "5 of 23"
        """
        self._current_match = current
        self._total_matches = total

        if total == 0:
            self._counter_label.setText("No matches")
            self._counter_label.setStyleSheet("color: #888;")
            self._prev_btn.setEnabled(False)
            self._next_btn.setEnabled(False)
        else:
            self._counter_label.setText(f"{current} of {total}")
            self._counter_label.setStyleSheet("color: #4CAF50;")  # Green for matches
            self._prev_btn.setEnabled(True)
            self._next_btn.setEnabled(True)

        logger.debug(f"Match count updated: {current} of {total}")

    def clear(self) -> None:
        """Clear the search input and reset match counter."""
        self._search_input.clear()
        self.update_match_count(0, 0)
        logger.debug("Find bar cleared")

    def set_not_found_style(self) -> None:
        """Apply visual feedback for no matches found."""
        self._search_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #4a2020;
                border: 1px solid #cc0000;
            }
            """
        )

    def clear_not_found_style(self) -> None:
        """Clear the not-found visual feedback."""
        self._search_input.setStyleSheet("")
