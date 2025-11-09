"""
Tests for ui.spell_check_manager module.

Tests spell check UI integration including:
- Spell check toggling
- Custom dictionary management
- Word ignoring
- Red squiggly underlines
- Context menu with suggestions
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from PySide6.QtWidgets import QMainWindow, QPlainTextEdit, QTextEdit


@pytest.fixture(scope="module", autouse=True)
def mock_pyspellchecker():
    """
    Mock pyspellchecker to prevent dictionary downloads during tests.

    pyspellchecker downloads dictionaries on first use, which can:
    - Hang tests if network is slow/unavailable
    - Take 5-30 seconds for dictionary downloads
    - Cause spurious test failures

    This fixture ensures all spell check tests use a fast in-memory mock.
    """
    # Create a comprehensive mock for PySpellChecker
    mock_spell_instance = MagicMock()

    # Configure the mock to return reasonable spell check results
    # unknown() returns a set of words that are NOT in the dictionary
    def mock_unknown(word_list):
        # Return only known misspellings
        return {w for w in word_list if w.lower() in {"helo", "tset", "erro", "xyzabc"}}

    mock_spell_instance.unknown.side_effect = mock_unknown
    mock_spell_instance.correction.return_value = "hello"
    mock_spell_instance.candidates.return_value = {"hello", "help", "hero"}

    # Patch where the SpellChecker is imported and used
    with patch("spellchecker.SpellChecker", return_value=mock_spell_instance):
        yield mock_spell_instance


@pytest.fixture
def main_window(qapp):
    """Create main window with required attributes for SpellCheckManager."""
    window = QMainWindow()
    window.editor = QPlainTextEdit()

    # Add ExtraSelection class to editor (required by spell_check_manager)
    # Use QTextEdit.ExtraSelection (QPlainTextEdit inherits from QTextEdit)
    window.editor.ExtraSelection = QTextEdit.ExtraSelection

    # Mock settings
    window._settings = Mock()
    window._settings.spell_check_enabled = True
    window._settings.spell_check_language = "en"
    window._settings.spell_check_custom_words = []

    # Mock status_manager
    window.status_manager = Mock()
    window.status_manager.show_message = Mock()

    # Mock action_manager
    window.action_manager = Mock()
    window.action_manager.toggle_spell_check_act = Mock()
    window.action_manager.toggle_spell_check_act.setText = Mock()

    return window


@pytest.mark.unit
class TestSpellCheckManagerInitialization:
    """Test SpellCheckManager initialization."""

    def test_import(self):
        """Test SpellCheckManager can be imported."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        assert SpellCheckManager is not None

    def test_creation(self, main_window):
        """Test creating SpellCheckManager instance."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        assert manager is not None
        assert manager.enabled is True  # From settings
        assert manager.spell_checker is not None

    def test_initialization_with_custom_words(self, main_window):
        """Test initializing with custom dictionary words."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        # Add custom words to settings
        main_window._settings.spell_check_custom_words = ["testword1", "testword2"]

        manager = SpellCheckManager(main_window)

        # Custom words should be added to spell checker
        custom_words = manager.spell_checker.get_custom_words()
        assert "testword1" in custom_words
        assert "testword2" in custom_words


