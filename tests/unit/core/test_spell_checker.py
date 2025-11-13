"""
Unit tests for SpellChecker core functionality.

Tests spell checking using pyspellchecker with support for:
- Word-by-word spell checking
- Spelling suggestions
- Custom dictionary management
- Multiple language support
"""

import pytest

from asciidoc_artisan.core.spell_checker import SpellChecker, SpellError


@pytest.mark.unit
class TestSpellError:
    """Test SpellError dataclass."""

    def test_spell_error_creation(self):
        """Test SpellError initializes correctly."""
        error = SpellError(
            word="helo", start=0, end=4, suggestions=["hello", "help"], line=1, column=0
        )

        assert error.word == "helo"
        assert error.start == 0
        assert error.end == 4
        assert error.suggestions == ["hello", "help"]
        assert error.line == 1
        assert error.column == 0

    def test_spell_error_repr(self):
        """Test SpellError string representation."""
        error = SpellError(
            word="tset", start=10, end=14, suggestions=["test"], line=2, column=5
        )

        repr_str = repr(error)
        assert "tset" in repr_str
        assert "line=2" in repr_str
        assert "col=5" in repr_str


@pytest.mark.unit
class TestSpellCheckerInitialization:
    """Test SpellChecker initialization."""

    def test_default_language(self):
        """Test SpellChecker initializes with English by default."""
        checker = SpellChecker()
        assert checker.get_language() == "en"

    def test_custom_language(self):
        """Test SpellChecker initializes with custom language."""
        checker = SpellChecker(language="es")
        assert checker.get_language() == "es"

    def test_initialization_state(self):
        """Test SpellChecker initializes with empty custom dictionary."""
        checker = SpellChecker()
        assert checker.get_custom_words() == []


@pytest.mark.unit
class TestCheckWord:
    """Test single word spell checking."""

    def test_check_correct_word(self):
        """Test correctly spelled word returns True."""
        checker = SpellChecker()
        assert checker.check_word("hello") is True
        assert checker.check_word("world") is True

    def test_check_misspelled_word(self):
        """Test misspelled word returns False."""
        checker = SpellChecker()
        assert checker.check_word("helo") is False
        assert checker.check_word("wrld") is False

    def test_check_empty_word(self):
        """Test empty word returns True."""
        checker = SpellChecker()
        assert checker.check_word("") is True
        assert checker.check_word("   ") is True

    def test_check_word_case_insensitive(self):
        """Test word checking is case-insensitive."""
        checker = SpellChecker()
        assert checker.check_word("Hello") is True
        assert checker.check_word("HELLO") is True
        assert checker.check_word("hElLo") is True

    def test_check_word_with_apostrophe(self):
        """Test words with apostrophes."""
        checker = SpellChecker()
        assert checker.check_word("don't") is True
        assert checker.check_word("it's") is True


@pytest.mark.unit
class TestSuggestions:
    """Test spelling suggestions."""

    def test_get_suggestions_for_misspelled_word(self):
        """Test suggestions are returned for misspelled words."""
        checker = SpellChecker()
        suggestions = checker.get_suggestions("helo")

        assert len(suggestions) > 0
        # Check for any reasonable suggestion (dictionary may vary)
        assert any(
            s in ["hello", "helot", "hero", "held", "hell", "help"] for s in suggestions
        )

    def test_get_suggestions_max_limit(self):
        """Test suggestions respect max_suggestions parameter."""
        checker = SpellChecker()
        suggestions = checker.get_suggestions("helo", max_suggestions=3)

        assert len(suggestions) <= 3

    def test_get_suggestions_empty_word(self):
        """Test empty word returns no suggestions."""
        checker = SpellChecker()
        assert checker.get_suggestions("") == []
        assert checker.get_suggestions("   ") == []

    def test_get_suggestions_for_nonsense(self):
        """Test suggestions for nonsense word."""
        checker = SpellChecker()
        # Very unusual string may have few or no suggestions
        suggestions = checker.get_suggestions("xzqpwlkjh")
        assert isinstance(suggestions, list)


@pytest.mark.unit
class TestCustomDictionary:
    """Test custom dictionary management."""

    def test_add_to_dictionary(self):
        """Test adding word to custom dictionary."""
        checker = SpellChecker()

        # Initially misspelled
        assert checker.check_word("AsciiDoc") is False

        # Add to dictionary
        checker.add_to_dictionary("AsciiDoc")

        # Now correct
        assert checker.check_word("AsciiDoc") is True

    def test_add_to_dictionary_case_insensitive(self):
        """Test custom dictionary is case-insensitive."""
        checker = SpellChecker()

        checker.add_to_dictionary("MyWord")

        assert checker.check_word("myword") is True
        assert checker.check_word("MYWORD") is True
        assert checker.check_word("MyWord") is True

    def test_get_custom_words(self):
        """Test getting custom words returns sorted list."""
        checker = SpellChecker()

        checker.add_to_dictionary("zebra")
        checker.add_to_dictionary("apple")
        checker.add_to_dictionary("banana")

        words = checker.get_custom_words()
        assert words == ["apple", "banana", "zebra"]

    def test_remove_from_dictionary(self):
        """Test removing word from custom dictionary."""
        checker = SpellChecker()

        checker.add_to_dictionary("testword")
        assert checker.check_word("testword") is True

        checker.remove_from_dictionary("testword")
        assert checker.check_word("testword") is False

    def test_clear_custom_dictionary(self):
        """Test clearing custom dictionary."""
        checker = SpellChecker()

        checker.add_to_dictionary("word1")
        checker.add_to_dictionary("word2")
        assert len(checker.get_custom_words()) == 2

        checker.clear_custom_dictionary()
        assert checker.get_custom_words() == []


