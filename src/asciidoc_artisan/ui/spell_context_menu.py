"""
Spell Context Menu - Context menu handling for spell check.

Provides right-click context menu with spell suggestions.
"""

from typing import TYPE_CHECKING, Any

from PySide6.QtGui import QAction, QContextMenuEvent, QTextCursor
from PySide6.QtWidgets import QMenu

if TYPE_CHECKING:
    from .spell_check_manager import SpellCheckManager


class SpellContextMenu:
    """Handles context menu for spell check suggestions."""

    def __init__(self, manager: "SpellCheckManager") -> None:
        """Initialize context menu handler."""
        self.manager = manager
        self.editor = manager.editor

    def get_word_and_error_at_position(self, event: QContextMenuEvent) -> tuple[str, QTextCursor, Any] | None:
        """Get word and spell error at cursor position."""
        cursor = self.editor.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText().strip()

        if not word:
            return None

        error = self.manager._find_error_at_position(cursor.selectionStart())
        if not error:
            return None

        return (word, cursor, error)

    def add_suggestion_actions(self, menu: QMenu, suggestions: list[str], cursor: QTextCursor) -> None:
        """Add suggestion actions to context menu."""
        if suggestions:
            for suggestion in suggestions:
                action = QAction(suggestion, menu)
                action.triggered.connect(lambda checked=False, s=suggestion, c=cursor: self.manager._replace_word(c, s))
                font = action.font()
                font.setBold(True)
                action.setFont(font)
                menu.addAction(action)
            menu.addSeparator()
        else:
            no_suggestions = QAction("(no suggestions)", menu)
            no_suggestions.setEnabled(False)
            menu.addAction(no_suggestions)
            menu.addSeparator()

    def add_dictionary_actions(self, menu: QMenu, word: str) -> None:
        """Add dictionary management actions to context menu."""
        add_action = QAction(f"Add '{word}' to Dictionary", menu)
        add_action.triggered.connect(lambda: self.manager.add_to_dictionary(word))
        menu.addAction(add_action)

        ignore_action = QAction(f"Ignore '{word}'", menu)
        ignore_action.triggered.connect(lambda: self.manager.ignore_word(word))
        menu.addAction(ignore_action)
        menu.addSeparator()

    def add_standard_actions(self, menu: QMenu) -> None:
        """Add standard editor actions to context menu."""
        menu.addSeparator()

        cut_action = QAction("Cut", menu)
        cut_action.triggered.connect(self.editor.cut)
        cut_action.setEnabled(self.editor.textCursor().hasSelection())
        menu.addAction(cut_action)

        copy_action = QAction("Copy", menu)
        copy_action.triggered.connect(self.editor.copy)
        copy_action.setEnabled(self.editor.textCursor().hasSelection())
        menu.addAction(copy_action)

        paste_action = QAction("Paste", menu)
        paste_action.triggered.connect(self.editor.paste)
        menu.addAction(paste_action)

        menu.addSeparator()

        select_all_action = QAction("Select All", menu)
        select_all_action.triggered.connect(self.editor.selectAll)
        menu.addAction(select_all_action)

    def show_default_context_menu(self, event: QContextMenuEvent) -> None:
        """Show default context menu."""
        menu = self.editor.createStandardContextMenu()
        menu.exec(event.globalPos())

    def show(self, event: QContextMenuEvent) -> None:
        """Show context menu with spell check suggestions."""
        if not self.manager.enabled:
            self.show_default_context_menu(event)
            return

        result = self.get_word_and_error_at_position(event)
        if not result:
            self.show_default_context_menu(event)
            return

        word, cursor, error = result

        menu = QMenu(self.editor)
        self.add_suggestion_actions(menu, error.suggestions[:5], cursor)
        self.add_dictionary_actions(menu, word)
        self.add_standard_actions(menu)
        menu.exec(event.globalPos())