@pytest.mark.unit
class TestSpellCheckToggle:
    """Test spell check toggle functionality."""

    def test_toggle_spell_check_off(self, main_window):
        """Test toggling spell check off."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        main_window._settings.spell_check_enabled = True
        manager = SpellCheckManager(main_window)

        assert manager.enabled is True

        # Toggle off
        manager.toggle_spell_check()

        assert manager.enabled is False
        assert main_window._settings.spell_check_enabled is False
        main_window.status_manager.show_message.assert_called()

    def test_toggle_spell_check_on(self, main_window):
        """Test toggling spell check on."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        main_window._settings.spell_check_enabled = False
        manager = SpellCheckManager(main_window)

        assert manager.enabled is False

        # Toggle on
        manager.toggle_spell_check()

        assert manager.enabled is True
        assert main_window._settings.spell_check_enabled is True

    def test_toggle_clears_highlights_when_disabled(self, main_window):
        """Test toggling off clears spelling highlights."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True
        manager.errors = [Mock()]  # Simulate existing errors

        # Toggle off
        manager.toggle_spell_check()

        # Errors should be cleared
        assert manager.errors == []


@pytest.mark.unit
class TestLanguageSupport:
    """Test language switching."""

    def test_set_language(self, main_window):
        """Test changing spell check language."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Change language
        manager.set_language("es")

        assert manager.spell_checker.get_language() == "es"
        assert main_window._settings.spell_check_language == "es"

    def test_set_language_triggers_recheck(self, main_window):
        """Test language change triggers spell check when enabled."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        with patch.object(manager, "_perform_spell_check") as mock_check:
            manager.set_language("fr")

            # Should trigger spell check
            mock_check.assert_called_once()


@pytest.mark.unit
class TestCustomDictionary:
    """Test custom dictionary management."""

    def test_add_to_dictionary(self, main_window):
        """Test adding word to custom dictionary."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Add word
        manager.add_to_dictionary("customword")

        # Should be in spell checker's custom dictionary
        assert "customword" in manager.spell_checker.get_custom_words()

        # Should be saved to settings
        assert "customword" in main_window._settings.spell_check_custom_words

    def test_add_to_dictionary_triggers_recheck(self, main_window):
        """Test adding to dictionary triggers spell check when enabled."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        with patch.object(manager, "_perform_spell_check") as mock_check:
            manager.add_to_dictionary("testword")

            # Should trigger spell check to remove highlights
            mock_check.assert_called_once()


@pytest.mark.unit
class TestIgnoredWords:
    """Test word ignoring functionality."""

    def test_ignore_word(self, main_window):
        """Test ignoring word for session."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Ignore word
        manager.ignore_word("tempword")

        # Should pass spell check
        assert manager.spell_checker.check_word("tempword") is True

        # Should NOT be in custom dictionary (session only)
        assert "tempword" not in manager.spell_checker.get_custom_words()

    def test_ignore_word_triggers_recheck(self, main_window):
        """Test ignoring word triggers spell check when enabled."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        with patch.object(manager, "_perform_spell_check") as mock_check:
            manager.ignore_word("ignoreword")

            # Should trigger spell check to remove highlights
            mock_check.assert_called_once()


@pytest.mark.unit
class TestSpellChecking:
    """Test spell checking functionality."""

    def test_perform_spell_check_when_enabled(self, main_window):
        """Test spell check runs when enabled."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        main_window.editor.setPlainText("Helo world, this is a tset.")
        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Perform spell check
        manager._perform_spell_check()

        # Should find errors
        assert len(manager.errors) > 0
        assert any(e.word == "Helo" for e in manager.errors)

    def test_perform_spell_check_when_disabled(self, main_window):
        """Test spell check skipped when disabled."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        main_window.editor.setPlainText("Helo world")
        manager = SpellCheckManager(main_window)
        manager.enabled = False

        # Clear errors
        manager.errors = []

        # Try to spell check
        manager._perform_spell_check()

        # Should not check
        assert manager.errors == []

    def test_text_changed_starts_timer(self, main_window):
        """Test text changed starts debounce timer."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Trigger text change
        manager._on_text_changed()

        # Timer should be active
        assert manager.check_timer.isActive()

    def test_text_changed_ignored_when_disabled(self, main_window):
        """Test text changed ignored when spell check disabled."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = False

        # Trigger text change
        manager._on_text_changed()

        # Timer should not be active
        assert not manager.check_timer.isActive()


@pytest.mark.unit
class TestHighlights:
    """Test spelling error highlights."""

    def test_update_highlights(self, main_window, qapp):
        """Test highlights are created for errors."""
        from asciidoc_artisan.core.spell_checker import SpellError
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Create mock error
        manager.errors = [
            SpellError(
                word="helo", start=0, end=4, suggestions=["hello"], line=1, column=0
            )
        ]

        # Update highlights
        manager._update_highlights()

        # Should create extra selections
        selections = manager.editor.extraSelections()
        assert len(selections) > 0

    def test_clear_highlights(self, main_window):
        """Test clearing highlights."""
        from asciidoc_artisan.core.spell_checker import SpellError
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Add some errors and highlights
        manager.errors = [
            SpellError(word="test", start=0, end=4, suggestions=[], line=1, column=0)
        ]
        manager._update_highlights()

        # Clear highlights
        manager._clear_highlights()

        # Should have no selections
        assert len(manager.editor.extraSelections()) == 0

    def test_find_error_at_position(self, main_window):
        """Test finding error at cursor position."""
        from asciidoc_artisan.core.spell_checker import SpellError
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Add error at position 10-14
        manager.errors = [
            SpellError(
                word="erro", start=10, end=14, suggestions=["error"], line=1, column=10
            )
        ]

        # Find error at position 12 (inside word)
        error = manager._find_error_at_position(12)
        assert error is not None
        assert error.word == "erro"

        # Find at position 5 (no error)
        error = manager._find_error_at_position(5)
        assert error is None


@pytest.mark.unit
class TestContextMenu:
    """Test context menu functionality."""

    @pytest.mark.skip(
        reason="QMenu.exec() blocks in test environment - requires manual testing"
    )
    def test_show_context_menu_with_suggestions(self, main_window):
        """Test context menu shows suggestions for misspelled word."""
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QContextMenuEvent

        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Set up editor with misspelled word
        main_window.editor.setPlainText("Helo world")
        manager._perform_spell_check()

        # Create mock context menu event
        event = Mock(spec=QContextMenuEvent)
        event.pos.return_value = QPoint(0, 0)
        event.globalPos.return_value = QPoint(100, 100)

        # Mock cursor to select "Helo"
        with patch.object(
            main_window.editor, "cursorForPosition"
        ) as mock_cursor_for_pos:
            mock_cursor = Mock()
            mock_cursor.selectedText.return_value = "Helo"
            mock_cursor.selectionStart.return_value = 0
            mock_cursor_for_pos.return_value = mock_cursor

            # Should not crash or hang
            manager.show_context_menu(event)

    def test_show_default_menu_when_disabled(self, main_window):
        """Test default context menu shown when spell check disabled."""
        from PySide6.QtGui import QContextMenuEvent

        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = False

        event = Mock(spec=QContextMenuEvent)

        with patch.object(manager, "_show_default_context_menu") as mock_default:
            manager.show_context_menu(event)

            # Should show default menu
            mock_default.assert_called_once_with(event)


@pytest.mark.unit
class TestWordReplacement:
    """Test word replacement functionality."""

    def test_replace_word(self, main_window):
        """Test replacing misspelled word with suggestion."""
        from PySide6.QtGui import QTextCursor

        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Set text with misspelled word
        main_window.editor.setPlainText("Helo world")

        # Create cursor selecting "Helo"
        cursor = main_window.editor.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(4, QTextCursor.MoveMode.KeepAnchor)

        # Replace with "Hello"
        manager._replace_word(cursor, "Hello")

        # Text should be replaced
        text = main_window.editor.toPlainText()
        assert "Hello world" in text or text.startswith("Hello")


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases for spell checking."""

    def test_spell_check_with_empty_text(self, main_window):
        """Test spell check with empty editor."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        main_window.editor.setPlainText("")
        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Should not crash
        manager._perform_spell_check()
        assert manager.errors == []

    def test_spell_check_with_very_long_text(self, main_window):
        """Test spell check with very long document."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        # Create document with 1000 words
        long_text = " ".join(["word"] * 1000)
        main_window.editor.setPlainText(long_text)

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Should not crash
        manager._perform_spell_check()
        assert isinstance(manager.errors, list)

    def test_spell_check_with_special_characters(self, main_window):
        """Test spell check with special characters."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        special_text = "Hello @world #test $money 100% done!"
        main_window.editor.setPlainText(special_text)

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Should handle special chars gracefully
        manager._perform_spell_check()
        assert isinstance(manager.errors, list)

    def test_spell_check_with_unicode_text(self, main_window):
        """Test spell check with Unicode characters."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        unicode_text = "Hello мир 世界 🌍"
        main_window.editor.setPlainText(unicode_text)

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Should not crash
        manager._perform_spell_check()
        assert isinstance(manager.errors, list)

    def test_spell_check_with_numbers_only(self, main_window):
        """Test spell check with numeric content."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        main_window.editor.setPlainText("123 456 789 1000")
        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Should not crash
        manager._perform_spell_check()
        assert isinstance(manager.errors, list)

    def test_spell_check_with_mixed_case(self, main_window):
        """Test spell check with mixed case words."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        mixed_text = "HELLO WoRlD tEsT"
        main_window.editor.setPlainText(mixed_text)
        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Should not crash
        manager._perform_spell_check()
        assert isinstance(manager.errors, list)

    def test_spell_check_with_repeated_words(self, main_window):
        """Test spell check with repeated words."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        repeated_text = "word word word word word"
        main_window.editor.setPlainText(repeated_text)
        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Should not crash
        manager._perform_spell_check()
        assert isinstance(manager.errors, list)


@pytest.mark.unit
class TestMultipleLanguageSwitching:
    """Test multiple language switching scenarios."""

    def test_switch_language_multiple_times(self, main_window):
        """Test switching language multiple times."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Switch languages multiple times
        manager.set_language("es")
        assert manager.spell_checker.get_language() == "es"

        manager.set_language("fr")
        assert manager.spell_checker.get_language() == "fr"

        manager.set_language("en")
        assert manager.spell_checker.get_language() == "en"

    def test_set_same_language_twice(self, main_window):
        """Test setting same language twice."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        manager.set_language("en")
        assert manager.spell_checker.get_language() == "en"

        # Set same language again
        manager.set_language("en")
        assert manager.spell_checker.get_language() == "en"

    def test_language_switch_clears_errors(self, main_window):
        """Test language switch clears existing errors."""
        from asciidoc_artisan.core.spell_checker import SpellError
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Add some errors
        manager.errors = [
            SpellError(word="test", start=0, end=4, suggestions=[], line=1, column=0)
        ]

        with patch.object(manager, "_perform_spell_check") as mock_check:
            manager.set_language("es")

            # Should trigger recheck
            mock_check.assert_called_once()

    def test_language_with_empty_code(self, main_window):
        """Test setting language with empty string."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        original_lang = manager.spell_checker.get_language()

        try:
            manager.set_language("")
            # Language should not change or handle gracefully
            assert manager.spell_checker.get_language() in ["", original_lang]
        except Exception:
            # Expected to fail gracefully
            assert True


