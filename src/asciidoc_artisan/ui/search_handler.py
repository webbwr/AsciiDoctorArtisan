"""
Search Handler - Manages find/replace operations in the editor.

Extracted from main_window.py to reduce class size (MA principle).
Handles search highlighting, match navigation, and replace operations.
"""

import logging
from typing import TYPE_CHECKING, Any, Protocol

from PySide6.QtCore import Slot
from PySide6.QtGui import QColor, QTextCursor
from PySide6.QtWidgets import QMessageBox, QTextEdit

if TYPE_CHECKING:
    from asciidoc_artisan.core.search_engine import SearchMatch

logger = logging.getLogger(__name__)


class SearchContext(Protocol):
    """Protocol for search context (avoid circular imports)."""

    editor: Any
    find_bar: Any
    search_engine: Any
    status_manager: Any

    def __getattr__(self, name: str) -> Any:  # pragma: no cover
        """Allow access to any attribute."""
        ...


class SearchHandler:
    """
    Find/Replace operations handler.

    This class was extracted from AsciiDocEditor to reduce class size
    per MA principle (~350 lines extracted).

    Handles:
    - Live search with highlighting
    - Find next/previous navigation
    - Single replace operation
    - Replace all with confirmation
    - Search highlighting management
    """

    def __init__(self, ctx: SearchContext) -> None:
        """
        Initialize search handler.

        Args:
            ctx: Search context providing editor, find_bar, search_engine
        """
        self.ctx = ctx

    @Slot(str, bool)
    def handle_search_requested(self, search_text: str, case_sensitive: bool) -> None:
        """Handle search text changes from find bar (live search).

        Args:
            search_text: Text to search for
            case_sensitive: Whether search is case-sensitive
        """
        if not search_text:
            self.clear_search_highlighting()
            self.ctx.find_bar.update_match_count(0, 0)
            return

        try:
            matches = self.ctx.search_engine.find_all(search_text, case_sensitive=case_sensitive)

            if matches:
                cursor = self.ctx.editor.textCursor()
                current_pos = cursor.position()

                # Find first match at or after cursor position
                current_match_index = 0
                for i, match in enumerate(matches):
                    if match.start >= current_pos:
                        current_match_index = i
                        break
                else:
                    current_match_index = len(matches) - 1

                self.ctx.find_bar.update_match_count(current_match_index + 1, len(matches))
                self.highlight_search_matches(matches)

                if matches:
                    self.select_match(matches[current_match_index])
            else:
                self.ctx.find_bar.update_match_count(0, 0)
                self.ctx.find_bar.set_not_found_style()
                self.clear_search_highlighting()

        except Exception as e:
            logger.error(f"Search error: {e}")
            self.ctx.find_bar.update_match_count(0, 0)

    @Slot()
    def handle_find_next(self) -> None:
        """Navigate to next search match."""
        search_text = self.ctx.find_bar.get_search_text()
        if not search_text:
            return

        try:
            cursor = self.ctx.editor.textCursor()
            current_pos = cursor.position()

            match = self.ctx.search_engine.find_next(
                search_text,
                start_offset=current_pos,
                case_sensitive=self.ctx.find_bar.is_case_sensitive(),
                wrap_around=True,
            )

            if match:
                self.select_match(match)
                matches = self.ctx.search_engine.find_all(
                    search_text, case_sensitive=self.ctx.find_bar.is_case_sensitive()
                )
                match_index = matches.index(match) if match in matches else 0
                self.ctx.find_bar.update_match_count(match_index + 1, len(matches))

        except Exception as e:
            logger.error(f"Find next error: {e}")

    @Slot()
    def handle_find_previous(self) -> None:
        """Navigate to previous search match."""
        search_text = self.ctx.find_bar.get_search_text()
        if not search_text:
            return

        try:
            cursor = self.ctx.editor.textCursor()
            current_pos = cursor.selectionStart()

            match = self.ctx.search_engine.find_previous(
                search_text,
                start_offset=current_pos,
                case_sensitive=self.ctx.find_bar.is_case_sensitive(),
                wrap_around=True,
            )

            if match:
                self.select_match(match)
                matches = self.ctx.search_engine.find_all(
                    search_text, case_sensitive=self.ctx.find_bar.is_case_sensitive()
                )
                match_index = matches.index(match) if match in matches else 0
                self.ctx.find_bar.update_match_count(match_index + 1, len(matches))

        except Exception as e:
            logger.error(f"Find previous error: {e}")

    @Slot()
    def handle_find_closed(self) -> None:
        """Handle find bar being closed."""
        self.clear_search_highlighting()
        self.ctx.editor.setFocus()
        logger.debug("Find bar closed, focus returned to editor")

    @Slot(str)
    def handle_replace(self, replace_text: str) -> None:
        """Replace current match and find next.

        Args:
            replace_text: Text to replace with
        """
        search_text = self.ctx.find_bar.get_search_text()
        if not search_text:
            return

        try:
            cursor = self.ctx.editor.textCursor()
            if not cursor.hasSelection():
                self.handle_find_next()
                cursor = self.ctx.editor.textCursor()
                if not cursor.hasSelection():
                    return

            selected_text = cursor.selectedText()
            case_sensitive = self.ctx.find_bar.is_case_sensitive()

            if case_sensitive:
                matches = selected_text == search_text
            else:
                matches = selected_text.lower() == search_text.lower()

            if matches:
                cursor.insertText(replace_text)
                self.ctx.editor.setTextCursor(cursor)
                self.ctx.search_engine.set_text(self.ctx.editor.toPlainText())
                self.handle_find_next()
                logger.info(f"Replaced '{search_text}' with '{replace_text}'")
            else:
                self.handle_find_next()

        except Exception as e:
            logger.error(f"Replace error: {e}")

    @Slot(str)
    def handle_replace_all(self, replace_text: str) -> None:
        """
        Replace all occurrences after confirmation.

        MA principle: Delegates to helper methods for clarity.

        Args:
            replace_text: Text to replace with
        """
        search_text = self.ctx.find_bar.get_search_text()
        if not search_text:
            return

        try:
            match_count = self._count_replace_matches(search_text)
            if match_count is None:
                return

            if not self._confirm_replace_all(search_text, replace_text, match_count):
                return

            self._execute_replace_all(search_text, replace_text)

        except Exception as e:
            logger.error(f"Replace all error: {e}")
            self.ctx.status_manager.show_status(f"Replace failed: {e}", 3000)

    def _count_replace_matches(self, search_text: str) -> int | None:
        """
        Count matches for replacement.

        Args:
            search_text: Text to search for

        Returns:
            Match count if matches found, None if no matches
        """
        matches = self.ctx.search_engine.find_all(search_text, case_sensitive=self.ctx.find_bar.is_case_sensitive())
        match_count = len(matches)

        if match_count == 0:
            self.ctx.status_manager.show_status("No matches to replace", 2000)
            return None

        return match_count

    def _confirm_replace_all(self, search_text: str, replace_text: str, match_count: int) -> bool:
        """
        Show confirmation dialog for replace all operation.

        Args:
            search_text: Text being searched
            replace_text: Replacement text
            match_count: Number of matches to replace

        Returns:
            True if user confirmed, False otherwise
        """
        reply = QMessageBox.question(
            self.ctx.editor,
            "Replace All",
            f"Replace {match_count} occurrence(s) of '{search_text}' with '{replace_text}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _execute_replace_all(self, search_text: str, replace_text: str) -> None:
        """
        Execute replace all and update editor state.

        Args:
            search_text: Text to search for
            replace_text: Text to replace with
        """
        new_text, count = self.ctx.search_engine.replace_all(
            search_text,
            replace_text,
            case_sensitive=self.ctx.find_bar.is_case_sensitive(),
        )

        cursor = self.ctx.editor.textCursor()
        cursor_pos = cursor.position()

        self.ctx.editor.setPlainText(new_text)

        cursor.setPosition(min(cursor_pos, len(new_text)))
        self.ctx.editor.setTextCursor(cursor)

        self.clear_search_highlighting()
        self.ctx.find_bar.update_match_count(0, 0)
        self.ctx.status_manager.show_status(f"Replaced {count} occurrence(s)", 3000)

        logger.info(f"Replaced all: {count} occurrences of '{search_text}' with '{replace_text}'")

    def select_match(self, match: "SearchMatch") -> None:
        """Select a search match in the editor.

        Args:
            match: SearchMatch object with start/end positions
        """
        cursor = self.ctx.editor.textCursor()
        cursor.setPosition(match.start)
        cursor.setPosition(match.end, QTextCursor.MoveMode.KeepAnchor)
        self.ctx.editor.setTextCursor(cursor)
        self.ctx.editor.ensureCursorVisible()

    def highlight_search_matches(self, matches: list["SearchMatch"]) -> None:
        """Highlight all search matches in the editor.

        Args:
            matches: List of SearchMatch objects
        """
        search_selections = []
        for match in matches:
            selection = QTextEdit.ExtraSelection()
            cursor = self.ctx.editor.textCursor()
            cursor.setPosition(match.start)
            cursor.setPosition(match.end, QTextCursor.MoveMode.KeepAnchor)

            selection.format.setBackground(QColor(255, 255, 0, 80))  # Light yellow
            selection.cursor = cursor
            search_selections.append(selection)

        self.ctx.editor.search_selections = search_selections
        self.apply_combined_selections()

    def clear_search_highlighting(self) -> None:
        """Clear all search highlighting from the editor."""
        self.ctx.editor.search_selections = []
        self.apply_combined_selections()
        self.ctx.find_bar.clear_not_found_style()

    def apply_combined_selections(self) -> None:
        """Combine search and spell check selections and apply to editor."""
        combined = list(getattr(self.ctx.editor, "search_selections", []))
        spell_sels = getattr(self.ctx.editor, "spell_check_selections", [])
        combined.extend(spell_sels)
        self.ctx.editor.setExtraSelections(combined)
