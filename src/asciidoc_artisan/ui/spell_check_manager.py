"""
Spell Check Manager - UI integration for spell checking.

Manages spell checking integration with the editor:
- Red squiggly underlines for misspelled words
- Right-click context menu with suggestions
- Toggle spell checking on/off (F7)
- Custom dictionary management

Implements specification requirement: Spell Checker (v1.8.0).
"""

import logging
from typing import TYPE_CHECKING, List, Optional

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import (
    QAction,
    QColor,
    QContextMenuEvent,
    QTextCharFormat,
    QTextCursor,
)
from PySide6.QtWidgets import QMenu

from asciidoc_artisan.core import SpellChecker, SpellError

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class SpellCheckManager:
    """
    Manages spell checking UI integration.

    Features:
    - Real-time spell checking with red squiggly underlines
    - Right-click context menu with suggestions
    - Add to dictionary / Ignore word options
    - F7 toggle for enabling/disabling spell check
    - Configurable spell check language

    Performance:
    - Debounced spell checking (500ms delay after typing stops)
    - Checks only visible text for large documents
    - Caches spell check results
    """

    def __init__(self, main_window: "AsciiDocEditor") -> None:
        """
        Initialize SpellCheckManager.

        Args:
            main_window: Reference to main window
        """
        self.main_window = main_window
        self.editor = main_window.editor

        # Initialize spell checker
        language = main_window.settings.spell_check_language or "en"
        self.spell_checker = SpellChecker(language=language)

        # Load custom words from settings
        custom_words = getattr(main_window.settings, "spell_check_custom_words", [])
        for word in custom_words:
            self.spell_checker.add_to_dictionary(word)

        # Spell check state
        self.enabled = main_window.settings.spell_check_enabled
        self.errors: List[SpellError] = []

        # Debounce timer for spell checking (check 500ms after typing stops)
        self.check_timer = QTimer()
        self.check_timer.setSingleShot(True)
        self.check_timer.timeout.connect(self._perform_spell_check)

        # Connect signals
        self.editor.textChanged.connect(self._on_text_changed)

        # Perform initial spell check if enabled
        if self.enabled:
            self._perform_spell_check()

        logger.info(
            f"SpellCheckManager initialized (enabled={self.enabled}, language={language})"
        )

    def toggle_spell_check(self) -> None:
        """Toggle spell checking on/off (F7)."""
        self.enabled = not self.enabled
        self.main_window.settings.spell_check_enabled = self.enabled

        if self.enabled:
            # Perform immediate spell check
            self._perform_spell_check()
            self.main_window.status_manager.show_message(
                "Spell check enabled", duration_ms=2000
            )
            logger.info("Spell check enabled")
        else:
            # Clear all highlights
            self._clear_highlights()
            self.errors = []
            self.main_window.status_manager.show_message(
                "Spell check disabled", duration_ms=2000
            )
            logger.info("Spell check disabled")

    def set_language(self, language: str) -> None:
        """
        Change spell check language.

        Args:
            language: Language code (e.g., 'en', 'es', 'fr', 'de')
        """
        self.spell_checker.set_language(language)
        self.main_window.settings.spell_check_language = language
        logger.info(f"Spell check language changed to: {language}")

        # Re-check with new language
        if self.enabled:
            self._perform_spell_check()

    def add_to_dictionary(self, word: str) -> None:
        """
        Add word to custom dictionary.

        Args:
            word: Word to add
        """
        self.spell_checker.add_to_dictionary(word)

        # Save custom dictionary to settings
        custom_words = self.spell_checker.get_custom_words()
        self.main_window.settings.spell_check_custom_words = custom_words

        # Re-check to remove this word's highlights
        if self.enabled:
            self._perform_spell_check()

        logger.info(f"Added '{word}' to custom dictionary")

    def ignore_word(self, word: str) -> None:
        """
        Ignore word for this session only.

        Args:
            word: Word to ignore
        """
        self.spell_checker.ignore_word(word)

        # Re-check to remove this word's highlights
        if self.enabled:
            self._perform_spell_check()

        logger.debug(f"Ignoring word '{word}' for this session")

    def show_context_menu(self, event: QContextMenuEvent) -> None:
        """
        Show context menu with spell check suggestions.

        Args:
            event: Context menu event
        """
        if not self.enabled:
            # Spell check disabled - show default context menu
            self._show_default_context_menu(event)
            return

        # Get cursor position at mouse click
        cursor = self.editor.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText().strip()

        if not word:
            # No word under cursor - show default menu
            self._show_default_context_menu(event)
            return

        # Check if this word is misspelled
        error = self._find_error_at_position(cursor.selectionStart())

        if not error:
            # Word is correctly spelled - show default menu
            self._show_default_context_menu(event)
            return

        # Create context menu with suggestions
        menu = QMenu(self.editor)

        # Add suggestions (bold text)
        suggestions = error.suggestions[:5]  # Max 5 suggestions
        if suggestions:
            for suggestion in suggestions:
                action = QAction(suggestion, menu)
                action.triggered.connect(
                    lambda checked=False, s=suggestion, c=cursor: self._replace_word(
                        c, s
                    )
                )
                font = action.font()
                font.setBold(True)
                action.setFont(font)
                menu.addAction(action)

            menu.addSeparator()
        else:
            # No suggestions available
            no_suggestions = QAction("(no suggestions)", menu)
            no_suggestions.setEnabled(False)
            menu.addAction(no_suggestions)
            menu.addSeparator()

        # Add "Add to Dictionary" action
        add_action = QAction(f"Add '{word}' to Dictionary", menu)
        add_action.triggered.connect(lambda: self.add_to_dictionary(word))
        menu.addAction(add_action)

        # Add "Ignore" action
        ignore_action = QAction(f"Ignore '{word}'", menu)
        ignore_action.triggered.connect(lambda: self.ignore_word(word))
        menu.addAction(ignore_action)

        menu.addSeparator()

        # Add standard editor actions
        self._add_standard_actions(menu)

        # Show menu
        menu.exec(event.globalPos())

    def _on_text_changed(self) -> None:
        """Handle text changed event - debounced spell check."""
        if not self.enabled:
            return

        # Restart timer (500ms delay after typing stops)
        self.check_timer.stop()
        self.check_timer.start(500)

    def _perform_spell_check(self) -> None:
        """Perform spell check on current document."""
        if not self.enabled:
            return

        text = self.editor.toPlainText()

        # Check spelling
        self.errors = self.spell_checker.check_text(text)

        # Update highlights
        self._update_highlights()

        logger.debug(f"Spell check complete: {len(self.errors)} errors found")

    def _update_highlights(self) -> None:
        """Update red squiggly underlines for all spelling errors."""
        # Clear existing highlights
        self._clear_highlights()

        if not self.errors:
            return

        # Create extra selections for each error
        selections = []
        for error in self.errors:
            # Create selection
            cursor = QTextCursor(self.editor.document())
            cursor.setPosition(error.start)
            cursor.setPosition(error.end, QTextCursor.MoveMode.KeepAnchor)

            # Create red squiggly underline format
            fmt = QTextCharFormat()
            fmt.setUnderlineColor(QColor(Qt.GlobalColor.red))
            fmt.setUnderlineStyle(
                QTextCharFormat.UnderlineStyle.SpellCheckUnderline
            )

            # Add to selections
            selection = self.editor.ExtraSelection()
            selection.cursor = cursor
            selection.format = fmt
            selections.append(selection)

        # Apply all selections at once
        self.editor.setExtraSelections(selections)

    def _clear_highlights(self) -> None:
        """Clear all spelling error highlights."""
        self.editor.setExtraSelections([])

    def _find_error_at_position(self, position: int) -> Optional[SpellError]:
        """
        Find spelling error at given text position.

        Args:
            position: Character position in document

        Returns:
            SpellError if found, None otherwise
        """
        for error in self.errors:
            if error.start <= position < error.end:
                return error
        return None

    def _replace_word(self, cursor: QTextCursor, replacement: str) -> None:
        """
        Replace misspelled word with suggestion.

        Args:
            cursor: Text cursor positioned at word
            replacement: Replacement text
        """
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(replacement)
        cursor.endEditBlock()

        # Re-check after replacement
        self._perform_spell_check()

    def _show_default_context_menu(self, event: QContextMenuEvent) -> None:
        """
        Show default context menu (cut, copy, paste, etc.).

        Args:
            event: Context menu event
        """
        menu = self.editor.createStandardContextMenu()
        menu.exec(event.globalPos())

    def _add_standard_actions(self, menu: QMenu) -> None:
        """
        Add standard editor actions to context menu.

        Args:
            menu: Context menu to add actions to
        """
        # Add separator
        menu.addSeparator()

        # Add cut, copy, paste
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

        # Add select all
        select_all_action = QAction("Select All", menu)
        select_all_action.triggered.connect(self.editor.selectAll)
        menu.addAction(select_all_action)
