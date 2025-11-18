#!/usr/bin/env python3
"""
Score all documentation files for readability.

This script analyzes all markdown files in the repository and generates
a comprehensive readability report using multiple metrics:
- Flesch-Kincaid Grade Level
- Flesch Reading Ease
- Gunning Fog Index
- SMOG Index
- Coleman-Liau Index
- Automated Readability Index

Target: Grade 5.0 or below (elementary school reading level)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import textstat
except ImportError:
    print("Error: textstat library not found")
    print("Install with: pip install textstat")
    sys.exit(1)


def clean_markdown(text: str) -> str:
    """Remove markdown formatting for readability analysis."""
    # Remove code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", "", text)

    # Remove headers
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)

    # Remove links but keep text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    # Remove images
    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", "", text)

    # Remove bold/italic
    text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^\*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # Remove bullet points
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r"^-{3,}$", "", text, flags=re.MULTILINE)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Clean up whitespace
    text = re.sub(r"\n\n+", "\n\n", text)

    return text.strip()


def score_document(file_path: Path) -> Dict[str, float]:
    """Score a single document for readability."""
    try:
        text = file_path.read_text(encoding="utf-8")
        clean_text = clean_markdown(text)

        # Skip if too short
        if len(clean_text.split()) < 100:
            return {"error": "Too short (< 100 words)"}

        scores = {
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(clean_text),
            "flesch_reading_ease": textstat.flesch_reading_ease(clean_text),
            "gunning_fog": textstat.gunning_fog(clean_text),
            "smog_index": textstat.smog_index(clean_text),
            "coleman_liau_index": textstat.coleman_liau_index(clean_text),
            "automated_readability_index": textstat.automated_readability_index(clean_text),
            "word_count": len(clean_text.split()),
            "sentence_count": textstat.sentence_count(clean_text),
            "avg_sentence_length": textstat.avg_sentence_length(clean_text),
        }

        return scores

    except Exception as e:
        return {"error": str(e)}


def categorize_score(grade: float) -> Tuple[str, str]:
    """Categorize readability grade level."""
    if grade <= 5.0:
        return "✅ EXCELLENT", "green"
    elif grade <= 8.0:
        return "✓ GOOD", "yellow"
    elif grade <= 12.0:
        return "⚠ FAIR", "orange"
    else:
        return "❌ NEEDS WORK", "red"


def find_markdown_files(root_dir: Path, exclude_dirs: List[str]) -> List[Path]:
    """Find all markdown files excluding certain directories."""
    markdown_files = []

    for md_file in root_dir.rglob("*.md"):
        # Skip excluded directories
        if any(excluded in md_file.parts for excluded in exclude_dirs):
            continue
        markdown_files.append(md_file)

    return sorted(markdown_files)


def main():
    """Main scoring function."""
    # Configuration
    repo_root = Path(__file__).parent.parent
    exclude_dirs = [
        "venv",
        "node_modules",
        ".git",
        ".pytest_cache",
        "htmlcov",
        ".claude",
    ]

    # Find all markdown files
    print("🔍 Finding markdown files...")
    md_files = find_markdown_files(repo_root, exclude_dirs)
    print(f"Found {len(md_files)} markdown files\n")

    # Score all files
    results = []
    for md_file in md_files:
        relative_path = md_file.relative_to(repo_root)
        scores = score_document(md_file)
        results.append((relative_path, scores))

    # Generate report
    print("=" * 100)
    print("DOCUMENTATION READABILITY REPORT")
    print("=" * 100)
    print("Target: Grade 5.0 or below (Elementary School Reading Level)")
    print(f"Analyzed: {len(results)} files\n")

    # Sort by grade level
    valid_results = [(path, scores) for path, scores in results if "error" not in scores]
    valid_results.sort(key=lambda x: x[1]["flesch_kincaid_grade"])

    # Print detailed results
    print("-" * 100)
    print(f"{'FILE':<60} {'GRADE':<8} {'EASE':<8} {'STATUS':<20}")
    print("-" * 100)

    excellent_count = 0
    good_count = 0
    fair_count = 0
    needs_work_count = 0
    error_count = 0

    for path, scores in results:
        if "error" in scores:
            print(f"{str(path):<60} {'N/A':<8} {'N/A':<8} ⚠ {scores['error']}")
            error_count += 1
        else:
            grade = scores["flesch_kincaid_grade"]
            ease = scores["flesch_reading_ease"]
            status, _ = categorize_score(grade)

            print(f"{str(path):<60} {grade:<8.1f} {ease:<8.1f} {status}")

            if grade <= 5.0:
                excellent_count += 1
            elif grade <= 8.0:
                good_count += 1
            elif grade <= 12.0:
                fair_count += 1
            else:
                needs_work_count += 1

    print("-" * 100)

    # Summary statistics
    print("\n" + "=" * 100)
    print("SUMMARY STATISTICS")
    print("=" * 100)

    if valid_results:
        grades = [scores["flesch_kincaid_grade"] for _, scores in valid_results]
        avg_grade = sum(grades) / len(grades)

        print(f"Average Grade Level: {avg_grade:.2f}")
        print(f"Best Score: {min(grades):.2f}")
        print(f"Worst Score: {max(grades):.2f}\n")

        print("Distribution:")
        print(
            f"  ✅ EXCELLENT (≤5.0):   {excellent_count:3d} files ({excellent_count / len(valid_results) * 100:.1f}%)"
        )
        print(f"  ✓  GOOD (5.1-8.0):     {good_count:3d} files ({good_count / len(valid_results) * 100:.1f}%)")
        print(f"  ⚠  FAIR (8.1-12.0):    {fair_count:3d} files ({fair_count / len(valid_results) * 100:.1f}%)")
        print(
            f"  ❌ NEEDS WORK (>12.0): {needs_work_count:3d} files ({needs_work_count / len(valid_results) * 100:.1f}%)"
        )
        if error_count > 0:
            print(f"  ⚠  ERRORS/SKIPPED:    {error_count:3d} files")

    # Files needing improvement
    if needs_work_count > 0:
        print("\n" + "=" * 100)
        print("FILES NEEDING IMPROVEMENT (Grade > 12.0)")
        print("=" * 100)

        for path, scores in valid_results:
            if scores["flesch_kincaid_grade"] > 12.0:
                grade = scores["flesch_kincaid_grade"]
                words = scores["word_count"]
                avg_sent = scores["avg_sentence_length"]
                print(f"\n📄 {path}")
                print(f"   Grade: {grade:.1f} | Words: {words} | Avg Sentence: {avg_sent:.1f} words")

    print("\n" + "=" * 100)
    print("LEGEND:")
    print("  Grade Level: Flesch-Kincaid Grade Level (lower is better)")
    print("  Ease: Flesch Reading Ease Score (higher is better, 70+ is easy)")
    print("  Target: Grade 5.0 or below for all user-facing documentation")
    print("=" * 100)

    # Exit code based on results
    if needs_work_count > 0:
        print(f"\n⚠️  WARNING: {needs_work_count} files exceed Grade 12.0")
        return 1
    elif fair_count > len(valid_results) * 0.3:
        print(f"\n⚠️  WARNING: {fair_count} files are at Grade 8.1-12.0 (>30% of files)")
        return 1
    else:
        print("\n✅ All documentation meets readability standards!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
