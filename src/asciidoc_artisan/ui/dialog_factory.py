"""
Dialog Factory - Reusable dialog components (MA principle extraction).

This module provides factory functions for creating common dialog UI elements,
eliminating ~180 lines of duplicate button/layout creation code across:
- dialogs.py
- github_dialogs.py
- installation_validator_dialog.py
- settings_dialog_helper.py
- telemetry_opt_in_dialog.py

Author: AsciiDoc Artisan Team
Version: 2.1.0
"""

from collections.abc import Callable
from enum import Enum, auto
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

from asciidoc_artisan.ui.style_constants import Colors, Fonts


class ButtonStyle(Enum):
    """Predefined button styles for consistent UI.

    Styles follow Bootstrap-inspired color conventions:
    - SUCCESS: Green, for positive actions (accept, confirm, save)
    - DANGER: Red, for destructive/negative actions (delete, decline, cancel)
    - WARNING: Yellow/Orange, for caution actions
    - PRIMARY: Blue, for primary actions
    - SECONDARY: Gray, for neutral/secondary actions
    """

    SUCCESS = auto()  # Green - positive actions
    DANGER = auto()  # Red - destructive/negative actions
    WARNING = auto()  # Yellow/Orange - caution
    PRIMARY = auto()  # Blue - primary actions
    SECONDARY = auto()  # Gray - neutral actions


class StyledButtonFactory:
    """Factory for creating consistently styled QPushButtons.

    MA principle: Centralizes button styling to eliminate duplicate CSS across dialogs.
    Saves ~50 lines per dialog that uses styled buttons.

    Example:
        >>> btn = StyledButtonFactory.create_button("Save", ButtonStyle.SUCCESS)
        >>> btn = StyledButtonFactory.create_button("Delete", ButtonStyle.DANGER, icon="🗑️")
    """

    # Color palette (uses style_constants for consistency)
    _COLORS = {
        ButtonStyle.SUCCESS: (Colors.SUCCESS, Colors.SUCCESS_HOVER),
        ButtonStyle.DANGER: (Colors.DANGER, Colors.DANGER_HOVER),
        ButtonStyle.WARNING: (Colors.WARNING, Colors.WARNING_HOVER),
        ButtonStyle.PRIMARY: (Colors.PRIMARY, Colors.PRIMARY_HOVER),
        ButtonStyle.SECONDARY: (Colors.SECONDARY, Colors.SECONDARY_HOVER),
    }

    # Text colors (white for most, dark for warning)
    _TEXT_COLORS = {
        ButtonStyle.SUCCESS: Colors.TEXT_LIGHT,
        ButtonStyle.DANGER: Colors.TEXT_LIGHT,
        ButtonStyle.WARNING: Colors.WARNING_TEXT,
        ButtonStyle.PRIMARY: Colors.TEXT_LIGHT,
        ButtonStyle.SECONDARY: Colors.TEXT_LIGHT,
    }

    @classmethod
    def create_button(
        cls,
        text: str,
        style: ButtonStyle,
        icon: str = "",
        bold: bool = True,
        padding: str = "10px 20px",
    ) -> QPushButton:
        """Create a styled QPushButton.

        Args:
            text: Button label text
            style: ButtonStyle enum value
            icon: Optional icon prefix (emoji or text)
            bold: Whether text should be bold (default: True)
            padding: CSS padding value (default: "10px 20px")

        Returns:
            Styled QPushButton ready to use
        """
        label = f"{icon} {text}" if icon else text
        button = QPushButton(label.strip())

        normal_color, hover_color = cls._COLORS[style]
        text_color = cls._TEXT_COLORS[style]
        font_weight = "bold" if bold else "normal"

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {normal_color};
                color: {text_color};
                padding: {padding};
                font-weight: {font_weight};
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

        return button

    @classmethod
    def create_success_button(cls, text: str, icon: str = "✓") -> QPushButton:
        """Create a green success button (convenience method)."""
        return cls.create_button(text, ButtonStyle.SUCCESS, icon)

    @classmethod
    def create_danger_button(cls, text: str, icon: str = "✗") -> QPushButton:
        """Create a red danger button (convenience method)."""
        return cls.create_button(text, ButtonStyle.DANGER, icon)

    @classmethod
    def create_secondary_button(cls, text: str, icon: str = "") -> QPushButton:
        """Create a gray secondary button (convenience method)."""
        return cls.create_button(text, ButtonStyle.SECONDARY, icon, bold=False)


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
        label.setStyleSheet(Fonts.STYLE_MUTED)
        label.setWordWrap(True)
        return label

    @staticmethod
    def create_required_label() -> QLabel:
        """Create standard '* Required field' label.

        Returns:
            QLabel with styled required field note
        """
        label = QLabel("* Required field")
        label.setStyleSheet(f"QLabel {{ {Fonts.STYLE_REQUIRED} }}")
        return label


