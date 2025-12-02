"""
Dialog Factory - Reusable dialog components (MA principle extraction).

This module provides factory functions for creating common dialog UI elements,
eliminating ~180 lines of duplicate button/layout creation code across:
- dialogs.py
- github_dialogs.py
- installation_validator_dialog.py
- settings_dialog_helper.py

Author: AsciiDoc Artisan Team
Version: 2.0.9
"""

from collections.abc import Callable
from typing import TypeVar

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Type variable for dialog type hints
T = TypeVar("T", bound=QDialog)


class DialogFactory:
    """Factory for creating common dialog components.

    Follows MA principle: centralized creation logic for reuse.
    """

    @staticmethod
    def create_button_box(
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
        ok_handler: Callable[[], None] | None = None,
        cancel_handler: Callable[[], None] | None = None,
    ) -> QDialogButtonBox:
        """Create standard OK/Cancel button box.

        Args:
            ok_text: Text for the OK button (default: "OK")
            cancel_text: Text for the Cancel button (default: "Cancel")
            ok_handler: Optional callback for OK button click
            cancel_handler: Optional callback for Cancel button click

        Returns:
            QDialogButtonBox with configured buttons and handlers
        """
        button_box = QDialogButtonBox()
        ok_btn = button_box.addButton(ok_text, QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_btn = button_box.addButton(cancel_text, QDialogButtonBox.ButtonRole.RejectRole)

        if ok_handler:
            ok_btn.clicked.connect(ok_handler)
        if cancel_handler:
            cancel_btn.clicked.connect(cancel_handler)

        return button_box

    @staticmethod
    def create_ok_cancel_layout(dialog: QDialog) -> QHBoxLayout:
        """Create horizontal layout with OK/Cancel buttons (legacy pattern).

        This method matches the existing `_create_ok_cancel_buttons()` pattern
        in dialogs.py for backward compatibility.

        Args:
            dialog: Parent dialog for accept/reject connections

        Returns:
            QHBoxLayout with stretch + OK + Cancel buttons
        """
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        return button_layout

    @staticmethod
    def create_dialog_layout(
        title: str,
        content_widget: QWidget | None = None,
        parent: QWidget | None = None,
        min_width: int = 400,
        min_height: int = 300,
    ) -> tuple[QDialog, QVBoxLayout]:
        """Create dialog with standard layout.

        Args:
            title: Window title for the dialog
            content_widget: Optional widget to add to layout
            parent: Parent widget (optional)
            min_width: Minimum dialog width (default: 400)
            min_height: Minimum dialog height (default: 300)

        Returns:
            Tuple of (dialog, layout) for further customization
        """
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(min_width, min_height)

        layout = QVBoxLayout(dialog)

        if content_widget is not None:
            layout.addWidget(content_widget)

        return dialog, layout

    @staticmethod
    def create_form_dialog(
        title: str,
        parent: QWidget | None = None,
        min_width: int = 400,
    ) -> tuple[QDialog, QVBoxLayout, QFormLayout]:
        """Create dialog with form layout for input fields.

        Args:
            title: Window title for the dialog
            parent: Parent widget (optional)
            min_width: Minimum dialog width (default: 400)

        Returns:
            Tuple of (dialog, layout, form) for adding form fields
        """
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setMinimumWidth(min_width)

        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        return dialog, layout, form

    @staticmethod
    def add_buttons_to_dialog(
        dialog: QDialog,
        layout: QVBoxLayout,
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
    ) -> QDialogButtonBox:
        """Add standard buttons to dialog layout.

        Args:
            dialog: Dialog to connect accept/reject signals
            layout: Layout to add buttons to
            ok_text: Text for OK button
            cancel_text: Text for Cancel button

        Returns:
            Created button box
        """
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        if ok_text != "OK":
            button_box.button(QDialogButtonBox.StandardButton.Ok).setText(ok_text)
        if cancel_text != "Cancel":
            button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(cancel_text)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        return button_box

    @staticmethod
    def create_help_label(help_text: str) -> QLabel:
        """Create styled help text label.

        Args:
            help_text: Help/description text

        Returns:
            QLabel with gray, small font styling
        """
        label = QLabel(help_text)
        label.setStyleSheet("color: gray; font-size: 10px;")
        label.setWordWrap(True)
        return label

    @staticmethod
    def create_required_label() -> QLabel:
        """Create standard '* Required field' label.

        Returns:
            QLabel with styled required field note
        """
        label = QLabel("* Required field")
        label.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        return label


# Module-level convenience functions for simpler imports


def create_ok_cancel_buttons(dialog: QDialog) -> QHBoxLayout:
    """Create OK/Cancel buttons layout (convenience function).

    This is a drop-in replacement for _create_ok_cancel_buttons() in dialogs.py.

    Args:
        dialog: Parent dialog for accept/reject connections

    Returns:
        QHBoxLayout with OK/Cancel buttons
    """
    return DialogFactory.create_ok_cancel_layout(dialog)


def create_button_box(
    ok_text: str = "OK",
    cancel_text: str = "Cancel",
    ok_handler: Callable[[], None] | None = None,
    cancel_handler: Callable[[], None] | None = None,
) -> QDialogButtonBox:
    """Create button box (convenience function).

    Args:
        ok_text: Text for OK button
        cancel_text: Text for Cancel button
        ok_handler: Optional OK click handler
        cancel_handler: Optional Cancel click handler

    Returns:
        Configured QDialogButtonBox
    """
    return DialogFactory.create_button_box(ok_text, cancel_text, ok_handler, cancel_handler)
