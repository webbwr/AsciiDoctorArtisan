#!/usr/bin/env python3
"""
Readability Checker - Grandmaster TechWriter Support Tool

Automatically tests documentation for Grade 5.0 readability while preserving
technical accuracy. Uses Flesch-Kincaid metrics and custom analysis.

Usage:
    python scripts/readability_check.py <file.md>
    python scripts/readability_check.py --stdin < file.md
"""

import re
import sys
import argparse
from typing import Dict, List, Tuple
from pathlib import Path


def count_syllables(word: str) -> int:
    """
    Count syllables in a word.

    Uses simple heuristics:
    - Count vowel groups
    - Adjust for common patterns
    """
    word = word.lower().strip()

    # Remove common suffixes that don't add syllables
    word = re.sub(r'(es|ed|e)$', '', word)

    # Count vowel groups
    vowel_groups = re.findall(r'[aeiouy]+', word)
    syllable_count = len(vowel_groups)

    # Minimum 1 syllable per word
    return max(1, syllable_count)


def flesch_reading_ease(text: str) -> float:
    """
    Calculate Flesch Reading Ease score.

    Formula: 206.835 - 1.015(total words/total sentences)
                      - 84.6(total syllables/total words)

    Score interpretation:
    90-100: Very Easy (5th grade)
    80-89:  Easy (6th grade)
    70-79:  Fairly Easy (7th grade)
    60-69:  Standard (8th-9th grade)
    <60:    Difficult (college+)
    """
    sentences = split_sentences(text)
    words = split_words(text)

    if not sentences or not words:
        return 0.0

    total_sentences = len(sentences)
    total_words = len(words)
    total_syllables = sum(count_syllables(word) for word in words)

    # Flesch Reading Ease formula
    score = (
        206.835
        - 1.015 * (total_words / total_sentences)
        - 84.6 * (total_syllables / total_words)
    )

    return round(score, 1)


def flesch_kincaid_grade(text: str) -> float:
    """
    Calculate Flesch-Kincaid Grade Level.

    Formula: 0.39(total words/total sentences)
           + 11.8(total syllables/total words)
           - 15.59

    Returns US grade level (e.g., 5.0 = 5th grade)
    """
    sentences = split_sentences(text)
    words = split_words(text)

    if not sentences or not words:
        return 0.0

    total_sentences = len(sentences)
    total_words = len(words)
    total_syllables = sum(count_syllables(word) for word in words)

    # Flesch-Kincaid Grade Level formula
    grade = (
        0.39 * (total_words / total_sentences)
        + 11.8 * (total_syllables / total_words)
        - 15.59
    )

    return round(grade, 1)


def split_sentences(text: str) -> List[str]:
    """Split text into sentences, handling common abbreviations."""
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', '', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Split on sentence boundaries
    sentences = re.split(r'[.!?]+\s+', text)

    # Filter empty and very short
    return [s.strip() for s in sentences if len(s.strip()) > 2]


def split_words(text: str) -> List[str]:
    """Split text into words, removing markup and code."""
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', '', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Remove markdown formatting
    text = re.sub(r'[*_~`#\[\]()]', '', text)

    # Split on whitespace and punctuation
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

    return [w for w in words if len(w) > 0]


def analyze_sentence_length(text: str) -> Dict[str, float]:
    """Analyze sentence length statistics."""
    sentences = split_sentences(text)

    if not sentences:
        return {'avg': 0, 'min': 0, 'max': 0}

    lengths = [len(split_words(s)) for s in sentences]

    return {
        'avg': round(sum(lengths) / len(lengths), 1),
        'min': min(lengths),
        'max': max(lengths),
        'total': len(sentences)
    }


def analyze_syllables_per_word(text: str) -> Dict[str, float]:
    """Analyze syllables per word statistics."""
    words = split_words(text)

    if not words:
        return {'avg': 0, 'min': 0, 'max': 0}

    syllable_counts = [count_syllables(word) for word in words]

    return {
        'avg': round(sum(syllable_counts) / len(syllable_counts), 2),
        'min': min(syllable_counts),
        'max': max(syllable_counts),
        'total_words': len(words)
    }


def find_complex_words(text: str, min_syllables: int = 3) -> List[Tuple[str, int]]:
    """Find words with many syllables (complexity indicators)."""
    words = split_words(text)

    complex_words = []
    for word in set(words):  # Unique words only
        syllables = count_syllables(word)
        if syllables >= min_syllables and len(word) > 4:
            complex_words.append((word, syllables))

    # Sort by syllable count descending
    return sorted(complex_words, key=lambda x: x[1], reverse=True)[:20]


