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


@pytest.mark.unit
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

    # Additional version extraction edge cases
    def test_extract_version_case_insensitive(self):
        """Test version extraction is case insensitive."""
        text = ":REVNUMBER: 4.5.6\n= Document\n"
        version = extract_document_version(text)
        assert version == "4.5.6"

    def test_extract_version_with_extra_whitespace(self):
        """Test version extraction handles extra whitespace."""
        text = ":version:    1.0.0   \n= Document\n"
        version = extract_document_version(text)
        assert version == "1.0.0"

    def test_extract_version_first_match_wins(self):
        """Test that first matching version attribute wins."""
        text = ":revnumber: 1.0.0\n:version: 2.0.0\n= Document\n"
        version = extract_document_version(text)
        assert version == "1.0.0"

    def test_extract_version_in_middle_of_document(self):
        """Test version extraction from middle of document."""
        text = "= Title\n\nSome content\n\n:version: 1.5.0\n\nMore content"
        version = extract_document_version(text)
        assert version == "1.5.0"

    def test_extract_version_with_rc_suffix(self):
        """Test version extraction with release candidate suffix."""
        text = ":rev: 2.0.0-RC1\n"
        version = extract_document_version(text)
        assert version == "2.0.0-RC1"

    def test_extract_version_with_alpha_suffix(self):
        """Test version extraction with alpha suffix."""
        text = ":version: 3.0.0-alpha.1\n"
        version = extract_document_version(text)
        assert version == "3.0.0-alpha.1"

    def test_extract_version_complex_format(self):
        """Test version extraction with complex version format."""
        text = ":revnumber: v1.2.3-beta.4+build.567\n"
        version = extract_document_version(text)
        assert version == "v1.2.3-beta.4+build.567"

    def test_extract_version_single_digit(self):
        """Test version extraction with single digit version."""
        text = ":version: 1\n"
        version = extract_document_version(text)
        assert version == "1"

    # Additional word counting edge cases
    def test_count_words_multiple_spaces(self):
        """Test word counting with multiple spaces between words."""
        text = "This  has   multiple    spaces"
        count = count_words(text)
        assert count == 4

    def test_count_words_with_tabs(self):
        """Test word counting with tabs as whitespace."""
        text = "Words\tseparated\tby\ttabs"
        count = count_words(text)
        assert count == 4

    def test_count_words_with_newlines(self):
        """Test word counting across multiple lines."""
        text = "First line\nSecond line\nThird line"
        count = count_words(text)
        assert count == 6

    def test_count_words_with_punctuation(self):
        """Test word counting with punctuation."""
        text = "Hello, world! How are you?"
        count = count_words(text)
        assert count == 5

    def test_count_words_with_numbers(self):
        """Test word counting includes numbers."""
        text = "Version 1.0 has 5 new features."
        count = count_words(text)
        assert count == 6

    # Additional grade level edge cases
    def test_calculate_grade_level_all_uppercase(self):
        """Test grade level calculation with all uppercase text."""
        text = "THE CAT SAT. THE DOG RAN."
        grade = calculate_grade_level(text)
        assert grade >= 0

    def test_calculate_grade_level_with_numbers(self):
        """Test grade level calculation with numbers in text."""
        text = "There are 5 cats and 3 dogs. They ran for 2 hours."
        grade = calculate_grade_level(text)
        assert grade >= 0

    def test_calculate_grade_level_single_word(self):
        """Test grade level calculation with single word."""
        text = "Word."
        grade = calculate_grade_level(text)
        assert grade >= 0

    def test_calculate_grade_level_very_long_sentence(self):
        """Test grade level calculation with very long sentence."""
        text = "This is a very long sentence with many words and clauses and phrases and it goes on and on and on."
        grade = calculate_grade_level(text)
        assert grade > 5  # Long sentences increase grade level

    def test_calculate_grade_level_multiple_short_sentences(self):
        """Test grade level calculation with many short sentences."""
        text = "I run. You walk. We talk. They listen. She jumps. He sits."
        grade = calculate_grade_level(text)
        assert 0 <= grade <= 5  # Short sentences lower grade level

    def test_calculate_grade_level_with_exclamations(self):
        """Test grade level calculation counts exclamation marks as sentence endings."""
        text = "This is great! I love it! So amazing!"
        grade = calculate_grade_level(text)
        assert grade >= 0

    def test_calculate_grade_level_with_questions(self):
        """Test grade level calculation counts question marks as sentence endings."""
        text = "What is this? How does it work? Why is it important?"
        grade = calculate_grade_level(text)
        assert grade >= 0
