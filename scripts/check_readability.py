#!/usr/bin/env python3
"""
Check readability of documentation files.

Validates that documentation meets Grade 5.0 reading level requirement (NFR-018).
Uses Flesch-Kincaid Grade Level metric.

Usage:
    python scripts/check_readability.py                    # Check all docs
    python scripts/check_readability.py SPECIFICATIONS.md  # Check specific file
    python scripts/check_readability.py --max-grade 6.0    # Custom threshold
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

try:
    import textstat
except ImportError:
    print("Error: textstat not installed")
    print("Install with: pip install textstat")
    sys.exit(1)


class ReadabilityChecker:
    """Check readability of markdown documentation."""

    def __init__(self, max_grade: float = 5.0):
        """
        Initialize checker.

        Args:
            max_grade: Maximum acceptable Flesch-Kincaid grade level
        """
        self.max_grade = max_grade
        self.results: List[Tuple[Path, float, bool]] = []

    def check_file(self, file_path: Path) -> Tuple[float, bool]:
        """
        Check readability of a single file.

        Args:
            file_path: Path to markdown file

        Returns:
            Tuple of (grade_level, passed)
        """
        try:
            text = file_path.read_text(encoding="utf-8")

            # Remove markdown syntax that interferes with readability scoring
            cleaned_text = self._clean_markdown(text)

            # Calculate Flesch-Kincaid Grade Level
            grade_level = textstat.flesch_kincaid_grade(cleaned_text)

            passed = grade_level <= self.max_grade

            self.results.append((file_path, grade_level, passed))

            return grade_level, passed

        except Exception as e:
            print(f"Error checking {file_path}: {e}")
            return 0.0, False

    def _clean_markdown(self, text: str) -> str:
        """
        Remove markdown syntax for readability analysis.

        Args:
            text: Raw markdown text

        Returns:
            Cleaned text without markdown syntax
        """
        import re

        # Remove code blocks (including language specifiers)
        text = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`]+`", "", text)

        # Remove table structures
        text = re.sub(r"\|[-\s\|]+\|", "", text)  # Table separators
        text = re.sub(r"\|", " ", text)  # Remaining pipes

        # Remove headers (keep the text)
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)

        # Remove links but keep text
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

        # Remove images
        text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", "", text)

        # Remove bold/italic markers (keep text)
        text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^\*]+)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)

        # Remove list markers
        text = re.sub(r"^[\*\-\+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)

        # Remove checkboxes
        text = re.sub(r"- \[[ x]\]\s+", "", text)

        # Remove horizontal rules
        text = re.sub(r"^[\-\*\_]{3,}$", "", text, flags=re.MULTILINE)

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Remove extra whitespace
        text = re.sub(r"\n\n+", "\n\n", text)
        text = re.sub(r"  +", " ", text)

        return text.strip()

    def print_results(self):
        """Print readability check results."""
        print("\n" + "=" * 70)
        print("READABILITY CHECK RESULTS (NFR-018)")
        print("=" * 70)
        print(f"Target: Flesch-Kincaid Grade {self.max_grade} or below\n")

        passed_count = sum(1 for _, _, passed in self.results if passed)
        total_count = len(self.results)

        for file_path, grade_level, passed in sorted(self.results):
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}  {file_path.name:30s}  Grade {grade_level:.1f}")

        print("\n" + "=" * 70)
        print(f"Results: {passed_count}/{total_count} files passed")
        print("=" * 70)

        if passed_count < total_count:
            print("\n⚠  Some files exceed the readability threshold!")
            print("   Simplify language in failed files to meet NFR-018.")
            return False
        else:
            print("\n✓  All files meet readability requirements!")
            return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check documentation readability (NFR-018)"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to check (default: all documentation files)",
    )
    parser.add_argument(
        "--max-grade",
        type=float,
        default=5.0,
        help="Maximum acceptable grade level (default: 5.0)",
    )

    args = parser.parse_args()

    # Determine files to check
    if args.files:
        files_to_check = [Path(f) for f in args.files]
    else:
        # Default: check all documentation files
        project_root = Path(__file__).parent.parent
        files_to_check = [
            project_root / "SPECIFICATIONS.md",
            project_root / "README.md",
            project_root / "CLAUDE.md",
            project_root / "SECURITY.md",
        ]
        # Add docs directory if it exists
        docs_dir = project_root / "docs"
        if docs_dir.exists():
            files_to_check.extend(docs_dir.glob("*.md"))

    # Filter to existing files
    files_to_check = [f for f in files_to_check if f.exists()]

    if not files_to_check:
        print("No files to check!")
        return 1

    # Run readability checks
    checker = ReadabilityChecker(max_grade=args.max_grade)

    for file_path in files_to_check:
        checker.check_file(file_path)

    # Print results and exit with appropriate code
    success = checker.print_results()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