def find_long_sentences(text: str, threshold: int = 20) -> List[Tuple[str, int]]:
    """Find sentences exceeding word count threshold."""
    sentences = split_sentences(text)

    long_sentences = []
    for sentence in sentences:
        word_count = len(split_words(sentence))
        if word_count > threshold:
            # Truncate for display
            preview = sentence[:80] + '...' if len(sentence) > 80 else sentence
            long_sentences.append((preview, word_count))

    return sorted(long_sentences, key=lambda x: x[1], reverse=True)[:10]


def check_ma_principles(text: str) -> Dict[str, any]:
    """Check for Japanese MA (negative space) principles."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    # Check paragraph length (MA: keep them short)
    avg_paragraph_sentences = sum(
        len(split_sentences(p)) for p in paragraphs
    ) / len(paragraphs) if paragraphs else 0

    # Check white space (blank lines between paragraphs)
    has_white_space = '\n\n' in text

    # Check for variety in sentence length (rhythm)
    sentences = split_sentences(text)
    if len(sentences) > 3:
        lengths = [len(split_words(s)) for s in sentences[:10]]
        variety = max(lengths) - min(lengths) if lengths else 0
    else:
        variety = 0

    return {
        'avg_sentences_per_paragraph': round(avg_paragraph_sentences, 1),
        'has_white_space': has_white_space,
        'sentence_variety': variety > 5,  # Good variety
        'total_paragraphs': len(paragraphs)
    }


def check_socratic_elements(text: str) -> Dict[str, any]:
    """Check for Socratic teaching elements."""
    # Count questions
    questions = len(re.findall(r'\?', text))

    # Check for progressive building (headings indicate structure)
    headings = len(re.findall(r'^#{1,6}\s+', text, re.MULTILINE))

    # Check for examples (look for "example:", "for instance", etc.)
    examples = len(re.findall(
        r'\b(example|for instance|such as|like this)\b',
        text,
        re.IGNORECASE
    ))

    return {
        'questions': questions,
        'has_questions': questions > 0,
        'headings': headings,
        'examples': examples,
        'progressive_structure': headings > 2
    }


def generate_report(text: str) -> Dict:
    """Generate comprehensive readability report."""
    fre = flesch_reading_ease(text)
    fk_grade = flesch_kincaid_grade(text)
    sentence_stats = analyze_sentence_length(text)
    syllable_stats = analyze_syllables_per_word(text)
    complex_words = find_complex_words(text)
    long_sentences = find_long_sentences(text)
    ma_check = check_ma_principles(text)
    socratic_check = check_socratic_elements(text)

    # Determine pass/fail
    passes = (
        fk_grade <= 5.0 and
        fre >= 70 and
        sentence_stats['avg'] <= 15 and
        syllable_stats['avg'] <= 1.5
    )

    # Grade interpretation
    if fk_grade <= 5.0:
        grade_desc = "Elementary (Target achieved!)"
    elif fk_grade <= 6.0:
        grade_desc = "6th grade (Close to target)"
    elif fk_grade <= 8.0:
        grade_desc = "Middle school (Needs simplification)"
    else:
        grade_desc = "High school+ (Significant simplification needed)"

    # Reading ease interpretation
    if fre >= 90:
        ease_desc = "Very Easy"
    elif fre >= 80:
        ease_desc = "Easy"
    elif fre >= 70:
        ease_desc = "Fairly Easy"
    elif fre >= 60:
        ease_desc = "Standard"
    else:
        ease_desc = "Difficult"

    return {
        'passes': passes,
        'readability': {
            'flesch_kincaid_grade': fk_grade,
            'grade_description': grade_desc,
            'flesch_reading_ease': fre,
            'ease_description': ease_desc,
            'target_grade': 5.0,
            'target_ease': 70
        },
        'sentence_stats': sentence_stats,
        'syllable_stats': syllable_stats,
        'complex_words': complex_words,
        'long_sentences': long_sentences,
        'ma_principles': ma_check,
        'socratic_elements': socratic_check
    }


def format_report(report: Dict) -> str:
    """Format report as readable text."""
    r = report['readability']
    ss = report['sentence_stats']
    sy = report['syllable_stats']

    status = "✓ PASS" if report['passes'] else "✗ NEEDS WORK"

    output = f"""
{'='*70}
READABILITY REPORT - {status}
{'='*70}

