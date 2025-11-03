"""
Tests for ui.spell_check_manager module.

Tests spell check UI integration including:
- Spell check toggling
- Custom dictionary management
- Word ignoring
- Red squiggly underlines
- Context menu with suggestions
"""

import pytest
from PySide6.QtWidgets import QMainWindow, QPlainTextEdit, QTextEdit
from PySide6.QtCore import QTimer
from unittest.mock import Mock, MagicMock, patch


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
        
        with patch.object(manager, '_perform_spell_check') as mock_check:
            manager.set_language("fr")
            
            # Should trigger spell check
            mock_check.assert_called_once()


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
        
        with patch.object(manager, '_perform_spell_check') as mock_check:
            manager.add_to_dictionary("testword")
            
            # Should trigger spell check to remove highlights
            mock_check.assert_called_once()


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
        
        with patch.object(manager, '_perform_spell_check') as mock_check:
            manager.ignore_word("ignoreword")
            
            # Should trigger spell check to remove highlights
            mock_check.assert_called_once()


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


class TestHighlights:
    """Test spelling error highlights."""

    def test_update_highlights(self, main_window, qapp):
        """Test highlights are created for errors."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager
        from asciidoc_artisan.core.spell_checker import SpellError
        
        manager = SpellCheckManager(main_window)
        
        # Create mock error
        manager.errors = [
            SpellError(
                word="helo",
                start=0,
                end=4,
                suggestions=["hello"],
                line=1,
                column=0
            )
        ]
        
        # Update highlights
        manager._update_highlights()
        
        # Should create extra selections
        selections = manager.editor.extraSelections()
        assert len(selections) > 0

    def test_clear_highlights(self, main_window):
        """Test clearing highlights."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager
        from asciidoc_artisan.core.spell_checker import SpellError
        
        manager = SpellCheckManager(main_window)
        
        # Add some errors and highlights
        manager.errors = [
            SpellError(
                word="test",
                start=0,
                end=4,
                suggestions=[],
                line=1,
                column=0
            )
        ]
        manager._update_highlights()
        
        # Clear highlights
        manager._clear_highlights()
        
        # Should have no selections
        assert len(manager.editor.extraSelections()) == 0

    def test_find_error_at_position(self, main_window):
        """Test finding error at cursor position."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager
        from asciidoc_artisan.core.spell_checker import SpellError
        
        manager = SpellCheckManager(main_window)
        
        # Add error at position 10-14
        manager.errors = [
            SpellError(
                word="erro",
                start=10,
                end=14,
                suggestions=["error"],
                line=1,
                column=10
            )
        ]
        
        # Find error at position 12 (inside word)
        error = manager._find_error_at_position(12)
        assert error is not None
        assert error.word == "erro"
        
        # Find at position 5 (no error)
        error = manager._find_error_at_position(5)
        assert error is None


class TestContextMenu:
    """Test context menu functionality."""

    def test_show_context_menu_with_suggestions(self, main_window):
        """Test context menu shows suggestions for misspelled word."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager
        from PySide6.QtGui import QContextMenuEvent
        from PySide6.QtCore import QPoint
        
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
        with patch.object(main_window.editor, 'cursorForPosition') as mock_cursor_for_pos:
            mock_cursor = Mock()
            mock_cursor.selectedText.return_value = "Helo"
            mock_cursor.selectionStart.return_value = 0
            mock_cursor_for_pos.return_value = mock_cursor
            
            # Should not crash
            manager.show_context_menu(event)

    def test_show_default_menu_when_disabled(self, main_window):
        """Test default context menu shown when spell check disabled."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager
        from PySide6.QtGui import QContextMenuEvent
        
        manager = SpellCheckManager(main_window)
        manager.enabled = False
        
        event = Mock(spec=QContextMenuEvent)
        
        with patch.object(manager, '_show_default_context_menu') as mock_default:
            manager.show_context_menu(event)
            
            # Should show default menu
            mock_default.assert_called_once_with(event)


class TestWordReplacement:
    """Test word replacement functionality."""

    def test_replace_word(self, main_window):
        """Test replacing misspelled word with suggestion."""
        from asciidoc_artisan.ui.spell_check_manager import SpellCheckManager
        from PySide6.QtGui import QTextCursor
        
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
