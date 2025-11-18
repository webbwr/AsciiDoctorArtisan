"""
Search Engine - Text search and replace functionality for AsciiDoc Artisan.

This module provides fast, flexible text search with support for:
- Case-sensitive and case-insensitive search
- Whole word matching
- Regular expression patterns
- Find all occurrences
- Replace single or all matches

Performance targets:
- Search operations complete in <50ms for documents up to 10,000 lines
- Memory-efficient iteration over large documents
- Incremental search support for live-as-you-type

Example:
    >>> engine = SearchEngine("Hello world, hello Python!")
    >>> results = engine.find_all("hello", case_sensitive=False)
    >>> len(results)
    2
    >>> results[0].start
    0
"""

import bisect
import logging
import re
from dataclasses import dataclass
from re import Pattern

logger = logging.getLogger(__name__)


@dataclass
class SearchMatch:
    """
    Represents a single search match in the text.

    Attributes:
        start: Character offset where match starts (0-indexed)
        end: Character offset where match ends (exclusive)
        text: The matched text
        line: Line number where match occurs (1-indexed)
        column: Column number where match starts (0-indexed)
    """

    start: int
    end: int
    text: str
    line: int
    column: int

    def __len__(self) -> int:
        """Return length of matched text."""
        return self.end - self.start

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"SearchMatch(line={self.line}, col={self.column}, text='{self.text}')"