GRADE LEVEL METRICS
-------------------
Flesch-Kincaid Grade: {r['flesch_kincaid_grade']} ({r['grade_description']})
  Target: ≤ {r['target_grade']} ({'✓' if r['flesch_kincaid_grade'] <= r['target_grade'] else '✗'})

Reading Ease Score: {r['flesch_reading_ease']} ({r['ease_description']})
  Target: ≥ {r['target_ease']} ({'✓' if r['flesch_reading_ease'] >= r['target_ease'] else '✗'})

SENTENCE ANALYSIS
-----------------
Average Length: {ss['avg']} words ({'✓' if ss['avg'] <= 15 else '✗'} target: ≤15)
Range: {ss['min']}-{ss['max']} words
Total Sentences: {ss['total']}

WORD ANALYSIS
-------------
Average Syllables: {sy['avg']} per word ({'✓' if sy['avg'] <= 1.5 else '✗'} target: ≤1.5)
Total Words: {sy['total_words']}
"""

    # Long sentences
    if report['long_sentences']:
        output += "\nLONG SENTENCES (>20 words)\n"
        output += "-" * 70 + "\n"
        for sentence, count in report['long_sentences'][:5]:
            output += f"• {count} words: {sentence}\n"

    # Complex words
    if report['complex_words']:
        output += "\nCOMPLEX WORDS (3+ syllables)\n"
        output += "-" * 70 + "\n"
        words_display = ", ".join(f"{w} ({s})" for w, s in report['complex_words'][:15])
        output += f"{words_display}\n"

    # MA principles
    ma = report['ma_principles']
    output += f"""
MA (NEGATIVE SPACE) PRINCIPLES
------------------------------
Sentences per paragraph: {ma['avg_sentences_per_paragraph']} ({'✓' if ma['avg_sentences_per_paragraph'] <= 4 else '✗'} target: ≤4)
Has white space: {'✓ Yes' if ma['has_white_space'] else '✗ No'}
Sentence variety: {'✓ Yes' if ma['sentence_variety'] else '✗ No'}
Total paragraphs: {ma['total_paragraphs']}
"""

    # Socratic elements
    soc = report['socratic_elements']
    output += f"""
SOCRATIC ELEMENTS
-----------------
Questions used: {soc['questions']} ({'✓' if soc['has_questions'] else '✗'} should use questions)
Headings (structure): {soc['headings']} ({'✓' if soc['progressive_structure'] else '✗'})
Examples provided: {soc['examples']}
"""

    # Recommendations
    output += "\nRECOMMENDATIONS\n"
    output += "-" * 70 + "\n"

    recommendations = []

    if r['flesch_kincaid_grade'] > 5.0:
        recommendations.append("• Simplify: Break long sentences into shorter ones (10-15 words)")

    if r['flesch_reading_ease'] < 70:
        recommendations.append("• Use simpler words: Replace complex words with common alternatives")

    if ss['avg'] > 15:
        recommendations.append("• Shorten sentences: Current average is too long")

    if sy['avg'] > 1.5:
        recommendations.append("• Reduce syllables: Use 1-2 syllable words where possible")

    if not ma['has_white_space']:
        recommendations.append("• Add white space: Include blank lines between paragraphs")

    if not soc['has_questions']:
        recommendations.append("• Add questions: Use Socratic method to engage readers")

    if report['long_sentences']:
        recommendations.append(f"• Fix {len(report['long_sentences'])} long sentences (see above)")

    if not recommendations:
        recommendations.append("✓ Excellent! Document meets all readability targets.")

    output += "\n".join(recommendations)

    output += f"\n\n{'='*70}\n"

    return output


def main():
    parser = argparse.ArgumentParser(
        description='Check readability of technical documentation (Target: Grade 5.0)'
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='Markdown file to analyze'
    )
    parser.add_argument(
        '--stdin',
        action='store_true',
        help='Read from stdin instead of file'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON instead of formatted report'
    )

    args = parser.parse_args()

    # Read input
    if args.stdin:
        text = sys.stdin.read()
    elif args.file:
        text = Path(args.file).read_text(encoding='utf-8')
    else:
        parser.print_help()
        sys.exit(1)

    # Generate report
    report = generate_report(text)

    # Output
    if args.json:
        import json
        print(json.dumps(report, indent=2))
    else:
        print(format_report(report))

    # Exit code: 0 if passes, 1 if needs work
    sys.exit(0 if report['passes'] else 1)


if __name__ == '__main__':
    main()
