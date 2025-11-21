"""
Document Metrics Calculator - Analyzes document content for metrics display.

Extracted from StatusManager to reduce class size (MA principle).
Handles document version extraction, word counting, and readability grade calculation.
"""

import re

# Pre-compiled regex patterns (hot path optimization, v1.9.1)
# Compiling at module level is 2-3x faster than compiling on each call
VERSION_PATTERNS = [
    # AsciiDoc attributes (most specific)
    re.compile(r"^\s*:revnumber:\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^\s*:version:\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^\s*:rev:\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    # Text-based version labels with colon (bold or plain)
    re.compile(r"^\s*\*Version\*:\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^\s*\*version\*:\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^\s*Version:\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^\s*version:\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    # Version in title/heading
    re.compile(r"\bv(\d+\.\d+(?:\.\d+)?)\b", re.MULTILINE | re.IGNORECASE),
    re.compile(r"\bVersion\s+(\d+\.\d+(?:\.\d+)?)\b", re.MULTILINE | re.IGNORECASE),
    re.compile(r"\bversion\s+(\d+\.\d+(?:\.\d+)?)\b", re.MULTILINE | re.IGNORECASE),
    # Standalone version with v prefix
    re.compile(r"^\s*v(\d+\.\d+(?:\.\d+)?)$", re.MULTILINE | re.IGNORECASE),
    # Standalone version without v prefix
    re.compile(r"^\s*(\d+\.\d+(?:\.\d+)?)$", re.MULTILINE | re.IGNORECASE),
]
TRAILING_ASTERISKS = re.compile(r"\*+$")
ASCIIDOC_ATTRIBUTES = re.compile(r"^:.*?:.*?$", re.MULTILINE)
ASCIIDOC_COMMENTS = re.compile(r"^//.*?$", re.MULTILINE)
ASCIIDOC_BLOCKS = re.compile(r"^\[.*?\]$", re.MULTILINE)
ASCIIDOC_INLINE_MARKUP = re.compile(r"\*\*|__|\*|_|`")
SENTENCE_SPLITTER = re.compile(r"[.!?]+")
SYLLABLE_VOWELS = re.compile(r"[aeiouy]+")


class DocumentMetricsCalculator:
    """
    Document metrics calculator for version, word count, and readability.

    This class was extracted from StatusManager to reduce class size
    per MA principle (609→~400 lines).

    Handles:
    - Document version extraction (AsciiDoc attributes and text patterns)
    - Word counting (excludes markup)
    - Flesch-Kincaid grade level calculation
    """

    def extract_document_version(self, text: str) -> str | None:
        """Extract document version from AsciiDoc attributes or text.

        Looks for:
        - AsciiDoc attributes: :revnumber:, :version:, :rev:
        - Text patterns: *Version*:, Version:, v1.2.3

        Args:
            text: AsciiDoc document content

        Returns:
            Version string or None if not found
        """
        # Use pre-compiled patterns (2-3x faster than compiling on each call)
        for pattern in VERSION_PATTERNS:
            match = pattern.search(text)
            if match:
                version = match.group(1).strip()
                # Clean up any trailing markup (use pre-compiled pattern)
                version = TRAILING_ASTERISKS.sub("", version)
                return version

        return None

    def count_words(self, text: str) -> int:
        """Count words in document content.

        Args:
            text: Document content

        Returns:
            Word count
        """
        # Remove AsciiDoc attributes and comments (use pre-compiled patterns)
        text = ASCIIDOC_ATTRIBUTES.sub("", text)
        text = ASCIIDOC_COMMENTS.sub("", text)

        # Split on whitespace and count
        words = text.split()
        return len(words)

    def calculate_grade_level(self, text: str) -> float:
        """Calculate Flesch-Kincaid grade level.

        Args:
            text: Document content

        Returns:
            Grade level (e.g., 5.23 = 5th grade reading level)
        """
        # Remove AsciiDoc markup (use pre-compiled patterns)
        text = ASCIIDOC_ATTRIBUTES.sub("", text)
        text = ASCIIDOC_COMMENTS.sub("", text)
        text = ASCIIDOC_BLOCKS.sub("", text)
        text = ASCIIDOC_INLINE_MARKUP.sub("", text)

        # Count sentences (use pre-compiled pattern)
        sentences = SENTENCE_SPLITTER.split(text)
        sentences = [s.strip() for s in sentences if s.strip()]
        num_sentences = len(sentences)

        if num_sentences == 0:
            return 0.0

        # Count words
        words = text.split()
        num_words = len(words)

        if num_words == 0:
            return 0.0

        # Count syllables (use pre-compiled pattern, hot path in loop)
        num_syllables = 0
        for word in words:
            word = word.lower()
            syllable_count = len(SYLLABLE_VOWELS.findall(word))
            # Adjust for silent e
            if word.endswith("e"):
                syllable_count -= 1
            # Minimum 1 syllable per word
            num_syllables += max(1, syllable_count)

        # Flesch-Kincaid Grade Level formula
        # 0.39 * (total words / total sentences) + 11.8 * (total syllables / total words) - 15.59
        grade = 0.39 * (num_words / num_sentences) + 11.8 * (num_syllables / num_words) - 15.59

        return round(max(0.0, grade), 2)

    def interpret_grade_level(self, grade: float) -> tuple[str, str]:
        """
        Interpret grade level for tooltip display.

        Args:
            grade: Grade level

        Returns:
            Tuple of (difficulty, audience)
        """
        if grade <= 5:
            return ("Elementary", "Easy to read for most audiences")
        elif grade <= 8:
            return ("Middle School", "Accessible to general readers")
        elif grade <= 12:
            return ("High School", "Suitable for educated readers")
        elif grade <= 16:
            return ("College", "Technical or academic content")
        else:
            return ("Graduate", "Complex academic content")