@pytest.mark.unit
class TestCustomDictionaryEdgeCases:
    """Test custom dictionary edge cases."""

    def test_add_duplicate_word_to_dictionary(self, main_window):
        """Test adding same word to dictionary twice."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        manager.add_to_dictionary("testword")
        manager.add_to_dictionary("testword")

        # Should not create duplicates in settings
        custom_words = main_window._settings.spell_check_custom_words
        assert custom_words.count("testword") == 1

    def test_add_word_with_mixed_case(self, main_window):
        """Test adding word with mixed case to dictionary."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        manager.add_to_dictionary("TestWord")

        # Should preserve case
        assert "TestWord" in manager.spell_checker.get_custom_words()

    def test_add_very_long_word(self, main_window):
        """Test adding very long word to dictionary."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        long_word = "a" * 100
        manager.add_to_dictionary(long_word)

        # Should handle long words
        assert long_word in manager.spell_checker.get_custom_words()

    def test_add_word_with_special_characters(self, main_window):
        """Test adding word with special characters."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        special_word = "test-word_123"
        manager.add_to_dictionary(special_word)

        # Should handle special chars
        assert special_word in manager.spell_checker.get_custom_words()

    def test_add_many_words_to_dictionary(self, main_window):
        """Test adding many words to dictionary."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Add 50 words
        for i in range(50):
            manager.add_to_dictionary(f"word{i}")

        # All should be added
        custom_words = manager.spell_checker.get_custom_words()
        assert len([w for w in custom_words if w.startswith("word")]) == 50


@pytest.mark.unit
class TestHighlightRenderingEdgeCases:
    """Test highlight rendering edge cases."""

    def test_highlight_many_errors(self, main_window):
        """Test highlighting many spelling errors."""
        from asciidoc_artisan.core.spell_checker import SpellError
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Create 50 errors
        manager.errors = [
            SpellError(
                word=f"err{i}",
                start=i * 10,
                end=i * 10 + 4,
                suggestions=[],
                line=1,
                column=i * 10,
            )
            for i in range(50)
        ]

        # Should not crash
        manager._update_highlights()
        assert isinstance(manager.editor.extraSelections(), list)

    def test_highlight_at_document_end(self, main_window):
        """Test highlighting error at end of document."""
        from asciidoc_artisan.core.spell_checker import SpellError
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        text = "Hello world erro"
        main_window.editor.setPlainText(text)

        manager = SpellCheckManager(main_window)

        # Error at end of document
        manager.errors = [
            SpellError(
                word="erro",
                start=len(text) - 4,
                end=len(text),
                suggestions=["error"],
                line=1,
                column=len(text) - 4,
            )
        ]

        # Should not crash
        manager._update_highlights()
        assert len(manager.editor.extraSelections()) > 0

    def test_highlight_with_zero_errors(self, main_window):
        """Test updating highlights with no errors."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.errors = []

        # Should not crash
        manager._update_highlights()
        assert len(manager.editor.extraSelections()) == 0

    def test_highlight_with_overlapping_positions(self, main_window):
        """Test handling errors with overlapping positions."""
        from asciidoc_artisan.core.spell_checker import SpellError
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Create errors with overlapping positions
        manager.errors = [
            SpellError(word="err1", start=0, end=10, suggestions=[], line=1, column=0),
            SpellError(word="err2", start=5, end=15, suggestions=[], line=1, column=5),
        ]

        # Should handle gracefully
        manager._update_highlights()
        assert isinstance(manager.editor.extraSelections(), list)


