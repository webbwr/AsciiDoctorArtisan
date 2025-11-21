"""
Status Bar Widget Factory - Creates and configures status bar widgets.

Extracted from StatusManager to reduce class size (MA principle).
Handles widget creation, styling, and layout for the status bar.
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton

if TYPE_CHECKING:  # pragma: no cover
    from .status_manager import StatusManager


class StatusBarWidgetFactory:
    """
    Factory for creating and configuring status bar widgets.

    This class was extracted from StatusManager to reduce class size
    per MA principle (451→~390 lines).

    Handles:
    - Cancel button creation and setup
    - Status label creation and configuration
    - Widget styling and tooltips
    - Status bar layout
    """

    def __init__(self, status_manager: "StatusManager") -> None:
        """
        Initialize the widget factory.

        Args:
            status_manager: StatusManager instance to configure widgets for
        """
        self.status_manager = status_manager

    def create_cancel_button(self) -> QPushButton:
        """
        Create and configure the cancel button.

        Returns:
            Configured QPushButton for cancellation
        """
        cancel_button = QPushButton("✕ Cancel")
        cancel_button.setMaximumWidth(80)
        cancel_button.setToolTip("Cancel current operation")
        cancel_button.clicked.connect(self.status_manager._on_cancel_clicked)
        cancel_button.hide()  # Hidden by default
        return cancel_button

    def create_word_count_label(self) -> QLabel:
        """
        Create and configure the word count label.

        Returns:
            Configured QLabel for word count display
        """
        label = QLabel("Words: 0")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setMinimumWidth(100)
        label.setToolTip("Document word count (excludes code blocks and comments)")
        return label

    def create_version_label(self) -> QLabel:
        """
        Create and configure the version label.

        Returns:
            Configured QLabel for version display
        """
        label = QLabel("")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setMinimumWidth(60)
        label.setToolTip("Document version (extracted from :version: or :revnumber: attributes)")
        return label

    def create_grade_level_label(self) -> QLabel:
        """
        Create and configure the grade level label.

        Returns:
            Configured QLabel for grade level display
        """
        label = QLabel("Grade: --")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setMinimumWidth(90)
        label.setToolTip("Reading grade level (Flesch-Kincaid readability score)")
        return label

    def create_git_status_label(self) -> QLabel:
        """
        Create and configure the Git status label.

        Returns:
            Configured QLabel for Git status display
        """
        label = QLabel("")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setMinimumWidth(80)
        label.setToolTip("Git repository status (click for details)")
        return label

    def create_ai_status_label(self) -> QLabel:
        """
        Create and configure the AI status label.

        Returns:
            Configured QLabel for AI status display
        """
        label = QLabel("")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setMinimumWidth(150)
        # Tooltip set dynamically in set_ai_model()
        return label

    def initialize_widgets(self) -> None:
        """
        Initialize all status bar widgets and add them to the status bar.

        Creates cancel button, status labels, and adds them to the status bar
        in the correct order with appropriate styling.
        """
        # Create cancel button (left side, shown only during operations)
        self.status_manager.cancel_button = self.create_cancel_button()

        # Add cancel button to left side of status bar
        self.status_manager.editor.status_bar.addWidget(self.status_manager.cancel_button)

        # Create permanent status bar widgets (right side)
        self.status_manager.word_count_label = self.create_word_count_label()
        self.status_manager.version_label = self.create_version_label()
        self.status_manager.grade_level_label = self.create_grade_level_label()
        self.status_manager.git_status_label = self.create_git_status_label()
        self.status_manager.ai_status_label = self.create_ai_status_label()

        # Add widgets to status bar (right side, permanent)
        # Order: Version | Word Count | Grade Level | Git | AI Status
        self.status_manager.editor.status_bar.addPermanentWidget(self.status_manager.version_label)
        self.status_manager.editor.status_bar.addPermanentWidget(self.status_manager.word_count_label)
        self.status_manager.editor.status_bar.addPermanentWidget(self.status_manager.grade_level_label)
        self.status_manager.editor.status_bar.addPermanentWidget(self.status_manager.git_status_label)
        self.status_manager.editor.status_bar.addPermanentWidget(self.status_manager.ai_status_label)
