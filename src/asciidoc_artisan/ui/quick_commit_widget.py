"""
Quick Commit Widget - Inline commit message input for fast commits.

This widget provides a non-modal inline input for Git commit messages,
allowing users to quickly commit changes without opening a dialog.

Features:
- Single-line commit message input
- Enter to commit, Escape to cancel
- OK button for mouse users
- Keyboard-driven workflow

Implements v1.9.0 Quick Commit feature.
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor


class QuickCommitWidget(QWidget):
    """
    Inline commit message input widget.

    Displays a horizontal bar with commit message input field and buttons.
    Designed to appear above the status bar for quick, keyboard-driven commits.

    Signals:
        commit_requested: Emitted when user commits (message: str)
        cancelled: Emitted when user cancels (Escape key)
    """

    commit_requested = Signal(str)
    cancelled = Signal()

    def __init__(self, parent: "AsciiDocEditor") -> None:
        """
        Initialize Quick Commit Widget.

        Args:
            parent: Parent window (AsciiDocEditor)
        """
        super().__init__(parent)

        # Create UI
        self._create_ui()

        # Hide by default
        self.hide()

        logger.debug("Quick Commit Widget initialized")

    def _create_ui(self) -> None:
        """Create the widget UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        # Label
        label = QLabel("Commit:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        # Commit message input
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Enter commit message...")
        self.message_input.returnPressed.connect(self._on_commit)
        layout.addWidget(self.message_input, 1)  # Stretch to fill space

        # OK button
        self.ok_button = QPushButton("✓")
        self.ok_button.setFixedSize(24, 24)
        self.ok_button.setToolTip("Commit (Enter)")
        self.ok_button.clicked.connect(self._on_commit)
        layout.addWidget(self.ok_button)

        # Cancel button
        self.cancel_button = QPushButton("✕")
        self.cancel_button.setFixedSize(24, 24)
        self.cancel_button.setToolTip("Cancel (Escape)")
        self.cancel_button.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_button)

    def show_and_focus(self) -> None:
        """
        Show widget and focus input field.

        Clears any previous text and sets focus to the input field
        for immediate typing.
        """
        self.message_input.clear()
        self.show()
        self.message_input.setFocus()
        logger.debug("Quick Commit Widget shown")

    def _on_commit(self) -> None:
        """Handle commit request (Enter key or OK button)."""
        message = self.message_input.text().strip()

        if not message:
            # Don't commit with empty message
            logger.debug("Quick commit cancelled: empty message")
            return

        logger.info(f"Quick commit requested: '{message[:50]}...'")
        self.commit_requested.emit(message)
        self.hide()

    def _on_cancel(self) -> None:
        """Handle cancel request (Cancel button)."""
        logger.debug("Quick commit cancelled by button")
        self.cancelled.emit()
        self.hide()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """
        Handle key press events.

        Overrides QWidget.keyPressEvent to handle Escape key for cancellation.

        Args:
            event: Qt key event
        """
        if event.key() == Qt.Key.Key_Escape:
            logger.debug("Quick commit cancelled: Escape key")
            self.cancelled.emit()
            self.hide()
        else:
            super().keyPressEvent(event)

    def get_message(self) -> str:
        """
        Get current commit message text.

        Returns:
            Current text in message input field (stripped)
        """
        return self.message_input.text().strip()

    def clear_message(self) -> None:
        """Clear commit message input field."""
        self.message_input.clear()
