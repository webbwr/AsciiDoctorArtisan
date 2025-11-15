"""
Spell Checker - Integrated spell checking for AsciiDoc Artisan.

This module provides spell checking using pyspellchecker with support for:
- Word-by-word spell checking
- Spelling suggestions
- Custom dictionary management
- Multiple language support
- Fast in-memory dictionary

Performance targets:
- Check 1000 words in <100ms
- Suggestions generated in <50ms per word
- Memory efficient (built-in dictionary)

Example:
    >>> checker = SpellChecker()
    >>> errors = checker.check_text("Helo world, this is a tset.")
    >>> len(errors)
    2
    >>> errors[0].word
    'Helo'
    >>> errors[0].suggestions
    ['Hello', 'Help', 'Hero']
"""

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

# Lazy import: Only load pyspellchecker when SpellChecker is instantiated
# This saves ~30-50ms at startup since most users don't enable spell check immediately
if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class SpellError:
    """
    Represents a spelling error found in text.

    Attributes:
        word: The misspelled word
        start: Character offset where word starts (0-indexed)
        end: Character offset where word ends (exclusive)
        suggestions: List of suggested corrections (up to 5)
        line: Line number where word occurs (1-indexed)
        column: Column number where word starts (0-indexed)
    """

    word: str
    start: int
    end: int
    suggestions: list[str]
    line: int
    column: int

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"SpellError(word='{self.word}', line={self.line}, col={self.column})"


class SpellChecker:
    """
    High-performance spell checker with custom dictionary support.

    This class provides fast spell checking using pyspellchecker with
    built-in dictionaries and support for custom words.

    Example:
        >>> checker = SpellChecker()
        >>> errors = checker.check_text("Helo world")
        >>> errors[0].word
        'Helo'
    """

    def __init__(self, language: str = "en") -> None:
        """
        Initialize SpellChecker with specified language.

        Args:
            language: Language code (e.g., 'en', 'es', 'fr', 'de')
        """
        # Lazy import: Load pyspellchecker only when needed
        from spellchecker import SpellChecker as PySpellChecker

        self._spell = PySpellChecker(language=language)
        self._custom_dictionary: set[str] = set()
        self._ignored_words: set[str] = set()
        self._language = language

        # Regex pattern to extract words (alphanumeric + apostrophes)
        # This matches: hello, don't, it's, etc.
        self._word_pattern = re.compile(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b")

        logger.info(f"SpellChecker initialized with language: {language}")

    def check_word(self, word: str) -> bool:
        """
        Check if a single word is spelled correctly.

        Args:
            word: Word to check

        Returns:
            True if word is spelled correctly or in custom dictionary,
            False otherwise

        Example:
            >>> checker = SpellChecker()
            >>> checker.check_word("hello")
            True
            >>> checker.check_word("helo")
            False
        """
        if not word or not word.strip():
            return True

        # Lowercase for checking
        word_lower = word.lower()

        # Check if in custom dictionary or ignored
        if word_lower in self._custom_dictionary or word_lower in self._ignored_words:
            return True

        # Check with pyspellchecker
        return word_lower not in self._spell.unknown([word_lower])

    def get_suggestions(self, word: str, max_suggestions: int = 5) -> list[str]:
        """
        Get spelling suggestions for a misspelled word.

        Args:
            word: Misspelled word
            max_suggestions: Maximum number of suggestions (default: 5)

        Returns:
            List of suggested corrections (up to max_suggestions)

        Example:
            >>> checker = SpellChecker()
            >>> checker.get_suggestions("helo")
            ['hello', 'help', 'hero', 'helot', 'halo']
        """
        if not word or not word.strip():
            return []

        # Get suggestions from pyspellchecker
        candidates = self._spell.candidates(word.lower())

        if not candidates:
            return []

        # Convert to list and limit to max_suggestions
        suggestions = list(candidates)[:max_suggestions]

        logger.debug(f"Suggestions for '{word}': {suggestions}")
        return suggestions

    def add_to_dictionary(self, word: str) -> None:
        """
        Add a word to the custom dictionary.

        Words in the custom dictionary are treated as correct.

        Args:
            word: Word to add to custom dictionary

        Example:
            >>> checker = SpellChecker()
            >>> checker.add_to_dictionary("AsciiDoc")
            >>> checker.check_word("AsciiDoc")
            True
        """
        if word and word.strip():
            self._custom_dictionary.add(word.lower())
            logger.info(f"Added '{word}' to custom dictionary")

    def remove_from_dictionary(self, word: str) -> None:
        """
        Remove a word from the custom dictionary.

        Args:
            word: Word to remove

        Example:
            >>> checker = SpellChecker()
            >>> checker.add_to_dictionary("test")
            >>> checker.remove_from_dictionary("test")
        """
        if word:
            self._custom_dictionary.discard(word.lower())
            logger.info(f"Removed '{word}' from custom dictionary")

    def ignore_word(self, word: str) -> None:
        """
        Ignore a word for this session only.

        Ignored words are not added to the custom dictionary and
        will not persist between sessions.

        Args:
            word: Word to ignore

        Example:
            >>> checker = SpellChecker()
            >>> checker.ignore_word("AsciiDoc")
            >>> checker.check_word("AsciiDoc")
            True
        """
        if word and word.strip():
            self._ignored_words.add(word.lower())
            logger.debug(f"Ignoring word '{word}' for this session")

    def check_text(self, text: str) -> list[SpellError]:
        """
        Check spelling for all words in text.

        Args:
            text: Text to spell check

        Returns:
            List of SpellError objects for misspelled words

        Example:
            >>> checker = SpellChecker()
            >>> errors = checker.check_text("Helo world, this is a tset.")
            >>> len(errors)
            2
            >>> errors[0].word
            'Helo'
        """
        if not text:
            return []

        errors: list[SpellError] = []
        lines = text.splitlines(keepends=True)
        current_offset = 0

        for line_num, line in enumerate(lines, start=1):
            # Find all words in the line
            for match in self._word_pattern.finditer(line):
                word = match.group(0)
                start = current_offset + match.start()
                end = current_offset + match.end()
                column = match.start()

                # Check if word is misspelled
                if not self.check_word(word):
                    suggestions = self.get_suggestions(word)
                    errors.append(
                        SpellError(
                            word=word,
                            start=start,
                            end=end,
                            suggestions=suggestions,
                            line=line_num,
                            column=column,
                        )
                    )

            current_offset += len(line)

        logger.debug(f"Found {len(errors)} spelling errors in text")
        return errors

    def clear_custom_dictionary(self) -> None:
        """Clear all words from the custom dictionary."""
        self._custom_dictionary.clear()
        logger.info("Custom dictionary cleared")

    def clear_ignored_words(self) -> None:
        """Clear all ignored words."""
        self._ignored_words.clear()
        logger.debug("Ignored words cleared")

    def get_custom_words(self) -> list[str]:
        """
        Get all words in the custom dictionary.

        Returns:
            List of custom words (sorted alphabetically)
        """
        return sorted(self._custom_dictionary)

    def set_language(self, language: str) -> None:
        """
        Change the spell checker language.

        Args:
            language: Language code (e.g., 'en', 'es', 'fr', 'de')

        Example:
            >>> checker = SpellChecker()
            >>> checker.set_language('es')
        """
        # Lazy import: Load pyspellchecker only when needed
        from spellchecker import SpellChecker as PySpellChecker

        self._spell = PySpellChecker(language=language)
        self._language = language
        logger.info(f"Language changed to: {language}")

    def get_language(self) -> str:
        """
        Get the current language.

        Returns:
            Current language code
        """
        return self._language