@pytest.mark.unit
class TestIgnoredWords:
    """Test ignored words functionality."""

    def test_ignore_word(self):
        """Test ignoring word for session."""
        checker = SpellChecker()

        # Initially misspelled
        assert checker.check_word("tempword") is False

        # Ignore for session
        checker.ignore_word("tempword")

        # Now passes check
        assert checker.check_word("tempword") is True

    def test_ignored_word_not_in_custom_dictionary(self):
        """Test ignored words don't appear in custom dictionary."""
        checker = SpellChecker()

        checker.ignore_word("tempword")

        assert "tempword" not in checker.get_custom_words()

    def test_clear_ignored_words(self):
        """Test clearing ignored words."""
        checker = SpellChecker()

        checker.ignore_word("tempword")
        assert checker.check_word("tempword") is True

        checker.clear_ignored_words()
        assert checker.check_word("tempword") is False


@pytest.mark.unit
class TestCheckText:
    """Test text spell checking."""

    def test_check_text_no_errors(self):
        """Test text with no spelling errors."""
        checker = SpellChecker()
        errors = checker.check_text("Hello world, this is a test.")

        assert len(errors) == 0

    def test_check_text_with_errors(self):
        """Test text with spelling errors."""
        checker = SpellChecker()
        errors = checker.check_text("Helo world, this is a tset.")

        assert len(errors) == 2
        assert errors[0].word == "Helo"
        assert errors[1].word == "tset"

    def test_check_text_error_positions(self):
        """Test error positions are correct."""
        checker = SpellChecker()
        text = "This is a tset."
        errors = checker.check_text(text)

        assert len(errors) == 1
        error = errors[0]

        assert error.word == "tset"
        assert text[error.start : error.end] == "tset"
        assert error.line == 1
        assert error.column == 10

    def test_check_text_multiline(self):
        """Test spell checking across multiple lines."""
        checker = SpellChecker()
        text = "First line with erro.\nSecond line with mistke."
        errors = checker.check_text(text)

        assert len(errors) == 2
        assert errors[0].word == "erro"
        assert errors[0].line == 1
        assert errors[1].word == "mistke"
        assert errors[1].line == 2

    def test_check_text_empty(self):
        """Test spell checking empty text."""
        checker = SpellChecker()
        assert checker.check_text("") == []

    def test_check_text_suggestions_included(self):
        """Test spell errors include suggestions."""
        checker = SpellChecker()
        errors = checker.check_text("Helo")

        assert len(errors) == 1
        assert len(errors[0].suggestions) > 0
        # Check for any reasonable suggestion (dictionary may vary)
        suggestions_lower = [s.lower() for s in errors[0].suggestions]
        assert any(
            s in ["hello", "helot", "hero", "held", "hell", "help"]
            for s in suggestions_lower
        )


@pytest.mark.unit
class TestLanguageSupport:
    """Test multiple language support."""

    def test_set_language(self):
        """Test changing language."""
        checker = SpellChecker(language="en")
        assert checker.get_language() == "en"

        checker.set_language("es")
        assert checker.get_language() == "es"

    def test_language_affects_checking(self):
        """Test language change affects spell checking."""
        checker = SpellChecker(language="en")

        # "hola" is Spanish, should be incorrect in English
        assert checker.check_word("hola") is False

        # Change to Spanish
        checker.set_language("es")

        # Now "hola" should be correct
        assert checker.check_word("hola") is True


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_add_empty_word_to_dictionary(self):
        """Test adding empty word to dictionary is ignored."""
        checker = SpellChecker()

        checker.add_to_dictionary("")
        checker.add_to_dictionary("   ")

        assert checker.get_custom_words() == []

    def test_ignore_empty_word(self):
        """Test ignoring empty word is handled."""
        checker = SpellChecker()

        # Should not crash
        checker.ignore_word("")
        checker.ignore_word("   ")

    def test_remove_nonexistent_word(self):
        """Test removing word not in dictionary doesn't crash."""
        checker = SpellChecker()

        # Should not crash
        checker.remove_from_dictionary("nonexistent")

    def test_text_with_only_punctuation(self):
        """Test text with only punctuation."""
        checker = SpellChecker()
        errors = checker.check_text("... !!! ???")

        assert len(errors) == 0

    def test_text_with_numbers(self):
        """Test text with numbers."""
        checker = SpellChecker()
        errors = checker.check_text("Test 123 with numbers 456.")

        assert len(errors) == 0


@pytest.mark.unit
def test_type_checking_pass():
    """Test TYPE_CHECKING pass statement (line 35)."""
    import sys
    from unittest.mock import patch

    # Force TYPE_CHECKING to be True to execute the pass
    with patch("typing.TYPE_CHECKING", True):
        # Remove module from cache to force reimport
        if "asciidoc_artisan.core.spell_checker" in sys.modules:
            del sys.modules["asciidoc_artisan.core.spell_checker"]

        # Import with TYPE_CHECKING=True
        import asciidoc_artisan.core.spell_checker

        # Verify module loaded
        assert asciidoc_artisan.core.spell_checker is not None