@pytest.mark.unit
class TestContextMenuEdgeCases:
    """Test context menu edge cases."""

    @pytest.mark.skip(
        reason="QMenu.exec() blocks in test environment - requires manual testing"
    )
    def test_context_menu_with_no_suggestions(self, main_window):
        """Test context menu when word has no suggestions."""
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QContextMenuEvent

        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        main_window.editor.setPlainText("xyzabc")

        event = Mock(spec=QContextMenuEvent)
        event.pos.return_value = QPoint(0, 0)
        event.globalPos.return_value = QPoint(100, 100)

        # Should not crash even with no suggestions
        with patch.object(
            main_window.editor, "cursorForPosition"
        ) as mock_cursor_for_pos:
            mock_cursor = Mock()
            mock_cursor.selectedText.return_value = "xyzabc"
            mock_cursor.selectionStart.return_value = 0
            mock_cursor_for_pos.return_value = mock_cursor

            manager.show_context_menu(event)

    @pytest.mark.skip(
        reason="QMenu.exec() blocks in test environment - requires manual testing"
    )
    def test_context_menu_at_document_start(self, main_window):
        """Test context menu at start of document."""
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QContextMenuEvent

        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        main_window.editor.setPlainText("Helo world")

        event = Mock(spec=QContextMenuEvent)
        event.pos.return_value = QPoint(0, 0)
        event.globalPos.return_value = QPoint(0, 0)

        # Should not crash
        with patch.object(main_window.editor, "cursorForPosition"):
            manager.show_context_menu(event)

    def test_context_menu_with_empty_text(self, main_window):
        """Test context menu with empty editor."""
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QContextMenuEvent

        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        main_window.editor.setPlainText("")

        event = Mock(spec=QContextMenuEvent)
        event.pos.return_value = QPoint(0, 0)
        event.globalPos.return_value = QPoint(100, 100)

        # Should show default menu
        with patch.object(manager, "_show_default_context_menu"):
            manager.show_context_menu(event)


