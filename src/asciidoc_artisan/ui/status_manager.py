"""
Status Manager - Handles status bar and UI feedback for AsciiDoc Artisan.

Implements:
- FR-045: Status bar with contextual messages
- FR-051: Window title (filename with unsaved indicator)
- Document metrics: version, word count, grade level
- AI status indicator

This module manages status messages, window titles, and user notifications,
extracted from main_window.py as part of Phase 2 architectural refactoring.

The StatusManager provides centralized UI feedback management.
"""

import re
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMessageBox

from asciidoc_artisan.core import APP_NAME, DEFAULT_FILENAME

if TYPE_CHECKING:

    from .main_window import AsciiDocEditor


class StatusManager:
    """Manages status display and UI feedback for AsciiDoc Artisan.

    This class encapsulates all status bar, window title, and message dialog
    functionality, plus document metrics display.

    Args:
        editor: Reference to the main AsciiDocEditor window
    """

    def __init__(self, editor: "AsciiDocEditor") -> None:
        """Initialize the StatusManager with a reference to the main editor."""
        self.editor = editor

        # Widgets will be created later when status bar is ready
        self.version_label: Optional[QLabel] = None
        self.word_count_label: Optional[QLabel] = None
        self.grade_level_label: Optional[QLabel] = None
        self.ai_status_label: Optional[QLabel] = None

    def initialize_widgets(self) -> None:
        """Initialize status bar widgets after status bar is created."""
        # Create permanent status bar widgets (right side)
        self.word_count_label = QLabel("Words: 0")
        self.version_label = QLabel("")
        self.grade_level_label = QLabel("Grade: --")
        self.ai_status_label = QLabel("")

        # Style the labels with balanced widths
        # Word count: wider for larger numbers
        self.word_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_count_label.setMinimumWidth(100)

        # Version: narrower, often short
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setMinimumWidth(60)

        # Grade level: medium width
        self.grade_level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grade_level_label.setMinimumWidth(90)

        # AI status: wider for model names
        self.ai_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ai_status_label.setMinimumWidth(150)

        # Add widgets to status bar (right side, permanent)
        # Order: Word Count | Grade Level | AI Status | Version
        self.editor.status_bar.addPermanentWidget(self.word_count_label)
        self.editor.status_bar.addPermanentWidget(self.grade_level_label)
        self.editor.status_bar.addPermanentWidget(self.ai_status_label)
        self.editor.status_bar.addPermanentWidget(self.version_label)

    def update_window_title(self) -> None:
        """Update the window title based on current file and save status."""
        title = APP_NAME

        if self.editor._current_file_path:
            title = f"{APP_NAME} - {self.editor._current_file_path.name}"
        else:
            title = f"{APP_NAME} - {DEFAULT_FILENAME}"

        if self.editor._unsaved_changes:
            title += "*"

        self.editor.setWindowTitle(title)

    def show_message(self, level: str, title: str, text: str) -> None:
        """Show a message dialog to the user.

        Args:
            level: Message level ('info', 'warning', 'critical')
            title: Dialog window title
            text: Message text to display
        """
        icon_map = {
            "info": QMessageBox.Icon.Information,
            "warning": QMessageBox.Icon.Warning,
            "critical": QMessageBox.Icon.Critical,
        }

        msg = QMessageBox(self.editor)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon_map.get(level, QMessageBox.Icon.Information))
        msg.exec()

    def show_status(self, message: str, timeout: int = 0) -> None:
        """Show a message in the status bar.

        Args:
            message: Status message to display
            timeout: Duration in milliseconds (0 = permanent)
        """
        self.editor.status_bar.showMessage(message, timeout)

    def prompt_save_before_action(self, action: str) -> bool:
        """Prompt user to save unsaved changes before an action.

        Args:
            action: Description of the action about to be performed

        Returns:
            True if user wants to proceed, False if cancelled
        """
        if not self.editor._unsaved_changes:
            return True

        reply = QMessageBox.question(
            self.editor,
            "Unsaved Changes",
            f"You have unsaved changes. Save before {action}?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.editor.save_file()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def extract_document_version(self, text: str) -> Optional[str]:
        """Extract document version from AsciiDoc attributes.

        Looks for :revnumber:, :version:, or :rev: attributes.

        Args:
            text: AsciiDoc document content

        Returns:
            Version string or None if not found
        """
        # Try various version attribute patterns
        patterns = [
            r"^:revnumber:\s*(.+)$",
            r"^:version:\s*(.+)$",
            r"^:rev:\s*(.+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def count_words(self, text: str) -> int:
        """Count words in document content.

        Args:
            text: Document content

        Returns:
            Word count
        """
        # Remove AsciiDoc attributes and comments
        text = re.sub(r"^:.*?:.*?$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^//.*?$", "", text, flags=re.MULTILINE)

        # Split on whitespace and count
        words = text.split()
        return len(words)

    def calculate_grade_level(self, text: str) -> float:
        """Calculate Flesch-Kincaid grade level.

        Args:
            text: Document content

        Returns:
            Grade level (e.g., 5.23 = 5th grade reading level)
        """
        # Remove AsciiDoc markup
        text = re.sub(r"^:.*?:.*?$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^//.*?$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\[.*?\]$", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*\*|__|\*|_|`", "", text)

        # Count sentences (. ! ?)
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        num_sentences = len(sentences)

        if num_sentences == 0:
            return 0.0

        # Count words
        words = text.split()
        num_words = len(words)

        if num_words == 0:
            return 0.0

        # Count syllables (simplified: vowel groups)
        num_syllables = 0
        for word in words:
            word = word.lower()
            syllable_count = len(re.findall(r"[aeiouy]+", word))
            # Adjust for silent e
            if word.endswith("e"):
                syllable_count -= 1
            # Minimum 1 syllable per word
            num_syllables += max(1, syllable_count)

        # Flesch-Kincaid Grade Level formula
        # 0.39 * (total words / total sentences) + 11.8 * (total syllables / total words) - 15.59
        grade = (
            0.39 * (num_words / num_sentences)
            + 11.8 * (num_syllables / num_words)
            - 15.59
        )

        return round(max(0.0, grade), 2)

    def update_document_metrics(self) -> None:
        """Update all document metrics in status bar."""
        # Skip if widgets not yet initialized
        if not self.version_label:
            return

        text = self.editor.editor.toPlainText()

        # Update version
        version = self.extract_document_version(text)
        if version:
            self.version_label.setText(f"v{version}")
        else:
            self.version_label.setText("")

        # Update word count
        word_count = self.count_words(text)
        self.word_count_label.setText(f"Words: {word_count}")

        # Update grade level
        if word_count > 0:
            grade = self.calculate_grade_level(text)
            self.grade_level_label.setText(f"Grade: {grade}")
        else:
            self.grade_level_label.setText("Grade: --")

    def set_ai_model(self, model_name: Optional[str] = None) -> None:
        """Set AI model name in status bar.

        Args:
            model_name: Name of the active AI model, "Pandoc" for standard conversion, or None to clear
        """
        if model_name:
            if model_name == "Pandoc":
                # Show Pandoc as the conversion method
                self.ai_status_label.setText("Conversion: Pandoc")
                self.ai_status_label.setToolTip("Using Pandoc for document conversion")
            else:
                # Show Ollama model name
                self.ai_status_label.setText(f"AI: {model_name}")
                self.ai_status_label.setToolTip(f"Ollama model: {model_name}")
        else:
            self.ai_status_label.setText("")
            self.ai_status_label.setToolTip("")

    def set_ai_active(self, active: bool) -> None:
        """Deprecated: Use set_ai_model() instead.

        Args:
            active: True if AI is active, False otherwise
        """
        # This method is kept for backward compatibility but does nothing
        # Use set_ai_model() to set the model name instead
        pass
