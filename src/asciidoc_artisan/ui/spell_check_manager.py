"""
Spell Check Manager - UI integration for spell checking.

Manages spell checking integration with the editor:
- Red squiggly underlines for misspelled words
- Right-click context menu with suggestions
- Toggle spell checking on/off (F7)
- Custom dictionary management
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QContextMenuEvent, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QTextEdit

from asciidoc_artisan.core import SpellChecker, SpellError

if TYPE_CHECKING:
    from .main_window import AsciiDocEditor

logger = logging.getLogger(__name__)


class SpellCheckManager:
    """Manages spell checking UI integration."""

    def __init__(self, main_window: "AsciiDocEditor") -> None:
        """Initialize SpellCheckManager."""
        self.main_window = main_window
        self.editor = main_window.editor

        # Initialize spell checker
        language = main_window._settings.spell_check_language or "en"
        self.spell_checker = SpellChecker(language=language)

        # Load custom words from settings
        custom_words = getattr(main_window._settings, "spell_check_custom_words", [])
        for word in custom_words:
            self.spell_checker.add_to_dictionary(word)

        # Spell check state
        self.enabled = main_window._settings.spell_check_enabled
        self.errors: list[SpellError] = []

        # Context menu handler (MA extraction)
        from .spell_context_menu import SpellContextMenu

        self._context_menu = SpellContextMenu(self)

        # Debounce timer for spell checking
        self.check_timer = QTimer()
        self.check_timer.setSingleShot(True)
        self.check_timer.timeout.connect(self._perform_spell_check)

        # Connect signals
        self.editor.textChanged.connect(self._on_text_changed)

        # Perform initial spell check if enabled
        if self.enabled:
            self._perform_spell_check()

        logger.info(f"SpellCheckManager initialized (enabled={self.enabled}, language={language})")

    def toggle_spell_check(self) -> None:
        """Toggle spell checking on/off (F7)."""
        self.enabled = not self.enabled
        self.main_window._settings.spell_check_enabled = self.enabled
        self._update_menu_text()

        if self.enabled:
            self._perform_spell_check()
            self.main_window.status_manager.show_message("info", "Spell Check", "Spell check enabled")
            logger.info("Spell check enabled")
        else:
            self.check_timer.stop()
            self._clear_highlights()
            self.errors = []
            self.main_window.status_manager.show_message("info", "Spell Check", "Spell check disabled")
            logger.info("Spell check disabled")

    def _update_menu_text(self) -> None:
        """Update the toggle menu item text to show current state."""
        if hasattr(self.main_window, "action_manager") and hasattr(
            self.main_window.action_manager, "toggle_spell_check_act"
        ):
            text = "✓ &Spell Check" if self.enabled else "&Spell Check"
            self.main_window.action_manager.toggle_spell_check_act.setText(text)

    def set_language(self, language: str) -> None:
        """Change spell check language."""
        self.spell_checker.set_language(language)
        self.main_window._settings.spell_check_language = language
        logger.info(f"Spell check language changed to: {language}")

        if self.enabled:
            self._perform_spell_check()

    def add_to_dictionary(self, word: str) -> None:
        """Add word to custom dictionary."""
        self.spell_checker.add_to_dictionary(word)
        custom_words = self.spell_checker.get_custom_words()
        self.main_window._settings.spell_check_custom_words = custom_words

        if self.enabled:
            self._perform_spell_check()

        logger.info(f"Added '{word}' to custom dictionary")

    def ignore_word(self, word: str) -> None:
        """Ignore word for this session only."""
        self.spell_checker.ignore_word(word)

        if self.enabled:
            self._perform_spell_check()

        logger.debug(f"Ignoring word '{word}' for this session")

    def show_context_menu(self, event: QContextMenuEvent) -> None:
        """Show context menu with spell check suggestions."""
        self._context_menu.show(event)

    def _on_text_changed(self) -> None:
        """Handle text changed event - debounced spell check."""
        if not self.enabled:
            return
        self.check_timer.stop()
        self.check_timer.start(500)

    def _perform_spell_check(self) -> None:
        """Perform spell check on current document."""
        if not self.enabled:
            return

        text = self.editor.toPlainText()
        self.errors = self.spell_checker.check_text(text)
        self._update_highlights()

        logger.info(f"Spell check complete: {len(self.errors)} errors found")

    def _update_highlights(self) -> None:
        """Update red squiggly underlines for all spelling errors."""
        if not self.errors:
            self._clear_highlights()
            return

        spell_check_selections = []
        for error in self.errors:
            cursor = QTextCursor(self.editor.document())
            cursor.setPosition(error.start)
            cursor.setPosition(error.end, QTextCursor.MoveMode.KeepAnchor)

            fmt = QTextCharFormat()
            fmt.setUnderlineColor(QColor(Qt.GlobalColor.red))
            fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)

            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format = fmt
            spell_check_selections.append(selection)

        self.editor.spell_check_selections = spell_check_selections
        self._apply_combined_selections()

    def _clear_highlights(self) -> None:
        """Clear all spelling error highlights."""
        self.editor.spell_check_selections = []
        self._apply_combined_selections()

    def _apply_combined_selections(self) -> None:
        """Combine spell check selections with other selections."""
        combined = list(getattr(self.editor, "spell_check_selections", []))
        search_sels = getattr(self.editor, "search_selections", [])
        combined.extend(search_sels)
        self.editor.setExtraSelections(combined)

    def _find_error_at_position(self, position: int) -> SpellError | None:
        """Find spelling error at given text position."""
        for error in self.errors:
            if error.start <= position < error.end:
                return error
        return None

    def _replace_word(self, cursor: QTextCursor, replacement: str) -> None:
        """Replace misspelled word with suggestion."""
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(replacement)
        cursor.endEditBlock()
        self._perform_spell_check()
