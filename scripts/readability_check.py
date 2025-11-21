#!/usr/bin/env python3
"""
Simple readability checker for documentation files.
Calculates Flesch-Kincaid Grade Level.
"""

import re
import sys
from pathlib import Path


def count_syllables(word: str) -> int:
    """Count syllables in a word using simple heuristic."""
    word = word.lower()
    vowels = "aeiouy"
    syllable_count = 0
    previous_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel

    # Adjust for silent 'e'
    if word.endswith("e"):
        syllable_count -= 1

    # Every word has at least one syllable
    return max(1, syllable_count)


def calculate_flesch_kincaid_grade(text: str) -> float:
    """Calculate Flesch-Kincaid Grade Level."""
    # Remove markdown formatting
    text = re.sub(r"[#*`_\[\](){}]", "", text)

    # Split into sentences (simple heuristic)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Split into words
    words = re.findall(r"\b[a-zA-Z]+\b", text)

    if not sentences or not words:
        return 0.0

    # Count syllables
    total_syllables = sum(count_syllables(word) for word in words)

    # Calculate Flesch-Kincaid Grade Level
    # Formula: 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    avg_words_per_sentence = len(words) / len(sentences)
    avg_syllables_per_word = total_syllables / len(words)

    grade = 0.39 * avg_words_per_sentence + 11.8 * avg_syllables_per_word - 15.59

    return max(0.0, grade)


def main():
    if len(sys.argv) < 2:
        print("Usage: readability_check.py <file>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: File {file_path} not found")
        sys.exit(1)

    try:
        text = file_path.read_text(encoding="utf-8")
        grade = calculate_flesch_kincaid_grade(text)
        print(f"Grade Level: {grade:.1f}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