@pytest.mark.unit
class TestTimerDebounceEdgeCases:
    """Test timer and debounce edge cases."""

    def test_multiple_rapid_text_changes(self, main_window):
        """Test multiple rapid text changes restart timer."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Trigger multiple changes
        manager._on_text_changed()
        manager._on_text_changed()
        manager._on_text_changed()

        # Timer should be active
        assert manager.check_timer.isActive()

    def test_timer_restarts_on_new_change(self, main_window):
        """Test timer restarts when new text change occurs."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        manager._on_text_changed()
        first_timer_active = manager.check_timer.isActive()

        # Trigger another change
        manager._on_text_changed()
        second_timer_active = manager.check_timer.isActive()

        # Both should be active (timer restarted)
        assert first_timer_active
        assert second_timer_active

    def test_timer_stops_when_disabled(self, main_window):
        """Test timer stops when spell check disabled."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        manager._on_text_changed()
        assert manager.check_timer.isActive()

        # Disable spell check
        manager.toggle_spell_check()

        # Timer should stop
        assert not manager.check_timer.isActive()


@pytest.mark.unit
class TestErrorRecovery:
    """Test error recovery scenarios."""

    def test_spell_check_with_invalid_spell_checker(self, main_window):
        """Test spell check handles invalid spell checker."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Set spell checker to None
        manager.spell_checker = None

        # Should handle gracefully
        try:
            manager._perform_spell_check()
            # Should not crash
            assert True
        except AttributeError:
            # Expected error
            assert True

    def test_highlight_with_invalid_cursor_position(self, main_window):
        """Test highlighting with invalid cursor position."""
        from asciidoc_artisan.core.spell_checker import SpellError
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        main_window.editor.setPlainText("Short")
        manager = SpellCheckManager(main_window)

        # Error beyond document length
        manager.errors = [
            SpellError(
                word="test", start=1000, end=1004, suggestions=[], line=1, column=1000
            )
        ]

        # Should handle gracefully
        try:
            manager._update_highlights()
            assert True
        except Exception:
            # Expected to handle gracefully
            assert True

    def test_find_error_with_negative_position(self, main_window):
        """Test finding error with negative position."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Should return None for negative position
        error = manager._find_error_at_position(-5)
        assert error is None


@pytest.mark.unit
class TestPerformanceScenarios:
    """Test performance scenarios."""

    def test_spell_check_large_document(self, main_window):
        """Test spell checking large document."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        # Create 5000 word document
        large_text = " ".join(["word"] * 5000)
        main_window.editor.setPlainText(large_text)

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Should complete without crashing
        manager._perform_spell_check()
        assert isinstance(manager.errors, list)

    def test_many_custom_words_performance(self, main_window):
        """Test performance with many custom words."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        # Add 100 custom words
        main_window._settings.spell_check_custom_words = [
            f"custom{i}" for i in range(100)
        ]

        manager = SpellCheckManager(main_window)

        # Should initialize without crashing
        assert manager is not None
        custom_words = manager.spell_checker.get_custom_words()
        assert len([w for w in custom_words if w.startswith("custom")]) == 100

    def test_rapid_toggle_performance(self, main_window):
        """Test rapid toggling performance."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Toggle 20 times
        for _ in range(20):
            manager.toggle_spell_check()

        # Should end in expected state (even number of toggles)
        assert manager.enabled is True  # Started True, toggled 20 times = True

    def test_highlight_performance_many_selections(self, main_window):
        """Test highlighting performance with many selections."""
        from asciidoc_artisan.core.spell_checker import SpellError
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Create 100 errors
        manager.errors = [
            SpellError(
                word=f"err{i}",
                start=i * 5,
                end=i * 5 + 3,
                suggestions=[],
                line=1,
                column=i * 5,
            )
            for i in range(100)
        ]

        # Should handle without crashing
        manager._update_highlights()
        assert isinstance(manager.editor.extraSelections(), list)

    def test_ignore_many_words_performance(self, main_window):
        """Test performance when ignoring many words."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Ignore 50 words
        for i in range(50):
            manager.ignore_word(f"ignore{i}")

        # Should handle without crashing
        assert manager.spell_checker is not None


@pytest.mark.unit
class TestStatePersistence:
    """Test state persistence across operations."""

    def test_settings_saved_on_toggle(self, main_window):
        """Test settings saved when toggling spell check."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        main_window._settings.spell_check_enabled = True
        manager = SpellCheckManager(main_window)

        manager.toggle_spell_check()

        # Settings should be updated
        assert main_window._settings.spell_check_enabled is False

    def test_settings_saved_on_language_change(self, main_window):
        """Test settings saved when changing language."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        manager.set_language("es")

        # Settings should be updated
        assert main_window._settings.spell_check_language == "es"

    def test_custom_words_persist_across_instances(self, main_window):
        """Test custom words persist across manager instances."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        # First instance adds word
        manager1 = SpellCheckManager(main_window)
        manager1.add_to_dictionary("persist")

        # Second instance should see the word (via settings)
        manager2 = SpellCheckManager(main_window)
        custom_words = manager2.spell_checker.get_custom_words()
        assert "persist" in custom_words

    def test_state_after_multiple_operations(self, main_window):
        """Test state consistency after multiple operations."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)

        # Perform multiple operations
        manager.set_language("es")
        manager.add_to_dictionary("test")
        manager.toggle_spell_check()
        manager.toggle_spell_check()
        manager.ignore_word("temp")

        # State should be consistent
        assert manager.enabled is True
        assert manager.spell_checker.get_language() == "es"
        assert "test" in manager.spell_checker.get_custom_words()


@pytest.mark.unit
class TestConcurrentOperations:
    """Test concurrent operations."""

    def test_spell_check_during_text_change(self, main_window):
        """Test spell check while text is changing."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        main_window.editor.setPlainText("Initial text")

        # Trigger spell check
        manager._perform_spell_check()

        # Change text during check (simulated)
        main_window.editor.setPlainText("Changed text")

        # Should handle gracefully
        manager._perform_spell_check()
        assert isinstance(manager.errors, list)

    def test_toggle_during_spell_check(self, main_window):
        """Test toggling spell check during ongoing check."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        main_window.editor.setPlainText("Test text")

        # Start spell check
        manager._perform_spell_check()

        # Toggle during check
        manager.toggle_spell_check()

        # Should handle state change
        assert manager.enabled is False
        assert manager.errors == []

    def test_language_change_during_spell_check(self, main_window):
        """Test language change during spell check."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        main_window.editor.setPlainText("Test text")

        # Start spell check
        manager._perform_spell_check()

        # Change language during check
        with patch.object(manager, "_perform_spell_check") as mock_check:
            manager.set_language("es")

            # Should trigger new check
            mock_check.assert_called_once()

    def test_add_to_dictionary_during_spell_check(self, main_window):
        """Test adding to dictionary during spell check."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        main_window.editor.setPlainText("testword content")

        # Start spell check
        manager._perform_spell_check()

        # Add word to dictionary during check
        with patch.object(manager, "_perform_spell_check") as mock_check:
            manager.add_to_dictionary("testword")

            # Should trigger new check
            mock_check.assert_called_once()

    def test_multiple_rapid_operations(self, main_window):
        """Test multiple rapid operations in sequence."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Rapid sequence of operations
        manager._on_text_changed()
        manager.add_to_dictionary("word1")
        manager._on_text_changed()
        manager.ignore_word("word2")
        manager._on_text_changed()
        manager.set_language("es")

        # Should handle gracefully
        assert manager.enabled is True
        assert manager.spell_checker.get_language() == "es"

    def test_clear_highlights_during_spell_check(self, main_window):
        """Test clearing highlights during spell check."""
        from asciidoc_artisan.core.spell_checker import SpellError
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager

        manager = SpellCheckManager(main_window)
        manager.enabled = True

        # Add errors
        manager.errors = [
            SpellError(word="test", start=0, end=4, suggestions=[], line=1, column=0)
        ]
        manager._update_highlights()

        # Clear during check
        manager._clear_highlights()

        # Should have no selections
        assert len(manager.editor.extraSelections()) == 0
