#!/usr/bin/env python3
"""
Simple readability checker without external dependencies.
Uses basic metrics to estimate grade level.
"""

import re
import sys
from pathlib import Path


def count_syllables(word):
    """Estimate syllables in a word."""
    word = word.lower()
    vowels = "aeiou"
    syllable_count = 0
    previous_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel

    # Adjust for silent e
    if word.endswith('e'):
        syllable_count -= 1

    # Every word has at least one syllable
    if syllable_count < 1:
        syllable_count = 1

    return syllable_count


def flesch_kincaid_grade(text):
    """Calculate Flesch-Kincaid Grade Level."""
    # Remove code blocks and special formatting
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)

    # Count sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)

    # Count words
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)

    # Count syllables
    total_syllables = sum(count_syllables(word) for word in words)

    if sentence_count == 0 or word_count == 0:
        return 0

    # Flesch-Kincaid Grade Level formula
    grade = (0.39 * (word_count / sentence_count)) + \
            (11.8 * (total_syllables / word_count)) - 15.59

    return max(0, grade)


def analyze_file(filepath):
    """Analyze a markdown file for readability."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        grade = flesch_kincaid_grade(text)

        # Categorize reading level
        if grade <= 6:
            level = "Elementary"
        elif grade <= 8:
            level = "Middle School"
        elif grade <= 12:
            level = "High School"
        elif grade <= 16:
            level = "College"
        else:
            level = "Graduate"

        return {
            'file': filepath.name,
            'grade': round(grade, 1),
            'level': level
        }
    except Exception as e:
        return {
            'file': filepath.name,
            'grade': 0,
            'level': f"Error: {e}"
        }


def main():
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
    else:
        files = list(Path('docs').glob('*.md'))
        files.append(Path('README.md'))

    results = []
    for filepath in files:
        if filepath.exists():
            result = analyze_file(filepath)
            results.append(result)

    # Print results
    print("\nReadability Analysis")
    print("=" * 60)
    print(f"{'File':<30} {'Grade':<10} {'Level':<20}")
    print("-" * 60)

    for result in sorted(results, key=lambda x: x['grade']):
        print(f"{result['file']:<30} {result['grade']:<10} {result['level']:<20}")

    print("=" * 60)
    avg_grade = sum(r['grade'] for r in results) / len(results) if results else 0
    print(f"\nAverage Grade Level: {avg_grade:.1f}")
    print("\nTarget: Grade 5-6 (Elementary)")


if __name__ == "__main__":
    main()
