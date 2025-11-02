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
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class FindBarWidget(QWidget):
    """
    Non-modal find/replace bar for quick text searches and replacements.

    This widget appears at the bottom of the editor and provides
    quick search and replace functionality without blocking the UI.

    Signals:
        search_requested(str, bool): Emitted when search parameters change
            - str: search text
            - bool: case sensitive
        find_next_requested(): Emitted when user clicks Find Next
        find_previous_requested(): Emitted when user clicks Find Previous
        replace_requested(str): Emitted when user clicks Replace
            - str: replacement text
        replace_all_requested(str): Emitted when user clicks Replace All
            - str: replacement text
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
    replace_requested = Signal(str)  # (replace_text)
    replace_all_requested = Signal(str)  # (replace_text)
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
        self._replace_mode = False  # Toggle between Find and Find/Replace
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        # Main vertical layout (stacks Find row and Replace row)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # === FIND ROW ===
        find_row = QHBoxLayout()
        find_row.setSpacing(8)

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
        find_row.addWidget(self._close_btn)

        # Toggle replace button
        self._toggle_replace_btn = QPushButton("▶")
        self._toggle_replace_btn.setFixedSize(24, 24)
        self._toggle_replace_btn.setToolTip("Toggle Replace (Ctrl+H)")
        self._toggle_replace_btn.setStyleSheet(
            """
            QPushButton {
                border: 1px solid #555;
                background-color: transparent;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            """
        )
        find_row.addWidget(self._toggle_replace_btn)

        # Label
        label = QLabel("Find:")
        find_row.addWidget(label)

        # Search input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search text...")
        self._search_input.setMinimumWidth(250)
        find_row.addWidget(self._search_input)

        # Match counter label
        self._counter_label = QLabel("No matches")
        self._counter_label.setMinimumWidth(80)
        self._counter_label.setStyleSheet("color: #888;")
        find_row.addWidget(self._counter_label)

        # Previous button
        self._prev_btn = QPushButton("Previous")
        self._prev_btn.setToolTip("Find Previous (Shift+F3)")
        find_row.addWidget(self._prev_btn)

        # Next button
        self._next_btn = QPushButton("Next")
        self._next_btn.setToolTip("Find Next (F3)")
        find_row.addWidget(self._next_btn)

        # Case sensitive checkbox
        self._case_checkbox = QCheckBox("Match case")
        find_row.addWidget(self._case_checkbox)

        # Stretch to push everything left
        find_row.addStretch()

        # Add find row to main layout
        main_layout.addLayout(find_row)

        # === REPLACE ROW ===
        self._replace_row_widget = QWidget()
        replace_row = QHBoxLayout(self._replace_row_widget)
        replace_row.setContentsMargins(0, 0, 0, 0)
        replace_row.setSpacing(8)

        # Spacer to align with find input (close + toggle buttons width)
        replace_row.addSpacing(56)

        # Replace label
        replace_label = QLabel("Replace:")
        replace_row.addWidget(replace_label)

        # Replace input
        self._replace_input = QLineEdit()
        self._replace_input.setPlaceholderText("Replace with...")
        self._replace_input.setMinimumWidth(250)
        replace_row.addWidget(self._replace_input)

        # Spacer to align with counter (80px width)
        replace_row.addSpacing(80)

        # Replace button
        self._replace_btn = QPushButton("Replace")
        self._replace_btn.setToolTip("Replace current match (Ctrl+Shift+1)")
        replace_row.addWidget(self._replace_btn)

        # Replace All button
        self._replace_all_btn = QPushButton("Replace All")
        self._replace_all_btn.setToolTip("Replace all matches (Ctrl+Shift+Enter)")
        replace_row.addWidget(self._replace_all_btn)

        # Stretch to push everything left
        replace_row.addStretch()

        # Add replace row to main layout (initially hidden)
        main_layout.addWidget(self._replace_row_widget)
        self._replace_row_widget.hide()

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
        self._toggle_replace_btn.clicked.connect(self._toggle_replace_mode)
        self._search_input.textChanged.connect(self._on_search_text_changed)
        self._search_input.returnPressed.connect(self._on_return_pressed)
        self._case_checkbox.toggled.connect(self._on_case_toggled)
        self._prev_btn.clicked.connect(self._on_previous_clicked)
        self._next_btn.clicked.connect(self._on_next_clicked)
        self._replace_btn.clicked.connect(self._on_replace_clicked)
        self._replace_all_btn.clicked.connect(self._on_replace_all_clicked)

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

    def _toggle_replace_mode(self) -> None:
        """Toggle between Find and Find/Replace mode."""
        self._replace_mode = not self._replace_mode

        if self._replace_mode:
            # Show replace controls
            self._replace_row_widget.show()
            self._toggle_replace_btn.setText("▼")
            logger.debug("Replace mode enabled")
        else:
            # Hide replace controls
            self._replace_row_widget.hide()
            self._toggle_replace_btn.setText("▶")
            logger.debug("Replace mode disabled")

    def _on_replace_clicked(self) -> None:
        """Handle Replace button click."""
        replace_text = self._replace_input.text()
        self.replace_requested.emit(replace_text)
        logger.debug(f"Replace requested with: '{replace_text}'")

    def _on_replace_all_clicked(self) -> None:
        """Handle Replace All button click."""
        replace_text = self._replace_input.text()
        self.replace_all_requested.emit(replace_text)
        logger.debug(f"Replace all requested with: '{replace_text}'")

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

    def show_replace_and_focus(self) -> None:
        """
        Show the find bar in replace mode and focus the search input.

        This is triggered by Ctrl+H (Find and Replace).
        """
        self.show()
        # Enable replace mode if not already enabled
        if not self._replace_mode:
            self._toggle_replace_mode()
        self._search_input.setFocus()
        self._search_input.selectAll()
        logger.debug("Find/Replace bar shown and focused")

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

    def get_replace_text(self) -> str:
        """
        Get current replace text.

        Returns:
            Current replace text
        """
        return self._replace_input.text()

    def set_replace_text(self, text: str) -> None:
        """
        Set replace text programmatically.

        Args:
            text: Text to set in replace input
        """
        self._replace_input.setText(text)

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
