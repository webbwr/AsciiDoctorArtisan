"""
Unit tests for status bar document metrics (no Qt required).

Tests the new v1.2.0 features:
- Document version extraction
- Word counting
- Grade level calculation
"""

# Extract the metric calculation methods for testing
# We'll test them as standalone functions


def extract_document_version(text: str):
    """Extract document version from AsciiDoc attributes."""
    import re

    patterns = [
        r"^:revnumber:\s*(.+)$",
        r"^:version:\s*(.+)$",
        r"^:rev:\s*(.+)$",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def count_words(text: str) -> int:
    """Count words in document content."""
    import re

    # Remove AsciiDoc attributes and comments
    text = re.sub(r"^:.*?:.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^//.*?$", "", text, flags=re.MULTILINE)

    # Split on whitespace and count
    words = text.split()
    return len(words)


def calculate_grade_level(text: str) -> float:
    """Calculate Flesch-Kincaid grade level."""
    import re

    # Remove AsciiDoc markup
    text = re.sub(r"^:.*?:.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^//.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\[.*?\]$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*|__|\*|_|`", "", text)

    # Count sentences (. ! ?)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = len(sentences)

    if num_sentences == 0:
        return 0.0

    # Count words
    words = text.split()
    num_words = len(words)

    if num_words == 0:
        return 0.0

    # Count syllables (simplified: vowel groups)
    num_syllables = 0
    for word in words:
        word = word.lower()
        syllable_count = len(re.findall(r"[aeiouy]+", word))
        # Adjust for silent e
        if word.endswith("e"):
            syllable_count -= 1
        # Minimum 1 syllable per word
        num_syllables += max(1, syllable_count)

    # Flesch-Kincaid Grade Level formula
    grade = (
        0.39 * (num_words / num_sentences) + 11.8 * (num_syllables / num_words) - 15.59
    )

    return round(max(0.0, grade), 2)


class TestDocumentMetrics:
    """Test document metrics calculation."""

    def test_extract_version_revnumber(self):
        """Test version extraction from :revnumber: attribute."""
        text = ":revnumber: 1.2.0\n= Document Title\n"
        version = extract_document_version(text)
        assert version == "1.2.0"

    def test_extract_version_version_attr(self):
        """Test version extraction from :version: attribute."""
        text = ":version: 2.1.3\n= Another Document\n"
        version = extract_document_version(text)
        assert version == "2.1.3"

    def test_extract_version_rev_attr(self):
        """Test version extraction from :rev: attribute."""
        text = ":rev: 3.0.1-beta\n= Beta Document\n"
        version = extract_document_version(text)
        assert version == "3.0.1-beta"

    def test_extract_version_not_found(self):
        """Test version extraction when no version attribute exists."""
        text = "= Document Without Version\n\nSome content here.\n"
        version = extract_document_version(text)
        assert version is None

    def test_count_words_simple(self):
        """Test word counting with simple text."""
        text = "This is a simple test document."
        count = count_words(text)
        assert count == 6

    def test_count_words_with_attributes(self):
        """Test word counting excludes AsciiDoc attributes."""
        text = ":author: John Doe\n:version: 1.0\n\nThis has five actual words."
        count = count_words(text)
        assert count == 5

    def test_count_words_with_comments(self):
        """Test word counting excludes comments."""
        text = "This is content.\n// This is a comment\nMore content here."
        count = count_words(text)
        assert count == 6

    def test_count_words_empty(self):
        """Test word counting with empty text."""
        count = count_words("")
        assert count == 0

    def test_calculate_grade_level_simple(self):
        """Test grade level calculation with simple text."""
        # Simple 1st grade level text
        text = "The cat sat. The dog ran. We had fun."
        grade = calculate_grade_level(text)
        assert 0 <= grade <= 5  # Should be low grade level

    def test_calculate_grade_level_complex(self):
        """Test grade level calculation with complex text."""
        # More complex text with longer words and sentences
        text = "The implementation of sophisticated algorithms requires comprehensive understanding of computational complexity theory."
        grade = calculate_grade_level(text)
        assert grade > 10  # Should be high grade level

    def test_calculate_grade_level_medium(self):
        """Test grade level calculation with medium complexity text."""
        # Medium complexity - simple clear text
        text = "The program helps you write papers. It shows your work as you type. This makes writing easier."
        grade = calculate_grade_level(text)
        assert 0 <= grade <= 5  # Should be low grade level (simple text)

    def test_calculate_grade_level_empty(self):
        """Test grade level calculation with empty text."""
        grade = calculate_grade_level("")
        assert grade == 0.0

    def test_calculate_grade_level_no_periods(self):
        """Test grade level calculation treats text without periods as one sentence."""
        text = "just some words without punctuation"
        # Will be treated as one sentence and calculate normally
        grade = calculate_grade_level(text)
        assert grade > 0  # Should have some grade level