class SearchEngine:
    """
    High-performance text search engine with multiple search modes.

    This class provides efficient text search with support for various
    search options including case sensitivity, whole word matching, and
    regular expressions.

    Example:
        >>> engine = SearchEngine("Line 1\\nLine 2\\nLine 3")
        >>> matches = engine.find_all("Line", case_sensitive=True)
        >>> len(matches)
        3
    """

    def __init__(self, text: str) -> None:
        """
        Initialize SearchEngine with text to search.

        Args:
            text: The text to search within
        """
        self._text = text
        self._lines: list[str] | None = None  # Lazy-loaded line cache
        self._line_offsets: list[int] | None = None  # Lazy-loaded offset index

    @property
    def text(self) -> str:
        """Get the current text being searched."""
        return self._text

    def set_text(self, text: str) -> None:
        """
        Update the text to search.

        Args:
            text: New text to search within
        """
        self._text = text
        self._lines = None  # Invalidate line cache
        self._line_offsets = None  # Invalidate offset index

    def _get_lines(self) -> list[str]:
        """
        Get cached list of lines (lazy-loaded).

        Returns:
            List of lines in the text
        """
        if self._lines is None:
            self._lines = self._text.splitlines(keepends=True)
        return self._lines

    def _build_line_offsets(self) -> list[int]:
        """
        Build line offset index for fast O(log n) line lookup.

        Returns:
            List of cumulative character offsets for each line start.
            Index i contains the offset where line i starts.

        Example:
            For text "abc\\ndef\\n":
            Returns [0, 4] (line 0 at offset 0, line 1 at offset 4)
        """
        if self._line_offsets is None:
            lines = self._get_lines()
            offsets = [0]  # First line always starts at offset 0
            current_offset = 0

            for line in lines:
                current_offset += len(line)
                offsets.append(current_offset)

            self._line_offsets = offsets

        return self._line_offsets

    def _create_pattern(
        self,
        search_text: str,
        case_sensitive: bool = True,
        whole_word: bool = False,
        use_regex: bool = False,
    ) -> Pattern[str]:
        """
        Create compiled regex pattern from search options.

        Args:
            search_text: Text or pattern to search for
            case_sensitive: Whether search is case-sensitive
            whole_word: Whether to match whole words only
            use_regex: Whether search_text is a regex pattern

        Returns:
            Compiled regex pattern

        Raises:
            re.error: If regex pattern is invalid
        """
        # Build pattern
        if use_regex:
            pattern = search_text
        else:
            # Escape special regex characters for literal search
            pattern = re.escape(search_text)

        # Add word boundary markers if whole word matching
        if whole_word:
            pattern = r"\b" + pattern + r"\b"

        # Compile with appropriate flags
        flags = 0 if case_sensitive else re.IGNORECASE
        return re.compile(pattern, flags)

    def _offset_to_line_col(self, offset: int) -> tuple[int, int]:
        """
        Convert character offset to line and column numbers using binary search.

        Performance: O(log n) instead of O(n) through binary search on offset index.

        Args:
            offset: Character offset in text (0-indexed)

        Returns:
            Tuple of (line_number, column_number)
            - line_number is 1-indexed
            - column_number is 0-indexed within the line
        """
        offsets = self._build_line_offsets()
        lines = self._get_lines()

        # Binary search to find line number (O(log n))
        # bisect_right returns the index where offset would be inserted
        # Subtract 1 to get the line that contains this offset
        line_num = bisect.bisect_right(offsets, offset) - 1

        # Edge case: offset at end of text (beyond all lines)
        if line_num >= len(lines):
            return (len(lines), 0)

        # Calculate column within the line
        column = offset - offsets[line_num]

        # Return 1-indexed line number
        return (line_num + 1, column)

    def find_all(
        self,
        search_text: str,
        case_sensitive: bool = True,
        whole_word: bool = False,
        use_regex: bool = False,
    ) -> list[SearchMatch]:
        """
        Find all occurrences of search_text in the document.

        Args:
            search_text: Text or pattern to search for
            case_sensitive: Whether search is case-sensitive (default: True)
            whole_word: Whether to match whole words only (default: False)
            use_regex: Whether search_text is a regex pattern (default: False)

        Returns:
            List of SearchMatch objects, in order of appearance

        Raises:
            ValueError: If search_text is empty
            re.error: If use_regex=True and pattern is invalid

        Example:
            >>> engine = SearchEngine("Hello world, hello Python!")
            >>> results = engine.find_all("hello", case_sensitive=False)
            >>> len(results)
            2
        """
        if not search_text:
            raise ValueError("Search text cannot be empty")

        try:
            pattern = self._create_pattern(search_text, case_sensitive, whole_word, use_regex)
        except re.error as e:
            logger.error(f"Invalid regex pattern: {search_text} - {e}")
            raise

        matches: list[SearchMatch] = []

        # Find all matches using regex
        for match in pattern.finditer(self._text):
            start = match.start()
            end = match.end()
            matched_text = match.group(0)
            line, column = self._offset_to_line_col(start)

            matches.append(
                SearchMatch(
                    start=start,
                    end=end,
                    text=matched_text,
                    line=line,
                    column=column,
                )
            )

        logger.debug(
            f"Found {len(matches)} matches for '{search_text}' "
            f"(case_sensitive={case_sensitive}, whole_word={whole_word}, "
            f"use_regex={use_regex})"
        )

        return matches

    def find_next(
        self,
        search_text: str,
        start_offset: int = 0,
        case_sensitive: bool = True,
        whole_word: bool = False,
        use_regex: bool = False,
        wrap_around: bool = True,
    ) -> SearchMatch | None:
        """
        Find next occurrence after start_offset.

        Args:
            search_text: Text or pattern to search for
            start_offset: Character offset to start searching from (default: 0)
            case_sensitive: Whether search is case-sensitive (default: True)
            whole_word: Whether to match whole words only (default: False)
            use_regex: Whether search_text is a regex pattern (default: False)
            wrap_around: Whether to wrap to beginning if no match found (default: True)

        Returns:
            SearchMatch if found, None otherwise

        Example:
            >>> engine = SearchEngine("Hello world, hello Python!")
            >>> match = engine.find_next("hello", case_sensitive=False)
            >>> match.start
            0
            >>> match = engine.find_next("hello", start_offset=1, case_sensitive=False)
            >>> match.start
            13
        """
        if not search_text:
            raise ValueError("Search text cannot be empty")

        try:
            pattern = self._create_pattern(search_text, case_sensitive, whole_word, use_regex)
        except re.error as e:
            logger.error(f"Invalid regex pattern: {search_text} - {e}")
            raise

        # Search from start_offset to end
        match = pattern.search(self._text, start_offset)

        # If no match and wrap_around enabled, search from beginning
        if match is None and wrap_around and start_offset > 0:
            match = pattern.search(self._text, 0, start_offset)

        if match is None:
            return None

        start = match.start()
        end = match.end()
        matched_text = match.group(0)
        line, column = self._offset_to_line_col(start)

        return SearchMatch(
            start=start,
            end=end,
            text=matched_text,
            line=line,
            column=column,
        )

    def find_previous(
        self,
        search_text: str,
        start_offset: int,
        case_sensitive: bool = True,
        whole_word: bool = False,
        use_regex: bool = False,
        wrap_around: bool = True,
    ) -> SearchMatch | None:
        """
        Find previous occurrence before start_offset.

        Args:
            search_text: Text or pattern to search for
            start_offset: Character offset to search backwards from
            case_sensitive: Whether search is case-sensitive (default: True)
            whole_word: Whether to match whole words only (default: False)
            use_regex: Whether search_text is a regex pattern (default: False)
            wrap_around: Whether to wrap to end if no match found (default: True)

        Returns:
            SearchMatch if found, None otherwise
        """
        if not search_text:
            raise ValueError("Search text cannot be empty")

        try:
            pattern = self._create_pattern(search_text, case_sensitive, whole_word, use_regex)
        except re.error as e:
            logger.error(f"Invalid regex pattern: {search_text} - {e}")
            raise

        # Find all matches before start_offset
        matches = []
        for match in pattern.finditer(self._text, 0, start_offset):
            matches.append(match)

        # If no matches and wrap_around, search from start_offset to end
        if not matches and wrap_around:
            for match in pattern.finditer(self._text, start_offset):
                matches.append(match)

        if not matches:
            return None

        # Return last match (closest to start_offset)
        match = matches[-1]
        start = match.start()
        end = match.end()
        matched_text = match.group(0)
        line, column = self._offset_to_line_col(start)

        return SearchMatch(
            start=start,
            end=end,
            text=matched_text,
            line=line,
            column=column,
        )

    def replace_all(
        self,
        search_text: str,
        replace_text: str,
        case_sensitive: bool = True,
        whole_word: bool = False,
        use_regex: bool = False,
    ) -> tuple[str, int]:
        """
        Replace all occurrences of search_text with replace_text.

        Args:
            search_text: Text or pattern to search for
            replace_text: Text to replace with (supports regex backreferences if use_regex=True)
            case_sensitive: Whether search is case-sensitive (default: True)
            whole_word: Whether to match whole words only (default: False)
            use_regex: Whether search_text is a regex pattern (default: False)

        Returns:
            Tuple of (new_text, count) where:
            - new_text is the text with replacements made
            - count is the number of replacements made

        Example:
            >>> engine = SearchEngine("Hello world, hello Python!")
            >>> new_text, count = engine.replace_all("hello", "hi", case_sensitive=False)
            >>> count
            2
            >>> new_text
            'hi world, hi Python!'
        """
        if not search_text:
            raise ValueError("Search text cannot be empty")

        try:
            pattern = self._create_pattern(search_text, case_sensitive, whole_word, use_regex)
        except re.error as e:
            logger.error(f"Invalid regex pattern: {search_text} - {e}")
            raise

        # Use regex sub to replace all occurrences
        new_text, count = pattern.subn(replace_text, self._text)

        logger.info(f"Replaced {count} occurrences of '{search_text}' with '{replace_text}'")

        return (new_text, count)