# === BASE SETTINGS DIALOG ===


class BaseSettingsDialog(QDialog):
    """Base class for settings dialogs with common structure.

    MA principle: Eliminates duplicate code across settings dialogs.
    Provides consistent structure:
    - Window title and minimum width
    - Optional header section
    - Settings content (implemented by subclass)
    - OK/Cancel buttons

    Subclasses should override:
    - _get_title(): Return window title
    - _get_header_text(): Return (title, description) tuple or None
    - _create_content(layout): Add settings widgets to layout

    Example:
        class MySettingsDialog(BaseSettingsDialog):
            def _get_title(self) -> str:
                return "My Settings"

            def _get_header_text(self) -> tuple[str, str] | None:
                return ("Configure Settings", "Adjust these options to customize behavior.")

            def _create_content(self, layout: QVBoxLayout) -> None:
                layout.addWidget(self.my_checkbox)
    """

    def __init__(self, parent: QWidget | None = None, min_width: int = 500) -> None:
        """Initialize base settings dialog.

        Args:
            parent: Parent widget (optional)
            min_width: Minimum dialog width (default: 500)
        """
        super().__init__(parent)
        self._min_width = min_width
        self._init_base_ui()

    def _get_title(self) -> str:
        """Return window title. Override in subclass."""
        return "Settings"

    def _get_header_text(self) -> tuple[str, str] | None:
        """Return header (title, description) tuple or None to skip header.

        Override in subclass to customize header.
        """
        return None

    def _create_content(self, layout: QVBoxLayout) -> None:
        """Add settings widgets to layout. Override in subclass."""
        pass

    def _init_base_ui(self) -> None:
        """Initialize the common UI structure."""
        self.setWindowTitle(self._get_title())
        self.setMinimumWidth(self._min_width)

        layout = QVBoxLayout(self)

        # Optional header section
        header = self._get_header_text()
        if header:
            self._add_header(layout, header[0], header[1])

        # Subclass content
        self._create_content(layout)

        # Dialog buttons
        layout.addLayout(DialogFactory.create_ok_cancel_layout(self))

    def _add_header(self, layout: QVBoxLayout, title: str, description: str) -> None:
        """Add styled header section to layout."""
        header_label = QLabel(title)
        header_label.setStyleSheet(f"QLabel {{ {Fonts.STYLE_HEADER} }}")
        layout.addWidget(header_label)

        if description:
            info_label = QLabel(description)
            info_label.setWordWrap(True)
            info_label.setStyleSheet(f"QLabel {{ {Fonts.STYLE_INFO} }}")
            layout.addWidget(info_label)

    def create_info_label(self, text: str) -> QLabel:
        """Create an info/help label with standard styling.

        Args:
            text: Information text to display

        Returns:
            Styled QLabel
        """
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"QLabel {{ {Fonts.STYLE_INFO} }}")
        return label

    def create_status_label(self, text: str, status: str = "normal") -> QLabel:
        """Create a status label with color based on status.

        Args:
            text: Status text to display
            status: One of "success", "warning", "error", "normal"

        Returns:
            Styled QLabel
        """
        label = QLabel(text)
        colors = {
            "success": Colors.SUCCESS,
            "warning": Colors.WARNING,
            "error": Colors.DANGER,
            "normal": Colors.TEXT_MUTED,
        }
        color = colors.get(status, Colors.TEXT_MUTED)
        label.setStyleSheet(f"QLabel {{ color: {color}; font-size: 10pt; }}")
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
