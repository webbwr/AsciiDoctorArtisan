"""
Status Bar Label Updater - Updates status bar labels with document metrics.

Extracted from StatusManager to reduce class size (MA principle).
Handles UI label updates for version, word count, and grade level.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .status_manager import StatusManager


class StatusBarLabelUpdater:
    """
    Updates status bar labels with document metrics.

    This class was extracted from StatusManager to reduce class size
    per MA principle (414→~336 lines).

    Handles:
    - Version label updates with tooltips
    - Word count label updates with statistics
    - Grade level label updates with readability info
    """

    def __init__(self, status_manager: "StatusManager") -> None:
        """
        Initialize the label updater.

        Args:
            status_manager: StatusManager instance to update labels for
        """
        self.status_manager = status_manager

    def update_version_label(self, text: str) -> None:
        """
        Update version label with document version.

        Args:
            text: Document text
        """
        version = self.status_manager.extract_document_version(text)
        if version:
            self.status_manager.version_label.setText(f"v{version}")
            self.status_manager.version_label.setToolTip(
                f"Document Version: {version}\n"
                "Detected from AsciiDoc attributes (:version:, :revnumber:, :rev:) or version text"
            )
        else:
            self.status_manager.version_label.setText("None")
            self.status_manager.version_label.setToolTip(
                "No document version detected\n"
                "Add version using AsciiDoc attributes:\n"
                "  :version: 1.0.0\n"
                "  :revnumber: 1.0"
            )

    def update_word_count_label(self, text: str, word_count: int) -> None:
        """
        Update word count label with document statistics.

        Args:
            text: Document text
            word_count: Word count
        """
        char_count = len(text)
        line_count = len(text.splitlines())
        self.status_manager.word_count_label.setText(f"Words: {word_count}")
        self.status_manager.word_count_label.setToolTip(
            f"Document Statistics:\n"
            f"  Words: {word_count:,}\n"
            f"  Characters: {char_count:,}\n"
            f"  Lines: {line_count:,}\n"
            "(Excludes code blocks and comments)"
        )

    def update_grade_level_label(self, text: str, word_count: int) -> None:
        """
        Update grade level label with readability metrics.

        Args:
            text: Document text
            word_count: Word count
        """
        if word_count > 0:
            grade = self.status_manager.calculate_grade_level(text)
            self.status_manager.grade_level_label.setText(f"Grade: {grade}")

            difficulty, audience = self.status_manager._interpret_grade_level(grade)

            self.status_manager.grade_level_label.setToolTip(
                f"Reading Grade Level: {grade}\n"
                f"Difficulty: {difficulty}\n"
                f"Target Audience: {audience}\n\n"
                "Based on Flesch-Kincaid readability formula\n"
                "(Average sentence length + syllables per word)"
            )
        else:
            self.status_manager.grade_level_label.setText("Grade: --")
            self.status_manager.grade_level_label.setToolTip(
                "Reading Grade Level: Not available\n(Document has no content to analyze)"
            )
